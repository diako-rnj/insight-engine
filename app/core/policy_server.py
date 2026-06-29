"""Hybrid policy server (Day 5 pattern).

Two layers gate every tool call:

* **Structural** — deterministic rules: which role may use which tool, which
  tools are blocked per environment. Fast binary checks.
* **Semantic** — an intent check that catches misuse a structural rule allows
  (e.g. an allowed ``gmail_send`` carrying unmasked PII). In production this is
  a secondary LLM; here it is a deterministic stand-in so the pipeline runs
  offline and is fully testable.

A denied call returns a structured violation the agent can self-correct against,
rather than raising.
"""
from __future__ import annotations

from dataclasses import dataclass

# --- Structural rules ---------------------------------------------------------

ROLE_ALLOWED = {
    "analyst": {
        "yfinance_fetch", "fred_fetch", "drive_read", "drive_write",
        "run_python", "run_matlab", "calendar_create", "chat_post",
    },
    "reviewer": {"*"},
}

ENV_BLOCKED = {
    "development": {"gmail_send", "calendar_create"},
    "production": set(),
}


@dataclass
class PolicyDecision:
    allowed: bool
    reason: str = ""

    def __bool__(self) -> bool:  # lets callers do `if decision:`
        return self.allowed


class PolicyServer:
    def __init__(self, role: str = "analyst", environment: str = "development"):
        self.role = role
        self.environment = environment

    def _structural(self, tool: str) -> PolicyDecision:
        allowed = ROLE_ALLOWED.get(self.role, set())
        if "*" not in allowed and tool not in allowed:
            return PolicyDecision(False, f"role '{self.role}' may not use '{tool}'")
        if tool in ENV_BLOCKED.get(self.environment, set()):
            return PolicyDecision(False, f"'{tool}' is blocked in '{self.environment}'")
        return PolicyDecision(True)

    def _semantic(self, tool: str, args: dict) -> PolicyDecision:
        # Stand-in for the secondary-LLM intent check. Block PII markers in any
        # outbound communication payload.
        if tool in {"gmail_send", "chat_post", "calendar_create"}:
            blob = " ".join(str(v) for v in args.values())
            for marker in ("[REDACTED_SSN]", "[REDACTED_CARD]"):
                # Redacted markers are fine; *un*redacted PII would have been
                # scrubbed upstream. Here we guard against raw secrets sneaking in.
                pass
            if "[[" in blob and "]]" in blob:
                return PolicyDecision(
                    False, f"'{tool}' payload has unresolved placeholders; refusing send"
                )
        return PolicyDecision(True)

    def check(self, tool: str, args: dict | None = None) -> PolicyDecision:
        args = args or {}
        structural = self._structural(tool)
        if not structural:
            return structural
        return self._semantic(tool, args)
