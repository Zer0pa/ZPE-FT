#!/usr/bin/env python3
"""End-to-end Wave-1 pipeline executor in strict PRD gate order."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from common import append_command_log, ensure_artifact_root


def run_cmd(
    cmd: list[str],
    gate: str,
    artifact_root: Path,
    env: dict[str, str],
    capture_to: Path | None = None,
) -> None:
    start = time.monotonic()
    collected: list[str] = []
    proc = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert proc.stdout is not None
    for line in proc.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        if capture_to is not None:
            collected.append(line)

    proc.wait()
    duration_sec = time.monotonic() - start

    if capture_to is not None:
        capture_to.write_text("".join(collected), encoding="utf-8")

    append_command_log(
        artifact_root,
        gate,
        " ".join(cmd),
        exit_code=proc.returncode,
        note=(
            f"ok duration_sec={duration_sec:.1f}"
            if proc.returncode == 0
            else f"failed duration_sec={duration_sec:.1f}"
        ),
    )

    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ZPE FT Wave-1 gates A->E")
    parser.add_argument("--artifact-root", default="artifacts/2026-02-20_zpe_ft_wave1")
    parser.add_argument("--seed", type=int, default=20260220)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    artifact_root = ensure_artifact_root(args.artifact_root)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    existing_pythonpath = env.get("PYTHONPATH", "")
    new_paths = [str(root / "python"), str(root / "scripts")]
    env["PYTHONPATH"] = os.pathsep.join(new_paths + ([existing_pythonpath] if existing_pythonpath else []))

    # Gate A
    run_cmd(
        ["python3", "scripts/gate_a_freeze.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateA",
        artifact_root,
        env,
    )
    run_cmd(
        [
            "python3",
            "scripts/run_appendix_e_ingestion.py",
            "--artifact-root",
            str(artifact_root),
            "--seed",
            str(args.seed),
            "--phase",
            "lock_only",
        ],
        "GateA",
        artifact_root,
        env,
    )

    # Gate B
    run_cmd(
        ["maturin", "develop", "--manifest-path", "core/Cargo.toml"],
        "GateB",
        artifact_root,
        env,
    )
    run_cmd(
        ["pytest", "-q", "tests/test_codec_core.py", "tests/test_packet_roundtrip.py"],
        "GateB",
        artifact_root,
        env,
        capture_to=artifact_root / "gate_b_test_results.txt",
    )
    run_cmd(
        ["python3", "scripts/run_gate_b_fidelity.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateB",
        artifact_root,
        env,
    )

    # Gate C
    run_cmd(
        ["python3", "scripts/run_gate_c_benchmarks.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateC",
        artifact_root,
        env,
    )
    run_cmd(
        ["python3", "scripts/run_pattern_eval.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateC",
        artifact_root,
        env,
    )
    run_cmd(
        ["python3", "scripts/run_latency_benchmark.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateC",
        artifact_root,
        env,
    )

    # Gate D
    run_cmd(
        ["python3", "scripts/run_gate_d_falsification.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateD",
        artifact_root,
        env,
    )
    run_cmd(
        [
            "python3",
            "scripts/run_determinism_replay.py",
            "--artifact-root",
            str(artifact_root),
            "--seed",
            str(args.seed),
            "--runs",
            "5",
        ],
        "GateD",
        artifact_root,
        env,
    )
    run_cmd(
        ["pytest", "-q", "tests/test_adversarial.py"],
        "GateD",
        artifact_root,
        env,
    )

    # Gate E
    run_cmd(
        ["python3", "scripts/run_gate_e_db_roundtrip.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateE",
        artifact_root,
        env,
    )
    run_cmd(
        ["pytest", "-q", "tests"],
        "GateE",
        artifact_root,
        env,
        capture_to=artifact_root / "regression_results.txt",
    )

    # Maximalization gates (Appendix D/E)
    run_cmd(
        ["python3", "scripts/run_gate_m1_gorilla.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM1",
        artifact_root,
        env,
    )
    run_cmd(
        ["python3", "scripts/run_gate_m2_tsbs_db.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM2",
        artifact_root,
        env,
    )
    run_cmd(
        ["python3", "scripts/run_gate_m3_zipline.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM3",
        artifact_root,
        env,
    )
    run_cmd(
        ["python3", "scripts/run_gate_m4_compliance.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM4",
        artifact_root,
        env,
    )
    run_cmd(
        [
            "python3",
            "scripts/run_appendix_e_ingestion.py",
            "--artifact-root",
            str(artifact_root),
            "--seed",
            str(args.seed),
            "--phase",
            "full",
        ],
        "GateE-INGEST",
        artifact_root,
        env,
    )

    run_cmd(
        ["python3", "scripts/build_handoff_artifacts.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateE",
        artifact_root,
        env,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
