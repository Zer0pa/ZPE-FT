# Consolidated Proof Report

| Claim | Evidence | Current reading |
| --- | --- | --- |
| FT-C001 OHLCV compression | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_ohlcv_benchmark.json` | Supported by local Wave-1 evidence |
| FT-C002 tick compression | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_tick_benchmark.json` | Supported by local Wave-1 evidence |
| FT-C003 reconstruction fidelity | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_reconstruction_fidelity.json` | Supported by local Wave-1 evidence |
| FT-C004 pattern search | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json` | Supported by local Wave-1 evidence |
| FT-C005 query latency | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_query_latency_benchmark.json` | Supported locally; TSBS/Timescale path still bounded by rerun caveat |
| FT-C006 DB roundtrip | `proofs/artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json` | SQLite roundtrip supported; Timescale equivalence unresolved |

## Governing Caveats

- `proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json` says `GO`, but it must be read together with the rerun files.
- `proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json` and `proofs/reruns/2026-02-21_runpod_readiness_manifest.json` keep the Timescale limit explicit.
- Historical path-bearing files are bounded by [HISTORICAL_PATH_LIMITS.md](HISTORICAL_PATH_LIMITS.md).

