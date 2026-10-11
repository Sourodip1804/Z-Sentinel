import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

MODEL_VERSION = "ZS-RF-1.0"

def build_training_data(n=10000, seed=42):
    rng = np.random.default_rng(seed)
    amount = rng.lognormal(
        mean=7.0,
        sigma=1.0,
        size=n
    )

    amount = np.clip(
        amount,
        10,
        100000
    )

    device_novelty = rng.binomial(
        1,
        0.15,
        n
    )

    location_deviation = rng.beta(
        1.5,
        5,
        n
    )

    transaction_velocity = (
        rng.poisson(2, n) + 1
    )

    unusual_time = rng.binomial(
        1,
        0.12,
        n
    )

    merchant_risk = rng.beta(
        2,
        5,
        n
    )

    amount_risk = np.clip(
        (amount - 5000) / 20000,
        0,
        1
    )

    logit = (
        -4.0
        + 2.8 * amount_risk
        + 2.2 * device_novelty
        + 2.0 * location_deviation
        + 0.22 * transaction_velocity
        + 1.7 * unusual_time
        + 2.0 * merchant_risk
    )

    probability = 1 / (
        1 + np.exp(-logit)
    )

    y = rng.binomial(
        1,
        probability
    )

    X = pd.DataFrame({
        "amount": amount,
        "device_novelty": device_novelty,
        "location_deviation": location_deviation,
        "transaction_velocity": transaction_velocity,
        "unusual_time": unusual_time,
        "merchant_risk": merchant_risk,
    })

    return X, y