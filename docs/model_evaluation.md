# Model evaluation

## Data source

If `ml/data/labeled_transactions.csv` is absent, `ml/train.py` builds a **synthetic** labelled set written to `ml/data/synthetic_transactions.csv`.

Public credit-card corpora (for example PCA-transformed Kaggle files) do not match this project's merchant, device, location, and velocity contract, so they are not silently remapped.

Treat all metrics from the synthetic set as development diagnostics. Do **not** claim validated real-world fraud performance.

## Protocol

- Stratified train / validation / test (70 / 15 / 15).
- Class weighting on the training split only (and XGBoost `scale_pos_weight` from train counts).
- Models compared on validation PR-AUC (primary under imbalance), plus precision, recall, F1, ROC-AUC, FPR, FNR, confusion matrix.
- Isotonic calibration fit on **validation** raw scores only.
- HIGH threshold tuned on validation to keep FPR ≤ 8% when possible; MEDIUM is 45% of that HIGH threshold (prototype policy).
- Test metrics are computed once after selection.

## Artifact

`ml/artifacts/zsentinel_pipeline_v1.joblib` contains:

- `pipeline` (preprocess + selected estimator)
- `calibrator` (isotonic or `None`)
- `model_version`
- `medium_threshold` / `high_threshold`
- `data_source`

The API never retrains on a request. Re-run `python ..\ml\train.py` from `backend` only when you intentionally replace the artifact.

Open `ml/artifacts/evaluation.json` after training for the actual numbers from your machine.
