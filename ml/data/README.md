# Training data

Z-Sentinel expects labelled rows that already match feature contract `txn_features_v1`.

Required columns:

- `amount`
- `hour_of_day`
- `device_novelty`
- `location_deviation`
- `transaction_velocity`
- `unusual_time`
- `merchant_category`
- `is_fraud` (training label only; never used at inference)

## Default development set

`ml/train.py` generates `synthetic_transactions.csv` when no public file is present.

That file is **synthetic**. Metrics computed from it are development diagnostics, not validated real-world fraud performance.

## Optional public / private labelled CSV

If you have an appropriately licensed labelled dataset mapped into this schema, save it as:

`ml/data/labeled_transactions.csv`

`train.py` will use it automatically. Do not commit datasets whose licenses forbid redistribution.
