"""Risk Assessment Agent — Sharpe, VaR, drawdown, beta, volatility."""

from __future__ import annotations

from app.core.config import Config
from app.core.risk import assess


def run(data: dict, cfg: Config) -> dict:
    rep = assess(
        data["close"],
        market_close=data.get("market_close"),
        risk_free_rate=cfg.risk_free_rate,
    )
    return {
        "reliable": rep.reliable,
        "warnings": rep.warnings,
        "metrics": rep.metrics,
    }
