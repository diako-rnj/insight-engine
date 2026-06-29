"""MCP distribution client.

Defaults to a ``DryRunMCPClient`` that records intended actions instead of
performing them, so the pipeline runs with zero credentials and is safe by
default. A real client is selected automatically when credentials are present;
its actual transport (Antigravity Workspace MCP) is wired in deployment, not
committed here.

Every outbound action passes through the PolicyServer and ContextResolver
before the client is ever called — see ``distribution_agent.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MCPAction:
    channel: str
    action: str
    args: dict
    status: str = "dry_run"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class DryRunMCPClient:
    """Logs what *would* be sent. Used whenever credentials are absent."""

    def __init__(self) -> None:
        self.log: list[MCPAction] = []

    def _record(self, channel: str, action: str, args: dict) -> MCPAction:
        entry = MCPAction(channel=channel, action=action, args=args)
        self.log.append(entry)
        return entry

    def drive_write(self, **args) -> MCPAction:
        return self._record("drive", "write_file", args)

    def gmail_send(self, **args) -> MCPAction:
        return self._record("gmail", "send", args)

    def calendar_create(self, **args) -> MCPAction:
        return self._record("calendar", "create_event", args)

    def chat_post(self, **args) -> MCPAction:
        return self._record("chat", "post", args)


def get_mcp_client():
    """Return a live client if configured, else the dry-run client.

    The live branch is intentionally a stub: real Workspace MCP transport is
    configured at deploy time via ``~/.gemini/config/mcp_config.json`` and OAuth,
    never via committed code or keys.
    """
    # A real implementation would inspect configured MCP servers here.
    return DryRunMCPClient()
