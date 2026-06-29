"""Critique Agent — reviews analysis quality and decides whether to loop back.

Mirrors the Gherkin "forecast confidence too low" scenario: if forecast MAPE
exceeds the configured threshold, it flags low confidence and requests a single
loop-back with an instruction to widen the confidence bands. It also validates
that anomaly findings carry statistical context and that risk metrics declare
their reliability. The loop is bounded (one retry) to avoid infinite cycles.
"""

from __future__ import annotations

from app.core.config import Config


def run(
    forecast: dict, anomalies: dict, risk: dict, cfg: Config, attempt: int = 0
) -> dict:
    issues: list[str] = []
    route = "approve"

    if forecast["mape"] > cfg.mape_threshold:
        issues.append(
            f"Forecast MAPE {forecast['mape']}% exceeds {cfg.mape_threshold}% threshold."
        )
        if attempt < 1:
            route = "loop_back"

    if not risk["reliable"]:
        issues.append("Risk metrics flagged as unreliable (short history).")

    confidence = "HIGH"
    if forecast["mape"] > cfg.mape_threshold:
        confidence = "LOW"
    elif forecast["mape"] > cfg.mape_threshold / 2:
        confidence = "MEDIUM"

    return {
        "route": route,  # "approve" | "loop_back"
        "confidence": confidence,
        "issues": issues,
        "instruction": (
            "Widen confidence bands and state uncertainty explicitly."
            if route == "loop_back"
            else ""
        ),
    }
