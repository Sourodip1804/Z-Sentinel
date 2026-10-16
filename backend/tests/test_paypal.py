from unittest.mock import MagicMock

from app.config import get_settings
from app.paypal_service import InvalidWebhookSignature, normalize_event, verify_webhook_signature


CAPTURE_EVENT = {
    "id": "WH-TEST-1",
    "event_type": "PAYMENT.CAPTURE.COMPLETED",
    "resource": {
        "id": "CAP-1",
        "amount": {"value": "88.10", "currency_code": "USD"},
    },
}


def _headers():
    return {
        "PAYPAL-AUTH-ALGO": "SHA256withRSA",
        "PAYPAL-CERT-URL": "https://api-m.sandbox.paypal.com/cert",
        "PAYPAL-TRANSMISSION-ID": "tx-1",
        "PAYPAL-TRANSMISSION-SIG": "sig",
        "PAYPAL-TRANSMISSION-TIME": "2026-10-15T10:00:00Z",
    }


def test_missing_credentials(client, monkeypatch):
    monkeypatch.setenv("PAYPAL_CLIENT_ID", "")
    monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "")
    monkeypatch.setenv("PAYPAL_WEBHOOK_ID", "")
    get_settings.cache_clear()
    response = client.post("/api/paypal/webhook", json=CAPTURE_EVENT, headers=_headers())
    assert response.status_code == 503
    get_settings.cache_clear()


def test_invalid_signature(client, monkeypatch):
    monkeypatch.setenv("PAYPAL_CLIENT_ID", "id")
    monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "secret")
    monkeypatch.setenv("PAYPAL_WEBHOOK_ID", "webhook")
    get_settings.cache_clear()

    def boom(*_args, **_kwargs):
        raise InvalidWebhookSignature("bad signature")

    monkeypatch.setattr("app.main.verify_webhook_signature", boom)
    response = client.post("/api/paypal/webhook", json=CAPTURE_EVENT, headers=_headers())
    assert response.status_code == 401
    get_settings.cache_clear()


def test_unsupported_event(client, monkeypatch):
    monkeypatch.setenv("PAYPAL_CLIENT_ID", "id")
    monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "secret")
    monkeypatch.setenv("PAYPAL_WEBHOOK_ID", "webhook")
    get_settings.cache_clear()
    monkeypatch.setattr("app.main.verify_webhook_signature", lambda *_args, **_kwargs: None)
    response = client.post(
        "/api/paypal/webhook",
        json={"id": "WH-2", "event_type": "CUSTOMER.DISPUTE.CREATED", "resource": {}},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
    get_settings.cache_clear()


def test_duplicate_webhook_event(client, monkeypatch):
    monkeypatch.setenv("PAYPAL_CLIENT_ID", "id")
    monkeypatch.setenv("PAYPAL_CLIENT_SECRET", "secret")
    monkeypatch.setenv("PAYPAL_WEBHOOK_ID", "webhook")
    get_settings.cache_clear()
    monkeypatch.setattr("app.main.verify_webhook_signature", lambda *_args, **_kwargs: None)
    first = client.post("/api/paypal/webhook", json=CAPTURE_EVENT, headers=_headers())
    second = client.post("/api/paypal/webhook", json=CAPTURE_EVENT, headers=_headers())
    assert first.status_code == 200
    assert first.json()["duplicate"] is False
    assert second.status_code == 200
    assert second.json()["duplicate"] is True
    get_settings.cache_clear()


def test_normalize_does_not_invent_behaviour():
    payload = normalize_event(CAPTURE_EVENT)
    assert payload.amount == 88.10
    assert payload.source == "paypal_sandbox"
    assert payload.device_novelty is None
    assert payload.location_deviation is None
    assert payload.transaction_velocity is None


def test_verify_calls_paypal_api():
    get_settings.cache_clear()
    from app.config import Settings

    mock_settings = Settings(
        paypal_client_id="id",
        paypal_client_secret="secret",
        paypal_webhook_id="hook",
        mongodb_uri="mongomock://localhost",
    )
    http = MagicMock()
    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "tok"}
    token_response.raise_for_status.return_value = None
    verify_response = MagicMock()
    verify_response.json.return_value = {"verification_status": "SUCCESS"}
    verify_response.raise_for_status.return_value = None
    http.post.side_effect = [token_response, verify_response]
    from app import paypal_service

    original = paypal_service.get_settings
    paypal_service.get_settings = lambda: mock_settings
    try:
        verify_webhook_signature(_headers(), CAPTURE_EVENT, http_client=http)
    finally:
        paypal_service.get_settings = original
    assert http.post.call_count == 2
