# Architecture

ZPE-FT currently has four main layers.

## Package Layer

- `python/zpe_finance/codec.py`: OHLCV and tick encoding/decoding
- `python/zpe_finance/packet.py`: packet framing
- `python/zpe_finance/search.py`: exact and approximate pattern search
- `python/zpe_finance/db_adapter.py`: DB-facing roundtrip logic

## Native Layer

- `core/src/lib.rs`: nibble packing, unpacking, subsequence search, and hashing helpers exposed through PyO3
- `python/zpe_finance/rust_bridge.py`: runtime bridge with deterministic Python fallback

## Execution Layer

- `scripts/run_wave1.py`: gate runner
- `scripts/run_gate_*.py`: gate-specific proof generation

## Proof Layer

- `proofs/artifacts/2026-02-21_ft_wave1_final/`: selected Wave-1 final evidence
- `proofs/reruns/`: deferred rerun evidence and unresolved external-compute surfaces
- `proofs/runbooks/`: historical operator runbooks kept for lineage, not current front-door instructions

