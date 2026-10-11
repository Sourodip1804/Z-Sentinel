import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestClassifier

MODEL_VERSION = "ZS-RF-1.0"

def built_training_data(n=10000, seed=42):
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