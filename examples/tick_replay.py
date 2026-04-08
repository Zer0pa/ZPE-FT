"""Compress a real tick stream and inspect replay timing fidelity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from zpe_finance.codec import decode_ticks, encode_ticks, raw_bytes_tick
from zpe_finance.corpus import SeriesSpec, load_series_from_spec
from zpe_finance.metrics import rmse_ticks


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _tail_series(series: dict[str, np.ndarray], rows: int) -> dict[str, np.ndarray]:
    count = min(len(series["timestamp"]), max(1, int(rows)))
    return {key: np.asarray(values)[-count:] for key, values in series.items()}


def _load_series(path: Path, symbol: str, tick_size: float, rows: int) -> dict[str, np.ndarray]:
    spec = SeriesSpec(
        series_id=f"{symbol.lower()}_tick_example",
        kind="tick",
        source_path=path,
        symbol=symbol,
        tick_size=tick_size,
        provenance="repo-bundled public tick sample",
        license_note="source-specific public market sample",
        timestamp_format="iso8601",
        columns={
            "timestamp": "timestamp",
            "bid": "bid",
            "ask": "ask",
            "bid_size": "bid_size",
            "ask_size": "ask_size",
        },
    )
    return _tail_series(load_series_from_spec(spec), rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(_repo_root() / "data" / "ticks" / "eurusd_dukascopy_tick_20d_1h.csv.gz"))
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--tick-size", type=float, default=0.00001)
    parser.add_argument("--rows", type=int, default=2048)
    args = parser.parse_args()

    series = _load_series(Path(args.input), args.symbol, args.tick_size, args.rows)
    payload = encode_ticks(series, tick_size=args.tick_size, instrument=args.symbol)
    decoded = decode_ticks(payload)

    bid_rmse = rmse_ticks(
        np.rint(series["bid"] / args.tick_size),
        np.rint(decoded["bid"] / args.tick_size),
    )
    ask_rmse = rmse_ticks(
        np.rint(series["ask"] / args.tick_size),
        np.rint(decoded["ask"] / args.tick_size),
    )
    timing_exact = bool(np.array_equal(series["timestamp"], decoded["timestamp"]))
    replay_deltas = np.diff(decoded["timestamp"][: min(9, len(decoded["timestamp"]))]).astype(np.int64)

    summary = {
        "dataset": Path(args.input).name,
        "rows": int(len(series["timestamp"])),
        "raw_bytes": raw_bytes_tick(len(series["timestamp"])),
        "compressed_bytes": len(payload),
        "compression_ratio": raw_bytes_tick(len(series["timestamp"])) / len(payload),
        "bid_rmse_ticks": float(bid_rmse),
        "ask_rmse_ticks": float(ask_rmse),
        "timing_exact": timing_exact,
        "replay_deltas_ms": [int(x) for x in replay_deltas.tolist()],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
