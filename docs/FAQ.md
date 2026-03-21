<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# FAQ

<p>
  <img src="../.github/assets/readme/section-bars/questions.svg" alt="QUESTIONS" width="100%">
</p>

## Is this a public release repo?

No. This is a private staged workstream repo. The package source, build, and
clean install/import path are evidenced in
[`../proofs/artifacts/operations/20260321T202948Z_build.log`](../proofs/artifacts/operations/20260321T202948Z_build.log)
and
[`../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log`](../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log),
but the release gate is still open.

## What are the current authority surfaces?

Trust three surfaces for three different questions:
- package/build/install truth:
  [`../proofs/artifacts/operations/20260321T202948Z_build.log`](../proofs/artifacts/operations/20260321T202948Z_build.log),
  [`../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log`](../proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log),
  and [`../proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log`](../proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log)
- promoted codec metrics on the controlled corpus:
  `2026-02-21_ft_wave1_final`
- enterprise/public benchmark status:
  the March 21 missing-inputs packet under
  [`../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/`](../proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/)

## Does the repo already close the open-access enterprise benchmark?

No. The gate is still blocked because `33` named corpus exports plus the
auditable query catalog and truth labels are still missing. Until those inputs
exist and a clean freeze/replay closes, the benchmark status cannot change.

## Is the March 19 Alpaca delayed-feed smoke an authority market benchmark?

No. It proves the repo-native acquisition and refresh path on a bounded sample.
It is explicitly not the closing enterprise benchmark.

## Why is there Rust code if quick verify may report `python-fallback`?

The helper is optional and repo-local. The truthful default path is the Python
fallback unless you explicitly build the helper from `core/`.

## Does the repo prove Timescale equivalence?

No. SQLite roundtrip is supported. Timescale equivalence remains
`INCONCLUSIVE`.

## Are the historical runbooks and raw logs current instructions?

No. Older copied gate runbooks and February log leftovers were intentionally
removed from the retained repo surface. Current operator prompts under
`proofs/runbooks/` remain execution context only, while the retained proof
artifacts may still preserve some machine-local text as lineage evidence. Use
the current repo docs and repo-relative scripts for live instructions.

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
