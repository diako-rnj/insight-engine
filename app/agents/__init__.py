"""Insight Engine agent pipeline.

Each agent is a thin, declarative wrapper around a tested core module. The
orchestration graph lives in ``app/agent.py``. This mirrors the ADK 2.0 pattern
(LlmAgent nodes + @node routing) while remaining runnable without a live model,
so the analytical contract can be unit-tested in CI.
"""
