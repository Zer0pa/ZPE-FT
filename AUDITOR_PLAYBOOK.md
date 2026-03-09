# Auditor Playbook

This is the shortest honest audit path for the private staged FT repository.

## Shortest Audit Path

1. Read [README.md](README.md) for current authority and current limits.
2. Read [PUBLIC_AUDIT_LIMITS.md](PUBLIC_AUDIT_LIMITS.md) before interpreting any proof file.
3. Install the package surface:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

4. Run a near-zero-cost import sanity:

```bash
python - <<'PY'
from zpe_finance import PatternIndex, encode_ohlcv, encode_ticks
from zpe_finance.rust_bridge import rust_version
print("ok", PatternIndex.__name__, callable(encode_ohlcv), callable(encode_ticks), rust_version())
PY
```

5. Inspect the carried-forward proof anchors:
   - [proofs/FINAL_STATUS.md](proofs/FINAL_STATUS.md)
   - [proofs/CONSOLIDATED_PROOF_REPORT.md](proofs/CONSOLIDATED_PROOF_REPORT.md)
   - [proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json](proofs/artifacts/2026-02-21_ft_wave1_final/quality_gate_scorecard.json)
   - [proofs/artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json](proofs/artifacts/2026-02-21_ft_wave1_final/ft_db_roundtrip_results.json)
   - [proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json](proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json)

## What This Establishes

- The repo contains a real FT package surface.
- The carried proof bundle documents strong local Wave-1 evidence for compression, fidelity, pattern search, query latency, and SQLite roundtrip behavior.
- The staged repo exposes the unresolved Timescale rerun requirement instead of hiding it.

## What This Does Not Establish

- It does not establish blind-clone reproducibility.
- It does not establish public-release readiness.
- It does not establish Timescale equivalence; that path remains deferred.
- It does not upgrade historical raw logs with stale machine paths into current instructions.

## If Your Replay Disagrees

- Treat current runtime output as stronger than prose.
- Local divergence should be reported with:
  - exact command
  - environment details
  - output or traceback
  - the specific proof file or claim you believe is contradicted

