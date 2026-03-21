# Docs Falsification Report

Timestamp: 2026-03-21T23:14:42Z
Repo: /Users/Zer0pa/ZPE/ZPE FT/zpe-finance
Branch: codex/phase06-reality-check

## Unsupported Claims Removed Or Downgraded
- Root README no longer leads controlled-authority reading with `quality_gate_scorecard.json`; it now leads with the current Phase 06 blocker and routes controlled claims through the retained bundle plus [`proofs/CONSOLIDATED_PROOF_REPORT.md`](/Users/Zer0pa/ZPE/ZPE FT/zpe-finance/proofs/CONSOLIDATED_PROOF_REPORT.md).
- Phase 06 blocker language was tightened from generic "missing corpus exports and authority labels" to the specific retained blocker: `33` named corpus exports plus the auditable query catalog and truth labels are still missing.
- [`docs/INTEGRATION_PATTERN.md`](/Users/Zer0pa/ZPE/ZPE FT/zpe-finance/docs/INTEGRATION_PATTERN.md) was downgraded from a supporting-authority reading to an operator-local reference and stripped of sibling absolute path claims.
- Historical cleanup language was narrowed so copied contract refs and operator prompts are now described as lineage or execution context, not front-door authority.

## Path And Render Issues Found
- Older February rerun leftovers, copied gate runbooks, and copied proof logs were removed from the retained repo surface.
- The retained March 19 rerun artifacts were normalized onto repo-relative paths without changing measured values.
- The March 21 blocker packet was made self-contained inside the repo by copying the referenced Phase 06 contract files into `retained_contract_refs/` and retargeting the query-catalog probe to the retained repo copy.
- Raw rerun status token drift was documented explicitly: the packet still uses `blocked_missing_inputs`, while repo docs normalize that token to `BLOCKED_MISSING_INPUTS` for readability.
- Private GitHub render parity passed: branch head matched remote, README blob matched remote, and rendered HTML contained the required mastheads, extra GIF slots, section bars, and internal route links.

## Remaining Owner Inputs
- Phase 06 is still blocked on the missing named corpus exports, auditable query catalog, and truth labels.
- Public release or PyPI promotion still requires owner ratification after the governing benchmark gate closes.

## Live Vs Local Drift
- Resolved for the rendered doc surfaces in this pass. The pushed branch commit and rendered README matched the local branch at commit `828afe6392dab5992090fa05ffc370e356f2d72d`.
