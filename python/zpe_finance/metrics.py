"""Metrics, hashing, and artifact helpers."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np


def rmse_ticks(a: np.ndarray, b: np.ndarray) -> float:
    if a.shape != b.shape:
        raise ValueError("shape mismatch for RMSE")
    diff = a.astype(np.float64) - b.astype(np.float64)
    return float(np.sqrt(np.mean(diff * diff)))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def dataset_digest(mapping: Mapping[str, np.ndarray]) -> str:
    h = hashlib.sha256()
    for key in sorted(mapping.keys()):
        arr = np.asarray(mapping[key])
        h.update(key.encode("utf-8"))
        h.update(str(arr.dtype).encode("utf-8"))
        h.update(str(arr.shape).encode("utf-8"))
        h.update(arr.tobytes(order="C"))
    return h.hexdigest()


def schema_inventory(mapping: Mapping[str, np.ndarray]) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    for key, arr in mapping.items():
        a = np.asarray(arr)
        inventory[key] = {
            "dtype": str(a.dtype),
            "shape": list(a.shape),
        }
    return inventory


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
