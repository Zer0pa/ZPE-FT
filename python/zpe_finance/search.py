"""Pattern indexing and approximate search over token streams."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

import numpy as np

from .rust_bridge import find_subsequence


@dataclass
class SearchResult:
    position: int
    score: float


class PatternIndex:
    def __init__(self, tokens: np.ndarray, k: int = 4):
        self.tokens = np.asarray(tokens, dtype=np.uint8)
        self.k = int(max(2, k))
        self.index: Dict[bytes, List[int]] = {}
        if len(self.tokens) >= self.k:
            for i in range(0, len(self.tokens) - self.k + 1):
                key = bytes(self.tokens[i : i + self.k])
                self.index.setdefault(key, []).append(i)

    def exact_search(self, pattern: Sequence[int]) -> List[int]:
        p = np.asarray(pattern, dtype=np.uint8)
        return [int(x) for x in find_subsequence(bytes(self.tokens), bytes(p))]

    def search(
        self,
        pattern: Sequence[int],
        top_k: int = 10,
        min_score: float = 0.0,
        max_candidates: int = 50_000,
    ) -> List[SearchResult]:
        p = np.asarray(pattern, dtype=np.uint8)
        m = len(p)
        if m == 0:
            raise ValueError("pattern cannot be empty")
        if m > len(self.tokens):
            return []

        if m >= self.k:
            key = bytes(p[: self.k])
            starts = self.index.get(key, [])
        else:
            starts = list(range(0, len(self.tokens) - m + 1))

        if not starts:
            starts = list(range(0, len(self.tokens) - m + 1))

        if len(starts) > max_candidates:
            starts = starts[:max_candidates]

        results: List[SearchResult] = []
        for pos in starts:
            if pos + m > len(self.tokens):
                continue
            window = self.tokens[pos : pos + m]
            mismatch = int(np.count_nonzero(window != p))
            score = 1.0 - (mismatch / m)
            if score >= min_score:
                results.append(SearchResult(position=int(pos), score=float(score)))

        results.sort(key=lambda x: (-x.score, x.position))
        return results[:top_k]


def precision_at_k(
    ranked: Sequence[SearchResult],
    truth_positions: Sequence[int],
    k: int = 10,
    tolerance: int = 2,
) -> float:
    truth = list(int(p) for p in truth_positions)
    if not truth:
        return 0.0

    hits = 0
    for item in list(ranked)[:k]:
        if any(abs(item.position - t) <= tolerance for t in truth):
            hits += 1
    return hits / float(max(1, k))
