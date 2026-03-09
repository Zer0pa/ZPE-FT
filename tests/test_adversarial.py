import numpy as np
import pytest

from zpe_finance.codec import decode_ohlcv, encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream
from zpe_finance.db_adapter import fault_inject_corruption


def test_reject_nan_bars():
    bars = generate_ohlcv_bars(num_bars=2000, seed=42, tick_size=0.01)
    bars["close"][123] = np.nan
    with pytest.raises(ValueError):
        encode_ohlcv(bars, tick_size=0.01)


def test_reject_ask_below_bid():
    ticks = generate_tick_stream(num_ticks=2000, seed=42, tick_size=0.0001)
    ticks["ask"][10] = ticks["bid"][10] - 0.0002
    with pytest.raises(ValueError):
        encode_ticks(ticks, tick_size=0.0001)


def test_corruption_detected_by_crc():
    bars = generate_ohlcv_bars(num_bars=2000, seed=7, tick_size=0.01)
    payload = encode_ohlcv(bars, tick_size=0.01)
    corrupted = fault_inject_corruption(payload)
    with pytest.raises(ValueError):
        decode_ohlcv(corrupted)
