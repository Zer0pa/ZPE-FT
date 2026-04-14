#!/usr/bin/env python3
"""Run executed public-market benchmarks for Phase 3."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from common import append_command_log, ensure_artifact_root, write_json
from zpe_finance.corpus import SeriesSpec, load_series_from_spec
from zpe_finance.data import try_fetch_equivalent_market_bars
from zpe_finance.public_benchmarks import (
    aggtrades_to_tick_series,
    run_ohlcv_benchmark,
    run_tick_benchmark,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _artifact_paths(artifact_root: Path) -> tuple[Path, Path]:
    return (
        artifact_root / "phase3_public_benchmarks.json",
        artifact_root / "phase3_public_benchmarks.md",
    )


def _series_date_range(series: dict[str, np.ndarray]) -> dict[str, str]:
    ts = np.asarray(series["timestamp"], dtype=np.int64)
    start = datetime.fromtimestamp(int(ts[0]) / 1000.0, tz=timezone.utc).date().isoformat()
    end = datetime.fromtimestamp(int(ts[-1]) / 1000.0, tz=timezone.utc).date().isoformat()
    return {"date_start": start, "date_end": end}


def _flatten_series(series: dict[str, Any]) -> dict[str, np.ndarray]:
    normalized: dict[str, np.ndarray] = {}
    for key, values in series.items():
        arr = np.asarray(values)
        if arr.ndim > 1:
            arr = arr.reshape(-1)
        normalized[key] = arr
    return normalized


def _load_yahoo_series(local_csv: str, symbol: str, tick_size: float, years: int) -> dict[str, np.ndarray]:
    if local_csv:
        spec = SeriesSpec(
            series_id=f"{symbol.lower()}_{years}y_daily",
            kind="ohlcv",
            source_path=Path(local_csv).expanduser().resolve(),
            symbol=symbol,
            tick_size=tick_size,
            provenance="phase-3 local yahoo export",
            license_note="user-fetched public market sample",
            timestamp_format="iso8601",
            columns={
                "timestamp": "timestamp",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
            },
        )
        return _flatten_series(load_series_from_spec(spec))

    fetched = try_fetch_equivalent_market_bars(symbol=symbol, years=years)
    if fetched.status != "OK" or fetched.bars is None:
        raise RuntimeError(fetched.note)
    return _flatten_series(fetched.bars)


def _download_binance_zip(url: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination
    urllib.request.urlretrieve(url, destination)
    return destination


def _load_binance_aggtrades(local_zip: str, url: str, temp_dir: Path) -> pd.DataFrame:
    if local_zip:
        zip_path = Path(local_zip).expanduser().resolve()
    else:
        filename = url.rstrip("/").rsplit("/", 1)[-1]
        zip_path = _download_binance_zip(url, temp_dir / filename)

    with zipfile.ZipFile(zip_path) as archive:
        names = archive.namelist()
        if not names:
            raise ValueError(f"zip archive has no entries: {zip_path}")
        with archive.open(names[0], "r") as handle:
            frame = pd.read_csv(
                handle,
                header=None,
                usecols=[1, 2, 5],
                names=["price", "quantity", "timestamp"],
                dtype={
                    "price": "float64",
                    "quantity": "float64",
                    "timestamp": "int64",
                },
            )
    if frame.empty:
        raise ValueError(f"aggTrades archive contained no rows: {zip_path}")
    if int(frame["timestamp"].max()) >= 10**15:
        frame["timestamp"] = (frame["timestamp"] // 1000).astype(np.int64)
    return frame


def _load_kaggle_series(local_csv: str, slug: str, relative_path: str) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    if local_csv:
        csv_path = Path(local_csv).expanduser().resolve()
    else:
        try:
            import kagglehub  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency path
            raise RuntimeError(
                "kagglehub is required for the Kaggle benchmark. Install it with `python -m pip install kagglehub`."
            ) from exc
        dataset_root = Path(kagglehub.dataset_download(slug))
        csv_path = dataset_root / relative_path

    frame = pd.read_csv(csv_path)
    if frame.empty:
        raise ValueError(f"Kaggle dataset contains no rows: {csv_path}")

    dates = pd.to_datetime(frame["Date"], utc=True)
    series = {
        "timestamp": (dates.astype("int64") // 1_000_000).to_numpy(dtype=np.int64),
        "open": frame["Open"].to_numpy(dtype=np.float64),
        "high": frame["High"].to_numpy(dtype=np.float64),
        "low": frame["Low"].to_numpy(dtype=np.float64),
        "close": frame["Close"].to_numpy(dtype=np.float64),
        "volume": frame["Volume"].to_numpy(dtype=np.float64),
    }
    metadata = {
        "csv_path": str(csv_path),
        "csv_bytes": int(csv_path.stat().st_size),
    }
    return _flatten_series(series), metadata


def _benchmark_entry_with_source(
    entry: dict[str, Any],
    *,
    source_artifact: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if source_artifact:
        entry["source_artifact"] = source_artifact
    entry.update(_series_date_range(entry.pop("_series_for_dates")))
    return entry


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Phase 3 Public Market Benchmarks",
        "",
        f"- Generated: `{report['generated_at_utc']}`",
        f"- Command: `{report['command']}`",
        "",
        "## Summary",
        "",
        "| dataset | baseline | ZPE | ratio | improvement |",
        "|---|---|---|---|---|",
    ]

    for entry in report["benchmarks"]:
        if entry["status"] != "ok":
            continue
        baseline = entry["baseline"]
        zpe = entry["zpe"]
        improvement = entry["improvement"]
        lines.append(
            "| "
            f"{entry['dataset_id']} | "
            f"{baseline['name']} `{baseline['compressed_bytes']}` bytes, p95 `{baseline['p95_ms']:.3f}` ms | "
            f"`{zpe['compressed_bytes']}` bytes, p95 `{zpe['query']['p95_ms']:.3f}` ms | "
            f"`{zpe['compression_ratio']:.4f}x` | "
            f"size `{improvement['size_vs_baseline_x']:.4f}x`, latency `{improvement['latency_vs_baseline_x']:.4f}x` |"
        )

    lines.extend(
        [
            "",
            "## Detailed",
            "",
            "| source | instrument | period | granularity | raw_size | parquet_zstd | zpe | zpe/raw | zpe_vs_parquet | query_latency | decode_latency |",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )

    for entry in report["benchmarks"]:
        if entry["status"] != "ok":
            continue
        baseline = entry["baseline"]
        zpe = entry["zpe"]
        decode_latency = entry["roundtrip"].get("decode_p95_ms")
        decode_text = "n/a" if decode_latency is None else f"`{float(decode_latency):.3f}` ms"
        lines.append(
            "| "
            f"{entry['source']} | "
            f"{entry['instrument']} | "
            f"{entry['period']} | "
            f"{entry['granularity']} | "
            f"`{entry['raw_bytes']}` | "
            f"`{baseline['compressed_bytes']}` | "
            f"`{zpe['compressed_bytes']}` | "
            f"`{zpe['compression_ratio']:.4f}x` | "
            f"`{entry['improvement']['size_vs_baseline_x']:.4f}x` | "
            f"zpe p95 `{zpe['query']['p95_ms']:.3f}` ms; parquet p95 `{baseline['p95_ms']:.3f}` ms | "
            f"{decode_text} |"
        )

    blocked = [entry for entry in report["benchmarks"] if entry["status"] != "ok"]
    if blocked:
        lines.extend(["", "## Blocked Inputs", ""])
        for entry in blocked:
            lines.append(f"- `{entry['dataset_id']}`: {entry['reason']}")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-root",
        default=str(_repo_root() / "proofs" / "artifacts" / "public_benchmarks"),
    )
    parser.add_argument("--temp-dir", default="")
    parser.add_argument("--yahoo-symbol", default="SPY")
    parser.add_argument("--yahoo-years", type=int, default=10)
    parser.add_argument("--yahoo-tick-size", type=float, default=0.01)
    parser.add_argument("--yahoo-local-csv", default="")
    parser.add_argument(
        "--binance-url",
        default="https://data.binance.vision/data/spot/monthly/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2019-01.zip",
    )
    parser.add_argument("--binance-local-zip", default="")
    parser.add_argument("--binance-symbol", default="BTCUSDT")
    parser.add_argument("--binance-period", default="2019-01")
    parser.add_argument("--binance-tick-size", type=float, default=0.01)
    parser.add_argument(
        "--kaggle-slug",
        default="borismarjanovic/price-volume-data-for-all-us-stocks-etfs",
    )
    parser.add_argument("--kaggle-relative-path", default="Data/ETFs/spy.us.txt")
    parser.add_argument("--kaggle-symbol", default="SPY")
    parser.add_argument("--kaggle-local-csv", default="")
    parser.add_argument("--kaggle-tick-size", type=float, default=0.01)
    parser.add_argument("--query-repetitions", type=int, default=3)
    parser.add_argument("--pattern-length", type=int, default=6)
    parser.add_argument("--keep-temp", action="store_true")
    parser.add_argument("--skip-kaggle", action="store_true")
    args = parser.parse_args()

    artifact_root = ensure_artifact_root(args.artifact_root)
    temp_dir = Path(args.temp_dir).expanduser().resolve() if args.temp_dir else artifact_root / "_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    report_path, markdown_path = _artifact_paths(artifact_root)
    append_command_log(
        artifact_root,
        "PHASE3",
        " ".join(
            [
                "python3",
                str(Path(__file__).resolve()),
                f"--artifact-root {artifact_root}",
            ]
        ),
        note="start public benchmarks",
    )

    benchmarks: list[dict[str, Any]] = []

    yahoo_series = _load_yahoo_series(
        args.yahoo_local_csv,
        args.yahoo_symbol,
        args.yahoo_tick_size,
        args.yahoo_years,
    )
    yahoo_entry = run_ohlcv_benchmark(
        dataset_id=f"yahoo_{args.yahoo_symbol.lower()}_{args.yahoo_years}y_daily",
        source="Yahoo Finance (yfinance)",
        source_url="https://pypi.org/project/yfinance/",
        instrument=args.yahoo_symbol,
        period=f"{args.yahoo_years}y",
        granularity="1d",
        series=yahoo_series,
        tick_size=args.yahoo_tick_size,
        workdir=temp_dir,
        repetitions=args.query_repetitions,
        pattern_length=args.pattern_length,
        notes="SPY is used as the public S&P 500 ETF proxy for this benchmark.",
    )
    yahoo_entry["_series_for_dates"] = yahoo_series
    benchmarks.append(
        _benchmark_entry_with_source(
            yahoo_entry,
            source_artifact={
                "fetch_mode": "local_csv" if args.yahoo_local_csv else "yfinance",
            },
        )
    )

    binance_frame = _load_binance_aggtrades(args.binance_local_zip, args.binance_url, temp_dir)
    binance_series = aggtrades_to_tick_series(
        binance_frame["timestamp"].to_numpy(dtype=np.int64),
        binance_frame["price"].to_numpy(dtype=np.float64),
        binance_frame["quantity"].to_numpy(dtype=np.float64),
    )
    binance_entry = run_tick_benchmark(
        dataset_id=f"binance_{args.binance_symbol.lower()}_aggtrades_{args.binance_period.replace('-', '_')}",
        source="Binance Public Data",
        source_url=args.binance_url,
        instrument=args.binance_symbol,
        period=args.binance_period,
        granularity="aggTrade",
        series=binance_series,
        tick_size=args.binance_tick_size,
        workdir=temp_dir,
        repetitions=args.query_repetitions,
        pattern_length=args.pattern_length,
        notes="Trade tape mapped into the repo tick schema with bid=ask=trade price and bid_size=ask_size=quantity because Binance public monthly aggTrades do not expose top-of-book quotes.",
    )
    binance_entry["_series_for_dates"] = binance_series
    if binance_frame["timestamp"].size > 0:
        min_ts = int(binance_frame["timestamp"].min())
        max_ts = int(binance_frame["timestamp"].max())
    else:
        min_ts = max_ts = 0
    benchmarks.append(
        _benchmark_entry_with_source(
            binance_entry,
            source_artifact={
                "kind": "zip" if not args.binance_local_zip else "local_zip",
                "rows": int(len(binance_frame.index)),
                "timestamp_start_ms": min_ts,
                "timestamp_end_ms": max_ts,
            },
        )
    )

    if not args.skip_kaggle:
        kaggle_series, kaggle_meta = _load_kaggle_series(
            args.kaggle_local_csv,
            args.kaggle_slug,
            args.kaggle_relative_path,
        )
        kaggle_entry = run_ohlcv_benchmark(
            dataset_id=f"kaggle_{args.kaggle_symbol.lower()}_daily",
            source="Kaggle financial dataset",
            source_url=f"https://www.kaggle.com/datasets/{args.kaggle_slug}",
            instrument=args.kaggle_symbol,
            period="full_history",
            granularity="1d",
            series=kaggle_series,
            tick_size=args.kaggle_tick_size,
            workdir=temp_dir,
            repetitions=args.query_repetitions,
            pattern_length=args.pattern_length,
            notes="Daily ETF history from the public Kaggle dataset `price-volume-data-for-all-us-stocks-etfs`.",
        )
        kaggle_entry["_series_for_dates"] = kaggle_series
        benchmarks.append(
            _benchmark_entry_with_source(
                kaggle_entry,
                source_artifact={
                    "slug": args.kaggle_slug,
                    **kaggle_meta,
                },
            )
        )

    report = {
        "generated_at_utc": _utc_now(),
        "command": " ".join(os.path.basename(part) if idx == 0 else part for idx, part in enumerate(os.sys.argv)),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "benchmarks": benchmarks,
    }

    write_json(report_path, report)
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    if not args.keep_temp and temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)

    append_command_log(
        artifact_root,
        "PHASE3",
        "write phase3_public_benchmarks.json + phase3_public_benchmarks.md",
        note="complete",
    )
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
