"""Shared utilities for gate scripts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

import numpy as np


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def parse_args(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--artifact-root",
        default="artifacts/2026-02-20_zpe_ft_wave1",
        help="Artifact output root",
    )
    parser.add_argument("--seed", type=int, default=20260220)
    return parser


def ensure_artifact_root(root: str | Path) -> Path:
    path = Path(root)
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_command_log(
    artifact_root: Path,
    gate: str,
    command: str,
    exit_code: int = 0,
    note: str = "",
) -> None:
    log_path = artifact_root / "command_log.txt"
    line = f"{utc_now_iso()}\t{gate}\t{exit_code}\t{command}"
    if note:
        line += f"\t{note}"
    line += "\n"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line)


def run_command_capture(
    cmd: Sequence[str],
    cwd: str | None = None,
    env: Mapping[str, str] | None = None,
    timeout_sec: float | None = None,
) -> Dict[str, Any]:
    env_dict = dict(os.environ)
    if env:
        env_dict.update(env)

    try:
        proc = subprocess.run(
            list(cmd),
            cwd=cwd,
            env=env_dict,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        return {
            "command": " ".join(shlex.quote(part) for part in cmd),
            "cwd": cwd,
            "exit_code": int(proc.returncode),
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "timeout": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(shlex.quote(part) for part in cmd),
            "cwd": cwd,
            "exit_code": 124,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\nTIMEOUT",
            "timeout": True,
        }
    except FileNotFoundError as exc:
        return {
            "command": " ".join(shlex.quote(part) for part in cmd),
            "cwd": cwd,
            "exit_code": 127,
            "stdout": "",
            "stderr": f"{exc}",
            "timeout": False,
        }


def append_validation_markdown(
    path: Path,
    section: str,
    attempt: Dict[str, Any],
    status: str,
    note: str = "",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"## {section}",
        "",
        f"- Status: `{status}`",
        f"- Command: `{attempt.get('command', '')}`",
        f"- Exit code: `{attempt.get('exit_code', 'NA')}`",
    ]
    if note:
        lines.append(f"- Note: {note}")
    stdout = (attempt.get("stdout") or "").strip()
    stderr = (attempt.get("stderr") or "").strip()
    lines.extend(
        [
            "",
            "### stdout",
            "```text",
            stdout[:4000],
            "```",
            "",
            "### stderr",
            "```text",
            stderr[:4000],
            "```",
            "",
        ]
    )
    with path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def dataset_digest(mapping: Mapping[str, np.ndarray]) -> str:
    h = hashlib.sha256()
    for key in sorted(mapping.keys()):
        arr = np.asarray(mapping[key])
        h.update(key.encode("utf-8"))
        h.update(str(arr.dtype).encode("utf-8"))
        h.update(str(arr.shape).encode("utf-8"))
        h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def schema_inventory(mapping: Mapping[str, np.ndarray]) -> Dict[str, Dict[str, Any]]:
    inventory: Dict[str, Dict[str, Any]] = {}
    for key, arr in mapping.items():
        a = np.asarray(arr)
        inventory[key] = {
            "dtype": str(a.dtype),
            "shape": list(a.shape),
        }
    return inventory
