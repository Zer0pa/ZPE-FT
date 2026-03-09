#!/usr/bin/env python3
"""Gate E: DB roundtrip contract test."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.codec import decode_ohlcv, decode_ticks, encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream
from zpe_finance.db_adapter import db_file_size_bytes, init_db, roundtrip_packet
from zpe_finance.metrics import rmse_ticks


def main() -> int:
    parser = parse_args("Gate E DB roundtrip")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateE",
        "python3 scripts/run_gate_e_db_roundtrip.py",
        note="start",
    )

    bars = generate_ohlcv_bars(num_bars=110_000, seed=args.seed, tick_size=0.01)
    ticks = generate_tick_stream(num_ticks=240_000, seed=args.seed, tick_size=0.0001)

    ohlcv_payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
    tick_payload = encode_ticks(ticks, tick_size=0.0001, instrument="EURUSD")

    db_path = artifact_root / "zpe_ft_wave1.sqlite3"
    conn = init_db(db_path)

    ohlcv_rt = roundtrip_packet(conn, "ohlcv_spy", ohlcv_payload)
    tick_rt = roundtrip_packet(conn, "tick_eurusd", tick_payload)

    ohlcv_dec = decode_ohlcv(ohlcv_payload)
    tick_dec = decode_ticks(tick_payload)

    ohlcv_rmse = rmse_ticks(
        np.rint(bars["close"] / 0.01),
        np.rint(ohlcv_dec["close"] / 0.01),
    )
    tick_rmse = rmse_ticks(
        np.rint(ticks["bid"] / 0.0001),
        np.rint(tick_dec["bid"] / 0.0001),
    )

    conn.close()

    pass_flag = (
        ohlcv_rt["bit_consistent"]
        and tick_rt["bit_consistent"]
        and ohlcv_rmse <= 0.5
        and tick_rmse <= 0.5
    )

    report = {
        "claim_id": "FT-C006",
        "db_backend": "sqlite3",
        "timescale_equivalence": {
            "status": "INCONCLUSIVE",
            "note": "TimescaleDB not provisioned in-lane; SQLite used as nearest local DB contract.",
            "comparability_impact": "SQL extension/operator-path equivalence not proven.",
        },
        "roundtrip": {
            "ohlcv": ohlcv_rt,
            "tick": tick_rt,
        },
        "decode_fidelity_rmse_ticks": {
            "ohlcv_close": ohlcv_rmse,
            "tick_bid": tick_rmse,
        },
        "db_file_bytes": db_file_size_bytes(db_path),
        "pass": pass_flag,
    }

    write_json(artifact_root / "ft_db_roundtrip_results.json", report)

    append_command_log(
        artifact_root,
        "GateE",
        "write ft_db_roundtrip_results.json",
        note=f"pass={pass_flag}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
