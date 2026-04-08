# Phase 3 Public Market Benchmarks

- Generated: `2026-04-08T02:56:13.501389+00:00`
- Command: `run_public_market_benchmarks.py --artifact-root /tmp/zpe-ft-phase3-artifacts --yahoo-local-csv /tmp/zpe-ft-phase3/spy_10y.csv --skip-kaggle`

## Summary

| dataset | baseline | ZPE | ratio | improvement |
|---|---|---|---|---|
| yahoo_spy_10y_daily | parquet_zstd_duckdb `54556` bytes, p95 `12.345` ms | `20296` bytes, p95 `0.253` ms | `5.9432x` | size `2.6880x`, latency `48.7347x` |
| binance_btcusdt_aggtrades_2019_01 | parquet_zstd_duckdb `94811473` bytes, p95 `454.749` ms | `29723317` bytes, p95 `519.473` ms | `12.0904x` | size `3.1898x`, latency `0.8754x` |

## Detailed

| source | instrument | period | granularity | raw_size | parquet_zstd | zpe | zpe/raw | zpe_vs_parquet | query_latency | decode_latency |
|---|---|---|---|---|---|---|---|---|---|---|
| Yahoo Finance (yfinance) | SPY | 10y | 1d | `120624` | `54556` | `20296` | `5.9432x` | `2.6880x` | zpe p95 `0.253` ms; parquet p95 `12.345` ms | n/a |
| Binance Public Data | BTCUSDT | 2019-01 | aggTrade | `359368080` | `94811473` | `29723317` | `12.0904x` | `3.1898x` | zpe p95 `519.473` ms; parquet p95 `454.749` ms | `11201.783` ms |
