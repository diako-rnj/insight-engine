"""Behavioral tests mapping directly to the spec's Gherkin scenarios.

Each test name references the scenario it verifies so the spec stays the source
of truth and the suite doubles as living documentation.
"""
from __future__ import annotations

from app.agent import auto_approve, auto_reject, run_pipeline
from app.agents import distribution_agent
from app.core.config import Config
from app.core.policy_server import PolicyServer


def _cfg(**kw) -> Config:
    base = dict(use_live_data=False, cache_path="app/data/snapshot.json")
    base.update(kw)
    return Config(**base)


# Feature: Forecasting --------------------------------------------------------

def test_scenario_single_stock_forecast():
    """Given ticker + horizon, Then a 30-day forecast with CI is produced."""
    result = run_pipeline("AAPL", 6, _cfg(), hitl=auto_reject)
    fc = result["forecast"]
    assert fc["horizon"] == 30
    assert len(fc["point"]) == 30 and len(fc["lower"]) == 30


# Feature: Security & HITL ----------------------------------------------------

def test_scenario_hitl_blocks_until_approval():
    """Then execution pauses; on reject NO external action is taken."""
    result = run_pipeline("AAPL", 6, _cfg(), hitl=auto_reject)
    assert result["distribution"]["status"] == "rejected"
    assert result["distribution"]["external_actions"] == []


def test_scenario_hitl_approval_distributes():
    """On approve, configured channels run (drive sink always available)."""
    result = run_pipeline("AAPL", 6, _cfg(drive_folder="/Reports"), hitl=auto_approve)
    assert result["distribution"]["status"] == "distributed"
    channels = {a["channel"] for a in result["distribution"]["external_actions"]}
    assert "drive" in channels


def test_scenario_dev_env_blocks_gmail():
    """Policy: development environment blocks gmail_send."""
    p = PolicyServer(role="analyst", environment="development")
    assert not p.check("gmail_send", {"to": "x@y.com"})


def test_scenario_reviewer_role_allows_all():
    p = PolicyServer(role="reviewer", environment="production")
    assert p.check("gmail_send", {"to": "x@y.com"})


def test_scenario_unresolved_placeholder_refused():
    """Semantic gate refuses an outbound payload with unresolved placeholders."""
    p = PolicyServer(role="reviewer", environment="production")
    assert not p.check("gmail_send", {"to": "[[GMAIL_RECIPIENT]]"})


# Feature: HITL checkpoint contents ------------------------------------------

def test_scenario_checkpoint_previews_actions():
    """The checkpoint surfaces summary, recipient, drive dest, calendar event."""
    result = run_pipeline("MSFT", 6, _cfg(), hitl=auto_reject)
    ck = result["checkpoint"]
    for field in ("summary_preview", "gmail_recipient", "drive_destination",
                  "calendar_event"):
        assert field in ck


# Feature: Honest reporting ---------------------------------------------------

def test_scenario_critique_routes_and_reports_confidence():
    result = run_pipeline("AAPL", 6, _cfg(), hitl=auto_reject)
    assert result["critique"]["confidence"] in {"LOW", "MEDIUM", "HIGH"}
    assert result["critique"]["route"] in {"approve", "loop_back"}
