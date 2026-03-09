#!/usr/bin/env python3
"""Gate D: adversarial and malformed falsification campaigns."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from common import append_command_log, ensure_artifact_root, parse_args, write_json
from zpe_finance.codec import decode_ohlcv, decode_ticks, encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream
from zpe_finance.db_adapter import chunk_and_reorder, fault_inject_corruption, init_db, roundtrip_packet
from zpe_finance.patterns import bars_to_tokens, build_confusion_set, canonical_pattern_library
from zpe_finance.search import PatternIndex


def main() -> int:
    parser = parse_args("Gate D falsification")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateD",
        "python3 scripts/run_gate_d_falsification.py",
        note="start",
    )

    results = []
    uncaught_crashes = 0

    # DT-FT-1: gap-open + extreme volatility
    try:
        bars = generate_ohlcv_bars(num_bars=80_000, seed=args.seed + 1, tick_size=0.01)
        bars["open"][::390] += 8.0
        bars["close"][::390] -= 6.0
        bars["high"][::390] += 10.0
        bars["low"][::390] -= 10.0
        payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
        decoded = decode_ohlcv(payload)
        ok = len(decoded["close"]) == len(bars["close"])
        results.append({
            "test_id": "DT-FT-1",
            "name": "gap-open/extreme-volatility",
            "status": "PASS" if ok else "FAIL",
            "note": "codec remained stable under gap shocks",
        })
    except Exception as exc:
        uncaught_crashes += 1
        results.append(
            {
                "test_id": "DT-FT-1",
                "name": "gap-open/extreme-volatility",
                "status": "FAIL",
                "note": str(exc),
            }
        )

    # DT-FT-2: malformed streams
    malformed_handled = 0
    malformed_total = 0
    malformed_cases = []
    try:
        bars_bad = generate_ohlcv_bars(num_bars=1000, seed=args.seed + 2, tick_size=0.01)
        ticks_bad = generate_tick_stream(num_ticks=2000, seed=args.seed + 2, tick_size=0.0001)

        case_set = []

        b1 = {k: np.copy(v) for k, v in bars_bad.items()}
        b1["close"][7] = np.nan
        case_set.append(("bar_nan", lambda: encode_ohlcv(b1, tick_size=0.01)))

        b2 = {k: np.copy(v) for k, v in bars_bad.items()}
        b2["timestamp"][10], b2["timestamp"][11] = b2["timestamp"][11], b2["timestamp"][10]
        case_set.append(("bar_out_of_order_ts", lambda: encode_ohlcv(b2, tick_size=0.01)))

        t1 = {k: np.copy(v) for k, v in ticks_bad.items()}
        t1["ask"][5] = t1["bid"][5] - 0.001
        case_set.append(("tick_ask_below_bid", lambda: encode_ticks(t1, tick_size=0.0001)))

        t2 = {k: np.copy(v) for k, v in ticks_bad.items()}
        t2["timestamp"][20], t2["timestamp"][21] = t2["timestamp"][21], t2["timestamp"][20]
        case_set.append(("tick_out_of_order_ts", lambda: encode_ticks(t2, tick_size=0.0001)))

        for name, fn in case_set:
            malformed_total += 1
            try:
                fn()
                malformed_cases.append({"case": name, "status": "FAIL", "note": "expected validation error"})
            except ValueError as exc:
                malformed_handled += 1
                malformed_cases.append({"case": name, "status": "PASS", "note": str(exc)})

        results.append(
            {
                "test_id": "DT-FT-2",
                "name": "malformed streams",
                "status": "PASS" if malformed_handled == malformed_total else "FAIL",
                "handled": malformed_handled,
                "total": malformed_total,
                "cases": malformed_cases,
            }
        )
    except Exception as exc:
        uncaught_crashes += 1
        results.append(
            {
                "test_id": "DT-FT-2",
                "name": "malformed streams",
                "status": "FAIL",
                "note": str(exc),
            }
        )

    # DT-FT-3: pattern confusion set
    try:
        bars = generate_ohlcv_bars(num_bars=100_000, seed=args.seed + 3, tick_size=0.01)
        tokens = bars_to_tokens(bars["close"], tick_size=0.01)
        template = canonical_pattern_library()["head_shoulders"]
        confusion = build_confusion_set(template)
        index = PatternIndex(tokens, k=4)

        # Query with near misses; ideal behaviour should avoid false confidence.
        confusion_high_scores = []
        for q in confusion:
            ranked = index.search(q, top_k=10, min_score=0.0)
            best = ranked[0].score if ranked else 0.0
            confusion_high_scores.append(float(best))

        max_confusion_score = max(confusion_high_scores) if confusion_high_scores else 0.0
        status = "PASS" if max_confusion_score < 0.95 else "FAIL"
        results.append(
            {
                "test_id": "DT-FT-3",
                "name": "pattern confusion set",
                "status": status,
                "max_confusion_score": max_confusion_score,
                "threshold": 0.95,
            }
        )
    except Exception as exc:
        uncaught_crashes += 1
        results.append(
            {
                "test_id": "DT-FT-3",
                "name": "pattern confusion set",
                "status": "FAIL",
                "note": str(exc),
            }
        )

    # DT-FT-5: DB corruption/reorder fault injection
    try:
        db_path = artifact_root / "falsification_faults.sqlite3"
        conn = init_db(db_path)
        bars = generate_ohlcv_bars(num_bars=8000, seed=args.seed + 5, tick_size=0.01)
        payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
        rt = roundtrip_packet(conn, "fault_probe", payload)

        corrupted = fault_inject_corruption(payload)
        corruption_detected = False
        try:
            decode_ohlcv(corrupted)
        except Exception:
            corruption_detected = True

        reordered = chunk_and_reorder(conn, "fault_probe_chunks", payload, chunk_size=41)
        reorder_detected = False
        try:
            decode_ohlcv(reordered)
        except Exception:
            reorder_detected = True

        status = "PASS" if (rt["bit_consistent"] and corruption_detected and reorder_detected) else "FAIL"
        results.append(
            {
                "test_id": "DT-FT-5",
                "name": "db corruption/reorder injection",
                "status": status,
                "roundtrip_bit_consistent": rt["bit_consistent"],
                "corruption_detected": corruption_detected,
                "reorder_detected": reorder_detected,
            }
        )
        conn.close()
    except Exception as exc:
        uncaught_crashes += 1
        results.append(
            {
                "test_id": "DT-FT-5",
                "name": "db corruption/reorder injection",
                "status": "FAIL",
                "note": str(exc),
            }
        )

    overall_pass = uncaught_crashes == 0 and all(r["status"] == "PASS" for r in results)

    md_lines = [
        "# Falsification Results (Gate D)",
        "",
        f"- Uncaught crashes: {uncaught_crashes}",
        f"- Overall: {'PASS' if overall_pass else 'FAIL'}",
        "",
        "| Test ID | Name | Status | Notes |",
        "|---|---|---|---|",
    ]
    for r in results:
        note = r.get("note", "")
        if r["test_id"] == "DT-FT-2":
            note = f"handled={r.get('handled', 0)}/{r.get('total', 0)}"
        if r["test_id"] == "DT-FT-3":
            note = f"max_confusion_score={r.get('max_confusion_score', 0.0):.4f}"
        if r["test_id"] == "DT-FT-5":
            note = (
                f"bit_consistent={r.get('roundtrip_bit_consistent')}, "
                f"corruption_detected={r.get('corruption_detected')}, "
                f"reorder_detected={r.get('reorder_detected')}"
            )
        md_lines.append(f"| {r['test_id']} | {r['name']} | {r['status']} | {note} |")

    falsification_md = "\n".join(md_lines) + "\n"
    (artifact_root / "falsification_results.md").write_text(falsification_md, encoding="utf-8")

    write_json(
        artifact_root / "falsification_results.json",
        {
            "overall_pass": overall_pass,
            "uncaught_crashes": uncaught_crashes,
            "results": results,
        },
    )

    append_command_log(
        artifact_root,
        "GateD",
        "write falsification_results.md",
        note=f"overall_pass={overall_pass},uncaught_crashes={uncaught_crashes}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
