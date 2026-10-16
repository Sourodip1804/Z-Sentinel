from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from .explainability import explain_prediction
from .genai_summary import maybe_genai_summary
from .ml_model import get_bundle, predict_probability
from .repositories.transactions import TransactionRepository
from .risk_engine import apply_policy
from .schemas import FEATURE_CONTRACT_VERSION, PredictionResponse, TransactionInput
from .simulator import transaction_id

logger = logging.getLogger("zsentinel")
PROBABILITY_NOTE = (
    "This value is a model score from a prototype trained primarily on synthetic labels. "
    "It is not a calibrated real-world fraud probability unless evaluation metadata says otherwise."
)


def score_and_persist(
    payload: TransactionInput,
    repository: TransactionRepository | None = None,
    assigned_id: str | None = None,
) -> PredictionResponse:
    repo = repository or TransactionRepository()
    start = time.perf_counter()
    probability, frame, features, unavailable, imputed = predict_probability(payload)
    bundle = get_bundle()
    policy = apply_policy(
        probability,
        medium_threshold=bundle.get("medium_threshold"),
        high_threshold=bundle.get("high_threshold"),
    )
    factors = explain_prediction(bundle["pipeline"], frame)
    summary, summary_source = maybe_genai_summary(
        policy.decision, policy.risk_level, policy.fraud_probability, factors
    )
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    txn_id = assigned_id or transaction_id()
    document = {
        "transaction_id": txn_id,
        "source": payload.source,
        "external_transaction_id": payload.external_transaction_id,
        "paypal_event_id": payload.paypal_event_id,
        "amount": payload.amount,
        "currency": payload.currency,
        "merchant_category": payload.merchant_category,
        "channel": payload.channel,
        "features": features,
        "fraud_probability": policy.fraud_probability,
        "risk_score": policy.risk_score,
        "risk_level": policy.risk_level,
        "decision": policy.decision,
        "model_version": bundle["model_version"],
        "feature_contract_version": FEATURE_CONTRACT_VERSION,
        "inference_time_ms": elapsed_ms,
        "timestamp": datetime.now(timezone.utc),
        "top_risk_factors": [factor.model_dump() for factor in factors],
        "imputed_fields": imputed,
        "unavailable_fields": unavailable,
        "probability_note": PROBABILITY_NOTE,
        "investigation_summary": summary,
        "summary_source": summary_source,
    }
    stored = repo.insert(document)
    logger.info(
        "scored transaction_id=%s decision=%s risk_level=%s latency_ms=%s",
        txn_id,
        policy.decision,
        policy.risk_level,
        elapsed_ms,
    )
    return PredictionResponse(**stored)
