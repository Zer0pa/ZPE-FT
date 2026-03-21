<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Contributing

ZPE-FT contributions are evidence-first.

<p>
  <img src=".github/assets/readme/section-bars/purpose.svg" alt="PURPOSE" width="100%">
</p>

Contribution baseline:
- evidence first
- do not upgrade claims without evidence
- do not hide negative, mixed, or inconclusive results
- keep changes scoped and reviewable
- preserve GitHub-safe rendering and repo-relative paths in docs

<p>
  <img src=".github/assets/readme/section-bars/before-you-start.svg" alt="BEFORE YOU START" width="100%">
</p>

1. Read [`README.md`](README.md), [`docs/AUDITOR_PLAYBOOK.md`](docs/AUDITOR_PLAYBOOK.md),
   and [`docs/PUBLIC_AUDIT_LIMITS.md`](docs/PUBLIC_AUDIT_LIMITS.md).
2. If you touch claim-bearing code or proof logic, attach concrete before/after
   evidence.
3. If you touch docs, keep cross-document tokens coherent:
   - repo URL
   - contact
   - license identity
   - authority artifacts
   - release posture

<p>
  <img src=".github/assets/readme/section-bars/evidence-discipline-as-community-norm.svg" alt="EVIDENCE DISCIPLINE AS COMMUNITY NORM" width="100%">
</p>

Every pull request should state:
- changed paths
- claim impact: none, bounded, or changed
- evidence path or test output for every claim-bearing change
- doc render or link-check result if docs changed
- whether any historical artifact was added, removed, or reclassified

Minimum evidence by change type:

| Change type | What is required |
|---|---|
| Package/runtime change | test output or replay artifact |
| Proof or benchmark change | artifact path plus exact claim impact |
| Docs change | path/render check plus cross-doc coherence |
| Historical artifact cleanup | explicit note describing what was removed and what retained surface now carries truth |

<p>
  <img src=".github/assets/readme/section-bars/scope-discipline.svg" alt="SCOPE DISCIPLINE" width="100%">
</p>

- One concern per change where practical.
- Do not convert a bounded smoke result into a broader claim.
- Do not turn historical workstation artifacts into live instructions unless you
  have rerun and replaced them.
- Do not introduce non-repo asset paths in documentation.

<p>
  <img src=".github/assets/readme/section-bars/licensing-of-contributions.svg" alt="LICENSING OF CONTRIBUTIONS" width="100%">
</p>

By contributing, you agree your contribution is provided under the terms of the
Zer0pa Source-Available License v6.0 in [`LICENSE`](LICENSE).

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
