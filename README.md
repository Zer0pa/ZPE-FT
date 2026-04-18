<p align="center">
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

<p align="center"><strong>Search financial patterns on compressed delayed-feed archives with deterministic replay and bounded price-field fidelity.</strong></p>
<p align="center"><em>Repo install is real. Carried Wave-1 codec evidence is real. The open-access enterprise benchmark is still blocked on missing inputs and auditable query truth.</em></p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-SAL%20v6.2-e5e7eb?labelColor=111111" alt="License: SAL v6.2"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-%3E%3D3.11-e5e7eb?labelColor=111111" alt="Python >=3.11"></a>
  <a href="proofs/artifacts/2026-02-21_ft_wave1_final/claim_status_delta.md"><img src="https://img.shields.io/badge/controlled%20bundle-Wave--1%20carried-e5e7eb?labelColor=111111" alt="Controlled bundle: Wave-1 carried"></a>
  <a href="proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json"><img src="https://img.shields.io/badge/current%20gate-BLOCKED__MISSING__INPUTS-e5e7eb?labelColor=111111" alt="Current gate: BLOCKED_MISSING_INPUTS"></a>
</p>
<p align="center">
  <a href="docs/AUDITOR_PLAYBOOK.md"><img src="https://img.shields.io/badge/quick%20audit-playbook-e5e7eb?labelColor=111111" alt="Quick audit: playbook"></a>
  <a href="docs/ARCHITECTURE.md"><img src="https://img.shields.io/badge/architecture-runtime%20map-e5e7eb?labelColor=111111" alt="Architecture: runtime map"></a>
  <a href="docs/PUBLIC_AUDIT_LIMITS.md"><img src="https://img.shields.io/badge/public%20audit-explicit%20limits-e5e7eb?labelColor=111111" alt="Public audit: explicit limits"></a>
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

The honest commercial wedge is narrow and specific: archive-native pattern search plus deterministic replay on delayed-feed market data, with strong compression on the controlled Wave-1 bundle and a bounded repo-native acquisition path. The repo install surface is real. The public-data rehearsal lanes are useful but non-authority. The open-access enterprise benchmark is still blocked on missing inputs and auditable FT-C004 truth.

| Field | Value |
|-------|-------|
| Architecture | MARKET_TICK_STREAM |
| Encoding | FT_NIBBLE_DELTA_V1 |

## Key Metrics

| Metric | Value | Baseline |
|---|---|---|
| PATTERN_SEARCH_P10 | 90% | top-10 precision |
| DETERMINISTIC_REPLAY | 5/5 | hash-consistent runs |
| WAVE1_OHLCV_CR | 19.19x | zlib 8.35x |
| WAVE1_TICK_CR | 20.57x | zlib 6.56x |

> Source: [`proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json`](proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json), [`proofs/artifacts/2026-02-21_ft_wave1_final/determinism_replay_results.json`](proofs/artifacts/2026-02-21_ft_wave1_final/determinism_replay_results.json), [`proofs/artifacts/2026-02-21_ft_wave1_final/before_after_metrics.json`](proofs/artifacts/2026-02-21_ft_wave1_final/before_after_metrics.json)

## Competitive Benchmarks

Wave-1 controlled codec claims and public rehearsal benchmarks are different surfaces. The controlled bundle carries the promoted codec numbers. The public benchmark shows the commercial shape on an open archive, but it does not close the enterprise gate.

| Lane | ZPE-FT | Comparator | Boundary |
|---|---|---|---|
| Wave-1 OHLCV controlled bundle | 19.19x | zlib 8.35x, lzma 13.13x, bz2 16.12x | Authority-bearing carried bundle |
| Wave-1 tick controlled bundle | 20.57x | zlib 6.56x, lzma 11.37x, bz2 11.76x | Authority-bearing carried bundle |
| Public BTCUSDT aggTrades archive | 10.90x | Parquet+ZSTD 3.87x | Public benchmark only |
| Real-market proxy lanes | Useful rehearsal only | 10x authority floor still missed on some series | `promotion_forbidden: true` in `BOUNDARY.json` |

## What We Prove

- The public repo builds, installs, imports, and retains current build/install/pytest logs under `proofs/artifacts/operations/`.
- The carried Wave-1 bundle proves deterministic OHLCV and top-of-book tick compression on the controlled corpus.
- Price fields plus top-of-book bid/ask carry `0.0` RMSE on the controlled bundle; volume is quantized separately and is not part of that claim.
- The repo contains a real compressed search surface, but public proxy retrieval remains bounded until labeled FT-C004 truth exists.
- The delayed-feed acquisition, freeze, and refresh path is real on the bounded SPY/AAPL smoke lane.

## What We Don't Claim

- No Phase 06 closure or passed open-access enterprise benchmark.
- No broad warehouse or incumbent displacement claim.
- No lossless volume reconstruction claim.
- No promoted public-data search-quality claim while FT-C004 remains unlabeled.
- No claim that the bounded proxy lanes satisfy the sovereign enterprise benchmark.

## Commercial Readiness

| Field | Value |
|---|---|
| Verdict | `BLOCKED` |
| Commit SHA | `59a2ec90bf38` |
| Confidence | `98%` |
| Source | [`proofs/artifacts/2026-02-21_ft_wave1_final/claim_status_delta.md`](proofs/artifacts/2026-02-21_ft_wave1_final/claim_status_delta.md) |

This repo is useful now for archive-native pattern search, deterministic replay, and bounded delayed-feed compression. The current buyer wedge is market-data infrastructure teams or quant research platforms via the Python SDK, and the governing blocker packet remains `BLOCKED_MISSING_INPUTS`: 33 named corpus exports plus auditable FT-C004 truth are still missing.

## Tests and Verification

| Code | Check | Verdict |
|---|---|---|
| V_01 | Package build, install, import | PASS |
| V_02 | Wave-1 OHLCV compression | PASS |
| V_03 | Wave-1 tick compression | PASS |
| V_04 | Controlled price-field fidelity | PASS |
| V_05 | Phase 06 contract freeze | FAIL |
| V_06 | Public proxy retrieval truth | INC |

## Proof Anchors

| Path | Why it matters |
|---|---|
| `proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log` | Public clone install and import truth |
| `proofs/artifacts/2026-02-21_ft_wave1_final/claim_status_delta.md` | Claim-by-claim carried Wave-1 bundle summary |
| `proofs/artifacts/2026-02-21_ft_wave1_final/before_after_metrics.json` | Controlled Wave-1 compression summary for the promoted codec claims |
| `proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json` | Controlled pattern-search precision evidence on the carried bundle |
| `proofs/artifacts/2026-02-21_ft_wave1_final/determinism_replay_results.json` | Five-run deterministic replay evidence for byte-identical outputs |
| `proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json` | Governing quality gate score used for the readiness confidence reading |
| `proofs/artifacts/2026-02-21_ft_wave1_final/ft_reconstruction_fidelity.json` | Controlled price-field and top-of-book fidelity evidence |
| `proofs/artifacts/real_market_benchmarks/BOUNDARY.json` | Public rehearsal boundary and promotion ban |
| `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json` | Sovereign blocker packet for the open-access enterprise benchmark |

## Repo Shape

| Area | Purpose |
|---|---|
| `python/`, `core/`, `scripts/` | Installable package, optional helper, and repo-local runners |
| `docs/` | Audit, architecture, legal, and packet-contract surfaces |
| `proofs/` | Carried bundles, reruns, blocker packets, and operations logs |
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

Start with `docs/AUDITOR_PLAYBOOK.md`, then read `docs/PUBLIC_AUDIT_LIMITS.md`, `docs/LEGAL_BOUNDARIES.md`, and `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`. `LICENSE` is the legal source of truth; the repo uses SAL v6.2.
