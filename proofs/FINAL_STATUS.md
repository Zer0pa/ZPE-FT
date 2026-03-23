<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Final Status

As of 2026-03-21, the current source-available repo surface contains:

- an FT package surface with shipped build and install evidence
- a controlled Wave-1 final bundle with promoted local codec evidence
- a bounded delayed-feed March smoke rerun
- an explicit missing-inputs blocker for the open-access enterprise benchmark

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

## Current Position

| Gate | Status | Evidence |
|---|---|---|
| Package/install truth | `SUPPORTED` | [`20260321T202948Z_build.log`](artifacts/operations/20260321T202948Z_build.log), [`20260321T202948Z_clean_install_verify.log`](artifacts/operations/20260321T202948Z_clean_install_verify.log), and [`20260321T202948Z_pytest_alignment.log`](artifacts/operations/20260321T202948Z_pytest_alignment.log) |
| Controlled codec authority | `SUPPORTED` | [`CONSOLIDATED_PROOF_REPORT.md`](CONSOLIDATED_PROOF_REPORT.md) and [`artifacts/2026-02-21_ft_wave1_final/`](artifacts/2026-02-21_ft_wave1_final/) |
| Delayed-feed acquisition smoke | `BOUNDED` | [`reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json`](reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json) |
| Open-access enterprise benchmark | `BLOCKED_MISSING_INPUTS` | [`reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json) |
| Blind-clone verification | `NOT_RUN` | no retained artifact in the current phase |
| Public release posture | `NOT_PUBLIC_READY` | [`../RELEASING.md`](../RELEASING.md) plus the current blocker packet |

## Strongest Current Readings

- FT-C001 through FT-C006 remain supported as local Wave-1 evidence only
- build/install/import truth is evidenced in
  [`artifacts/operations/20260321T202948Z_build.log`](artifacts/operations/20260321T202948Z_build.log),
  [`artifacts/operations/20260321T202948Z_clean_install_verify.log`](artifacts/operations/20260321T202948Z_clean_install_verify.log),
  and [`artifacts/operations/20260321T202948Z_pytest_alignment.log`](artifacts/operations/20260321T202948Z_pytest_alignment.log)
- SQLite roundtrip is supported
- Timescale equivalence remains `INCONCLUSIVE`
- the March 19 delayed-feed smoke is real but non-closing
- older path-bearing copied gate runbooks and February leftovers were
  intentionally removed from the retained repo surface
- some retained supporting artifacts still preserve historical machine-local
  traces and must be read as evidence, not as live instructions

## Open Limit

The governing open limit is the Phase 06 buyer-authority gate:

- `33` named corpus exports are still missing
- the auditable query catalog / truth labels are still missing for authority use
- the current closing packet is
  [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json)

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
