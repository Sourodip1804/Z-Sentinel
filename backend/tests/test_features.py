from app.feature_engineering import payload_to_feature_dict
from app.schemas import TransactionInput


def test_missing_fields_are_listed_not_hidden():
    payload = TransactionInput(amount=10, merchant_category="online")
    _, _, unavailable, imputed = __import__(
        "app.feature_engineering", fromlist=["payload_to_frame"]
    ).payload_to_frame(payload)
    assert "device_novelty" in unavailable
    assert "device_novelty" in imputed
    features = payload_to_feature_dict(payload)
    assert features["device_novelty"] == 0.0
