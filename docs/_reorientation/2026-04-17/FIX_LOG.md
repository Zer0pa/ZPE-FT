# Reorientation Fix Log — 2026-04-17

## Drift

- [`README.md`](../../../README.md) — replaced missing quick-audit targets with real retained docs by adding [`docs/AUDITOR_PLAYBOOK.md`](../../AUDITOR_PLAYBOOK.md) and [`docs/PUBLIC_AUDIT_LIMITS.md`](../../PUBLIC_AUDIT_LIMITS.md), and corrected the `docs/` row in `Repo Shape`.
- [`CHANGELOG.md`](../../../CHANGELOG.md) — removed references to missing registry/support/governance/release files and rewrote the unreleased surface around files that actually exist on current HEAD.
- [`docs/LEGAL_BOUNDARIES.md`](../../LEGAL_BOUNDARIES.md) — aligned the repo license callout to SAL v6.2.
- [`docs/market_surface.json`](../../market_surface.json) — replaced stale `PRIVATE_STAGE` with the real current blocker status `BLOCKED_MISSING_INPUTS`.
- [`proofs/artifacts/2026-02-21_ft_wave1_final/claim_status_delta.md`](../../../proofs/artifacts/2026-02-21_ft_wave1_final/claim_status_delta.md) — replaced references to removed evidence files with retained proof files that still exist in the carried bundle.

## Clarity

- [`README.md`](../../../README.md) — rewrote the commercial-readiness narrative from defensive release language into a direct useful-now-plus-blocker statement.
- [`docs/AUDITOR_PLAYBOOK.md`](../../AUDITOR_PLAYBOOK.md) — added a single truthful read order for external review instead of leaving the audit path implicit.
- [`proofs/phase06_inputs/README.md`](../../../proofs/phase06_inputs/README.md) — reframed the directory as the exact-input contract for closing the enterprise gate.

## Consistency

- [`README.md`](../../../README.md), [`docs/PUBLIC_AUDIT_LIMITS.md`](../../PUBLIC_AUDIT_LIMITS.md), and [`docs/market_surface.json`](../../market_surface.json) — aligned all public status wording on `BLOCKED_MISSING_INPUTS`.
- [`README.md`](../../../README.md) and [`docs/LEGAL_BOUNDARIES.md`](../../LEGAL_BOUNDARIES.md) — aligned the outward license wording on SAL v6.2.

## Framing

- [`README.md`](../../../README.md) and [`docs/AUDITOR_PLAYBOOK.md`](../../AUDITOR_PLAYBOOK.md) — kept FT framed as a single market-data codec/search product, not as a portfolio-level platform claim.
- [`proofs/reruns/README.md`](../../../proofs/reruns/README.md) and [`docs/LEGAL_BOUNDARIES.md`](../../LEGAL_BOUNDARIES.md) — made explicit that copied contract refs remain lineage context and may preserve superseded wording.

## Beta posture

- [`README.md`](../../../README.md) — changed `Release posture` to `Useful now, improving continuously`.
- [`CHANGELOG.md`](../../../CHANGELOG.md) — renamed `Not A Release` to `Current Commercial Boundary`.
- [`docs/PUBLIC_AUDIT_LIMITS.md`](../../PUBLIC_AUDIT_LIMITS.md) — stated the public posture directly: useful now, bounded authority surface, blocker still real.

## Primitive scope

- [`docs/_reorientation/2026-04-17/NOVELTY_CARD.md`](NOVELTY_CARD.md) — recorded that FT is not a Compass-8 lane and cited the actual codec surfaces in [`python/zpe_finance/codec.py`](../../../python/zpe_finance/codec.py) and [`python/zpe_finance/packet.py`](../../../python/zpe_finance/packet.py).

## Honest limits

- [`README.md`](../../../README.md) and [`docs/PUBLIC_AUDIT_LIMITS.md`](../../PUBLIC_AUDIT_LIMITS.md) — kept the enterprise gate blocked on missing Phase 06 inputs and auditable FT-C004 truth.
- [`proofs/reruns/README.md`](../../../proofs/reruns/README.md) — kept retained contract refs outside front-door authority.

## Audit coverage

- Reviewed without doc changes: [`docs/ARCHITECTURE.md`](../../ARCHITECTURE.md), [`docs/INTEGRATION_PATTERN.md`](../../INTEGRATION_PATTERN.md), [`docs/specs/ZPFIN_SPEC.md`](../../specs/ZPFIN_SPEC.md), [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/06-CONTEXT.md`](../../../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/06-CONTEXT.md), [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/HIGHEST_VALUE_ARTIFACT_DECISION.md`](../../../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/HIGHEST_VALUE_ARTIFACT_DECISION.md), [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/PRD_ZPE_FT.md`](../../../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/PRD_ZPE_FT.md), [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/REAL_MARKET_ATTACK_PLAN.md`](../../../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/retained_contract_refs/REAL_MARKET_ATTACK_PLAN.md), and the example JSON/request surfaces under [`docs/examples/`](../../examples/).
