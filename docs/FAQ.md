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

For promoted codec claims, the authority surface is the controlled
`2026-02-21_ft_wave1_final` bundle. For the current enterprise/public gate, the
authority surface is the March 21 missing-inputs packet.

## Does the repo already close the open-access enterprise benchmark?

No. The current Phase 06 contract freeze is blocked on missing corpus exports
and authority labels.

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

No. Historical artifacts are preserved for lineage and error signatures. Use
the current repo docs and repo-relative scripts for live instructions.
