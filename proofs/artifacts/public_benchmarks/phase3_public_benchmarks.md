# Phase 3 Public Market Benchmarks

- Generated: `2026-04-08T03:01:52.345052+00:00`
- Command: `run_public_market_benchmarks.py --artifact-root proofs/artifacts/public_benchmarks --binance-url https://data.binance.vision/data/spot/monthly/aggTrades/BTCUSDT/BTCUSDT-aggTrades-2017-09.zip --binance-period 2017-09 --query-repetitions 3`

## Summary

| dataset | baseline | ZPE | ratio | improvement |
|---|---|---|---|---|
| yahoo_spy_10y_daily | parquet_zstd_duckdb `54556` bytes, p95 `43.904` ms | `20296` bytes, p95 `0.698` ms | `5.9432x` | size `2.6880x`, latency `62.8967x` |
| binance_btcusdt_aggtrades_2017_09 | parquet_zstd_duckdb `3082046` bytes, p95 `55.642` ms | `1095061` bytes, p95 `63.401` ms | `10.8969x` | size `2.8145x`, latency `0.8776x` |
| kaggle_spy_daily | parquet_zstd_duckdb `69737` bytes, p95 `13.707` ms | `21020` bytes, p95 `1.037` ms | `7.3096x` | size `3.3176x`, latency `13.2149x` |

## Detailed

| source | instrument | period | granularity | raw_size | parquet_zstd | zpe | zpe/raw | zpe_vs_parquet | query_latency | decode_latency |
|---|---|---|---|---|---|---|---|---|---|---|
| Yahoo Finance (yfinance) | SPY | 10y | 1d | `120624` | `54556` | `20296` | `5.9432x` | `2.6880x` | zpe p95 `0.698` ms; parquet p95 `43.904` ms | n/a |
| Binance Public Data | BTCUSDT | 2017-09 | aggTrade | `11932800` | `3082046` | `1095061` | `10.8969x` | `2.8145x` | zpe p95 `63.401` ms; parquet p95 `55.642` ms | `667.378` ms |
| Kaggle financial dataset | SPY | full_history | 1d | `153648` | `69737` | `21020` | `7.3096x` | `3.3176x` | zpe p95 `1.037` ms; parquet p95 `13.707` ms | n/a |
