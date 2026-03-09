"""Data generation and optional external ingestion."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Tuple

import numpy as np


@dataclass
class MarketFetchResult:
    status: str
    source: str
    bars: Dict[str, np.ndarray] | None
    note: str


def generate_ohlcv_bars(
    num_bars: int,
    seed: int,
    tick_size: float = 0.01,
    start_ts_ms: int = 1262304000000,
    interval_ms: int = 60_000,
    base_price: float = 300.0,
) -> Dict[str, np.ndarray]:
    if num_bars <= 0:
        raise ValueError("num_bars must be positive")

    rng = np.random.default_rng(seed)

    ts = start_ts_ms + np.arange(num_bars, dtype=np.int64) * interval_ms

    open_ticks = np.empty(num_bars, dtype=np.int64)
    high_ticks = np.empty(num_bars, dtype=np.int64)
    low_ticks = np.empty(num_bars, dtype=np.int64)
    close_ticks = np.empty(num_bars, dtype=np.int64)
    volume = np.empty(num_bars, dtype=np.float64)

    base_tick = int(round(base_price / tick_size))
    prev_close = base_tick

    for i in range(num_bars):
        is_session_open = i % 390 == 0
        overnight_gap = int(rng.integers(-12, 13)) if is_session_open and i > 0 else 0
        open_noise = int(rng.choice([-2, -1, 0, 1, 2], p=[0.05, 0.2, 0.5, 0.2, 0.05]))
        open_tick = prev_close + overnight_gap + open_noise

        body = int(rng.choice([-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6], p=[0.01, 0.02, 0.04, 0.08, 0.2, 0.3, 0.2, 0.08, 0.04, 0.02, 0.01]))
        close_tick = open_tick + body

        top_wick = int(rng.integers(0, 5))
        bot_wick = int(rng.integers(0, 5))

        high_tick = max(open_tick, close_tick) + top_wick
        low_tick = min(open_tick, close_tick) - bot_wick

        intraday_scale = 0.7 + 0.6 * abs(body)
        vol = float(max(1.0, rng.lognormal(mean=11.2 + 0.03 * intraday_scale, sigma=0.35)))

        open_ticks[i] = open_tick
        high_ticks[i] = high_tick
        low_ticks[i] = low_tick
        close_ticks[i] = close_tick
        volume[i] = vol

        prev_close = close_tick

    return {
        "timestamp": ts,
        "open": open_ticks.astype(np.float64) * tick_size,
        "high": high_ticks.astype(np.float64) * tick_size,
        "low": low_ticks.astype(np.float64) * tick_size,
        "close": close_ticks.astype(np.float64) * tick_size,
        "volume": volume,
    }


def generate_tick_stream(
    num_ticks: int,
    seed: int,
    tick_size: float = 0.0001,
    start_ts_ms: int = 1672531200000,
    base_price: float = 1.1000,
) -> Dict[str, np.ndarray]:
    if num_ticks <= 0:
        raise ValueError("num_ticks must be positive")

    rng = np.random.default_rng(seed)

    dt = rng.integers(1, 25, size=num_ticks, dtype=np.int64)
    dt[0] = 1
    ts = np.cumsum(dt, dtype=np.int64) + start_ts_ms

    bid_ticks = np.empty(num_ticks, dtype=np.int64)
    ask_ticks = np.empty(num_ticks, dtype=np.int64)
    bid_size = np.empty(num_ticks, dtype=np.float64)
    ask_size = np.empty(num_ticks, dtype=np.float64)

    bid_curr = int(round(base_price / tick_size))
    spread_curr = 2

    for i in range(num_ticks):
        jump = int(rng.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4], p=[0.01, 0.03, 0.09, 0.22, 0.30, 0.22, 0.09, 0.03, 0.01]))
        bid_curr += jump

        spread_move = int(rng.choice([-1, 0, 1], p=[0.1, 0.8, 0.1]))
        spread_curr = int(np.clip(spread_curr + spread_move, 1, 6))

        bid_ticks[i] = bid_curr
        ask_ticks[i] = bid_curr + spread_curr

        bid_size[i] = float(max(1.0, rng.lognormal(mean=3.0, sigma=0.65)))
        ask_size[i] = float(max(1.0, rng.lognormal(mean=3.0, sigma=0.65)))

    return {
        "timestamp": ts,
        "bid": bid_ticks.astype(np.float64) * tick_size,
        "ask": ask_ticks.astype(np.float64) * tick_size,
        "bid_size": bid_size,
        "ask_size": ask_size,
    }


def try_fetch_equivalent_market_bars(symbol: str = "SPY", years: int = 10) -> MarketFetchResult:
    try:
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency optional
        return MarketFetchResult(
            status="UNAVAILABLE",
            source="yfinance",
            bars=None,
            note=f"yfinance unavailable: {exc}",
        )

    def _download():
        period = f"{years}y"
        return yf.download(
            symbol,
            period=period,
            interval="1d",
            auto_adjust=False,
            progress=False,
            timeout=30,
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(_download)
            df = future.result(timeout=45)
        if df is None or len(df) == 0:
            return MarketFetchResult(
                status="UNAVAILABLE",
                source="yfinance",
                bars=None,
                note="No rows returned from yfinance",
            )

        # yfinance index is timezone-aware/naive datetime; map to epoch ms.
        ts = (
            df.index.tz_localize(timezone.utc)
            if df.index.tz is None
            else df.index.tz_convert(timezone.utc)
        )
        ts_ms = (ts.view("int64") // 1_000_000).astype(np.int64)

        bars = {
            "timestamp": ts_ms,
            "open": df["Open"].to_numpy(dtype=np.float64),
            "high": df["High"].to_numpy(dtype=np.float64),
            "low": df["Low"].to_numpy(dtype=np.float64),
            "close": df["Close"].to_numpy(dtype=np.float64),
            "volume": df["Volume"].to_numpy(dtype=np.float64),
        }

        now = datetime.now(tz=timezone.utc).isoformat()
        return MarketFetchResult(
            status="OK",
            source="yfinance",
            bars=bars,
            note=f"Fetched {len(df)} rows at {now}",
        )
    except TimeoutError:  # pragma: no cover - network timeout path
        return MarketFetchResult(
            status="UNAVAILABLE",
            source="yfinance",
            bars=None,
            note="fetch timed out after 45s",
        )
    except Exception as exc:  # pragma: no cover - network/remote failure path
        return MarketFetchResult(
            status="UNAVAILABLE",
            source="yfinance",
            bars=None,
            note=f"fetch failed: {exc}",
        )
