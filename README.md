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
  <a href="docs/INTEGRATION_PATTERN.md"><img src="https://img.shields.io/badge/observability-Comet%20hooks-e5e7eb?labelColor=111111" alt="Observability: Comet hooks"></a>
</p>

# ZPE-FT

| What This Is | Key Metrics | Competitive Benchmarks | What We Prove | What We Don't Claim |
|---|---|---|---|---|
| [Jump](#what-this-is) | [Jump](#key-metrics) | [Jump](#competitive-benchmarks) | [Jump](#what-we-prove) | [Jump](#what-we-dont-claim) |

| Commercial Readiness | Tests and Verification | Proof Anchors | Repo Shape | Quick Start |
|---|---|---|---|---|
| [Jump](#commercial-readiness) | [Jump](#tests-and-verification) | [Jump](#proof-anchors) | [Jump](#repo-shape) | [Jump](#quick-start) |

## What This Is

ZPE-FT is a deterministic financial time-series codec and search surface for teams that need to archive delayed-feed market data, replay it exactly, and query patterns without first inflating the archive back into a warehouse table.

The honest commercial wedge is narrow and specific: compressed delayed-feed archives with deterministic replay, retained public-benchmark evidence on open datasets, and bounded replay fidelity on the in-repo smoke bundle. The public-data rehearsal lanes are useful but non-authority. The open-access enterprise benchmark is still blocked on missing inputs and auditable FT-C004 truth.

## Key Metrics

| Metric | Value | Baseline |
|---|---|---|
| Public SPY 10y daily compression | 5.94x | Parquet+ZSTD 2.21x |
| Public BTCUSDT aggTrades compression | 10.90x | Parquet+ZSTD 3.87x |
| Public Kaggle SPY compression | 7.31x | Parquet+ZSTD 2.20x |
| Bounded replay fidelity | 0.0 max RMSE ticks | threshold 0.5 |

> Source: `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json`; `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json`

## Competitive Benchmarks

The retained repo evidence splits into two surfaces: public rehearsal benchmarks on open datasets, and a bounded replay smoke bundle for delayed-feed fidelity. Neither surface closes the open-access enterprise gate on its own.

| Lane | ZPE-FT | Comparator | Boundary |
|---|---|---|---|
| Public SPY 10y daily archive | 5.94x | Parquet+ZSTD 2.21x | Open dataset, non-authority |
| Public BTCUSDT aggTrades archive | 10.90x | Parquet+ZSTD 3.87x | Open dataset, non-authority |
| Public Kaggle SPY archive | 7.31x | Parquet+ZSTD 2.20x | Open dataset, non-authority |
| Real-market proxy lanes | Useful rehearsal only | 10x authority floor still missed on some series | `promotion_forbidden: true` in `BOUNDARY.json` |

## What We Prove

- The repo retains public benchmark artifacts and repo-operation logs under `proofs/artifacts/`.
- The retained public benchmark bundle measures compression and query behavior on open SPY and BTCUSDT datasets.
- The bounded replay smoke bundle carries `0.0` max RMSE ticks on retained OHLCV and top-of-book series.
- The repo contains a real compressed search surface, but public proxy retrieval remains bounded until labeled FT-C004 truth exists.
- The delayed-feed acquisition, freeze, and refresh path is real on the bounded SPY/AAPL smoke lane.

## What We Don't Claim

- No Phase 06 closure or public release readiness.
- No broad warehouse or incumbent displacement claim.
- No lossless volume reconstruction claim.
- No promoted public-data search-quality claim while FT-C004 remains unlabeled.
- No claim that the bounded proxy lanes satisfy the sovereign enterprise benchmark.

## Commercial Readiness

| Field | Value |
|-------|-------|
| Verdict | BLOCKED |
| Commit SHA | c8c6ea5e9dcc |
| Confidence | 98% |
| Source | proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json |

## Tests and Verification

| Code | Check | Verdict |
|---|---|---|
| V_01 | Public SPY 10y daily compression | PASS |
| V_02 | Public BTCUSDT aggTrades compression | PASS |
| V_03 | Public Kaggle SPY compression | PASS |
| V_04 | Bounded replay price-field fidelity | PASS |
| V_05 | Phase 06 contract freeze | FAIL |
| V_06 | Public proxy retrieval truth | INC |

## Proof Anchors

| Path | Why it matters |
|---|---|
| `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json` | Retained public benchmark compression and query evidence |
| `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json` | Bounded replay price-field and top-of-book fidelity evidence |
| `proofs/artifacts/real_market_benchmarks/BOUNDARY.json` | Public rehearsal boundary and promotion ban |
| `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json` | Sovereign blocker packet for the open-access enterprise benchmark |
| `proofs/phase06_inputs/series_gap_matrix.csv` | Declared missing-input matrix behind the blocked Phase 06 gate |

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
