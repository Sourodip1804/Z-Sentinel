"""Shared leakage-safe feature contract for training and inference."""

from __future__ import annotations

from typing import Any, Optional

import pandas as pd

from .schemas import FEATURE_CONTRACT_VERSION, MERCHANT_CATEGORIES, TransactionInput

NUMERIC_FEATURES = [
    "amount",
    "hour_of_day",
    "device_novelty",
    "location_deviation",
    "transaction_velocity",
    "unusual_time",
]
CATEGORICAL_FEATURES = ["merchant_category"]
MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES
NIGHT_HOURS = {0, 1, 2, 3, 4, 5, 23}

# Training-only defaults used when a live field is unavailable.
# These are documented imputations, not invented customer behaviour.
IMPUTATION_DEFAULTS = {
    "amount": 50.0,
    "hour_of_day": 12,
    "device_novelty": 0.0,
    "location_deviation": 0.20,
    "transaction_velocity": 2.0,
    "unusual_time": 0.0,
    "merchant_category": "other",
}


def derive_unusual_time(hour_of_day: Optional[int], unusual_time: Optional[float]) -> float:
    if unusual_time is not None:
        return float(unusual_time)
    if hour_of_day is None:
        return float(IMPUTATION_DEFAULTS["unusual_time"])
    return 1.0 if int(hour_of_day) in NIGHT_HOURS else 0.0


def availability(payload: TransactionInput) -> tuple[list[str], list[str]]:
    unavailable: list[str] = []
    imputed: list[str] = []
    mapping = {
        "hour_of_day": payload.hour_of_day,
        "device_novelty": payload.device_novelty,
        "location_deviation": payload.location_deviation,
        "transaction_velocity": payload.transaction_velocity,
        "unusual_time": payload.unusual_time,
    }
    for name, value in mapping.items():
        if value is None:
            unavailable.append(name)
            imputed.append(name)
    return unavailable, imputed


def payload_to_feature_dict(payload: TransactionInput) -> dict[str, Any]:
    hour = payload.hour_of_day if payload.hour_of_day is not None else IMPUTATION_DEFAULTS["hour_of_day"]
    unusual = derive_unusual_time(payload.hour_of_day, payload.unusual_time)
    return {
        "amount": float(payload.amount),
        "hour_of_day": int(hour),
        "device_novelty": float(
            payload.device_novelty
            if payload.device_novelty is not None
            else IMPUTATION_DEFAULTS["device_novelty"]
        ),
        "location_deviation": float(
            payload.location_deviation
            if payload.location_deviation is not None
            else IMPUTATION_DEFAULTS["location_deviation"]
        ),
        "transaction_velocity": float(
            payload.transaction_velocity
            if payload.transaction_velocity is not None
            else IMPUTATION_DEFAULTS["transaction_velocity"]
        ),
        "unusual_time": float(unusual),
        "merchant_category": payload.merchant_category
        if payload.merchant_category in MERCHANT_CATEGORIES
        else "other",
    }


def features_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in MODEL_FEATURES:
        if column not in frame.columns:
            raise ValueError(f"Missing required feature column: {column}")
    return frame[MODEL_FEATURES]


def payload_to_frame(payload: TransactionInput) -> tuple[pd.DataFrame, dict[str, Any], list[str], list[str]]:
    features = payload_to_feature_dict(payload)
    unavailable, imputed = availability(payload)
    return features_frame([features]), features, unavailable, imputed


def training_frame(frame: pd.DataFrame) -> pd.DataFrame:
    required = MODEL_FEATURES + ["is_fraud"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Training data missing columns: {missing}")
    if frame["is_fraud"].isna().any():
        raise ValueError("Training labels contain null values")
    cleaned = frame.copy()
    cleaned["merchant_category"] = (
        cleaned["merchant_category"].astype(str).str.lower().where(
            cleaned["merchant_category"].astype(str).str.lower().isin(MERCHANT_CATEGORIES),
            "other",
        )
    )
    for column in NUMERIC_FEATURES:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        cleaned[column] = cleaned[column].fillna(IMPUTATION_DEFAULTS.get(column, 0.0))
    cleaned["is_fraud"] = cleaned["is_fraud"].astype(int)
    leak_cols = [c for c in cleaned.columns if c.lower() in {"fraud", "label", "class"} and c != "is_fraud"]
    if leak_cols:
        raise ValueError(f"Potential leakage columns present: {leak_cols}")
    return cleaned[MODEL_FEATURES + ["is_fraud"]]


def contract_metadata() -> dict[str, Any]:
    return {
        "feature_contract_version": FEATURE_CONTRACT_VERSION,
        "model_features": MODEL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "imputation_defaults": IMPUTATION_DEFAULTS,
        "notes": [
            "Only pre-decision fields are used.",
            "is_fraud is a training label and is never an inference feature.",
            "Missing live fields are listed in unavailable_fields and filled with documented defaults.",
        ],
    }
