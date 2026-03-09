# Historical Path Limits

Some preserved proof materials in this repo still carry stale machine-absolute paths from the source workstation.

## Why They Were Kept

- to preserve raw evidence lineage
- to preserve exact error signatures for deferred reruns
- to avoid fabricating fresh proof where no rerun was performed in this phase

## Where This Applies

- `proofs/reruns/2026-02-21_runpod_readiness_manifest.json`
- `proofs/reruns/2026-02-21_tsbs_db_benchmark_results.json`
- `proofs/logs/2026-02-21_operator_command_log_historical.txt`
- `proofs/runbooks/RUNBOOK_ZPE_FT_*.md`
- some carried artifact files such as `gorilla_eval_results.json` and `integration_readiness_contract.json`

## How To Read Them

- Treat machine-absolute paths as historical provenance only.
- Do not execute them as current instructions.
- Use current repo-relative docs, scripts, and audit files for current operations.

