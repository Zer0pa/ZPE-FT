> Retained context copy for the March 21 blocker packet. Original machine-local
> paths are intentionally preserved in this copied reference; do not treat this
> file as the current public instruction surface for the repo.

# Real Market Attack Plan

## Real-Market Corpus To Freeze Next

Freeze two corpora under one declared open-access or commercially safe permission envelope. Do not use vague public data with unclear provenance. Use reusable or commercially safe market-data sources with explicit benchmarking rights.

### RM-01 OHLCV Corpus
- 24 months
- 1-minute bars
- 30 liquid US symbols:
  - `SPY`, `QQQ`
  - 10 liquid mega-cap equities
  - 10 liquid financials / futures proxies
  - 8 liquid sector or index ETFs
- Required freeze fields:
  - schema
  - timezone rules
  - adjustment policy
  - content hash
  - provenance
  - licensing note

### RM-02 Tick Corpus
- 20 full sessions
- top-of-book ticks
- 3 liquid instruments:
  - one US equity
  - one index future
  - one FX pair
- Required freeze fields:
  - feed type
  - tick-size regime
  - event schema
  - content hash
  - provenance
  - licensing note

The point of the freeze is not dataset size theater. The point is commercial representativeness plus legal cleanliness.

## Exact Incumbent-Workflow Workload

`Query by example over historical price action`

Given a user-selected motif window of `32-128` points from real OHLCV or tick history:
- search the frozen corpus for top-k similar historical segments
- return ranked matches interactively
- replay those matched spans back into the current analysis workflow

Primary jobs:
- quant research pattern mining
- retrospective surveillance review
- event study setup
- backtest dataset curation

This is the workload. Not raw ingest bragging. Not generic SQL benchmarks. Not “fast database” rhetoric.

## Exact Comparison Protocol

### Candidate
- `sidecar-accelerator` backed by `zpe-finance`
- `.zpfin` archive path enabled
- compressed-space motif index/query path enabled

### Baseline A
- Raw Parquet or raw feed export
- current Python/DuckDB/Arrow full-scan motif workflow

### Baseline B
- Current operational store
  - QuestDB, ClickHouse, Tiger/Timescale, or kdb-class platform
- using the actual current query/export path for motif retrieval or nearest equivalent brute-force window scan

### Fixed Conditions
- Same corpus
- Same query catalog
- Same hardware class
- same single-core interactive search measurement for the primary query path
- same replay/export destination

### Query Catalog
- 50 motif queries
- mix of:
  - breakout continuation
  - bull/bear flag
  - double bottom / double top
  - head-and-shoulders style reversal
  - gap continuation / gap failure
  - intraday microstructure motifs on ticks

### Metrics
- `p50` and `p95` motif-query latency
- storage footprint
- bytes scanned per query or equivalent query CPU-time
- `P@10` or analyst-audited match acceptance rate
- replay/export wall-clock
- reconstruction RMSE / exactness
- integration friction:
  - required schema changes
  - required primary-store replacement
  - operational steps added

## Exact Kill Condition
Kill the sidecar-first thesis for the pilot if any of the following happen:

1. `P@10 < 0.85` on the frozen real-market query catalog.
2. Any replay/fidelity guardrail regresses below current frozen standards.
3. Query p95 is less than `10x` better than Baseline A.
4. Storage improvement is less than `10x` versus raw float/tick storage.
5. The sidecar requires replacing the incumbent primary storage system instead of attaching beside it.
6. The incumbent platform plus existing workflow already closes the same motif workload within the same order of magnitude.

If one of these happens, stop the market story. Do not narrate a partial win.

## Exact Success Condition
Success requires all of the following on the frozen real-market corpus:

1. Motif-query `p95` at least `10x` better than Baseline A.
2. Archive footprint at least `10x` lower than raw float/tick storage.
3. `P@10 >= 0.85` or equivalent audited analyst acceptance.
4. Exact replay or `<= 0.5` tick RMSE with no silent degradation.
5. One real sidecar integration path stays non-regressive.
6. The user can keep the incumbent store and add ZPE as a sidecar, not a replacement.

## What To Run Immediately After Freeze
1. Reproduce the carried narrow metrics on RM-01 and RM-02.
2. Run the motif query catalog against Baseline A, Baseline B, and the sidecar.
3. Export top-k matched spans into the existing notebook/backtest/surveillance path.
4. Decide go/no-go from the kill and success conditions above.

## Strategic Note
If the sidecar wins, then adapter work becomes justified.

If the sidecar does not win, adapter work is not rescue. It is scope escape.
