"""Compress a real OHLCV series and run a native pattern query."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from zpe_finance.codec import decode_ohlcv, encode_ohlcv, raw_bytes_ohlcv
from zpe_finance.corpus import SeriesSpec, load_series_from_spec
from zpe_finance.data import try_fetch_equivalent_market_bars
from zpe_finance.metrics import rmse_ticks
from zpe_finance.search import PatternIndex


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _tail_series(series: dict[str, np.ndarray], rows: int) -> dict[str, np.ndarray]:
    count = min(len(series["timestamp"]), max(1, int(rows)))
    return {key: np.asarray(values)[-count:] for key, values in series.items()}


def _load_series(path: Path, symbol: str, tick_size: float, rows: int) -> dict[str, np.ndarray]:
    spec = SeriesSpec(
        series_id=f"{symbol.lower()}_example",
        kind="ohlcv",
        source_path=path,
        symbol=symbol,
        tick_size=tick_size,
        provenance="repo-bundled public OHLCV sample",
        license_note="source-specific public market sample",
        timestamp_format="iso8601",
        columns={
            "timestamp": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        },
    )
    return _tail_series(load_series_from_spec(spec), rows)


def _download_series(symbol: str, rows: int) -> dict[str, np.ndarray]:
    result = try_fetch_equivalent_market_bars(symbol=symbol, years=10)
    if result.status != "OK" or result.bars is None:
        raise RuntimeError(result.note)
    return _tail_series(result.bars, rows)


def _close_tokens(series: dict[str, np.ndarray], tick_size: float) -> np.ndarray:
    close_ticks = np.rint(series["close"] / tick_size).astype(np.int64)
    deltas = np.diff(close_ticks, prepend=close_ticks[0])
    return np.clip(deltas + 127, 0, 255).astype(np.uint8)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(_repo_root() / "data" / "ohlcv" / "spy_1d_24m.csv.gz"))
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--tick-size", type=float, default=0.01)
    parser.add_argument("--rows", type=int, default=512)
    parser.add_argument("--download", action="store_true", help="Fetch free daily bars via yfinance instead of bundled data")
    args = parser.parse_args()

    if args.download:
        series = _download_series(args.symbol, args.rows)
    else:
        series = _load_series(Path(args.input), args.symbol, args.tick_size, args.rows)

    payload = encode_ohlcv(series, tick_size=args.tick_size, instrument=args.symbol)
    decoded = decode_ohlcv(payload)
    rmse = rmse_ticks(
        np.rint(series["close"] / args.tick_size),
        np.rint(decoded["close"] / args.tick_size),
    )

    tokens = _close_tokens(series, args.tick_size)
    pattern_start = max(0, min(len(tokens) - 8, len(tokens) // 3))
    pattern = tokens[pattern_start : pattern_start + 8]
    index = PatternIndex(tokens, k=4)
    exact_hits = index.exact_search(pattern.tolist())

    summary = {
        "dataset": Path(args.input).name if not args.download else f"{args.symbol.lower()}_yfinance",
        "rows": int(len(series["timestamp"])),
        "raw_bytes": raw_bytes_ohlcv(len(series["timestamp"])),
        "compressed_bytes": len(payload),
        "compression_ratio": raw_bytes_ohlcv(len(series["timestamp"])) / len(payload),
        "rmse_ticks": float(rmse),
        "pattern_window": [int(x) for x in pattern.tolist()],
        "exact_hits": [int(x) for x in exact_hits[:5]],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
