from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

FEATURE_CONTRACT_VERSION = "txn_features_v1"
MERCHANT_CATEGORIES = (
    "grocery",
    "electronics",
    "travel",
    "restaurant",
    "fuel",
    "online",
    "other",
)
CHANNELS = ("online", "pos", "atm", "other")
SOURCES = ("api", "simulator", "paypal_sandbox")
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]
Decision = Literal["APPROVE", "REVIEW", "BLOCK"]


class TransactionInput(BaseModel):
    """Leakage-safe input contract shared by training, simulation, and inference."""

    amount: float = Field(gt=0, le=1_000_000, examples=[129.50])
    currency: str = Field(default="USD", min_length=3, max_length=3)
    merchant_category: str = "other"
    hour_of_day: Optional[int] = Field(default=None, ge=0, le=23)
    device_novelty: Optional[float] = Field(default=None, ge=0, le=1)
    location_deviation: Optional[float] = Field(default=None, ge=0, le=1)
    transaction_velocity: Optional[float] = Field(default=None, ge=0, le=100)
    unusual_time: Optional[float] = Field(default=None, ge=0, le=1)
    channel: str = "online"
    source: str = "api"
    external_transaction_id: Optional[str] = None
    paypal_event_id: Optional[str] = None

    @field_validator("currency")
    @classmethod
    def uppercase_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("merchant_category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        cleaned = (value or "other").strip().lower()
        return cleaned if cleaned in MERCHANT_CATEGORIES else "other"

    @field_validator("channel")
    @classmethod
    def normalize_channel(cls, value: str) -> str:
        cleaned = (value or "online").strip().lower()
        return cleaned if cleaned in CHANNELS else "other"

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        cleaned = (value or "api").strip().lower()
        return cleaned if cleaned in SOURCES else "api"


class RiskFactor(BaseModel):
    feature: str
    value: Optional[float | str] = None
    contribution: float
    direction: Literal["increases_fraud_risk", "decreases_fraud_risk"]
    strength: float
    method: str


class PredictionResponse(BaseModel):
    transaction_id: str
    source: str
    amount: float
    currency: str
    merchant_category: str
    channel: str
    fraud_probability: float
    risk_score: float
    risk_level: RiskLevel
    decision: str
    model_version: str
    feature_contract_version: str = FEATURE_CONTRACT_VERSION
    inference_time_ms: float
    timestamp: datetime
    top_risk_factors: list[RiskFactor]
    imputed_fields: list[str] = Field(default_factory=list)
    unavailable_fields: list[str] = Field(default_factory=list)
    probability_note: str
    investigation_summary: Optional[str] = None
    summary_source: Literal["none", "deterministic", "genai"] = "none"
    features: dict[str, Any] = Field(default_factory=dict)


class TransactionRecord(PredictionResponse):
    external_transaction_id: Optional[str] = None
    paypal_event_id: Optional[str] = None


class PaginatedTransactions(BaseModel):
    items: list[TransactionRecord]
    total: int
    page: int
    page_size: int


class StatsResponse(BaseModel):
    total_transactions: int
    high_risk_transactions: int
    approved: int
    review: int
    blocked: int
    average_inference_ms: float


class RiskCountsResponse(BaseModel):
    LOW: int
    MEDIUM: int
    HIGH: int


class HealthResponse(BaseModel):
    status: str
    service: str
    model_ready: bool
    model_version: Optional[str]
    mongodb_ready: bool
    database_mode: str = "live"
    paypal_configured: bool
    genai_configured: bool
    feature_contract_version: str


class SimulateRequest(BaseModel):
    scenario: Optional[str] = None
    seed: Optional[int] = None


class ModelStatusResponse(BaseModel):
    model_ready: bool
    model_version: Optional[str] = None
    selected_model: Optional[str] = None
    feature_contract_version: str = FEATURE_CONTRACT_VERSION
    features: list[str] = Field(default_factory=list)
    medium_threshold: Optional[float] = None
    high_threshold: Optional[float] = None
    calibrated: Optional[bool] = None
    data_source: Optional[str] = None
    artifact_path: Optional[str] = None


class ModelMetricsResponse(BaseModel):
    available: bool
    model_version: Optional[str] = None
    selected_model: Optional[str] = None
    data_source: Optional[str] = None
    disclaimer: Optional[str] = None
    validation_comparison: dict[str, Any] = Field(default_factory=dict)
    test_metrics: dict[str, Any] = Field(default_factory=dict)
    medium_threshold: Optional[float] = None
    high_threshold: Optional[float] = None
    calibrated: Optional[bool] = None
    n_train: Optional[int] = None
    n_valid: Optional[int] = None
    n_test: Optional[int] = None

