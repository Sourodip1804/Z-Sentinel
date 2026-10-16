# Z-Sentinel architecture

Z-Sentinel is a portable inference and decision service. The live prototype runs locally with FastAPI, a saved scikit-learn pipeline, MongoDB, and a React dashboard.

```mermaid
flowchart LR
  subgraph offline [Offline]
    D[Labeled or synthetic data]
    T[train.py]
    E[evaluate.py]
    A[Versioned artifact]
    D --> T --> E --> A
  end
  subgraph online [Online prototype]
    I[API / simulator / PayPal webhook]
    V[Validation]
    F[Feature contract txn_features_v1]
    M[Loaded model]
    R[Risk policy]
    S[SHAP / model explanation]
    DB[(MongoDB audit)]
    UI[React dashboard]
    I --> V --> F --> M --> R --> S --> DB --> UI
  end
  A --> M
```

## Responsibilities

| Area | Implementation |
| --- | --- |
| Feature contract | `backend/app/feature_engineering.py` and `txn_features_v1` |
| Training | `ml/train.py` — Logistic Regression, Random Forest, optional XGBoost |
| Inference | FastAPI loads `ml/artifacts/zsentinel_pipeline_v1.joblib` once at startup |
| Decision | `backend/app/risk_engine.py` prototype thresholds |
| Explainability | SHAP Tree/Linear explainer with model-specific fallback |
| Persistence | MongoDB `transactions` collection |
| Dashboard | React + Vite consuming `/api/*` |

## Honesty boundary

1. **Implemented and tested locally:** training, API inference, SHAP factors, MongoDB audit, dashboard, pytest suite (Mongo mocked).
2. **Optional demonstration:** PayPal Sandbox webhooks when credentials and HTTPS are configured. Capture-completed events are not pre-capture blocks.
3. **Not deployed:** IBM Z / Machine Learning for IBM z/OS. See `docs/ibm_z_integration.md`.
