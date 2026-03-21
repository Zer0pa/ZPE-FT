<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Canonical Doc Registry

This registry maps the current FT documentation surfaces to their owned concern
and truth class.

<p>
  <img src="../.github/assets/readme/section-bars/where-to-go.svg" alt="WHERE TO GO" width="100%">
</p>

Front door and policy:

| Path | Owns | Use when | Truth class |
|---|---|---|---|
| [`../README.md`](../README.md) | front-door summary, authority block, repo routes | you need the shortest truthful overview | public repo truth |
| [`../CHANGELOG.md`](../CHANGELOG.md) | release-surface change history | you need doc or release-surface change history | public repo truth |
| [`../CITATION.cff`](../CITATION.cff) | citation metadata | you need citation metadata | public repo truth |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | contribution rules and evidence discipline | you are preparing a change or pull request | public repo truth |
| [`../SECURITY.md`](../SECURITY.md) | vulnerability reporting policy | you need the security disclosure route | public repo truth |
| [`../GOVERNANCE.md`](../GOVERNANCE.md) | status semantics and evidence policy | you need status or closure rules | public repo truth |
| [`../RELEASING.md`](../RELEASING.md) | release gate and publish boundary | you need release posture or publish conditions | public repo truth |
| [`../LICENSE`](../LICENSE) | legal source of truth | you need license terms | public repo truth |
| [`../AUDITOR_PLAYBOOK.md`](../AUDITOR_PLAYBOOK.md) | shortest honest audit path | you are auditing repo claims | supporting authority |
| [`../PUBLIC_AUDIT_LIMITS.md`](../PUBLIC_AUDIT_LIMITS.md) | audit boundary and limit matrix | you need the bounded reading rules | supporting authority |

Technical and routing docs:

| Path | Owns | Use when | Truth class |
|---|---|---|---|
| [`README.md`](README.md) | docs routing layer | you are starting inside `docs/` | public repo truth |
| [`FAQ.md`](FAQ.md) | reader questions | you need short answers before reading deeper docs | public repo truth |
| [`SUPPORT.md`](SUPPORT.md) | support routing | you need the correct channel or escalation path | public repo truth |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | runtime/helper/script/proof map | you need the technical layout | public repo truth |
| [`LEGAL_BOUNDARIES.md`](LEGAL_BOUNDARIES.md) | legal and data boundary notes | you need legal/data boundary context | public repo truth |
| [`INTEGRATION_PATTERN.md`](INTEGRATION_PATTERN.md) | repo-local integration notes | you need build/integration details beyond the front door | operator-local reference |
| [`specs/ZPFIN_SPEC.md`](specs/ZPFIN_SPEC.md) | packet-format contract | you need the codec packet contract | supporting authority |

Proof and rerun docs:

| Path | Owns | Use when | Truth class |
|---|---|---|---|
| [`../proofs/FINAL_STATUS.md`](../proofs/FINAL_STATUS.md) | current proof posture summary | you need the current gate posture | supporting authority |
| [`../proofs/CONSOLIDATED_PROOF_REPORT.md`](../proofs/CONSOLIDATED_PROOF_REPORT.md) | claim-by-claim evidence reading | you need the claim-by-claim boundary | supporting authority |
| [`../proofs/HISTORICAL_PATH_LIMITS.md`](../proofs/HISTORICAL_PATH_LIMITS.md) | historical-path boundary | you need to understand what was removed or retained | supporting authority |
| [`../proofs/reruns/README.md`](../proofs/reruns/README.md) | rerun-surface routing | you need the retained rerun entry points | supporting authority |

Example request configs:

| Path | Owns | Use when | Truth class |
|---|---|---|---|
| [`examples/alpaca_corpus_request.example.json`](examples/alpaca_corpus_request.example.json) | delayed-feed acquisition request shape | you are running the Alpaca smoke path | supporting reference |
| [`examples/real_market_corpus_spec.example.json`](examples/real_market_corpus_spec.example.json) | real-market corpus manifest example | you are shaping a corpus freeze request | supporting reference |
| [`examples/real_market_query_catalog.example.json`](examples/real_market_query_catalog.example.json) | query-catalog example | you are defining repo-local market queries | supporting reference |
| [`examples/phase06_benchmark_request.example.json`](examples/phase06_benchmark_request.example.json) | Phase 06 benchmark request example | you are inspecting the enterprise benchmark input contract | supporting reference |

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
