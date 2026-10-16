from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from .config import get_settings
from .schemas import TransactionInput

logger = logging.getLogger("zsentinel")

SUPPORTED_EVENTS = {
    "PAYMENT.CAPTURE.COMPLETED",
    "CHECKOUT.ORDER.APPROVED",
}


class PayPalError(Exception):
    pass


class PayPalNotConfigured(PayPalError):
    pass


class InvalidWebhookSignature(PayPalError):
    pass


class UnsupportedEvent(PayPalError):
    def __init__(self, event_type: str):
        super().__init__(event_type)
        self.event_type = event_type


def _token(client: httpx.Client) -> str:
    settings = get_settings()
    if not settings.paypal_configured:
        raise PayPalNotConfigured("PayPal Sandbox credentials are not configured")
    response = client.post(
        f"{settings.paypal_api_base}/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        auth=(settings.paypal_client_id, settings.paypal_client_secret),
        headers={"Accept": "application/json"},
        timeout=10.0,
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise PayPalError("PayPal token response missing access_token")
    return token


def verify_webhook_signature(
    headers: dict[str, str],
    event: dict[str, Any],
    http_client: Optional[httpx.Client] = None,
) -> None:
    settings = get_settings()
    if not settings.paypal_configured:
        raise PayPalNotConfigured(
            "PayPal webhook received but PAYPAL_CLIENT_ID / SECRET / WEBHOOK_ID are not set"
        )
    required = [
        "paypal-auth-algo",
        "paypal-cert-url",
        "paypal-transmission-id",
        "paypal-transmission-sig",
        "paypal-transmission-time",
    ]
    normalized = {key.lower(): value for key, value in headers.items()}
    missing = [key for key in required if not normalized.get(key)]
    if missing:
        raise InvalidWebhookSignature(f"Missing PayPal signature headers: {missing}")

    payload = {
        "auth_algo": normalized["paypal-auth-algo"],
        "cert_url": normalized["paypal-cert-url"],
        "transmission_id": normalized["paypal-transmission-id"],
        "transmission_sig": normalized["paypal-transmission-sig"],
        "transmission_time": normalized["paypal-transmission-time"],
        "webhook_id": settings.paypal_webhook_id,
        "webhook_event": event,
    }
    close_client = False
    client = http_client
    if client is None:
        client = httpx.Client()
        close_client = True
    try:
        token = _token(client)
        response = client.post(
            f"{settings.paypal_api_base}/v1/notifications/verify-webhook-signature",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
        status = str(response.json().get("verification_status", "")).upper()
        if status != "SUCCESS":
            raise InvalidWebhookSignature("PayPal signature verification failed")
    except (InvalidWebhookSignature, PayPalNotConfigured):
        raise
    except Exception as exc:
        raise InvalidWebhookSignature(f"Could not verify PayPal signature: {exc}") from exc
    finally:
        if close_client:
            client.close()


def _nested_amount(resource: dict[str, Any]) -> tuple[float, str]:
    amount = resource.get("amount") or resource.get("seller_receivable_breakdown", {}).get("gross_amount") or {}
    if isinstance(amount, dict):
        value = amount.get("value") or amount.get("total")
        currency = amount.get("currency_code") or amount.get("currency") or "USD"
        if value is not None:
            return float(value), str(currency)
    purchase = resource.get("purchase_units")
    if isinstance(purchase, list) and purchase:
        amount = purchase[0].get("amount") or {}
        if amount.get("value"):
            return float(amount["value"]), str(amount.get("currency_code") or "USD")
    raise PayPalError("Supported PayPal event did not contain an amount")


def normalize_event(event: dict[str, Any]) -> TransactionInput:
    event_type = str(event.get("event_type") or "")
    if event_type not in SUPPORTED_EVENTS:
        raise UnsupportedEvent(event_type or "unknown")
    resource = event.get("resource") or {}
    amount, currency = _nested_amount(resource)
    external_id = str(resource.get("id") or event.get("id") or "")
    event_id = str(event.get("id") or "")
    # Behavioural fields are not present on capture webhooks; leave them unavailable.
    return TransactionInput(
        amount=amount,
        currency=currency,
        merchant_category="online",
        channel="online",
        source="paypal_sandbox",
        external_transaction_id=external_id or None,
        paypal_event_id=event_id or None,
        hour_of_day=None,
        device_novelty=None,
        location_deviation=None,
        transaction_velocity=None,
        unusual_time=None,
    )
