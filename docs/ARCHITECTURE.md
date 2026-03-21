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
| Controlled authority | [`../proofs/artifacts/2026-02-21_ft_wave1_final/`](../proofs/artifacts/2026-02-21_ft_wave1_final/) | promoted codec claims on the carried Wave-1 corpus |
| Bounded operator/local smoke | [`../proofs/reruns/2026-03-19_alpaca_demo_smoke/`](../proofs/reruns/2026-03-19_alpaca_demo_smoke/) | delayed-feed acquisition/freeze/refresh reality on a two-series sample |
| Current enterprise blocker | [`../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json) | open-access benchmark is not closed |
| Historical operator reruns | [`../proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json`](../proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json), [`../proofs/logs/2026-02-21_operator_command_log_historical.txt`](../proofs/logs/2026-02-21_operator_command_log_historical.txt) | lineage only; not live operating instructions |

<p>
  <img src="../.github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

| Runtime surface | Truthful entrypoint |
|---|---|
| Base package sanity | `python -m pip install -e .` then import `zpe_finance` |
| Heavier repo-local proof work | `python -m pip install -e ".[test,proof]"` |
| Optional helper path | `python -m pip install -e ".[native]"` then `cd core && maturin develop --release` |
| Controlled Wave-1 replay | `python scripts/run_wave1.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --native-helper auto` |
| Repo-local env gate | `python poc/scripts/00_env_check.py --workspace . --repo .` |

The `artifacts/2026-02-20_zpe_ft_wave1` path is a local rerun destination. The
carried promoted evidence bundle remains
[`../proofs/artifacts/2026-02-21_ft_wave1_final/`](../proofs/artifacts/2026-02-21_ft_wave1_final/).

Current package/build/install evidence:
- [`../proofs/artifacts/operations/20260321T202948Z_build.log`](../proofs/artifacts/operations/20260321T202948Z_build.log)
- [`../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log`](../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log)
- [`../proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log`](../proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log)

<p>
  <img src="../.github/assets/readme/section-bars/open-risks-non-blocking.svg" alt="OPEN RISKS (NON-BLOCKING)" width="100%">
</p>

- the promoted codec claims remain controlled-corpus claims
- the delayed-feed market smoke remains bounded and non-closing
- Timescale equivalence remains unresolved
- the open-access enterprise benchmark remains blocked until the missing Phase
  06 exports and auditable labels exist
