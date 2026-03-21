<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Releasing

This document defines the release gate and decision boundary for the current
ZPE-FT repo.

Canonical repo and license coordinates live in [`README.md`](README.md) and
[`LICENSE`](LICENSE).

<p>
  <img src=".github/assets/readme/section-bars/release-notes.svg" alt="RELEASING" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

Release statements in this repo are bounded to evidence-backed package and proof
claims. No public release should be inferred from package reality alone.

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

| Gate | Required state | Current state |
|---|---|---|
| Package / install truth | clean install, import, and build path are truthful | supported via [`20260321T202948Z_build.log`](proofs/artifacts/operations/20260321T202948Z_build.log) and [`20260321T202948Z_clean_install_verify.log`](proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log) |
| Controlled codec authority | `2026-02-21` Wave-1 final bundle remains coherent and promoted claims stay bounded to it | supported |
| Delayed-feed acquisition truth | repo-native acquisition and refresh path works on the bounded March smoke | bounded |
| Open-access enterprise benchmark | Phase 06 corpus exports, auditable labels, and freeze/replay close cleanly | blocked |
| DB equivalence breadth | Timescale-backed path closes or is explicitly excluded from a release claim | inconclusive |
| Docs/render coherence | front door, support docs, and proof docs agree on repo URL, license, authority artifacts, and release posture | required for any release surface |
| Owner publish decision | owner ratifies any public release or PyPI move | required |

<p>
  <img src=".github/assets/readme/section-bars/compatibility-vector-impact.svg" alt="RELEASE IMPACT" width="100%">
</p>

Current release truth:
- the repo has shipped build, install, and pytest evidence for the current package path
- the current docs route to the same authority bundle, bounded smoke surface,
  and benchmark-blocker packet
- the repo is not yet public-release-ready because the open-access enterprise
  benchmark is still blocked and the broader DB equivalence story is unresolved

Until those gates close, release execution remains manual and evidence-gated.

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
