# RUNBOOK_ZPE_FT_GATE_D

## Goal
Malformed/adversarial campaigns and deterministic replay checks.

## Command Ledger
1. `python3 scripts/run_gate_d_falsification.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`
2. `python3 scripts/run_determinism_replay.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220 --runs 5`
3. `pytest -q tests/test_adversarial.py`

## Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/falsification_results.md`
- `artifacts/2026-02-20_zpe_ft_wave1/determinism_replay_results.json`

## Fail Signatures
- Uncaught crash rate > 0%.
- Replay hash divergence.
- Silent fallback without explicit logging.

## Rollback
- Patch fault handling and deterministic serialization.
- Re-run Gate D and all downstream gates.

## Falsification Predeclare
- DT-FT-1..DT-FT-5 campaigns must run before claim upgrades.
