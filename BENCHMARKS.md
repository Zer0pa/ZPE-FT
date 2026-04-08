# Benchmarks

## Methodology

Benchmarks in this repo must be run on real public datasets or on retained
proof artifacts already committed to the repo. No README or benchmark table
entry should appear here unless it can be traced to:

1. A committed script or example command.
2. A committed dataset source path or public dataset URL.
3. A retained artifact or console log produced by that run.

All ratio figures use the repo's declared raw baselines:

- OHLCV: `raw_bytes_ohlcv(count)` from [python/zpe_finance/codec.py](python/zpe_finance/codec.py)
- Tick: `raw_bytes_tick(count)` from [python/zpe_finance/codec.py](python/zpe_finance/codec.py)

Comparator baselines are run against the same decoded numeric series using
committed repo code. Phase 3 populates the table below with executed results.

## Planned Inputs

- Yahoo Finance daily and provider-max 1-minute OHLCV exports already staged in `data/ohlcv/`
- Dukascopy top-of-book proxy exports already staged in `data/ticks/`
- Binance public market data fetched during Phase 3

## Result Table

| dataset | baseline | zpe | ratio | improvement |
|---|---|---|---|---|
| pending phase 3 run | pending | pending | pending | pending |
