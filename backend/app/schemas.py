from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class TransactionInput(BaseModel):
    amount: float = Field(gt=0)
    merchant_category: str = "other"
    device_novelty: float = Field(
        default=0,
        ge=0,
        le=1
    )

    location_deviation: float = Field(
        default=0,
        ge=0,
        le=1
    )

    transaction_velocity: float = Field(
        default=1,
        ge=0
    )

    unusual_time: float = Field(
        default=0,
        ge=0,
        le=1
    )


class PredictionResponse(BaseModel):

    transaction_id: str

    fraud_probability: float

    risk_score: float

    risk_level: str

    decision: str

    model_version: str

    inference_time_ms: float

    timestamp: datetime

    top_risk_factors: List[str]


class TransactionResponse(PredictionResponse):

    amount: float

    merchant_category: str

    device_novelty: float

    location_deviation: float

    transaction_velocity: float

    unusual_time: float


class StatsResponse(BaseModel):

    total_transactions: int

    high_risk_transactions: int

    fraud_predictions: int

    approved: int

    review: int

    blocked: int

    average_inference_ms: float