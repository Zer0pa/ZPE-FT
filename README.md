<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

<p align="center"><strong>Search financial patterns on compressed delayed-feed archives with deterministic replay and bounded price-field fidelity.</strong></p>
<p align="center"><em>Repo install is real. Retained public-benchmark and bounded proxy evidence are real. The exact Phase 06 authority pack and auditable FT-C004 truth are still missing.</em></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v7.0-e5e7eb?labelColor=111111" alt="License: SAL v7.0"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-%3E%3D3.11-e5e7eb?labelColor=111111" alt="Python >=3.11"></a>
  <a href="proofs/PHASE3_PUBLIC_BENCHMARKS.json"><img src="https://img.shields.io/badge/public%20benchmark-retained-e5e7eb?labelColor=111111" alt="Public benchmark: retained"></a>
  <a href="proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json"><img src="https://img.shields.io/badge/current%20gate-BLOCKED__MISSING__INPUTS-e5e7eb?labelColor=111111" alt="Current gate: BLOCKED_MISSING_INPUTS"></a>
</p>
<p align="center">
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/architecture-runtime%20map-e5e7eb?labelColor=111111" alt="Architecture: runtime map"></a>
  <a href="proofs/phase06_inputs/README.md"><img src="https://img.shields.io/badge/phase06%20inputs-gap%20ledger-e5e7eb?labelColor=111111" alt="Phase 06 inputs: gap ledger"></a>
  <a href="proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json"><img src="https://img.shields.io/badge/FT--C004-truth%20requirements-e5e7eb?labelColor=111111" alt="FT-C004: truth requirements"></a>
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

The honest public wedge is narrow and specific: retained public benchmarks, bounded delayed-feed proxy bundles, and a repo-native acquisition path. The install surface is real. The strongest retained artifacts are still non-authority for Phase 06, and the open-access enterprise benchmark remains blocked on missing exact inputs and auditable FT-C004 truth.

## Key Metrics

| Metric | Value | Baseline |
|---|---|---|
| Public BTCUSDT archive compression | 10.90x | Parquet+ZSTD 3.87x |
| Minute-proxy OHLCV floor | 8.75x | 10x floor |
| Tick-proxy compression floor | 7.16x | 8x floor |
| Smoke-lane price fidelity | 0.0 max RMSE ticks | 0.5 threshold |

> Source: `proofs/PHASE3_PUBLIC_BENCHMARKS.json`, `proofs/artifacts/real_market_benchmarks/minute_30d/artifacts/ft_ohlcv_benchmark.json`, `proofs/artifacts/real_market_benchmarks/tick_20_sessions/artifacts/ft_tick_benchmark.json`, `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json`

## Competitive Benchmarks

The retained public and bounded-proxy surfaces are different evidentiary classes. Public benchmarks show the commercial shape on open archives, bounded proxy bundles reduce execution risk, and neither closes the sovereign enterprise gate.

| Lane | ZPE-FT | Comparator | Boundary |
|---|---|---|---|
| Public BTCUSDT aggTrades archive | 10.90x | Parquet+ZSTD 3.87x | Public benchmark only |
| Minute 30d bounded proxy bundle | 8.75x minimum | 10x authority floor | `promotion_forbidden: true` in `BOUNDARY.json` |
| Tick 20 sessions bounded proxy bundle | 7.16x minimum | 8x authority floor | `promotion_forbidden: true` in `BOUNDARY.json` |
| Alpaca smoke lane | 13.19x OHLCV, 8.40x tick, 0.0 RMSE | Two-series delayed-feed smoke | Operator/local rerun only |

## What We Prove

- The public repo retains a shipped pytest alignment log and runnable package surface.
- The retained public BTCUSDT benchmark compresses materially better than Parquet+ZSTD on archive size.
- The bounded minute and tick proxy bundles are useful rehearsal artifacts with explicit promotion bans for Phase 06.
- The bounded SPY/AAPL smoke lane carries `0.0` max RMSE ticks on retained price-field replay.
- The repo carries the 33-series Phase 06 gap ledger plus the current blocker packet in-repo.

## What We Don't Claim

- No exact Wave-1 authority bundle is carried in the current tracked repo.
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
| V_01 | Package pytest alignment | PASS |
| V_02 | Public BTCUSDT archive compression | PASS |
| V_03 | Bounded minute/tick proxy benchmark gate | FAIL |
| V_04 | Bounded smoke price fidelity | PASS |
| V_05 | Phase 06 contract freeze | FAIL |
| V_06 | FT-C004 truth readiness | FAIL |

## Proof Anchors

| Path | Why it matters |
|---|---|
| `proofs/artifacts/operations/20260321T160048Z_pytest.log` | Retained pytest alignment log for the shipped package surface |
| `proofs/PHASE3_PUBLIC_BENCHMARKS.json` | Public Yahoo/Binance/Kaggle benchmark summary |
| `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json` | Bounded SPY/AAPL smoke-lane fidelity evidence |
| `proofs/artifacts/real_market_benchmarks/BOUNDARY.json` | Public rehearsal boundary and promotion ban |
| `proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json` | FT-C004 truth blockers and label rule |
| `proofs/phase06_inputs/series_gap_matrix.csv` | 33-series authority gap ledger |
| `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json` | Sovereign blocker packet for the open-access enterprise benchmark |

## Repo Shape

| Area | Purpose |
|---|---|
| `python/`, `core/`, `scripts/` | Installable package, optional helper, and repo-local runners |
| `docs/` | Architecture, legal, observability, and market-surface docs |
| `proofs/` | Public benchmarks, bounded proxy bundles, reruns, blocker packets, and operations logs |
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

Start with `docs/ARCHITECTURE.md`, then read `proofs/phase06_inputs/README.md` and `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`. `LICENSE` is the legal source of truth; the repo uses SAL v7.0.
