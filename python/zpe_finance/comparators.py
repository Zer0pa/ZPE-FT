"""Comparator benchmarks and substitution-aware reporting."""

from __future__ import annotations

import bz2
import gzip
import lzma
import struct
import zlib
from typing import Any, Dict

import numpy as np


def _ratio(raw_size: int, compressed_size: int) -> float:
    if compressed_size <= 0:
        return 0.0
    return raw_size / compressed_size


def _encode_varint(value: int) -> bytes:
    out = bytearray()
    v = int(value)
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    out.append(v)
    return bytes(out)


def gorilla_xor_proxy(series: np.ndarray) -> bytes:
    arr = np.asarray(series, dtype=np.float64)
    bits = arr.view(np.uint64)
    if len(bits) == 0:
        return b""

    out = bytearray(struct.pack("<Q", int(bits[0])))
    prev = int(bits[0])
    for value in bits[1:]:
        curr = int(value)
        xor = prev ^ curr
        out.extend(_encode_varint(xor))
        prev = curr
    return bytes(out)


def sax_proxy(series: np.ndarray, bins: int = 16) -> bytes:
    arr = np.asarray(series, dtype=np.float64)
    if len(arr) == 0:
        return b""

    q = np.quantile(arr, np.linspace(0.0, 1.0, bins + 1))
    symbols = np.digitize(arr, q[1:-1], right=True).astype(np.uint8)

    out = bytearray()
    run_symbol = int(symbols[0])
    run_len = 1
    for s in symbols[1:]:
        sval = int(s)
        if sval == run_symbol and run_len < 255:
            run_len += 1
        else:
            out.append(run_symbol)
            out.append(run_len)
            run_symbol = sval
            run_len = 1
    out.append(run_symbol)
    out.append(run_len)
    return bytes(out)


def benchmark_comparators(series: np.ndarray) -> Dict[str, Any]:
    arr = np.asarray(series, dtype=np.float64)
    raw = arr.tobytes(order="C")
    raw_size = len(raw)

    results: Dict[str, Any] = {}

    def add(name: str, payload: bytes, note: str = "") -> None:
        results[name] = {
            "compressed_bytes": len(payload),
            "compression_ratio": _ratio(raw_size, len(payload)),
            "status": "OK",
            "note": note,
        }

    add("zlib", zlib.compress(raw, level=9), "incumbent baseline")
    add("gzip", gzip.compress(raw, compresslevel=9))
    add("bz2", bz2.compress(raw, compresslevel=9))
    add("lzma", lzma.compress(raw))
    add(
        "gorilla_xor_proxy",
        gorilla_xor_proxy(arr),
        "proxy; not byte-identical Gorilla implementation",
    )
    add(
        "sax_proxy",
        sax_proxy(arr),
        "proxy for symbolic compression when time_series_compression unavailable",
    )

    try:
        import zstandard as zstd  # type: ignore

        cctx = zstd.ZstdCompressor(level=19)
        add("zstd", cctx.compress(raw), "modern comparator")
    except Exception as exc:  # pragma: no cover
        results["zstd"] = {
            "status": "UNAVAILABLE",
            "error": str(exc),
            "substitution": "lzma",
            "comparability_impact": "modern comparator reduced",
        }

    try:
        import lz4.frame as lz4f  # type: ignore

        add("lz4", lz4f.compress(raw), "fast modern comparator")
    except Exception as exc:  # pragma: no cover
        results["lz4"] = {
            "status": "UNAVAILABLE",
            "error": str(exc),
            "substitution": "zlib",
            "comparability_impact": "high-speed comparator reduced",
        }

    try:
        import time_series_compression as tsc  # type: ignore

        _ = tsc  # API varies; probe import only
        results["time_series_compression"] = {
            "status": "INCONCLUSIVE",
            "note": "package import succeeded but API variation prevented automated benchmark",
            "substitution": "sax_proxy",
            "comparability_impact": "partial",
        }
    except Exception as exc:  # pragma: no cover
        results["time_series_compression"] = {
            "status": "UNAVAILABLE",
            "error": str(exc),
            "substitution": "sax_proxy",
            "comparability_impact": "benchmark comparability reduced",
        }

    return {
        "raw_bytes": raw_size,
        "comparators": results,
    }
