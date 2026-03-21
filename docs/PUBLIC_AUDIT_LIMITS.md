<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Public Audit Limits

This note defines what the current staged ZPE-FT repo can and cannot establish.
It is intentionally narrow.

<p>
  <img src="../.github/assets/readme/section-bars/scope.svg" alt="SCOPE" width="100%">
</p>

## What The Current Repo Can Establish

- the package, tests, scripts, and proof surfaces are real
- the shipped build, install, and pytest logs support the repo-local package path
- the controlled `2026-02-21` Wave-1 bundle supports the promoted local codec
  claims on its carried corpus
- the repo-native delayed-feed smoke path is real on a bounded two-series sample
- the repo is honest that the open-access enterprise benchmark is still blocked

## What The Current Repo Does Not Establish

- blind-clone verification
- public release readiness
- authority-bearing market `P@10`
- Timescale-backed DB equivalence
- final enterprise benchmark closure

<p>
  <img src="../.github/assets/readme/section-bars/verification.svg" alt="VERIFICATION" width="100%">
</p>

Claim-scope limits:

| Limit | Current state | Why it matters |
|---|---|---|
| Controlled vs market authority | The promoted codec metrics come from the carried Wave-1 controlled bundle. | Readers must not convert controlled-corpus evidence into open-market authority. |
| Delayed-feed smoke scope | The March 19 Alpaca rerun is a two-series delayed-feed smoke with no authority labels. | It proves acquisition/refresh reality, not market pattern authority. |
| Open-access benchmark gate | The March 21 freeze packet is `BLOCKED_MISSING_INPUTS`. | The enterprise/public benchmark is still open, so the repo cannot claim that closure. |
| Timescale path | The Timescale-adjacent rerun remains `INCONCLUSIVE`. | SQLite support does not imply Timescale equivalence. |

Provenance and surface limits:

| Limit | Current state | Why it matters |
|---|---|---|
| Historical absolute paths | Older path-bearing reruns and copied gate runbooks were intentionally removed from the retained repo surface; some carried proof-support files and copied contract refs still preserve original machine-local text. | Current repo truth is carried by retained docs and proof artifacts, but path-bearing copied context must be read as lineage material rather than live instructions. |
| Operator/local vs shipped repo truth | Some delayed-feed and environment-specific surfaces are operator/local. | The shipped repo docs and artifacts outrank remembered workstation narratives. |
| Telemetry sidecars | Comet / Opik are optional sidecars, not the evidentiary root. | Observability URLs do not replace shipped artifacts. |

<p>
  <img src="../.github/assets/readme/section-bars/setup-and-verification.svg" alt="SETUP AND VERIFICATION" width="100%">
</p>

Current audit-path requirements:
- base audit path: `python -m pip install -e .`
- heavier repo-local proof path: `python -m pip install -e ".[test,proof]"`
- optional helper path: `python -m pip install -e ".[native]"` then
  `cd core && maturin develop --release`

Feature and key notes:
- manual telemetry keys are not required for the base audit path
- the repo-local proof gate may require more local disk and dependencies than
  the base package path
- current package/build evidence lives in
  [`../proofs/artifacts/operations/20260321T202948Z_build.log`](../proofs/artifacts/operations/20260321T202948Z_build.log),
  [`../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log`](../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log),
  and [`../proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log`](../proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log)

<p>
  <img src="../.github/assets/readme/section-bars/evidence-and-claims.svg" alt="EVIDENCE AND CLAIMS" width="100%">
</p>

- Apply the status labels literally: `INCONCLUSIVE`, `NEEDS_LABELS`, and
  `BLOCKED_MISSING_INPUTS` are not placeholders for a later green narrative.
- Repo docs normalize raw rerun status tokens such as `blocked_missing_inputs`
  into uppercase labels for readability; the blocker state is unchanged.
- Read the `2026-02-21` bundle as controlled codec authority and the March 21
  packet as the current benchmark blocker.
- Treat the March 19 delayed-feed smoke and historical absolute-path reruns as
  bounded or lineage evidence only.

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
