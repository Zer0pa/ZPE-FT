import json
import os
import subprocess
import sys
from pathlib import Path

from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream


def _write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(str(value) for value in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_real_market_refresh_writes_codec_latency_report(tmp_path: Path):
    bars = generate_ohlcv_bars(num_bars=128, seed=20260406, tick_size=0.01)
    ticks = generate_tick_stream(num_ticks=256, seed=20260406, tick_size=0.0001)

    bars_csv = tmp_path / "spy_1m.csv"
    tick_csv = tmp_path / "eurusd_tob.csv"

    _write_csv(
        bars_csv,
        ["ts", "open_px", "high_px", "low_px", "close_px", "volume"],
        [
            [
                int(bars["timestamp"][idx]),
                float(bars["open"][idx]),
                float(bars["high"][idx]),
                float(bars["low"][idx]),
                float(bars["close"][idx]),
                float(bars["volume"][idx]),
            ]
            for idx in range(len(bars["timestamp"]))
        ],
    )
    _write_csv(
        tick_csv,
        ["ts", "bid_px", "ask_px", "bid_sz", "ask_sz"],
        [
            [
                int(ticks["timestamp"][idx]),
                float(ticks["bid"][idx]),
                float(ticks["ask"][idx]),
                float(ticks["bid_size"][idx]),
                float(ticks["ask_size"][idx]),
            ]
            for idx in range(len(ticks["timestamp"]))
        ],
    )

    config = {
        "corpus_id": "fixture-commercial-refresh-extras",
        "buyer_workload": "query-by-example over historical price action",
        "baseline_matrix": {
            "ohlcv": ["raw_scan", "duckdb_sqlite"],
            "tick": ["raw_scan", "top_of_book_scan"],
        },
        "rights_policy": {"classification": "test-only"},
        "truth_catalog": {"ft_c004": {"mode": "labeled_or_auditable"}},
        "series": [
            {
                "series_id": "spy_1m",
                "kind": "ohlcv",
                "source_path": str(bars_csv),
                "symbol": "SPY",
                "tick_size": 0.01,
                "provenance": "fixture synthetic export",
                "license_note": "test-only",
                "timezone": "UTC",
                "timestamp_format": "epoch_ms",
                "columns": {
                    "timestamp": "ts",
                    "open": "open_px",
                    "high": "high_px",
                    "low": "low_px",
                    "close": "close_px",
                    "volume": "volume",
                },
            },
            {
                "series_id": "eurusd_tob",
                "kind": "tick",
                "source_path": str(tick_csv),
                "symbol": "EURUSD",
                "tick_size": 0.0001,
                "provenance": "fixture synthetic export",
                "license_note": "test-only",
                "timezone": "UTC",
                "timestamp_format": "epoch_ms",
                "columns": {
                    "timestamp": "ts",
                    "bid": "bid_px",
                    "ask": "ask_px",
                    "bid_size": "bid_sz",
                    "ask_size": "ask_sz",
                },
            },
        ],
    }
    config_path = tmp_path / "corpus_spec.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    artifact_root = tmp_path / "artifacts"
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root / "python")

    freeze_cmd = [
        sys.executable,
        str(repo_root / "scripts" / "freeze_real_market_corpus.py"),
        "--artifact-root",
        str(artifact_root),
        "--config",
        str(config_path),
    ]
    refresh_cmd = [
        sys.executable,
        str(repo_root / "scripts" / "run_real_market_refresh.py"),
        "--artifact-root",
        str(artifact_root),
        "--manifest",
        str(artifact_root / "real_market_corpus_manifest.json"),
        "--latency-repetitions",
        "2",
        "--codec-repetitions",
        "2",
    ]

    subprocess.run(freeze_cmd, check=True, env=env, cwd=repo_root)
    subprocess.run(refresh_cmd, check=True, env=env, cwd=repo_root)

    codec_latency = json.loads((artifact_root / "ft_encode_decode_latency.json").read_text(encoding="utf-8"))
    assert codec_latency["claim_id"] == "FT-C003"
    assert codec_latency["aggregate"]["encode_ms"]["p95"] >= 0.0
    assert codec_latency["aggregate"]["decode_ms"]["p95"] >= 0.0


def test_check_truth_surface_reports_blocked_catalog(tmp_path: Path):
    catalog = {
        "catalog_id": "pending-ftc004",
        "status": "PENDING_LABEL_AUDIT",
        "truth_rule": "FT-C004 remains NEEDS_LABELS until relevant_positions or audit refs are attached.",
        "query_slots": [
            {
                "slot_id": "slot-001",
                "family": "breakout_continuation",
                "series_kind": "ohlcv",
                "truth_status": "PENDING_LABEL_AUDIT",
            }
        ],
    }
    catalog_path = tmp_path / "pending_catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    output_path = tmp_path / "truth_report.json"
    repo_root = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "check_truth_surface.py"),
        "--query-catalog",
        str(catalog_path),
        "--output",
        str(output_path),
    ]
    proc = subprocess.run(cmd, check=False, cwd=repo_root)

    assert proc.returncode == 2
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["claim_id"] == "FT-C004"
    assert report["status"] == "blocked_missing_authority_truth"
    assert report["blocked_count"] == 1
    assert report["ready_count"] == 0


def test_check_truth_surface_reports_ready_catalog(tmp_path: Path):
    catalog = {
        "catalog_id": "ready-ftc004",
        "status": "READY",
        "queries": [
            {
                "query_id": "query-001",
                "truth_status": "AUDITABLE",
                "audit_refs": ["analyst-note-001"],
            }
        ],
    }
    catalog_path = tmp_path / "ready_catalog.json"
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")

    output_path = tmp_path / "truth_report.json"
    repo_root = Path(__file__).resolve().parents[1]
    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "check_truth_surface.py"),
        "--query-catalog",
        str(catalog_path),
        "--output",
        str(output_path),
    ]
    proc = subprocess.run(cmd, check=False, cwd=repo_root)

    assert proc.returncode == 0
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["status"] == "ready"
    assert report["blocked_count"] == 0
    assert report["ready_count"] == 1
