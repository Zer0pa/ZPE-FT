<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Final Status

As of 2026-03-21, this private staged repo contains:
- an FT package surface with shipped build and install evidence
- a controlled Wave-1 final bundle with promoted local codec evidence
- a bounded delayed-feed March smoke rerun
- an honest missing-inputs blocker for the open-access enterprise benchmark

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

## Current Position

| Coordinate | State |
|---|---|
| Package/install truth | `SUPPORTED` via [`20260321T202948Z_build.log`](artifacts/operations/20260321T202948Z_build.log) and [`20260321T202948Z_clean_install_verify.log`](artifacts/operations/20260321T202948Z_clean_install_verify.log) |
| Controlled codec authority | `SUPPORTED` |
| Delayed-feed acquisition smoke | `BOUNDED` |
| Open-access enterprise benchmark | `BLOCKED_MISSING_INPUTS` |
| Blind-clone verification | not run in this phase |
| Public release posture | `NOT_PUBLIC_READY` |

## Strongest Current Readings

- FT-C001 through FT-C006 remain supported as local Wave-1 evidence only
- build/install/import truth is evidenced in
  [`artifacts/operations/20260321T202948Z_build.log`](artifacts/operations/20260321T202948Z_build.log),
  [`artifacts/operations/20260321T202948Z_clean_install_verify.log`](artifacts/operations/20260321T202948Z_clean_install_verify.log),
  and [`artifacts/operations/20260321T202948Z_pytest_alignment.log`](artifacts/operations/20260321T202948Z_pytest_alignment.log)
- SQLite roundtrip is supported
- Timescale equivalence remains `INCONCLUSIVE`
- the March 19 delayed-feed smoke is real but non-closing

## Open Limit

The open limit is no longer only Timescale. The governing open limit is the
Phase 06 buyer-authority gate:
- `33` named corpus exports are still missing
- the auditable query catalog / truth labels are still missing for authority use
- the current closing packet is
  [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json)
