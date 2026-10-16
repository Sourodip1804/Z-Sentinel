from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd

from .config import get_settings
from .feature_engineering import payload_to_frame
from .schemas import TransactionInput

logger = logging.getLogger("zsentinel")

_bundle: Optional[dict[str, Any]] = None


class ModelNotReady(Exception):
    pass


def load_model(path: Optional[str] = None) -> dict[str, Any]:
    global _bundle
    settings = get_settings()
    artifact = Path(path) if path else settings.resolved_artifact_path
    if not artifact.exists():
        raise ModelNotReady(
            f"Model artifact not found at {artifact}. Run 'python ml/train.py' before starting the API."
        )
    loaded = joblib.load(artifact)
    if "pipeline" not in loaded or "model_version" not in loaded:
        raise ModelNotReady("Artifact is missing pipeline or model_version")
    _bundle = loaded
    logger.info("Loaded model version=%s path=%s", loaded["model_version"], artifact)
    return loaded


def model_status() -> tuple[bool, Optional[str]]:
    if _bundle is None:
        return False, None
    return True, str(_bundle.get("model_version", "unknown"))


def get_bundle() -> dict[str, Any]:
    if _bundle is None:
        raise ModelNotReady(
            "Model is not loaded. Run 'python ml/train.py' and verify the model artifact is available."
        )
    return _bundle


def predict_probability(
    payload: TransactionInput,
) -> tuple[float, pd.DataFrame, dict[str, Any], list[str], list[str]]:
    bundle = get_bundle()
    frame, features, unavailable, imputed = payload_to_frame(payload)
    pipeline = bundle["pipeline"]
    raw = float(pipeline.predict_proba(frame)[0][1])
    calibrator = bundle.get("calibrator")
    probability = float(calibrator.predict([raw])[0]) if calibrator is not None else raw
    probability = min(max(probability, 0.0), 1.0)
    return probability, frame, features, unavailable, imputed
