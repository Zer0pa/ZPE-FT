#!/usr/bin/env python3
"""Gate A: runbook/data/schema/resource freeze."""

from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

import numpy as np

from common import (
    append_command_log,
    dataset_digest,
    ensure_artifact_root,
    parse_args,
    schema_inventory,
    utc_now_iso,
    write_json,
)
from zpe_finance.data import (
    generate_ohlcv_bars,
    generate_tick_stream,
    try_fetch_equivalent_market_bars,
)
from zpe_finance.rust_bridge import HAS_RUST, RUST_IMPORT_ERROR, rust_version


RESOURCE_MAP = {
    "gorilla_tsc": "https://github.com/burmanm/gorilla-tsc",
    "time_series_compression": "https://github.com/vinerya/time_series_compression",
    "fintsb": "https://arxiv.org/abs/2502.18834",
    "polygon": "https://polygon.io",
    "kdbx_tsbs": "https://kx.com/blog/benchmarking-kdb-x-vs-questdb-clickhouse-timescaledb-and-influxdb-with-tsbs/",
    "zipline_reloaded": "https://github.com/stefan-jansen/zipline-reloaded",
    "acd_paper": "https://ieeexplore.ieee.org/document/10913266/",
    "neats_paper": "https://arxiv.org/abs/2412.16266",
    "plutus_paper": "https://arxiv.org/abs/2408.10111",
}


def probe_url(url: str, timeout: float = 10.0) -> dict:
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
        return {"status": "OK", "http_code": int(code)}
    except Exception as exc:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                code = getattr(resp, "status", 200)
            return {
                "status": "OK",
                "http_code": int(code),
                "note": "GET fallback after HEAD failure",
            }
        except Exception as exc2:
            return {
                "status": "UNAVAILABLE",
                "error": str(exc2),
                "head_error": str(exc),
            }


def main() -> int:
    parser = parse_args("Gate A freeze")
    args = parser.parse_args()
    artifact_root = ensure_artifact_root(args.artifact_root)

    append_command_log(
        artifact_root,
        "GateA",
        "python3 scripts/gate_a_freeze.py",
        note="start",
    )

    bars = generate_ohlcv_bars(num_bars=250_000, seed=args.seed, tick_size=0.01)
    ticks = generate_tick_stream(num_ticks=600_000, seed=args.seed, tick_size=0.0001)

    market_fetch = try_fetch_equivalent_market_bars(symbol="SPY", years=10)

    datasets = [
        {
            "dataset_id": "synthetic_ohlcv_primary",
            "source_reference": "deterministic_generator",
            "retrieval_timestamp_utc": utc_now_iso(),
            "row_count": int(len(bars["timestamp"])),
            "schema": schema_inventory(bars),
            "content_sha256": dataset_digest(bars),
            "seed": int(args.seed),
            "tick_size": 0.01,
        },
        {
            "dataset_id": "synthetic_tick_primary",
            "source_reference": "deterministic_generator",
            "retrieval_timestamp_utc": utc_now_iso(),
            "row_count": int(len(ticks["timestamp"])),
            "schema": schema_inventory(ticks),
            "content_sha256": dataset_digest(ticks),
            "seed": int(args.seed),
            "tick_size": 0.0001,
        },
    ]

    if market_fetch.status == "OK" and market_fetch.bars is not None:
        datasets.append(
            {
                "dataset_id": "equivalent_market_feed_spy",
                "source_reference": market_fetch.source,
                "retrieval_timestamp_utc": utc_now_iso(),
                "row_count": int(len(market_fetch.bars["timestamp"])),
                "schema": schema_inventory(market_fetch.bars),
                "content_sha256": dataset_digest(market_fetch.bars),
                "note": market_fetch.note,
            }
        )
    else:
        datasets.append(
            {
                "dataset_id": "equivalent_market_feed_spy",
                "source_reference": market_fetch.source,
                "status": market_fetch.status,
                "note": market_fetch.note,
                "substitution": "synthetic_ohlcv_primary",
                "comparability_impact": "external market provenance reduced",
            }
        )

    dataset_lock = {
        "gate": "A",
        "seed_policy": {
            "global_seed": int(args.seed),
            "replay_runs": 5,
        },
        "datasets": datasets,
        "rust_core": {
            "enabled": bool(HAS_RUST),
            "version": rust_version(),
            "import_error": RUST_IMPORT_ERROR,
        },
    }

    schema_inventory_freeze = {
        "bar_schema": schema_inventory(bars),
        "tick_schema": schema_inventory(ticks),
        "schema_version": "zpe-finance-v0.1.0",
        "freeze_timestamp_utc": utc_now_iso(),
    }

    resource_probe = {
        "probe_timestamp_utc": utc_now_iso(),
        "resources": {
            name: {
                "url": url,
                **probe_url(url),
            }
            for name, url in RESOURCE_MAP.items()
        },
    }

    write_json(artifact_root / "dataset_lock.json", dataset_lock)
    write_json(artifact_root / "schema_inventory_freeze.json", schema_inventory_freeze)
    write_json(artifact_root / "resource_probe_results.json", resource_probe)

    append_command_log(
        artifact_root,
        "GateA",
        "write dataset_lock/schema_inventory/resource_probe",
        note="complete",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
