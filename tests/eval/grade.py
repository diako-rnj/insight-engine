"""Evaluation runner: scores pipeline runs against the golden dataset.

Mirrors the spec's evaluation framework — routing correctness, security
containment, metric completeness. Deterministic checks here; an LLM-as-judge
layer (rubric scoring of the report prose) is the documented extension point.

Run:  python -m tests.eval.grade
"""
from __future__ import annotations

import json
import os

from app.agent import auto_approve, auto_reject, run_pipeline
from app.core.config import Config

GOLDEN = os.path.join(os.path.dirname(__file__), "datasets", "golden.json")


def _check(case: dict) -> tuple[bool, list[str]]:
    notes: list[str] = []
    env = case.get("env", {})
    cfg = Config(
        use_live_data=False,
        cache_path="app/data/snapshot.json",
        drive_folder=env.get("DRIVE_FOLDER"),
    )
    hitl = auto_approve if case.get("hitl") == "approve" else auto_reject
    r = run_pipeline(case["input"]["ticker"], case["input"]["months"], cfg, hitl=hitl)
    exp = case["expect"]
    ok = True

    if "forecast_horizon" in exp:
        cond = r["forecast"]["horizon"] == exp["forecast_horizon"]
        ok &= cond; notes.append(f"horizon={'ok' if cond else 'FAIL'}")
    if exp.get("has_confidence_bands"):
        cond = len(r["forecast"]["lower"]) == len(r["forecast"]["point"])
        ok &= cond; notes.append(f"bands={'ok' if cond else 'FAIL'}")
    if "confidence_in" in exp:
        cond = r["critique"]["confidence"] in exp["confidence_in"]
        ok &= cond; notes.append(f"confidence={'ok' if cond else 'FAIL'}")
    if "min_anomalies" in exp:
        cond = r["anomalies"]["count"] >= exp["min_anomalies"]
        ok &= cond; notes.append(f"anomalies>={exp['min_anomalies']}:{'ok' if cond else 'FAIL'}")
    if exp.get("has_baseline_stats"):
        cond = "mean_close" in r["anomalies"]["baseline"]
        ok &= cond; notes.append(f"baseline={'ok' if cond else 'FAIL'}")
    if "required_metrics" in exp:
        cond = all(m in r["risk"]["metrics"] for m in exp["required_metrics"])
        ok &= cond; notes.append(f"metrics={'ok' if cond else 'FAIL'}")
    if "distribution_status" in exp:
        cond = r["distribution"]["status"] == exp["distribution_status"]
        ok &= cond; notes.append(f"dist={'ok' if cond else 'FAIL'}")
    if exp.get("external_actions_empty"):
        cond = r["distribution"]["external_actions"] == []
        ok &= cond; notes.append(f"no_egress={'ok' if cond else 'FAIL'}")
    if exp.get("drive_channel_present"):
        chans = {a.get("channel") for a in r["distribution"]["external_actions"]}
        cond = "drive" in chans
        ok &= cond; notes.append(f"drive={'ok' if cond else 'FAIL'}")

    return ok, notes


def main() -> None:
    with open(GOLDEN) as fh:
        cases = json.load(fh)["cases"]
    passed = 0
    print(f"Running {len(cases)} golden cases\n" + "-" * 50)
    for case in cases:
        ok, notes = _check(case)
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {case['id']:28} {' '.join(notes)}")
    print("-" * 50)
    print(f"Score: {passed}/{len(cases)} ({passed / len(cases) * 100:.0f}%)")


if __name__ == "__main__":
    main()
