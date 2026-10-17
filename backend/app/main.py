from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import BACKEND_DIR, PROJECT_ROOT, get_settings
from .database import (
    DatabaseUnavailable,
    close_mongo,
    init_mongo,
    is_mock_database,
    ping_mongo,
)
from .ml_model import ModelNotReady, get_bundle, load_model, model_status
from .paypal_service import (
    InvalidWebhookSignature,
    PayPalNotConfigured,
    UnsupportedEvent,
    normalize_event,
    verify_webhook_signature,
)
from .prediction_service import score_and_persist
from .repositories.transactions import DuplicateEventError, PersistenceError, TransactionRepository
from .schemas import (
    FEATURE_CONTRACT_VERSION,
    HealthResponse,
    ModelMetricsResponse,
    ModelStatusResponse,
    PaginatedTransactions,
    PredictionResponse,
    RiskCountsResponse,
    SimulateRequest,
    StatsResponse,
    TransactionInput,
    TransactionRecord,
)
from .simulator import generate_transaction

logging.basicConfig(level=get_settings().log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("zsentinel")


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    try:
        init_mongo()
    except Exception as exc:
        logger.warning("MongoDB initialization warning: %s", exc)
    try:
        load_model(str(settings.resolved_artifact_path))
    except Exception as exc:
        logger.warning(
            "Model loading warning: %s. Run 'python ml/train.py' before running live predictions.",
            exc,
        )
    yield
    close_mongo()


app = FastAPI(
    title="Z-Sentinel API",
    description="Real-Time AI Fraud Risk & Decision Engine for IBM Z Datathon",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://z-sentinel.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ModelNotReady)
async def model_not_ready(_, exc: ModelNotReady):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(DatabaseUnavailable)
async def db_unavailable(_, exc: DatabaseUnavailable):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(PersistenceError)
async def persist_error(_, exc: PersistenceError):
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health():
    ready, version = model_status()
    mongo_ok = False
    try:
        mongo_ok = ping_mongo()
    except Exception:
        mongo_ok = False
    settings = get_settings()
    db_mode = "mock_in_memory" if is_mock_database() else "mongodb"
    return HealthResponse(
        status="online" if ready and mongo_ok else "degraded",
        service="Z-Sentinel",
        model_ready=ready,
        model_version=version,
        mongodb_ready=mongo_ok,
        database_mode=db_mode,
        paypal_configured=settings.paypal_configured,
        genai_configured=settings.genai_configured,
        feature_contract_version=FEATURE_CONTRACT_VERSION,
    )


@app.post("/api/predict", response_model=PredictionResponse, tags=["Inference"])
@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
def predict(payload: TransactionInput):
    """Evaluate a transaction, compute risk score/level/decision, and log audit row."""
    return score_and_persist(payload)


@app.post("/api/transactions", response_model=PredictionResponse, tags=["Transactions"])
@app.post("/transactions", response_model=PredictionResponse, tags=["Transactions"])
def create_transaction(payload: TransactionInput):
    """Ingest, validate, score, and persist a transaction."""
    return score_and_persist(payload)


@app.post("/api/transactions/simulate", response_model=PredictionResponse, tags=["Simulation"])
@app.post("/api/simulate", response_model=PredictionResponse, tags=["Simulation"])
@app.post("/simulate", response_model=PredictionResponse, tags=["Simulation"])
def simulate(body: SimulateRequest | None = None):
    """Generate and score a synthetic transaction for demonstration/testing."""
    request = body or SimulateRequest()
    payload = generate_transaction(scenario=request.scenario, seed=request.seed)
    return score_and_persist(payload)


@app.get("/api/transactions", response_model=PaginatedTransactions, tags=["Transactions"])
@app.get("/transactions", response_model=PaginatedTransactions, tags=["Transactions"])
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    risk_level: str | None = Query(default=None),
    decision: str | None = Query(default=None),
):
    """Retrieve historical transaction audit logs with pagination and optional filtering."""
    items, total = TransactionRepository().list_recent(
        page=page, page_size=page_size, risk_level=risk_level, decision=decision
    )
    return PaginatedTransactions(
        items=[TransactionRecord(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@app.get("/api/transactions/{transaction_id}", response_model=TransactionRecord, tags=["Transactions"])
@app.get("/transactions/{transaction_id}", response_model=TransactionRecord, tags=["Transactions"])
def get_transaction(transaction_id: str):
    """Retrieve a specific transaction audit record by its ID."""
    item = TransactionRepository().find_by_id(transaction_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionRecord(**item)


@app.get("/api/stats", response_model=StatsResponse, tags=["Analytics"])
@app.get("/stats", response_model=StatsResponse, tags=["Analytics"])
def stats():
    """Retrieve aggregate dashboard statistics (totals, approved, review, blocked, avg latency)."""
    return StatsResponse(**TransactionRepository().stats())


@app.get("/api/risk", response_model=RiskCountsResponse, tags=["Analytics"])
@app.get("/risk", response_model=RiskCountsResponse, tags=["Analytics"])
def risk():
    """Retrieve current distribution count of transactions across LOW, MEDIUM, and HIGH risk."""
    return RiskCountsResponse(**TransactionRepository().risk_counts())


@app.get("/api/model/status", response_model=ModelStatusResponse, tags=["Model"])
@app.get("/model/status", response_model=ModelStatusResponse, tags=["Model"])
def model_status_endpoint():
    """Show whether a trained model is available and its metadata."""
    ready, version = model_status()
    if not ready:
        return ModelStatusResponse(model_ready=False)
    bundle = get_bundle()
    settings = get_settings()
    return ModelStatusResponse(
        model_ready=True,
        model_version=version,
        selected_model=bundle.get("selected_model"),
        feature_contract_version=bundle.get("feature_contract_version", FEATURE_CONTRACT_VERSION),
        features=bundle.get("features", []),
        medium_threshold=bundle.get("medium_threshold"),
        high_threshold=bundle.get("high_threshold"),
        calibrated=bundle.get("calibrated"),
        data_source=bundle.get("data_source"),
        artifact_path=str(settings.resolved_artifact_path),
    )


@app.get("/api/model/metrics", response_model=ModelMetricsResponse, tags=["Model"])
@app.get("/model/metrics", response_model=ModelMetricsResponse, tags=["Model"])
def model_metrics():
    """Retrieve offline model evaluation metrics (ROC-AUC, PR-AUC, F1, precision, recall, confusion matrix)."""
    candidates = [
        PROJECT_ROOT / "ml" / "artifacts" / "evaluation.json",
        BACKEND_DIR.parent / "ml" / "artifacts" / "evaluation.json",
        Path("ml/artifacts/evaluation.json").resolve(),
    ]
    eval_path = None
    for c in candidates:
        if c.exists():
            eval_path = c
            break

    if not eval_path:
        return ModelMetricsResponse(
            available=False,
            disclaimer="Evaluation metrics file not found. Run 'python ml/train.py' to generate.",
        )
    try:
        data = json.loads(eval_path.read_text(encoding="utf-8"))
        return ModelMetricsResponse(available=True, **data)
    except Exception as exc:
        return ModelMetricsResponse(
            available=False,
            disclaimer=f"Error reading evaluation metrics: {exc}",
        )


@app.post("/api/paypal/webhook", tags=["PayPal"])
@app.post("/paypal/webhook", tags=["PayPal"])
async def paypal_webhook(request: Request):
    """Optional PayPal Sandbox webhook receiver for post-capture event ingestion."""
    try:
        event = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from exc
    headers = dict(request.headers)
    try:
        verify_webhook_signature(headers, event)
        payload = normalize_event(event)
        result = score_and_persist(payload)
        return {"status": "processed", "duplicate": False, "transaction": result}
    except PayPalNotConfigured as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except InvalidWebhookSignature as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except UnsupportedEvent as exc:
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "reason": "unsupported_event", "event_type": exc.event_type},
        )
    except DuplicateEventError as exc:
        return {"status": "duplicate", "duplicate": True, "transaction": exc.existing}
    except PersistenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
