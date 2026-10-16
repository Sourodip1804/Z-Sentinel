from app.risk_engine import apply_policy


def test_low_medium_high_thresholds():
    low = apply_policy(0.10, medium_threshold=0.25, high_threshold=0.60)
    assert low.risk_level == "LOW"
    assert low.decision == "APPROVE"
    assert low.risk_score == 10.0

    medium = apply_policy(0.40, medium_threshold=0.25, high_threshold=0.60)
    assert medium.risk_level == "MEDIUM"
    assert medium.decision == "REVIEW"

    high = apply_policy(0.80, medium_threshold=0.25, high_threshold=0.60)
    assert high.risk_level == "HIGH"
    assert high.decision == "BLOCK"
    assert high.risk_score == 80.0


def test_probability_is_clamped():
    result = apply_policy(1.4, medium_threshold=0.25, high_threshold=0.60)
    assert result.fraud_probability == 1.0
    assert result.risk_score == 100.0
