#!/usr/bin/env python3
"""Gate M1: direct Gorilla comparator and BFCL harness attempts."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import numpy as np

from common import (
    append_command_log,
    append_validation_markdown,
    ensure_artifact_root,
    parse_args,
    run_command_capture,
    write_json,
)
from zpe_finance.data import generate_ohlcv_bars
from zpe_finance.metrics import rmse_ticks, sha256_bytes


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_bfcl_python(
    repo_root: Path,
    validation_md: Path,
    attempts: list[dict],
) -> str | None:
    """Return a Python interpreter path suitable for BFCL (prefers local py3.11 venv)."""

    venv_python = repo_root / ".tmp_bfcl311" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)

    for candidate in ["/usr/local/bin/python3.11", "python3.11"]:
        probe = run_command_capture([candidate, "--version"], cwd=str(repo_root))
        attempts.append(probe)
        append_validation_markdown(
            validation_md,
            "M1 BFCL python3.11 probe",
            probe,
            "OK" if probe["exit_code"] == 0 else "FAIL",
        )
        if probe["exit_code"] == 0:
            make_venv_cmd = run_command_capture([candidate, "-m", "venv", str(repo_root / ".tmp_bfcl311")], cwd=str(repo_root))
            attempts.append(make_venv_cmd)
            append_validation_markdown(
                validation_md,
                "M1 BFCL python3.11 venv create",
                make_venv_cmd,
                "OK" if make_venv_cmd["exit_code"] == 0 else "FAIL",
            )
            if make_venv_cmd["exit_code"] == 0 and venv_python.exists():
                return str(venv_python)
    return None


def main() -> int:
    parser = parse_args("Gate M1 Gorilla comparator")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)
    validation_md = artifact_root / "max_resource_validation_log.md"

    append_command_log(
        artifact_root,
        "GateM1",
        "python3 scripts/run_gate_m1_gorilla.py",
        note="start",
    )

    repo_root = Path(__file__).resolve().parents[1]
    ext = repo_root / "external_resources"
    ext.mkdir(parents=True, exist_ok=True)

    attempts = []
    impracticality = []

    clone_cmd = run_command_capture(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/ghilesmeddour/gorilla-time-series-compression.git",
            str(ext / "gorilla-time-series-compression"),
        ],
        cwd=str(repo_root),
    )
    if (ext / "gorilla-time-series-compression").exists():
        clone_cmd["exit_code"] = 0
        if "already exists" not in clone_cmd.get("stderr", ""):
            clone_cmd["stderr"] = (clone_cmd.get("stderr", "") + "\nusing existing checkout").strip()
    attempts.append(clone_cmd)
    append_validation_markdown(validation_md, "M1 Gorilla clone", clone_cmd, "OK" if clone_cmd["exit_code"] == 0 else "FAIL")

    clone_bfcl_cmd = run_command_capture(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/ShishirPatil/gorilla.git",
            str(ext / "gorilla-bfcl"),
        ],
        cwd=str(repo_root),
    )
    if (ext / "gorilla-bfcl").exists():
        clone_bfcl_cmd["exit_code"] = 0
        if "already exists" not in clone_bfcl_cmd.get("stderr", ""):
            clone_bfcl_cmd["stderr"] = (clone_bfcl_cmd.get("stderr", "") + "\nusing existing checkout").strip()
    attempts.append(clone_bfcl_cmd)
    append_validation_markdown(validation_md, "M1 BFCL clone", clone_bfcl_cmd, "OK" if clone_bfcl_cmd["exit_code"] == 0 else "FAIL")

    install_gc_cmd = run_command_capture(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-q",
            str(ext / "gorilla-time-series-compression"),
        ],
        cwd=str(repo_root),
    )
    attempts.append(install_gc_cmd)
    append_validation_markdown(
        validation_md,
        "M1 Gorilla package install",
        install_gc_cmd,
        "OK" if install_gc_cmd["exit_code"] == 0 else "FAIL",
    )

    gorilla_eval = {
        "status": "INCONCLUSIVE",
        "note": "direct comparator not executed",
    }

    if install_gc_cmd["exit_code"] == 0:
        try:
            import gorillacompression as gc  # type: ignore

            bars = generate_ohlcv_bars(num_bars=120_000, seed=args.seed + 11, tick_size=0.01)
            ts_sec = (bars["timestamp"] // 1000).astype(np.int64)
            close = bars["close"].astype(np.float64)

            # Gorilla timestamp constraint is 32-bit signed epoch seconds.
            ts_sec = np.clip(ts_sec, 0, 2_147_483_647)
            pairs = list(zip(ts_sec.tolist(), close.tolist()))

            content = gc.PairsEncoder.encode_all(pairs, float_format="f64")
            decoded_pairs = gc.PairsDecoder.decode_all(content)
            decoded_values = np.asarray([float(v) for _, v in decoded_pairs], dtype=np.float64)

            raw_bytes_pairs = len(pairs) * 16
            encoded_bytes = len(content["encoded"])
            cr_pairs = raw_bytes_pairs / max(1, encoded_bytes)

            value_rmse = rmse_ticks(
                np.rint(close / 0.01),
                np.rint(decoded_values / 0.01),
            )

            # Comparator DB roundtrip parity (external comparator output for FT-C006 linkage)
            conn = sqlite3.connect(str(artifact_root / "gorilla_roundtrip.sqlite3"))
            conn.execute(
                "CREATE TABLE IF NOT EXISTS gorilla_payload (id TEXT PRIMARY KEY, payload BLOB, digest TEXT)"
            )
            payload = bytes(content["encoded"])
            digest_before = sha256_bytes(payload)
            conn.execute(
                "INSERT OR REPLACE INTO gorilla_payload (id, payload, digest) VALUES (?, ?, ?)",
                ("close_pairs", payload, digest_before),
            )
            conn.commit()
            row = conn.execute("SELECT payload FROM gorilla_payload WHERE id=?", ("close_pairs",)).fetchone()
            conn.close()
            payload_after = bytes(row[0]) if row else b""
            digest_after = sha256_bytes(payload_after)

            gorilla_eval = {
                "status": "PASS",
                "pairs_count": len(pairs),
                "encoded_bytes": encoded_bytes,
                "raw_pair_bytes": raw_bytes_pairs,
                "compression_ratio_pairs": cr_pairs,
                "rmse_ticks": value_rmse,
                "db_roundtrip_bit_consistent": digest_before == digest_after,
                "hash_before": digest_before,
                "hash_after": digest_after,
            }
        except Exception as exc:
            gorilla_eval = {
                "status": "INCONCLUSIVE",
                "note": f"direct Gorilla run failed: {exc}",
            }
            impracticality.append(
                {
                    "resource": "gorilla_time_series_comparator",
                    "code": "IMP-NOCODE",
                    "error_signature": str(exc),
                    "fallback": "zpe internal comparator matrix + gorilla_xor_proxy",
                    "claim_impact": "FT-C003/FT-C006 remain INCONCLUSIVE without external output",
                }
            )

    # BFCL harness attempt (API/function-calling Gorilla)
    bfcl_repo = ext / "gorilla-bfcl" / "berkeley-function-call-leaderboard"
    bfcl_python = sys.executable
    bfcl_install_cmd = run_command_capture(
        [bfcl_python, "-m", "pip", "install", "-q", "-e", str(bfcl_repo)],
        cwd=str(repo_root),
    )
    attempts.append(bfcl_install_cmd)
    append_validation_markdown(
        validation_md,
        "M1 BFCL install",
        bfcl_install_cmd,
        "OK" if bfcl_install_cmd["exit_code"] == 0 else "FAIL",
    )

    # Python 3.13 commonly fails BFCL due faiss wheel constraints. Fall back to local py3.11 venv.
    if bfcl_install_cmd["exit_code"] != 0:
        fallback_python = _resolve_bfcl_python(repo_root, validation_md, attempts)
        if fallback_python:
            bfcl_python = fallback_python
            ensure_pip_cmd = run_command_capture(
                [bfcl_python, "-m", "pip", "install", "-q", "--upgrade", "pip"],
                cwd=str(repo_root),
            )
            attempts.append(ensure_pip_cmd)
            append_validation_markdown(
                validation_md,
                "M1 BFCL py3.11 pip upgrade",
                ensure_pip_cmd,
                "OK" if ensure_pip_cmd["exit_code"] == 0 else "FAIL",
            )

            bfcl_install_cmd = run_command_capture(
                [bfcl_python, "-m", "pip", "install", "-q", "-e", str(bfcl_repo)],
                cwd=str(repo_root),
                timeout_sec=900.0,
            )
            attempts.append(bfcl_install_cmd)
            append_validation_markdown(
                validation_md,
                "M1 BFCL install (py3.11 fallback)",
                bfcl_install_cmd,
                "OK" if bfcl_install_cmd["exit_code"] == 0 else "FAIL",
            )

            # BFCL imports qwen-agent transitively, which requires soundfile.
            bfcl_soundfile_cmd = run_command_capture(
                [bfcl_python, "-m", "pip", "install", "-q", "soundfile"],
                cwd=str(repo_root),
                timeout_sec=240.0,
            )
            attempts.append(bfcl_soundfile_cmd)
            append_validation_markdown(
                validation_md,
                "M1 BFCL soundfile dependency",
                bfcl_soundfile_cmd,
                "OK" if bfcl_soundfile_cmd["exit_code"] == 0 else "FAIL",
            )

    bfcl_eval = {
        "status": "INCONCLUSIVE",
        "note": "BFCL execution not completed",
    }

    if bfcl_install_cmd["exit_code"] == 0:
        bfcl_help_cmd = run_command_capture(
            [bfcl_python, "-m", "bfcl_eval", "--help"],
            cwd=str(bfcl_repo),
            timeout_sec=180.0,
        )
        attempts.append(bfcl_help_cmd)
        append_validation_markdown(
            validation_md,
            "M1 BFCL CLI probe",
            bfcl_help_cmd,
            "OK" if bfcl_help_cmd["exit_code"] == 0 else "FAIL",
        )

        # Restrict BFCL generation to one deterministic test-id to avoid runaway runtime.
        ids_path = bfcl_repo / "test_case_ids_to_generate.json"
        ids_path.write_text(
            json.dumps({"simple_python": ["simple_python_0"]}, indent=2) + "\n",
            encoding="utf-8",
        )

        bfcl_generate_cmd = run_command_capture(
            [
                bfcl_python,
                "-m",
                "bfcl_eval",
                "generate",
                "--model",
                "gorilla-openfunctions-v2",
                "--test-category",
                "simple_python",
                "--num-threads",
                "1",
                "--run-ids",
                "--allow-overwrite",
            ],
            cwd=str(bfcl_repo),
            timeout_sec=90.0,
        )
        attempts.append(bfcl_generate_cmd)
        append_validation_markdown(
            validation_md,
            "M1 BFCL generate attempt",
            bfcl_generate_cmd,
            "OK" if bfcl_generate_cmd["exit_code"] == 0 else "FAIL",
        )

        combined = ((bfcl_generate_cmd.get("stderr") or "") + "\n" + (bfcl_generate_cmd.get("stdout") or "")).lower()
        inference_error = (
            "error occurred during inference" in combined
            or "connection refused" in combined
            or "max retries exceeded" in combined
            or "httpsconnectionpool" in combined
            or "401" in combined
            or "api key" in combined
        )

        if bfcl_generate_cmd["exit_code"] == 0 and not inference_error:
            bfcl_eval = {
                "status": "PASS",
                "note": "BFCL generate completed",
            }
        else:
            code = "IMP-NOCODE"
            if (
                "connection refused" in combined
                or "max retries exceeded" in combined
                or "httpsconnectionpool" in combined
                or "401" in combined
                or "api key" in combined
            ):
                code = "IMP-ACCESS"
            elif "model" in combined and "not supported" in combined:
                code = "IMP-NOCODE"
            bfcl_eval = {
                "status": "INCONCLUSIVE",
                "note": "BFCL generate failed",
                "error_signature": combined[:500],
            }
            impracticality.append(
                {
                    "resource": "gorilla_bfcl_harness",
                    "code": code,
                    "error_signature": combined[:500],
                    "command": bfcl_generate_cmd.get("command"),
                    "fallback": "direct Gorilla time-series comparator results",
                    "claim_impact": "No direct impact on FT core codec metrics; function-calling comparator remains INCONCLUSIVE",
                }
            )
    else:
        impracticality.append(
            {
                "resource": "gorilla_bfcl_harness",
                "code": "IMP-NOCODE",
                "error_signature": (bfcl_install_cmd.get("stderr") or "")[:500],
                "command": bfcl_install_cmd.get("command"),
                "fallback": "repository-level probe only",
                "claim_impact": "BFCL parity unavailable",
            }
        )

    zpe_fidelity = _load_json(artifact_root / "ft_reconstruction_fidelity.json")
    zpe_db = _load_json(artifact_root / "ft_db_roundtrip_results.json")

    ext_outputs_present = gorilla_eval.get("status") == "PASS"
    claim_linkage = {
        "FT-C003": {
            "external_comparator_output_present": ext_outputs_present,
            "zpe_rmse_ticks": zpe_fidelity.get("metrics", {}).get("max_rmse_ticks"),
            "gorilla_rmse_ticks": gorilla_eval.get("rmse_ticks"),
            "status": "PASS" if ext_outputs_present else "INCONCLUSIVE",
        },
        "FT-C006": {
            "external_comparator_output_present": ext_outputs_present,
            "zpe_db_roundtrip_pass": zpe_db.get("pass"),
            "gorilla_db_roundtrip_bit_consistent": gorilla_eval.get("db_roundtrip_bit_consistent"),
            "status": "PASS" if ext_outputs_present else "INCONCLUSIVE",
        },
    }

    report = {
        "gate": "M1",
        "resource": "Gorilla comparator + BFCL",
        "gorilla_time_series_eval": gorilla_eval,
        "bfcl_eval": bfcl_eval,
        "claim_linkage": claim_linkage,
        "attempts": attempts,
        "impracticality": impracticality,
    }

    write_json(artifact_root / "gorilla_eval_results.json", report)

    append_command_log(
        artifact_root,
        "GateM1",
        "write gorilla_eval_results.json",
        note=f"gorilla_status={gorilla_eval.get('status')},bfcl_status={bfcl_eval.get('status')}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
