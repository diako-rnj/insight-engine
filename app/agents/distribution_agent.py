"""Distribution Agent — HITL checkpoint, then policy-gated MCP distribution.

Implements the spec's security contract:
* Execution PAUSES at a checkpoint that previews exactly what would go out
  (report summary, Gmail recipient, Drive destination, calendar event).
* Nothing leaves until an explicit approval is supplied.
* Every action is screened by the PolicyServer and its args resolved by the
  ContextResolver before the MCP client is ever called.
* On rejection, the report is kept locally only and the decision is logged.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import Config
from app.core.context_resolver import ContextResolver
from app.core.mcp_client import get_mcp_client
from app.core.policy_server import PolicyServer


@dataclass
class Checkpoint:
    """The HITL preview presented to the human before any external action."""

    summary_preview: str
    gmail_recipient: str
    drive_destination: str
    calendar_event: str
    channels: list[str] = field(default_factory=list)


def build_checkpoint(report: dict, cfg: Config) -> Checkpoint:
    preview = " ".join(report["summary"].split()[:200])
    channels = [
        c for c in ("drive", "gmail", "calendar", "chat") if cfg.channel_enabled(c)
    ]
    return Checkpoint(
        summary_preview=preview,
        gmail_recipient=cfg.gmail_recipient or "[[GMAIL_RECIPIENT]]",
        drive_destination=cfg.drive_folder or "[[DRIVE_FOLDER]]",
        calendar_event=f"Follow-up review: {report['report_path']}",
        channels=channels,
    )


def distribute(
    report: dict, cfg: Config, *, approved: bool, feedback: str = ""
) -> dict:
    """Run distribution iff approved. Returns an audit record either way."""
    if not approved:
        return {
            "status": "rejected",
            "feedback": feedback,
            "external_actions": [],
            "note": "Report saved locally only; no external action taken.",
        }

    policy = PolicyServer(role="analyst", environment=cfg.environment)
    resolver = ContextResolver(
        runtime_state={
            k: v
            for k, v in {
                "GMAIL_RECIPIENT": cfg.gmail_recipient,
                "DRIVE_FOLDER": cfg.drive_folder,
            }.items()
            if v
        }
    )
    client = get_mcp_client()
    actions: list[dict] = []

    plan = [
        (
            "drive",
            "drive_write",
            {
                "folder": "[[DRIVE_FOLDER]]",
                "filename": report["report_path"].split("/")[-1],
                "content_path": report["report_path"],
            },
        ),
        (
            "gmail",
            "gmail_send",
            {
                "to": "[[GMAIL_RECIPIENT]]",
                "subject": "Insight Engine — analysis complete",
                "body": ContextResolver.scrub(report["summary"]),
            },
        ),
        (
            "calendar",
            "calendar_create",
            {
                "title": "Insight Engine follow-up review",
                "in_days": 7,
            },
        ),
        ("chat", "chat_post", {"text": "Analysis complete ✅"}),
    ]

    for channel, tool, raw_args in plan:
        if not cfg.channel_enabled(channel):
            actions.append({"channel": channel, "status": "skipped (not configured)"})
            continue
        args = resolver.resolve_args(raw_args)
        decision = policy.check(tool, args)
        if not decision:
            actions.append(
                {"channel": channel, "status": f"blocked: {decision.reason}"}
            )
            continue
        result = getattr(client, tool)(**args)
        actions.append(
            {"channel": channel, "status": result.status, "action": result.action}
        )

    return {
        "status": "distributed",
        "external_actions": actions,
        "unresolved_placeholders": resolver.unresolved(),
    }
