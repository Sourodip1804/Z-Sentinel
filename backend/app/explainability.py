FEATURE_LABELS = {
    "amount":
        "High transaction amount",

    "device_novelty":
        "New or unusual device",

    "location_deviation":
        "Unusual location deviation",

    "transaction_velocity":
        "High transaction velocity",

    "unusual_time":
        "Unusual transaction timing",

    "merchant_risk":
        "Higher-risk merchant category",
}

def explain_transaction(
        features,
        model,
        top_n=3

):
    