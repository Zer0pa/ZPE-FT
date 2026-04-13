# V6 Authority Surface — Completion Report

**Repo:** ZPE-FT
**Agent:** Codex
**Date:** 2026-04-14
**Branch:** campaign/v6-authority-surface

## Dimensions Executed

- [x] **A: Key Metrics** — rewritten to the V6 authority slate with retained proof links and named Parquet ZSTD baselines
- [x] **B: Competitive Benchmarks** — added from retained public-benchmark evidence; Binance regression kept visible
- [x] **C: pip Install Fix** — root install path already worked structurally; root `pyproject.toml` metadata aligned to `zpe-ft` and `LicenseRef-Zer0pa-SAL-6.2`
- [x] **D: Publish Workflow** — added `.github/workflows/publish.yml` for `zpe-ft`
- [x] **E: Proof Sync** — synced 16 proof files into the public tree plus `BENCHMARKS.md` for the competitive doc surface

## Verification

- pip install from root: PASS
- import test: PASS
- Proof anchors verified: 8/8 exist
- Competitive claims honest: YES — the README calls out the Binance `0.8776×` query regression instead of hiding it

## Key Metrics Written

| Metric | Value | Baseline | Proof File |
|--------|-------|----------|------------|
| OHLCV_CR | 19.1913× | vs Parquet ZSTD 5.9432× | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_ohlcv_benchmark.json` |
| TICK_CR | 20.5672× | vs Parquet ZSTD 10.8969× | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_tick_benchmark.json` |
| PATTERN_SEARCH | P@10 = 0.90 | — | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json` |
| QUERY_LATENCY | p95 = 0.0567 ms | vs Parquet ZSTD 13.2149-62.8967× faster on daily surfaces; Binance 0.8776× (regression) | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_query_latency_benchmark.json` |

## Issues / Blockers

- `origin/main` was missing the retained `2026-02-21_ft_wave1_final/` bundle plus the Phase 3 public benchmark docs needed to support the V6 README surface. Those files were synced from the local authority worktree.
- The repo `LICENSE` file and README license copy still reference SAL v6.0. V6 scope allowed `pyproject.toml` metadata changes but did not authorize a license-text migration, so `pyproject.toml` now reflects `LicenseRef-Zer0pa-SAL-6.2` while the checked-in legal text remains on v6.0.
