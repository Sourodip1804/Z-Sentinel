def calculate_risk(fraud_probability):
    risk_score = round(
        fraud_probability*100,
        2
    )
    
   
    