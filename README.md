# ZPE-FT

Private staging repository for the ZPE financial time-series sector.

This repo contains the FT package surface, the preserved Rust-core source, selected Wave-1 proof artifacts, and the minimum front-door/audit/legal structure needed for private inspection. It is not a public release and it is not yet a Phase 5 verified snapshot.

## What This Repo Is

- Python package for OHLCV and tick-stream encoding/decoding under `python/zpe_finance`
- Rust-core source for nibble packing and subsequence search under `core/`
- Gate and proof-generation scripts under `scripts/`
- Curated proof artifacts under `proofs/`
- FT packet/spec material under `docs/specs/ZPFIN_SPEC.md`

## Current Authority

The strongest carried-forward evidence in this repo comes from the 2026-02-21 Wave-1 final bundle:

| Surface | Current evidence |
| --- | --- |
| OHLCV compression | `19.19x` in [proofs/artifacts/2026-02-21_ft_wave1_final/ft_ohlcv_benchmark.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_ohlcv_benchmark.json) |
| Tick compression | `20.57x` in [proofs/artifacts/2026-02-21_ft_wave1_final/ft_tick_benchmark.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_tick_benchmark.json) |
| Reconstruction fidelity | `0.0` tick RMSE in [proofs/artifacts/2026-02-21_ft_wave1_final/ft_reconstruction_fidelity.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_reconstruction_fidelity.json) |
| Pattern search | mean `P@10 = 0.9` in [proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_pattern_search_eval.json) |
| Query latency | local `p95 = 0.0567 ms` in [proofs/artifacts/2026-02-21_ft_wave1_final/ft_query_latency_benchmark.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_query_latency_benchmark.json) |
| DB roundtrip | SQLite bit-consistent in [proofs/artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json) |

Current hard limits:

- The Timescale path remains `INCONCLUSIVE`; see [proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json](proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json).
- Runpod rerun is still required for the deferred Docker-enabled Timescale path; see [proofs/reruns/2026-02-21_runpod_readiness_manifest.json](proofs/reruns/2026-02-21_runpod_readiness_manifest.json).
- Blind-clone verification has not been run in this phase.

## Proof Anchors

- [proofs/FINAL_STATUS.md](proofs/FINAL_STATUS.md)
- [proofs/CONSOLIDATED_PROOF_REPORT.md](proofs/CONSOLIDATED_PROOF_REPORT.md)
- [proofs/HISTORICAL_PATH_LIMITS.md](proofs/HISTORICAL_PATH_LIMITS.md)
- [proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json](proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json)
- [proofs/artifacts/2026-02-21_ft_wave1_final/determinism_replay_results.json](proofs/artifacts/2026-02-21_ft_wave1_final/determinism_replay_results.json)
- [proofs/reruns/2026-02-21_runpod_readiness_manifest.json](proofs/reruns/2026-02-21_runpod_readiness_manifest.json)

## Quick Verify

Minimal package sanity only:

```bash
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

Expected note:

- `rust_bridge` may report `python-fallback` unless the PyO3 extension is built separately. The Rust source is preserved in `core/`, but this phase did not add a packaged Rust build pipeline.

## Repo Map

- [AUDITOR_PLAYBOOK.md](AUDITOR_PLAYBOOK.md)
- [PUBLIC_AUDIT_LIMITS.md](PUBLIC_AUDIT_LIMITS.md)
- [docs/README.md](docs/README.md)
- [proofs/FINAL_STATUS.md](proofs/FINAL_STATUS.md)

## License Boundary

`LICENSE` is the legal source of truth. This repository is source-available under Zer0pa SAL v6.0, not an OSI open-source license.

## Lane Boundaries

- This repo is the private staged FT repo only.
- Outer-workspace orchestration records, vendored repos, toolchains, caches, and machine-local environments are intentionally excluded.
- Historical raw proof captures that still contain machine-absolute paths are preserved only as evidence and are explicitly bounded by [proofs/HISTORICAL_PATH_LIMITS.md](proofs/HISTORICAL_PATH_LIMITS.md).

