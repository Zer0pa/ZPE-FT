#!/usr/bin/env python3
"""Repo-local Wave-1 verification harness in strict PRD gate order."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from common import append_command_log, ensure_artifact_root


def run_cmd(
    cmd: list[str],
    gate: str,
    artifact_root: Path,
    repo_root: Path,
    env: dict[str, str],
    capture_to: Path | None = None,
    cwd: Path | None = None,
) -> None:
    start = time.monotonic()
    collected: list[str] = []
    workdir = cwd or repo_root
    try:
        cwd_label = str(workdir.relative_to(repo_root))
    except ValueError:
        cwd_label = str(workdir)
    log_command = " ".join(cmd) if workdir == repo_root else f"(cd {cwd_label} && {' '.join(cmd)})"
    proc = subprocess.Popen(
        cmd,
        cwd=str(workdir),
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
        log_command,
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
    parser = argparse.ArgumentParser(description="Run repo-local ZPE FT Wave-1 verification gates")
    parser.add_argument("--artifact-root", default="artifacts/2026-02-20_zpe_ft_wave1")
    parser.add_argument("--seed", type=int, default=20260220)
    parser.add_argument(
        "--native-helper",
        choices=("auto", "require", "skip"),
        default="auto",
        help="Build the optional Rust helper with maturin before Gate B",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    artifact_path = Path(args.artifact_root)
    artifact_root = ensure_artifact_root(artifact_path if artifact_path.is_absolute() else root / artifact_path)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    # Gate A
    run_cmd(
        [sys.executable, "scripts/gate_a_freeze.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateA",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [
            sys.executable,
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
        root,
        env,
    )

    # Gate B
    maturin_bin = shutil.which("maturin")
    if args.native_helper != "skip":
        if maturin_bin is not None:
            run_cmd(
                [maturin_bin, "develop", "--release"],
                "GateB",
                artifact_root,
                root,
                env,
                cwd=root / "core",
            )
        elif args.native_helper == "require":
            append_command_log(
                artifact_root,
                "GateB",
                "(cd core && maturin develop --release)",
                exit_code=127,
                note="maturin missing; install optional native helper tooling first",
            )
            raise SystemExit(
                "maturin not found; install optional native helper tooling first "
                "(python -m pip install -e '.[native]')."
            )
        else:
            append_command_log(
                artifact_root,
                "GateB",
                "(cd core && maturin develop --release)",
                exit_code=0,
                note="skipped native helper build: maturin not found",
            )
    run_cmd(
        [sys.executable, "-m", "pytest", "-q", "tests/test_codec_core.py", "tests/test_packet_roundtrip.py"],
        "GateB",
        artifact_root,
        root,
        env,
        capture_to=artifact_root / "gate_b_test_results.txt",
    )
    run_cmd(
        [sys.executable, "scripts/run_gate_b_fidelity.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateB",
        artifact_root,
        root,
        env,
    )

    # Gate C
    run_cmd(
        [sys.executable, "scripts/run_gate_c_benchmarks.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateC",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [sys.executable, "scripts/run_pattern_eval.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateC",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [sys.executable, "scripts/run_latency_benchmark.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateC",
        artifact_root,
        root,
        env,
    )

    # Gate D
    run_cmd(
        [sys.executable, "scripts/run_gate_d_falsification.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateD",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [
            sys.executable,
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
        root,
        env,
    )
    run_cmd(
        [sys.executable, "-m", "pytest", "-q", "tests/test_adversarial.py"],
        "GateD",
        artifact_root,
        root,
        env,
    )

    # Gate E
    run_cmd(
        [sys.executable, "scripts/run_gate_e_db_roundtrip.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateE",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [sys.executable, "-m", "pytest", "-q", "tests"],
        "GateE",
        artifact_root,
        root,
        env,
        capture_to=artifact_root / "regression_results.txt",
    )

    # Maximalization gates (Appendix D/E)
    run_cmd(
        [sys.executable, "scripts/run_gate_m1_gorilla.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM1",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [sys.executable, "scripts/run_gate_m2_tsbs_db.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM2",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [sys.executable, "scripts/run_gate_m3_zipline.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM3",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [sys.executable, "scripts/run_gate_m4_compliance.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateM4",
        artifact_root,
        root,
        env,
    )
    run_cmd(
        [
            sys.executable,
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
        root,
        env,
    )

    run_cmd(
        [sys.executable, "scripts/build_handoff_artifacts.py", "--artifact-root", str(artifact_root), "--seed", str(args.seed)],
        "GateE",
        artifact_root,
        root,
        env,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
