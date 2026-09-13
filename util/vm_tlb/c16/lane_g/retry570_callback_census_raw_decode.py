#!/usr/bin/env python3
"""Decode the fixed-POD callback census buffer outside any NVBit callback."""
from __future__ import annotations

import argparse
import json
import re
import struct
from collections import Counter
from pathlib import Path

from c16_native_common import ContractError, atomic_json, sha256_file

HEADER = struct.Struct("<16sIIQQQQQ")
EVENT = struct.Struct("<QQQII")


def cuda_api_names(metadata: Path | None) -> dict[int, str]:
    """Decode NVBit's generated API table offline, never in the callback."""
    if metadata is None:
        return {}
    names: dict[int, str] = {}
    pattern = re.compile(r"ACTION\(\s*\w+\s*,\s*(\d+)\s*,\s*(\w+)\s*,")
    for ordinal, name in pattern.findall(metadata.read_text(encoding="utf-8", errors="replace")):
        numeric = int(ordinal)
        if numeric in names and names[numeric] != name:
            raise ContractError(f"ambiguous CUDA API cbid {numeric} in {metadata}")
        names[numeric] = name
    if not names:
        raise ContractError(f"no NVBit CUDA API metadata entries found in {metadata}")
    return names


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--cuda-api-meta", type=Path,
                        help="optional NVBit tools_cuda_api_meta.h, decoded offline only")
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
    names = cuda_api_names(args.cuda_api_meta)
    cbid_counts = Counter(event[3] for event in events)
    callback_summary = [
        {"cbid": cbid, "callback_name": names.get(cbid, "UNKNOWN"), "event_count": count}
        for cbid, count in sorted(cbid_counts.items())
    ]
    atomic_json(args.receipt, {
        "schema_version": "C16_G_RETRY570_CALLBACK_CENSUS_RAW_DECODE_V1",
        "raw_path": str(args.raw), "raw_bytes": len(blob), "raw_sha256": sha256_file(args.raw),
        "capacity": capacity, "event_size": event_size, "write_count": write_count,
        "dropped_count": dropped, "max_callback_depth": maximum_depth,
        "reentrant_callback_count": reentrant, "materialized_event_count": present,
        "first_event": list(events[0]) if events else None,
        "last_event": list(events[-1]) if events else None,
        "cuda_api_meta": str(args.cuda_api_meta) if args.cuda_api_meta else "NOT_PROVIDED",
        "callback_summary_offline": callback_summary,
        "scientific_eligible": False,
    })


if __name__ == "__main__":
    main()
