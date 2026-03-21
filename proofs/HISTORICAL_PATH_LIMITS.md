<p>
  <img src="../.github/assets/readme/zpe-masthead.gif" alt="ZPE-FT Masthead" width="100%">
</p>

# Historical Path Limits

Some preserved proof materials in this repo still carry stale machine-absolute
paths from source workstations.

## Why They Were Kept

- to preserve raw evidence lineage
- to preserve exact error signatures for deferred reruns
- to avoid fabricating fresh proof where no clean rerun was performed

## Where This Applies

- `proofs/reruns/2026-02-21_runpod_readiness_manifest.json`
- `proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json`
- `proofs/logs/2026-02-21_operator_command_log_historical.txt`
- `proofs/runbooks/RUNBOOK_ZPE_FT_*.md`
- carried artifact files such as `gorilla_eval_results.json`

## What This Does Not Mean

- it does not downgrade the repo-relative March 19 delayed-feed smoke artifacts
- it does not downgrade the March 21 missing-inputs packet
- it does not hide the current live blockers around missing inputs, rights
  freezes, or unresolved infrastructure dependencies

## How To Read Them

- Treat machine-absolute paths as historical provenance only.
- Do not execute them as current instructions.
- Use current repo-relative docs, scripts, and proof docs for current
  operations.
