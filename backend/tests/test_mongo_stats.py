def test_stats_and_risk_use_persisted_rows(client):
    client.post(
        "/api/predict",
        json={
            "amount": 20,
            "merchant_category": "grocery",
            "hour_of_day": 10,
            "device_novelty": 0,
            "location_deviation": 0.05,
            "transaction_velocity": 1,
            "unusual_time": 0,
        },
    )
    client.post("/api/transactions/simulate", json={"scenario": "high_amount_online"})
    stats = client.get("/api/stats").json()
    risk = client.get("/api/risk").json()
    listing = client.get("/api/transactions?page=1&page_size=10").json()
    assert stats["total_transactions"] >= 2
    assert "high_risk_transactions" in stats
    assert stats["approved"] + stats["review"] + stats["blocked"] == stats["total_transactions"]
    assert risk["LOW"] + risk["MEDIUM"] + risk["HIGH"] == stats["total_transactions"]
    assert listing["total"] == stats["total_transactions"]
    assert listing["items"]
