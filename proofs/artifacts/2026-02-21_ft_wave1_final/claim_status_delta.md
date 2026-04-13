# Claim Status Delta

| Claim ID | Pre | Post | Evidence |
|---|---|---|---|
| FT-C001 | UNTESTED | PASS | `./proofs/artifacts/2026-02-21_ft_wave1_final/ft_ohlcv_benchmark.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/tsbs_db_benchmark_results.json` |
| FT-C002 | UNTESTED | PASS | `./proofs/artifacts/2026-02-21_ft_wave1_final/ft_tick_benchmark.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/zipline_roundtrip_results.json` |
| FT-C003 | UNTESTED | PASS | `./proofs/artifacts/2026-02-21_ft_wave1_final/ft_reconstruction_fidelity.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/gorilla_eval_results.json` |
| FT-C004 | UNTESTED | PASS | `./proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/zipline_roundtrip_results.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/tsbs_db_benchmark_results.json` |
| FT-C005 | UNTESTED | PASS | `./proofs/artifacts/2026-02-21_ft_wave1_final/ft_query_latency_benchmark.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/tsbs_db_benchmark_results.json` |
| FT-C006 | UNTESTED | PASS | `./proofs/artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json`<br>`./proofs/artifacts/2026-02-21_ft_wave1_final/gorilla_eval_results.json` |

## Substitution and Impracticality Notes
- Appendix-E attempt-all outcomes and IMP-coded decisions are in `impracticality_decisions.json`.
- TSBS/Timescale/Zipline/TRADES closure state is in `net_new_gap_closure_matrix.json`.
