<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# ZPE-FT

ZPE-FT ships a Python financial time-series codec and pattern-search package,
an optional repo-local Rust helper, and the retained proof surfaces that bound
what this repo can honestly claim. The package/build/install path is real, the
controlled Wave-1 codec evidence is retained, and the open-access enterprise
benchmark is still blocked. This repo is not public-release-ready.

<p>
  <img src=".github/assets/readme/section-bars/what-this-is.svg" alt="WHAT THIS IS" width="100%">
</p>

| Surface | Current role |
|---|---|
| `python/zpe_finance/` | Installable codec/search surface for OHLCV and tick workflows |
| `core/` | Optional repo-local Rust helper for nibble packing, hashing, and subsequence search |
| `scripts/` | Repo-local replay, acquisition, freeze, and refresh runners |
| `proofs/artifacts/2026-02-21_ft_wave1_final/` | Carried controlled authority bundle for promoted codec claims |
| `proofs/reruns/2026-03-19_alpaca_demo_smoke/` | Bounded delayed-feed market-refresh smoke on a two-series sample |
| `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/` | Current blocker packet for the open-access enterprise benchmark |
| `docs/specs/ZPFIN_SPEC.md` | Packet-format reference for the FT codec surface |

<p>
  <img src=".github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

Canonical authority block:

| Scope | Authority surface | What it establishes | What it does not establish |
|---|---|---|---|
| Current release / benchmark blocker | [`proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`](proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json) | The open-access enterprise benchmark is currently blocked because `33` named corpus exports plus the auditable query catalog and truth labels are still missing | A codec failure verdict or a closed Phase 06 gate |
| Controlled codec claims | [`proofs/CONSOLIDATED_PROOF_REPORT.md`](proofs/CONSOLIDATED_PROOF_REPORT.md) and [`proofs/artifacts/2026-02-21_ft_wave1_final/`](proofs/artifacts/2026-02-21_ft_wave1_final/) | The carried Wave-1 bundle supports promoted local codec claims on the controlled corpus | Blind-clone reproducibility, public release readiness, or enterprise benchmark closure |
| Bounded market-refresh reality | [`proofs/reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json`](proofs/reruns/2026-03-19_alpaca_demo_smoke/real_market_corpus_manifest.json) | The repo-native delayed-feed acquisition, freeze, and refresh path is real on SPY and AAPL | Authority-bearing market `P@10`, broad market displacement, or enterprise readiness |

Canonical repo coordinates:
- Repository URL: `https://github.com/Zer0pa/ZPE-FT`
- Contact: `architects@zer0pa.ai`
- License identity: Zer0pa Source-Available License v6.0
- Public-release posture: `NOT_PUBLIC_READY`

Choose your path:
- Audit the current truth: [`AUDITOR_PLAYBOOK.md`](AUDITOR_PLAYBOOK.md), [`PUBLIC_AUDIT_LIMITS.md`](PUBLIC_AUDIT_LIMITS.md), and [`proofs/FINAL_STATUS.md`](proofs/FINAL_STATUS.md)
- Install or exercise the package: [`pyproject.toml`](pyproject.toml) and the setup section below
- Understand runtime and proof layout: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Review release posture: [`RELEASING.md`](RELEASING.md)

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-2.gif" alt="ZPE-FT Masthead Option 3.2" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

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

| Surface | Truthful entrypoint | Boundary |
|---|---|---|
| Base package sanity | `python -m pip install -e .` | Package import, local codec use, and docs audit |
| Heavier repo-local proof work | `python -m pip install -e ".[test,proof]"` | Proof and rerun work inside this repo |
| Optional native helper | `python -m pip install -e ".[native]"` then `cd core && maturin develop --release` | Only when you intentionally exercise the repo-local helper |
| Controlled Wave-1 replay | `python scripts/run_wave1.py --artifact-root artifacts/2026-02-20_zpe_ft_wave1 --native-helper auto` | Writes a fresh local rerun destination; it does not replace the carried authority bundle under `proofs/artifacts/2026-02-21_ft_wave1_final/` |
| Repo-local env gate | `python poc/scripts/00_env_check.py --workspace . --repo .` | Operator/local proof setup, not the front-door package path |

<p>
  <img src=".github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

Current evidence you can safely repeat:
- shipped build, install, and import truth is evidenced in [`20260321T202948Z_build.log`](proofs/artifacts/operations/20260321T202948Z_build.log), [`20260321T202948Z_clean_install_verify.log`](proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log), and [`20260321T202948Z_pytest_alignment.log`](proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log)
- controlled Wave-1 results remain `19.19x` OHLCV compression, `20.57x` tick compression, max RMSE `0.0`, mean `P@10 = 0.90`, and local query latency `p95 = 0.0567 ms`
- SQLite roundtrip is supported on the carried bundle
- direct comparator evidence exists in the carried bundle, but broader incumbent-displacement claims are not promoted from this repo pass
- the March 19 delayed-feed smoke is real but bounded
- Timescale-backed DB equivalence remains `INCONCLUSIVE`
- the open-access enterprise benchmark remains `BLOCKED_MISSING_INPUTS`: `33` named corpus exports plus the auditable query catalog and truth labels are still missing

Read the proof posture here:
- [`proofs/FINAL_STATUS.md`](proofs/FINAL_STATUS.md)
- [`proofs/CONSOLIDATED_PROOF_REPORT.md`](proofs/CONSOLIDATED_PROOF_REPORT.md)
- [`PUBLIC_AUDIT_LIMITS.md`](PUBLIC_AUDIT_LIMITS.md)
- [`proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log`](proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log)

<p>
  <img src=".github/assets/readme/section-bars/where-to-go.svg" alt="WHERE TO GO" width="100%">
</p>

Routes:
- Fastest honest audit path: [`AUDITOR_PLAYBOOK.md`](AUDITOR_PLAYBOOK.md)
- Canonical doc ownership: [`docs/DOC_REGISTRY.md`](docs/DOC_REGISTRY.md)
- Docs index: [`docs/README.md`](docs/README.md)
- Runtime and proof map: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Release gate: [`RELEASING.md`](RELEASING.md)
- Support routing: [`docs/SUPPORT.md`](docs/SUPPORT.md)

<p>
  <img src=".github/assets/readme/zpe-masthead-option-3-3.gif" alt="ZPE-FT Masthead Option 3.3" width="100%">
</p>

<p>
  <img src=".github/assets/readme/section-bars/contributing-security-support.svg" alt="CONTRIBUTING, SECURITY, SUPPORT" width="100%">
</p>

Support surfaces:
- Contribution rules: [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Security reporting: [`SECURITY.md`](SECURITY.md)
- License boundary: [`docs/LEGAL_BOUNDARIES.md`](docs/LEGAL_BOUNDARIES.md)
- Common questions: [`docs/FAQ.md`](docs/FAQ.md)

<p>
  <img src=".github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
