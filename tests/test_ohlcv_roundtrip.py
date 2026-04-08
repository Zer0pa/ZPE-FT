from pathlib import Path

import numpy as np

from zpe_finance.codec import decode_ohlcv, encode_ohlcv, raw_bytes_ohlcv
from zpe_finance.corpus import SeriesSpec, load_series_from_spec
from zpe_finance.metrics import rmse_ticks


def test_real_ohlcv_roundtrip_on_repo_dataset():
    repo_root = Path(__file__).resolve().parents[1]
    spec = SeriesSpec(
        series_id="spy_daily_roundtrip",
        kind="ohlcv",
        source_path=repo_root / "data" / "ohlcv" / "spy_1d_24m.csv.gz",
        symbol="SPY",
        tick_size=0.01,
        provenance="repo-bundled public OHLCV sample",
        license_note="public market sample",
        timestamp_format="iso8601",
        columns={
            "timestamp": "timestamp",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        },
    )
    bars = load_series_from_spec(spec)
    payload = encode_ohlcv(bars, tick_size=0.01, instrument="SPY")
    decoded = decode_ohlcv(payload)

    rmse = rmse_ticks(
        np.rint(bars["close"] / 0.01),
        np.rint(decoded["close"] / 0.01),
    )
    assert rmse <= 0.5
    assert len(payload) < raw_bytes_ohlcv(len(bars["timestamp"]))
