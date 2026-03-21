from pathlib import Path

from zpe_finance.alpaca import (
    AlpacaClient,
    build_generated_corpus_spec,
    load_alpaca_corpus_request,
    write_alpaca_bar_csv,
    write_alpaca_quote_csv,
)
from zpe_finance.corpus import load_series_from_spec, series_spec_from_dict


def test_alpaca_client_paginates_and_generates_corpus_spec(tmp_path: Path):
    pages = {
        ("/v2/stocks/bars", ""): {
            "bars": {
                "SPY": [
                    {"t": "2026-03-17T13:30:00Z", "o": 560.1, "h": 560.4, "l": 559.9, "c": 560.2, "v": 1000},
                ]
            },
            "next_page_token": "bars-2",
        },
        ("/v2/stocks/bars", "bars-2"): {
            "bars": {
                "SPY": [
                    {"t": "2026-03-17T13:31:00Z", "o": 560.2, "h": 560.5, "l": 560.0, "c": 560.3, "v": 1200},
                ]
            },
            "next_page_token": None,
        },
        ("/v2/stocks/quotes", ""): {
            "quotes": {
                "AAPL": [
                    {"t": "2026-03-17T13:30:00.001000000Z", "bp": 240.16, "ap": 240.18, "bs": 100, "as": 200},
                ]
            },
            "next_page_token": "quotes-2",
        },
        ("/v2/stocks/quotes", "quotes-2"): {
            "quotes": {
                "AAPL": [
                    {"t": "2026-03-17T13:30:00.001500000Z", "bp": 240.17, "ap": 240.19, "bs": 100, "as": 100},
                ]
            },
            "next_page_token": None,
        },
    }

    def fake_transport(path, params):
        return pages[(path, str(params.get("page_token", "")))]

    client = AlpacaClient("key", "secret", transport=fake_transport)
    bars = client.get_stock_bars(
        symbol="SPY",
        timeframe="1Min",
        start="2026-03-17T13:30:00Z",
        end="2026-03-17T13:32:00Z",
    )
    quotes = client.get_stock_quotes(
        symbol="AAPL",
        start="2026-03-17T13:30:00Z",
        end="2026-03-17T13:30:10Z",
    )

    bars_path = tmp_path / "spy_bars.csv"
    quotes_path = tmp_path / "aapl_quotes.csv"
    assert write_alpaca_bar_csv(bars_path, bars) == 2
    assert write_alpaca_quote_csv(quotes_path, quotes) == 2

    config_path = tmp_path / "alpaca_config.json"
    config_path.write_text(
        """
{
  "corpus_id": "alpaca_test",
  "dataset_dir": "alpaca_exports",
  "series": [
    {
      "series_id": "spy_1m",
      "kind": "ohlcv",
      "symbol": "SPY",
      "tick_size": 0.01,
      "start": "2026-03-17T13:30:00Z",
      "end": "2026-03-17T13:32:00Z",
      "provenance": "test bars",
      "license_note": "test-only"
    },
    {
      "series_id": "aapl_quotes",
      "kind": "tick",
      "symbol": "AAPL",
      "tick_size": 0.01,
      "start": "2026-03-17T13:30:00Z",
      "end": "2026-03-17T13:30:10Z",
      "provenance": "test quotes",
      "license_note": "test-only"
    }
  ]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )

    config, requests, dataset_dir = load_alpaca_corpus_request(config_path)
    assert dataset_dir == (tmp_path / "alpaca_exports").resolve()
    generated = build_generated_corpus_spec(
        config,
        requests,
        {
            "spy_1m": bars_path,
            "aapl_quotes": quotes_path,
        },
    )
    assert generated["corpus_id"] == "alpaca_test"
    assert generated["series"][0]["timestamp_format"] == "epoch_ms"
    assert generated["series"][1]["timestamp_format"] == "epoch_ns"
    assert generated["series"][1]["columns"]["bid"] == "bid_px"


def test_epoch_ns_tick_loading_preserves_sub_millisecond_precision(tmp_path: Path):
    csv_path = tmp_path / "quotes.csv"
    csv_path.write_text(
        "\n".join(
            [
                "ts,bid_px,ask_px,bid_sz,ask_sz",
                "1710682200001000000,240.16,240.18,100,200",
                "1710682200001500000,240.17,240.19,100,100",
                "1710682200002000000,240.15,240.17,200,300",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    spec = series_spec_from_dict(
        {
            "series_id": "aapl_quotes",
            "kind": "tick",
            "source_path": str(csv_path),
            "symbol": "AAPL",
            "tick_size": 0.01,
            "provenance": "test quotes",
            "license_note": "test-only",
            "timestamp_format": "epoch_ns",
            "columns": {
                "timestamp": "ts",
                "bid": "bid_px",
                "ask": "ask_px",
                "bid_size": "bid_sz",
                "ask_size": "ask_sz",
            },
        },
        tmp_path,
    )
    ticks = load_series_from_spec(spec)

    assert ticks["timestamp"].tolist() == [
        1710682200001000000,
        1710682200001500000,
        1710682200002000000,
    ]
