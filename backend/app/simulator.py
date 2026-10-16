from __future__ import annotations

import random
import uuid

from .schemas import TransactionInput

SCENARIOS = {
    "legitimate_grocery": dict(
        amount=42.15,
        merchant_category="grocery",
        hour_of_day=11,
        device_novelty=0.0,
        location_deviation=0.08,
        transaction_velocity=1,
        unusual_time=0.0,
        channel="pos",
    ),
    "high_amount_online": dict(
        amount=9800.00,
        merchant_category="online",
        hour_of_day=2,
        device_novelty=1.0,
        location_deviation=0.82,
        transaction_velocity=9,
        unusual_time=1.0,
        channel="online",
    ),
    "new_device_travel": dict(
        amount=2400.00,
        merchant_category="travel",
        hour_of_day=21,
        device_novelty=1.0,
        location_deviation=0.71,
        transaction_velocity=4,
        unusual_time=0.0,
        channel="online",
    ),
    "night_velocity": dict(
        amount=760.40,
        merchant_category="electronics",
        hour_of_day=3,
        device_novelty=0.0,
        location_deviation=0.33,
        transaction_velocity=12,
        unusual_time=1.0,
        channel="online",
    ),
    "location_spike": dict(
        amount=310.00,
        merchant_category="fuel",
        hour_of_day=18,
        device_novelty=0.0,
        location_deviation=0.94,
        transaction_velocity=3,
        unusual_time=0.0,
        channel="pos",
    ),
}


def transaction_id() -> str:
    return "TXN-" + uuid.uuid4().hex[:10].upper()


def generate_transaction(scenario: str | None = None, seed: int | None = None) -> TransactionInput:
    rng = random.Random(seed)
    name = scenario if scenario in SCENARIOS else rng.choice(list(SCENARIOS))
    payload = dict(SCENARIOS[name])
    jitter = 1 + rng.uniform(-0.08, 0.08)
    payload["amount"] = round(max(1.0, payload["amount"] * jitter), 2)
    payload["source"] = "simulator"
    payload["currency"] = "USD"
    return TransactionInput(**payload)
