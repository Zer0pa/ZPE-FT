from pathlib import Path

from zpe_finance.codec import decode_ohlcv, encode_ohlcv
from zpe_finance.data import generate_ohlcv_bars
from zpe_finance.db_adapter import init_db, roundtrip_packet


def test_sqlite_roundtrip_bit_consistency(tmp_path: Path):
    bars = generate_ohlcv_bars(num_bars=4000, seed=20260220, tick_size=0.01)
    payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")

    conn = init_db(tmp_path / "rt.sqlite3")
    rt = roundtrip_packet(conn, "series", payload)
    conn.close()

    assert rt["bit_consistent"] is True
    dec = decode_ohlcv(payload)
    assert len(dec["close"]) == len(bars["close"])
