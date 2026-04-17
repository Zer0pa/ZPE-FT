<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/release-notes.svg" alt="RELEASE NOTES" width="100%">
</p>

# Changelog

## Unreleased

### Added

- quick audit path in [`docs/AUDITOR_PLAYBOOK.md`](docs/AUDITOR_PLAYBOOK.md)
- explicit public-boundary summary in [`docs/PUBLIC_AUDIT_LIMITS.md`](docs/PUBLIC_AUDIT_LIMITS.md)
- architecture index in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- legal boundary note in [`docs/LEGAL_BOUNDARIES.md`](docs/LEGAL_BOUNDARIES.md)
- Phase 06 input ledger in [`proofs/phase06_inputs/README.md`](proofs/phase06_inputs/README.md)
- rerun boundary note in [`proofs/reruns/README.md`](proofs/reruns/README.md)
- public benchmark runner in [`scripts/run_public_market_benchmarks.py`](scripts/run_public_market_benchmarks.py)
- executed public benchmark helpers in [`python/zpe_finance/public_benchmarks.py`](python/zpe_finance/public_benchmarks.py)

### Changed

- rewrote the front-door README around one authority block, one status snapshot,
  and explicit controlled-vs-market truth boundaries
- aligned the audit, public-boundary, architecture, legal, and proof-ledger
  docs to the current FT repo truth
- updated proof-summary docs to reflect the March 19 delayed-feed smoke and the
  March 21 blocked enterprise benchmark packet
- moved the docs surface onto repo-local IMC-style masthead and section-bar
  assets
- retained the executed Yahoo Finance, Binance Public Data, and Kaggle
  benchmark narratives under
  [`proofs/artifacts/public_benchmarks/`](proofs/artifacts/public_benchmarks/)

### Current Commercial Boundary

- repo install, replay, and carried Wave-1 evidence are useful now
- the open-access enterprise benchmark remains blocked on missing Phase 06
  inputs and authority labels

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
