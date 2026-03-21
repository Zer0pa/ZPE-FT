import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream


def _write_csv(path: Path, header: list[str], rows: list[list[object]]) -> None:
    lines = [",".join(header)]
    for row in rows:
        lines.append(",".join(str(value) for value in row))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_real_market_freeze_and_refresh_scripts(tmp_path: Path):
    bars = generate_ohlcv_bars(num_bars=256, seed=20260220, tick_size=0.01)
    ticks = generate_tick_stream(num_ticks=512, seed=20260220, tick_size=0.0001)

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
        "corpus_id": "fixture-commercial-refresh",
        "buyer_workload": "query-by-example over historical price action",
        "baseline_matrix": {
            "ohlcv": ["raw_scan", "duckdb_sqlite"],
            "tick": ["raw_scan", "top_of_book_scan"],
        },
        "rights_policy": {
            "classification": "test-only",
            "phase06_rule": "no hidden private dependency",
        },
        "truth_catalog": {
            "ft_c004": {
                "mode": "labeled_or_auditable",
                "unresolved_rule": "remain NEEDS_LABELS",
            }
        },
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
    ]

    subprocess.run(freeze_cmd, check=True, env=env, cwd=repo_root)
    subprocess.run(refresh_cmd, check=True, env=env, cwd=repo_root)

    manifest = json.loads((artifact_root / "real_market_corpus_manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["series"]) == 2
    assert manifest["contract"]["baseline_matrix"]["ohlcv"] == ["raw_scan", "duckdb_sqlite"]
    assert manifest["contract"]["truth_catalog"]["ft_c004"]["mode"] == "labeled_or_auditable"

    ohlcv_benchmark = json.loads((artifact_root / "ft_ohlcv_benchmark.json").read_text(encoding="utf-8"))
    tick_benchmark = json.loads((artifact_root / "ft_tick_benchmark.json").read_text(encoding="utf-8"))
    fidelity = json.loads((artifact_root / "ft_reconstruction_fidelity.json").read_text(encoding="utf-8"))
    pattern = json.loads((artifact_root / "ft_pattern_search_eval.json").read_text(encoding="utf-8"))
    latency = json.loads((artifact_root / "ft_query_latency_benchmark.json").read_text(encoding="utf-8"))
    roundtrip = json.loads((artifact_root / "ft_db_roundtrip_results.json").read_text(encoding="utf-8"))

    assert ohlcv_benchmark["pass"] is True
    assert tick_benchmark["pass"] is True
    assert fidelity["pass"] is True
    assert pattern["status"] == "NEEDS_LABELS"
    assert latency["pass"] is True
    assert roundtrip["pass"] is True


def test_freeze_writes_missing_input_packet_when_phase06_inputs_are_absent(tmp_path: Path):
    config = {
        "corpus_id": "phase06-missing-inputs",
        "buyer_workload": "query-by-example over historical price action",
        "baseline_matrix": {"ohlcv": ["raw_scan"]},
        "rights_policy": {"classification": "commercially_safe_pending"},
        "truth_catalog": {"ft_c004": {"mode": "auditable_required"}},
        "query_catalog_path": str(tmp_path / "missing_query_catalog.json"),
        "series": [
            {
                "series_id": "spy_1m",
                "kind": "ohlcv",
                "source_path": str(tmp_path / "missing_spy.csv"),
                "symbol": "SPY",
                "tick_size": 0.01,
                "provenance": "missing benchmark export",
                "license_note": "phase06 pending",
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
            }
        ],
    }
    config_path = tmp_path / "phase06_missing.json"
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

    proc = subprocess.run(freeze_cmd, check=False, env=env, cwd=repo_root)
    assert proc.returncode == 2

    packet = json.loads((artifact_root / "missing_inputs_packet.json").read_text(encoding="utf-8"))
    probe = json.loads((artifact_root / "resource_probe_results.json").read_text(encoding="utf-8"))

    assert packet["status"] == "blocked_missing_inputs"
    assert packet["contract"]["baseline_matrix"]["ohlcv"] == ["raw_scan"]
    assert packet["missing_inputs"]["series"] == [
        {
            "series_id": "spy_1m",
            "path": str(tmp_path / "missing_spy.csv"),
        }
    ]
    assert packet["missing_inputs"]["query_catalog"] == {"path": str(tmp_path / "missing_query_catalog.json")}
    assert probe["missing_inputs"]["series"] == ["spy_1m"]
    assert probe["missing_inputs"]["query_catalog"] == str(tmp_path / "missing_query_catalog.json")
