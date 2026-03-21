"""Real-market corpus loading, normalization, and freeze metadata."""

from __future__ import annotations

import csv
import gzip
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

import numpy as np

from .metrics import dataset_digest, schema_inventory, sha256_file
from .schema import BAR_FIELDS, TICK_FIELDS, validate_bars, validate_ticks

SUPPORTED_KINDS = ("ohlcv", "tick")
SUPPORTED_TIMESTAMP_FORMATS = ("epoch_s", "epoch_ms", "epoch_ns", "iso8601")


@dataclass(frozen=True)
class SeriesSpec:
    series_id: str
    kind: str
    source_path: Path
    symbol: str
    tick_size: float
    provenance: str
    license_note: str
    timezone: str = "UTC"
    delimiter: str = ","
    timestamp_format: str = "epoch_ms"
    columns: Mapping[str, str] | None = None
    scales: Mapping[str, float] | None = None

    @property
    def required_fields(self) -> Sequence[str]:
        return BAR_FIELDS if self.kind == "ohlcv" else TICK_FIELDS


def _resolve_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else (base_dir / path)


def _normalize_iso8601(raw: str, tz_name: str) -> int:
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz_name))
    return int(dt.astimezone(timezone.utc).timestamp() * 1000.0)


def _parse_integer_timestamp(raw: str, field: str) -> int:
    text = raw.strip()
    if not text:
        raise ValueError(f"empty timestamp value for field: {field}")
    if "." in text or "e" in text.lower():
        return int(float(text))
    return int(text)


def _parse_timestamp(raw: str, timestamp_format: str, tz_name: str) -> int:
    if timestamp_format == "epoch_s":
        return _parse_integer_timestamp(raw, "timestamp") * 1000
    if timestamp_format == "epoch_ms":
        return _parse_integer_timestamp(raw, "timestamp")
    if timestamp_format == "epoch_ns":
        return _parse_integer_timestamp(raw, "timestamp")
    if timestamp_format == "iso8601":
        return _normalize_iso8601(raw, tz_name)
    raise ValueError(f"unsupported timestamp_format: {timestamp_format}")


def _timestamp_unit(timestamp_format: str) -> str:
    return "ns" if timestamp_format == "epoch_ns" else "ms"


def _required_fields(kind: str) -> Sequence[str]:
    if kind == "ohlcv":
        return BAR_FIELDS
    if kind == "tick":
        return TICK_FIELDS
    raise ValueError(f"unsupported kind: {kind}")


def _open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", newline="")
    return path.open("r", encoding="utf-8", newline="")


def _parse_float(raw: str, field: str) -> float:
    text = raw.strip()
    if not text:
        raise ValueError(f"empty numeric value for field: {field}")
    return float(text)


def _build_series_arrays(spec: SeriesSpec, rows: Iterable[Mapping[str, str]]) -> Dict[str, np.ndarray]:
    columns = dict(spec.columns or {})
    scales = dict(spec.scales or {})
    required_fields = list(spec.required_fields)
    missing_columns = [field for field in required_fields if field not in columns]
    if missing_columns:
        raise ValueError(f"missing column mappings for fields: {missing_columns}")

    timestamp_values: list[int] = []
    numeric_fields = [field for field in required_fields if field != "timestamp"]
    numeric_values = {field: [] for field in numeric_fields}

    for row in rows:
        timestamp_values.append(
            _parse_timestamp(
                row[columns["timestamp"]],
                spec.timestamp_format,
                spec.timezone,
            )
        )
        for field in numeric_fields:
            scale = float(scales.get(field, 1.0))
            numeric_values[field].append(_parse_float(row[columns[field]], field) * scale)

    if not timestamp_values:
        raise ValueError(f"no rows loaded for series: {spec.series_id}")

    payload: Dict[str, np.ndarray] = {
        "timestamp": np.asarray(timestamp_values, dtype=np.int64),
    }
    for field in numeric_fields:
        payload[field] = np.asarray(numeric_values[field], dtype=np.float64)
    return payload


def load_series_from_spec(spec: SeriesSpec) -> Dict[str, np.ndarray]:
    if spec.kind not in SUPPORTED_KINDS:
        raise ValueError(f"unsupported series kind: {spec.kind}")
    if spec.timestamp_format not in SUPPORTED_TIMESTAMP_FORMATS:
        raise ValueError(f"unsupported timestamp_format: {spec.timestamp_format}")
    if spec.tick_size <= 0:
        raise ValueError("tick_size must be positive")
    if not spec.source_path.exists():
        raise FileNotFoundError(spec.source_path)

    with _open_text(spec.source_path) as handle:
        reader = csv.DictReader(handle, delimiter=spec.delimiter)
        if reader.fieldnames is None:
            raise ValueError(f"missing header row in source file: {spec.source_path}")
        rows = list(reader)

    payload = _build_series_arrays(spec, rows)
    if spec.kind == "ohlcv":
        return validate_bars(payload)
    return validate_ticks(payload)


def write_normalized_series(path: Path, series: Mapping[str, np.ndarray]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **series)


def load_normalized_series(path: Path) -> Dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        return {key: np.asarray(data[key]) for key in data.files}


def series_spec_from_dict(payload: Mapping[str, Any], base_dir: Path) -> SeriesSpec:
    required = ("series_id", "kind", "source_path", "symbol", "tick_size", "provenance", "license_note")
    missing = [field for field in required if field not in payload]
    if missing:
        raise ValueError(f"missing series spec fields: {missing}")
    kind = str(payload["kind"])
    return SeriesSpec(
        series_id=str(payload["series_id"]),
        kind=kind,
        source_path=_resolve_path(base_dir, str(payload["source_path"])),
        symbol=str(payload["symbol"]),
        tick_size=float(payload["tick_size"]),
        provenance=str(payload["provenance"]),
        license_note=str(payload["license_note"]),
        timezone=str(payload.get("timezone", "UTC")),
        delimiter=str(payload.get("delimiter", ",")),
        timestamp_format=str(payload.get("timestamp_format", "epoch_ms")),
        columns=dict(payload.get("columns", {})),
        scales={str(key): float(value) for key, value in dict(payload.get("scales", {})).items()},
    )


def load_corpus_config(path: Path) -> tuple[dict[str, Any], list[SeriesSpec]]:
    config = json.loads(path.read_text(encoding="utf-8"))
    series_payload = config.get("series", [])
    if not isinstance(series_payload, list) or not series_payload:
        raise ValueError("corpus config must contain a non-empty 'series' list")
    specs = [series_spec_from_dict(item, path.parent) for item in series_payload]
    return config, specs


def freeze_series_entry(
    spec: SeriesSpec,
    series: Mapping[str, np.ndarray],
    normalized_path: Path | None = None,
) -> dict[str, Any]:
    entry = {
        "series_id": spec.series_id,
        "kind": spec.kind,
        "symbol": spec.symbol,
        "tick_size": float(spec.tick_size),
        "source_path": str(spec.source_path),
        "source_sha256": sha256_file(spec.source_path),
        "row_count": int(len(series["timestamp"])),
        "schema": schema_inventory(series),
        "content_sha256": dataset_digest(series),
        "timestamp_start": int(series["timestamp"][0]),
        "timestamp_end": int(series["timestamp"][-1]),
        "timestamp_unit": _timestamp_unit(spec.timestamp_format),
        "provenance": spec.provenance,
        "license_note": spec.license_note,
        "timezone": spec.timezone,
        "delimiter": spec.delimiter,
        "timestamp_format": spec.timestamp_format,
        "columns": dict(spec.columns or {}),
        "scales": {key: float(value) for key, value in dict(spec.scales or {}).items()},
    }
    if normalized_path is not None:
        entry["normalized_path"] = str(normalized_path)
    return entry


def load_series_from_manifest_entry(entry: Mapping[str, Any]) -> Dict[str, np.ndarray]:
    normalized_path = entry.get("normalized_path")
    if normalized_path:
        path = Path(str(normalized_path))
        if path.exists():
            return load_normalized_series(path)
    spec = series_spec_from_dict(entry, Path.cwd())
    return load_series_from_spec(spec)
