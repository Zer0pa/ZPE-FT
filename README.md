# ZPE-FT

> Product-page mirror for `/encoding/ZPE-FT/`.
> Live public repo: [Zer0pa/ZPE-FT](https://github.com/Zer0pa/ZPE-FT).
> GitHub Markdown cannot reproduce the website typography, CSS, JavaScript, scroll behavior, or live bento layout; this README translates the product page into GitHub-safe Markdown evidence blocks.

## 0. Install / Developer Commands

The product page is the positioning authority. This section is the only retained developer-surface material from the previous root README.

```bash
Financial tick-stream encoding. Bounded proof surface for trade-tape replay, missing-input blockers, and auditable FT-C004 truth. Install from PyPI: `pip install zpe-ft
pip install zpe-ft
git clone https://github.com/Zer0pa/ZPE-FT.git
python -m pip install -U pip
python -m pip install -e .
```

## Product Page Mirror

**Product-page title:** ZPE-FT · Public market replay on delayed feeds · Zer0pa

**Product-page description:** ZPE-FT · bounded public market replay on delayed feeds · SPY 5.94x, BTC 10.90x, Kaggle 7.31x compression with price-field RMSE 0.0 on reported fields · Phase 06 inputs pending · PyPI v0.1.1

### Hero Translation

> 00 · ZPE-FT · FINANCIAL TIME-SERIESDEVELOPER-READY · PHASE 06 PENDING Self-Aware Market Data A compression codec for delayed-feed market archives — compact, exact, queryable · ZPE-FT · PyPI zpe-ft v0.1.1 · github.com/Zer0pa/ZPE-FT Market archives store rows well. They rarely retain the price pattern. Finding a six-month-old chart shape today means rebuilding from scratch, not retrieving. ZPE-FT compresses delayed and public feeds 5.9–10.9× smaller than raw, replays price fields at RMSE = 0.0, and runs OHLCV pattern queries up to 62.9× faster than Parquet+zstd through DuckDB. The public-corpus result is real. The enterprise benchmark still waits on Phase 06 inputs and FT-C004 labels.

## Positioning

| Field | Value |
| --- | --- |
| Section | encoding |
| Product route | /encoding/ZPE-FT/ |
| Live public repository | https://github.com/Zer0pa/ZPE-FT |
| Repo identity used here | ZPE-FT |
| Website display identity | ZPE-FT |
| Verdict | BLOCKED |
| Posture | always_in_beta |
| Headline metric | Public benchmark (3 datasets, parquet+zstd+DuckDB baseline): 5.9–10.9× smaller than raw; up to 62.9× faster pattern query vs DuckDB; exact tick fidelity (RMSE = 0.0). |
| Honest blocker | No Phase 06 closure or public release readiness; No broad warehouse or incumbent displacement claim; No lossless volume reconstruction claim; No promoted public-data search-quality claim while FT-C004 remains unresolved; No claim that the bounded proxy lanes satisfy the sovereign enterprise benchmark. |
| Mechanics asset from product page | FT.gif |

## Key Metrics

| Metric | Value | Baseline |
| --- | --- | --- |
| SPY 10y daily compression ratio vs raw | 5.94× smaller | Raw OHLCV bytes |
| Price-field reconstruction fidelity | RMSE = 0.0 ticks (exact) | Parquet lossless round-trip |
| Pattern query latency vs DuckDB (OHLCV) | 62.9× faster (0.70 ms vs 43.9 ms p95) | parquet+zstd+DuckDB |
| 30-symbol 24-month corpus fidelity | 0.0 RMSE across all 30 series, 15,000 corpus points | Alpaca daily bars, in-repo proxy lane |

## Proof Anchors

| Path | State |
| --- | --- |
| proofs/artifacts/public_benchmarks/phase3_public_benchmarks.json | VERIFIED |
| proofs/reruns/2026-03-19_alpaca_demo_smoke/ft_reconstruction_fidelity.json | VERIFIED |
| proofs/artifacts/real_market_benchmarks/BOUNDARY.json | VERIFIED |
| proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json | VERIFIED |
| proofs/phase06_inputs/series_gap_matrix.csv | VERIFIED |

## What We Prove

- Public benchmark artifacts are retained for Yahoo SPY, Binance BTCUSDT aggTrades, and Kaggle SPY.
- Repo-bundled OHLCV roundtrip stays within the bounded price-field error threshold and compresses below raw bytes.
- Freeze and refresh scripts execute on a declared corpus contract and emit benchmark, fidelity, latency, and roundtrip artifacts.
- Missing authority inputs keep the sovereign Phase 06 gate blocked.
- FT-C004 truth remains blocked until labels or audit refs exist.

## What We Do Not Claim

- No Phase 06 closure or public release readiness.
- No broad warehouse or incumbent displacement claim.
- No lossless volume reconstruction claim.
- No promoted public-data search-quality claim while FT-C004 remains unresolved.
- No claim that the bounded proxy lanes satisfy the sovereign enterprise benchmark.

## Blockers / Failures

> No Phase 06 closure or public release readiness; No broad warehouse or incumbent displacement claim; No lossless volume reconstruction claim; No promoted public-data search-quality claim while FT-C004 remains unresolved; No claim that the bounded proxy lanes satisfy the sovereign enterprise benchmark.

## Verification Surface

| Code | Check | Verdict |
| --- | --- | --- |
| V_01 | Public SPY 10y daily compression | PASS |
| V_02 | Public BTCUSDT aggTrades compression | PASS |
| V_03 | Public Kaggle SPY compression | PASS |
| V_04 | Bounded replay price-field fidelity | PASS |
| V_05 | Phase 06 contract freeze | FAIL |
| V_06 | Public proxy retrieval truth | INC |

## License

| Field | Value |
| --- | --- |
| License | SAL-7.0 |
| Authority source | proofs/reruns/2026-03-21_phase06_contract_freeze_attempt_v3/missing_inputs_packet.json |

## Upcoming Workstreams

| Category | Summary |
| --- | --- |
| Research-Deferred — Investigation Underway | FT-C004 truth resolution. Open question must be diagnosed and a falsifiable claim formulated before Phase 06 enterprise benchmark work commits direction. |
| Operations / External Dependency | Phase 06 enterprise authority inputs. Authority datasets pending acquisition; engineer-side scaffolding ready. |

## Related Repos

No related repos are declared on the product page frontmatter.

<details>
<summary>Full Visible Product-Page Bento Translation</summary>

This section preserves the product page cells as Markdown text blocks. It intentionally omits shared site navigation, footer chrome, CSS, and scripts.

### Bento Cell 1

> 00 · ZPE-FT · FINANCIAL TIME-SERIESDEVELOPER-READY · PHASE 06 PENDING Self-Aware Market Data A compression codec for delayed-feed market archives — compact, exact, queryable · ZPE-FT · PyPI zpe-ft v0.1.1 · github.com/Zer0pa/ZPE-FT Market archives store rows well. They rarely retain the price pattern. Finding a six-month-old chart shape today means rebuilding from scratch, not retrieving. ZPE-FT compresses delayed and public feeds 5.9–10.9× smaller than raw, replays price fields at RMSE = 0.0, and runs OHLCV pattern queries up to 62.9× faster than Parquet+zstd through DuckDB. The public-corpus result is real. The enterprise benchmark still waits on Phase 06 inputs and FT-C004 labels.

### Bento Cell 2

> 01 · THE GAPSTORED, NOT KNOWN A market archive stores what happened. It does not remember what price did.

### Bento Cell 3

> 02 · MARKETSADJACENT FORECASTS Market data '30$52.1B Fintech analytics '30$45.6B Capital markets software '30$31.4B Time-series database '30$5.7B Financial data infrastructure '31$78.9B Capital-markets data and analytics forecasts. Every tool listed above still pays the storage and rebuild cost that ZPE-FT removes from the file itself.

### Bento Cell 4

> 03 · VALUE $78.9B Financial data infrastructure keeps growing. The storage and search bill on delayed-feed history is the line item nobody has solved.

### Bento Cell 5

> 04 · INSIGHT Encode the pattern. The archive knows its shape.

### Bento Cell 6

> 05.1 · CURRENT TECHSTORED AND REBUILT Delayed market data lives in raw CSV, Parquet+zstd, or vendor stores. Cheap to write, fast to scan. But the file holds bytes, not patterns. Asking what a price did means rebuilding the answer, not retrieving it.

### Bento Cell 7

> 05.2 · OUR TECHENCODE THE PATTERN ZPE-FT encodes pattern structure into the archive itself. Price fields replay at RMSE 0.0. OHLCV pattern queries run up to 62.9× faster than Parquet+zstd through DuckDB. SPY 10-year: 5.94× smaller. Binance BTC aggTrades: 10.90×. Kaggle SPY full history: 7.31×. Public, delayed-feed corpora only.

### Bento Cell 8

> 05.3 · BENCHMARKSDELAYED-FEED PUBLIC CORPORA SPY 10y5.94× vs raw BTC tick10.90× vs raw Kaggle SPY7.31× vs raw Price RMSE0.0reported fields SPY5.94× BTC10.90× Kaggle7.31× Status: three public corpora stand · Phase 06 enterprise benchmark and FT-C004 labels pending.

### Bento Cell 9

> 06 · MEASUREMENTPHASE3 PUBLIC BENCHMARKS Three public corpora stand. Phase 06 still needs its inputs.

### Bento Cell 10

> 06.1 · COMPARATIVE PERFORMANCE · DELAYED-FEED VS RAW SPY 10y5.94× smaller BTC aggTrades10.90× Kaggle SPY7.31× Phase 06pending Yahoo SPY 10y, Binance BTCUSDT aggTrades, Kaggle SPY full history — all delayed feed. Reported price fields replay exactly. BTC tick data wins on size but not on query speed; no latency claim is made there. Phase 06 inputs and FT-C004 truth labels remain unresolved.

### Bento Cell 11

> 07 · KEY METRICSDELAYED-FEED CORPORA

### Bento Cell 12

> 07.1 · SPY 10y 5.94× vs raw · Yahoo Finance daily

### Bento Cell 13

> 07.2 · BTC TICK 10.90× vs raw · Binance public aggTrades

### Bento Cell 14

> 07.3 · KAGGLE SPY 7.31× vs raw · Kaggle full history

### Bento Cell 15

> 07.4 · PROXY RMSE 0.0ticks price fields · public proxy corpus

### Bento Cell 16

> 07.5 · SOVEREIGN null Enterprise metric pending · Phase 06 inputs open

### Bento Cell 17

> 08 · FIDELITYPRICE FIELDS VS VOLUME Price fields replay exactly. RMSE = 0.0 decides.

### Bento Cell 18

> 08.1 · WHAT EXACT REPLAY MEANSPUBLIC PROXY SCOPE The 62.9× figure is the p95 query latency win on Yahoo SPY OHLCV versus Parquet+zstd through DuckDB. BTC aggTrades is size-positive at latency parity or slower — no latency win is claimed on tick data. Price-field RMSE = 0.0 holds on reported fields across all three public corpora. Deterministic replay is declared on public inputs with committed benchmark artifacts in the repo. Anyone with the corpora can rerun the numbers and get the same bytes. Phase 06 enterprise inputs remain missing. FT-C004 retrieval truth labels remain unresolved.

### Bento Cell 19

> 08.2 · HONEST BLOCKER Honest Blocker · Public-corpus benchmarks are not the enterprise benchmark. Phase 06 still needs 33 missing input series and unresolved FT-C004 truth labels. ZPE-FT is not a real-time feed, not a trading system, and makes no lossless volume claim. PyPI ships v0.1.1; v0.1.2 is pending.

### Bento Cell 20

> 09 FIVE FUTURES FROM ONE DELAYED-FEED ARCHIVE.

### Bento Cell 21

> 09.1 · THE AMBITION The bet is not to beat the warehouse. The bet is that a market archive can stay compact, exact, and queryable at the same time — and that when delayed-feed history behaves that way, the warehouse stops being the only place a fintech team is allowed to ask questions.

### Bento Cell 22

> 09.2 · WHAT WORKS NOW Today, on three public corpora: 5.94–10.90× compression, RMSE 0.0 on price fields, 62.9× OHLCV query win.

### Bento Cell 23

> 09.3 · WHAT'S STILL OPEN Still open: Phase 06 enterprise inputs, FT-C004 retrieval labels, the private-data benchmark, and PyPI v0.1.2.

### Bento Cell 24

> 09.4 · ARCHIVES · NEAR-TERM (12–24 MO) More history fits in the same budget A data team that cuts delayed-feed storage by six to eleven times can keep ten years of tick history where they used to keep one. The retention conversation shifts from “what do we drop” to “what do we still ask of it.”

### Bento Cell 25

> 09.5 · QUERIES · NEAR-TERM (12–24 MO) Pattern search runs on the archive An analyst hunting a price pattern from three years ago does not stage a fresh DuckDB rebuild first. The query goes against the compressed file. Backtest setup and exploratory research move from hours of preparation toward a single command.

### Bento Cell 26

> 09.6 · FIDELITY · MID-TERM (24–48 MO) Every price still matches exactly A compliance reviewer who asks whether the archived close equals the source close gets a zero-difference answer on reported price fields. Compaction stops carrying the usual quiet trust tax, which makes long-horizon market archives easier to defend.

### Bento Cell 27

> 09.7 · TRUTH · MID-TERM (24–48 MO) Retrieval claims wait for labels The pending FT-C004 label set is the gate that decides whether “we found this pattern” is allowed to graduate into a product feature. Buyers see retrieval evaluated against a fixed reference, not against the vendor’s own examples.

### Bento Cell 28

> 09.8 · PARADIGM · PARADIGM (48 MO+) Market archives become query-native If exact replay and low-latency search stay coupled once enterprise data joins the picture, delayed-feed history stops being cold storage that warehouses must rebuild from. It becomes the searchable layer that fintech analytics sits on top of.

</details>

---

Source mapping: product route `/encoding/ZPE-FT/` -> live public repo `Zer0pa/ZPE-FT`. README generated from product-page authority plus retained install/dev commands only.
