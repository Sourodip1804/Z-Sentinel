import time


from datetime import datetime

from fastapi import(
    Depends,
    FastAPI,
    HTTPException
    
)

from fastapi.middleware.cors import(
    CORSMiddleware
)

from sqlalchemy.orm import Session

from .database import (
    Base,
    engine,
    get_db
)

from .models import Transaction

from .schemas import (
    PredictionResponse,
    StatsResponse,
    TransactionInput,
    TransactionResponse
)

from .ml_model import (
    MODEL,
    MODEL_VERSION,
    predict
)

from .risk_engine import (
    calculate_risk
)

from .explainability import (
    explain_transaction
)

from .simulator import (
    generate_transaction,
    transaction_id
)

Base.metadata.create_all(bind=engine)

# creating the fastapi
app = FastAPI(
    title="Z-Sentinel API",
    description= "Real-Time AI Fraud Risk & Decision Engine",
    version="1.0.0"

)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# now the core prediction model 

def run_prediction(payload:TransactionInput):
    start = time.perf_counter()
    probability, features = predict(payload)
    risk_score, risk_level, decision = (calculate_risk(probability))
    factors = explain_transaction(features, MODEL)
    elapsed_ms = round((time.perf_counter() - start)*1000,2)
    return{
        "transaction_id":
            transaction_id(),

        "fraud_probability":
            round(
                probability,
                6
            ),

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "decision":
            decision,

        "model_version":
            MODEL_VERSION,

        "inference_time_ms":
            elapsed_ms,

        "timestamp":
            datetime.datetime.utcnow(),

        "top_risk_factors":
            factors
    
    }

# for saving the transaction 

def save_transaction(db: Session, payload:TransactionInput, result: dict):
    row = Transaction(
        transaction_id=
            result["transaction_id"],

        amount=payload.amount,

        merchant_category=
            payload.merchant_category,

        device_novelty=
            payload.device_novelty,

        location_deviation=
            payload.location_deviation,

        transaction_velocity=
            payload.transaction_velocity,

        unusual_time=
            payload.unusual_time,

        fraud_probability=
            result["fraud_probability"],

        risk_score=
            result["risk_score"],

        risk_level=
            result["risk_level"],

        decision=
            result["decision"],

        top_risk_factors=
            result["top_risk_factors"],

        model_version=
            result["model_version"],

        inference_time_ms=
            result["inference_time_ms"],

        timestamp=
            result["timestamp"]
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# for the health point 
@app.get("/api/health")
def health():
    return {
        "status": "online",
        "service": "Z-Sentinel",
        "model_version":
            MODEL_VERSION
    }


# prediction model end point

@app.post("/api/predict", response_model=PredictionResponse)

def predict_transaction(
    payload:TransactionInput,
    db: Session = Depends(get_db)

):
    result = run_prediction(payload)
    save_transaction(db, payload, result)
    return result 

def row_to_response(row: Transaction) -> dict:
    return {
        "transaction_id": row.transaction_id,
        "amount": row.amount,
        "merchant_category": row.merchant_category,
        "device_novelty": row.device_novelty,
        "location_deviation": row.location_deviation,
        "transaction_velocity": row.transaction_velocity,
        "unusual_time": row.unusual_time,
        "fraud_probability": row.fraud_probability,
        "risk_score": row.risk_score,
        "risk_level": row.risk_level,
        "decision": row.decision,
        "top_risk_factors": row.top_risk_factors,
        "model_version": row.model_version,
        "inference_time_ms": row.inference_time_ms,
        "timestamp": row.timestamp,
    }


# for the simulator endpoint
@app.post(
    "/api/transactions/simulate",
    response_model=TransactionResponse
)
def simulate_transaction(
    db: Session = Depends(get_db)
):

    payload = generate_transaction()
    result = run_prediction(
        payload
    )

    row = save_transaction(
        db,
        payload,
        result
    )

    return row_to_response(row)