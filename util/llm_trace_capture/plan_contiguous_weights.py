#!/usr/bin/env python3
"""Create and validate a deterministic, static contiguous weight-layout plan."""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SCHEMA = "m4a-contiguous-weight-layout-v1"


def align_up(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def build(payload: dict, alignment: int) -> dict:
    tensors = payload.get("tensors")
    if not isinstance(tensors, list) or not tensors:
        raise ValueError("input requires a non-empty tensors list")
    offset = 0
    rows = []
    names = set()
    for index, tensor in enumerate(tensors):
        if not isinstance(tensor, dict):
            raise ValueError(f"tensor {index} is not an object")
        name, nbytes = tensor.get("name"), tensor.get("nbytes")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError(f"tensor {index} has a missing or duplicate name")
        if not isinstance(nbytes, int) or nbytes <= 0:
            raise ValueError(f"tensor {name} has invalid nbytes")
        names.add(name)
        offset = align_up(offset, alignment)
        rows.append({"name": name, "offset_bytes": offset, "size_bytes": nbytes,
                     "source_index": index, "dtype": tensor.get("dtype", "UNKNOWN")})
        offset += nbytes
    out = {"schema_version": SCHEMA, "alignment_bytes": alignment,
           "tensor_order": "input order", "total_size_bytes": align_up(offset, alignment),
           "tensors": rows,
           "runtime_simva_start": "UNKNOWN_M4A_C_REQUIRED"}
    validate(out)
    return out


def validate(layout: dict) -> None:
    if layout.get("schema_version") != SCHEMA:
        raise ValueError("wrong layout schema")
    alignment = layout.get("alignment_bytes")
    if not isinstance(alignment, int) or alignment <= 0:
        raise ValueError("invalid alignment")
    previous_end = 0
    for row in layout.get("tensors", []):
        start, size = row.get("offset_bytes"), row.get("size_bytes")
        if not isinstance(start, int) or not isinstance(size, int) or start < previous_end or size <= 0:
            raise ValueError("overlapping or invalid tensor range")
        if start % alignment:
            raise ValueError("unaligned tensor offset")
        previous_end = start + size
    if previous_end > layout.get("total_size_bytes", -1):
        raise ValueError("layout total is too small")


def self_test() -> None:
    layout = build({"tensors": [{"name": "b", "nbytes": 3}, {"name": "a", "nbytes": 5}]}, 4)
    assert [x["name"] for x in layout["tensors"]] == ["b", "a"]
    assert [x["offset_bytes"] for x in layout["tensors"]] == [0, 4]
    try:
        build({"tensors": [{"name": "x", "nbytes": 1}, {"name": "x", "nbytes": 1}]}, 4)
    except ValueError:
        return
    raise AssertionError("duplicate tensor names must fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--alignment-bytes", type=int, default=256)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(); print("PASS contiguous-layout self-test"); return 0
    if not args.input or not args.output or args.alignment_bytes <= 0:
        parser.error("--input, --output, and positive --alignment-bytes are required")
    payload = json.loads(args.input.read_text())
    layout = build(payload, args.alignment_bytes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(layout, indent=2, sort_keys=True) + "\n")
    print(f"PASS layout={args.output} tensors={len(layout['tensors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
