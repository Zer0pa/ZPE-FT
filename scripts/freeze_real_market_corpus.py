#!/usr/bin/env python3
"""Freeze commercial-safe real-market corpora into a reproducible manifest."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from common import append_command_log, ensure_artifact_root, parse_args, start_comet_logger, utc_now_iso, write_json
from zpe_finance.corpus import (
    freeze_series_entry,
    load_corpus_config,
    load_series_from_spec,
    write_normalized_series,
)
from zpe_finance.metrics import schema_inventory, sha256_file


def _resolve_support_path(raw_path: str, *, base_dir: Path) -> Path:
    path = Path(raw_path).expanduser()
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path


def _query_probe(raw_path: str, *, base_dir: Path) -> dict[str, Any] | None:
    if not raw_path:
        return None
    resolved = _resolve_support_path(raw_path, base_dir=base_dir)
    return {
        "path": str(resolved),
        "exists": resolved.exists(),
        "sha256": sha256_file(resolved) if resolved.exists() else None,
    }


def _series_probe(spec) -> dict[str, Any]:
    return {
        "series_id": spec.series_id,
        "source_path": str(spec.source_path),
        "exists": spec.source_path.exists(),
        "bytes": spec.source_path.stat().st_size if spec.source_path.exists() else None,
        "sha256": sha256_file(spec.source_path) if spec.source_path.exists() else None,
    }


def _build_contract_snapshot(config: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "authority_metric",
        "buyer_workload",
        "baseline_matrix",
        "rights_policy",
        "provenance_policy",
        "truth_catalog",
        "replay_surface",
        "authority_contract_refs",
    )
    return {key: config[key] for key in keys if key in config}


def _write_missing_inputs_packet(
    *,
    artifact_root: Path,
    config_path: Path,
    config: dict[str, Any],
    query_probe: dict[str, Any] | None,
    input_probes: list[dict[str, Any]],
) -> Path:
    missing_series = [
        {
            "series_id": probe["series_id"],
            "path": probe["source_path"],
        }
        for probe in input_probes
        if not probe["exists"]
    ]
    packet = {
        "status": "blocked_missing_inputs",
        "generated_at_utc": utc_now_iso(),
        "corpus_id": config.get("corpus_id", "real_market_corpus"),
        "config_path": str(config_path),
        "config_sha256": sha256_file(config_path),
        "contract": _build_contract_snapshot(config),
        "missing_inputs": {
            "series": missing_series,
            "query_catalog": (
                {
                    "path": query_probe["path"],
                }
                if query_probe and not query_probe["exists"]
                else None
            ),
        },
        "input_probes": input_probes,
        "query_catalog_probe": query_probe,
        "next_action": (
            "Provide the named Phase 06 corpus exports and auditable query catalog, "
            "then rerun freeze_real_market_corpus.py without changing the benchmark contract."
        ),
    }
    packet_path = artifact_root / "missing_inputs_packet.json"
    write_json(packet_path, packet)
    return packet_path


def main() -> int:
    parser = parse_args("Freeze real-market corpus")
    parser.add_argument("--config", required=True, help="Path to the corpus JSON spec")
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve()
    artifact_root = ensure_artifact_root(args.artifact_root)
    comet = start_comet_logger(
        artifact_root,
        "freeze_real_market_corpus",
        args=args,
        tags=("phase-06", "buyer-corpus", "freeze"),
        parameters={"config_path": str(config_path)},
    )
    normalized_dir = artifact_root / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    append_command_log(
        artifact_root,
        "EV-01",
        f"python3 scripts/freeze_real_market_corpus.py --config {config_path}",
        note="start",
    )

    try:
        config, specs = load_corpus_config(config_path)
        query_probe = _query_probe(str(config.get("query_catalog_path", "")).strip(), base_dir=config_path.parent)
        input_probes = [_series_probe(spec) for spec in specs]

        missing_inputs = [probe for probe in input_probes if not probe["exists"]]
        if query_probe and not query_probe["exists"]:
            missing_inputs.append({"series_id": "query_catalog", "source_path": query_probe["path"], "exists": False})

        resource_probe = {
            "probe_timestamp_utc": utc_now_iso(),
            "config_path": str(config_path),
            "config_sha256": sha256_file(config_path),
            "query_catalog": query_probe,
            "inputs": input_probes,
            "missing_inputs": {
                "series": [probe["series_id"] for probe in input_probes if not probe["exists"]],
                "query_catalog": None if not query_probe or query_probe["exists"] else query_probe["path"],
            },
        }
        resource_probe_path = artifact_root / "resource_probe_results.json"
        write_json(resource_probe_path, resource_probe)

        if missing_inputs:
            missing_packet_path = _write_missing_inputs_packet(
                artifact_root=artifact_root,
                config_path=config_path,
                config=config,
                query_probe=query_probe,
                input_probes=input_probes,
            )
            append_command_log(
                artifact_root,
                "EV-01",
                "blocked: named benchmark inputs missing",
                exit_code=2,
                note=(
                    f"missing_series={len([probe for probe in input_probes if not probe['exists']])} "
                    f"missing_query_catalog={bool(query_probe and not query_probe['exists'])}"
                ),
            )
            comet.finalize(
                status="blocked",
                others={
                    "gate": "EV-01",
                    "blocked_reason": "missing_inputs",
                    "missing_series_count": len([probe for probe in input_probes if not probe["exists"]]),
                    "missing_query_catalog": bool(query_probe and not query_probe["exists"]),
                },
                assets=(resource_probe_path, missing_packet_path, artifact_root / "command_log.txt"),
            )
            return 2

        frozen_entries = []
        schema_by_series = {}
        for spec in specs:
            series = load_series_from_spec(spec)
            normalized_path = normalized_dir / f"{spec.series_id}.npz"
            write_normalized_series(normalized_path, series)

            entry = freeze_series_entry(spec, series, normalized_path=normalized_path)
            frozen_entries.append(entry)
            schema_by_series[spec.series_id] = entry["schema"]

        manifest = {
            "corpus_id": config.get("corpus_id", "real_market_corpus"),
            "generated_at_utc": utc_now_iso(),
            "authority_metric": config.get("authority_metric", "AM-C05_FROZEN"),
            "buyer_workload": config.get(
                "buyer_workload",
                "query-by-example over historical price action",
            ),
            "query_catalog_path": query_probe["path"] if query_probe else "",
            "contract": _build_contract_snapshot(config),
            "series": frozen_entries,
        }

        dataset_lock = {
            "gate": "EV-01",
            "config_path": str(config_path),
            "config_sha256": sha256_file(config_path),
            "contract": _build_contract_snapshot(config),
            "datasets": frozen_entries,
        }

        schema_freeze = {
            "schema_version": "zpe-finance-real-market-v0.1.0",
            "freeze_timestamp_utc": utc_now_iso(),
            "series": schema_by_series,
        }

        manifest_path = artifact_root / "real_market_corpus_manifest.json"
        dataset_lock_path = artifact_root / "dataset_lock.json"
        schema_freeze_path = artifact_root / "schema_inventory_freeze.json"

        write_json(manifest_path, manifest)
        write_json(dataset_lock_path, dataset_lock)
        write_json(schema_freeze_path, schema_freeze)

        append_command_log(
            artifact_root,
            "EV-01",
            "write real_market_corpus_manifest/dataset_lock/schema_inventory/resource_probe",
            note=f"series={len(frozen_entries)} contract_keys={len(manifest['contract'])}",
        )
        comet.finalize(
            status="completed",
            metrics={"series_count": len(frozen_entries)},
            others={
                "gate": "EV-01",
                "corpus_id": manifest["corpus_id"],
                "buyer_workload": manifest["buyer_workload"],
            },
            assets=(
                manifest_path,
                dataset_lock_path,
                schema_freeze_path,
                resource_probe_path,
                artifact_root / "command_log.txt",
            ),
        )
        return 0
    except Exception as exc:
        comet.finalize(
            status="failed",
            others={
                "gate": "EV-01",
                "error": str(exc),
                "config_path": str(config_path),
            },
            assets=(artifact_root / "command_log.txt",),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
