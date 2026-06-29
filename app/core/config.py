"""Central configuration for Insight Engine.

All sensitive values come from the environment. Nothing is hardcoded. Anything
absent degrades gracefully: missing credentials disable the corresponding MCP
distribution channel rather than crashing the pipeline.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _flag(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Config:
    """Runtime configuration resolved from environment variables."""

    # Data
    use_live_data: bool = field(default_factory=lambda: _flag("USE_LIVE_DATA", default=True))
    cache_path: str = field(
        default_factory=lambda: os.getenv("CACHE_PATH", "app/data/snapshot.json")
    )
    fred_api_key: str | None = field(default_factory=lambda: os.getenv("FRED_API_KEY"))

    # Analysis
    forecast_horizon_days: int = field(
        default_factory=lambda: int(os.getenv("FORECAST_HORIZON_DAYS", "30"))
    )
    mape_threshold: float = field(
        default_factory=lambda: float(os.getenv("MAPE_THRESHOLD", "15.0"))
    )
    use_matlab: bool = field(default_factory=lambda: _flag("USE_MATLAB"))

    # Distribution / MCP
    environment: str = field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development")
    )
    gmail_recipient: str | None = field(
        default_factory=lambda: os.getenv("GMAIL_RECIPIENT")
    )
    drive_folder: str | None = field(default_factory=lambda: os.getenv("DRIVE_FOLDER"))

    # Storage
    db_path: str = field(
        default_factory=lambda: os.getenv("DB_PATH", "artifacts/history.db")
    )
    reports_dir: str = field(
        default_factory=lambda: os.getenv("REPORTS_DIR", "artifacts/reports")
    )
    charts_dir: str = field(
        default_factory=lambda: os.getenv("CHARTS_DIR", "artifacts/charts")
    )

    # Risk-free rate for Sharpe (annualized, decimal)
    risk_free_rate: float = field(
        default_factory=lambda: float(os.getenv("RISK_FREE_RATE", "0.04"))
    )

    def channel_enabled(self, channel: str) -> bool:
        """A distribution channel is enabled only if its credential is present."""
        required = {
            "gmail": self.gmail_recipient,
            "drive": True,  # local sink always available
            "calendar": self.gmail_recipient,  # uses same Workspace OAuth in practice
            "chat": _flag("CHAT_ENABLED"),
        }
        return bool(required.get(channel, False))


CONFIG = Config()
