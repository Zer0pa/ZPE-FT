#!/usr/bin/env python3
"""Fetch delayed stock bars and quotes from Alpaca into the real-market corpus contract."""

from __future__ import annotations

from pathlib import Path

from common import append_command_log, ensure_artifact_root, parse_args, start_comet_logger, write_json
from zpe_finance.alpaca import (
    AlpacaClient,
    AlpacaSeriesRequest,
    build_generated_corpus_spec,
    load_alpaca_corpus_request,
    write_alpaca_bar_csv,
    write_alpaca_quote_csv,
)


def _output_path(dataset_dir: Path, request: AlpacaSeriesRequest) -> Path:
    suffix = "bars" if request.kind == "ohlcv" else "quotes"
    return dataset_dir / f"{request.series_id}_{suffix}.csv"


def main() -> int:
    parser = parse_args("Fetch delayed Alpaca market-data corpus")
    parser.add_argument("--config", required=True, help="Path to the Alpaca request JSON spec")
    parser.add_argument(
        "--spec-output",
        default="",
        help="Optional path for the generated freeze-compatible corpus spec",
    )
    parser.add_argument(
        "--base-url",
        default="https://data.alpaca.markets",
        help="Official Alpaca market-data base URL",
    )
    args = parser.parse_args()

    artifact_root = ensure_artifact_root(args.artifact_root)
    comet = start_comet_logger(
        artifact_root,
        "fetch_alpaca_corpus",
        args=args,
        tags=("phase-05", "alpaca", "corpus-fetch"),
    )
    config_path = Path(args.config).expanduser().resolve()
    spec_output = (
        Path(args.spec_output).expanduser().resolve()
        if args.spec_output
        else artifact_root / "alpaca_real_market_corpus_spec.generated.json"
    )

    append_command_log(
        artifact_root,
        "EV-00A",
        f"python3 scripts/fetch_alpaca_corpus.py --config {config_path}",
        note="start",
    )
    try:
        config, requests, dataset_dir = load_alpaca_corpus_request(config_path)
        dataset_dir.mkdir(parents=True, exist_ok=True)
        client = AlpacaClient.from_env(base_url=args.base_url)

        csv_paths: dict[str, Path] = {}
        fetch_series: list[dict[str, object]] = []
        total_rows = 0
        for request in requests:
            csv_path = _output_path(dataset_dir, request)
            if request.kind == "ohlcv":
                items = client.get_stock_bars(
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    start=request.start,
                    end=request.end,
                    feed=request.feed,
                    adjustment=request.adjustment,
                    limit=request.limit,
                )
                row_count = write_alpaca_bar_csv(csv_path, items)
            else:
                items = client.get_stock_quotes(
                    symbol=request.symbol,
                    start=request.start,
                    end=request.end,
                    feed=request.feed,
                    limit=request.limit,
                )
                row_count = write_alpaca_quote_csv(csv_path, items)

            total_rows += int(row_count)
            csv_paths[request.series_id] = csv_path
            fetch_series.append(
                {
                    "series_id": request.series_id,
                    "kind": request.kind,
                    "symbol": request.symbol,
                    "rows": row_count,
                    "start": request.start,
                    "end": request.end,
                    "feed": request.feed,
                    "timeframe": request.timeframe if request.kind == "ohlcv" else None,
                    "output_path": str(csv_path),
                }
            )

        generated_spec = build_generated_corpus_spec(config, requests, csv_paths)
        fetch_manifest_path = artifact_root / "alpaca_fetch_manifest.json"
        write_json(spec_output, generated_spec)
        write_json(
            fetch_manifest_path,
            {
                "source": "alpaca_market_data_api",
                "config_path": str(config_path),
                "generated_spec_path": str(spec_output),
                "series": fetch_series,
            },
        )

        append_command_log(
            artifact_root,
            "EV-00A",
            "write Alpaca delayed-stock corpus CSVs and generated corpus spec",
            note=f"series={len(fetch_series)}",
        )
        comet.finalize(
            status="completed",
            metrics={
                "series_count": len(fetch_series),
                "total_rows": total_rows,
            },
            others={
                "gate": "EV-00A",
                "config_path": str(config_path),
                "spec_output": str(spec_output),
            },
            assets=(
                fetch_manifest_path,
                spec_output,
                artifact_root / "command_log.txt",
            ),
        )
        return 0
    except Exception as exc:
        comet.finalize(
            status="failed",
            others={
                "gate": "EV-00A",
                "error": str(exc),
                "config_path": str(config_path),
            },
            assets=(artifact_root / "command_log.txt",),
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
