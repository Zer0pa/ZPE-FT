# RUNBOOK_ZPE_FT_GATE_C

## Goal
Compression benchmarks, comparator matrix, pattern quality, and latency benchmarks.

## Command Ledger
1. `python3 scripts/run_gate_c_benchmarks.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
2. `python3 scripts/run_pattern_eval.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
3. `python3 scripts/run_latency_benchmark.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`

## Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/ft_ohlcv_benchmark.json`
- `artifacts/2026-02-20_zpe_ft_wave1/ft_tick_benchmark.json`
- `artifacts/2026-02-20_zpe_ft_wave1/ft_pattern_search_eval.json`
- `artifacts/2026-02-20_zpe_ft_wave1/ft_query_latency_benchmark.json`

## Fail Signatures
- Compression ratio below thresholds.
- P@10 below 0.85.
- Query latency >= 100 ms.
- Comparator run missing without substitution log.

## Rollback
- Patch encoding/search/index logic.
- Re-run Gate C and downstream gates.

## Falsification Predeclare
- Run confusion-set patterns and noisy near-miss queries before FT-C004/FT-C005 promotion.
