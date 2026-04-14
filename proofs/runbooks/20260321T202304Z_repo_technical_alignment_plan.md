# ZPE-FT Technical Alignment Plan

Timestamp: 2026-03-21T20:23:04Z
Repo: /Users/zer0pa-build/ZPE/ZPE FT/zpe-finance
Working Instruction Surface:
- /Users/zer0pa-build/ZPE/ZPE FT/zpe-finance/proofs/runbooks/REPO_TECHNICAL_ALIGNMENT_EXECUTION_PROMPT.md
- /Users/zer0pa-build/ZPE/ZPE FT/zpe-finance/proofs/runbooks/REPO_TECHNICAL_EXECUTION_SUPPLEMENT.md

## Classification
- Standalone Python package with an optional repo-local native helper.

## Target Architecture
- Keep `zpe-finance` as a `setuptools` Python distribution.
- Keep the Rust helper non-default and repo-local unless explicitly built.
- Make the base install path truthful for Python fallback.
- Make proof and observability dependencies explicit through extras.
- Make repo-local verification/build surfaces run against the installed package, not `PYTHONPATH` injection.

## Execution Plan
1. Align package metadata and extras in `pyproject.toml` with the actual runtime and proof surfaces.
2. Fix verification harness truth by removing implicit interpreter and `PYTHONPATH` assumptions from the repo-local gate runner and by making optional native-helper behavior explicit.
3. Fix dependency truth in gate scripts where runtime package installation is currently hidden inside execution.
4. Add a minimal CI/package verification workflow that builds the wheel/sdist and checks import/install behavior without claiming publication.
5. Update only the minimum technical docs needed to describe the truthful base install, proof extras, and optional native helper path.
6. Falsify the result with build, editable install, clean-wheel install, import checks, targeted script checks, and full pytest.
