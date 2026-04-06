# Missing Data Status

This note records what the repo can fetch and benchmark today without pretending the sovereign Phase 06 gate is closed.

## Available Now

- Bounded public rehearsal lane: 30 US equity OHLCV symbols via yfinance.
- Bounded Dukascopy tick proxy lane: 20x1h liquid-session slices for EURUSD, AAPL, and E_SandP-500.
- Repo-native bounded runner: `scripts/run_phase06_partial.py` freezes and reruns the current public proxy slices through the real-market lane.
- Machine-readable boundary artifacts: `proofs/artifacts/real_market_benchmarks/BOUNDARY.json`, per-lane `contract_status.json`, `proofs/phase06_inputs/series_gap_matrix.csv`, and `proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json`.

## Latest Observed Proxy Results

- Daily proxy lane: `30/30` symbols, `2y @ 1d`, mean compression `5.9968x`, min compression `4.7828x`, query latency `p95 = 0.0775 ms`, encode `p95 = 4.2460 ms`, decode `p95 = 2.9994 ms`, `FT-C004 = NEEDS_LABELS`.
- Daily bars remain non-authority because the declared Phase 06 contract requires 24 months of 1-minute bars, not 2 years of daily bars.
- Provider-max minute proxy lane: `30/30` symbols, `8d @ 1m per materialized series (requested 30d)`, mean compression `14.1615x`, min compression `8.7491x`, query latency `p95 = 0.2158 ms`, encode `p95 = 15.5593 ms`, decode `p95 = 11.8777 ms`, `FT-C004 = NEEDS_LABELS`.
- This workspace still observes Yahoo reject single `30d` `1m` requests and materialize a provider-max `8d` fallback instead.
- Dukascopy tick lane: `3/3` series, `20x1h_slices @ tick per materialized series (requested 20_sessions)`, mean compression `11.1070x`, min compression `7.1596x`, query latency `p95 = 39.1440 ms`, encode `p95 = 1281.2870 ms`, decode `p95 = 978.3470 ms`, `FT-C004 = NEEDS_LABELS`.
- This lane now includes bounded Dukascopy one-hour liquid-session slices for `EURUSD`, `AAPL`, and an `ES1`-adjacent `E_SandP-500` stream, but it is still non-authority.

## Still Missing For Sovereign Phase 06 Closure

- Full 24-month 1-minute OHLCV for the declared 30-symbol suite under `proofs/phase06_inputs/ohlcv/`.
- Rights-safe top-of-book tick exports for `AAPL`, `ES1`, `EURUSD` under `proofs/phase06_inputs/ticks/`.
- Labeled or auditable `FT-C004` truth for authority-bearing retrieval evaluation.

## Boundary

- Daily and provider-max minute outputs are explicitly non-authority rehearsal artifacts.
- They reduce execution risk, but they do not satisfy the declared 33-series benchmark contract.

## Current Artifacts

- Boundary manifest: `proofs/artifacts/real_market_benchmarks/BOUNDARY.json`
- FT-C004 truth-gap report: `proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json`
- 33-series gap matrix: `proofs/phase06_inputs/series_gap_matrix.csv`
- Phase 06 input ledger: `proofs/phase06_inputs/README.md`
- Tick lane status: `data/ticks/tick_fetch_status.json`
- Phase summaries: `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-02-SUMMARY.md` and `../.gpd/phases/06-open-access-enterprise-wedge-benchmark/06-03-SUMMARY.md`

## Next Actions

- Acquire the exact 30-symbol `1m_24m` pack and place it under `proofs/phase06_inputs/ohlcv/`.
- Acquire the remaining exact `AAPL`, `ES1`, `EURUSD` tick targets and place them under `proofs/phase06_inputs/ticks/`.
- Attach labels or analyst-audited truth references that allow `FT-C004` to leave `NEEDS_LABELS` honestly.
- Rerun `freeze_real_market_corpus.py` and `run_real_market_refresh.py` on the exact Phase 06 pack without changing the benchmark contract.

Generated: `2026-04-06T17:24:24.897384+00:00`
