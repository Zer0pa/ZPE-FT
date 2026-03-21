# Docs Falsification Report

Timestamp: 2026-03-21T22:10:30Z
Branch: `codex/phase06-reality-check`

## Unsupported Claims Removed Or Downgraded

- Package/build/install reality is now routed to shipped evidence logs instead of
  standing as unsupported prose:
  [`20260321T202948Z_build.log`](20260321T202948Z_build.log),
  [`20260321T202948Z_clean_install_verify.log`](20260321T202948Z_clean_install_verify.log),
  and [`20260321T202948Z_pytest_alignment.log`](20260321T202948Z_pytest_alignment.log).
- The legal boundary wording was narrowed so shipped proof artifacts and
  historical reruns are no longer described as a blanket relicensing of every
  embedded external output.
- The Wave-1 story now separates the carried authority bundle under
  `proofs/artifacts/2026-02-21_ft_wave1_final/` from fresh local rerun
  destinations under `artifacts/2026-02-20_zpe_ft_wave1`.
- The docs no longer treat “current authority artifact” as singular; they now
  distinguish codec-claim authority from release-gate authority.
- Unsupported status wording such as `formed` was removed from the current proof
  posture.

## Path And Render Issues Found

- One nonexistent section-bar reference was removed and replaced with a shipped
  asset.
- Misleading live-IMC section-bar filenames were avoided where they would have
  rendered the wrong label text.
- The canonical registry, architecture map, and consolidated proof table were
  converted from code-formatted paths to clickable links.
- Local markdown/image/file-path verification passed:
  [`20260321T220422Z_docs_link_check.log`](20260321T220422Z_docs_link_check.log).
- Token/evidence consistency verification passed:
  [`20260321T220422Z_docs_consistency_check.log`](20260321T220422Z_docs_consistency_check.log).
- GitHub-render verification on the pushed private branch passed:
  [`20260321T220808Z_github_render_check.log`](20260321T220808Z_github_render_check.log).

## Remaining Owner Inputs

- Materialize the `33` named Phase 06 corpus exports.
- Attach the auditable query catalog and truth-label surface required for the
  buyer-authority benchmark.
- Decide whether the Timescale path closes or is explicitly excluded from
  release claims.
- Ratify any public release or PyPI move only after the benchmark gate closes.

## Live-Vs-Local Drift

- The canonical docs playbook was copied into the repo and used as the local
  operating surface:
  [`../../runbooks/ZER0PA_REPO_DOCS_PLAYBOOK_CANONICAL_2026-03-21.md`](../../runbooks/ZER0PA_REPO_DOCS_PLAYBOOK_CANONICAL_2026-03-21.md).
- The pushed branch hash matched the local branch hash during verification.
- The GitHub raw README hash matched the local README hash exactly.
- GitHub-rendered HTML on the pushed branch showed the mastheads, section bars,
  and routed internal links expected by this docs pass.

## Verdict

- The documentation pass is coherent enough to push and review.
- The repo is still not public-ready because the governing Phase 06
  buyer-authority benchmark remains open.
