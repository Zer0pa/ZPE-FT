#!/usr/bin/env python3
"""Fetch and benchmark the bounded free-data Phase 06 rehearsal lane."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TICKERS = [
    "SPY",
    "QQQ",
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL",
    "META",
    "TSLA",
    "BRK-B",
    "AVGO",
    "LLY",
    "JPM",
    "BAC",
    "GS",
    "MS",
    "C",
    "WFC",
    "BLK",
    "SCHW",
    "CME",
    "SPGI",
    "XLF",
    "DIA",
    "IWM",
    "XLK",
    "XLE",
    "XLV",
    "XLI",
    "SOXX",
]

REQUIRED_TICK_SERIES = [
    {
        "series_id": "aapl_nbbo_20_sessions",
        "symbol": "AAPL",
        "asset_class": "equity_top_of_book",
        "required_freq": "nbbo_tick",
        "required_window": "20_sessions",
        "candidate_source": "rights-safe top-of-book export provider or auditable academic export",
        "target_subpath": "ticks/aapl_nbbo_20_sessions.csv.gz",
        "proxy_or_exact": "exact_required_no_repo_native_proxy",
        "next_action": "Acquire a rights-safe AAPL top-of-book export and place it under proofs/phase06_inputs/ticks/aapl_nbbo_20_sessions.csv.gz.",
    },
    {
        "series_id": "es1_nbbo_20_sessions",
        "symbol": "ES1",
        "asset_class": "futures_top_of_book",
        "required_freq": "top_of_book_tick",
        "required_window": "20_sessions",
        "candidate_source": "rights-safe futures top-of-book export provider",
        "target_subpath": "ticks/es1_nbbo_20_sessions.csv.gz",
        "proxy_or_exact": "exact_required_no_repo_native_proxy",
        "next_action": "Acquire a rights-safe ES1 top-of-book export and place it under proofs/phase06_inputs/ticks/es1_nbbo_20_sessions.csv.gz.",
    },
    {
        "series_id": "eurusd_nbbo_20_sessions",
        "symbol": "EURUSD",
        "asset_class": "fx_top_of_book",
        "required_freq": "top_of_book_tick",
        "required_window": "20_sessions",
        "candidate_source": "rights-safe FX top-of-book export provider",
        "target_subpath": "ticks/eurusd_nbbo_20_sessions.csv.gz",
        "proxy_or_exact": "exact_required_no_repo_native_proxy",
        "next_action": "Acquire a rights-safe EURUSD top-of-book export and place it under proofs/phase06_inputs/ticks/eurusd_nbbo_20_sessions.csv.gz.",
    },
]

BASE_OPEN_BLOCKERS = [
    "Materialize the declared 30-symbol 24-month 1-minute OHLCV authority pack under proofs/phase06_inputs/ohlcv/.",
    "Attach labeled or auditable FT-C004 truth; unlabeled queries remain non-authority.",
]

PHASE06_QUERY_CATALOG_REL = Path("..") / ".gpd" / "phases" / "06-open-access-enterprise-wedge-benchmark" / "phase06_query_catalog.pending.json"
PHASE06_SUMMARY_REL = Path("..") / ".gpd" / "phases" / "06-open-access-enterprise-wedge-benchmark" / "06-03-SUMMARY.md"
PHASE06_TRUTH_GAP_REL = Path("..") / ".gpd" / "phases" / "06-open-access-enterprise-wedge-benchmark" / "06-ftc004-truth-gap.md"


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_open_blockers(repo_root: Path) -> list[str]:
    blockers = list(BASE_OPEN_BLOCKERS)
    tick_root = repo_root / "proofs" / "phase06_inputs" / "ticks"
    missing_tick_targets = []
    if not (tick_root / "aapl_nbbo_20_sessions.csv.gz").exists():
        missing_tick_targets.append("AAPL NBBO/top-of-book")
    if not (tick_root / "es1_nbbo_20_sessions.csv.gz").exists():
        missing_tick_targets.append("ES1 top-of-book")
    if not (tick_root / "eurusd_nbbo_20_sessions.csv.gz").exists():
        missing_tick_targets.append("EURUSD top-of-book")
    if missing_tick_targets:
        blockers.insert(
            1,
            "Materialize the remaining rights-safe tick targets under proofs/phase06_inputs/ticks/: "
            + ", ".join(missing_tick_targets)
            + ".",
        )
    return blockers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch and benchmark the bounded free-data Phase 06 lane.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the zpe-finance repo root",
    )
    parser.add_argument(
        "--symbols",
        default=",".join(TICKERS),
        help="Comma-separated ticker list for the OHLCV rehearsal lane",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Reuse existing CSV.gz files instead of downloading from yfinance",
    )
    parser.add_argument(
        "--skip-daily",
        action="store_true",
        help="Skip the 2-year daily OHLCV lane",
    )
    parser.add_argument(
        "--skip-minute",
        action="store_true",
        help="Skip the requested 30-day 1-minute OHLCV lane",
    )
    parser.add_argument(
        "--skip-tick",
        action="store_true",
        help="Skip the bounded Dukascopy tick proxy lane",
    )
    parser.add_argument(
        "--latency-repetitions",
        type=int,
        default=3,
        help="Latency repetitions passed through to run_real_market_refresh.py",
    )
    parser.add_argument(
        "--truth-catalog",
        default="",
        help="Optional FT-C004 truth catalog override for the boundary report",
    )
    return parser.parse_args()


def normalize_series_slug(symbol: str) -> str:
    return symbol.lower().replace(".", "").replace("-", "")


def normalize_file_slug(symbol: str) -> str:
    return symbol.lower().replace(".", "-")


@dataclass
class LaneSpec:
    lane_id: str
    period: str
    interval: str
    suffix: str
    non_authority_reason: str
    fallback_period: str | None = None
    fallback_suffix: str | None = None

def lane_specs(args: argparse.Namespace) -> list[LaneSpec]:
    lanes: list[LaneSpec] = []
    if not args.skip_daily:
        lanes.append(
            LaneSpec(
                lane_id="daily_24m",
                period="2y",
                interval="1d",
                suffix="1d_24m",
                non_authority_reason="Daily bars are free and useful for rehearsal, but they do not satisfy the 1-minute authority contract.",
            )
        )
    if not args.skip_minute:
        lanes.append(
            LaneSpec(
                lane_id="minute_30d",
                period="30d",
                interval="1m",
                suffix="1m_30d",
                non_authority_reason=(
                    "Yahoo 1-minute data is currently capped below the requested 30-day window on this machine; "
                    "the runner falls back to the provider maximum and still treats the result as non-authority."
                ),
                fallback_period="8d",
                fallback_suffix="1m_8d",
            )
        )
    if not args.skip_tick:
        lanes.append(
            LaneSpec(
                lane_id="tick_20_sessions",
                period="20_sessions",
                interval="tick",
                suffix="tick_proxy",
                non_authority_reason=(
                    "This bounded Dukascopy lane contains 20 one-hour liquid-session slices for AAPL, EURUSD, and an ES1-adjacent "
                    "E_SandP-500 proxy. It advances the real-market tick surface but does not close the exact 20-session authority contract."
                ),
            )
        )
    return lanes


def import_market_stack():
    try:
        import pandas as pd  # type: ignore
        import yfinance as yf  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "Missing market dependencies. Install at least pandas and yfinance in the active environment. "
            f"Import error: {exc}"
        ) from exc
    return pd, yf


def flatten_yfinance_frame(frame, symbol: str, pd):
    if frame is None or len(frame) == 0:
        return frame
    if isinstance(frame.columns, pd.MultiIndex):
        if symbol in frame.columns.get_level_values(-1):
            frame = frame.xs(symbol, axis=1, level=-1)
        elif len(set(frame.columns.get_level_values(-1))) == 1:
            frame = frame.droplevel(-1, axis=1)
    return frame


def normalize_yfinance_frame(frame, symbol: str, pd):
    normalized = flatten_yfinance_frame(frame, symbol, pd)
    if normalized is None or len(normalized) == 0:
        return None

    columns = {str(col).strip().lower(): col for col in normalized.columns}
    required = {
        "open": columns.get("open"),
        "high": columns.get("high"),
        "low": columns.get("low"),
        "close": columns.get("close"),
        "volume": columns.get("volume"),
    }
    if any(value is None for value in required.values()):
        missing = [key for key, value in required.items() if value is None]
        raise ValueError(f"{symbol}: yfinance frame missing columns {missing}")

    timestamps = pd.to_datetime(normalized.index, utc=True)
    open_col = normalized[required["open"]].astype("float64")
    high_col = normalized[required["high"]].astype("float64")
    low_col = normalized[required["low"]].astype("float64")
    close_col = normalized[required["close"]].astype("float64")

    # Some provider rows violate the strict bar invariants the corpus loader enforces.
    low_col = pd.concat([low_col, open_col, close_col], axis=1).min(axis=1)
    high_col = pd.concat([high_col, open_col, close_col], axis=1).max(axis=1)

    out = pd.DataFrame(
        {
            "timestamp": timestamps.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "open": open_col,
            "high": high_col,
            "low": low_col,
            "close": close_col,
            "volume": normalized[required["volume"]].fillna(0.0).astype("float64"),
        }
    )
    return out


def _existing_lane_file(output_dir: Path, symbol: str, lane: LaneSpec) -> tuple[Path, str, str] | None:
    candidates = [
        (
            output_dir / f"{normalize_file_slug(symbol)}_{lane.suffix}.csv.gz",
            f"{normalize_series_slug(symbol)}_{lane.suffix}",
            lane.period,
        )
    ]
    if lane.fallback_period and lane.fallback_suffix:
        candidates.append(
            (
                output_dir / f"{normalize_file_slug(symbol)}_{lane.fallback_suffix}.csv.gz",
                f"{normalize_series_slug(symbol)}_{lane.fallback_suffix}",
                lane.fallback_period,
            )
        )
    for path, series_id, actual_period in candidates:
        if path.exists():
            return path, series_id, actual_period
    return None


def fetch_lane_data(
    *,
    repo_root: Path,
    lane: LaneSpec,
    symbols: list[str],
    skip_download: bool,
) -> dict[str, Any]:
    pd, yf = import_market_stack()
    output_dir = repo_root / "data" / "ohlcv"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_entries: list[dict[str, Any]] = []

    for symbol in symbols:
        file_path = output_dir / f"{normalize_file_slug(symbol)}_{lane.suffix}.csv.gz"
        series_id = f"{normalize_series_slug(symbol)}_{lane.suffix}"

        if skip_download:
            existing = _existing_lane_file(output_dir, symbol, lane)
            if existing:
                existing_path, existing_series_id, actual_period = existing
                manifest_entries.append(
                    {
                        "series_id": existing_series_id,
                        "symbol": symbol,
                        "path": str(existing_path),
                        "status": "reused",
                        "rows": None,
                        "period": lane.period,
                        "actual_period": actual_period,
                        "interval": lane.interval,
                    }
                )
            else:
                manifest_entries.append(
                    {
                        "series_id": series_id,
                        "symbol": symbol,
                        "path": str(file_path),
                        "status": "missing_local_file",
                        "rows": 0,
                        "period": lane.period,
                        "actual_period": lane.period,
                        "interval": lane.interval,
                    }
                )
            continue

        actual_period = lane.period
        actual_suffix = lane.suffix
        frame = yf.download(
            symbol,
            period=lane.period,
            interval=lane.interval,
            auto_adjust=False,
            progress=False,
            threads=False,
            timeout=30,
        )
        normalized = normalize_yfinance_frame(frame, symbol, pd)
        if normalized is None and lane.fallback_period and lane.fallback_suffix:
            actual_period = lane.fallback_period
            actual_suffix = lane.fallback_suffix
            file_path = output_dir / f"{normalize_file_slug(symbol)}_{actual_suffix}.csv.gz"
            series_id = f"{normalize_series_slug(symbol)}_{actual_suffix}"
            frame = yf.download(
                symbol,
                period=lane.fallback_period,
                interval=lane.interval,
                auto_adjust=False,
                progress=False,
                threads=False,
                timeout=30,
            )
            normalized = normalize_yfinance_frame(frame, symbol, pd)
        if normalized is None or len(normalized) == 0:
            manifest_entries.append(
                {
                    "series_id": series_id,
                    "symbol": symbol,
                    "path": str(file_path),
                    "status": "empty",
                    "rows": 0,
                    "period": lane.period,
                    "actual_period": actual_period,
                    "interval": lane.interval,
                }
            )
            continue

        normalized.to_csv(file_path, index=False, compression="gzip")
        manifest_entries.append(
            {
                "series_id": series_id,
                "symbol": symbol,
                "path": str(file_path),
                "status": "downloaded",
                "rows": int(len(normalized)),
                "period": lane.period,
                "actual_period": actual_period,
                "interval": lane.interval,
                "start": str(normalized.iloc[0]["timestamp"]),
                "end": str(normalized.iloc[-1]["timestamp"]),
            }
        )

    manifest = {
        "lane_id": lane.lane_id,
        "generated_at_utc": utc_now_iso(),
        "source": "yfinance",
        "period": lane.period,
        "interval": lane.interval,
        "status_counts": {
            "downloaded": sum(1 for entry in manifest_entries if entry["status"] == "downloaded"),
            "reused": sum(1 for entry in manifest_entries if entry["status"] == "reused"),
            "empty": sum(1 for entry in manifest_entries if entry["status"] == "empty"),
            "missing_local_file": sum(1 for entry in manifest_entries if entry["status"] == "missing_local_file"),
        },
        "entries": manifest_entries,
        "non_authority_reason": lane.non_authority_reason,
    }
    manifest_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane.lane_id / "fetch_manifest.json"
    write_json(manifest_path, manifest)
    return manifest


def fetch_tick_lane_data(
    *,
    repo_root: Path,
    lane: LaneSpec,
    skip_download: bool,
) -> tuple[dict[str, Any], Path]:
    status_path = repo_root / "data" / "ticks" / "tick_fetch_status.json"
    fetch_cmd = [
        sys.executable,
        str(repo_root / "scripts" / "fetch_dukascopy_ticks.py"),
        "--repo-root",
        str(repo_root),
    ]
    if skip_download:
        fetch_cmd.append("--skip-download")

    fetch_result = run_command(repo_root=repo_root, cmd=fetch_cmd, env=dict(os.environ))
    fetch_log_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane.lane_id / "tick_fetch_command.txt"
    write_command_result(fetch_log_path, fetch_result)
    if fetch_result["exit_code"] != 0:
        raise SystemExit(f"fetch_dukascopy_ticks.py failed with exit code {fetch_result['exit_code']}")
    if not status_path.exists():
        raise SystemExit("fetch_dukascopy_ticks.py did not materialize data/ticks/tick_fetch_status.json")

    status_payload = read_json(status_path)
    manifest_entries = []
    for entry in status_payload.get("entries", []):
        if not isinstance(entry, dict):
            continue
        raw_path = str(entry.get("path") or "")
        resolved_path = Path(raw_path).expanduser()
        if raw_path and not resolved_path.is_absolute():
            resolved_path = (repo_root / raw_path).resolve()
        materialized_sessions = entry.get("materialized_sessions")
        actual_period = lane.period
        if materialized_sessions:
            actual_period = f"{materialized_sessions}x1h_slices"
        manifest_entries.append(
            {
                "series_id": entry["series_id"],
                "symbol": entry["symbol"],
                "instrument": entry.get("instrument") or entry.get("dukascopy_instrument"),
                "path": str(resolved_path),
                "status": entry["status"],
                "rows": entry.get("rows", entry.get("row_count")),
                "period": lane.period,
                "actual_period": actual_period,
                "interval": lane.interval,
                "start": entry.get("materialized_start_utc"),
                "end": entry.get("materialized_end_utc"),
                "tick_size": entry.get("tick_size"),
                "exact_contract_match": bool(entry.get("exact_contract", entry.get("exact_contract_match"))),
                "contract_gap_reason": entry.get("authority_note") or entry.get("exact_gap_reason"),
            }
        )

    manifest = {
        "lane_id": lane.lane_id,
        "generated_at_utc": utc_now_iso(),
        "source": status_payload.get("source", "Dukascopy freeserv historical ticks"),
        "period": lane.period,
        "interval": lane.interval,
        "status_counts": {
            "downloaded": sum(1 for entry in manifest_entries if entry["status"] == "downloaded"),
            "reused": sum(1 for entry in manifest_entries if entry["status"] == "reused"),
            "empty": sum(1 for entry in manifest_entries if entry["status"] == "empty"),
            "error": sum(1 for entry in manifest_entries if entry["status"] == "error"),
            "missing_local_file": sum(1 for entry in manifest_entries if entry["status"] == "missing_local_file"),
        },
        "entries": manifest_entries,
        "non_authority_reason": lane.non_authority_reason,
    }
    manifest_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane.lane_id / "fetch_manifest.json"
    write_json(manifest_path, manifest)
    return manifest, status_path


def build_corpus_config(repo_root: Path, lane: LaneSpec, manifest: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    series = []
    for entry in manifest["entries"]:
        if entry["status"] not in {"downloaded", "reused"}:
            continue
        actual_period = str(entry.get("actual_period") or lane.period)
        provenance = f"Yahoo Finance via yfinance ({lane.interval}, requested {lane.period}, actual {actual_period})"
        series.append(
            {
                "series_id": entry["series_id"],
                "kind": "ohlcv",
                "source_path": entry["path"],
                "symbol": entry["symbol"],
                "tick_size": 0.01,
                "provenance": provenance,
                "license_note": f"Free/public proxy lane only. {lane.non_authority_reason}",
                "timezone": "UTC",
                "timestamp_format": "iso8601",
                "columns": {
                    "timestamp": "timestamp",
                    "open": "open",
                    "high": "high",
                    "low": "low",
                    "close": "close",
                    "volume": "volume",
                },
            }
        )

    config = {
        "corpus_id": f"phase06_partial_{lane.lane_id}",
        "authority_metric": "AM-C05_FROZEN",
        "buyer_workload": "query-by-example over historical price action",
        "baseline_matrix": {
            "ohlcv": ["raw_csv_scan", "sqlite_sidecar_roundtrip"],
            "comparison_rule": "Free-data rehearsal only; this config may not be promoted as Phase 06 authority closure.",
        },
        "rights_policy": {
            "classification": "free_public_proxy_non_authority",
            "freeze_rule": "Reproducible provenance is required, but this lane remains a rehearsal proxy rather than the authority suite.",
        },
        "truth_catalog": {
            "ft_c004": {
                "mode": "labels_pending_non_authority",
                "unresolved_rule": "Auto-generated queries on this lane are non-authority and must remain NEEDS_LABELS.",
            }
        },
        "series": series,
    }
    config_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane.lane_id / "corpus_config.json"
    write_json(config_path, config)
    return config_path, config


def build_tick_corpus_config(repo_root: Path, lane: LaneSpec, manifest: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    series = []
    for entry in manifest["entries"]:
        if entry["status"] not in {"downloaded", "reused"}:
            continue
        provenance = (
            f"Dukascopy freeserv chart/json3 ({entry['instrument']}, requested {lane.period}, actual {entry['actual_period']})"
        )
        series.append(
            {
                "series_id": entry["series_id"],
                "kind": "tick",
                "source_path": entry["path"],
                "symbol": entry["symbol"],
                "tick_size": float(entry["tick_size"]),
                "provenance": provenance,
                "license_note": f"Bounded public tick lane only. {entry.get('contract_gap_reason') or lane.non_authority_reason}",
                "timezone": "UTC",
                "timestamp_format": "iso8601",
                "columns": {
                    "timestamp": "timestamp",
                    "bid": "bid",
                    "ask": "ask",
                    "bid_size": "bid_size",
                    "ask_size": "ask_size",
                },
            }
        )

    config = {
        "corpus_id": f"phase06_partial_{lane.lane_id}",
        "authority_metric": "AM-C05_FROZEN",
        "buyer_workload": "query-by-example over historical price action",
        "baseline_matrix": {
            "tick": ["raw_csv_scan", "top_of_book_scan", "sqlite_sidecar_roundtrip"],
            "comparison_rule": "Free-data rehearsal only; this config may not be promoted as Phase 06 authority closure.",
        },
        "rights_policy": {
            "classification": "free_public_proxy_non_authority",
            "freeze_rule": "Reproducible provenance is required, but this lane remains a rehearsal proxy rather than the authority suite.",
        },
        "truth_catalog": {
            "ft_c004": {
                "mode": "labels_pending_non_authority",
                "unresolved_rule": "Auto-generated queries on this lane are non-authority and must remain NEEDS_LABELS.",
            }
        },
        "series": series,
    }
    config_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane.lane_id / "corpus_config.json"
    write_json(config_path, config)
    return config_path, config


def run_command(*, repo_root: Path, cmd: list[str], env: dict[str, str]) -> dict[str, Any]:
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "command": cmd,
        "exit_code": int(proc.returncode),
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def write_command_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"command: {' '.join(result['command'])}",
        f"exit_code: {result['exit_code']}",
        "",
        "stdout:",
        result["stdout"],
        "",
        "stderr:",
        result["stderr"],
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def benchmark_lane(
    *,
    repo_root: Path,
    lane: LaneSpec,
    config_path: Path,
    latency_repetitions: int,
) -> dict[str, Any]:
    artifact_dir = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane.lane_id / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    python_path = str(repo_root / "python")
    env["PYTHONPATH"] = python_path if not env.get("PYTHONPATH") else f"{python_path}:{env['PYTHONPATH']}"

    freeze_cmd = [
        sys.executable,
        str(repo_root / "scripts" / "freeze_real_market_corpus.py"),
        "--artifact-root",
        str(artifact_dir),
        "--config",
        str(config_path),
    ]
    freeze_result = run_command(repo_root=repo_root, cmd=freeze_cmd, env=env)
    write_command_result(artifact_dir / "freeze_command.txt", freeze_result)
    if freeze_result["exit_code"] != 0:
        return {
            "lane_id": lane.lane_id,
            "status": "freeze_failed",
            "freeze_exit_code": freeze_result["exit_code"],
            "artifact_dir": str(artifact_dir),
        }

    manifest_path = artifact_dir / "real_market_corpus_manifest.json"
    refresh_cmd = [
        sys.executable,
        str(repo_root / "scripts" / "run_real_market_refresh.py"),
        "--artifact-root",
        str(artifact_dir),
        "--manifest",
        str(manifest_path),
        "--latency-repetitions",
        str(latency_repetitions),
    ]
    refresh_result = run_command(repo_root=repo_root, cmd=refresh_cmd, env=env)
    write_command_result(artifact_dir / "refresh_command.txt", refresh_result)

    summary = {
        "lane_id": lane.lane_id,
        "status": "completed" if refresh_result["exit_code"] == 0 else "refresh_failed",
        "freeze_exit_code": freeze_result["exit_code"],
        "refresh_exit_code": refresh_result["exit_code"],
        "artifact_dir": str(artifact_dir),
        "non_authority_reason": lane.non_authority_reason,
    }

    for report_name in (
        "ft_ohlcv_benchmark.json",
        "ft_tick_benchmark.json",
        "ft_reconstruction_fidelity.json",
        "ft_encode_decode_latency.json",
        "ft_query_latency_benchmark.json",
        "ft_pattern_search_eval.json",
        "ft_db_roundtrip_results.json",
    ):
        report_path = artifact_dir / report_name
        if report_path.exists():
            summary[report_name] = read_json(report_path)
    return summary


def load_existing_latest(repo_root: Path) -> list[dict[str, Any]]:
    latest_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / "LATEST.json"
    if not latest_path.exists():
        return []
    try:
        payload = read_json(latest_path)
    except Exception:
        return []
    lanes = payload.get("lanes", [])
    if not isinstance(lanes, list):
        return []
    return [lane for lane in lanes if isinstance(lane, dict) and lane.get("lane_id")]


def merge_lane_results(existing: list[dict[str, Any]], current: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for lane in existing:
        lane_id = str(lane.get("lane_id") or "").strip()
        if lane_id:
            merged[lane_id] = lane
    for lane in current:
        lane_id = str(lane.get("lane_id") or "").strip()
        if lane_id:
            merged[lane_id] = lane
    return [merged[lane_id] for lane_id in sorted(merged.keys())]


def load_fetch_manifest(repo_root: Path, lane_id: str) -> dict[str, Any]:
    path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane_id / "fetch_manifest.json"
    if not path.exists():
        return {}
    return read_json(path)


def summarize_actual_window(manifest: dict[str, Any]) -> str:
    if not manifest:
        return "unknown"
    requested_period = str(manifest.get("period") or "")
    interval = str(manifest.get("interval") or "")
    actual_periods = sorted(
        {
            str(entry.get("actual_period") or requested_period)
            for entry in manifest.get("entries", [])
            if entry.get("status") in {"downloaded", "reused"}
        }
    )
    if not actual_periods:
        return f"requested {requested_period} @ {interval}; no materialized series"
    if len(actual_periods) == 1:
        actual_period = actual_periods[0]
        if actual_period != requested_period:
            return f"{actual_period} @ {interval} per materialized series (requested {requested_period})"
        return f"{actual_period} @ {interval}"
    return ", ".join(f"{period} @ {interval}" for period in actual_periods)


def _metric_or_none(result: dict[str, Any], *keys: str) -> float | None:
    cursor: Any = result
    for key in keys:
        if not isinstance(cursor, dict) or key not in cursor:
            return None
        cursor = cursor[key]
    if cursor is None:
        return None
    try:
        return float(cursor)
    except (TypeError, ValueError):
        return None


def _lane_deviations(lane_id: str, manifest: dict[str, Any], result: dict[str, Any]) -> list[str]:
    deviations: list[str] = []
    requested_period = str(manifest.get("period") or "")
    actual_window = summarize_actual_window(manifest)
    truth_status = str(result.get("ft_pattern_search_eval.json", {}).get("status") or "UNKNOWN")
    min_ratio = _metric_or_none(result, "ft_ohlcv_benchmark.json", "aggregate", "min_compression_ratio")
    min_tick_ratio = _metric_or_none(result, "ft_tick_benchmark.json", "aggregate", "min_compression_ratio")
    ohlcv_series_count = len(result.get("ft_ohlcv_benchmark.json", {}).get("series", []))
    tick_series_count = len(result.get("ft_tick_benchmark.json", {}).get("series", []))

    if lane_id == "daily_24m":
        deviations.append("Uses daily bars instead of the declared 1-minute authority cadence.")
    if lane_id == "minute_30d" and requested_period and "requested" in actual_window:
        deviations.append(f"Provider delivered {actual_window} rather than the requested {requested_period} @ {manifest.get('interval')}.")
    if lane_id == "tick_20_sessions":
        deviations.append("Dukascopy supplies bounded one-hour liquid-session top-of-book slices here, not the exact 20-session authority export.")
        deviations.append("The AAPL file is a single-provider top-of-book feed rather than an exact NBBO pack.")
        deviations.append("The ES1 file is populated with Dukascopy E_SandP-500, which is useful but not the exact ES1 contract.")
        deviations.append("The EURUSD file is useful top-of-book rehearsal data, but it is still a bounded proxy slice rather than the exact authority pack under proofs/phase06_inputs/ticks/.")
    if truth_status != "PASS":
        deviations.append(f"FT-C004 remains {truth_status}; unlabeled retrieval is non-authority.")
    if ohlcv_series_count and min_ratio is not None and min_ratio < 10.0:
        deviations.append(f"Minimum OHLCV compression remains below the 10x authority floor ({min_ratio:.4f}x).")
    if tick_series_count and min_tick_ratio is not None and min_tick_ratio < 8.0:
        deviations.append(f"Minimum tick compression remains below the 8x authority floor ({min_tick_ratio:.4f}x).")
    if lane_id != "tick_20_sessions":
        deviations.append("No AAPL, ES1, or EURUSD top-of-book tick series are included in this lane.")
    return deviations


def build_lane_contract_status(repo_root: Path, lane_result: dict[str, Any]) -> dict[str, Any]:
    lane_id = str(lane_result.get("lane_id") or "unknown")
    manifest = load_fetch_manifest(repo_root, lane_id)
    entries = [entry for entry in manifest.get("entries", []) if entry.get("status") in {"downloaded", "reused"}]
    failed_symbols = sorted(
        {str(entry.get("symbol")) for entry in manifest.get("entries", []) if entry.get("status") not in {"downloaded", "reused"}}
    )
    truth_status = str(lane_result.get("ft_pattern_search_eval.json", {}).get("status") or "UNKNOWN")

    return {
        "generated_at_utc": utc_now_iso(),
        "lane_id": lane_id,
        "authority_class": "bounded_public_non_authority_proxy",
        "phase06_contract_match": False,
        "promotion_forbidden": True,
        "requested_data_window": f"{manifest.get('period')} @ {manifest.get('interval')}" if manifest else "unknown",
        "actual_data_window": summarize_actual_window(manifest),
        "coverage": {
            "downloaded_or_reused_count": len(entries),
            "expected_count": len(manifest.get("entries", [])),
            "failed_symbols": failed_symbols,
            "exact_contract_count": sum(1 for entry in entries if entry.get("exact_contract_match")),
            "proxy_count": sum(1 for entry in entries if not entry.get("exact_contract_match")),
        },
        "truth_status": truth_status,
        "known_deviations": _lane_deviations(lane_id, manifest, lane_result),
        "open_blockers": build_open_blockers(repo_root),
        "metrics": {
            "ohlcv_mean_compression_ratio": _metric_or_none(
                lane_result,
                "ft_ohlcv_benchmark.json",
                "aggregate",
                "mean_compression_ratio",
            ),
            "ohlcv_min_compression_ratio": _metric_or_none(
                lane_result,
                "ft_ohlcv_benchmark.json",
                "aggregate",
                "min_compression_ratio",
            ),
            "query_latency_p95_ms": _metric_or_none(
                lane_result,
                "ft_query_latency_benchmark.json",
                "latencies_ms",
                "p95",
            ),
            "encode_p95_ms": _metric_or_none(
                lane_result,
                "ft_encode_decode_latency.json",
                "aggregate",
                "encode_ms",
                "p95",
            ),
            "decode_p95_ms": _metric_or_none(
                lane_result,
                "ft_encode_decode_latency.json",
                "aggregate",
                "decode_ms",
                "p95",
            ),
            "max_rmse_ticks": _metric_or_none(
                lane_result,
                "ft_reconstruction_fidelity.json",
                "metrics",
                "max_rmse_ticks",
            ),
            "tick_mean_compression_ratio": _metric_or_none(
                lane_result,
                "ft_tick_benchmark.json",
                "aggregate",
                "mean_compression_ratio",
            ),
            "tick_min_compression_ratio": _metric_or_none(
                lane_result,
                "ft_tick_benchmark.json",
                "aggregate",
                "min_compression_ratio",
            ),
        },
    }


def write_lane_contract_statuses(repo_root: Path, lane_results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for result in lane_results:
        lane_id = str(result.get("lane_id") or "").strip()
        if not lane_id:
            continue
        status = build_lane_contract_status(repo_root, result)
        path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane_id / "contract_status.json"
        write_json(path, status)
        statuses[lane_id] = status
    return statuses


def run_truth_surface_check(repo_root: Path, catalog_override: str) -> tuple[Path, dict[str, Any]]:
    truth_report_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / "ft_c004_truth_requirements.json"
    catalog_path = Path(catalog_override).expanduser().resolve() if catalog_override else (repo_root / PHASE06_QUERY_CATALOG_REL).resolve()
    cmd = [
        sys.executable,
        str(repo_root / "scripts" / "check_truth_surface.py"),
        "--query-catalog",
        str(catalog_path),
        "--output",
        str(truth_report_path),
    ]
    result = run_command(repo_root=repo_root, cmd=cmd, env=dict(os.environ))
    write_command_result(
        repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / "check_truth_surface_command.txt",
        result,
    )
    if result["exit_code"] not in {0, 2}:
        raise SystemExit(f"check_truth_surface.py failed with exit code {result['exit_code']}")
    return truth_report_path, read_json(truth_report_path)


def write_boundary_manifest(
    repo_root: Path,
    lane_statuses: dict[str, dict[str, Any]],
    truth_report_path: Path,
    truth_report: dict[str, Any],
) -> Path:
    deviations: list[str] = []
    lane_refs = []
    for lane_id, status in sorted(lane_statuses.items()):
        deviations.extend(status.get("known_deviations", []))
        lane_refs.append(
            {
                "lane_id": lane_id,
                "contract_status_path": str(
                    repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / lane_id / "contract_status.json"
                ),
                "actual_data_window": status.get("actual_data_window"),
                "truth_status": status.get("truth_status"),
            }
        )

    deduped_deviations = list(dict.fromkeys(deviations))
    payload = {
        "generated_at_utc": utc_now_iso(),
        "authority_class": "bounded_public_non_authority_proxy_bundle",
        "phase06_contract_match": False,
        "promotion_forbidden": True,
        "authority_boundary": "These bounded public-data artifacts reduce execution risk, but they cannot be promoted into Phase 06 authority evidence.",
        "known_deviations": deduped_deviations,
        "open_blockers": build_open_blockers(repo_root),
        "truth_status": truth_report.get("status", "unknown"),
        "truth_report_path": str(truth_report_path),
        "lane_contract_statuses": lane_refs,
        "references": [
            "../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-01-benchmark-spec.md",
            "../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-01-query-and-truth-spec.md",
            "../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-02-SUMMARY.md",
            "../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-03-SUMMARY.md",
        ],
    }
    path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / "BOUNDARY.json"
    write_json(path, payload)
    return path


def write_phase06_gap_artifacts(repo_root: Path) -> tuple[Path, Path]:
    phase06_inputs_root = repo_root / "proofs" / "phase06_inputs"
    phase06_inputs_root.mkdir(parents=True, exist_ok=True)
    matrix_path = phase06_inputs_root / "series_gap_matrix.csv"
    readme_path = phase06_inputs_root / "README.md"
    header = [
        "series_id",
        "asset_class",
        "required_freq",
        "required_window",
        "truth_requirement",
        "candidate_source",
        "rights_status",
        "proxy_or_exact",
        "acquired",
        "next_action",
    ]

    with matrix_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        for symbol in TICKERS:
            series_id = f"{normalize_series_slug(symbol)}_1m_24m"
            target_path = phase06_inputs_root / "ohlcv" / f"{series_id}.csv.gz"
            writer.writerow(
                {
                    "series_id": series_id,
                    "asset_class": "equity_ohlcv",
                    "required_freq": "1m",
                    "required_window": "24m",
                    "truth_requirement": "FT-C001/003/005/006 exact corpus plus FT-C004 labels or audit refs",
                    "candidate_source": "rights-safe 24-month 1-minute export provider or auditable open-access equivalent",
                    "rights_status": "UNRESOLVED",
                    "proxy_or_exact": "proxy_daily_24m_and_provider_max_1m_8d_available_exact_required",
                    "acquired": str(target_path.exists()).lower(),
                    "next_action": f"Place the exact export at proofs/phase06_inputs/ohlcv/{series_id}.csv.gz and rerun EV-01.",
                }
            )
        for tick_row in REQUIRED_TICK_SERIES:
            target_path = phase06_inputs_root / tick_row["target_subpath"]
            writer.writerow(
                {
                    "series_id": tick_row["series_id"],
                    "asset_class": tick_row["asset_class"],
                    "required_freq": tick_row["required_freq"],
                    "required_window": tick_row["required_window"],
                    "truth_requirement": "FT-C002/003/005/006 exact corpus plus FT-C004 labels or audit refs",
                    "candidate_source": tick_row["candidate_source"],
                    "rights_status": "UNRESOLVED",
                    "proxy_or_exact": tick_row["proxy_or_exact"],
                    "acquired": str(target_path.exists()).lower(),
                    "next_action": tick_row["next_action"],
                }
            )

    lines = [
        "# Phase 06 Input Ledger",
        "",
        "This directory is the exact-input ledger for the sovereign Phase 06 benchmark. It is intentionally useful even when the exact authority files are still absent.",
        "",
        "## What This Directory Means",
        "",
        "- `series_gap_matrix.csv` is the machine-readable 33-series blocker map.",
        "- `ohlcv/` is reserved for the exact 30-symbol `1m_24m` authority pack.",
        "- `ticks/` is reserved for the exact `AAPL`, `ES1`, and `EURUSD` top-of-book authority pack.",
        "",
        "## Boundary",
        "",
        "- Daily `2y` proxies, provider-max `1m_8d` proxies, and bounded Dukascopy tick slices live under `data/ohlcv/`, `data/ticks/`, and `proofs/artifacts/real_market_benchmarks/`; they are useful, but they are not this directory.",
        "- Populating this directory with exact files is necessary but not sufficient. `FT-C004` still requires labeled or auditable truth.",
        "",
        "## Required References",
        "",
        "- `../artifacts/real_market_benchmarks/BOUNDARY.json`",
        "- `../artifacts/real_market_benchmarks/ft_c004_truth_requirements.json`",
        "- `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-01-benchmark-spec.md`",
        "- `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-01-query-and-truth-spec.md`",
        f"- `{PHASE06_TRUTH_GAP_REL.as_posix()}`",
        "",
        "## Current Status",
        "",
        "As of this snapshot, this directory is a blocker ledger, not an authority-data payload.",
        "",
    ]
    readme_path.write_text("\n".join(lines), encoding="utf-8")
    return matrix_path, readme_path


def _format_metric(metric: float | None, suffix: str = "") -> str:
    if metric is None:
        return "n/a"
    return f"{metric:.4f}{suffix}"


def write_missing_data_readme(
    repo_root: Path,
    lane_statuses: dict[str, dict[str, Any]],
    tick_status_path: Path,
    boundary_path: Path,
    gap_matrix_path: Path,
    gap_readme_path: Path,
    truth_report_path: Path,
) -> Path:
    daily = lane_statuses.get("daily_24m")
    minute = lane_statuses.get("minute_30d")
    tick = lane_statuses.get("tick_20_sessions")

    lines = [
        "# Missing Data Status",
        "",
        "This note records what the repo can fetch and benchmark today without pretending the sovereign Phase 06 gate is closed.",
        "",
        "## Available Now",
        "",
        "- Bounded public rehearsal lane: 30 US equity OHLCV symbols via yfinance.",
        "- Bounded Dukascopy tick proxy lane: 20x1h liquid-session slices for EURUSD, AAPL, and E_SandP-500.",
        "- Repo-native bounded runner: `scripts/run_phase06_partial.py` freezes and reruns the current public proxy slices through the real-market lane.",
        "- Machine-readable boundary artifacts: `proofs/artifacts/real_market_benchmarks/BOUNDARY.json`, per-lane `contract_status.json`, `proofs/phase06_inputs/series_gap_matrix.csv`, and `proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json`.",
        "",
        "## Latest Observed Proxy Results",
        "",
    ]

    if daily:
        metrics = daily["metrics"]
        lines.extend(
            [
                (
                    f"- Daily proxy lane: `{daily['coverage']['downloaded_or_reused_count']}/{daily['coverage']['expected_count']}` symbols, "
                    f"`{daily['actual_data_window']}`, mean compression `{_format_metric(metrics['ohlcv_mean_compression_ratio'], 'x')}`, "
                    f"min compression `{_format_metric(metrics['ohlcv_min_compression_ratio'], 'x')}`, "
                    f"query latency `p95 = {_format_metric(metrics['query_latency_p95_ms'], ' ms')}`, "
                    f"encode `p95 = {_format_metric(metrics['encode_p95_ms'], ' ms')}`, "
                    f"decode `p95 = {_format_metric(metrics['decode_p95_ms'], ' ms')}`, "
                    f"`FT-C004 = {daily['truth_status']}`."
                ),
                "- Daily bars remain non-authority because the declared Phase 06 contract requires 24 months of 1-minute bars, not 2 years of daily bars.",
            ]
        )

    if minute:
        metrics = minute["metrics"]
        lines.extend(
            [
                (
                    f"- Provider-max minute proxy lane: `{minute['coverage']['downloaded_or_reused_count']}/{minute['coverage']['expected_count']}` symbols, "
                    f"`{minute['actual_data_window']}`, mean compression `{_format_metric(metrics['ohlcv_mean_compression_ratio'], 'x')}`, "
                    f"min compression `{_format_metric(metrics['ohlcv_min_compression_ratio'], 'x')}`, "
                    f"query latency `p95 = {_format_metric(metrics['query_latency_p95_ms'], ' ms')}`, "
                    f"encode `p95 = {_format_metric(metrics['encode_p95_ms'], ' ms')}`, "
                    f"decode `p95 = {_format_metric(metrics['decode_p95_ms'], ' ms')}`, "
                    f"`FT-C004 = {minute['truth_status']}`."
                ),
                "- This workspace still observes Yahoo reject single `30d` `1m` requests and materialize a provider-max `8d` fallback instead.",
            ]
        )

    if tick:
        metrics = tick["metrics"]
        lines.extend(
            [
                (
                    f"- Dukascopy tick lane: `{tick['coverage']['downloaded_or_reused_count']}/{tick['coverage']['expected_count']}` series, "
                    f"`{tick['actual_data_window']}`, mean compression `{_format_metric(metrics['tick_mean_compression_ratio'], 'x')}`, "
                    f"min compression `{_format_metric(metrics['tick_min_compression_ratio'], 'x')}`, "
                    f"query latency `p95 = {_format_metric(metrics['query_latency_p95_ms'], ' ms')}`, "
                    f"encode `p95 = {_format_metric(metrics['encode_p95_ms'], ' ms')}`, "
                    f"decode `p95 = {_format_metric(metrics['decode_p95_ms'], ' ms')}`, "
                    f"`FT-C004 = {tick['truth_status']}`."
                ),
                "- This lane now includes bounded Dukascopy one-hour liquid-session slices for `EURUSD`, `AAPL`, and an `ES1`-adjacent `E_SandP-500` stream, but it is still non-authority.",
            ]
        )

    missing_tick_targets = ["AAPL", "ES1"]
    exact_eurusd_path = repo_root / "proofs" / "phase06_inputs" / "ticks" / "eurusd_nbbo_20_sessions.csv.gz"
    if not exact_eurusd_path.exists():
        missing_tick_targets.append("EURUSD")

    lines.extend(
        [
            "",
            "## Still Missing For Sovereign Phase 06 Closure",
            "",
            "- Full 24-month 1-minute OHLCV for the declared 30-symbol suite under `proofs/phase06_inputs/ohlcv/`.",
            "- Rights-safe top-of-book tick exports for `" + "`, `".join(missing_tick_targets) + "` under `proofs/phase06_inputs/ticks/`.",
            "- Labeled or auditable `FT-C004` truth for authority-bearing retrieval evaluation.",
            "",
            "## Boundary",
            "",
            "- Daily and provider-max minute outputs are explicitly non-authority rehearsal artifacts.",
            "- They reduce execution risk, but they do not satisfy the declared 33-series benchmark contract.",
            "",
            "## Current Artifacts",
            "",
            f"- Boundary manifest: `{boundary_path.relative_to(repo_root)}`",
            f"- FT-C004 truth-gap report: `{truth_report_path.relative_to(repo_root)}`",
            f"- 33-series gap matrix: `{gap_matrix_path.relative_to(repo_root)}`",
            f"- Phase 06 input ledger: `{gap_readme_path.relative_to(repo_root)}`",
            f"- Tick lane status: `{tick_status_path.relative_to(repo_root)}`",
            "- Phase summaries: `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-02-SUMMARY.md` and `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-03-SUMMARY.md`",
            "",
            "## Next Actions",
            "",
            "- Acquire the exact 30-symbol `1m_24m` pack and place it under `proofs/phase06_inputs/ohlcv/`.",
            "- Acquire the remaining exact `" + "`, `".join(missing_tick_targets) + "` tick targets and place them under `proofs/phase06_inputs/ticks/`.",
            "- Attach labels or analyst-audited truth references that allow `FT-C004` to leave `NEEDS_LABELS` honestly.",
            "- Rerun `freeze_real_market_corpus.py` and `run_real_market_refresh.py` on the exact Phase 06 pack without changing the benchmark contract.",
            "",
            f"Generated: `{utc_now_iso()}`",
        ]
    )
    path = repo_root / "MISSING_DATA_README.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    symbols = [item.strip().upper() for item in args.symbols.split(",") if item.strip()]
    results: list[dict[str, Any]] = []
    tick_status_path = repo_root / "data" / "ticks" / "tick_fetch_status.json"

    for lane in lane_specs(args):
        if lane.interval == "tick":
            manifest, tick_status_path = fetch_tick_lane_data(repo_root=repo_root, lane=lane, skip_download=args.skip_download)
            config_path, config = build_tick_corpus_config(repo_root, lane, manifest)
        else:
            manifest = fetch_lane_data(repo_root=repo_root, lane=lane, symbols=symbols, skip_download=args.skip_download)
            config_path, config = build_corpus_config(repo_root, lane, manifest)
        if not config["series"]:
            results.append(
                {
                    "lane_id": lane.lane_id,
                    "status": "no_series",
                    "artifact_dir": str(config_path.parent),
                    "non_authority_reason": lane.non_authority_reason,
                }
            )
            continue
        results.append(
            benchmark_lane(
                repo_root=repo_root,
                lane=lane,
                config_path=config_path,
                latency_repetitions=args.latency_repetitions,
            )
        )

    combined_results = merge_lane_results(load_existing_latest(repo_root), results)
    truth_report_path, truth_report = run_truth_surface_check(repo_root, args.truth_catalog)
    lane_statuses = write_lane_contract_statuses(repo_root, combined_results)
    boundary_path = write_boundary_manifest(repo_root, lane_statuses, truth_report_path, truth_report)
    gap_matrix_path, gap_readme_path = write_phase06_gap_artifacts(repo_root)
    readme_path = write_missing_data_readme(
        repo_root,
        lane_statuses,
        tick_status_path,
        boundary_path,
        gap_matrix_path,
        gap_readme_path,
        truth_report_path,
    )

    summary = {
        "generated_at_utc": utc_now_iso(),
        "repo_root": str(repo_root),
        "lanes": combined_results,
        "boundary_path": str(boundary_path),
        "truth_report_path": str(truth_report_path),
        "phase06_gap_matrix": str(gap_matrix_path),
        "phase06_gap_readme": str(gap_readme_path),
        "tick_status_path": str(tick_status_path),
        "missing_data_readme": str(readme_path),
    }
    summary_path = repo_root / "proofs" / "artifacts" / "real_market_benchmarks" / "LATEST.json"
    write_json(summary_path, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
