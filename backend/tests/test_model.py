from app.ml_model import get_bundle, model_status, predict_probability
from app.schemas import TransactionInput


def test_model_loads_with_api(client):
    ready, version = model_status()
    assert ready is True
    bundle = get_bundle()
    assert bundle["pipeline"] is not None
    assert version == bundle["model_version"]


def test_predict_probability_range(client):
    payload = TransactionInput(amount=50, merchant_category="grocery", hour_of_day=10)
    probability, frame, features, unavailable, imputed = predict_probability(payload)
    assert 0 <= probability <= 1
    assert list(frame.columns)
    assert "amount" in features
