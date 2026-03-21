<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Auditor Playbook

This is the shortest honest audit path for the current private staged ZPE-FT
repo. It is not a scientific novelty ruling, a legal opinion, or a substitute
for deeper diligence.

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

Three dimensions of current truth:
- Dimension 1: the `zpe_finance` package source, build path, and clean install/import path are evidenced in shipped logs.
- Dimension 2: the promoted codec claims are carried by the controlled
  `2026-02-21` Wave-1 final bundle.
- Dimension 3: the repo is honest that the open-access enterprise benchmark and
  Timescale equivalence remain unresolved.

<p>
  <img src=".github/assets/readme/section-bars/quick-start.svg" alt="QUICK START" width="100%">
</p>

1. Acquire the current private repo snapshot you have been granted access to:

```bash
git clone https://github.com/Zer0pa/ZPE-FT.git
cd ZPE-FT
```

2. Install the base package surface:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .
```

3. Verify import truth:

```bash
python - <<'PY'
import zpe_finance
from zpe_finance.rust_bridge import rust_version
print("exports", sorted(zpe_finance.__all__))
print("rust_bridge", rust_version())
PY
```

Expected current truth:
- the package imports cleanly
- `rust_bridge` may truthfully report `python-fallback` unless you explicitly
  build the optional helper
- shipped verification logs for this surface live at
  [`proofs/artifacts/operations/20260321T202948Z_build.log`](proofs/artifacts/operations/20260321T202948Z_build.log),
  [`proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log`](proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log),
  and [`proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log`](proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log)

4. Read the current authority surfaces together:
- [`README.md`](README.md)
- [`PUBLIC_AUDIT_LIMITS.md`](PUBLIC_AUDIT_LIMITS.md)
- [`proofs/FINAL_STATUS.md`](proofs/FINAL_STATUS.md)
- [`proofs/CONSOLIDATED_PROOF_REPORT.md`](proofs/CONSOLIDATED_PROOF_REPORT.md)

5. If you need the heavier repo-local proof surface, install the proof extras:

```bash
python -m pip install -e ".[test,proof]"
```

Optional repo-local gates:
- controlled Wave-1 replay: `python scripts/run_wave1.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --native-helper auto`
  This writes a fresh local rerun destination. It does not replace the carried
  authority bundle under `proofs/artifacts/2026-02-21_ft_wave1_final/`.
- repo-local environment gate for proof work: `python poc/scripts/00_env_check.py --workspace . --repo .`

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

| Anchor / artifact | Class | What it is for | What it is not for |
|---|---|---|---|
| [`proofs/artifacts/2026-02-21_ft_wave1_final/`](proofs/artifacts/2026-02-21_ft_wave1_final/) | controlled authority | promoted local codec claims on the carried Wave-1 corpus | market-authority proof or enterprise benchmark closure |
| [`proofs/reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json`](proofs/reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json) | bounded operator/local truth | repo-native delayed-feed acquisition and refresh smoke on SPY/AAPL | public/open-access authority or labeled market-pattern proof |
| [`proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_pattern_search_eval.json`](proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_pattern_search_eval.json) | bounded operator/local truth | explicit evidence that the smoke run remains `NEEDS_LABELS` | authority-bearing real-market `P@10` |
| [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json) | current blocker surface | exact current reason the open-access enterprise benchmark is blocked | a codec failure verdict |
| [`proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json`](proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json) | historical operator evidence | chronology for the deferred Timescale-adjacent path | current portable instructions or a closed equivalence gate |
| [`proofs/logs/2026-02-21_operator_command_log_historical.txt`](proofs/logs/2026-02-21_operator_command_log_historical.txt) | historical lineage | raw workstation command lineage | current repo-native operating instructions |

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

Current evidence you can safely repeat after audit:
- OHLCV compression: `19.19x` on the carried Wave-1 controlled corpus
- Tick compression: `20.57x` on the carried Wave-1 controlled corpus
- Reconstruction fidelity: supported on the carried bundle
- Pattern search: mean `P@10 = 0.9` on the carried canonical-template corpus
- SQLite roundtrip: supported on the carried bundle
- Delayed-feed smoke: real but bounded; not authority for enterprise claims
- Timescale equivalence: `INCONCLUSIVE`
- Open-access enterprise benchmark: `BLOCKED_MISSING_INPUTS`

<p>
  <img src=".github/assets/readme/section-bars/evidence-dispute.svg" alt="EVIDENCE DISPUTE" width="100%">
</p>

If your replay disagrees, capture:
- commit hash or snapshot identity
- exact command
- stdout / stderr
- the specific artifact or claim you believe is contradicted
- whether the disagreement is on the controlled Wave-1 bundle, the delayed-feed
  smoke, or the open-access benchmark blocker surface

Then read:
- [`PUBLIC_AUDIT_LIMITS.md`](PUBLIC_AUDIT_LIMITS.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/FAQ.md`](docs/FAQ.md)
