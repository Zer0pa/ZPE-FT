# Benchmarks

## Methodology

Benchmarks in this repo must be run on real public datasets or on retained
proof artifacts already committed to the repo. No README or benchmark table
entry should appear here unless it can be traced to:

1. A committed script or example command.
2. A committed dataset source path or public dataset URL.
3. A retained artifact or console log produced by that run.

All ratio figures use the repo's declared raw baselines:

- OHLCV: `raw_bytes_ohlcv(count)` from [python/zpe_finance/codec.py](python/zpe_finance/codec.py)
- Tick: `raw_bytes_tick(count)` from [python/zpe_finance/codec.py](python/zpe_finance/codec.py)

Phase 3 uses [`scripts/run_public_market_benchmarks.py`](scripts/run_public_market_benchmarks.py)
and carries the condensed run-of-record snapshot at
[`proofs/PHASE3_PUBLIC_BENCHMARKS.json`](proofs/PHASE3_PUBLIC_BENCHMARKS.json).

Comparator baselines are DuckDB-written Parquet ZSTD files over the same
normalized series. Query latency compares ZPE exact pattern search against the
same tokenized pattern expressed as a Parquet scan query. Tick decode latency
is reported separately for replay-heavy surfaces.

The Binance public archive exposes `aggTrades`, not top-of-book quotes. This
benchmark maps trade prints into the repo tick schema with `bid=ask=price` and
`bid_size=ask_size=quantity`. That public phase-3 surface is useful for
compression and replay stress, but it does not supersede the sovereign Phase 06
authority gate.

## Executed Inputs

- Yahoo Finance `SPY` daily OHLCV via `yfinance`, covering `2016-04-08` through
  `2026-04-07`.
- Binance Public Data `BTCUSDT` spot `aggTrades` monthly archive for
  `2017-09-01` through `2017-09-30`.
- Kaggle dataset `borismarjanovic/price-volume-data-for-all-us-stocks-etfs`,
  file `Data/ETFs/spy.us.txt`, covering `2005-02-25` through `2017-11-10`.

Trace artifacts:

- [`PHASE3_PUBLIC_BENCHMARKS.json`](proofs/PHASE3_PUBLIC_BENCHMARKS.json)
- [`PHASE3_PUBLIC_BENCHMARKS.md`](proofs/PHASE3_PUBLIC_BENCHMARKS.md)

## Universal Summary

| dataset | baseline | ZPE | ratio | improvement |
|---|---|---|---|---|
| `yahoo_spy_10y_daily` | `54556` bytes, p95 `43.904` ms | `20296` bytes, p95 `0.698` ms | `5.9432x` | size `2.6880x`, latency `62.8967x` |
| `binance_btcusdt_aggtrades_2017_09` | `3082046` bytes, p95 `55.642` ms | `1095061` bytes, p95 `63.401` ms | `10.8969x` | size `2.8145x`, latency `0.8776x` |
| `kaggle_spy_daily` | `69737` bytes, p95 `13.707` ms | `21020` bytes, p95 `1.037` ms | `7.3096x` | size `3.3176x`, latency `13.2149x` |

## Detailed Results

| source | instrument | period | granularity | raw_size | baseline_size | zpe_size | zpe_ratio | size_improvement | parquet_query_p95_ms | zpe_query_p95_ms | decode_p95_ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Yahoo Finance (`yfinance`) | `SPY` | `2016-04-08..2026-04-07` | `1d` | `120624` | `54556` | `20296` | `5.9432x` | `2.6880x` | `43.904` | `0.698` | `n/a` |
| Binance Public Data | `BTCUSDT` | `2017-09-01..2017-09-30` | `aggTrade` | `11932800` | `3082046` | `1095061` | `10.8969x` | `2.8145x` | `55.642` | `63.401` | `667.378` |
| Kaggle financial dataset | `SPY` | `2005-02-25..2017-11-10` | `1d` | `153648` | `69737` | `21020` | `7.3096x` | `3.3176x` | `13.707` | `1.037` | `n/a` |

## Notes

- Yahoo and Kaggle daily surfaces are materially smaller than Parquet ZSTD and
  materially faster on the exact-pattern query used in the run-of-record
  artifacts.
- Binance `2017-09` `aggTrades` is `2.8145x` smaller than Parquet ZSTD with
  exact replay preserved after timestamp disambiguation, but the exact-query
  path came in slower than the DuckDB Parquet scan (`0.8776x` latency
  improvement, meaning a latency regression on that dataset).
- These public benchmarks enrich the repo truth surface. They do not close or
  replace the still-open Phase 06 authority contract.
