# Phase 06 Input Ledger

This directory is the exact-input ledger for the sovereign Phase 06 benchmark. It is intentionally useful even when the exact authority files are still absent.

## What This Directory Means

- `series_gap_matrix.csv` is the machine-readable 33-series blocker map.
- `ohlcv/` is reserved for the exact 30-symbol `1m_24m` authority pack.
- `ticks/` is reserved for the exact `AAPL`, `ES1`, and `EURUSD` top-of-book authority pack.

## Boundary

- Daily `2y` proxies, provider-max `1m_8d` proxies, and bounded Dukascopy tick slices live under `data/ohlcv/`, `data/ticks/`, and `proofs/artifacts/real_market_benchmarks/`; they are useful, but they are not this directory.
- Populating this directory with exact files is necessary but not sufficient. `FT-C004` still requires labeled or auditable truth.

## Required References

- `../artifacts/real_market_benchmarks/BOUNDARY.json`
- `../artifacts/real_market_benchmarks/ft_c004_truth_requirements.json`
- `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-01-benchmark-spec.md`
- `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-01-query-and-truth-spec.md`
- `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-ftc004-truth-gap.md`

## Current Status

As of this snapshot, this directory is a blocker ledger, not an authority-data payload.
