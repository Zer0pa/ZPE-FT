#!/usr/bin/env python3
"""Gate C: single-core pattern-query latency benchmark."""

from __future__ import annotations

import time

import numpy as np

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.data import generate_ohlcv_bars
from zpe_finance.patterns import bars_to_tokens, canonical_pattern_library
from zpe_finance.search import PatternIndex


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = int(round((len(sorted_values) - 1) * p))
    return sorted_values[max(0, min(idx, len(sorted_values) - 1))]


def main() -> int:
    parser = parse_args("Latency benchmark")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateC",
        "python3 scripts/run_latency_benchmark.py",
        note="start",
    )

    # Approximate 10-year minute corpus scale.
    bars = generate_ohlcv_bars(num_bars=1_000_000, seed=args.seed, tick_size=0.01)
    tokens = bars_to_tokens(bars["close"], tick_size=0.01)
    library = canonical_pattern_library()
    template = library["head_shoulders"]

    index = PatternIndex(tokens, k=4)

    latencies_ms = []
    for _ in range(40):
        t0 = time.perf_counter()
        _ = index.search(template, top_k=10, min_score=0.75)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(float(elapsed_ms))

    latencies_ms.sort()
    p50 = percentile(latencies_ms, 0.50)
    p95 = percentile(latencies_ms, 0.95)
    best = min(latencies_ms)

    report = {
        "claim_id": "FT-C005",
        "corpus_points": int(len(tokens)),
        "runs": len(latencies_ms),
        "latencies_ms": {
            "p50": p50,
            "p95": p95,
            "best": best,
        },
        "threshold_ms": 100.0,
        "stretch_threshold_ms": 50.0,
        "pass": p95 < 100.0,
        "stretch_pass": p95 < 50.0,
        "single_core_target": True,
    }

    write_json(artifact_root / "ft_query_latency_benchmark.json", report)

    append_command_log(
        artifact_root,
        "GateC",
        "write ft_query_latency_benchmark.json",
        note=f"p95_ms={p95:.3f}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
