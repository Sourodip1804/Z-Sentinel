# IBM Z / Machine Learning for IBM z/OS integration

This document is a **proposed** integration. This repository has not been deployed on IBM Z hardware and does not claim an MLz runtime.

## Why the split exists

Core banking posting often runs on IBM Z transaction monitors (CICS / IMS) with strict latency, audit, and residency requirements. Z-Sentinel's local FastAPI service is a portable contract: the same JSON request/response could be served by Machine Learning for IBM z/OS (MLz) after the model is converted and hosted in that environment.

## Transaction-processing boundary

1. Authorization or posting flow reaches a CICS/IMS program.
2. The program builds `txn_features_v1` from data already available **before** the financial decision.
3. It calls an inference endpoint (local FastAPI in this prototype; MLz scoring service in a future IBM Z deployment).
4. It receives `fraud_probability`, `risk_score`, `risk_level`, `decision`, `model_version`, `inference_time_ms`, and explanation factors.
5. The host program applies its own policy override if required, then writes an audit record.

Z-Sentinel's `APPROVE` / `REVIEW` / `BLOCK` values are **recommendations**. They must not silently replace host security or funds-availability checks.

## Inference contract

Request: `TransactionInput` in `backend/app/schemas.py`.  
Response: `PredictionResponse`.  
Latency: measured in-process as `inference_time_ms` on the scoring service; IBM Z deployments should also measure round-trip time in the calling transaction.

## Model versioning

Each response includes `model_version` (currently `ZS-PIPE-1.0`). MLz deployments should keep the same field so audit rows remain comparable when a champion/challenger model is swapped.

## Potential MLz integration points (not implemented)

- Export the sklearn/XGBoost pipeline to a format supported by the available MLz version.
- Host scoring beside the transaction region to avoid cross-network hops.
- Stream audit JSON to the same operational data store used by the bank, or keep MongoDB only for the datathon prototype.
- Use Workload Manager and encryption for in-flight inference traffic.

## Categories

| Category | Status |
| --- | --- |
| Local FastAPI + saved model + MongoDB + dashboard | Implemented |
| Synthetic / PayPal Sandbox events | Optional demonstration |
| IBM Z transaction region + MLz scoring | Proposed only |
