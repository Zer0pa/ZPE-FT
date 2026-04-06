#!/usr/bin/env python3
"""Validate whether FT-C004 has authority-bearing truth attached."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


READY_STATUSES = {
    "AUDITABLE",
    "AUDIT_REFS_ATTACHED",
    "LABELS_ATTACHED",
    "LABELED",
    "READY",
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _truth_items(catalog: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    queries = catalog.get("queries")
    if isinstance(queries, list) and queries:
        return [item for item in queries if isinstance(item, dict)], "queries"
    query_slots = catalog.get("query_slots")
    if isinstance(query_slots, list):
        return [item for item in query_slots if isinstance(item, dict)], "query_slots"
    return [], "queries"


def build_truth_surface_report(catalog: dict[str, Any], catalog_path: Path) -> dict[str, Any]:
    items, source_field = _truth_items(catalog)
    blocked_items = []
    ready_items = []

    for item in items:
        item_id = str(item.get("query_id") or item.get("slot_id") or "unknown")
        truth_status = str(item.get("truth_status") or catalog.get("status") or "MISSING").upper()
        relevant_positions = _as_list(item.get("relevant_positions"))
        audit_refs = (
            _as_list(item.get("audit_refs"))
            + _as_list(item.get("analyst_review_refs"))
            + _as_list(item.get("evidence_refs"))
        )
        is_ready = bool(relevant_positions) or bool(audit_refs) or truth_status in READY_STATUSES
        record = {
            "id": item_id,
            "family": item.get("family"),
            "series_kind": item.get("series_kind"),
            "truth_status": truth_status,
            "relevant_positions_count": len(relevant_positions),
            "audit_ref_count": len(audit_refs),
        }
        if is_ready:
            ready_items.append(record)
        else:
            blocked_items.append(record)

    status = "ready" if items and not blocked_items else "blocked_missing_authority_truth"
    return {
        "claim_id": "FT-C004",
        "catalog_id": catalog.get("catalog_id", "unknown"),
        "catalog_path": str(catalog_path),
        "catalog_status": catalog.get("status", "unknown"),
        "query_source_field": source_field,
        "status": status,
        "target_query_count": catalog.get("target_query_count"),
        "inspected_items": len(items),
        "ready_count": len(ready_items),
        "blocked_count": len(blocked_items),
        "truth_rule": catalog.get(
            "truth_rule",
            "FT-C004 remains non-authority until relevant positions or analyst-reviewed audit references exist per query.",
        ),
        "accepted_truth_modes": [
            "Attach explicit relevant_positions labels to the query.",
            "Attach analyst-reviewed audit_refs or equivalent evidence_refs to the query.",
            "Keep unresolved queries marked NEEDS_LABELS or PENDING_LABEL_AUDIT until one of the above exists.",
        ],
        "required_fields_for_promotion": [
            "query_id or slot_id",
            "truth_status",
            "relevant_positions or analyst_review_refs/audit_refs",
        ],
        "open_blockers": blocked_items,
        "ready_items": ready_items,
        "next_actions": [
            "Attach relevant_positions labels or analyst-reviewed audit references to every authority-bearing FT-C004 query.",
            "Keep unlabeled or auto-generated queries explicitly non-authority.",
            "Do not score FT-C004 as pass until the truth surface is ready.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate FT-C004 truth readiness.")
    parser.add_argument("--query-catalog", required=True, help="Path to the query or slot catalog JSON.")
    parser.add_argument("--output", default="", help="Optional path for the JSON report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    catalog_path = Path(args.query_catalog).expanduser().resolve()
    report = build_truth_surface_report(_read_json(catalog_path), catalog_path)

    if args.output:
        _write_json(Path(args.output).expanduser().resolve(), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
