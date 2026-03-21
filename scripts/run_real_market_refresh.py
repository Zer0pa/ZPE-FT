#!/usr/bin/env python3
"""Rerun the FT metric package on frozen real-market corpora."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from common import append_command_log, ensure_artifact_root, parse_args, start_comet_logger, write_json
from zpe_finance.codec import (
    decode_ohlcv,
    decode_ticks,
    encode_ohlcv,
    encode_ticks,
    raw_bytes_ohlcv,
    raw_bytes_tick,
)
from zpe_finance.corpus import load_series_from_manifest_entry
from zpe_finance.db_adapter import init_db, roundtrip_packet
from zpe_finance.metrics import rmse_ticks
from zpe_finance.patterns import bars_to_tokens, ticks_to_tokens
from zpe_finance.search import PatternIndex, precision_at_k


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((len(ordered) - 1) * p))
    return float(ordered[max(0, min(idx, len(ordered) - 1))])


def _tokens_for_series(entry: dict[str, Any], series: dict[str, np.ndarray]) -> np.ndarray:
    tick_size = float(entry["tick_size"])
    if entry["kind"] == "ohlcv":
        return bars_to_tokens(series["close"], tick_size=tick_size)
    return ticks_to_tokens(series["bid"], series["ask"], tick_size=tick_size)


def _candidate_lengths(token_count: int) -> list[int]:
    lengths = [32, 64, 128]
    valid = [length for length in lengths if length < token_count]
    if valid:
        return valid
    fallback = max(8, min(16, max(2, token_count // 2)))
    return [fallback]


def _generate_query_catalog(series_tokens: dict[str, np.ndarray], per_series: int = 8) -> dict[str, Any]:
    queries: list[dict[str, Any]] = []
    for series_id, tokens in series_tokens.items():
        token_count = len(tokens)
        lengths = _candidate_lengths(token_count)
        starts: list[int] = []
        for length in lengths:
            if token_count <= length:
                continue
            positions = np.linspace(length, token_count - length, num=per_series, dtype=int)
            for start in positions.tolist():
                starts.append(int(start))
        dedup_starts = sorted(set(starts))[:per_series]
        for idx, start in enumerate(dedup_starts):
            length = lengths[idx % len(lengths)]
            if start + length > token_count:
                continue
            queries.append(
                {
                    "query_id": f"{series_id}_auto_{idx:02d}",
                    "series_id": series_id,
                    "start_index": int(start),
                    "length": int(length),
                    "min_score": 0.75,
                }
            )
    return {
        "catalog_id": "generated_real_market_catalog",
        "status": "AUTO_GENERATED_UNSCORED",
        "queries": queries,
    }


def _load_or_generate_query_catalog(
    manifest: dict[str, Any],
    series_tokens: dict[str, np.ndarray],
    explicit_path: str,
    artifact_root: Path,
) -> tuple[dict[str, Any], str]:
    source = explicit_path or str(manifest.get("query_catalog_path", "")).strip()
    if source:
        path = Path(source).expanduser()
        if not path.is_absolute():
            path = (artifact_root / source).resolve()
        catalog = _read_json(path)
        return catalog, str(path)

    catalog = _generate_query_catalog(series_tokens)
    path = artifact_root / "starter_query_catalog.generated.json"
    write_json(path, catalog)
    return catalog, str(path)


def _evaluate_ohlcv_fidelity(
    series: dict[str, np.ndarray],
    decoded: dict[str, np.ndarray],
    tick_size: float,
) -> dict[str, float]:
    return {
        "ohlcv_open_rmse_ticks": rmse_ticks(
            np.rint(series["open"] / tick_size),
            np.rint(decoded["open"] / tick_size),
        ),
        "ohlcv_high_rmse_ticks": rmse_ticks(
            np.rint(series["high"] / tick_size),
            np.rint(decoded["high"] / tick_size),
        ),
        "ohlcv_low_rmse_ticks": rmse_ticks(
            np.rint(series["low"] / tick_size),
            np.rint(decoded["low"] / tick_size),
        ),
        "ohlcv_close_rmse_ticks": rmse_ticks(
            np.rint(series["close"] / tick_size),
            np.rint(decoded["close"] / tick_size),
        ),
    }


def _evaluate_tick_fidelity(
    series: dict[str, np.ndarray],
    decoded: dict[str, np.ndarray],
    tick_size: float,
) -> dict[str, float]:
    return {
        "tick_bid_rmse_ticks": rmse_ticks(
            np.rint(series["bid"] / tick_size),
            np.rint(decoded["bid"] / tick_size),
        ),
        "tick_ask_rmse_ticks": rmse_ticks(
            np.rint(series["ask"] / tick_size),
            np.rint(decoded["ask"] / tick_size),
        ),
    }


def main() -> int:
    parser = parse_args("Run real-market refresh")
    parser.add_argument("--manifest", required=True, help="Path to real_market_corpus_manifest.json")
    parser.add_argument("--query-catalog", default="", help="Optional query catalog override")
    parser.add_argument("--latency-repetitions", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    artifact_root = ensure_artifact_root(args.artifact_root)
    manifest_path = Path(args.manifest).expanduser().resolve()
    comet = start_comet_logger(
        artifact_root,
        "run_real_market_refresh",
        args=args,
        tags=("phase-06", "buyer-corpus", "refresh"),
        parameters={"manifest_path": str(manifest_path)},
    )
    manifest = _read_json(manifest_path)

    append_command_log(
        artifact_root,
        "EV-02",
        f"python3 scripts/run_real_market_refresh.py --manifest {manifest_path}",
        note="start",
    )

    try:
        series_entries = list(manifest.get("series", []))
        if not series_entries:
            raise ValueError("manifest contains no series")

        loaded_series: dict[str, dict[str, np.ndarray]] = {}
        series_tokens: dict[str, np.ndarray] = {}
        for entry in series_entries:
            series_id = str(entry["series_id"])
            series = load_series_from_manifest_entry(entry)
            loaded_series[series_id] = series
            series_tokens[series_id] = _tokens_for_series(entry, series)

        query_catalog, query_catalog_source = _load_or_generate_query_catalog(
            manifest,
            series_tokens,
            args.query_catalog,
            artifact_root,
        )

        ohlcv_series = []
        tick_series = []
        fidelity_series = []
        db_series = []
        latency_values: list[float] = []
        latency_series: list[dict[str, Any]] = []
        scored_queries: list[float] = []
        query_results: list[dict[str, Any]] = []

        conn = init_db(artifact_root / "real_market_roundtrip.sqlite3")
        try:
            for entry in series_entries:
                series_id = str(entry["series_id"])
                series = loaded_series[series_id]
                tick_size = float(entry["tick_size"])

                if entry["kind"] == "ohlcv":
                    payload = encode_ohlcv(series, tick_size=tick_size, instrument=str(entry["symbol"]))
                    decoded = decode_ohlcv(payload)
                    rmse_metrics = _evaluate_ohlcv_fidelity(series, decoded, tick_size)
                    ratio = raw_bytes_ohlcv(len(series["timestamp"])) / len(payload)
                    ohlcv_series.append(
                        {
                            "series_id": series_id,
                            "symbol": entry["symbol"],
                            "raw_bytes": raw_bytes_ohlcv(len(series["timestamp"])),
                            "compressed_bytes": len(payload),
                            "compression_ratio": ratio,
                            "threshold": 10.0,
                            "pass": ratio >= 10.0,
                        }
                    )
                else:
                    payload = encode_ticks(series, tick_size=tick_size, instrument=str(entry["symbol"]))
                    decoded = decode_ticks(payload)
                    rmse_metrics = _evaluate_tick_fidelity(series, decoded, tick_size)
                    ratio = raw_bytes_tick(len(series["timestamp"])) / len(payload)
                    tick_series.append(
                        {
                            "series_id": series_id,
                            "symbol": entry["symbol"],
                            "raw_bytes": raw_bytes_tick(len(series["timestamp"])),
                            "compressed_bytes": len(payload),
                            "compression_ratio": ratio,
                            "threshold": 8.0,
                            "pass": ratio >= 8.0,
                        }
                    )

                fidelity_series.append(
                    {
                        "series_id": series_id,
                        "kind": entry["kind"],
                        "metrics": rmse_metrics,
                        "max_rmse_ticks": max(rmse_metrics.values()),
                    }
                )

                db_series.append(roundtrip_packet(conn, series_id, payload))

            query_map: dict[str, list[dict[str, Any]]] = {}
            for query in list(query_catalog.get("queries", [])):
                query_map.setdefault(str(query["series_id"]), []).append(query)

            for entry in series_entries:
                series_id = str(entry["series_id"])
                tokens = series_tokens[series_id]
                index = PatternIndex(tokens, k=4)
                series_query_latencies: list[float] = []
                for query in query_map.get(series_id, []):
                    start = int(query["start_index"])
                    length = int(query["length"])
                    if start < 0 or start + length > len(tokens):
                        continue
                    pattern = tokens[start : start + length]
                    min_score = float(query.get("min_score", 0.75))
                    ranked = []
                    for _ in range(max(1, int(args.latency_repetitions))):
                        t0 = time.perf_counter()
                        ranked = index.search(pattern, top_k=args.top_k, min_score=min_score)
                        elapsed_ms = (time.perf_counter() - t0) * 1000.0
                        latency_values.append(float(elapsed_ms))
                        series_query_latencies.append(float(elapsed_ms))

                    relevant_positions = list(query.get("relevant_positions", []))
                    p_at_10 = None
                    if relevant_positions:
                        p_at_10 = precision_at_k(ranked, relevant_positions, k=args.top_k, tolerance=3)
                        scored_queries.append(p_at_10)

                    query_results.append(
                        {
                            "query_id": query["query_id"],
                            "series_id": series_id,
                            "start_index": start,
                            "length": length,
                            "relevant_positions": relevant_positions,
                            "p_at_10": p_at_10,
                            "top_k": [{"position": item.position, "score": item.score} for item in ranked],
                        }
                    )

                latency_series.append(
                    {
                        "series_id": series_id,
                        "queries": len(query_map.get(series_id, [])),
                        "latencies_ms": {
                            "p50": _percentile(series_query_latencies, 0.50),
                            "p95": _percentile(series_query_latencies, 0.95),
                            "best": min(series_query_latencies) if series_query_latencies else 0.0,
                        },
                    }
                )
        finally:
            conn.close()

        max_rmse = max((item["max_rmse_ticks"] for item in fidelity_series), default=0.0)
        mean_p_at_10 = sum(scored_queries) / len(scored_queries) if scored_queries else None
        pattern_status = "PASS" if mean_p_at_10 is not None and mean_p_at_10 >= 0.85 else "NEEDS_LABELS"
        if mean_p_at_10 is not None and mean_p_at_10 < 0.85:
            pattern_status = "FAIL"

        ohlcv_report = {
            "claim_id": "FT-C001",
            "source_manifest": str(manifest_path),
            "series": ohlcv_series,
            "threshold": 10.0,
            "aggregate": {
                "min_compression_ratio": min((item["compression_ratio"] for item in ohlcv_series), default=0.0),
                "mean_compression_ratio": (
                    sum(item["compression_ratio"] for item in ohlcv_series) / len(ohlcv_series)
                    if ohlcv_series
                    else 0.0
                ),
            },
            "pass": all(item["pass"] for item in ohlcv_series) if ohlcv_series else False,
        }

        tick_report = {
            "claim_id": "FT-C002",
            "source_manifest": str(manifest_path),
            "series": tick_series,
            "threshold": 8.0,
            "aggregate": {
                "min_compression_ratio": min((item["compression_ratio"] for item in tick_series), default=0.0),
                "mean_compression_ratio": (
                    sum(item["compression_ratio"] for item in tick_series) / len(tick_series)
                    if tick_series
                    else 0.0
                ),
            },
            "pass": all(item["pass"] for item in tick_series) if tick_series else False,
        }

        fidelity_report = {
            "threshold_rmse_ticks": 0.5,
            "metrics": {
                "max_rmse_ticks": max_rmse,
            },
            "series": fidelity_series,
            "pass": max_rmse <= 0.5,
        }

        latency_report = {
            "claim_id": "FT-C005",
            "source_manifest": str(manifest_path),
            "query_catalog_source": query_catalog_source,
            "corpus_points": int(sum(len(tokens) for tokens in series_tokens.values())),
            "queries": len(query_results),
            "latencies_ms": {
                "p50": _percentile(latency_values, 0.50),
                "p95": _percentile(latency_values, 0.95),
                "best": min(latency_values) if latency_values else 0.0,
            },
            "series": latency_series,
            "threshold_ms": 100.0,
            "pass": _percentile(latency_values, 0.95) < 100.0 if latency_values else False,
            "single_core_target": True,
        }

        pattern_report = {
            "claim_id": "FT-C004",
            "source_manifest": str(manifest_path),
            "query_catalog_source": query_catalog_source,
            "threshold": 0.85,
            "mean_p_at_10": mean_p_at_10,
            "scored_queries": len(scored_queries),
            "unscored_queries": len(query_results) - len(scored_queries),
            "status": pattern_status,
            "pass": bool(mean_p_at_10 is not None and mean_p_at_10 >= 0.85),
            "pattern_results": query_results,
        }

        db_report = {
            "claim_id": "FT-C006",
            "source_manifest": str(manifest_path),
            "series": db_series,
            "pass": all(item["bit_consistent"] for item in db_series) if db_series else False,
        }

        ohlcv_report_path = artifact_root / "ft_ohlcv_benchmark.json"
        tick_report_path = artifact_root / "ft_tick_benchmark.json"
        fidelity_report_path = artifact_root / "ft_reconstruction_fidelity.json"
        latency_report_path = artifact_root / "ft_query_latency_benchmark.json"
        pattern_report_path = artifact_root / "ft_pattern_search_eval.json"
        db_report_path = artifact_root / "ft_db_roundtrip_results.json"

        write_json(ohlcv_report_path, ohlcv_report)
        write_json(tick_report_path, tick_report)
        write_json(fidelity_report_path, fidelity_report)
        write_json(latency_report_path, latency_report)
        write_json(pattern_report_path, pattern_report)
        write_json(db_report_path, db_report)

        append_command_log(
            artifact_root,
            "EV-02",
            "write FT real-market refresh artifacts",
            note=(
                f"ohlcv_pass={ohlcv_report['pass']} "
                f"tick_pass={tick_report['pass']} "
                f"latency_p95_ms={latency_report['latencies_ms']['p95']:.4f} "
                f"pattern_status={pattern_status}"
            ),
        )
        comet.finalize(
            status="completed",
            metrics={
                "ohlcv_pass": ohlcv_report["pass"],
                "tick_pass": tick_report["pass"],
                "fidelity_pass": fidelity_report["pass"],
                "latency_pass": latency_report["pass"],
                "latency_p95_ms": latency_report["latencies_ms"]["p95"],
                "max_rmse_ticks": fidelity_report["metrics"]["max_rmse_ticks"],
                "scored_queries": pattern_report["scored_queries"],
            },
            others={
                "gate": "EV-02",
                "pattern_status": pattern_status,
                "query_catalog_source": query_catalog_source,
                "manifest_path": str(manifest_path),
            },
            assets=(
                ohlcv_report_path,
                tick_report_path,
                fidelity_report_path,
                latency_report_path,
                pattern_report_path,
                db_report_path,
                artifact_root / "starter_query_catalog.generated.json",
                artifact_root / "command_log.txt",
            ),
        )
        return 0
    except Exception as exc:
        comet.finalize(
            status="failed",
            others={
                "gate": "EV-02",
                "error": str(exc),
                "manifest_path": str(manifest_path),
            },
            assets=(artifact_root / "command_log.txt",),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
