"""CLI entrypoint: ``python -m app.run --ticker AAPL --months 6``.

Runs the full pipeline. By default the HITL checkpoint prompts on the terminal;
pass ``--yes`` to auto-approve or ``--no`` to auto-reject (useful for demos and
CI). Live data activates with ``--live`` (requires yfinance + internet).
"""

from __future__ import annotations

import argparse
import json

from app.agent import auto_approve, auto_reject, run_pipeline, HitlDecider
from app.agents import distribution_agent
from app.core.config import CONFIG, Config


def _interactive_hitl(ckpt: distribution_agent.Checkpoint) -> tuple[bool, str]:
    print("\n" + "=" * 60)
    print("⏸  HUMAN-IN-THE-LOOP CHECKPOINT")
    print("=" * 60)
    print(f"Summary : {ckpt.summary_preview[:300]}...")
    print(f"Gmail   : {ckpt.gmail_recipient}")
    print(f"Drive   : {ckpt.drive_destination}")
    print(f"Calendar: {ckpt.calendar_event}")
    print(f"Channels: {', '.join(ckpt.channels) or '(none configured)'}")
    print("-" * 60)
    ans = input("Approve external distribution? [y/N]: ").strip().lower()
    return (ans == "y", "" if ans == "y" else "human rejected at checkpoint")


def main() -> None:
    parser = argparse.ArgumentParser(description="Insight Engine pipeline")
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--months", type=int, default=6)
    parser.add_argument("--yes", action="store_true", help="auto-approve HITL")
    parser.add_argument("--no", action="store_true", help="auto-reject HITL")
    parser.add_argument("--json", action="store_true", help="print full result as JSON")
    args = parser.parse_args()

    cfg = Config(use_live_data=True)

    hitl: HitlDecider
    if args.yes:
        hitl = auto_approve
    elif args.no:
        hitl = auto_reject
    else:
        hitl = _interactive_hitl

    result = run_pipeline(args.ticker, args.months, cfg, hitl=hitl)

    if args.json:
        # Trim large arrays for readability.
        slim = dict(result)
        slim["forecast"] = {
            k: v
            for k, v in result["forecast"].items()
            if k not in ("trend", "residual")
        }
        print(json.dumps(slim, indent=2, default=str))
        return

    print("\n" + "=" * 60)
    print(f"INSIGHT ENGINE — {result['ticker']}  (data: {result['data_source']})")
    print("=" * 60)
    print("Trace:", " → ".join(result["trace"]))
    print("\n" + result["report"]["summary"])
    print(f"\nReport: {result['report']['report_path']}")
    print(f"Distribution: {result['distribution']['status']}")


if __name__ == "__main__":
    main()
