from __future__ import annotations

from dataclasses import dataclass

from .config import get_settings


@dataclass(frozen=True)
class RiskDecision:
    fraud_probability: float
    risk_score: float
    risk_level: str
    decision: str
    policy_version: str
    threshold_note: str


POLICY_VERSION = "prototype-v1"

THRESHOLD_NOTE = (
    "Prototype policy: thresholds were selected on synthetic validation data to "
    "balance false positives (blocking good customers) against false negatives "
    "(missing fraud). 0.5 is not assumed to be correct. Scores are model outputs "
    "and should not be treated as proven real-world fraud probabilities."
)


def apply_policy(
    fraud_probability: float,
    medium_threshold: float | None = None,
    high_threshold: float | None = None,
) -> RiskDecision:
    settings = get_settings()
    medium = settings.risk_medium_threshold if medium_threshold is None else medium_threshold
    high = settings.risk_high_threshold if high_threshold is None else high_threshold
    if high <= medium:
        raise ValueError("HIGH threshold must be greater than MEDIUM threshold")
    probability = max(0.0, min(1.0, float(fraud_probability)))
    risk_score = round(probability * 100.0, 2)
    if probability >= high:
        level, decision = "HIGH", "BLOCK"
    elif probability >= medium:
        level, decision = "MEDIUM", "REVIEW"
    else:
        level, decision = "LOW", "APPROVE"
    return RiskDecision(
        fraud_probability=round(probability, 6),
        risk_score=risk_score,
        risk_level=level,
        decision=decision,
        policy_version=POLICY_VERSION,
        threshold_note=THRESHOLD_NOTE,
    )
