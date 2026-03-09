# RUNBOOK_ZPE_FT_GATE_B

## Goal
Core encode/decode implementation and fidelity checks.

## Command Ledger
1. `maturin develop --manifest-path core/Cargo.toml`
2. `pytest -q tests/test_codec_core.py tests/test_packet_roundtrip.py`
3. `python3 scripts/run_gate_b_fidelity.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --seed 20260220`

## Expected Outputs
- `artifacts/2026-02-20_zpe_ft_wave1/ft_reconstruction_fidelity.json`
- `artifacts/2026-02-20_zpe_ft_wave1/gate_b_test_results.txt`

## Fail Signatures
- Decode mismatch on non-malformed inputs.
- RMSE > 0.5 tick.
- Crash on NaN/malformed payload.

## Rollback
- Patch codec + validators only.
- Re-run Gate B tests and fidelity script.

## Falsification Predeclare
- Feed extreme gaps and malformed bars before promoting FT-C003.
