<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

<p align="center"><strong>Search financial patterns on compressed delayed-feed archives with deterministic replay and bounded price-field fidelity.</strong></p>
<p align="center"><em>Retained public-benchmark, bounded replay, and blocker artifacts are real. The open-access enterprise benchmark is still blocked on missing inputs and auditable query truth.</em></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111" alt="License: SAL v7.0"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-%3E%3D3.11-e5e7eb?labelColor=111111" alt="Python >=3.11"></a>
  <a href="proofs/artifacts/public_benchmarks/phase3_public_benchmarks.md"><img src="https://img.shields.io/badge/public%20benchmark-retained-e5e7eb?labelColor=111111" alt="Public benchmark: retained"></a>
  <a href="proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json"><img src="https://img.shields.io/badge/current%20gate-BLOCKED__MISSING__INPUTS-e5e7eb?labelColor=111111" alt="Current gate: BLOCKED_MISSING_INPUTS"></a>
</p>
<p align="center">
  <a href="docs/LEGAL_BOUNDARIES.md"><img src="https://img.shields.io/badge/legal-boundaries-e5e7eb?labelColor=111111" alt="Legal boundaries"></a>
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/architecture-runtime%20map-e5e7eb?labelColor=111111" alt="Architecture: runtime map"></a>
  <a href="docs/specs/ZPFIN_SPEC.md"><img src="https://img.shields.io/badge/packet%20spec-.zpfin-e5e7eb?labelColor=111111" alt="Packet spec: .zpfin"></a>
</p>

# ZPE-FT

| What This Is | Verified Claims | What We Don't Claim |
|---|---|---|
| [Jump](#what-this-is) | [Jump](#verified-claims) | [Jump](#what-we-dont-claim) |

| Commercial Readiness | Repo Shape | Quick Start |
|---|---|---|
| [Jump](#commercial-readiness) | [Jump](#repo-shape) | [Jump](#quick-start) |

## What This Is

ZPE-FT is a deterministic financial time-series codec and search surface for teams that need to archive delayed-feed market data, replay it exactly, and query patterns without first inflating the archive back into a warehouse table.

The honest commercial wedge is narrow and specific: compressed delayed-feed archives with deterministic replay, retained public-benchmark evidence on open datasets, and bounded replay fidelity on the in-repo smoke bundle. Public-data rehearsal lanes are useful but non-authority. The open-access enterprise benchmark is still blocked on missing inputs and auditable FT-C004 truth.

## Verified Claims

| Claim | Proof artifact on disk | CI coverage |
|---|---|---|
| Public benchmark artifacts are retained for Yahoo SPY, Binance BTCUSDT aggTrades, and Kaggle SPY. | `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json` | `tests/test_public_benchmarks.py` runs the benchmark script on local fixtures and requires three `status == "ok"` entries. |
| Repo-bundled OHLCV roundtrip stays within the bounded price-field error threshold and compresses below raw bytes. | `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json` | `tests/test_ohlcv_roundtrip.py` asserts `rmse <= 0.5` ticks and encoded payload is smaller than raw. |
| Freeze and refresh scripts execute on a declared corpus contract and emit benchmark, fidelity, latency, and roundtrip artifacts. | `proofs/reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json` | `tests/test_real_market_corpus.py` runs `freeze_real_market_corpus.py` and `run_real_market_refresh.py` on fixture corpora. |
| Missing authority inputs keep the sovereign Phase 06 gate blocked. | `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json` | `tests/test_real_market_corpus.py` asserts missing inputs return `blocked_missing_inputs`. |
| FT-C004 truth remains blocked until labels or audit refs exist. | `proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json` | `tests/test_phase06_partial_scripts.py` and `tests/test_real_market_refresh_extras.py` assert blocked-vs-ready truth-surface outcomes. |

## What We Don't Claim

- No Phase 06 closure or public release readiness.
- No broad warehouse or incumbent displacement claim.
- No lossless volume reconstruction claim.
- No promoted public-data search-quality claim while FT-C004 remains unresolved.
- No claim that the bounded proxy lanes satisfy the sovereign enterprise benchmark.

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | BLOCKED |
| Reason | Phase 06 still lacks the declared authority inputs and auditable FT-C004 truth. |
| Source | `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`; `proofs/phase06_inputs/series_gap_matrix.csv` |

## Repo Shape

| Area | Purpose |
|---|---|
| `python/`, `core/`, `scripts/` | Installable package, optional helper, and repo-local runners |
| `docs/` | Audit, architecture, support, and contract surfaces |
| `proofs/` | Retained benchmarks, reruns, blocker packets, and operations logs |
| Root files | Release metadata, legal terms, and the front door |

## Quick Start

Install from PyPI:

```bash
pip install zpe-ft
```

Verify from source:

```bash
git clone https://github.com/Zer0pa/ZPE-FT.git
cd ZPE-FT
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
python - <<'PY'
import zpe_finance
from zpe_finance.rust_bridge import rust_version
print("exports", sorted(zpe_finance.__all__))
print("rust_bridge", rust_version())
PY
```

Start with `docs/ARCHITECTURE.md`, then read `docs/LEGAL_BOUNDARIES.md` and `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`. `LICENSE` is the legal source of truth; the repo uses SAL v7.0.
