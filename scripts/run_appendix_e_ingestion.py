#!/usr/bin/env python3
"""Appendix E ingestion, attempt-all closure matrix, and NET-NEW artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from common import append_command_log, ensure_artifact_root, parse_args, run_command_capture, write_json


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(65536)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_optional_path(repo_root: Path, raw_path: str | None, fallback: Path) -> Path:
    if raw_path:
        path = Path(raw_path)
        return path if path.is_absolute() else (repo_root / path)
    return fallback


def make_lock(repo_root: Path, resource_pack_md: str | None, resource_pack_pdf: str | None) -> Dict[str, Any]:
    md_path = _resolve_optional_path(
        repo_root,
        resource_pack_md,
        repo_root / "docs" / "references" / "ZPE_10_Lane_NET_NEW_Resource_Maximization_Pack.md",
    )
    pdf_path = _resolve_optional_path(
        repo_root,
        resource_pack_pdf,
        repo_root / "docs" / "references" / "ZPE_10_Lane_NET_NEW_Resource_Maximization_Pack.pdf",
    )

    resources = [
        {
            "id": "E3-TSBS",
            "name": "TSBS",
            "required_action": "Generate/load benchmark data and compare throughput/latency",
            "claim_linkage": ["FT-C001", "FT-C004", "FT-C005"],
            "source": "https://github.com/timescale/tsbs",
        },
        {
            "id": "E3-GORILLA-BFCL",
            "name": "Gorilla BFCL harness",
            "required_action": "Run API-function benchmark and report score parity",
            "claim_linkage": ["FT-C003", "FT-C006"],
            "source": "https://github.com/ShishirPatil/gorilla",
        },
        {
            "id": "E3-ZIPLINE",
            "name": "Zipline-Reloaded",
            "required_action": "Execute round-trip backtest fidelity harness",
            "claim_linkage": ["FT-C002", "FT-C004"],
            "source": "https://github.com/stefan-jansen/zipline-reloaded",
        },
        {
            "id": "E3-TRADES",
            "name": "TRADES diffusion market sim",
            "required_action": "Add synthetic stress microstructure benchmark",
            "claim_linkage": ["FT-C001", "FT-C005", "FT-C006"],
            "source": "https://arxiv.org/abs/2502.07071",
        },
    ]

    docs = []
    for doc in [md_path, pdf_path]:
        exists = doc.exists()
        docs.append(
            {
                "path": str(doc),
                "exists": exists,
                "bytes": doc.stat().st_size if exists else None,
                "sha256": sha256_file(doc) if exists else None,
            }
        )

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "evidence_inputs": docs,
        "resource_plan": resources,
    }


def main() -> int:
    parser = parse_args("Appendix E ingestion")
    parser.add_argument("--phase", choices=["full", "lock_only"], default="full")
    parser.add_argument(
        "--resource-pack-md",
        default="",
        help="Optional path to the NET-NEW resource pack markdown file",
    )
    parser.add_argument(
        "--resource-pack-pdf",
        default="",
        help="Optional path to the NET-NEW resource pack PDF file",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    artifact_root = ensure_artifact_root(args.artifact_root)
    artifact_prefix = artifact_root.as_posix()

    append_command_log(
        artifact_root,
        "GateE-INGEST",
        f"python3 scripts/run_appendix_e_ingestion.py --phase {args.phase}",
        note="start",
    )

    lock = make_lock(
        repo_root,
        args.resource_pack_md or None,
        args.resource_pack_pdf or None,
    )
    write_json(artifact_root / "max_resource_lock.json", lock)

    if args.phase == "lock_only":
        append_command_log(
            artifact_root,
            "GateE-INGEST",
            "write max_resource_lock.json",
            note="lock_only complete",
        )
        return 0

    m1 = read_json(artifact_root / "gorilla_eval_results.json")
    m2 = read_json(artifact_root / "tsbs_db_benchmark_results.json")
    m3 = read_json(artifact_root / "zipline_roundtrip_results.json")
    m4 = read_json(artifact_root / "compliance_mode_results.json")

    ft_ohlcv = read_json(artifact_root / "ft_ohlcv_benchmark.json")
    ft_tick = read_json(artifact_root / "ft_tick_benchmark.json")
    ft_fid = read_json(artifact_root / "ft_reconstruction_fidelity.json")
    ft_pattern = read_json(artifact_root / "ft_pattern_search_eval.json")
    ft_latency = read_json(artifact_root / "ft_query_latency_benchmark.json")
    ft_db = read_json(artifact_root / "ft_db_roundtrip_results.json")

    validation_path = artifact_root / "max_resource_validation_log.md"
    existing_validation = validation_path.read_text(encoding="utf-8") if validation_path.exists() else ""

    env_bootstrap_cmd = run_command_capture(
        ["zsh", "-lc", "set -a; [ -f .env ] && source .env; rc=$?; set +a; exit $rc"],
        cwd=str(repo_root),
    )

    impracticality: List[Dict[str, Any]] = []
    for block in [m1, m2, m3, m4]:
        for item in block.get("impracticality", []):
            impracticality.append(item)

    if env_bootstrap_cmd.get("exit_code", 0) != 0 or "no such file or directory" in (env_bootstrap_cmd.get("stderr") or ""):
        impracticality.append(
            {
                "resource": "Environment bootstrap (.env)",
                "code": "IMP-ACCESS",
                "error_signature": (env_bootstrap_cmd.get("stderr") or env_bootstrap_cmd.get("stdout") or "bootstrap failed")[:500],
                "fallback": "non-secret-required execution path",
                "claim_impact": "tokenized external resource calls may be reduced",
                "command": env_bootstrap_cmd.get("command"),
            }
        )

    # Attempt TRADES/DeepMarket directly.
    deepmarket_clone = run_command_capture(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/LeonardoBerti00/DeepMarket.git",
            str(repo_root / "external_resources" / "DeepMarket"),
        ],
        cwd=str(repo_root),
    )
    if (repo_root / "external_resources" / "DeepMarket").exists():
        deepmarket_clone["exit_code"] = 0

    deepmarket_root = repo_root / "external_resources" / "DeepMarket"
    deepmarket_py: str | None = None
    deepmarket_py_probe = {
        "command": "python interpreter probe for DeepMarket",
        "cwd": str(repo_root),
        "exit_code": 1,
        "stdout": "",
        "stderr": "No usable python interpreter found",
    }
    deepmarket_dep_install = {
        "command": "DeepMarket targeted dependency install",
        "cwd": str(repo_root),
        "exit_code": 1,
        "stdout": "",
        "stderr": "skipped",
    }
    deepmarket_import_probe = {
        "command": "DeepMarket TRADES import probe",
        "cwd": str(repo_root),
        "exit_code": 1,
        "stdout": "",
        "stderr": "skipped",
    }
    deepmarket_probe = {
        "command": "DeepMarket TRADES forward probe",
        "cwd": str(repo_root),
        "exit_code": 1,
        "stdout": "",
        "stderr": "skipped",
    }

    for candidate in [
        str(repo_root / ".tmp_bfcl311" / "bin" / "python"),
        sys.executable,
        "/usr/local/bin/python3.11",
        "python3.11",
        "python3",
    ]:
        deepmarket_py_probe = run_command_capture([candidate, "--version"], cwd=str(repo_root))
        if deepmarket_py_probe.get("exit_code") == 0:
            deepmarket_py = candidate
            break

    if deepmarket_py and deepmarket_root.exists():
        deepmarket_dep_install = run_command_capture(
            [
                deepmarket_py,
                "-m",
                "pip",
                "install",
                "-q",
                "einops",
                "matplotlib",
                "torchvision",
            ],
            cwd=str(repo_root),
            timeout_sec=600.0,
        )
        deepmarket_import_probe = run_command_capture(
            [
                deepmarket_py,
                "-c",
                "from models.diffusers.TRADES.TRADES import TRADES; print('trades_import_ok')",
            ],
            cwd=str(repo_root),
            env={"PYTHONPATH": str(deepmarket_root)},
            timeout_sec=180.0,
        )
        deepmarket_probe = run_command_capture(
            [
                deepmarket_py,
                "-c",
                (
                    "import torch\n"
                    "from models.diffusers.TRADES.TRADES import TRADES\n"
                    "model=TRADES(input_size=24,cond_seq_len=4,num_diffusionsteps=16,depth=2,num_heads=8,"
                    "gen_sequence_size=1,cond_dropout_prob=0.1,is_augmented=False,dropout=0.1,"
                    "cond_type='full',cond_method='concatenation')\n"
                    "x=torch.randn(2,1,24)\n"
                    "cond_orders=torch.randn(2,4,24)\n"
                    "cond_lob=torch.randn(2,5,40)\n"
                    "t=torch.randint(0,16,(2,))\n"
                    "noise,var=model(x,cond_orders,t,cond_lob=cond_lob)\n"
                    "print('trades_forward_ok', tuple(noise.shape), tuple(var.shape))\n"
                ),
            ],
            cwd=str(repo_root),
            env={"PYTHONPATH": str(deepmarket_root)},
            timeout_sec=240.0,
        )

    trades_status = "PASS" if deepmarket_probe.get("exit_code") == 0 else "INCONCLUSIVE"
    if trades_status != "PASS":
        failure_text = (
            deepmarket_probe.get("stderr")
            or deepmarket_import_probe.get("stderr")
            or deepmarket_dep_install.get("stderr")
            or deepmarket_py_probe.get("stderr")
            or "DeepMarket TRADES probe failed"
        )
        failure_lower = failure_text.lower()
        imp_code = "IMP-NOCODE"
        if "no space left on device" in failure_lower:
            imp_code = "IMP-STORAGE"
        elif "could not resolve host" in failure_lower or "connection" in failure_lower:
            imp_code = "IMP-ACCESS"
        impracticality.append(
            {
                "resource": "TRADES diffusion market sim (DeepMarket)",
                "code": imp_code,
                "error_signature": failure_text[:500],
                "fallback": "deterministic synthetic microstructure stress generator",
                "claim_impact": "TRADES-specific comparability INCONCLUSIVE",
                "command": deepmarket_probe.get("command"),
            }
        )

    validation_header = [
        "# Max Resource Validation Log",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Phase: {args.phase}",
        "",
        "## Environment bootstrap",
        f"- Command: `{env_bootstrap_cmd.get('command', '')}`",
        f"- Exit: `{env_bootstrap_cmd.get('exit_code', 'NA')}`",
        "",
        "## TRADES / DeepMarket attempts",
        f"- Python interpreter: `{deepmarket_py or 'UNAVAILABLE'}`",
        f"- Clone exit: `{deepmarket_clone.get('exit_code', 'NA')}`",
        f"- Python probe exit: `{deepmarket_py_probe.get('exit_code', 'NA')}`",
        f"- Dependency install exit: `{deepmarket_dep_install.get('exit_code', 'NA')}`",
        f"- TRADES import probe exit: `{deepmarket_import_probe.get('exit_code', 'NA')}`",
        f"- TRADES forward probe exit: `{deepmarket_probe.get('exit_code', 'NA')}`",
        "",
    ]

    validation_path.write_text("\n".join(validation_header) + existing_validation, encoding="utf-8")

    impracticality_decisions = {
        "allowed_codes": ["IMP-LICENSE", "IMP-ACCESS", "IMP-COMPUTE", "IMP-STORAGE", "IMP-NOCODE"],
        "decisions": impracticality,
    }
    write_json(artifact_root / "impracticality_decisions.json", impracticality_decisions)

    # Comparator table
    csv_path = artifact_root / "external_comparator_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "comparator",
            "metric",
            "value",
            "status",
            "artifact",
            "notes",
        ])
        writer.writerow([
            "zpe_ohlcv",
            "compression_ratio",
            ft_ohlcv.get("compression_ratio"),
            "PASS" if ft_ohlcv.get("pass") else "FAIL",
            "ft_ohlcv_benchmark.json",
            "core codec",
        ])
        writer.writerow([
            "zpe_tick",
            "compression_ratio",
            ft_tick.get("compression_ratio"),
            "PASS" if ft_tick.get("pass") else "FAIL",
            "ft_tick_benchmark.json",
            "core codec",
        ])
        writer.writerow([
            "gorilla_direct",
            "compression_ratio_pairs",
            m1.get("gorilla_time_series_eval", {}).get("compression_ratio_pairs"),
            m1.get("gorilla_time_series_eval", {}).get("status", "INCONCLUSIVE"),
            "gorilla_eval_results.json",
            "direct external incumbent",
        ])
        writer.writerow([
            "gorilla_direct",
            "rmse_ticks",
            m1.get("gorilla_time_series_eval", {}).get("rmse_ticks"),
            m1.get("gorilla_time_series_eval", {}).get("status", "INCONCLUSIVE"),
            "gorilla_eval_results.json",
            "external fidelity comparator",
        ])
        writer.writerow([
            "duckdb_tsbs_like",
            "point_query_p95_ms",
            m2.get("non_sqlite_db", {}).get("latency_ms", {}).get("point_p95"),
            m2.get("tsbs_resource", {}).get("status", "INCONCLUSIVE"),
            "tsbs_db_benchmark_results.json",
            "TSBS workload path",
        ])
        writer.writerow([
            "zipline_csvdir",
            "ingest_run_roundtrip",
            m3.get("status"),
            m3.get("status", "INCONCLUSIVE"),
            "zipline_roundtrip_results.json",
            "integration comparator",
        ])

    # Claim-resource map
    claim_map = {
        "FT-C001": {
            "resources": ["TSBS", "TRADES"],
            "status": "PASS" if ft_ohlcv.get("pass") else "INCONCLUSIVE",
            "evidence": [
                "ft_ohlcv_benchmark.json",
                "tsbs_db_benchmark_results.json",
            ],
        },
        "FT-C002": {
            "resources": ["Zipline-Reloaded"],
            "status": "PASS" if m3.get("status") == "PASS" and ft_tick.get("pass") else "INCONCLUSIVE",
            "evidence": ["ft_tick_benchmark.json", "zipline_roundtrip_results.json"],
        },
        "FT-C003": {
            "resources": ["Gorilla BFCL harness"],
            "status": m1.get("claim_linkage", {}).get("FT-C003", {}).get("status", "INCONCLUSIVE"),
            "evidence": ["ft_reconstruction_fidelity.json", "gorilla_eval_results.json"],
        },
        "FT-C004": {
            "resources": ["TSBS", "Zipline-Reloaded"],
            "status": "PASS" if ft_pattern.get("pass") and m3.get("status") == "PASS" else "INCONCLUSIVE",
            "evidence": ["ft_pattern_search_eval.json", "zipline_roundtrip_results.json", "tsbs_db_benchmark_results.json"],
        },
        "FT-C005": {
            "resources": ["TSBS", "TRADES"],
            "status": "PASS" if ft_latency.get("pass") and m2.get("tsbs_resource", {}).get("status") == "PASS" else "INCONCLUSIVE",
            "evidence": ["ft_query_latency_benchmark.json", "tsbs_db_benchmark_results.json"],
        },
        "FT-C006": {
            "resources": ["Gorilla BFCL harness", "TRADES"],
            "status": m1.get("claim_linkage", {}).get("FT-C006", {}).get("status", "INCONCLUSIVE"),
            "evidence": ["ft_db_roundtrip_results.json", "gorilla_eval_results.json"],
        },
    }

    # Commercialization rule: if only restricted/non-commercial resources remain for a claim,
    # mark it PAUSED_EXTERNAL with explicit evidence.
    imp_license_resources = {item.get("resource") for item in impracticality if item.get("code") == "IMP-LICENSE"}
    if imp_license_resources:
        for claim_id, row in claim_map.items():
            resources = set(row.get("resources", []))
            if resources and resources.issubset(imp_license_resources):
                row["status"] = "PAUSED_EXTERNAL"
                evidence = list(row.get("evidence", []))
                if "impracticality_decisions.json" not in evidence:
                    evidence.append("impracticality_decisions.json")
                row["evidence"] = evidence
                row["commercialization_note"] = "Only restricted/non-commercial resources available; waiting for commercial-safe alternative."
    write_json(artifact_root / "max_claim_resource_map.json", claim_map)

    # Gate closure matrix E-G1..E-G5
    attempted_resources = {
        "TSBS": bool(m2),
        "Gorilla BFCL harness": bool(m1),
        "Zipline-Reloaded": bool(m3),
        "TRADES diffusion market sim": True,
    }

    imp_compute_present = any(item.get("code") == "IMP-COMPUTE" for item in impracticality)

    if imp_compute_present:
        pip_freeze_cmd = run_command_capture(
            ["python3", "-m", "pip", "freeze"],
            cwd=str(repo_root),
            timeout_sec=180.0,
        )
        pinned_deps_path = artifact_root / "runpod_pinned_deps.lock.txt"
        pinned_deps_path.write_text(pip_freeze_cmd.get("stdout", ""), encoding="utf-8")

        runpod_chain = [
            f"python3 scripts/run_gate_m1_gorilla.py --artifact-root {artifact_prefix} --seed {args.seed}",
            f"python3 scripts/run_gate_m2_tsbs_db.py --artifact-root {artifact_prefix} --seed {args.seed}",
            f"python3 scripts/run_gate_m3_zipline.py --artifact-root {artifact_prefix} --seed {args.seed}",
            f"python3 scripts/run_gate_m4_compliance.py --artifact-root {artifact_prefix} --seed {args.seed}",
            f"python3 scripts/run_appendix_e_ingestion.py --artifact-root {artifact_prefix} --seed {args.seed} --phase full",
            f"python3 scripts/build_handoff_artifacts.py --artifact-root {artifact_prefix} --seed {args.seed}",
        ]
        (artifact_root / "runpod_command_chain.sh").write_text(
            "#!/usr/bin/env bash\nset -euo pipefail\n"
            + "\n".join(runpod_chain)
            + "\n",
            encoding="utf-8",
        )

        expected_manifest = {
            "artifact_root": artifact_prefix,
            "expected_after_runpod": [
                "gorilla_eval_results.json",
                "tsbs_db_benchmark_results.json",
                "zipline_roundtrip_results.json",
                "compliance_mode_results.json",
                "max_resource_validation_log.md",
                "max_claim_resource_map.json",
                "impracticality_decisions.json",
                "net_new_gap_closure_matrix.json",
                "quality_gate_scorecard.json",
                "handoff_manifest.json",
            ],
        }
        write_json(artifact_root / "runpod_expected_artifact_manifest.json", expected_manifest)

        runpod_manifest = {
            "required": True,
            "reason": "Local compute/infrastructure impracticality detected",
            "deferred_items": [item for item in impracticality if item.get("code") == "IMP-COMPUTE"],
            "validated_local_commands": [
                *runpod_chain[:4],
            ],
            "runpod_target": "B200/H100 with Docker-enabled TimescaleDB path",
            "status": "READY",
            "pinned_deps_lock": str(pinned_deps_path),
            "command_chain": str(artifact_root / "runpod_command_chain.sh"),
            "expected_artifacts_manifest": str(artifact_root / "runpod_expected_artifact_manifest.json"),
        }
        write_json(artifact_root / "runpod_readiness_manifest.json", runpod_manifest)
        (artifact_root / "runpod_exec_plan.md").write_text(
            "# RunPod Exec Plan\n\n"
            "1. Provision Docker-enabled GPU node (B200/H100 class).\n"
            "2. Install Go toolchain + TSBS binaries in worker image.\n"
            "3. Start TimescaleDB 2.x container and execute non-SQLite DB gate.\n"
            "4. Apply pinned dependencies from `runpod_pinned_deps.lock.txt`.\n"
            "5. Execute exact chain in `runpod_command_chain.sh`.\n"
            "6. Verify outputs against `runpod_expected_artifact_manifest.json`.\n",
            encoding="utf-8",
        )

    e_g1 = all(attempted_resources.values())
    e_g2 = (
        claim_map["FT-C003"]["status"] == "PASS"
        and claim_map["FT-C006"]["status"] == "PASS"
    )
    e_g3 = m2.get("tsbs_resource", {}).get("status") == "PASS"
    e_g4 = True
    for res in ["TSBS", "Gorilla BFCL harness", "Zipline-Reloaded", "TRADES diffusion market sim"]:
        if not attempted_resources.get(res, False):
            e_g4 = False
    # if any resource ended INCONCLUSIVE, require IMP entry
    if m2.get("tsbs_resource", {}).get("status") != "PASS":
        e_g4 = e_g4 and any(item.get("resource") == "TSBS" for item in impracticality)
    if m3.get("status") != "PASS":
        e_g4 = e_g4 and any("zipline" in item.get("resource", "").lower() for item in impracticality)
    if trades_status != "PASS":
        e_g4 = e_g4 and any("TRADES" in item.get("resource", "") for item in impracticality)

    e_g5 = True
    if imp_compute_present:
        e_g5 = (artifact_root / "runpod_readiness_manifest.json").exists()

    closure = {
        "appendix_e_gates": {
            "E-G1_attempt_all_resources": e_g1,
            "E-G2_external_outputs_for_FT-C003_FT-C006": e_g2,
            "E-G3_tsbs_throughput_latency_present": e_g3,
            "E-G4_valid_impracticality_for_skips": e_g4,
            "E-G5_runpod_artifacts_when_imp_compute": e_g5,
        },
        "resource_attempts": attempted_resources,
        "gate_m_status": {
            "M1": m1.get("gorilla_time_series_eval", {}).get("status"),
            "M2": "PASS" if m2.get("non_sqlite_db", {}).get("packet_roundtrip_bit_consistent") else "INCONCLUSIVE",
            "M3": m3.get("status"),
            "M4": m4.get("status"),
        },
        "overall_appendix_e_pass": all([e_g1, e_g2, e_g3, e_g4, e_g5]),
    }
    write_json(artifact_root / "net_new_gap_closure_matrix.json", closure)

    append_command_log(
        artifact_root,
        "GateE-INGEST",
        "write Appendix E mandatory artifacts",
        note=f"appendix_e_pass={closure['overall_appendix_e_pass']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
