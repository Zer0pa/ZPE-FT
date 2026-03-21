#!/usr/bin/env python3
"""Task 0 environment gate for the FT public proof track."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_MODULES = (
    "yfinance",
    "pandas_datareader",
    "requests",
    "pandas",
    "numpy",
    "scipy",
    "sklearn",
)


@dataclass
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_command(command: list[str], cwd: Path | None = None) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    return CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def detect_cpu() -> str:
    if platform.system() != "Darwin":
        return platform.processor() or "unknown"
    result = run_command(["sysctl", "-n", "machdep.cpu.brand_string"])
    if result.returncode == 0 and result.stdout:
        return result.stdout
    return platform.processor() or "unknown"


def check_disk(workspace: Path, threshold_gib: float) -> dict[str, Any]:
    _, _, free = shutil.disk_usage(workspace)
    gib = 1024 ** 3
    free_gib = free / gib
    return {
        "workspace": str(workspace.resolve()),
        "free_bytes": free,
        "free_gib": round(free_gib, 2),
        "threshold_gib": threshold_gib,
        "status": "PASS" if free_gib >= threshold_gib else "FAIL",
    }


def check_imports() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for module_name in REQUIRED_MODULES:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", "unknown")
            results.append(
                {
                    "module": module_name,
                    "status": "PASS",
                    "detail": f"import ok (version {version})",
                }
            )
        except Exception as exc:  # pragma: no cover - runtime state
            results.append(
                {
                    "module": module_name,
                    "status": "FAIL",
                    "detail": f"{type(exc).__name__}: {exc}",
                }
            )
    return results


def check_pytest(repo: Path) -> dict[str, Any]:
    pytest_path = shutil.which("pytest")
    if pytest_path is None:
        return {
            "status": "FAIL",
            "command": ["pytest", "-q"],
            "detail": "pytest not found on PATH",
            "stdout_tail": [],
            "stderr_tail": [],
        }

    result = run_command([pytest_path, "-q"], cwd=repo)
    return {
        "status": "PASS" if result.returncode == 0 else "FAIL",
        "command": result.command,
        "detail": f"exit code {result.returncode}",
        "stdout_tail": result.stdout.splitlines()[-20:],
        "stderr_tail": result.stderr.splitlines()[-20:],
    }


def check_adb() -> dict[str, Any]:
    adb_path = shutil.which("adb")
    if adb_path is None:
        return {
            "status": "UNAVAILABLE",
            "blocking": False,
            "detail": "adb not found on PATH",
            "devices": [],
        }

    result = run_command([adb_path, "devices"])
    device_lines = [
        line.strip()
        for line in result.stdout.splitlines()[1:]
        if line.strip()
    ]
    devices = [line.split()[0] for line in device_lines]
    return {
        "status": "CONNECTED" if devices else "UNAVAILABLE",
        "blocking": False,
        "detail": f"exit code {result.returncode}",
        "devices": devices,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def gate_verdict(
    disk: dict[str, Any], imports: list[dict[str, Any]], tests: dict[str, Any]
) -> dict[str, Any]:
    blockers: list[str] = []
    if disk["status"] != "PASS":
        blockers.append(
            f"free disk {disk['free_gib']} GiB is below the {disk['threshold_gib']} GiB gate"
        )

    missing_modules = [item["module"] for item in imports if item["status"] != "PASS"]
    if missing_modules:
        blockers.append("required imports missing: " + ", ".join(missing_modules))

    if tests["status"] != "PASS":
        blockers.append("repo tests did not pass")

    return {
        "status": "PASS" if not blockers else "FAIL",
        "blocking_conditions": blockers,
        "next_action": (
            "public proof may continue to free/public data and package checks"
            if not blockers
            else "stop at Task 0 until the listed blockers are cleared"
        ),
    }


def build_report(workspace: Path, repo: Path, threshold_gib: float) -> dict[str, Any]:
    disk = check_disk(workspace, threshold_gib)
    imports = check_imports()
    tests = check_pytest(repo)
    adb = check_adb()
    verdict = gate_verdict(disk, imports, tests)

    return {
        "timestamp_utc": now_utc(),
        "policy": {
            "disk_threshold_gib": threshold_gib,
            "runpod_requires_explicit_approval": True,
            "secondary_device": "Red Magic 10 Pro+ via adb when attached",
            "sovereign_boundary": "Phase 06 buyer authority remains the top gate",
        },
        "workspace": str(workspace.resolve()),
        "repo": str(repo.resolve()),
        "machine": {
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
            "cpu": detect_cpu(),
        },
        "disk": disk,
        "imports": imports,
        "repo_tests": tests,
        "adb": adb,
        "verdict": verdict,
    }


def write_outputs(report: dict[str, Any], log_dir: Path) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    json_path = log_dir / "env_check.json"
    log_path = log_dir / "env_check.log"

    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# FT Public Track Task 0 Environment Check",
        "",
        f"Timestamp: {report['timestamp_utc']}",
        f"Workspace: {report['workspace']}",
        f"Repo: {report['repo']}",
        "",
        "## Machine",
        f"- Platform: {report['machine']['platform']}",
        f"- CPU: {report['machine']['cpu']}",
        "",
        "## Policy",
        f"- Disk gate: {report['policy']['disk_threshold_gib']} GiB free",
        "- RunPod: explicit approval required",
        f"- Sovereign boundary: {report['policy']['sovereign_boundary']}",
        "",
        "## Disk",
        f"- Status: {report['disk']['status']}",
        f"- Free GiB: {report['disk']['free_gib']}",
        "",
        "## Imports",
    ]

    for item in report["imports"]:
        lines.append(f"- {item['module']}: {item['status']} ({item['detail']})")

    lines.extend(
        [
            "",
            "## Repo Tests",
            f"- Status: {report['repo_tests']['status']}",
            f"- Detail: {report['repo_tests']['detail']}",
            "",
            "## ADB",
            f"- Status: {report['adb']['status']}",
            f"- Devices: {', '.join(report['adb'].get('devices', [])) or 'none'}",
            "",
            "## Verdict",
            f"- Gate: {report['verdict']['status']}",
        ]
    )

    if report["verdict"]["blocking_conditions"]:
        lines.append("- Blocking conditions:")
        for blocker in report["verdict"]["blocking_conditions"]:
            lines.append(f"  - {blocker}")
    else:
        lines.append("- Blocking conditions: none")

    lines.append(f"- Next action: {report['verdict']['next_action']}")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".", help="outer workspace path")
    parser.add_argument("--repo", default="zpe-finance", help="inner repo path")
    parser.add_argument("--log-dir", default=None, help="output directory (defaults to <repo>/poc/logs)")
    parser.add_argument(
        "--disk-threshold-gib",
        type=float,
        default=15.0,
        help="minimum free disk required to continue the public track",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace = Path(args.workspace)
    repo = Path(args.repo)
    log_dir = Path(args.log_dir) if args.log_dir else repo / "poc" / "logs"

    report = build_report(workspace=workspace, repo=repo, threshold_gib=args.disk_threshold_gib)
    write_outputs(report, log_dir)
    print(json.dumps(report["verdict"], indent=2))
    return 0 if report["verdict"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
