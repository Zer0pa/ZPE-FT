"""Shared utilities for gate scripts."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from zpe_finance.comet_logging import CometRunLogger
from zpe_finance.metrics import dataset_digest, schema_inventory


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


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    return str(value)


def _git_value(repo_root: Path, *args: str) -> str:
    attempt = run_command_capture(["git", *args], cwd=str(repo_root))
    if attempt["exit_code"] != 0:
        return ""
    return str((attempt["stdout"] or "").strip())


def start_comet_logger(
    artifact_root: Path,
    script_name: str,
    *,
    args: argparse.Namespace | None = None,
    tags: Sequence[str] = (),
    parameters: Mapping[str, Any] | None = None,
    others: Mapping[str, Any] | None = None,
) -> CometRunLogger:
    repo_root = Path(__file__).resolve().parents[1]
    script_parameters: dict[str, Any] = {
        "artifact_root": str(artifact_root),
        "repo_root": str(repo_root),
    }
    if args is not None:
        script_parameters.update({str(key): _json_safe(value) for key, value in vars(args).items()})
    if parameters:
        script_parameters.update({str(key): _json_safe(value) for key, value in parameters.items()})

    git_parameters = {
        "git_branch": _git_value(repo_root, "branch", "--show-current"),
        "git_commit": _git_value(repo_root, "rev-parse", "HEAD"),
        "git_remote_origin": _git_value(repo_root, "remote", "get-url", "origin"),
    }
    script_parameters.update({key: value for key, value in git_parameters.items() if value})

    return CometRunLogger.start(
        artifact_root=artifact_root,
        script_name=script_name,
        tags=tags,
        parameters=script_parameters,
        others=others,
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    from zpe_finance.metrics import write_json as metrics_write_json

    metrics_write_json(path, payload)


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
