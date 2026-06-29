"""Forecasting Agent — ARIMA + Prophet ensemble with confidence bands."""
from __future__ import annotations

from app.core.config import Config
from app.core.forecasting import forecast


def run(data: dict, cfg: Config) -> dict:
    fc = forecast(data["close"], horizon=cfg.forecast_horizon_days)
    return {
        "method": fc.method,
        "horizon": fc.horizon,
        "point": fc.point,
        "lower": fc.lower,
        "upper": fc.upper,
        "mape": fc.mape,
        "trend": fc.trend,
        "residual": fc.residual,
    }
