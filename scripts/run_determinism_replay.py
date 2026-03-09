#!/usr/bin/env python3
"""Gate D: deterministic replay verification."""

from __future__ import annotations

import argparse
import time

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.codec import encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream
from zpe_finance.metrics import sha256_bytes
from zpe_finance.patterns import bars_to_tokens, canonical_pattern_library
from zpe_finance.search import PatternIndex


def main() -> int:
    parser = parse_args("Determinism replay")
    parser.add_argument("--runs", type=int, default=5)
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateD",
        "python3 scripts/run_determinism_replay.py",
        note="start",
    )

    run_hashes = []

    for i in range(args.runs):
        run_start = time.monotonic()
        print(f"[determinism] run {i + 1}/{args.runs} start", flush=True)
        bars = generate_ohlcv_bars(num_bars=90_000, seed=args.seed, tick_size=0.01)
        ticks = generate_tick_stream(num_ticks=200_000, seed=args.seed, tick_size=0.0001)

        ohlcv_payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
        tick_payload = encode_ticks(ticks, tick_size=0.0001, instrument="EURUSD")

        tokens = bars_to_tokens(bars["close"], tick_size=0.01)
        pattern = canonical_pattern_library()["head_shoulders"]
        index = PatternIndex(tokens, k=4)
        ranked = index.search(pattern, top_k=10, min_score=0.75)

        ranked_blob = "|".join(f"{r.position}:{r.score:.6f}" for r in ranked).encode("utf-8")
        digest = sha256_bytes(ohlcv_payload + tick_payload + ranked_blob)
        run_hashes.append(
            {
                "run": i + 1,
                "digest": digest,
                "ohlcv_bytes": len(ohlcv_payload),
                "tick_bytes": len(tick_payload),
                "elapsed_sec": round(time.monotonic() - run_start, 3),
            }
        )
        print(
            f"[determinism] run {i + 1}/{args.runs} done "
            f"elapsed_sec={run_hashes[-1]['elapsed_sec']:.3f}",
            flush=True,
        )

    unique_hashes = sorted({item["digest"] for item in run_hashes})
    pass_flag = len(unique_hashes) == 1

    report = {
        "runs": args.runs,
        "hash_consistent_runs": args.runs if pass_flag else args.runs - 1,
        "required_hash_consistent_runs": 5,
        "unique_hash_count": len(unique_hashes),
        "unique_hashes": unique_hashes,
        "pass": pass_flag and args.runs >= 5,
        "run_details": run_hashes,
    }

    write_json(artifact_root / "determinism_replay_results.json", report)

    append_command_log(
        artifact_root,
        "GateD",
        "write determinism_replay_results.json",
        note=f"unique_hash_count={len(unique_hashes)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
