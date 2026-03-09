"""SQLite adapter for bit-consistent packet roundtrip checks."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Dict

from .metrics import sha256_bytes


def init_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS zpe_packets (
            series_id TEXT PRIMARY KEY,
            payload BLOB NOT NULL,
            payload_sha256 TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS zpe_chunks (
            series_id TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            payload BLOB NOT NULL,
            PRIMARY KEY (series_id, chunk_index)
        )
        """
    )
    conn.commit()
    return conn


def store_packet(conn: sqlite3.Connection, series_id: str, payload: bytes) -> None:
    digest = sha256_bytes(payload)
    conn.execute(
        "INSERT OR REPLACE INTO zpe_packets (series_id, payload, payload_sha256) VALUES (?, ?, ?)",
        (series_id, payload, digest),
    )
    conn.commit()


def fetch_packet(conn: sqlite3.Connection, series_id: str) -> bytes:
    row = conn.execute(
        "SELECT payload FROM zpe_packets WHERE series_id = ?",
        (series_id,),
    ).fetchone()
    if not row:
        raise KeyError(f"series_id not found: {series_id}")
    return bytes(row[0])


def roundtrip_packet(conn: sqlite3.Connection, series_id: str, payload: bytes) -> Dict[str, object]:
    before_hash = sha256_bytes(payload)
    store_packet(conn, series_id, payload)
    reloaded = fetch_packet(conn, series_id)
    after_hash = sha256_bytes(reloaded)

    return {
        "series_id": series_id,
        "before_hash": before_hash,
        "after_hash": after_hash,
        "bit_consistent": before_hash == after_hash,
        "payload_bytes": len(payload),
    }


def fault_inject_corruption(payload: bytes) -> bytes:
    if not payload:
        return payload
    idx = min(len(payload) - 1, 13)
    corrupted = bytearray(payload)
    corrupted[idx] ^= 0x7F
    return bytes(corrupted)


def chunk_and_reorder(conn: sqlite3.Connection, series_id: str, payload: bytes, chunk_size: int = 64) -> bytes:
    conn.execute("DELETE FROM zpe_chunks WHERE series_id = ?", (series_id,))
    chunks = [payload[i : i + chunk_size] for i in range(0, len(payload), chunk_size)]
    for idx, chunk in enumerate(chunks):
        conn.execute(
            "INSERT INTO zpe_chunks (series_id, chunk_index, payload) VALUES (?, ?, ?)",
            (series_id, idx, chunk),
        )
    conn.commit()

    rows = conn.execute(
        "SELECT payload FROM zpe_chunks WHERE series_id = ? ORDER BY chunk_index DESC",
        (series_id,),
    ).fetchall()
    return b"".join(bytes(row[0]) for row in rows)


def db_file_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    return os.path.getsize(path)
