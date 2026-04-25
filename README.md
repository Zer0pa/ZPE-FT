<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

<p align="center"><strong>Search financial patterns on compressed delayed-feed archives with deterministic replay and bounded price-field fidelity.</strong></p>
<p align="center"><em>One of 17 independent codec products in the Zer0pa portfolio. Retained public-benchmark, bounded replay, and blocker artifacts are real. The open-access enterprise benchmark is still blocked on missing inputs and auditable query truth.</em></p>
<p align="center"><strong>Public benchmark (3 datasets, parquet+zstd+DuckDB baseline):</strong> 5.9–10.9× smaller than raw (aggregate across 3 datasets) · 2.7–3.3× smaller than parquet+zstd (aggregate across 3 datasets) · up to 62.9× faster pattern query vs DuckDB (OHLCV datasets; tick at scale: latency parity) · exact tick fidelity (RMSE = 0.0) · <a href="proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json">proof artifact</a></p>

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

| What This Is | Verified Claims | Comp Benchmarks | What We Don't Claim |
|---|---|---|---|
| [Jump](#what-this-is) | [Jump](#verified-claims) | [Jump](#comp-benchmarks-vs-parquetzstdduckdb) | [Jump](#what-we-dont-claim) |

| Commercial Readiness | Tests and Verification | Proof Anchors | Repo Shape | Quick Start |
|---|---|---|---|---|
| [Jump](#commercial-readiness) | [Jump](#tests-and-verification) | [Jump](#proof-anchors) | [Jump](#repo-shape) | [Jump](#quick-start) |

## What This Is

ZPE-FT is a deterministic financial time-series codec and search surface for teams that need to archive delayed-feed market data, replay it exactly, and query patterns without first inflating the archive back into a warehouse table.

The wedge is narrow and specific: compressed delayed-feed archives with deterministic replay, retained public-benchmark evidence on open datasets, and bounded replay fidelity on the in-repo smoke bundle. Public-data rehearsal lanes are useful evidence; they are not authority enterprise inputs. The open-access enterprise benchmark is still blocked on missing inputs and auditable FT-C004 truth.

## Verified Claims

| Claim | Proof artifact on disk | CI coverage |
|---|---|---|
| Public benchmark artifacts are retained for Yahoo SPY, Binance BTCUSDT aggTrades, and Kaggle SPY. | `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json` | `tests/test_public_benchmarks.py` runs the benchmark script on local fixtures and requires three `status == "ok"` entries. |
| Repo-bundled OHLCV roundtrip stays within the bounded price-field error threshold and compresses below raw bytes. | `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json` | `tests/test_ohlcv_roundtrip.py` asserts `rmse <= 0.5` ticks and encoded payload is smaller than raw. |
| Freeze and refresh scripts execute on a declared corpus contract and emit benchmark, fidelity, latency, and roundtrip artifacts. | `proofs/reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json` | `tests/test_real_market_corpus.py` runs `freeze_real_market_corpus.py` and `run_real_market_refresh.py` on fixture corpora. |
| Missing authority inputs keep the sovereign Phase 06 gate blocked. | `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json` | `tests/test_real_market_corpus.py` asserts missing inputs return `blocked_missing_inputs`. |
| FT-C004 truth remains blocked until labels or audit refs exist. | `proofs/artifacts/real_market_benchmarks/ft_c004_truth_requirements.json` | `tests/test_phase06_partial_scripts.py` and `tests/test_real_market_refresh_extras.py` assert blocked-vs-ready truth-surface outcomes. |

## Comp Benchmarks vs parquet+zstd+DuckDB

The baseline for all comp benchmarks is **Parquet (ZSTD compression) queried via DuckDB** — a representative modern data-warehouse path for financial time-series pattern search. Each row below is a retained artifact from a real public dataset run, not a synthetic fixture.

| Dataset | Rows | ZPE size vs raw | ZPE size vs parquet+zstd | ZPE query p95 vs parquet p95 | Price-field RMSE (ticks) | Proof artifact |
|---|---|---|---|---|---|---|
| Yahoo SPY 10y daily (OHLCV) | 2,513 | **5.94x** | **2.69x** | **62.9x faster** (0.70 ms vs 43.9 ms) | 0.0 | `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json` |
| Kaggle SPY full history (OHLCV) | 3,201 | **7.31x** | **3.32x** | **13.2x faster** (1.04 ms vs 13.7 ms) | 0.0 | `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json` |
| Binance BTCUSDT aggTrades 2017-09 (tick) | 198,880 | **10.90x** | **2.81x** | parity (63.4 ms vs 55.6 ms) | 0.0 | `proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json` |

Notes on scope: the Binance tick dataset is a trade-tape mapping (bid=ask=trade price) because Binance public aggTrades do not expose top-of-book quotes; query-latency parity at ~200k rows is expected for that workload shape. OHLCV latency advantage is largest on daily series; tick at scale has a different profile. These are delayed-feed public datasets, not authority enterprise inputs.

## Retained Proxy-Lane Metrics

These results are from repo-bundled provider-max proxy lanes (not the sovereign Phase 06 authority pack). They are useful evidence of codec behaviour across 30 symbols and tick corpora; they are not the enterprise benchmark.

| Lane | Series | RMSE (ticks) | Query p95 | Encode p95 | Proof artifact |
|---|---|---|---|---|---|
| Alpaca demo smoke — SPY 1m bars | 1 OHLCV | **0.0** (exact tick) | 0.01 ms | n/a | `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json` |
| Alpaca demo smoke — AAPL tick stream | 1 tick | **0.0** (exact tick); 8.40x compression vs raw | n/a | n/a | `proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_tick_benchmark.json` |
| 30-symbol daily 24-month corpus | 30 OHLCV | **0.0 across all 30 series** | 0.077 ms (p95 across 15,000 corpus points) | 4.2 ms | `proofs/artifacts/real_market_benchmarks/daily_24m/artifacts/ft_reconstruction_fidelity.json` |
| Dukascopy tick 20-session corpus | 3 tick | **0.0 across all 3 series**; 7.2–14.9x compression range (mean 11.1x) | 39.1 ms (p95) | 1,281 ms | `proofs/artifacts/real_market_benchmarks/tick_20_sessions/artifacts/ft_reconstruction_fidelity.json` |

CI coverage for all proxy lanes: `tests/test_real_market_corpus.py`, `tests/test_ohlcv_roundtrip.py`, `tests/test_packet_roundtrip.py`.

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
| Commit SHA | c8c6ea5e9dcc |
| Confidence | 98% |
| Source | `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`; `proofs/phase06_inputs/series_gap_matrix.csv` |

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
