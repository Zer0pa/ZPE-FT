import json
import os
import subprocess
import sys
from pathlib import Path


def _run_example(script_name: str, *args: str) -> dict:
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root / "python")
    cmd = [sys.executable, str(repo_root / "examples" / script_name), *args]
    proc = subprocess.run(
        cmd,
        check=True,
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def test_ohlcv_example_runs_on_repo_bundled_data():
    summary = _run_example(
        "ohlcv_compress.py",
        "--input",
        "data/ohlcv/spy_1d_24m.csv.gz",
        "--symbol",
        "SPY",
        "--tick-size",
        "0.01",
        "--rows",
        "128",
    )
    assert summary["rows"] == 128
    assert summary["compression_ratio"] > 1.0
    assert summary["rmse_ticks"] <= 0.5
    assert summary["exact_hits"]


def test_tick_example_runs_on_repo_bundled_data():
    summary = _run_example(
        "tick_replay.py",
        "--input",
        "data/ticks/eurusd_dukascopy_tick_20d_1h.csv.gz",
        "--symbol",
        "EURUSD",
        "--tick-size",
        "0.00001",
        "--rows",
        "256",
    )
    assert summary["rows"] == 256
    assert summary["compression_ratio"] > 1.0
    assert summary["timing_exact"] is True
    assert len(summary["replay_deltas_ms"]) > 0
