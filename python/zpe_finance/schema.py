"""Schema validation for bars and ticks."""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np

BAR_FIELDS = ("timestamp", "open", "high", "low", "close", "volume")
TICK_FIELDS = ("timestamp", "bid", "ask", "bid_size", "ask_size")


def _as_array(values, dtype) -> np.ndarray:
    arr = np.asarray(values, dtype=dtype)
    if arr.ndim != 1:
        raise ValueError("all input fields must be 1D arrays")
    return arr


def _ensure_no_nan_or_inf(arr: np.ndarray, name: str) -> None:
    if np.issubdtype(arr.dtype, np.floating):
        if np.isnan(arr).any() or np.isinf(arr).any():
            raise ValueError(f"{name} contains NaN/Inf")


def validate_bars(bars: Mapping[str, object]) -> Dict[str, np.ndarray]:
    missing = [f for f in BAR_FIELDS if f not in bars]
    if missing:
        raise ValueError(f"missing bar fields: {missing}")

    out: Dict[str, np.ndarray] = {
        "timestamp": _as_array(bars["timestamp"], np.int64),
        "open": _as_array(bars["open"], np.float64),
        "high": _as_array(bars["high"], np.float64),
        "low": _as_array(bars["low"], np.float64),
        "close": _as_array(bars["close"], np.float64),
        "volume": _as_array(bars["volume"], np.float64),
    }

    n = len(out["timestamp"])
    if n == 0:
        raise ValueError("bars cannot be empty")

    for field, arr in out.items():
        if len(arr) != n:
            raise ValueError(f"field length mismatch: {field}")
        _ensure_no_nan_or_inf(arr, field)

    ts = out["timestamp"]
    if np.any(np.diff(ts) <= 0):
        raise ValueError("bar timestamps must be strictly increasing")

    op = out["open"]
    hi = out["high"]
    lo = out["low"]
    cl = out["close"]
    if np.any(hi < np.maximum(op, cl)):
        raise ValueError("bar high must be >= max(open, close)")
    if np.any(lo > np.minimum(op, cl)):
        raise ValueError("bar low must be <= min(open, close)")

    if np.any(out["volume"] < 0):
        raise ValueError("bar volume cannot be negative")

    return out


def validate_ticks(ticks: Mapping[str, object]) -> Dict[str, np.ndarray]:
    missing = [f for f in TICK_FIELDS if f not in ticks]
    if missing:
        raise ValueError(f"missing tick fields: {missing}")

    out: Dict[str, np.ndarray] = {
        "timestamp": _as_array(ticks["timestamp"], np.int64),
        "bid": _as_array(ticks["bid"], np.float64),
        "ask": _as_array(ticks["ask"], np.float64),
        "bid_size": _as_array(ticks["bid_size"], np.float64),
        "ask_size": _as_array(ticks["ask_size"], np.float64),
    }

    n = len(out["timestamp"])
    if n == 0:
        raise ValueError("ticks cannot be empty")

    for field, arr in out.items():
        if len(arr) != n:
            raise ValueError(f"field length mismatch: {field}")
        _ensure_no_nan_or_inf(arr, field)

    ts = out["timestamp"]
    if np.any(np.diff(ts) <= 0):
        raise ValueError("tick timestamps must be strictly increasing")

    bid = out["bid"]
    ask = out["ask"]
    if np.any(ask < bid):
        raise ValueError("tick ask must be >= bid")

    if np.any(out["bid_size"] < 0) or np.any(out["ask_size"] < 0):
        raise ValueError("tick sizes cannot be negative")

    return out
