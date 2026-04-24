<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Architecture

This document is the canonical architecture index for the current FT repo. It
defines where package truth, helper truth, script truth, and proof truth live.

Canonical repo and license coordinates live in [`../README.md`](../README.md)
and [`../LICENSE`](../LICENSE).

<p>
  <img src="../.github/assets/readme/section-bars/architecture-and-theory.svg" alt="ARCHITECTURE AND THEORY" width="100%">
</p>

<p>
  <img src="../.github/assets/readme/section-bars/interface-contracts.svg" alt="INTERFACE CONTRACTS" width="100%">
</p>

| Surface | Role | Canonical path |
|---|---|---|
| Python package | Installable codec/search surface | [`../python/zpe_finance/`](../python/zpe_finance/) |
| Optional native helper | Repo-local helper for nibble packing, hashing, and search primitives | [`../core/`](../core/) |
| Packet contract | FT packet-format reference | [`specs/ZPFIN_SPEC.md`](specs/ZPFIN_SPEC.md) |
| Example request configs | Repo-local example manifests for acquisition, corpus freeze, and query catalog work | [`examples/`](examples/) |
| Base install metadata | Build, dependency, and extra declarations | [`../pyproject.toml`](../pyproject.toml) |
| Gate runner | Controlled Wave-1 replay entrypoint that writes a fresh local rerun output | [`../scripts/run_wave1.py`](../scripts/run_wave1.py) |
| Real-market acquisition | Delayed-feed acquisition helper | [`../scripts/fetch_alpaca_corpus.py`](../scripts/fetch_alpaca_corpus.py) |
| Real-market freeze | Manifest and provenance freeze | [`../scripts/freeze_real_market_corpus.py`](../scripts/freeze_real_market_corpus.py) |
| Real-market refresh | Compression/fidelity/latency refresh on a frozen manifest | [`../scripts/run_real_market_refresh.py`](../scripts/run_real_market_refresh.py) |

<p>
  <img src="../.github/assets/readme/section-bars/proof-corpus.svg" alt="PROOF CORPUS" width="100%">
</p>

| Proof class | Current artifact | Meaning |
|---|---|---|
| Public benchmark summary | [`../proofs/PHASE3_PUBLIC_BENCHMARKS.json`](../proofs/PHASE3_PUBLIC_BENCHMARKS.json) | retained Yahoo/Binance/Kaggle compression and latency snapshot |
| Bounded public proxy bundles | [`../proofs/artifacts/real_market_benchmarks/`](../proofs/artifacts/real_market_benchmarks/) | useful rehearsal bundles with explicit promotion-forbidden boundary |
| Bounded operator/local smoke | [`../proofs/reruns/2026-03-19_alpaca_demo_smoke/`](../proofs/reruns/2026-03-19_alpaca_demo_smoke/) | delayed-feed acquisition/freeze/refresh reality on a two-series sample |
| Current enterprise blocker | [`../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json) | open-access benchmark is not closed |
| Phase 06 input ledger | [`../proofs/phase06_inputs/`](../proofs/phase06_inputs/) | 33-series gap ledger for the absent exact authority pack |

<p>
  <img src="../.github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

| Runtime surface | Truthful entrypoint | Boundary |
|---|---|---|
| Base package sanity | `python -m pip install -e .` then import `zpe_finance` | package import, local codec use, and docs audit |
| Heavier repo-local proof work | `python -m pip install -e ".[test,proof]"` | proof and rerun work inside this repo |
| Optional helper path | `python -m pip install -e ".[native]"` then `cd core && maturin develop --release` | only when you intentionally exercise the repo-local helper |
| Local wave-1 helper | `python scripts/run_wave1.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --native-helper auto` | writes a local rerun destination only; no carried public authority bundle is retained in this repo |
| Repo-local env gate | `python poc/scripts/00_env_check.py --workspace . --repo .` | operator/local proof setup, not the front-door package path |

The repo retains bounded public-benchmark and blocker surfaces under
[`../proofs/`](../proofs/). The exact `30 + 3` authority pack remains absent
from [`../proofs/phase06_inputs/`](../proofs/phase06_inputs/).

Current retained operations evidence:
- [`../proofs/artifacts/operations/20260321T160048Z_pytest.log`](../proofs/artifacts/operations/20260321T160048Z_pytest.log)
- [`../proofs/artifacts/operations/20260321T160048Z_free_source_feasibility_probe.json`](../proofs/artifacts/operations/20260321T160048Z_free_source_feasibility_probe.json)
- [`../proofs/artifacts/operations/20260321T231416Z_docs_link_check.log`](../proofs/artifacts/operations/20260321T231416Z_docs_link_check.log)

Older path-bearing reruns and logs were intentionally removed from the retained
repo surface during the current cleanup. The unresolved Timescale path remains
excluded from promoted claims until a fresh repo-relative rerun replaces it.

<p>
  <img src="../.github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

- the retained public and bounded-proxy artifacts remain non-authority for Phase 06
- the delayed-feed market smoke remains bounded and non-closing
- Timescale equivalence remains unresolved
- the open-access enterprise benchmark remains blocked until the missing Phase
  06 exports and auditable labels exist

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
