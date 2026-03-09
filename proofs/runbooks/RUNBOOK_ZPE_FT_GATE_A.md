# RUNBOOK_ZPE_FT_GATE_A

## Goal
Runbook freeze, dataset/resource lock, schema/inventory freeze.

## Command Ledger
1. `mkdir -p runbooks artifacts/2026-02-20_zpe_ft_wave1 python/zpe_finance core/src tests scripts format`
2. `python3 scripts/gate_a_freeze.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`

## Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/dataset_lock.json`
- `artifacts/2026-02-20_zpe_ft_wave1/schema_inventory_freeze.json`
- `artifacts/2026-02-20_zpe_ft_wave1/resource_probe_results.json`

## Fail Signatures
- Missing schema fields for bars/ticks.
- Dataset hashes not generated.
- External resource probe crash.

## Rollback
- Fix data/schema script only.
- Re-run Gate A fully before any coding claims.

## Falsification Predeclare
- Attempt malformed schemas and out-of-order timestamps in freeze script.

## 2026-02-21 Extension: Appendix E Predeclare (Additive)

### Additional Command Ledger
3. `python3 scripts/run_appendix_e_ingestion.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220 --phase lock_only`

### Additional Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/max_resource_lock.json`

### Additional Fail Signatures
- Missing lock entries for E3 resources (TSBS, Gorilla BFCL, Zipline, TRADES).
