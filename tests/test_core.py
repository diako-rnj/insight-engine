"""Unit tests for the analytical core modules."""

from __future__ import annotations

import math

from app.core.anomaly_detection import detect
from app.core.forecasting import forecast
from app.core.risk import assess


def _series(n=120, spike_at=84):
    import random

    rng = random.Random(42)
    closes, vols, dates = [], [], []
    p = 100.0
    for i in range(n):
        p *= math.exp(0.0005 + 0.01 * math.sin(i / 7))
        closes.append(round(p, 2))
        # Realistic volume with natural variance (real data is never flat).
        v = 5_000_000.0 + rng.gauss(0, 300_000)
        if i == spike_at:
            v += 20_000_000  # planted spike well beyond 3σ
        vols.append(max(v, 1_000_000))
        dates.append(f"d{i:03d}")
    return dates, closes, vols


def test_forecast_returns_bands_and_mape():
    _, closes, _ = _series()
    fc = forecast(closes, horizon=30)
    assert len(fc.point) == 30
    assert len(fc.lower) == len(fc.upper) == 30
    # Upper band always above lower band.
    assert all(u >= l for u, l in zip(fc.upper, fc.lower))
    assert fc.mape >= 0


def test_forecast_short_series_high_mape():
    fc = forecast([100, 101, 102, 103, 104], horizon=5)
    assert fc.mape >= 0  # never NaN/crash on tiny input


def test_anomaly_detects_planted_volume_spike():
    dates, closes, vols = _series(spike_at=84)
    rep = detect(dates, closes, vols)
    spikes = [a for a in rep.anomalies if a.kind == "volume_spike"]
    assert spikes, "should flag the planted volume spike"
    assert any(a.severity == "HIGH" for a in spikes)


def test_anomaly_no_false_storm():
    # Smooth series, no planted spike. Random noise may trip a rare >3σ bar,
    # but the detector must not produce a *storm* of false positives.
    dates, closes, vols = _series(spike_at=-1)
    rep = detect(dates, closes, vols)
    volume_flags = [a for a in rep.anomalies if a.kind == "volume_spike"]
    assert len(volume_flags) <= 2, "should not flag a storm of false spikes"
    assert "mean_close" in rep.baseline


def test_risk_metrics_present():
    _, closes, _ = _series(252)
    rep = assess(closes, risk_free_rate=0.04)
    assert rep.reliable
    for key in (
        "sharpe_ratio",
        "var_95_historical",
        "max_drawdown_pct",
        "annualized_volatility_pct",
    ):
        assert key in rep.metrics


def test_risk_insufficient_history_warns():
    rep = assess([100, 101, 99, 102, 98] * 5)  # 25 days < 60
    assert not rep.reliable
    assert any("Insufficient history" in w for w in rep.warnings)
