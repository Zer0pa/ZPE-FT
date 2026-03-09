"""Directional tokenization and canonical pattern templates."""

from __future__ import annotations

from typing import Dict, Iterable, List

import numpy as np


def deltas_to_tokens(deltas: np.ndarray) -> np.ndarray:
    d = np.asarray(deltas, dtype=np.int64)
    tokens = np.empty(len(d), dtype=np.uint8)

    tokens[d <= -8] = 0
    tokens[(d > -8) & (d <= -3)] = 1
    tokens[(d > -3) & (d <= -1)] = 2
    tokens[d == 0] = 3
    tokens[d == 1] = 4
    tokens[(d >= 2) & (d <= 3)] = 5
    tokens[(d >= 4) & (d <= 7)] = 6
    tokens[d >= 8] = 7
    return tokens


def bars_to_tokens(close: np.ndarray, tick_size: float) -> np.ndarray:
    close_ticks = np.rint(np.asarray(close, dtype=np.float64) / tick_size).astype(np.int64)
    deltas = np.diff(close_ticks, prepend=close_ticks[0])
    return deltas_to_tokens(deltas)


def _repeat(token: int, length: int) -> List[int]:
    return [token] * length


def canonical_pattern_library() -> Dict[str, np.ndarray]:
    head_shoulders = (
        _repeat(6, 5)
        + _repeat(2, 4)
        + _repeat(7, 7)
        + _repeat(1, 7)
        + _repeat(6, 5)
        + _repeat(2, 5)
    )
    double_bottom = _repeat(1, 8) + _repeat(6, 5) + _repeat(1, 8) + _repeat(6, 7)
    bull_flag = _repeat(7, 14) + _repeat(3, 7) + _repeat(6, 9)
    cup_handle = _repeat(1, 7) + _repeat(3, 12) + _repeat(6, 7) + _repeat(2, 4) + _repeat(6, 6)

    return {
        "head_shoulders": np.asarray(head_shoulders, dtype=np.uint8),
        "double_bottom": np.asarray(double_bottom, dtype=np.uint8),
        "bull_flag": np.asarray(bull_flag, dtype=np.uint8),
        "cup_handle": np.asarray(cup_handle, dtype=np.uint8),
    }


def build_confusion_set(pattern: np.ndarray) -> List[np.ndarray]:
    p = np.asarray(pattern, dtype=np.uint8)
    confusion: List[np.ndarray] = []

    # Near-miss by flipping sparse tokens.
    for stride in (5, 7, 9):
        q = p.copy()
        q[::stride] = (q[::stride] + 1) % 8
        confusion.append(q)

    # Length-distorted near misses.
    confusion.append(p[:-2])
    confusion.append(np.concatenate([p, p[-3:]]))

    # Inverted direction near-miss.
    confusion.append((7 - p).astype(np.uint8))

    return confusion


def inject_patterns(
    base_tokens: np.ndarray,
    template: np.ndarray,
    positions: Iterable[int],
) -> tuple[np.ndarray, List[int]]:
    out = np.asarray(base_tokens, dtype=np.uint8).copy()
    truth: List[int] = []
    m = len(template)
    for pos in positions:
        if pos < 0 or pos + m > len(out):
            continue
        out[pos : pos + m] = template
        truth.append(int(pos))
    return out, truth
