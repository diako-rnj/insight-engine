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
        # pyrefly: ignore [missing-import]
        import matplotlib

        matplotlib.use("Agg")
        # pyrefly: ignore [missing-import]
        import matplotlib.pyplot as plt
        # pyrefly: ignore [missing-import]
        import matplotlib.patches as mpatches
    except Exception:
        return False

    opens = data["open"]
    highs = data["high"]
    lows = data["low"]
    close = data["close"]
    x_hist = list(range(len(close)))
    x_fc = list(range(len(close), len(close) + forecast["horizon"]))

    fig, ax = plt.subplots(figsize=(11, 5))

    # 1. Candlesticks
    up_idx = [i for i, (o, c) in enumerate(zip(opens, close)) if c >= o]
    down_idx = [i for i, (o, c) in enumerate(zip(opens, close)) if c < o]

    ax.vlines(
        up_idx,
        [lows[i] for i in up_idx],
        [highs[i] for i in up_idx],
        color="#26a69a",
        linewidth=1,
        zorder=2,
    )
    ax.vlines(
        down_idx,
        [lows[i] for i in down_idx],
        [highs[i] for i in down_idx],
        color="#ef5350",
        linewidth=1,
        zorder=2,
    )

    width = 0.8 if len(close) <= 60 else 0.5
    ax.bar(
        up_idx,
        [close[i] - opens[i] for i in up_idx],
        bottom=[opens[i] for i in up_idx],
        color="#26a69a",
        width=width,
        zorder=3,
    )
    ax.bar(
        down_idx,
        [opens[i] - close[i] for i in down_idx],
        bottom=[close[i] for i in down_idx],
        color="#ef5350",
        width=width,
        zorder=3,
    )

    # 2. Forecast
    ax.plot(
        x_fc,
        forecast["point"],
        label="Forecast",
        linestyle="--",
        color="#2962ff",
        zorder=4,
    )
    ax.fill_between(
        x_fc,
        forecast["lower"],
        forecast["upper"],
        alpha=0.2,
        color="#2962ff",
        label="95% CI",
        zorder=1,
    )

    # 3. Anomalies
    for a in anomalies["anomalies"]:
        if a["index"] < len(close):
            # Place the marker slightly above the high
            y_pos = highs[a["index"]] * 1.01
            ax.scatter(
                [a["index"]], [y_pos], color="#d50000", zorder=5, marker="v", s=60
            )

    # Legend
    handles, labels = ax.get_legend_handles_labels()
    handles.append(mpatches.Patch(color="#26a69a", label="Bullish"))
    handles.append(mpatches.Patch(color="#ef5350", label="Bearish"))

    ax.set_title(f"{data['ticker']} — Price, Forecast, Anomalies")
    ax.set_xlabel("Trading day")
    ax.set_ylabel("Price")
    ax.legend(handles=handles, loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return True


def _exec_summary(
    data: dict, forecast: dict, anomalies: dict, risk: dict, critique: dict
) -> str:
    last = data["close"][-1]
    target = forecast["point"][-1]
    direction = "upside" if target > last else "downside"
    pct = (target - last) / last * 100
    a_line = (
        f"{anomalies['count']} statistically significant anomaly(ies) flagged"
        if anomalies["found"]
        else "No statistically significant anomalies detected"
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


def run(
    data: dict, forecast: dict, anomalies: dict, risk: dict, critique: dict, cfg: Config
) -> dict:
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
        lines += [
            f"![{data['ticker']} chart]({os.path.relpath(chart_path, cfg.reports_dir)})",
            "",
        ]
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
            lines.append(
                f"| {a['date']} | {a['kind']} | {a['severity']} | {a['detail']} |"
            )
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
        "## Methodology",
        "",
        "This report was generated using a multi-agent quantitative analysis pipeline:",
        "- **Forecasting**: An ensemble of ARIMA and Prophet models was used to project the future price action. The 95% confidence intervals represent the statistical bounds within which the price is expected to fluctuate.",
        "- **Anomaly Detection**: Unusual trading activity was flagged by evaluating rolling Z-scores for volume spikes, and Bollinger Band analysis to detect extreme price deviations beyond 2 standard deviations from the moving average.",
        "- **Risk Evaluation**: The Sharpe Ratio measures risk-adjusted return, comparing the asset's performance to the risk-free rate. Value at Risk (VaR) estimates the maximum potential loss over a specific timeframe with a 95% confidence level. Max Drawdown represents the largest historical drop from a peak to a trough.",
        "",
        "## Legal Disclaimer",
        "",
        "**STRICTLY CONFIDENTIAL & FOR INFORMATIONAL PURPOSES ONLY.**",
        "",
        "This document and its contents have been generated by an automated Artificial Intelligence (AI) agent. The analysis, forecasts, and metrics presented herein are derived entirely from mathematical models and historical data. **They do not constitute financial advice, investment recommendations, or an offer to buy/sell any securities.**",
        "",
        "Financial markets are inherently volatile and unpredictable. Model-based forecasts are estimates and are not guarantees of future performance. Past performance is not indicative of future results. The user assumes full responsibility for any trading or investment decisions made based on this report.",
        "",
        "Please consult a certified financial advisor or professional before executing any trades or investments.",
        "",
        "---",
        "*Generated by Insight Engine Core.*",
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
