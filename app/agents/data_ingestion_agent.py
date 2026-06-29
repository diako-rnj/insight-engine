"""Data Ingestion Agent — fetches OHLCV (+ optional market proxy) for analysis."""
from __future__ import annotations

from app.core.config import Config
from app.core.data_ingestion import Series, ingest


def run(ticker: str, months: int, cfg: Config) -> dict:
    series: Series = ingest(
        ticker, months, use_live=cfg.use_live_data, cache_path=cfg.cache_path
    )
    # Market proxy for beta (S&P 500). Reuses the same hybrid path.
    market = ingest("SPY", months, use_live=cfg.use_live_data, cache_path=cfg.cache_path)
    return {
        "ticker": series.ticker,
        "source": series.source,
        "n_days": len(series),
        "dates": series.dates,
        "close": series.close,
        "volume": series.volume,
        "market_close": market.close if len(market) == len(series) else None,
    }
