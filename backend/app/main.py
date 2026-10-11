import time


from datetime import datetime

from fastapi import(
    Depends,
    FastAPI,
    HTTPException
    
)

from fastapi.middleware.cors import(
    CORSMiddleware
)

from sqlalchemy.orm import Session

from .database import (
    Base,
    engine,
    get_db
)

from .models import Transaction

from .schemas import (
    PredictionResponse,
    StatsResponse,
    TransactionInput,
    TransactionResponse
)

from .ml_model import (
    MODEL,
    MODEL_VERSION,
    predict
)

from .risk_engine import (
    calculate_risk
)

from .explainability import (
    explain_transaction
)

from .simulator import (
    generate_transaction,
    transaction_id
)

Base.metadata.create_all(bind=engine)

# creating the fastapi
app = FastAPI(
    title="Z-Sentinel API",
    description= "Real-Time AI Fraud Risk & Decision Engine",
    version="1.0.0"

)


