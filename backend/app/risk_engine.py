def calculate_risk(fraud_probability):
    risk_score = round(
        fraud_probability*100,
        2
    )
    if fraud_probability >= 0.75:
        return(
            risk_score,
            "HIGH",
            "BLOCK"
        )
    if fraud_probability >= 0.40:
        return(
            risk_score,
            "MEDIUM",
            "REVIEW"
        )
    else:
        return(
            risk_score,
            "LOW",
            "APPROVE"
        )

   
    