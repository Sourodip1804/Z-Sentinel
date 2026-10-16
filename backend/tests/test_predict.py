from __future__ import annotations


VALID = {
    "amount": 120.5,
    "currency": "USD",
    "merchant_category": "grocery",
    "hour_of_day": 11,
    "device_novelty": 0,
    "location_deviation": 0.1,
    "transaction_velocity": 1,
    "unusual_time": 0,
    "channel": "pos",
}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["model_ready"] is True
    assert body["mongodb_ready"] is True
    assert body["feature_contract_version"] == "txn_features_v1"

    # Also test the non-prefixed /health alias
    res_root = client.get("/health")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "Z-Sentinel"


def test_valid_prediction(client):
    response = client.post("/api/predict", json=VALID)
    assert response.status_code == 200
    body = response.json()
    assert 0 <= body["fraud_probability"] <= 1
    assert body["risk_score"] == round(body["fraud_probability"] * 100, 2)
    assert body["risk_level"] in {"LOW", "MEDIUM", "HIGH"}
    assert body["decision"] in {"APPROVE", "REVIEW", "BLOCK"}
    assert body["model_version"]
    assert body["inference_time_ms"] >= 0
    assert body["top_risk_factors"]
    assert "feature" in body["top_risk_factors"][0]
    stored = client.get(f"/api/transactions/{body['transaction_id']}")
    assert stored.status_code == 200

    # Also test /predict root alias
    res_root = client.post("/predict", json=VALID)
    assert res_root.status_code == 200
    assert res_root.json()["decision"] in {"APPROVE", "REVIEW", "BLOCK"}


def test_transactions_ingestion(client):
    response = client.post("/transactions", json=VALID)
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_id"].startswith("TXN-")
    assert data["amount"] == 120.5

    # Retrieve from /transactions
    list_res = client.get("/transactions")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1


def test_invalid_amount_rejected(client):
    payload = dict(VALID)
    payload["amount"] = -5
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422


def test_simulate_uses_same_pipeline(client):
    response = client.post("/api/transactions/simulate", json={"scenario": "high_amount_online"})
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "simulator"
    assert body["decision"] in {"APPROVE", "REVIEW", "BLOCK"}

    # Also test /simulate alias
    res_alias = client.post("/simulate", json={"scenario": "legitimate_grocery"})
    assert res_alias.status_code == 200
    assert res_alias.json()["source"] == "simulator"


def test_model_status_and_metrics(client):
    status_res = client.get("/model/status")
    assert status_res.status_code == 200
    status_body = status_res.json()
    assert status_body["model_ready"] is True
    assert status_body["model_version"] is not None

    metrics_res = client.get("/model/metrics")
    assert metrics_res.status_code == 200
    metrics_body = metrics_res.json()
    assert metrics_body["available"] is True
    assert "test_metrics" in metrics_body
