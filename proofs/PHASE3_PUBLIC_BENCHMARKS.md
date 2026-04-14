# Phase 3 Public Benchmarks

- Generated: `2026-04-08T03:01:52.345052+00:00`
- Command:
  `run_public_market_benchmarks.py --artifact-root proofs/artifacts/public_benchmarks --binance-url https://data.binance.vision/data/spot/monthly/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2017-09.zip --binance-period 2017-09 --query-repetitions 3`
- Source script:
  [`scripts/run_public_market_benchmarks.py`](../scripts/run_public_market_benchmarks.py)

## Summary

| dataset | baseline | ZPE | ratio | improvement |
|---|---|---|---|---|
| `yahoo_spy_10y_daily` | `54556` bytes, p95 `43.904` ms | `20296` bytes, p95 `0.698` ms | `5.9432x` | size `2.6880x`, latency `62.8967x` |
| `binance_btcusdt_aggtrades_2017_09` | `3082046` bytes, p95 `55.642` ms | `1095061` bytes, p95 `63.401` ms | `10.8969x` | size `2.8145x`, latency `0.8776x` |
| `kaggle_spy_daily` | `69737` bytes, p95 `13.707` ms | `21020` bytes, p95 `1.037` ms | `7.3096x` | size `3.3176x`, latency `13.2149x` |

## Notes

- Yahoo and Kaggle daily surfaces are materially smaller than Parquet ZSTD and
  materially faster on the exact-pattern query used in the run-of-record.
- Binance `2017-09` `aggTrades` is smaller than Parquet ZSTD with exact replay
  preserved after timestamp disambiguation, but the exact-query path is still
  slower than the DuckDB Parquet scan on this public trade-tape mapping.
- These public benchmarks enrich the repo truth surface. They do not close or
  replace the still-open Phase 06 authority contract.
