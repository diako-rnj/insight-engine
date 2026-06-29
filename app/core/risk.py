"""Risk assessment core.

Computes the metric table from the spec. Honours the insufficient-history
contract: with fewer than 60 trading days it flags unreliability and attaches
explicit confidence warnings rather than emitting misleading numbers silently.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

TRADING_DAYS = 252


@dataclass
class RiskReport:
    metrics: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    reliable: bool = True


def _log_returns(close: list[float]) -> list[float]:
    return [math.log(close[i] / close[i - 1]) for i in range(1, len(close))]


def assess(close: list[float], market_close: list[float] | None = None,
           risk_free_rate: float = 0.04) -> RiskReport:
    report = RiskReport()
    n = len(close)

    if n < 60:
        report.reliable = False
        report.warnings.append(
            f"Insufficient history ({n} days < 60). Metrics may be unreliable."
        )

    rets = _log_returns(close)
    if not rets:
        report.warnings.append("No returns computable.")
        return report

    mean_daily = statistics.fmean(rets)
    std_daily = statistics.pstdev(rets) or 1e-9

    # Sharpe (annualized)
    ann_return = mean_daily * TRADING_DAYS
    ann_vol = std_daily * math.sqrt(TRADING_DAYS)
    sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol else 0.0

    # VaR — historical (empirical percentile) and parametric (normal)
    srt = sorted(rets)

    def hist_var(p: float) -> float:
        idx = max(0, min(len(srt) - 1, int((1 - p) * len(srt))))
        return -srt[idx]

    def param_var(z: float) -> float:
        return -(mean_daily - z * std_daily)

    # Max drawdown (peak-to-trough on price)
    peak, max_dd = close[0], 0.0
    for px in close:
        peak = max(peak, px)
        max_dd = max(max_dd, (peak - px) / peak)

    # Beta vs market (covariance / market variance), if market series supplied
    beta = None
    if market_close and len(market_close) == len(close):
        mret = _log_returns(market_close)
        m_mean = statistics.fmean(mret)
        cov = statistics.fmean(
            [(rets[i] - mean_daily) * (mret[i] - m_mean) for i in range(len(rets))]
        )
        m_var = statistics.pvariance(mret) or 1e-9
        beta = round(cov / m_var, 3)

    report.metrics = {
        "sharpe_ratio": round(sharpe, 3),
        "var_95_historical": round(hist_var(0.95) * 100, 2),
        "var_95_parametric": round(param_var(1.645) * 100, 2),
        "var_99_historical": round(hist_var(0.99) * 100, 2),
        "var_99_parametric": round(param_var(2.326) * 100, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "annualized_volatility_pct": round(ann_vol * 100, 2),
        "annualized_return_pct": round(ann_return * 100, 2),
        "beta_vs_market": beta if beta is not None else "n/a (no market series)",
    }
    return report
