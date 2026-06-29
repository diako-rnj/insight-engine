"""Data ingestion: hybrid live + cached + synthetic.

Resolution order:
1. If ``--live`` and ``yfinance`` is importable, fetch real OHLCV.
2. Else load a cached JSON snapshot from disk.
3. Else deterministically synthesize a realistic series so the pipeline always
   runs (and tests stay hermetic).

The output is a plain ``list[dict]`` of daily bars — no pandas required at the
ingestion boundary, which keeps the cache human-readable and the contract
simple. Downstream agents convert to arrays/frames as needed.
"""

from __future__ import annotations

import json
import math
import os
import random
from dataclasses import dataclass


@dataclass
class Series:
    ticker: str
    dates: list[str]
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    volume: list[float]
    source: str  # "live" | "cache" | "synthetic"

    def __len__(self) -> int:
        return len(self.close)


def _synthesize(ticker: str, n: int) -> Series:
    """Deterministic geometric-random-walk with a planted volume spike anomaly."""
    rng = random.Random(hash(ticker) & 0xFFFF)
    price = 150.0
    opens, highs, lows, closes, vols, dates = [], [], [], [], [], []
    for i in range(n):
        drift = 0.0004
        shock = rng.gauss(0, 0.012)

        # Open price slightly offset from previous close
        o = round(price * (1.0 + rng.gauss(0, 0.002)), 2)
        opens.append(o)

        price *= math.exp(drift + shock)
        c = round(price, 2)
        closes.append(c)

        # Wicks
        highs.append(round(max(o, c) * (1.0 + abs(rng.gauss(0, 0.005))), 2))
        lows.append(round(min(o, c) * (1.0 - abs(rng.gauss(0, 0.005))), 2))

        base_vol = 5_000_000 + rng.gauss(0, 400_000)
        # Plant one clear volume anomaly ~70% through the window.
        if i == int(n * 0.7):
            base_vol *= 4.5
        vols.append(float(round(max(base_vol, 1_000_000))))
        dates.append(f"2026-day-{i:03d}")
    return Series(ticker, dates, opens, highs, lows, closes, vols, "synthetic")


def _load_cache(path: str, ticker: str) -> Series | None:
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        blob = json.load(fh)
    rec = blob.get(ticker)
    if not rec:
        return None
    # Provide fallback to 'close' if 'open' is missing in an older cache
    return Series(
        ticker=ticker,
        dates=rec["dates"],
        open=rec.get("open", rec["close"]),
        high=rec.get("high", rec["close"]),
        low=rec.get("low", rec["close"]),
        close=[float(x) for x in rec["close"]],
        volume=[float(x) for x in rec["volume"]],
        source="cache",
    )


def _fetch_live(ticker: str, months: int) -> Series | None:
    try:
        import yfinance as yf  # noqa: WPS433 (optional dependency)
    except ImportError:
        return None
    period = f"{max(months, 1)}mo"
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    if df is None or df.empty:
        return None
    return Series(
        ticker=ticker,
        dates=[d.strftime("%Y-%m-%d") for d in df.index],
        open=[float(x) for x in df["Open"].to_list()],
        high=[float(x) for x in df["High"].to_list()],
        low=[float(x) for x in df["Low"].to_list()],
        close=[float(x) for x in df["Close"].to_list()],
        volume=[float(x) for x in df["Volume"].to_list()],
        source="live",
    )


def ingest(ticker: str, months: int, *, use_live: bool, cache_path: str) -> Series:
    """Return a price series using the hybrid resolution order described above."""
    trading_days = max(months * 21, 30)
    if use_live:
        live = _fetch_live(ticker, months)
        if live and len(live) >= 30:
            return live
    cached = _load_cache(cache_path, ticker)
    if cached and len(cached) >= 30:
        return cached
    return _synthesize(ticker, trading_days)
