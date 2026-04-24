# Phase 06 Input Ledger

This directory is the exact-input ledger for the sovereign Phase 06 benchmark. It is intentionally useful even when the exact authority files are still absent.

## What This Directory Means

- `series_gap_matrix.csv` is the machine-readable 33-series blocker map.
- `ohlcv/` is reserved for the exact 30-symbol `1m_24m` authority pack.
- `ticks/` is reserved for the exact `AAPL`, `ES1`, and `EURUSD` top-of-book authority pack.

## Boundary

- The retained daily, minute, and tick proxy bundles live under `proofs/artifacts/real_market_benchmarks/`; they are useful, but they are not this directory.
- Populating this directory with exact files is necessary but not sufficient. `FT-C004` still requires labeled or auditable truth.

## Required References

- `../artifacts/real_market_benchmarks/BOUNDARY.json`
- `../artifacts/real_market_benchmarks/ft_c004_truth_requirements.json`
- `../reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`
- `../reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/PRD_ZPE_FT.md`
- `../reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/REAL_MARKET_ATTACK_PLAN.md`
- `../reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/phase06_query_catalog.pending.json`

## Current Status

As of this snapshot, this directory is a blocker ledger, not an authority-data payload.
