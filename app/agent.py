"""Orchestrator — the agent graph.

Wires the pipeline declared in the spec:

    ingest → (forecast ‖ anomaly ‖ risk) → critique →[loop_back?]→ report → HITL → distribute

The critique node may route one loop-back to the forecasting step. The HITL gate
is represented by a callback so the same graph runs both interactively (asking a
human) and non-interactively (tests / CI supply the decision).
"""
from __future__ import annotations

from typing import Callable

from app.agents import (
    anomaly_agent,
    critique_agent,
    data_ingestion_agent,
    distribution_agent,
    forecasting_agent,
    report_agent,
    risk_agent,
)
from app.core.config import Config

# A HITL decider takes the checkpoint and returns (approved, feedback).
HitlDecider = Callable[[distribution_agent.Checkpoint], tuple[bool, str]]


def auto_approve(_ckpt) -> tuple[bool, str]:
    return True, ""


def auto_reject(_ckpt) -> tuple[bool, str]:
    return False, "auto-reject (non-interactive default)"


def run_pipeline(ticker: str, months: int, cfg: Config,
                 hitl: HitlDecider = auto_reject) -> dict:
    trace: list[str] = []

    data = data_ingestion_agent.run(ticker, months, cfg)
    trace.append(f"ingest:{data['source']}:{data['n_days']}d")

    forecast = forecasting_agent.run(data, cfg)
    anomalies = anomaly_agent.run(data, cfg)
    risk = risk_agent.run(data, cfg)
    trace.append(f"analyze:{forecast['method']}:anom={anomalies['count']}")

    critique = critique_agent.run(forecast, anomalies, risk, cfg, attempt=0)
    if critique["route"] == "loop_back":
        trace.append("critique:loop_back")
        # Single bounded retry: re-forecast then re-critique with attempt=1.
        forecast = forecasting_agent.run(data, cfg)
        critique = critique_agent.run(forecast, anomalies, risk, cfg, attempt=1)
    trace.append(f"critique:{critique['confidence']}")

    report = report_agent.run(data, forecast, anomalies, risk, critique, cfg)
    trace.append("report:written")

    checkpoint = distribution_agent.build_checkpoint(report, cfg)
    approved, feedback = hitl(checkpoint)
    trace.append(f"hitl:{'approved' if approved else 'rejected'}")

    dist = distribution_agent.distribute(report, cfg, approved=approved, feedback=feedback)
    trace.append(f"distribute:{dist['status']}")

    return {
        "ticker": ticker,
        "trace": trace,
        "data_source": data["source"],
        "forecast": forecast,
        "anomalies": anomalies,
        "risk": risk,
        "critique": critique,
        "report": {k: report[k] for k in ("report_path", "chart_path", "summary")},
        "checkpoint": checkpoint.__dict__,
        "distribution": dist,
    }
