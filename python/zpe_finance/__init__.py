"""ZPE finance codec package."""

from .alpaca import AlpacaClient, build_generated_corpus_spec, load_alpaca_corpus_request
from .codec import (
    decode_ohlcv,
    decode_ticks,
    encode_ohlcv,
    encode_ticks,
    raw_bytes_ohlcv,
    raw_bytes_tick,
)
from .corpus import load_corpus_config, load_series_from_manifest_entry, load_series_from_spec
from .data import generate_ohlcv_bars, generate_tick_stream, try_fetch_equivalent_market_bars
from .search import PatternIndex

__all__ = [
    "AlpacaClient",
    "load_alpaca_corpus_request",
    "build_generated_corpus_spec",
    "encode_ohlcv",
    "decode_ohlcv",
    "encode_ticks",
    "decode_ticks",
    "raw_bytes_ohlcv",
    "raw_bytes_tick",
    "generate_ohlcv_bars",
    "generate_tick_stream",
    "try_fetch_equivalent_market_bars",
    "load_corpus_config",
    "load_series_from_spec",
    "load_series_from_manifest_entry",
    "PatternIndex",
]
