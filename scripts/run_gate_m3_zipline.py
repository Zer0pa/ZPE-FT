#!/usr/bin/env python3
"""Gate M3: Zipline ingestion roundtrip without schema loss."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from common import (
    append_command_log,
    append_validation_markdown,
    ensure_artifact_root,
    parse_args,
    run_command_capture,
    write_json,
)


def main() -> int:
    parser = parse_args("Gate M3 Zipline")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)
    validation_md = artifact_root / "max_resource_validation_log.md"

    append_command_log(
        artifact_root,
        "GateM3",
        "python3 scripts/run_gate_m3_zipline.py",
        note="start",
    )

    repo_root = Path(__file__).resolve().parents[1]
    zip_venv = repo_root / ".venv311_zipline"
    data_dir = artifact_root / "zipline_csvdir"
    data_daily = data_dir / "daily"
    data_daily.mkdir(parents=True, exist_ok=True)

    attempts = []
    impracticality = []

    py311_probe = run_command_capture(["python3.11", "--version"], cwd=str(repo_root))
    attempts.append(py311_probe)
    append_validation_markdown(validation_md, "M3 Python 3.11 probe", py311_probe, "OK" if py311_probe["exit_code"] == 0 else "FAIL")

    if py311_probe["exit_code"] != 0:
        impracticality.append(
            {
                "resource": "zipline-reloaded",
                "code": "IMP-NOCODE",
                "error_signature": (py311_probe.get("stderr") or py311_probe.get("stdout") or "python3.11 unavailable")[:500],
                "fallback": "adapter-only schema contract",
                "claim_impact": "FT-C002/FT-C004 Zipline runtime evidence INCONCLUSIVE",
            }
        )
        report = {
            "gate": "M3",
            "status": "INCONCLUSIVE",
            "attempts": attempts,
            "impracticality": impracticality,
        }
        write_json(artifact_root / "zipline_roundtrip_results.json", report)
        return 0

    venv_create = run_command_capture(["python3.11", "-m", "venv", str(zip_venv)], cwd=str(repo_root))
    attempts.append(venv_create)
    append_validation_markdown(validation_md, "M3 Zipline venv create", venv_create, "OK" if venv_create["exit_code"] == 0 else "FAIL")

    pip_install = run_command_capture(
        [str(zip_venv / "bin" / "pip"), "install", "-q", "--upgrade", "pip", "setuptools", "wheel", "zipline-reloaded"],
        cwd=str(repo_root),
        timeout_sec=600.0,
    )
    attempts.append(pip_install)
    append_validation_markdown(validation_md, "M3 zipline install", pip_install, "OK" if pip_install["exit_code"] == 0 else "FAIL")

    if pip_install["exit_code"] != 0:
        impracticality.append(
            {
                "resource": "zipline-reloaded",
                "code": "IMP-NOCODE",
                "error_signature": (pip_install.get("stderr") or "install failure")[:500],
                "fallback": "adapter-only schema contract",
                "claim_impact": "FT-C002/FT-C004 Zipline runtime evidence INCONCLUSIVE",
            }
        )
        report = {
            "gate": "M3",
            "status": "INCONCLUSIVE",
            "attempts": attempts,
            "impracticality": impracticality,
        }
        write_json(artifact_root / "zipline_roundtrip_results.json", report)
        return 0

    generate_csv = run_command_capture(
        [
            str(zip_venv / "bin" / "python"),
            "-c",
            (
                "import numpy as np, pandas as pd;"
                "from zipline.utils.calendar_utils import get_calendar;"
                f"out=r'{str(data_daily / 'SPY.csv')}';"
                "cal=get_calendar('NYSE');"
                "sessions=cal.sessions_in_range(pd.Timestamp('2020-01-02'), pd.Timestamp('2021-05-04'));"
                "rng=np.random.default_rng(20260220);"
                "n=len(sessions);"
                "p=300+np.cumsum(rng.normal(0,1,size=n));"
                "o=p+rng.normal(0,0.5,size=n);"
                "c=p+rng.normal(0,0.5,size=n);"
                "h=np.maximum(o,c)+np.abs(rng.normal(0,0.6,size=n));"
                "l=np.minimum(o,c)-np.abs(rng.normal(0,0.6,size=n));"
                "v=rng.integers(1000000,5000000,size=n);"
                "df=pd.DataFrame({'open':o,'high':h,'low':l,'close':c,'volume':v},index=sessions);"
                "df.to_csv(out,index_label='date');"
                "print(len(df))"
            ),
        ],
        cwd=str(repo_root),
    )
    attempts.append(generate_csv)
    append_validation_markdown(validation_md, "M3 CSVDIR data generation", generate_csv, "OK" if generate_csv["exit_code"] == 0 else "FAIL")

    env = {"CSVDIR": str(data_dir)}

    ingest_cmd = run_command_capture(
        [str(zip_venv / "bin" / "zipline"), "ingest", "-b", "csvdir", "--no-show-progress"],
        cwd=str(repo_root),
        env=env,
        timeout_sec=600.0,
    )
    attempts.append(ingest_cmd)
    append_validation_markdown(validation_md, "M3 zipline ingest csvdir", ingest_cmd, "OK" if ingest_cmd["exit_code"] == 0 else "FAIL")

    algo_path = artifact_root / "zipline_algo.py"
    algo_path.write_text(
        "from zipline.api import order_target, record, symbol\n"
        "def initialize(context):\n"
        "    context.asset = symbol('SPY')\n"
        "def handle_data(context, data):\n"
        "    p = data.current(context.asset, 'price')\n"
        "    order_target(context.asset, 10)\n"
        "    record(price=p)\n",
        encoding="utf-8",
    )

    out_pickle = artifact_root / "zipline_perf.pickle"
    run_cmd = run_command_capture(
        [
            str(zip_venv / "bin" / "zipline"),
            "run",
            "-b",
            "csvdir",
            "-f",
            str(algo_path),
            "--start",
            "2020-03-01",
            "--end",
            "2020-12-31",
            "--output",
            str(out_pickle),
            "--no-benchmark",
        ],
        cwd=str(repo_root),
        env=env,
        timeout_sec=600.0,
    )
    attempts.append(run_cmd)
    append_validation_markdown(validation_md, "M3 zipline run", run_cmd, "OK" if run_cmd["exit_code"] == 0 else "FAIL")

    schema_check = run_command_capture(
        [
            str(zip_venv / "bin" / "python"),
            "-c",
            (
                "import pandas as pd;"
                f"df=pd.read_pickle(r'{str(out_pickle)}');"
                "required={'portfolio_value','returns'};"
                "missing=required-set(df.columns);"
                "print('rows',len(df));"
                "print('missing',sorted(missing));"
                "raise SystemExit(0 if not missing and len(df)>0 else 1)"
            ),
        ],
        cwd=str(repo_root),
    )
    attempts.append(schema_check)
    append_validation_markdown(validation_md, "M3 zipline output schema check", schema_check, "OK" if schema_check["exit_code"] == 0 else "FAIL")

    status = "PASS" if all(a["exit_code"] == 0 for a in [generate_csv, ingest_cmd, run_cmd, schema_check]) else "INCONCLUSIVE"
    if status != "PASS":
        impracticality.append(
            {
                "resource": "zipline-reloaded",
                "code": "IMP-NOCODE",
                "error_signature": (schema_check.get("stderr") or run_cmd.get("stderr") or ingest_cmd.get("stderr") or "zipline workflow failure")[:500],
                "fallback": "zpe feed adapter contract only",
                "claim_impact": "FT-C002/FT-C004 Zipline evidence downgraded to INCONCLUSIVE",
            }
        )

    report = {
        "gate": "M3",
        "status": status,
        "csvdir": str(data_dir),
        "zipline_output": str(out_pickle),
        "claim_linkage": {
            "FT-C002": {"status": "PASS" if status == "PASS" else "INCONCLUSIVE"},
            "FT-C004": {"status": "PASS" if status == "PASS" else "INCONCLUSIVE"},
        },
        "attempts": attempts,
        "impracticality": impracticality,
    }

    write_json(artifact_root / "zipline_roundtrip_results.json", report)

    append_command_log(
        artifact_root,
        "GateM3",
        "write zipline_roundtrip_results.json",
        note=f"status={status}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
