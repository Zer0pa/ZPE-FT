# RUNBOOK_ZPE_FT_MASTER

## Metadata
- Lane: `/Users/prinivenpillay/ZPE Multimodality/ZPE FT`
- PRD: `PRD_ZPE_FT_SECTOR_EXPANSION_WAVE1_2026-02-20.md`
- Startup prompt: `STARTUP_PROMPT_ZPE_FT_SECTOR_AGENT_2026-02-20.md`
- Concept anchor: `/Users/prinivenpillay/ZPE Multimodality/ZPE Sector Expansion Concept Docs/ZPE Financial Time Series — Concept Document v1.0.md`
- Rubric: `/Users/prinivenpillay/ZPE Multimodality/SECTOR_EXECUTION_QUALITY_RUBRIC_2026-02-20.md`
- Artifact root: `artifacts/2026-02-20_zpe_ft_wave1/`

## Lane Boundary
- Read/write only inside this lane.
- Do not modify `/Users/prinivenpillay/ZPE Multimodality/packetgram`.
- Do not modify `/Users/prinivenpillay/ZPE Multimodality/strokegram`.

## Gate Order (Hard)
1. Gate A: runbook + dataset/resource lock + schema freeze.
2. Gate B: encode/decode + fidelity.
3. Gate C: compression + pattern search + latency.
4. Gate D: adversarial/malformed/determinism.
5. Gate E: DB roundtrip + packaging + claim update.

## Deterministic Seed Policy
- Global seed: `20260220`.
- Python: `random.seed(20260220)`, `numpy.random.default_rng(20260220)`.
- Rust: deterministic algorithms only, no wall-clock randomness.
- Replays: 5 runs; hash of canonical outputs must be identical.

## Dataset/Resource Provenance Lock
- Primary bar source: local deterministic synthetic generator plus optional public market bars (`yfinance`) when reachable.
- Primary tick source: deterministic synthetic MqlTick-like stream generator.
- Provenance metadata per dataset saved in `artifacts/2026-02-20_zpe_ft_wave1/dataset_lock.json` with:
  - source_reference
  - retrieval_timestamp_utc
  - row_count
  - schema hash
  - content hash (SHA-256)
- If external data fetch fails, fallback to deterministic synthetic corpus and keep comparability-related claims `INCONCLUSIVE` unless equivalence is established.

## Schema/Inventory Freeze (Planned)
- `python/zpe_finance/schema.py`: canonical bar/tick schema and validators.
- `format/ZPFIN_SPEC.md`: packet framing and versioning.
- `artifacts/.../schema_inventory_freeze.json`: frozen field inventory + versions.

## Claim Matrix With Popper-First Falsification
- FT-C001 (OHLCV CR >= 10x)
  - Falsify first: run compression on gap/open and volatility spikes.
  - Evidence: `artifacts/.../ft_ohlcv_benchmark.json`.
- FT-C002 (Tick CR >= 8x)
  - Falsify first: microburst ticks and spread spikes.
  - Evidence: `artifacts/.../ft_tick_benchmark.json`.
- FT-C003 (RMSE <= 0.5 tick)
  - Falsify first: adversarial large deltas + malformed bars.
  - Evidence: `artifacts/.../ft_reconstruction_fidelity.json`.
- FT-C004 (P@10 >= 0.85)
  - Falsify first: confusion set with near-miss templates.
  - Evidence: `artifacts/.../ft_pattern_search_eval.json`.
- FT-C005 (Latency < 100 ms)
  - Falsify first: 10-year corpus, single-core, repeated runs.
  - Evidence: `artifacts/.../ft_query_latency_benchmark.json`.
- FT-C006 (DB roundtrip bit-consistent)
  - Falsify first: corruption/reorder fault injection.
  - Evidence: `artifacts/.../ft_db_roundtrip_results.json`.

## Appendix B Traceability Plan (Predeclared)
1. Gorilla TSC comparator
   - Primary: install/open-source Gorilla implementation benchmark.
   - Fallback: zstd+lz4+zlib + documented inability to execute Gorilla.
   - Impact: incumbent comparability reduced if Gorilla absent.
2. `time_series_compression` comparator
   - Primary: run `time_series_compression` methods on same corpus.
   - Fallback: internal SAX/PAA proxy if install fails.
3. FinTSB benchmark
   - Primary: use FinTSB taxonomy patterns for evaluation categories.
   - Fallback: local canonical taxonomy with explicit mapping notes.
4. Polygon.io or equivalent feed
   - Primary: Polygon API ingestion.
   - Fallback: yfinance/Stooq equivalent with equivalence notes.
5. KDB-X or equivalent DB corpus
   - Primary: TSBS/KDB-X published workload where available.
   - Fallback: deterministic synthetic TSBS-like workload.
6. Zipline-Reloaded integration smoke
   - Primary: install zipline-reloaded and run minimal feed smoke test.
   - Fallback: adapter contract test without runtime install.
7. ACD, NeaTS, PLUTUS outcomes as design deltas
   - Primary: map design choices and measured deltas in innovation report.

## Command Ledger (Master)
- Gate A/B/C/D/E commands logged to `artifacts/2026-02-20_zpe_ft_wave1/command_log.txt`.
- Each command entry: timestamp, gate, command, exit code, summary.

## Fail Signatures
- Any uncaught crash in malformed/adversarial tests.
- Determinism hash divergence across 5 replays.
- Claim threshold miss.
- DB encode/decode hash mismatch.

## Rollback Path
- Keep gate snapshots in git working tree checkpoints and artifact snapshots.
- On gate failure:
  1. Patch only failing component.
  2. Re-run failed gate.
  3. Re-run all downstream gates.
  4. Update claim status only with new evidence file paths.

## Fallback Plan
- Dependency failures trigger nearest viable substitute with logged signature + comparability impact.
- No threshold relaxation.
- Claims remain `INCONCLUSIVE` when substitution equivalence is unproven.

## 2026-02-21 Maximalization + NET-NEW Extension (Additive)

### Environment Bootstrap Status
- `set -a; [ -f .env ] && source .env; set +a` executed.
- Current status: `.env` present but contains at least one malformed/unescaped value with spaces causing parse failure.
- Action: record blocker in `impracticality_decisions.json` and `max_resource_validation_log.md`; continue with non-secret-compatible paths.

### Additional Gate Order (After Gate E)
6. Gate M1: direct Gorilla comparator harness + parity table.
7. Gate M2: non-SQLite DB/random-access benchmark on TSBS/KDB-X style workload.
8. Gate M3: Zipline ingestion roundtrip with schema fidelity checks.
9. Gate M4: compliance-mode reproducibility tests.
10. Gate E-INGEST: Appendix E ingestion + attempt-all evidence + gap closure contract.

### Appendix E Attempt-All Resource Plan
- E3-R1 TSBS
  - Attempt: clone/generate/load TSBS dataset and run throughput/latency evaluation.
  - Artifact: `max_resource_validation_log.md`, `external_comparator_table.csv`, `net_new_gap_closure_matrix.json`.
- E3-R2 Gorilla BFCL harness
  - Attempt: clone and execute direct Gorilla comparator scripts/harness.
  - Artifact: `gorilla_eval_results.json`, `external_comparator_table.csv`.
- E3-R3 Zipline-Reloaded
  - Attempt: install/import and execute roundtrip feed harness.
  - Artifact: `max_resource_validation_log.md`, `net_new_gap_closure_matrix.json`.
- E3-R4 TRADES diffusion market sim
  - Attempt: locate runnable code/resource; if absent, log impracticality with required code.
  - Artifact: `impracticality_decisions.json`, `net_new_gap_closure_matrix.json`.

### Impracticality Policy (Strict)
- Allowed only: `IMP-LICENSE`, `IMP-ACCESS`, `IMP-COMPUTE`, `IMP-STORAGE`, `IMP-NOCODE`.
- Every IMP entry must include:
  - command evidence
  - raw error signature
  - fallback substitution
  - claim-impact note (`PASS`/`INCONCLUSIVE` implications)

### NET-NEW Mandatory Artifacts
- `max_resource_lock.json`
- `max_resource_validation_log.md`
- `max_claim_resource_map.json`
- `impracticality_decisions.json`
- `external_comparator_table.csv`
- `gorilla_eval_results.json`
- `runpod_readiness_manifest.json` (required when any `IMP-COMPUTE`)
- `net_new_gap_closure_matrix.json`

### Additional Fail Signatures
- Missing any Appendix E mandatory artifact.
- Any E3 resource not attempted and not backed by valid `IMP-*` evidence.
- FT-C003/FT-C006 lacking external comparator outputs (E-G2).
- TSBS throughput/latency evidence missing for FT-C005 (E-G3).

### Additional Rollback
- If M/E gate fails:
  1. preserve failed artifact snapshots,
  2. patch only failing maximalization path,
  3. rerun failed maximalization gate + downstream maximalization gates,
  4. refresh claim and gap-closure artifacts.

## 2026-02-21 Final-Phase Closure Addendum (Appendix F)

### Closure Artifact Root
- `artifacts/2026-02-21_zpe_ft_wave1_final/`

### Final-Phase Gate Queue (Hard Order)
1. F-G1: TSBS throughput/latency evidence present and schema-valid.
2. F-G2: `FT-C005` adjudicated as `PASS` or explicit `FAIL` (never unresolved without `IMP-*`).
3. F-G3: portability failures resolved or retained with explicit impact trace.

### Final-Phase Command Ledger (Predeclared)
1. `python3 scripts/run_gate_m2_tsbs_db.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220`
2. `python3 scripts/run_appendix_e_ingestion.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220 --phase full`
3. `python3 scripts/build_handoff_artifacts.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220`
4. `python3 scripts/run_wave1.py --artifact-root artifacts/2026-02-21_zpe_ft_wave1_final --seed 20260220` (full rerun for closure-quality reproducibility)

### Commercialization Adjudication Rule
- If only non-commercial/restricted assets exist and no commercial-safe open alternative is available, dependent claims are marked `PAUSED_EXTERNAL`.
- Evidence requirements:
  - license/provenance artifact path,
  - attempted commercial-safe alternative artifact path,
  - explicit claim-impact map in `claim_status_delta.md`.

### Final-Phase Expected Outputs
- Core: `handoff_manifest.json`, `before_after_metrics.json`, `falsification_results.md`, `claim_status_delta.md`, `command_log.txt`, `quality_gate_scorecard.json`.
- NET-NEW: `net_new_gap_closure_matrix.json`, `impracticality_decisions.json`, `max_resource_validation_log.md`, `max_claim_resource_map.json`.
- RunPod (if any `IMP-COMPUTE`): `runpod_readiness_manifest.json`, `runpod_exec_plan.md`.

### Final-Phase Fail Signatures
- `E-G3` false due missing/invalid TSBS throughput-latency proof.
- Any core claim left `INCONCLUSIVE` without explicit `IMP-*` reason.
- Any commercialization-blocked claim not marked `PAUSED_EXTERNAL` with evidence.

### Final-Phase Rollback
1. Patch only failing closure script.
2. Rerun failing gate + downstream (`F-G1` -> `F-G3`).
3. Rebuild handoff contract and regenerate scorecard.
