#!/usr/bin/env python3
"""Gate C: compression benchmarks + comparator matrix."""

from __future__ import annotations

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.codec import (
    encode_ohlcv,
    encode_ticks,
    raw_bytes_ohlcv,
    raw_bytes_tick,
)
from zpe_finance.comparators import benchmark_comparators
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream


def main() -> int:
    parser = parse_args("Gate C benchmarks")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateC",
        "python3 scripts/run_gate_c_benchmarks.py",
        note="start",
    )

    bars = generate_ohlcv_bars(num_bars=500_000, seed=args.seed, tick_size=0.01)
    ticks = generate_tick_stream(num_ticks=1_000_000, seed=args.seed, tick_size=0.0001)

    ohlcv_payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
    tick_payload = encode_ticks(ticks, tick_size=0.0001, instrument="EURUSD")

    raw_ohlcv = raw_bytes_ohlcv(len(bars["timestamp"]))
    raw_tick = raw_bytes_tick(len(ticks["timestamp"]))

    ohlcv_ratio = raw_ohlcv / len(ohlcv_payload)
    tick_ratio = raw_tick / len(tick_payload)

    ohlcv_comparators = benchmark_comparators(bars["close"])
    tick_comparators = benchmark_comparators((ticks["bid"] + ticks["ask"]) * 0.5)

    ohlcv_report = {
        "claim_id": "FT-C001",
        "raw_bytes": raw_ohlcv,
        "compressed_bytes": len(ohlcv_payload),
        "compression_ratio": ohlcv_ratio,
        "threshold": 10.0,
        "stretch_threshold": 12.0,
        "pass": ohlcv_ratio >= 10.0,
        "stretch_pass": ohlcv_ratio >= 12.0,
        "comparators": ohlcv_comparators,
    }

    tick_report = {
        "claim_id": "FT-C002",
        "raw_bytes": raw_tick,
        "compressed_bytes": len(tick_payload),
        "compression_ratio": tick_ratio,
        "threshold": 8.0,
        "pass": tick_ratio >= 8.0,
        "comparators": tick_comparators,
    }

    write_json(artifact_root / "ft_ohlcv_benchmark.json", ohlcv_report)
    write_json(artifact_root / "ft_tick_benchmark.json", tick_report)

    append_command_log(
        artifact_root,
        "GateC",
        "write ft_ohlcv_benchmark.json + ft_tick_benchmark.json",
        note=f"ohlcv_cr={ohlcv_ratio:.3f}, tick_cr={tick_ratio:.3f}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
