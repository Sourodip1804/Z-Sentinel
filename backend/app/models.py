from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON
)

from .database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_id = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    merchant_category = Column(
        String,
        nullable=False
    )

    device_novelty = Column(
        Float,
        nullable=False
    )

    location_deviation = Column(
        Float,
        nullable=False
    )

    transaction_velocity = Column(
        Float,
        nullable=False
    )

    unusual_time = Column(
        Float,
        nullable=False
    )

    fraud_probability = Column(
        Float,
        nullable=False
    )

    risk_score = Column(
        Float,
        nullable=False
    )

    risk_level = Column(
        String,
        nullable=False
    )

    decision = Column(
        String,
        nullable=False
    )

    top_risk_factors = Column(
        JSON,
        default=list
    )

    model_version = Column(
        String,
        nullable=False
    )

    inference_time_ms = Column(
        Float,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )