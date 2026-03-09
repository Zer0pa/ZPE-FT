"""Binary packet framing for .zpfin payloads."""

from __future__ import annotations

import struct
import zlib
from typing import Dict, Tuple

MAGIC = b"ZPFN1"
VERSION = 1

KIND_OHLCV = 1
KIND_TICK = 2

HEADER_NO_CRC_FMT = "<5sBBBIdqqIIIII"
HEADER_NO_CRC_SIZE = struct.calcsize(HEADER_NO_CRC_FMT)
CRC_FMT = "<I"
CRC_SIZE = struct.calcsize(CRC_FMT)


def pack_packet(meta: Dict[str, int | float], nibble_bytes: bytes, overflow_bytes: bytes) -> bytes:
    header_no_crc = struct.pack(
        HEADER_NO_CRC_FMT,
        MAGIC,
        VERSION,
        int(meta["kind"]),
        int(meta.get("flags", 0)),
        int(meta["count"]),
        float(meta["tick_size"]),
        int(meta["base_tick"]),
        int(meta["base_aux"]),
        int(meta["interval_ms"]),
        int(meta["nibble_count"]),
        len(nibble_bytes),
        len(overflow_bytes),
        int(meta["instrument_hash"]),
    )
    crc = zlib.crc32(header_no_crc)
    crc = zlib.crc32(nibble_bytes, crc)
    crc = zlib.crc32(overflow_bytes, crc) & 0xFFFFFFFF

    return header_no_crc + struct.pack(CRC_FMT, crc) + nibble_bytes + overflow_bytes


def unpack_packet(payload: bytes) -> Tuple[Dict[str, int | float], bytes, bytes]:
    if len(payload) < HEADER_NO_CRC_SIZE + CRC_SIZE:
        raise ValueError("payload too short")

    header_no_crc = payload[:HEADER_NO_CRC_SIZE]
    (
        magic,
        version,
        kind,
        flags,
        count,
        tick_size,
        base_tick,
        base_aux,
        interval_ms,
        nibble_count,
        nibble_len,
        overflow_len,
        instrument_hash,
    ) = struct.unpack(HEADER_NO_CRC_FMT, header_no_crc)

    if magic != MAGIC:
        raise ValueError("invalid packet magic")
    if version != VERSION:
        raise ValueError(f"unsupported packet version: {version}")

    crc_offset = HEADER_NO_CRC_SIZE
    expected_crc = struct.unpack(CRC_FMT, payload[crc_offset : crc_offset + CRC_SIZE])[0]
    body_offset = crc_offset + CRC_SIZE

    expected_total = body_offset + nibble_len + overflow_len
    if expected_total != len(payload):
        raise ValueError("payload length mismatch")

    nibble_bytes = payload[body_offset : body_offset + nibble_len]
    overflow_bytes = payload[body_offset + nibble_len : expected_total]

    actual_crc = zlib.crc32(header_no_crc)
    actual_crc = zlib.crc32(nibble_bytes, actual_crc)
    actual_crc = zlib.crc32(overflow_bytes, actual_crc) & 0xFFFFFFFF

    if actual_crc != expected_crc:
        raise ValueError("packet CRC mismatch")

    meta: Dict[str, int | float] = {
        "kind": int(kind),
        "flags": int(flags),
        "count": int(count),
        "tick_size": float(tick_size),
        "base_tick": int(base_tick),
        "base_aux": int(base_aux),
        "interval_ms": int(interval_ms),
        "nibble_count": int(nibble_count),
        "nibble_len": int(nibble_len),
        "overflow_len": int(overflow_len),
        "instrument_hash": int(instrument_hash),
    }
    return meta, nibble_bytes, overflow_bytes
