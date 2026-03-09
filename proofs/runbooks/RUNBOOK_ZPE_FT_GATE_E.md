# RUNBOOK_ZPE_FT_GATE_E

## Goal
DB roundtrip, packaging, claim delta closure, and handoff contract completion.

## Command Ledger
1. `python3 scripts/run_gate_e_db_roundtrip.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
2. `pytest -q > artifacts/2026-02-20_zpe_ft_wave1/regression_results.txt`
3. `python3 scripts/build_handoff_artifacts.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`

## Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/ft_db_roundtrip_results.json`
- `artifacts/2026-02-20_zpe_ft_wave1/regression_results.txt`
- `artifacts/2026-02-20_zpe_ft_wave1/handoff_manifest.json`
- `artifacts/2026-02-20_zpe_ft_wave1/before_after_metrics.json`
- `artifacts/2026-02-20_zpe_ft_wave1/claim_status_delta.md`
- `artifacts/2026-02-20_zpe_ft_wave1/quality_gate_scorecard.json`
- `artifacts/2026-02-20_zpe_ft_wave1/innovation_delta_report.md`
- `artifacts/2026-02-20_zpe_ft_wave1/integration_readiness_contract.json`
- `artifacts/2026-02-20_zpe_ft_wave1/residual_risk_register.md`
- `artifacts/2026-02-20_zpe_ft_wave1/concept_open_questions_resolution.md`
- `artifacts/2026-02-20_zpe_ft_wave1/concept_resource_traceability.json`

## Fail Signatures
- DB roundtrip hash mismatch.
- Missing mandatory artifacts.
- Claim promoted without evidence path.

## Rollback
- Patch DB adapter/artifact builder only.
- Re-run Gate E.

## Falsification Predeclare
- Inject payload corruption/reorder before FT-C006 promotion.

## 2026-02-21 Extension: M/E Gate Contract (Additive)

### Extended Command Ledger
4. `python3 scripts/run_gate_m1_gorilla.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
5. `python3 scripts/run_gate_m2_tsbs_db.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
6. `python3 scripts/run_gate_m3_zipline.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
7. `python3 scripts/run_gate_m4_compliance.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
8. `python3 scripts/run_appendix_e_ingestion.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`

### Extended Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/max_resource_lock.json`
- `artifacts/2026-02-20_zpe_ft_wave1/max_resource_validation_log.md`
- `artifacts/2026-02-20_zpe_ft_wave1/max_claim_resource_map.json`
- `artifacts/2026-02-20_zpe_ft_wave1/impracticality_decisions.json`
- `artifacts/2026-02-20_zpe_ft_wave1/external_comparator_table.csv`
- `artifacts/2026-02-20_zpe_ft_wave1/gorilla_eval_results.json`
- `artifacts/2026-02-20_zpe_ft_wave1/net_new_gap_closure_matrix.json`
- `artifacts/2026-02-20_zpe_ft_wave1/runpod_readiness_manifest.json` (if any `IMP-COMPUTE`)

### Extended Fail Signatures
- Any Appendix D/E gate missing command evidence.
- Any E3 resource attempt missing command + outcome log line.
- Any `IMP-*` entry without fallback and claim impact.

### Extended Rollback
- Patch only maximalization/ingestion scripts.
- Re-run failed M/E gate and downstream M/E gates.

## 2026-02-21 Final-Phase Closure Addendum

### Closure Root
- `artifacts/2026-02-21_zpe_ft_wave1_final/`

### Additional Command Ledger
9. `python3 scripts/run_gate_m2_tsbs_db.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220`
10. `python3 scripts/run_gate_m3_zipline.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220`
11. `python3 scripts/run_gate_m4_compliance.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220`
12. `python3 scripts/run_appendix_e_ingestion.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220 --phase full`
13. `python3 scripts/build_handoff_artifacts.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220`

### Additional Expected Outputs
- `artifacts/2026-02-21_zpe_ft_wave1_final/tsbs_db_benchmark_results.json`
- `artifacts/2026-02-21_zpe_ft_wave1_final/net_new_gap_closure_matrix.json`
- `artifacts/2026-02-21_zpe_ft_wave1_final/quality_gate_scorecard.json`
- `artifacts/2026-02-21_zpe_ft_wave1_final/claim_status_delta.md`

### Additional Fail Signatures
- TSBS generation command accepted but no throughput/latency written.
- `FT-C005` remains `INCONCLUSIVE` without new `IMP-*` evidence.
- Any hardcoded old artifact-root path inside generated handoff contracts.

### Additional Rollback
1. Fix failing M2/E-ingest/handoff script only.
2. Re-run step 9 through 13.
3. Revalidate `E-G3`, `F-G1`, and `F-G2` prior to final adjudication.
