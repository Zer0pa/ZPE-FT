"""Core encode/decode logic for OHLCV and tick streams."""

from __future__ import annotations

import math
from typing import Dict, Mapping, Tuple

import numpy as np

from .packet import KIND_OHLCV, KIND_TICK, pack_packet, unpack_packet
from .rust_bridge import fnv1a64, pack_nibbles, unpack_nibbles
from .schema import validate_bars, validate_ticks


def raw_bytes_ohlcv(count: int) -> int:
    # PRD baseline uses raw float64 bar payload (6 x float64)
    return int(count) * 6 * 8


def raw_bytes_tick(count: int) -> int:
    # MqlTick-like baseline in PRD
    return int(count) * 60


def _zigzag_encode(value: int) -> int:
    return (value << 1) ^ (value >> 63)


def _zigzag_decode(value: int) -> int:
    return (value >> 1) ^ -(value & 1)


def _encode_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError("varint requires unsigned integer")
    out = bytearray()
    v = value
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80)
        v >>= 7
    out.append(v)
    return bytes(out)


def _decode_varint(data: bytes, offset: int) -> Tuple[int, int]:
    shift = 0
    value = 0
    pos = offset
    while True:
        if pos >= len(data):
            raise ValueError("truncated varint overflow stream")
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return value, pos
        shift += 7
        if shift > 63:
            raise ValueError("varint too large")


def _encode_signed_nibble(value: int, overflow: bytearray) -> int:
    if -7 <= value <= 7:
        return value + 7
    overflow.extend(_encode_varint(_zigzag_encode(value)))
    return 15


def _decode_signed_nibble(code: int, overflow: bytes, pos: int) -> Tuple[int, int]:
    if code <= 14:
        return code - 7, pos
    value, new_pos = _decode_varint(overflow, pos)
    return _zigzag_decode(value), new_pos


def _encode_unsigned_nibble(value: int, overflow: bytearray) -> int:
    if 0 <= value <= 14:
        return value
    overflow.extend(_encode_varint(value))
    return 15


def _decode_unsigned_nibble(code: int, overflow: bytes, pos: int) -> Tuple[int, int]:
    if code <= 14:
        return code, pos
    return _decode_varint(overflow, pos)


def _volume_to_log_nibble(volume: float) -> int:
    if volume <= 0:
        return 0
    return int(min(15, max(0, round(math.log2(volume + 1.0)))))


def _log_nibble_to_volume(code: int) -> float:
    return float((1 << code) - 1)


def encode_ohlcv(
    bars: Mapping[str, object],
    tick_size: float,
    instrument: str = "UNKNOWN",
) -> bytes:
    if tick_size <= 0:
        raise ValueError("tick_size must be positive")

    valid = validate_bars(bars)
    ts = valid["timestamp"]
    op = valid["open"]
    hi = valid["high"]
    lo = valid["low"]
    cl = valid["close"]
    vol = valid["volume"]
    count = len(ts)

    op_ticks = np.rint(op / tick_size).astype(np.int64)
    hi_ticks = np.rint(hi / tick_size).astype(np.int64)
    lo_ticks = np.rint(lo / tick_size).astype(np.int64)
    cl_ticks = np.rint(cl / tick_size).astype(np.int64)

    overflow = bytearray()
    nibbles = []

    prev_close = int(op_ticks[0])
    for i in range(count):
        open_tick = int(op_ticks[i])
        close_tick = int(cl_ticks[i])
        high_tick = int(hi_ticks[i])
        low_tick = int(lo_ticks[i])

        do = open_tick - prev_close
        dc = close_tick - open_tick
        dh = high_tick - max(open_tick, close_tick)
        dl = min(open_tick, close_tick) - low_tick

        if dh < 0 or dl < 0:
            raise ValueError("invalid OHLC relationship after tick quantisation")

        do_code = _encode_signed_nibble(do, overflow)
        dc_code = _encode_signed_nibble(dc, overflow)
        dh_code = _encode_unsigned_nibble(dh, overflow)
        dl_code = _encode_unsigned_nibble(dl, overflow)
        vol_code = _volume_to_log_nibble(float(vol[i]))

        nibbles.extend((do_code, dc_code, dh_code, dl_code, vol_code))

        prev_close = close_tick

    nibble_bytes = pack_nibbles(nibbles)

    interval_ms = int(np.median(np.diff(ts))) if count > 1 else 0
    packet_meta: Dict[str, int | float] = {
        "kind": KIND_OHLCV,
        "count": count,
        "tick_size": float(tick_size),
        "base_tick": int(op_ticks[0]),
        "base_aux": int(ts[0]),
        "interval_ms": interval_ms,
        "nibble_count": len(nibbles),
        "instrument_hash": int(fnv1a64(instrument.encode("utf-8")) & 0xFFFFFFFF),
    }
    return pack_packet(packet_meta, nibble_bytes, bytes(overflow))


def decode_ohlcv(payload: bytes) -> Dict[str, np.ndarray]:
    meta, nibble_bytes, overflow = unpack_packet(payload)
    if meta["kind"] != KIND_OHLCV:
        raise ValueError("payload is not OHLCV")

    count = int(meta["count"])
    nibbles = unpack_nibbles(nibble_bytes, int(meta["nibble_count"]))
    if len(nibbles) != count * 5:
        raise ValueError("unexpected nibble count for OHLCV payload")

    tick_size = float(meta["tick_size"])
    base_tick = int(meta["base_tick"])
    start_ts = int(meta["base_aux"])
    interval = int(meta["interval_ms"])

    timestamp = np.empty(count, dtype=np.int64)
    op = np.empty(count, dtype=np.float64)
    hi = np.empty(count, dtype=np.float64)
    lo = np.empty(count, dtype=np.float64)
    cl = np.empty(count, dtype=np.float64)
    vol = np.empty(count, dtype=np.float64)

    overflow_pos = 0
    prev_close = base_tick

    idx = 0
    for i in range(count):
        do_code = nibbles[idx]
        dc_code = nibbles[idx + 1]
        dh_code = nibbles[idx + 2]
        dl_code = nibbles[idx + 3]
        vol_code = nibbles[idx + 4]
        idx += 5

        do, overflow_pos = _decode_signed_nibble(do_code, overflow, overflow_pos)
        dc, overflow_pos = _decode_signed_nibble(dc_code, overflow, overflow_pos)
        dh, overflow_pos = _decode_unsigned_nibble(dh_code, overflow, overflow_pos)
        dl, overflow_pos = _decode_unsigned_nibble(dl_code, overflow, overflow_pos)

        open_tick = prev_close + do
        close_tick = open_tick + dc
        high_tick = max(open_tick, close_tick) + dh
        low_tick = min(open_tick, close_tick) - dl

        timestamp[i] = start_ts + (i * interval)
        op[i] = open_tick * tick_size
        cl[i] = close_tick * tick_size
        hi[i] = high_tick * tick_size
        lo[i] = low_tick * tick_size
        vol[i] = _log_nibble_to_volume(vol_code)

        prev_close = close_tick

    if overflow_pos != len(overflow):
        raise ValueError("unconsumed OHLCV overflow bytes")

    return {
        "timestamp": timestamp,
        "open": op,
        "high": hi,
        "low": lo,
        "close": cl,
        "volume": vol,
    }


def encode_ticks(
    ticks: Mapping[str, object],
    tick_size: float,
    instrument: str = "UNKNOWN",
) -> bytes:
    if tick_size <= 0:
        raise ValueError("tick_size must be positive")

    valid = validate_ticks(ticks)
    ts = valid["timestamp"]
    bid = valid["bid"]
    ask = valid["ask"]
    bid_size = valid["bid_size"]
    ask_size = valid["ask_size"]
    count = len(ts)

    bid_ticks = np.rint(bid / tick_size).astype(np.int64)
    ask_ticks = np.rint(ask / tick_size).astype(np.int64)

    overflow = bytearray()
    nibbles = []

    prev_ts = int(ts[0])
    prev_bid = int(bid_ticks[0])
    prev_ask = int(bid_ticks[0])

    for i in range(count):
        curr_ts = int(ts[i])
        curr_bid = int(bid_ticks[i])
        curr_ask = int(ask_ticks[i])

        dt = 0 if i == 0 else curr_ts - prev_ts
        dbid = curr_bid - prev_bid
        dask = curr_ask - prev_ask

        if curr_ask < curr_bid:
            raise ValueError("ask must be >= bid after quantisation")

        dt_code = _encode_unsigned_nibble(dt, overflow)
        dbid_code = _encode_signed_nibble(dbid, overflow)
        dask_code = _encode_signed_nibble(dask, overflow)
        bid_log = _volume_to_log_nibble(float(bid_size[i]))
        ask_log = _volume_to_log_nibble(float(ask_size[i]))

        nibbles.extend((dt_code, dbid_code, dask_code, bid_log, ask_log))

        prev_ts = curr_ts
        prev_bid = curr_bid
        prev_ask = curr_ask

    nibble_bytes = pack_nibbles(nibbles)

    packet_meta: Dict[str, int | float] = {
        "kind": KIND_TICK,
        "count": count,
        "tick_size": float(tick_size),
        "base_tick": int(bid_ticks[0]),
        "base_aux": int(ts[0]),
        "interval_ms": 0,
        "nibble_count": len(nibbles),
        "instrument_hash": int(fnv1a64(instrument.encode("utf-8")) & 0xFFFFFFFF),
    }
    return pack_packet(packet_meta, nibble_bytes, bytes(overflow))


def decode_ticks(payload: bytes) -> Dict[str, np.ndarray]:
    meta, nibble_bytes, overflow = unpack_packet(payload)
    if meta["kind"] != KIND_TICK:
        raise ValueError("payload is not tick data")

    count = int(meta["count"])
    nibbles = unpack_nibbles(nibble_bytes, int(meta["nibble_count"]))
    if len(nibbles) != count * 5:
        raise ValueError("unexpected nibble count for tick payload")

    tick_size = float(meta["tick_size"])
    base_bid_tick = int(meta["base_tick"])
    start_ts = int(meta["base_aux"])

    timestamp = np.empty(count, dtype=np.int64)
    bid = np.empty(count, dtype=np.float64)
    ask = np.empty(count, dtype=np.float64)
    bid_size = np.empty(count, dtype=np.float64)
    ask_size = np.empty(count, dtype=np.float64)

    overflow_pos = 0
    prev_ts = start_ts
    prev_bid = base_bid_tick
    prev_ask = base_bid_tick

    idx = 0
    for i in range(count):
        dt_code = nibbles[idx]
        dbid_code = nibbles[idx + 1]
        dask_code = nibbles[idx + 2]
        bid_log = nibbles[idx + 3]
        ask_log = nibbles[idx + 4]
        idx += 5

        dt, overflow_pos = _decode_unsigned_nibble(dt_code, overflow, overflow_pos)
        dbid, overflow_pos = _decode_signed_nibble(dbid_code, overflow, overflow_pos)
        dask, overflow_pos = _decode_signed_nibble(dask_code, overflow, overflow_pos)

        curr_ts = prev_ts + dt
        curr_bid = prev_bid + dbid
        curr_ask = prev_ask + dask

        if curr_ask < curr_bid:
            raise ValueError("decoded ask below bid")

        timestamp[i] = curr_ts
        bid[i] = curr_bid * tick_size
        ask[i] = curr_ask * tick_size
        bid_size[i] = _log_nibble_to_volume(bid_log)
        ask_size[i] = _log_nibble_to_volume(ask_log)

        prev_ts = curr_ts
        prev_bid = curr_bid
        prev_ask = curr_ask

    if overflow_pos != len(overflow):
        raise ValueError("unconsumed tick overflow bytes")

    return {
        "timestamp": timestamp,
        "bid": bid,
        "ask": ask,
        "bid_size": bid_size,
        "ask_size": ask_size,
    }
