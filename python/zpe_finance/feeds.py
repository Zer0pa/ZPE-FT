"""Zipline-Reloaded integration smoke adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class ZiplineSmokeResult:
    status: str
    note: str


class ZPEFeedAdapter:
    def __init__(self, bars: Dict[str, np.ndarray]):
        self.bars = bars

    def to_bundle_frame(self) -> Dict[str, np.ndarray]:
        required = ("timestamp", "open", "high", "low", "close", "volume")
        for key in required:
            if key not in self.bars:
                raise ValueError(f"missing field: {key}")
        return {
            "date": self.bars["timestamp"],
            "open": self.bars["open"],
            "high": self.bars["high"],
            "low": self.bars["low"],
            "close": self.bars["close"],
            "volume": self.bars["volume"],
        }


def zipline_smoke_check() -> ZiplineSmokeResult:
    try:
        import zipline  # type: ignore  # noqa: F401

        return ZiplineSmokeResult(status="OK", note="zipline import succeeded")
    except Exception as exc:  # pragma: no cover - optional dependency
        return ZiplineSmokeResult(
            status="INCONCLUSIVE",
            note=f"zipline-reloaded unavailable: {exc}",
        )
