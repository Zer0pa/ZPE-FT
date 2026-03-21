<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Governance

This document defines the FT repo governance boundary for evidence handling,
status language, and release-truth discipline.

Canonical repo and license coordinates live in [`README.md`](README.md) and
[`LICENSE`](LICENSE).

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

Governance baseline:
- technical claims must be artifact-backed
- runtime, test, and proof artifacts outrank prose when they conflict
- bounded results stay bounded
- historical lineage is retained rather than rewritten into a false pass
- blocked gates are reported plainly

<p>
  <img src=".github/assets/readme/section-bars/compatibility-commitments.svg" alt="COMPATIBILITY COMMITMENTS" width="100%">
</p>

| Coordinate | Current lock | What it means |
|---|---|---|
| Controlled codec authority | `2026-02-21_ft_wave1_final` | promoted local codec claims remain tied to the carried Wave-1 controlled corpus |
| Bounded market smoke | `2026-03-19_alpaca_demo_smoke` | acquisition and refresh path is real but market authority is still bounded |
| Current benchmark blocker | `2026-03-21_phase06_contract_freeze_attempt_v3` | open-access enterprise benchmark is currently blocked |
| DB posture | SQLite supported, Timescale `INCONCLUSIVE` | DB roundtrip truth is narrower than full DB equivalence |
| Release posture | `NOT_PUBLIC_READY` | no public release or PyPI promotion is supported by current evidence |

<p>
  <img src=".github/assets/readme/section-bars/mode-semantics.svg" alt="MODE SEMANTICS" width="100%">
</p>

| Token | Meaning |
|---|---|
| `SUPPORTED` | Evidence in the shipped repo supports the claim within the stated boundary. |
| `BOUNDED` | A real surface exists, but the claim is intentionally narrow. |
| `INCONCLUSIVE` | The evidence is unresolved or conflicts remain. |
| `BLOCKED` | A named input, label, or owner dependency prevents gate closure. |
| `HISTORICAL` | The artifact is kept for lineage only and is not a live instruction surface. |
| `NOT_PUBLIC_READY` | The repo may be real and useful, but the release gate is not closed. |

<p>
  <img src=".github/assets/readme/section-bars/escalation-path.svg" alt="ESCALATION PATH" width="100%">
</p>

Owner-ratified closure is still required for:
- open-access enterprise benchmark completion
- any public release or PyPI publication decision
- any claim that converts the March smoke into public market authority
