#!/usr/bin/env python3
"""Decode the fixed-POD callback census buffer outside any NVBit callback."""
from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path

from c16_native_common import ContractError, atomic_json, sha256_file

HEADER = struct.Struct("<16sIIQQQQQ")
EVENT = struct.Struct("<QQQII")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    blob = args.raw.read_bytes()
    if len(blob) < HEADER.size:
        raise ContractError("raw callback buffer is shorter than its fixed header")
    magic, version, event_size, capacity, write_count, dropped, maximum_depth, reentrant = HEADER.unpack_from(blob)
    if not magic.startswith(b"C16RAWCBV1") or version != 1 or event_size != EVENT.size:
        raise ContractError("raw callback buffer has an unexpected schema")
    present = min(write_count, capacity)
    expected = HEADER.size + capacity * EVENT.size
    if len(blob) != expected:
        raise ContractError("raw callback buffer size differs from fixed capacity")
    events = [EVENT.unpack_from(blob, HEADER.size + index * EVENT.size) for index in range(present)]
    atomic_json(args.receipt, {
        "schema_version": "C16_G_RETRY570_CALLBACK_CENSUS_RAW_DECODE_V1",
        "raw_path": str(args.raw), "raw_bytes": len(blob), "raw_sha256": sha256_file(args.raw),
        "capacity": capacity, "event_size": event_size, "write_count": write_count,
        "dropped_count": dropped, "max_callback_depth": maximum_depth,
        "reentrant_callback_count": reentrant, "materialized_event_count": present,
        "first_event": list(events[0]) if events else None,
        "last_event": list(events[-1]) if events else None,
        "scientific_eligible": False,
    })


if __name__ == "__main__":
    main()
