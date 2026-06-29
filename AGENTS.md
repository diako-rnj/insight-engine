# AGENTS.md — Insight Engine

Cross-tool context for AI coding agents (Antigravity, Claude Code, Codex, etc.).
Project DNA lives here so instructions don't fragment across tools.

## What this is
A multi-agent financial analysis pipeline: ticker + question → forecast +
anomalies + risk → report → HITL gate → distribution. Spec-driven; the spec in
`specs/insight_engine_spec.md` is the source of truth.

## Architecture rules
- Each agent in `app/agents/` is a thin wrapper over a tested core module in
  `app/core/`. Keep analytical logic in `core`, orchestration in `agent.py`.
- Every analytical function must degrade gracefully when an optional library is
  absent. The pipeline must always return a result; it must never hard-fail on a
  missing dependency or credential.
- Forecasts always carry confidence bands + MAPE. Anomaly detection never
  fabricates anomalies. Risk metrics declare reliability.

## Security rules (non-negotiable)
- No secrets or PII in code. Use `[[VARIABLE]]` placeholders + ContextResolver.
- Every outbound action passes PolicyServer.check() before any MCP call.
- The HITL checkpoint must run before any external distribution. No bypass.

## Conventions
- Python 3.11+, Google-style docstrings.
- Directories snake_case; skill names kebab-case.
- Pin library versions (model cutoff causes stale suggestions).

## Commands
- Run:   `python -m app.run --ticker AAPL --months 6`
- Tests: `pytest -q`
- Eval:  `python -m tests.eval.grade`
