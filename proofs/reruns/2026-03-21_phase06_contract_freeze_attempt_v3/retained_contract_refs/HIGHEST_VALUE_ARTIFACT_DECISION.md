> Retained context copy for the March 21 blocker packet. Original machine-local
> paths are intentionally preserved in this copied reference; do not treat this
> file as the current public instruction surface for the repo.

# Highest Value Artifact Decision

## Chosen Artifact
`sidecar-accelerator`

Sharpened definition:

A finance-native compressed motif-query and archive sidecar that plugs into an existing market-data workflow and exposes:
- archive to `.zpfin`
- exact replay
- compressed-space motif retrieval
- export of matched spans back into the buyer's existing research or surveillance stack

Internals:
- `zpe-finance` is the engine.
- `.zpfin` is the archive/transport contract.
- `pattern-library` is the retrieval primitive.

## User
- Quant research platform teams
- Market surveillance / market-abuse analytics teams
- Historical market-data engineering teams
- Backtesting and signal-research teams already operating on QuestDB, ClickHouse, Tiger/Timescale, raw Parquet, or kdb-class stacks

## Insertion Point
- After feed landing and normalization
- Beside the buyer's current TSDB or lakehouse, not instead of it
- Before backtesting, surveillance review, or motif-mining workflows

Concrete insertion points:
- sidecar index over historical OHLCV or tick archives
- export/replay bridge into existing notebooks, backtest jobs, or surveillance jobs
- cold-storage archive path for high-volume market data

## Exact Incumbent Behavior It Beats
It does not beat incumbent write-heavy TSDB platforms at being full databases.

It beats this exact incumbent workflow:

`store raw market data -> run SQL/Python full scans or ad hoc analytics jobs to find recurring price motifs -> export matching windows into downstream analysis`

That incumbent workflow is slow, scan-heavy, and storage-heavy.

## Why The Beat Matters Commercially
- It avoids rip-and-replace.
- It targets a pain buyers already pay for: archive cost plus slow retrospective pattern retrieval.
- It creates immediate value inside existing stacks rather than asking the buyer to adopt a new primary database.
- It converts the one real differentiated capability in the current evidence surface, compressed-space finance motif retrieval, into a directly purchasable surface.

## What “Order-of-Magnitude Better” Means Here
For this artifact, “order-of-magnitude better” is not vague. It means all of the following on the frozen real-market workload:

1. Motif-query p95 latency at least `10x` better than the buyer's raw-scan baseline.
2. Archive storage footprint at least `10x` better than raw float/tick storage.
3. Query bytes scanned or equivalent CPU-time per motif search at least `10x` lower than the raw baseline.
4. No regression on exact replay / bounded-lossless fidelity guardrails.

If those conditions are not met, this is not a winning artifact. It is just an interesting codec.

## Why This Wins Over The Other Candidate Surfaces
- Better than transport-first: buyers do not need a new format as the first purchasing decision.
- Better than adapter-first: adapters inherit incumbent platform battles before the differentiated workload is proven.
- Better than model-bridge-first: that lane is farther from current proof and closer to enterprise theater.
- Better than TSDB-replacement rhetoric: current incumbents are already too strong on platform breadth.

## Strategic Consequence
The correct sequence is:

`kernel -> sidecar win -> adapter expansion if demanded`

Not:

`kernel -> database replacement claim -> adapter scramble -> model bridge story`

## Evidence Base
- Local: `PRD_ZPE_FT.md`
- Local: `/Users/Zer0pa/ZPE/Zer0pa PRD & Research/ZPE FT/output/market_landscape_decision_note.md`
- Local: `/Users/Zer0pa/ZPE/ZPE FT/artifacts/2026-02-21_zpe_ft_wave1_final/zipline_roundtrip_results.json`
- Local: `/Users/Zer0pa/ZPE/ZPE FT/artifacts/2026-02-21_zpe_ft_wave1_final/ft_query_latency_benchmark.json`
- Local: `/Users/Zer0pa/ZPE/ZPE FT/artifacts/2026-02-21_zpe_ft_wave1_final/ft_db_roundtrip_results.json`
- Official: [QuestDB capital markets](https://questdb.com/industries/capital-markets/)
- Official: [ClickHouse time-series guide](https://clickhouse.com/resources/engineering/what-is-time-series-database)
- Official: [KDB-X overview](https://docs.kx.com/latest/kdb-x/Get_Started/kdb-x-overview.htm)
- Official: [KDB-X temporal similarity search](https://docs.kx.com/public-preview/kdb-x/integrations/ai-libraries-tss.htm)
