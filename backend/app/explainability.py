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
    importances = (
        model.feature_importances_
    )
    pairs = sorted(
        zip(
            features.columns,
            importances
        ),
        key=lambda x: x[1],
        reverse=True
    )

    active = features.iloc[0]

    factors = []

    for feature, importance in pairs:

        value = float(
            active[feature]
        )

        if (
            feature == "amount"
            and value > 5000
        ):
            factors.append(
                FEATURE_LABELS[feature]
            )

        elif (
            feature == "device_novelty"
            and value >= 0.5
        ):
            factors.append(
                FEATURE_LABELS[feature]
            )

        elif (
            feature == "location_deviation"
            and value >= 0.5
        ):
            factors.append(
                FEATURE_LABELS[feature]
            )

        elif (
            feature == "transaction_velocity"
            and value >= 5
        ):
            factors.append(
                FEATURE_LABELS[feature]
            )

        elif (
            feature == "unusual_time"
            and value >= 0.5
        ):
            factors.append(
                FEATURE_LABELS[feature]
            )

        elif (
            feature == "merchant_risk"
            and value >= 0.5
        ):
            factors.append(
                FEATURE_LABELS[feature]
            )

        if len(factors) >= top_n:
            break

    if not factors:

        factors.append(
            "No dominant abnormal factor detected"
        )

    return factors
    