#!/usr/bin/env python3
"""Fetch bounded Dukascopy tick proxy slices for Phase 06 rehearsal."""

from __future__ import annotations

import argparse
import csv
import gzip
import json
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DUKASCOPY_URL = "https://freeserv.dukascopy.com/2.0/index.php"
WINDOW_START = time(hour=14, minute=30)
WINDOW_LENGTH = timedelta(hours=1)
MAX_LIMIT = 30_000
LOOKBACK_DAYS = 80


@dataclass(frozen=True)
class TickProxySpec:
    series_id: str
    symbol: str
    dukascopy_instrument: str
    output_name: str
    tick_size: float
    contract_target: str
    exact_gap_reason: str


TICK_PROXY_SPECS = (
    TickProxySpec(
        series_id="eurusd_dukascopy_tick_20d_1h",
        symbol="EURUSD",
        dukascopy_instrument="EUR/USD",
        output_name="eurusd_dukascopy_tick_20d_1h.csv.gz",
        tick_size=0.00001,
        contract_target="eurusd_nbbo_20_sessions",
        exact_gap_reason=(
            "Bounded 20x1h liquid-session slices are useful, but the sovereign contract still expects the exact "
            "20-session authority pack under proofs/phase06_inputs/ticks/."
        ),
    ),
    TickProxySpec(
        series_id="aapl_dukascopy_tick_20d_1h",
        symbol="AAPL",
        dukascopy_instrument="AAPL.US/USD",
        output_name="aapl_dukascopy_tick_20d_1h.csv.gz",
        tick_size=0.001,
        contract_target="aapl_nbbo_20_sessions",
        exact_gap_reason=(
            "Dukascopy exposes a single-venue stock CFD top-of-book feed, not AAPL NBBO, and this fetch is bounded "
            "to 20x1h liquid-session slices."
        ),
    ),
    TickProxySpec(
        series_id="e_sandp_500_dukascopy_tick_20d_1h",
        symbol="E_SandP-500",
        dukascopy_instrument="E_SandP-500",
        output_name="e-sandp-500_dukascopy_tick_20d_1h.csv.gz",
        tick_size=0.001,
        contract_target="es1_nbbo_20_sessions",
        exact_gap_reason=(
            "Dukascopy exposes an E_SandP-500 CFD/index stream, not ES1 futures top-of-book, and this fetch is "
            "bounded to 20x1h liquid-session slices."
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch bounded Dukascopy tick proxy slices.")
    parser.add_argument("--repo-root", default=".", help="Path to the zpe-finance repo root")
    parser.add_argument(
        "--session-count",
        type=int,
        default=20,
        help="Number of weekday liquid-session slices to materialize per instrument",
    )
    parser.add_argument(
        "--end-date",
        default="",
        help="Optional UTC end date in YYYY-MM-DD format; defaults to yesterday UTC",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Reuse existing CSV.gz files instead of hitting Dukascopy",
    )
    parser.add_argument(
        "--series",
        default="",
        help="Optional comma-separated list of series_id or symbol selectors",
    )
    return parser.parse_args()


def utc_now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _repo_root(raw_path: str) -> Path:
    return Path(raw_path).expanduser().resolve()


def _default_end_date() -> date:
    return (datetime.now(tz=timezone.utc) - timedelta(days=1)).date()


def _resolve_end_date(raw: str) -> date:
    if not raw:
        return _default_end_date()
    return datetime.strptime(raw, "%Y-%m-%d").date()


def _session_candidates(end_date: date, count: int) -> list[date]:
    candidates: list[date] = []
    cursor = end_date
    for _ in range(LOOKBACK_DAYS):
        if cursor.weekday() < 5:
            candidates.append(cursor)
            if len(candidates) >= count:
                break
        cursor -= timedelta(days=1)
    return list(reversed(candidates))


def _jsonp_payload(text: str) -> Any:
    start = text.find("(")
    end = text.rfind(")")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("unexpected Dukascopy JSONP payload")
    return json.loads(text[start + 1 : end])


def _fetch_window(spec: TickProxySpec, start: datetime, end: datetime) -> list[dict[str, str | float]]:
    callback_name = "__codex_dukascopy_callback"
    params = {
        "path": "chart/json3",
        "splits": "true",
        "stocks": "true",
        "time_direction": "N",
        "jsonp": callback_name,
        "last_update": str(int(start.timestamp() * 1000)),
        "offer_side": "B",
        "instrument": spec.dukascopy_instrument,
        "interval": "TICK",
        "limit": str(MAX_LIMIT),
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://freeserv.dukascopy.com/2.0/?path=chart/index",
    }
    request = Request(f"{DUKASCOPY_URL}?{urlencode(params)}", headers=headers)
    with urlopen(request, timeout=15) as response:
        payload = _jsonp_payload(response.read().decode("utf-8"))

    end_ms = int(end.timestamp() * 1000)
    rows: list[dict[str, str | float]] = []
    for record in payload:
        if not isinstance(record, list) or len(record) < 5:
            continue
        timestamp_ms = int(record[0])
        if timestamp_ms >= end_ms:
            continue
        rows.append(
            {
                "timestamp": datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                ),
                "bid": float(record[1]),
                "ask": float(record[2]),
                "bid_size": float(record[3]) / 1_000_000.0,
                "ask_size": float(record[4]) / 1_000_000.0,
            }
        )
    return rows


def _count_rows(path: Path) -> int:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def _write_csv(path: Path, rows: list[dict[str, str | float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["timestamp", "bid", "ask", "bid_size", "ask_size"])
        writer.writeheader()
        writer.writerows(rows)


def _materialize_series(
    *,
    repo_root: Path,
    spec: TickProxySpec,
    session_count: int,
    end_date: date,
    skip_download: bool,
) -> dict[str, Any]:
    output_path = repo_root / "data" / "ticks" / spec.output_name
    session_dates = _session_candidates(end_date, session_count)

    if skip_download and output_path.exists():
        return {
            "series_id": spec.series_id,
            "symbol": spec.symbol,
            "dukascopy_instrument": spec.dukascopy_instrument,
            "path": str(output_path.relative_to(repo_root)),
            "status": "reused",
            "row_count": _count_rows(output_path),
            "tick_size": spec.tick_size,
            "window_utc": "14:30-15:30",
            "requested_session_count": session_count,
            "materialized_sessions": len(session_dates),
            "session_dates": [item.isoformat() for item in session_dates],
            "contract_target": spec.contract_target,
            "exact_contract_match": False,
            "exact_gap_reason": spec.exact_gap_reason,
            "source": "Dukascopy freeserv chart/json3",
        }

    rows: list[dict[str, str | float]] = []
    materialized_dates: list[str] = []
    failures: list[dict[str, str]] = []
    for session_date in session_dates:
        start = datetime.combine(session_date, WINDOW_START, tzinfo=timezone.utc)
        end = start + WINDOW_LENGTH
        try:
            window_rows = _fetch_window(spec, start, end)
        except Exception as exc:
            failures.append({"session_date": session_date.isoformat(), "error": str(exc)})
            continue
        if not window_rows:
            continue
        rows.extend(window_rows)
        materialized_dates.append(session_date.isoformat())

    if rows:
        _write_csv(output_path, rows)

    return {
        "series_id": spec.series_id,
        "symbol": spec.symbol,
        "dukascopy_instrument": spec.dukascopy_instrument,
        "path": str(output_path.relative_to(repo_root)),
        "status": "downloaded" if rows else "empty",
        "row_count": len(rows),
        "tick_size": spec.tick_size,
        "window_utc": "14:30-15:30",
        "requested_session_count": session_count,
        "materialized_sessions": len(materialized_dates),
        "session_dates": materialized_dates,
        "contract_target": spec.contract_target,
        "exact_contract_match": False,
        "exact_gap_reason": spec.exact_gap_reason,
        "source": "Dukascopy freeserv chart/json3",
        "failures": failures,
    }


def _write_readme(repo_root: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Phase 06 Tick Proxy Lane",
        "",
        "This directory carries bounded Dukascopy top-of-book proxy slices for the public rehearsal lane.",
        "",
        "## What Is Here",
        "",
        "- `eurusd_dukascopy_tick_20d_1h.csv.gz`: 20 weekday overlap-window slices for `EUR/USD`.",
        "- `aapl_dukascopy_tick_20d_1h.csv.gz`: 20 weekday overlap-window slices for `AAPL.US/USD`.",
        "- `e-sandp-500_dukascopy_tick_20d_1h.csv.gz`: 20 weekday overlap-window slices for `E_SandP-500`.",
        "",
        "## Boundary",
        "",
        "- These files are non-authority proxy inputs for A3/A4 only.",
        "- They do not replace the sovereign contract requirement for the exact authority pack under `proofs/phase06_inputs/ticks/`.",
        "- `AAPL.US/USD` is not NBBO and `E_SandP-500` is not `ES1` futures top-of-book.",
        "",
        "## Current Status",
        "",
    ]
    for entry in payload.get("entries", []):
        lines.append(
            f"- `{entry['series_id']}`: status `{entry['status']}`, rows `{entry['row_count']}`, "
            f"sessions `{entry['materialized_sessions']}/{entry['requested_session_count']}`."
        )
    lines.extend(
        [
            "",
            f"Generated: `{payload['generated_at_utc']}`",
        ]
    )
    (repo_root / "data" / "ticks" / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    repo_root = _repo_root(args.repo_root)
    end_date = _resolve_end_date(args.end_date)
    selectors = {
        item.strip().lower()
        for item in args.series.split(",")
        if item.strip()
    }
    specs = [
        spec
        for spec in TICK_PROXY_SPECS
        if not selectors or spec.series_id.lower() in selectors or spec.symbol.lower() in selectors
    ]

    entries = [
        _materialize_series(
            repo_root=repo_root,
            spec=spec,
            session_count=max(1, int(args.session_count)),
            end_date=end_date,
            skip_download=args.skip_download,
        )
        for spec in specs
    ]

    payload = {
        "status": "partial_proxy_fetched" if any(entry["row_count"] for entry in entries) else "not_fetched",
        "generated_at_utc": utc_now_iso(),
        "source": "Dukascopy freeserv chart/json3",
        "window_utc": "14:30-15:30",
        "requested_session_count": max(1, int(args.session_count)),
        "contract_boundary": (
            "These files are bounded Dukascopy proxies for public rehearsal only. They cannot be promoted into the "
            "exact Phase 06 authority pack."
        ),
        "entries": entries,
    }

    status_path = repo_root / "data" / "ticks" / "tick_fetch_status.json"
    write_json(status_path, payload)
    _write_readme(repo_root, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
