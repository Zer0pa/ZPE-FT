#!/usr/bin/env python3
"""Gate C: pattern-search quality evaluation."""

from __future__ import annotations

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.data import generate_ohlcv_bars
from zpe_finance.patterns import (
    bars_to_tokens,
    build_confusion_set,
    canonical_pattern_library,
    inject_patterns,
)
from zpe_finance.search import PatternIndex, precision_at_k


def main() -> int:
    parser = parse_args("Pattern evaluation")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateC",
        "python3 scripts/run_pattern_eval.py",
        note="start",
    )

    bars = generate_ohlcv_bars(num_bars=220_000, seed=args.seed, tick_size=0.01)
    tokens = bars_to_tokens(bars["close"], tick_size=0.01)

    library = canonical_pattern_library()
    index_results = {}

    aggregate_scores = []

    for name, template in library.items():
        positions = [
            5_000,
            25_000,
            45_000,
            65_000,
            85_000,
            105_000,
            125_000,
            145_000,
            165_000,
            185_000,
            200_000,
            210_000,
        ]
        corpus, truth = inject_patterns(tokens, template, positions)

        # Inject near misses for confusion pressure.
        for offset, confusion in enumerate(build_confusion_set(template)):
            c_pos = 12_000 + offset * 17_000
            if c_pos + len(confusion) < len(corpus):
                corpus[c_pos : c_pos + len(confusion)] = confusion

        index = PatternIndex(corpus, k=4)
        ranked = index.search(template, top_k=10, min_score=0.75)
        p_at_10 = precision_at_k(ranked, truth, k=10, tolerance=3)
        aggregate_scores.append(p_at_10)

        index_results[name] = {
            "truth_positions": truth,
            "top_k": [{"position": r.position, "score": r.score} for r in ranked],
            "p_at_10": p_at_10,
        }

    mean_p_at_10 = sum(aggregate_scores) / max(1, len(aggregate_scores))

    report = {
        "claim_id": "FT-C004",
        "threshold": 0.85,
        "mean_p_at_10": mean_p_at_10,
        "pass": mean_p_at_10 >= 0.85,
        "taxonomy_reference": "FinTSB 4-category mapping via canonical templates",
        "pattern_results": index_results,
    }

    write_json(artifact_root / "ft_pattern_search_eval.json", report)

    append_command_log(
        artifact_root,
        "GateC",
        "write ft_pattern_search_eval.json",
        note=f"mean_p_at_10={mean_p_at_10:.4f}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
