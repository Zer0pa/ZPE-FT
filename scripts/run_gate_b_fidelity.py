#!/usr/bin/env python3
"""Gate B: encode/decode fidelity checks."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.codec import decode_ohlcv, decode_ticks, encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream
from zpe_finance.metrics import rmse_ticks


def main() -> int:
    parser = parse_args("Gate B fidelity")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateB",
        "python3 scripts/run_gate_b_fidelity.py",
        note="start",
    )

    bars = generate_ohlcv_bars(num_bars=120_000, seed=args.seed, tick_size=0.01)
    ticks = generate_tick_stream(num_ticks=300_000, seed=args.seed, tick_size=0.0001)

    ohlcv_payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
    tick_payload = encode_ticks(ticks, tick_size=0.0001, instrument="EURUSD")

    ohlcv_dec = decode_ohlcv(ohlcv_payload)
    tick_dec = decode_ticks(tick_payload)

    tick_size_bar = 0.01
    tick_size_tick = 0.0001

    bar_rmse_close = rmse_ticks(
        np.rint(bars["close"] / tick_size_bar),
        np.rint(ohlcv_dec["close"] / tick_size_bar),
    )
    bar_rmse_open = rmse_ticks(
        np.rint(bars["open"] / tick_size_bar),
        np.rint(ohlcv_dec["open"] / tick_size_bar),
    )
    bar_rmse_high = rmse_ticks(
        np.rint(bars["high"] / tick_size_bar),
        np.rint(ohlcv_dec["high"] / tick_size_bar),
    )
    bar_rmse_low = rmse_ticks(
        np.rint(bars["low"] / tick_size_bar),
        np.rint(ohlcv_dec["low"] / tick_size_bar),
    )

    tick_rmse_bid = rmse_ticks(
        np.rint(ticks["bid"] / tick_size_tick),
        np.rint(tick_dec["bid"] / tick_size_tick),
    )
    tick_rmse_ask = rmse_ticks(
        np.rint(ticks["ask"] / tick_size_tick),
        np.rint(tick_dec["ask"] / tick_size_tick),
    )

    max_rmse = max(
        bar_rmse_close,
        bar_rmse_open,
        bar_rmse_high,
        bar_rmse_low,
        tick_rmse_bid,
        tick_rmse_ask,
    )

    result = {
        "threshold_rmse_ticks": 0.5,
        "metrics": {
            "ohlcv_open_rmse_ticks": bar_rmse_open,
            "ohlcv_high_rmse_ticks": bar_rmse_high,
            "ohlcv_low_rmse_ticks": bar_rmse_low,
            "ohlcv_close_rmse_ticks": bar_rmse_close,
            "tick_bid_rmse_ticks": tick_rmse_bid,
            "tick_ask_rmse_ticks": tick_rmse_ask,
            "max_rmse_ticks": max_rmse,
        },
        "pass": max_rmse <= 0.5,
        "artifact_payload_bytes": {
            "ohlcv_payload": len(ohlcv_payload),
            "tick_payload": len(tick_payload),
        },
    }

    write_json(artifact_root / "ft_reconstruction_fidelity.json", result)

    gate_test_summary = artifact_root / "gate_b_test_results.txt"
    gate_test_summary.write_text(
        "Gate B fidelity executed\n"
        + f"max_rmse_ticks={max_rmse:.6f}\n"
        + f"pass={result['pass']}\n",
        encoding="utf-8",
    )

    append_command_log(
        artifact_root,
        "GateB",
        "write ft_reconstruction_fidelity.json",
        note=f"max_rmse_ticks={max_rmse:.6f}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
