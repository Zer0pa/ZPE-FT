<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Consolidated Proof Report

| Claim | Evidence | Current reading |
|---|---|---|
| Package / build / install truth | [`20260321T202948Z_build.log`](artifacts/operations/20260321T202948Z_build.log), [`20260321T202948Z_clean_install_verify.log`](artifacts/operations/20260321T202948Z_clean_install_verify.log), [`20260321T202948Z_pytest_alignment.log`](artifacts/operations/20260321T202948Z_pytest_alignment.log) | Supported as shipped repo-local package/build/install evidence |
| FT-C001 OHLCV compression | [`ft_ohlcv_benchmark.json`](artifacts/2026-02-21_ft_wave1_final/ft_ohlcv_benchmark.json) | Supported as local Wave-1 evidence only; bounded delayed-feed smoke also passed at `13.19x` |
| FT-C002 tick compression | [`ft_tick_benchmark.json`](artifacts/2026-02-21_ft_wave1_final/ft_tick_benchmark.json) | Supported as local Wave-1 evidence only; bounded delayed-feed smoke also passed at `8.40x` |
| FT-C003 reconstruction fidelity | [`ft_reconstruction_fidelity.json`](artifacts/2026-02-21_ft_wave1_final/ft_reconstruction_fidelity.json) | Supported as local Wave-1 evidence only |
| FT-C004 pattern search | [`ft_pattern_search_eval.json`](artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json) | Supported as local Wave-1 evidence only; the March 19 delayed-feed smoke remains `NEEDS_LABELS` and is not authority-bearing |
| FT-C005 query latency | [`ft_query_latency_benchmark.json`](artifacts/2026-02-21_ft_wave1_final/ft_query_latency_benchmark.json) | Supported locally on the carried bundle; Timescale path remains `INCONCLUSIVE` |
| FT-C006 DB roundtrip | [`ft_db_roundtrip_results.json`](artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json) | SQLite supported; DuckDB fallback historical rerun exists; Timescale equivalence unresolved |
| Gorilla / comparator breadth | [`gorilla_eval_results.json`](artifacts/2026-02-21_ft_wave1_final/gorilla_eval_results.json) | Direct time-series comparator evidence exists in the carried bundle; broader function-calling / remote endpoint comparator closure is not promoted here |

## Governing Caveats

- `proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json`
  remains a controlled Wave-1 bundle artifact. It is not the sovereign gate.
- `proofs/reruns/2026-03-19_alpaca_demo_smoke/` is internal delayed-feed
  qualification only.
- `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`
  is the current open-access enterprise benchmark truth.
- historical path-bearing files remain bounded by
  [`HISTORICAL_PATH_LIMITS.md`](HISTORICAL_PATH_LIMITS.md).
