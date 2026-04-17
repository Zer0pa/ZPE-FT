# ZPE-FT Novelty Card

**Product:** ZPE-FT  
**Domain:** Delayed-feed OHLCV and top-of-book tick archives for bounded market-data workflows.  
**What we sell:** Smaller market-data archives that still replay deterministically and can be searched without first inflating them into warehouse tables.

## Novel contributions

1. **Market-structure nibble codec** — ZPE-FT encodes OHLCV bars and top-of-book ticks as five-channel market deltas, keeps price-path structure explicit, and spills rare larger moves into a separate overflow stream. The codec is organized around market invariants such as prior-close deltas, high/low excess, bid/ask deltas, and separate volume-size quantization. Code: [`python/zpe_finance/codec.py`](../../../python/zpe_finance/codec.py). Relevant lines: `99-163`, `231-293`. Nearest prior art (if known): generic delta codecs, Gorilla-style time-series compression, unsigned/signed varint packing. What is genuinely new here: the lane-specific channelization for financial bars and ticks, with deterministic replay and explicit separation between promoted price-field fidelity and separately quantized volume channels.
2. **`.zpfin` replay contract** — The codec is bound to a repo-native packet format that carries tick size, base tick, base timestamp, interval, nibble count, overflow lengths, an instrument hash, and CRC-checked payload boundaries. Code: [`python/zpe_finance/packet.py`](../../../python/zpe_finance/packet.py). Relevant lines: `9-45`. Nearest prior art (if known): framed binary containers with CRC integrity checks. What is genuinely new here: the FT-specific replay contract that keeps archive payloads deterministic and self-describing for delayed-feed bar and tick lanes.
3. **Archive-native motif search surface** — ZPE-FT exposes exact and approximate pattern search directly over encoded token streams instead of positioning search as a separate warehouse-only step. Code: [`python/zpe_finance/search.py`](../../../python/zpe_finance/search.py). Relevant lines: `19-70`. Nearest prior art (if known): exact subsequence search, k-gram indexes, approximate window scoring. What is genuinely new here: the product packaging of motif retrieval with the codec and replay surface for bounded financial archive workflows.

## Standard techniques used (explicit, not novel)

- delta encoding
- ZigZag integer coding
- unsigned varints
- nibble packing
- CRC32 packet integrity checks
- k-gram indexing
- exact subsequence search
- NumPy vectorized array handling

## Compass-8 / 8-primitive architecture

NO — FT uses price/timestamp delta channels, nibble-plus-overflow packing, and a `.zpfin` packet contract instead of a directional Compass-8 encoder. Code references: [`python/zpe_finance/codec.py`](../../../python/zpe_finance/codec.py) and [`python/zpe_finance/packet.py`](../../../python/zpe_finance/packet.py).

## Open novelty questions for the license agent

- Should the archive-native motif search surface be scheduled as protectable novelty, or treated as product integration of known subsequence and k-gram methods over the codec?
- Should the `.zpfin` replay contract be scheduled as separate novelty, or treated as the container boundary that supports the codec claims rather than a standalone invention?
