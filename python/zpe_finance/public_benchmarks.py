"""Helpers for executed public-market benchmark runs."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from .codec import (
    decode_ohlcv,
    decode_ticks,
    encode_ohlcv,
    encode_ticks,
    raw_bytes_ohlcv,
    raw_bytes_tick,
)
from .metrics import rmse_ticks
from .patterns import bars_to_tokens, ticks_to_tokens
from .search import PatternIndex


def _percentile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    index = int(round((len(ordered) - 1) * q))
    index = max(0, min(index, len(ordered) - 1))
    return float(ordered[index])


def _ratio(raw_bytes: int, compressed_bytes: int) -> float:
    if compressed_bytes <= 0:
        return 0.0
    return float(raw_bytes) / float(compressed_bytes)


def _improvement(baseline_value: float, zpe_value: float) -> float:
    if zpe_value <= 0:
        return 0.0
    return float(baseline_value) / float(zpe_value)


def _select_pattern(tokens: np.ndarray, desired_length: int) -> np.ndarray:
    token_count = int(len(tokens))
    if token_count == 0:
        raise ValueError("token stream is empty")

    if token_count == 1:
        return np.asarray(tokens[:1], dtype=np.uint8)

    length = max(2, min(int(desired_length), token_count))
    start = max(0, min(token_count - length, token_count // 3))
    return np.asarray(tokens[start : start + length], dtype=np.uint8)


def _strictly_increasing_timestamps(values: Sequence[int]) -> np.ndarray:
    timestamps = np.asarray(values, dtype=np.int64).reshape(-1).copy()
    if len(timestamps) == 0:
        return timestamps

    for index in range(1, len(timestamps)):
        if timestamps[index] <= timestamps[index - 1]:
            timestamps[index] = timestamps[index - 1] + 1
    return timestamps


def _token_case(delta_sql: str) -> str:
    return (
        f"CASE "
        f"WHEN {delta_sql} <= -8 THEN 0 "
        f"WHEN {delta_sql} <= -3 THEN 1 "
        f"WHEN {delta_sql} <= -1 THEN 2 "
        f"WHEN {delta_sql} = 0 THEN 3 "
        f"WHEN {delta_sql} = 1 THEN 4 "
        f"WHEN {delta_sql} <= 3 THEN 5 "
        f"WHEN {delta_sql} <= 7 THEN 6 "
        f"ELSE 7 END"
    )


def _quote_sql_path(path: Path) -> str:
    return str(path).replace("'", "''")


def _write_parquet(frame: Any, path: Path) -> int:
    import duckdb  # type: ignore

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()

    conn = duckdb.connect()
    try:
        conn.register("frame_view", frame)
        conn.execute(
            f"COPY frame_view TO '{_quote_sql_path(path)}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
    finally:
        conn.close()

    return int(path.stat().st_size)


def _measure_exact_search(tokens: np.ndarray, pattern: np.ndarray, repetitions: int) -> dict[str, Any]:
    samples: list[float] = []
    hits = 0
    index = PatternIndex(tokens, k=4)
    for _ in range(max(1, int(repetitions))):
        start = time.perf_counter()
        positions = index.exact_search(pattern.tolist())
        samples.append((time.perf_counter() - start) * 1000.0)
        hits = len(positions)

    return {
        "pattern": [int(value) for value in pattern.tolist()],
        "length": int(len(pattern)),
        "hits": int(hits),
        "p50_ms": _percentile(samples, 0.50),
        "p95_ms": _percentile(samples, 0.95),
        "best_ms": min(samples) if samples else 0.0,
    }


def _build_parquet_pattern_query(path: Path, kind: str, tick_size: float, pattern: np.ndarray) -> str:
    price_expr = "close" if kind == "ohlcv" else "((bid + ask) * 0.5)"
    joins = []
    for offset, token in enumerate(pattern.tolist()[1:], start=1):
        joins.append(
            f"JOIN tokens t{offset} ON t{offset}.rid = t0.rid + {offset} AND t{offset}.token = {int(token)}"
        )

    join_sql = "\n".join(joins)
    path_sql = _quote_sql_path(path)
    first_token = int(pattern[0])

    return f"""
WITH priced AS (
  SELECT
    row_id AS rid,
    CAST(ROUND(({price_expr}) / {tick_size}) AS BIGINT) AS px
  FROM read_parquet('{path_sql}')
),
deltas AS (
  SELECT
    rid,
    COALESCE(px - LAG(px) OVER (ORDER BY rid), 0) AS delta
  FROM priced
),
tokens AS (
  SELECT
    rid,
    {_token_case('delta')} AS token
  FROM deltas
)
SELECT COUNT(*) AS hits
FROM tokens t0
{join_sql}
WHERE t0.token = {first_token}
""".strip()


def _measure_parquet_query(
    frame: Any,
    path: Path,
    kind: str,
    tick_size: float,
    pattern: np.ndarray,
    repetitions: int,
) -> dict[str, Any]:
    import duckdb  # type: ignore

    parquet_bytes = _write_parquet(frame, path)
    query = _build_parquet_pattern_query(path, kind, tick_size, pattern)

    samples: list[float] = []
    hits = 0
    conn = duckdb.connect()
    try:
        for _ in range(max(1, int(repetitions))):
            start = time.perf_counter()
            result = conn.execute(query).fetchone()
            samples.append((time.perf_counter() - start) * 1000.0)
            hits = int(result[0]) if result else 0
    finally:
        conn.close()

    return {
        "file": str(path),
        "compressed_bytes": parquet_bytes,
        "compression_ratio": 0.0,
        "hits": int(hits),
        "p50_ms": _percentile(samples, 0.50),
        "p95_ms": _percentile(samples, 0.95),
        "best_ms": min(samples) if samples else 0.0,
        "query_sql": query,
    }


def _ohlcv_frame(series: Mapping[str, np.ndarray]) -> Any:
    import pandas as pd  # type: ignore

    return pd.DataFrame(
        {
            "row_id": np.arange(len(series["timestamp"]), dtype=np.int64),
            "timestamp": np.asarray(series["timestamp"], dtype=np.int64),
            "open": np.asarray(series["open"], dtype=np.float64),
            "high": np.asarray(series["high"], dtype=np.float64),
            "low": np.asarray(series["low"], dtype=np.float64),
            "close": np.asarray(series["close"], dtype=np.float64),
            "volume": np.asarray(series["volume"], dtype=np.float64),
        }
    )


def _tick_frame(series: Mapping[str, np.ndarray]) -> Any:
    import pandas as pd  # type: ignore

    return pd.DataFrame(
        {
            "row_id": np.arange(len(series["timestamp"]), dtype=np.int64),
            "timestamp": np.asarray(series["timestamp"], dtype=np.int64),
            "bid": np.asarray(series["bid"], dtype=np.float64),
            "ask": np.asarray(series["ask"], dtype=np.float64),
            "bid_size": np.asarray(series["bid_size"], dtype=np.float64),
            "ask_size": np.asarray(series["ask_size"], dtype=np.float64),
        }
    )


def aggtrades_to_tick_series(
    timestamp_ms: Sequence[int],
    price: Sequence[float],
    quantity: Sequence[float],
) -> dict[str, np.ndarray]:
    ts = _strictly_increasing_timestamps(timestamp_ms)
    px = np.asarray(price, dtype=np.float64)
    qty = np.asarray(quantity, dtype=np.float64)
    if len(ts) == 0:
        raise ValueError("aggTrades input is empty")
    if not (len(ts) == len(px) == len(qty)):
        raise ValueError("aggTrades fields must have matching length")

    return {
        "timestamp": ts,
        "bid": px.copy(),
        "ask": px.copy(),
        "bid_size": qty.copy(),
        "ask_size": qty.copy(),
    }


def run_ohlcv_benchmark(
    *,
    dataset_id: str,
    source: str,
    source_url: str,
    instrument: str,
    period: str,
    granularity: str,
    series: Mapping[str, np.ndarray],
    tick_size: float,
    workdir: Path,
    notes: str = "",
    repetitions: int = 3,
    pattern_length: int = 8,
) -> dict[str, Any]:
    payload = encode_ohlcv(series, tick_size=tick_size, instrument=instrument)
    decoded = decode_ohlcv(payload)

    count = int(len(series["timestamp"]))
    raw_bytes = raw_bytes_ohlcv(count)
    pattern = _select_pattern(bars_to_tokens(series["close"], tick_size=tick_size), pattern_length)
    zpe_query = _measure_exact_search(
        bars_to_tokens(series["close"], tick_size=tick_size),
        pattern,
        repetitions,
    )
    parquet_query = _measure_parquet_query(
        _ohlcv_frame(series),
        workdir / f"{dataset_id}.parquet",
        "ohlcv",
        tick_size,
        pattern,
        repetitions,
    )

    parquet_query["compression_ratio"] = _ratio(raw_bytes, parquet_query["compressed_bytes"])

    rmse = rmse_ticks(
        np.rint(np.asarray(series["close"], dtype=np.float64) / tick_size),
        np.rint(np.asarray(decoded["close"], dtype=np.float64) / tick_size),
    )

    return {
        "dataset_id": dataset_id,
        "status": "ok",
        "kind": "ohlcv",
        "source": source,
        "source_url": source_url,
        "instrument": instrument,
        "period": period,
        "granularity": granularity,
        "rows": count,
        "raw_bytes": raw_bytes,
        "baseline": {
            "name": "parquet_zstd_duckdb",
            **parquet_query,
        },
        "zpe": {
            "compressed_bytes": int(len(payload)),
            "compression_ratio": _ratio(raw_bytes, len(payload)),
            "query": zpe_query,
        },
        "improvement": {
            "size_vs_baseline_x": _improvement(
                parquet_query["compressed_bytes"],
                len(payload),
            ),
            "latency_vs_baseline_x": _improvement(
                parquet_query["p95_ms"],
                zpe_query["p95_ms"],
            ),
        },
        "roundtrip": {
            "close_rmse_ticks": float(rmse),
        },
        "notes": notes,
    }


def run_tick_benchmark(
    *,
    dataset_id: str,
    source: str,
    source_url: str,
    instrument: str,
    period: str,
    granularity: str,
    series: Mapping[str, np.ndarray],
    tick_size: float,
    workdir: Path,
    notes: str = "",
    repetitions: int = 3,
    pattern_length: int = 8,
) -> dict[str, Any]:
    encode_samples: list[float] = []
    decode_samples: list[float] = []
    payload = b""
    decoded: dict[str, np.ndarray] = {}
    for _ in range(max(1, int(repetitions))):
        encode_start = time.perf_counter()
        payload = encode_ticks(series, tick_size=tick_size, instrument=instrument)
        encode_samples.append((time.perf_counter() - encode_start) * 1000.0)

        decode_start = time.perf_counter()
        decoded = decode_ticks(payload)
        decode_samples.append((time.perf_counter() - decode_start) * 1000.0)

    count = int(len(series["timestamp"]))
    raw_bytes = raw_bytes_tick(count)
    tokens = ticks_to_tokens(series["bid"], series["ask"], tick_size=tick_size)
    pattern = _select_pattern(tokens, pattern_length)
    zpe_query = _measure_exact_search(tokens, pattern, repetitions)
    parquet_query = _measure_parquet_query(
        _tick_frame(series),
        workdir / f"{dataset_id}.parquet",
        "tick",
        tick_size,
        pattern,
        repetitions,
    )

    parquet_query["compression_ratio"] = _ratio(raw_bytes, parquet_query["compressed_bytes"])

    bid_rmse = rmse_ticks(
        np.rint(np.asarray(series["bid"], dtype=np.float64) / tick_size),
        np.rint(np.asarray(decoded["bid"], dtype=np.float64) / tick_size),
    )
    ask_rmse = rmse_ticks(
        np.rint(np.asarray(series["ask"], dtype=np.float64) / tick_size),
        np.rint(np.asarray(decoded["ask"], dtype=np.float64) / tick_size),
    )

    return {
        "dataset_id": dataset_id,
        "status": "ok",
        "kind": "tick",
        "source": source,
        "source_url": source_url,
        "instrument": instrument,
        "period": period,
        "granularity": granularity,
        "rows": count,
        "raw_bytes": raw_bytes,
        "baseline": {
            "name": "parquet_zstd_duckdb",
            **parquet_query,
        },
        "zpe": {
            "compressed_bytes": int(len(payload)),
            "compression_ratio": _ratio(raw_bytes, len(payload)),
            "query": zpe_query,
        },
        "improvement": {
            "size_vs_baseline_x": _improvement(
                parquet_query["compressed_bytes"],
                len(payload),
            ),
            "latency_vs_baseline_x": _improvement(
                parquet_query["p95_ms"],
                zpe_query["p95_ms"],
            ),
        },
        "roundtrip": {
            "bid_rmse_ticks": float(bid_rmse),
            "ask_rmse_ticks": float(ask_rmse),
            "encode_p95_ms": _percentile(encode_samples, 0.95),
            "decode_p95_ms": _percentile(decode_samples, 0.95),
            "timing_exact": bool(
                np.array_equal(
                    np.asarray(series["timestamp"], dtype=np.int64),
                    np.asarray(decoded["timestamp"], dtype=np.int64),
                )
            ),
        },
        "notes": notes,
    }
