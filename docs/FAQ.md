<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

Organised by first-contact question. If the answer you need is not here, read
`docs/SUPPORT.md`.

---

<p>
  <img src="../.github/assets/readme/section-bars/questions.svg" alt="QUESTIONS" width="100%">
</p>

## Is this the public release repo?

No. This is the live source-available repo for the workstream, but the release
gate is still open. The package path is real and the proof surfaces are real,
yet the repo remains `NOT_PUBLIC_READY` until the governing benchmark blocker
is closed.

## What are the current authority surfaces?

Trust three surfaces for three different questions:

- package/build/install truth:
  `proofs/artifacts/operations/20260321T202948Z_build.log`,
  `proofs/artifacts/operations/20260321T202948Z_clean_install_verify.log`,
  and `proofs/artifacts/operations/20260321T202948Z_pytest_alignment.log`
- promoted codec metrics on the controlled corpus:
  `proofs/artifacts/2026-02-21_ft_wave1_final/`
- open-access enterprise benchmark status:
  `proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json`

## Does the repo already close the open-access enterprise benchmark?

No. The gate is still blocked because `33` named corpus exports plus the
auditable query catalog and truth labels are still missing. Until those inputs
exist and a clean freeze/replay closes, the benchmark status cannot change.

## Is the March 19 Alpaca delayed-feed smoke an authority market benchmark?

No. It proves the repo-native acquisition, freeze, and refresh path on a
bounded sample. It is explicitly not the closing enterprise benchmark.

## Why is there Rust code if quick verify may report `python-fallback`?

The helper is optional and repo-local. The truthful default quick verify path
is the Python surface unless you explicitly build the native helper from
`core/`.

## Does the repo prove Timescale equivalence?

No. SQLite roundtrip is supported. Timescale equivalence remains
`INCONCLUSIVE`.

## Are the historical runbooks and raw logs current instructions?

No. Older path-bearing runbooks and historical leftovers are retained only as
lineage or operator-local context. Current front-door instructions live in the
root `README.md`, `docs/AUDITOR_PLAYBOOK.md`, `docs/ARCHITECTURE.md`, and the
repo-relative scripts they cite.

## What is the strongest honest way to describe ZPE-FT today?

As a real financial time-series codec/search repo with retained controlled-bundle
evidence, a bounded market smoke, and an explicit benchmark blocker. The honest
read is stronger than "demo only" and weaker than "public release ready."

<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>
