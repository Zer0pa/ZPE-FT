import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


def _write_yahoo_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "timestamp,open,high,low,close,volume",
                "2024-01-02T00:00:00+00:00,470.0,472.0,469.5,471.5,1000000",
                "2024-01-03T00:00:00+00:00,471.5,473.0,470.5,472.2,1100000",
                "2024-01-04T00:00:00+00:00,472.2,474.5,471.8,474.0,1200000",
                "2024-01-05T00:00:00+00:00,474.0,475.0,472.9,473.4,950000",
                "2024-01-08T00:00:00+00:00,473.4,476.0,473.0,475.8,980000",
                "2024-01-09T00:00:00+00:00,475.8,477.1,475.0,476.3,1020000",
                "2024-01-10T00:00:00+00:00,476.3,478.0,476.0,477.9,1080000",
                "2024-01-11T00:00:00+00:00,477.9,479.2,477.0,478.8,990000",
                "2024-01-12T00:00:00+00:00,478.8,480.0,478.2,479.1,1010000",
                "2024-01-16T00:00:00+00:00,479.1,481.3,478.8,480.7,1150000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_binance_zip(path: Path) -> None:
    rows = [
        "1,43000.10,0.5000,1,1,1711929600000,0,1",
        "2,43000.20,0.2500,2,2,1711929600000,1,1",
        "3,43000.25,0.3000,3,3,1711929602000,0,1",
        "4,43000.20,0.2000,4,4,1711929602000,1,1",
        "5,43000.35,0.4500,5,5,1711929604000,0,1",
        "6,43000.50,0.1000,6,6,1711929604000,0,1",
        "7,43000.55,0.1200,7,7,1711929606000,1,1",
        "8,43000.48,0.2200,8,8,1711929606000,1,1",
        "9,43000.62,0.1800,9,9,1711929608000,0,1",
        "10,43000.70,0.3300,10,10,1711929609000,0,1",
        "11,43000.68,0.2100,11,11,1711929609000,1,1",
        "12,43000.80,0.2700,12,12,1711929611000,0,1",
    ]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("BTCUSDT-aggTrades-fixture.csv", "\n".join(rows) + "\n")


def _write_kaggle_csv(path: Path) -> None:
    path.write_text(
        "\n".join(
            [
                "Date,Open,High,Low,Close,Volume,OpenInt",
                "2015-01-02,204.12,206.88,203.62,205.43,121465900,0",
                "2015-01-05,204.17,204.37,201.35,201.72,169632600,0",
                "2015-01-06,202.09,202.72,198.86,199.82,209151400,0",
                "2015-01-07,201.42,202.72,200.88,202.31,125346700,0",
                "2015-01-08,204.01,206.16,203.99,205.90,147217800,0",
                "2015-01-09,206.34,206.66,204.20,204.25,159729000,0",
                "2015-01-12,203.05,204.47,201.92,202.65,135582100,0",
                "2015-01-13,204.12,204.25,200.91,202.08,166146100,0",
                "2015-01-14,199.62,201.27,198.16,200.27,217613000,0",
                "2015-01-15,201.63,202.52,199.26,199.96,197072700,0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def test_public_market_benchmark_script_runs_with_local_fixtures(tmp_path: Path):
    yahoo_csv = tmp_path / "spy_fixture.csv"
    binance_zip = tmp_path / "btc_fixture.zip"
    kaggle_csv = tmp_path / "spy_kaggle_fixture.csv"
    artifact_root = tmp_path / "artifacts"

    _write_yahoo_csv(yahoo_csv)
    _write_binance_zip(binance_zip)
    _write_kaggle_csv(kaggle_csv)

    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root / "python")

    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "run_public_market_benchmarks.py"),
        "--artifact-root",
        str(artifact_root),
        "--temp-dir",
        str(tmp_path / "work"),
        "--yahoo-local-csv",
        str(yahoo_csv),
        "--binance-local-zip",
        str(binance_zip),
        "--binance-period",
        "fixture-2019-01",
        "--kaggle-local-csv",
        str(kaggle_csv),
        "--query-repetitions",
        "1",
    ]
    proc = subprocess.run(cmd, check=True, cwd=repo_root, env=env, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    report = json.loads((artifact_root / "phase3_public_benchmarks.json").read_text(encoding="utf-8"))
    assert len(report["benchmarks"]) == 3

    yahoo_entry = next(item for item in report["benchmarks"] if item["dataset_id"].startswith("yahoo_"))
    assert yahoo_entry["status"] == "ok"
    assert yahoo_entry["zpe"]["compression_ratio"] > 1.0
    assert yahoo_entry["baseline"]["compressed_bytes"] > 0

    binance_entry = next(item for item in report["benchmarks"] if item["dataset_id"].startswith("binance_"))
    assert binance_entry["status"] == "ok"
    assert binance_entry["roundtrip"]["timing_exact"] is True
    assert binance_entry["zpe"]["compression_ratio"] > 1.0

    kaggle_entry = next(item for item in report["benchmarks"] if item["dataset_id"].startswith("kaggle_"))
    assert kaggle_entry["status"] == "ok"
    assert kaggle_entry["zpe"]["compression_ratio"] > 1.0

    markdown = (artifact_root / "phase3_public_benchmarks.md").read_text(encoding="utf-8")
    assert "| dataset | baseline | ZPE | ratio | improvement |" in markdown
    assert "binance_btcusdt_aggtrades_fixture_2019_01" in markdown
    assert "kaggle_spy_daily" in markdown
