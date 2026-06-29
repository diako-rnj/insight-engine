"""Context hygiene: the ContextResolver pattern from the Day 5 whitepaper.

Tool arguments are written with ``[[VARIABLE_NAME]]`` placeholders instead of
literal secrets or PII. This middleware resolves them from runtime state, then
environment variables, immediately before a tool call. Unresolved placeholders
are left intact and flagged — they are never silently dropped, and real values
never live in the agent's context window.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

_PLACEHOLDER = re.compile(r"\[\[([A-Z0-9_]+)\]\]")

# Patterns we redact from any free text before it reaches an LLM or a log.
_REDACTORS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[REDACTED_SSN]"),
    (re.compile(r"\b(?:\d[ -]*?){13,16}\b"), "[REDACTED_CARD]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[REDACTED_EMAIL]"),
]


@dataclass
class ContextResolver:
    """Resolves placeholders and scrubs PII. Order: runtime state → env."""

    runtime_state: dict[str, str] = field(default_factory=dict)
    audit_log: list[dict] = field(default_factory=list)

    def resolve(self, value: str) -> str:
        """Replace ``[[VAR]]`` tokens. Logs resolution outcome for audit."""
        def _sub(match: re.Match) -> str:
            key = match.group(1)
            resolved = self.runtime_state.get(key) or os.getenv(key)
            self.audit_log.append(
                {"key": key, "resolved": resolved is not None, "source":
                 "state" if key in self.runtime_state else ("env" if os.getenv(key) else "none")}
            )
            # Leave unresolved placeholders visible rather than failing silently.
            return resolved if resolved is not None else match.group(0)

        return _PLACEHOLDER.sub(_sub, value)

    def resolve_args(self, args: dict) -> dict:
        """Resolve placeholders across all string values in a tool-arg dict."""
        return {
            k: (self.resolve(v) if isinstance(v, str) else v) for k, v in args.items()
        }

    @staticmethod
    def scrub(text: str) -> str:
        """Strip obvious PII from free text before it enters context or logs."""
        for pattern, repl in _REDACTORS:
            text = pattern.sub(repl, text)
        return text

    def unresolved(self) -> list[str]:
        """Keys that could not be resolved this session (audit/QA aid)."""
        return [e["key"] for e in self.audit_log if not e["resolved"]]
