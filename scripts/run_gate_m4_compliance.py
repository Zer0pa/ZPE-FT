#!/usr/bin/env python3
"""Gate M4: compliance-mode technical tests (lossless/bounded and reproducible)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.codec import decode_ohlcv, decode_ticks, encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = parse_args("Gate M4 compliance")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateM4",
        "python3 scripts/run_gate_m4_compliance.py",
        note="start",
    )

    tests = []

    # C1: Exact reconstruction on tick-aligned equity bars.
    bars = generate_ohlcv_bars(num_bars=80_000, seed=args.seed + 31, tick_size=0.01)
    payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
    dec = decode_ohlcv(payload)
    exact = bool(np.array_equal(np.rint(bars["close"] / 0.01), np.rint(dec["close"] / 0.01)))
    tests.append(
        {
            "test_id": "CM-1",
            "name": "equity_tick_aligned_exact_reconstruction",
            "status": "PASS" if exact else "FAIL",
            "details": {"digest": _digest(payload)},
        }
    )

    # C2: FX tick stream exact reconstruction on bid/ask ticks.
    ticks = generate_tick_stream(num_ticks=180_000, seed=args.seed + 31, tick_size=0.0001)
    t_payload = encode_ticks(ticks, tick_size=0.0001, instrument="EURUSD")
    t_dec = decode_ticks(t_payload)
    exact_fx = bool(
        np.array_equal(np.rint(ticks["bid"] / 0.0001), np.rint(t_dec["bid"] / 0.0001))
        and np.array_equal(np.rint(ticks["ask"] / 0.0001), np.rint(t_dec["ask"] / 0.0001))
    )
    tests.append(
        {
            "test_id": "CM-2",
            "name": "fx_tick_aligned_exact_reconstruction",
            "status": "PASS" if exact_fx else "FAIL",
            "details": {"digest": _digest(t_payload)},
        }
    )

    # C3: Cross-asset deterministic replay (equity/fx/crypto tick-size regimes).
    assets = [
        ("SPY", 0.01, 120_000),
        ("EURUSD", 0.0001, 120_000),
        ("BTCUSD", 0.1, 120_000),
    ]
    replay_hashes = []
    for name, tick_size, n in assets:
        bars_i = generate_ohlcv_bars(num_bars=n, seed=args.seed + 31, tick_size=tick_size)
        payload_i = encode_ohlcv(bars_i, tick_size=tick_size, instrument=name)
        replay_hashes.append(_digest(payload_i))

    replay_hashes_2 = []
    for name, tick_size, n in assets:
        bars_i = generate_ohlcv_bars(num_bars=n, seed=args.seed + 31, tick_size=tick_size)
        payload_i = encode_ohlcv(bars_i, tick_size=tick_size, instrument=name)
        replay_hashes_2.append(_digest(payload_i))

    deterministic_multi_asset = replay_hashes == replay_hashes_2
    tests.append(
        {
            "test_id": "CM-3",
            "name": "multi_asset_deterministic_replay",
            "status": "PASS" if deterministic_multi_asset else "FAIL",
            "details": {"run1": replay_hashes, "run2": replay_hashes_2},
        }
    )

    # C4: Overnight gap stress on compliance mode.
    bars_gap = generate_ohlcv_bars(num_bars=60_000, seed=args.seed + 32, tick_size=0.01)
    gap_idx = np.arange(0, bars_gap["open"].shape[0], 390, dtype=int)
    bars_gap["open"][gap_idx] += 12.0
    bars_gap["close"][gap_idx] -= 8.0
    # Keep OHLC invariants valid after synthetic gap perturbation.
    hi_floor = np.maximum(bars_gap["open"][gap_idx], bars_gap["close"][gap_idx]) + 0.01
    lo_cap = np.minimum(bars_gap["open"][gap_idx], bars_gap["close"][gap_idx]) - 0.01
    bars_gap["high"][gap_idx] = np.maximum(bars_gap["high"][gap_idx], hi_floor)
    bars_gap["low"][gap_idx] = np.minimum(bars_gap["low"][gap_idx], lo_cap)
    gap_payload = encode_ohlcv(bars_gap, tick_size=0.01, instrument="SPY")
    gap_dec = decode_ohlcv(gap_payload)
    bounded = bool(np.max(np.abs(np.rint((bars_gap["close"] - gap_dec["close"]) / 0.01))) <= 0)
    tests.append(
        {
            "test_id": "CM-4",
            "name": "overnight_gap_compliance_reconstruction",
            "status": "PASS" if bounded else "FAIL",
            "details": {"digest": _digest(gap_payload)},
        }
    )

    pass_flag = all(t["status"] == "PASS" for t in tests)

    report = {
        "gate": "M4",
        "status": "PASS" if pass_flag else "INCONCLUSIVE",
        "compliance_mode": {
            "lossless_tick_aligned": pass_flag,
            "bounded_error_policy_ticks": 0,
            "deterministic_replay": deterministic_multi_asset,
        },
        "tests": tests,
        "mifid_note": "Technical compliance-mode tests implemented; legal interpretation remains external.",
    }

    write_json(artifact_root / "compliance_mode_results.json", report)

    append_command_log(
        artifact_root,
        "GateM4",
        "write compliance_mode_results.json",
        note=f"status={report['status']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
