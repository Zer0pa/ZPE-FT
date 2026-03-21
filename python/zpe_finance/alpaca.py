"""Alpaca market-data ingestion for repo-native corpus freezes."""

from __future__ import annotations

import csv
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

JsonTransport = Callable[[str, Mapping[str, str]], Mapping[str, Any]]

SUPPORTED_ALPACA_KINDS = ("ohlcv", "tick")
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


class AlpacaAPIError(RuntimeError):
    """Raised when Alpaca returns an error response."""


@dataclass(frozen=True)
class AlpacaSeriesRequest:
    series_id: str
    kind: str
    symbol: str
    tick_size: float
    start: str
    end: str
    provenance: str
    license_note: str
    timeframe: str = "1Min"
    feed: str = "iex"
    adjustment: str = "raw"
    limit: int = 10_000


def _resolve_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else (base_dir / path).resolve()


def _coerce_int(raw: Any, field: str) -> int:
    if isinstance(raw, bool):
        raise ValueError(f"invalid integer value for {field}")
    if isinstance(raw, int):
        return raw
    text = str(raw).strip()
    if not text:
        raise ValueError(f"empty integer value for {field}")
    return int(text)


def _coerce_float(raw: Any, field: str) -> float:
    text = str(raw).strip()
    if not text:
        raise ValueError(f"empty numeric value for {field}")
    return float(text)


def _parse_rfc3339_ns(raw: str) -> int:
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    if "+" in text[10:]:
        main, offset = text.rsplit("+", 1)
        offset = f"+{offset}"
    elif "-" in text[10:]:
        main, offset = text.rsplit("-", 1)
        offset = f"-{offset}"
    else:
        main = text
        offset = "+00:00"

    if "." in main:
        base, fraction = main.split(".", 1)
    else:
        base = main
        fraction = ""

    dt = datetime.fromisoformat(f"{base}{offset}").astimezone(timezone.utc)
    delta = dt - _EPOCH
    whole_ns = (delta.days * 86_400 + delta.seconds) * 1_000_000_000
    frac_ns = int((fraction + "000000000")[:9]) if fraction else 0
    return whole_ns + frac_ns


def alpaca_series_request_from_dict(payload: Mapping[str, Any]) -> AlpacaSeriesRequest:
    required = ("series_id", "kind", "symbol", "tick_size", "start", "end", "provenance", "license_note")
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"missing Alpaca request fields: {missing}")

    kind = str(payload["kind"])
    if kind not in SUPPORTED_ALPACA_KINDS:
        raise ValueError(f"unsupported Alpaca series kind: {kind}")

    return AlpacaSeriesRequest(
        series_id=str(payload["series_id"]),
        kind=kind,
        symbol=str(payload["symbol"]),
        tick_size=float(payload["tick_size"]),
        start=str(payload["start"]),
        end=str(payload["end"]),
        provenance=str(payload["provenance"]),
        license_note=str(payload["license_note"]),
        timeframe=str(payload.get("timeframe", "1Min")),
        feed=str(payload.get("feed", "iex")),
        adjustment=str(payload.get("adjustment", "raw")),
        limit=_coerce_int(payload.get("limit", 10_000), "limit"),
    )


def load_alpaca_corpus_request(path: Path) -> tuple[dict[str, Any], list[AlpacaSeriesRequest], Path]:
    config = json.loads(path.read_text(encoding="utf-8"))
    series_payload = config.get("series", [])
    if not isinstance(series_payload, list) or not series_payload:
        raise ValueError("Alpaca config must contain a non-empty 'series' list")

    dataset_dir = _resolve_path(path.parent, str(config.get("dataset_dir", "buyer_exports/alpaca")))
    requests = [alpaca_series_request_from_dict(item) for item in series_payload]
    return config, requests, dataset_dir


class AlpacaClient:
    """Minimal Alpaca market-data client using the official REST surface."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        *,
        base_url: str = "https://data.alpaca.markets",
        timeout_sec: float = 30.0,
        transport: JsonTransport | None = None,
    ) -> None:
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret are required")
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = float(timeout_sec)
        self._transport = transport or self._request_json

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str = "https://data.alpaca.markets",
        timeout_sec: float = 30.0,
    ) -> "AlpacaClient":
        api_key = os.environ.get("ALPACA_API_KEY_ID") or os.environ.get("APCA_API_KEY_ID") or ""
        api_secret = os.environ.get("ALPACA_API_SECRET_KEY") or os.environ.get("APCA_API_SECRET_KEY") or ""
        if not api_key or not api_secret:
            raise ValueError(
                "missing Alpaca credentials: set ALPACA_API_KEY_ID/APCA_API_KEY_ID "
                "and ALPACA_API_SECRET_KEY/APCA_API_SECRET_KEY"
            )
        return cls(api_key, api_secret, base_url=base_url, timeout_sec=timeout_sec)

    def _request_json(self, path: str, params: Mapping[str, str]) -> Mapping[str, Any]:
        query = urllib.parse.urlencode({key: str(value) for key, value in params.items() if str(value) != ""})
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.api_secret,
                "User-Agent": "zpe-finance/0.1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_sec) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise AlpacaAPIError(f"Alpaca request failed: {exc.code} {exc.reason}: {body}") from exc
        except urllib.error.URLError as exc:
            raise AlpacaAPIError(f"Alpaca request failed: {exc}") from exc

    def _paginate(
        self,
        path: str,
        items_key: str,
        symbol: str,
        params: Mapping[str, str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        next_page_token = ""
        while True:
            request_params = dict(params)
            if next_page_token:
                request_params["page_token"] = next_page_token
            payload = self._transport(path, request_params)
            items = payload.get(items_key, {}).get(symbol, [])
            if not isinstance(items, list):
                raise AlpacaAPIError(f"unexpected Alpaca payload shape for {path}")
            rows.extend(dict(item) for item in items)
            next_page_token = str(payload.get("next_page_token") or "")
            if not next_page_token:
                break
        return rows

    def get_stock_bars(
        self,
        *,
        symbol: str,
        timeframe: str,
        start: str,
        end: str,
        feed: str = "iex",
        adjustment: str = "raw",
        limit: int = 10_000,
    ) -> list[dict[str, Any]]:
        return self._paginate(
            "/v2/stocks/bars",
            "bars",
            symbol,
            {
                "symbols": symbol,
                "timeframe": timeframe,
                "start": start,
                "end": end,
                "feed": feed,
                "adjustment": adjustment,
                "sort": "asc",
                "limit": str(limit),
            },
        )

    def get_stock_quotes(
        self,
        *,
        symbol: str,
        start: str,
        end: str,
        feed: str = "iex",
        limit: int = 10_000,
    ) -> list[dict[str, Any]]:
        return self._paginate(
            "/v2/stocks/quotes",
            "quotes",
            symbol,
            {
                "symbols": symbol,
                "start": start,
                "end": end,
                "feed": feed,
                "sort": "asc",
                "limit": str(limit),
            },
        )


def _write_csv(path: Path, header: Iterable[str], rows: Iterable[Iterable[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(list(header))
        writer.writerows(rows)


def normalize_alpaca_bar_rows(items: Iterable[Mapping[str, Any]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for item in items:
        rows.append(
            [
                _parse_rfc3339_ns(str(item["t"])) // 1_000_000,
                _coerce_float(item["o"], "o"),
                _coerce_float(item["h"], "h"),
                _coerce_float(item["l"], "l"),
                _coerce_float(item["c"], "c"),
                _coerce_float(item.get("v", 0.0), "v"),
            ]
        )
    if not rows:
        raise ValueError("no Alpaca OHLCV rows returned")
    return rows


def normalize_alpaca_quote_rows(items: Iterable[Mapping[str, Any]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for item in items:
        rows.append(
            [
                _parse_rfc3339_ns(str(item["t"])),
                _coerce_float(item["bp"], "bp"),
                _coerce_float(item["ap"], "ap"),
                _coerce_float(item.get("bs", 0.0), "bs"),
                _coerce_float(item.get("as", 0.0), "as"),
            ]
        )
    if not rows:
        raise ValueError("no Alpaca quote rows returned")
    return rows


def write_alpaca_bar_csv(path: Path, items: Iterable[Mapping[str, Any]]) -> int:
    rows = normalize_alpaca_bar_rows(items)
    _write_csv(path, ("ts", "open_px", "high_px", "low_px", "close_px", "volume"), rows)
    return len(rows)


def write_alpaca_quote_csv(path: Path, items: Iterable[Mapping[str, Any]]) -> int:
    rows = normalize_alpaca_quote_rows(items)
    _write_csv(path, ("ts", "bid_px", "ask_px", "bid_sz", "ask_sz"), rows)
    return len(rows)


def build_generated_corpus_spec(
    config: Mapping[str, Any],
    requests: Iterable[AlpacaSeriesRequest],
    csv_paths: Mapping[str, Path],
) -> dict[str, Any]:
    series_payload: list[dict[str, Any]] = []
    for request in requests:
        source_path = csv_paths.get(request.series_id)
        if source_path is None:
            raise ValueError(f"missing generated CSV for series: {request.series_id}")
        if request.kind == "ohlcv":
            columns = {
                "timestamp": "ts",
                "open": "open_px",
                "high": "high_px",
                "low": "low_px",
                "close": "close_px",
                "volume": "volume",
            }
        else:
            columns = {
                "timestamp": "ts",
                "bid": "bid_px",
                "ask": "ask_px",
                "bid_size": "bid_sz",
                "ask_size": "ask_sz",
            }

        series_payload.append(
            {
                "series_id": request.series_id,
                "kind": request.kind,
                "source_path": str(source_path),
                "symbol": request.symbol,
                "tick_size": float(request.tick_size),
                "provenance": request.provenance,
                "license_note": request.license_note,
                "timezone": "UTC",
                "timestamp_format": "epoch_ms" if request.kind == "ohlcv" else "epoch_ns",
                "columns": columns,
            }
        )

    payload = {
        "corpus_id": str(config.get("corpus_id", "alpaca_delayed_stock_corpus")),
        "authority_metric": str(config.get("authority_metric", "AM-C05_FROZEN")),
        "buyer_workload": str(config.get("buyer_workload", "query-by-example over delayed stock price action")),
        "series": series_payload,
    }
    query_catalog_path = str(config.get("query_catalog_path", "")).strip()
    if query_catalog_path:
        payload["query_catalog_path"] = query_catalog_path
    return payload
