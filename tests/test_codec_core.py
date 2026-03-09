import numpy as np

from zpe_finance.codec import decode_ohlcv, decode_ticks, encode_ohlcv, encode_ticks
from zpe_finance.data import generate_ohlcv_bars, generate_tick_stream
from zpe_finance.metrics import rmse_ticks
from zpe_finance.rust_bridge import pack_nibbles, unpack_nibbles


def test_nibble_pack_unpack_roundtrip():
    values = [0, 1, 2, 3, 14, 15, 9, 4, 6]
    packed = pack_nibbles(values)
    unpacked = unpack_nibbles(packed, len(values))
    assert unpacked == values


def test_ohlcv_encode_decode_fidelity():
    bars = generate_ohlcv_bars(num_bars=5000, seed=20260220, tick_size=0.01)
    payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
    decoded = decode_ohlcv(payload)

    rmse = rmse_ticks(
        np.rint(bars["close"] / 0.01),
        np.rint(decoded["close"] / 0.01),
    )
    assert rmse <= 0.5
    assert len(payload) < len(bars["close"]) * 48


def test_tick_encode_decode_fidelity():
    ticks = generate_tick_stream(num_ticks=10000, seed=20260220, tick_size=0.0001)
    payload = encode_ticks(ticks, tick_size=0.0001, instrument="EURUSD")
    decoded = decode_ticks(payload)

    rmse = rmse_ticks(
        np.rint(ticks["bid"] / 0.0001),
        np.rint(decoded["bid"] / 0.0001),
    )
    assert rmse <= 0.5
