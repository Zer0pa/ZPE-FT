# Phase 06 Tick Proxy Lane

This directory carries bounded Dukascopy top-of-book proxy slices for the public rehearsal lane.

## What Is Here

- `eurusd_dukascopy_tick_20d_1h.csv.gz`: 20 weekday overlap-window slices for `EUR/USD`.
- `aapl_dukascopy_tick_20d_1h.csv.gz`: 20 weekday overlap-window slices for `AAPL.US/USD`.
- `e-sandp-500_dukascopy_tick_20d_1h.csv.gz`: 20 weekday overlap-window slices for `E_SandP-500`.

## Boundary

- These files are non-authority proxy inputs for A3/A4 only.
- They do not replace the sovereign contract requirement for the exact authority pack under `proofs/phase06_inputs/ticks/`.
- `AAPL.US/USD` is not NBBO and `E_SandP-500` is not `ES1` futures top-of-book.

## Current Status

- `eurusd_dukascopy_tick_20d_1h`: status `reused`, rows `192859`, sessions `20/20`.
- `aapl_dukascopy_tick_20d_1h`: status `reused`, rows `224292`, sessions `20/20`.
- `e_sandp_500_dukascopy_tick_20d_1h`: status `reused`, rows `189766`, sessions `20/20`.

Generated: `2026-04-06T17:23:59.284469+00:00`
