from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .schemas import RiskFactor


def _direction(value: float) -> str:
    return "increases_fraud_risk" if value >= 0 else "decreases_fraud_risk"


def _clean_name(raw: str) -> str:
    name = raw
    for prefix in ("preprocess__", "num__", "cat__", "remainder__"):
        name = name.replace(prefix, "")
    return name


def explain_prediction(pipeline: Any, frame: pd.DataFrame, top_n: int = 5) -> list[RiskFactor]:
    """Local explanation grounded in the fitted model features and contributions."""
    classifier = pipeline.named_steps["model"]
    preprocess = pipeline.named_steps["preprocess"]
    transformed = preprocess.transform(frame)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    feature_names = list(preprocess.get_feature_names_out())
    method = "model_specific"
    contributions: np.ndarray | None = None

    if hasattr(classifier, "coef_"):
        # For linear models with standard-scaled features (mean = 0),
        # coef_i * x_i is the exact Shapley contribution to the log-odds decision margin.
        contributions = np.array(classifier.coef_[0], dtype=float) * np.array(
            transformed[0], dtype=float
        )
        method = "linear_shap"
    elif hasattr(classifier, "feature_importances_"):
        try:
            import shap

            explainer = shap.TreeExplainer(classifier)
            shap_values = explainer.shap_values(transformed)
            if isinstance(shap_values, list) and len(shap_values) > 1:
                contributions = np.array(shap_values[1][0], dtype=float)
            else:
                values = np.array(shap_values)
                if values.ndim == 3:
                    contributions = values[0, :, 1]
                elif values.ndim == 2:
                    contributions = values[0]
                else:
                    contributions = values
            method = "shap_tree"
        except Exception:
            row = np.array(transformed[0], dtype=float)
            contributions = np.array(classifier.feature_importances_, dtype=float) * np.sign(row + 1e-9)
            method = "tree_importance_fallback"
    else:
        return [
            RiskFactor(
                feature="unavailable",
                value=None,
                contribution=0.0,
                direction="decreases_fraud_risk",
                strength=0.0,
                method="none",
            )
        ]

    raw_values = frame.iloc[0].to_dict()
    items: list[RiskFactor] = []
    for name, contrib in zip(feature_names, contributions.flatten()):
        display = _clean_name(str(name))
        source = display.split("_")[0] if display.startswith("merchant_category") else display
        value: Any = raw_values.get(source, raw_values.get(display))
        if display.startswith("merchant_category"):
            value = raw_values.get("merchant_category")
        numeric = float(contrib)
        items.append(
            RiskFactor(
                feature=display,
                value=value if isinstance(value, (int, float, str)) else None,
                contribution=round(numeric, 6),
                direction=_direction(numeric),
                strength=round(abs(numeric), 6),
                method=method,
            )
        )
    items.sort(key=lambda item: item.strength, reverse=True)
    return items[:top_n]
