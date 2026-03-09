"""Rust bridge with deterministic Python fallback."""

from __future__ import annotations

from typing import Iterable, List

HAS_RUST = False
RUST_IMPORT_ERROR = None

try:
    import zpe_finance_rs as _rs

    HAS_RUST = True
except Exception as exc:  # pragma: no cover - fallback path
    _rs = None
    RUST_IMPORT_ERROR = str(exc)


def pack_nibbles(values: Iterable[int]) -> bytes:
    vals = [int(v) for v in values]
    if HAS_RUST:
        return bytes(_rs.pack_nibbles(vals))

    out = bytearray()
    i = 0
    while i < len(vals):
        hi = vals[i]
        if hi < 0 or hi > 15:
            raise ValueError("nibble value must be in [0, 15]")
        lo = vals[i + 1] if i + 1 < len(vals) else 0
        if lo < 0 or lo > 15:
            raise ValueError("nibble value must be in [0, 15]")
        out.append((hi << 4) | lo)
        i += 2
    return bytes(out)


def unpack_nibbles(data: bytes, value_count: int) -> List[int]:
    if HAS_RUST:
        return [int(v) for v in _rs.unpack_nibbles(list(data), int(value_count))]

    out: List[int] = []
    for byte in data:
        if len(out) < value_count:
            out.append((byte >> 4) & 0x0F)
        if len(out) < value_count:
            out.append(byte & 0x0F)
        if len(out) >= value_count:
            break
    return out


def find_subsequence(haystack: bytes, needle: bytes) -> List[int]:
    if not needle:
        raise ValueError("needle must not be empty")
    if HAS_RUST:
        return [int(v) for v in _rs.find_subsequence(list(haystack), list(needle))]

    matches: List[int] = []
    n = len(needle)
    for i in range(0, len(haystack) - n + 1):
        if haystack[i : i + n] == needle:
            matches.append(i)
    return matches


def fnv1a64(data: bytes) -> int:
    if HAS_RUST:
        return int(_rs.fnv1a64(list(data)))

    offset = 0xCBF29CE484222325
    prime = 0x100000001B3
    h = offset
    for b in data:
        h ^= b
        h = (h * prime) & 0xFFFFFFFFFFFFFFFF
    return h


def rust_version() -> str:
    if HAS_RUST:
        return str(_rs.version())
    return "python-fallback"
