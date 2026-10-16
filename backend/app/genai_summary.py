from __future__ import annotations

import logging
from typing import Optional

import httpx

from .config import get_settings
from .schemas import RiskFactor

logger = logging.getLogger("zsentinel")


def deterministic_summary(
    decision: str,
    risk_level: str,
    probability: float,
    factors: list[RiskFactor],
) -> str:
    top = ", ".join(f"{item.feature} ({item.direction})" for item in factors[:3]) or "no dominant factor"
    return (
        "Deterministic investigation summary (not a GenAI decision): "
        f"recommended action {decision} at {risk_level} risk "
        f"(model score {probability:.3f}). Strongest evidence: {top}. "
        "The ML model and policy engine remain authoritative."
    )


def maybe_genai_summary(
    decision: str,
    risk_level: str,
    probability: float,
    factors: list[RiskFactor],
) -> tuple[str, str]:
    fallback = deterministic_summary(decision, risk_level, probability, factors)
    settings = get_settings()
    if not settings.genai_configured:
        return fallback, "deterministic"
    evidence = [
        {
            "feature": item.feature,
            "direction": item.direction,
            "strength": item.strength,
        }
        for item in factors[:5]
    ]
    try:
        headers = {"Authorization": f"Bearer {settings.genai_api_key}"}
        payload = {
            "model": settings.genai_model or "local",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Write one short fraud-investigation paragraph from structured evidence. "
                        "Do not decide APPROVE/REVIEW/BLOCK. Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": str({"risk_level": risk_level, "score": probability, "evidence": evidence}),
                },
            ],
        }
        response = httpx.post(settings.genai_api_url, headers=headers, json=payload, timeout=8.0)
        response.raise_for_status()
        body = response.json()
        text: Optional[str] = None
        if isinstance(body, dict):
            text = (
                body.get("summary")
                or body.get("choices", [{}])[0].get("message", {}).get("content")
            )
        if not text:
            return fallback, "deterministic"
        labeled = "Generated explanatory text (not a decision): " + str(text).strip()
        return labeled, "genai"
    except Exception as exc:
        logger.warning("GenAI summary unavailable; using deterministic text")
        logger.debug("GenAI error: %s", exc)
        return fallback, "deterministic"
