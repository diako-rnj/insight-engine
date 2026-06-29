"""Report Writer Agent — Markdown report + chart + executive summary.

Generates a structured report from the analysis results. Charts render with
matplotlib when available; otherwise the report still produces with a note that
the chart was skipped (the pipeline never hard-fails on a plotting backend).
"""
from __future__ import annotations

import os

from app.core.config import Config


def _render_chart(data: dict, forecast: dict, anomalies: dict, path: str) -> bool:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False

    close = data["close"]
    x_hist = list(range(len(close)))
    x_fc = list(range(len(close), len(close) + forecast["horizon"]))

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(x_hist, close, label="Historical close", linewidth=1.4)
    ax.plot(x_fc, forecast["point"], label="Forecast", linestyle="--")
    ax.fill_between(x_fc, forecast["lower"], forecast["upper"], alpha=0.2,
                    label="95% CI")
    for a in anomalies["anomalies"]:
        if a["index"] < len(close):
            ax.scatter([a["index"]], [close[a["index"]]], color="red", zorder=5,
                       marker="v", s=60)
    ax.set_title(f"{data['ticker']} — price, forecast, anomalies")
    ax.set_xlabel("Trading day")
    ax.set_ylabel("Price")
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _exec_summary(data: dict, forecast: dict, anomalies: dict, risk: dict,
                  critique: dict) -> str:
    last = data["close"][-1]
    target = forecast["point"][-1]
    direction = "upside" if target > last else "downside"
    pct = (target - last) / last * 100
    a_line = (
        f"{anomalies['count']} statistically significant anomaly(ies) flagged"
        if anomalies["found"] else "No statistically significant anomalies detected"
    )
    return (
        f"{data['ticker']} closed at {last:.2f}. The {forecast['method']} model "
        f"projects {target:.2f} over {forecast['horizon']} trading days "
        f"({pct:+.1f}% {direction}), forecast confidence {critique['confidence']} "
        f"(MAPE {forecast['mape']}%). {a_line}. "
        f"Annualized volatility {risk['metrics'].get('annualized_volatility_pct')}%, "
        f"Sharpe {risk['metrics'].get('sharpe_ratio')}, "
        f"max drawdown {risk['metrics'].get('max_drawdown_pct')}%."
    )


def run(data: dict, forecast: dict, anomalies: dict, risk: dict,
        critique: dict, cfg: Config) -> dict:
    os.makedirs(cfg.reports_dir, exist_ok=True)
    os.makedirs(cfg.charts_dir, exist_ok=True)

    chart_path = os.path.join(cfg.charts_dir, f"{data['ticker']}_chart.png")
    has_chart = _render_chart(data, forecast, anomalies, chart_path)

    summary = _exec_summary(data, forecast, anomalies, risk, critique)

    lines = [
        f"# Insight Engine Report — {data['ticker']}",
        "",
        f"*Data source: {data['source']} · {data['n_days']} trading days · "
        f"forecast confidence: {critique['confidence']}*",
        "",
        "## Executive Summary",
        "",
        summary,
        "",
    ]

    if has_chart:
        lines += [f"![{data['ticker']} chart]({os.path.relpath(chart_path, cfg.reports_dir)})", ""]
    else:
        lines += ["*(Chart skipped: matplotlib backend unavailable.)*", ""]

    lines += [
        "## Forecast",
        "",
        f"- Method: `{forecast['method']}`",
        f"- Horizon: {forecast['horizon']} trading days",
        f"- Backtest MAPE: {forecast['mape']}%",
        f"- Endpoint: {forecast['point'][-1]:.2f} "
        f"(95% CI {forecast['lower'][-1]:.2f}–{forecast['upper'][-1]:.2f})",
        "",
        "## Anomaly Detection",
        "",
    ]
    if anomalies["found"]:
        lines.append("| Date | Type | Severity | Detail |")
        lines.append("|---|---|---|---|")
        for a in anomalies["anomalies"]:
            lines.append(f"| {a['date']} | {a['kind']} | {a['severity']} | {a['detail']} |")
    else:
        b = anomalies["baseline"]
        lines.append("No statistically significant anomalies detected.")
        lines.append("")
        lines.append(
            f"Baseline: mean close {b['mean_close']}, std {b['std_close']}, "
            f"mean volume {b['mean_volume']:,}, Z threshold {b['volume_z_threshold']}σ."
        )
    lines.append("")

    lines += ["## Risk Assessment", ""]
    if not risk["reliable"]:
        for w in risk["warnings"]:
            lines.append(f"> ⚠️ {w}")
        lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    for k, v in risk["metrics"].items():
        lines.append(f"| {k.replace('_', ' ').title()} | {v} |")
    lines.append("")

    if critique["issues"]:
        lines += ["## Critique Notes", ""]
        for issue in critique["issues"]:
            lines.append(f"- {issue}")
        lines.append("")

    lines += [
        "---",
        "*Generated by Insight Engine. Not investment advice. "
        "Forecasts are model estimates, not guarantees.*",
    ]

    report_md = "\n".join(lines)
    report_path = os.path.join(cfg.reports_dir, f"{data['ticker']}_report.md")
    with open(report_path, "w") as fh:
        fh.write(report_md)

    return {
        "report_path": report_path,
        "chart_path": chart_path if has_chart else None,
        "summary": summary,
        "markdown": report_md,
    }
