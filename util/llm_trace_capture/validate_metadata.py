#!/usr/bin/env python3
"""Validate the M4A allocation sidecar without GPU dependencies."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SCHEMA = "m4a-allocation-sidecar-v1"
KINDS = {"WEIGHT", "KV_CACHE", "ACTIVATION", "WORKSPACE", "UNKNOWN"}
PHASES = {"MODEL_LOAD", "PREFILL", "DECODE"}


def number(value):
    if isinstance(value, int): return value
    if isinstance(value, str) and value.startswith("0x"): return int(value, 16)
    raise ValueError("address must be integer or 0x string")


def validate(data: dict, addresses: list[int] | None = None) -> dict:
    if data.get("schema_version") != SCHEMA: raise ValueError("wrong schema_version")
    run = data.get("run")
    if not isinstance(run, dict) or not isinstance(run.get("run_id"), str) or not run["run_id"]:
        raise ValueError("run.run_id is required")
    ranges = []
    for allocation in data.get("allocations", []):
        aid, kind = allocation.get("allocation_id"), allocation.get("object_kind")
        start, size = number(allocation.get("simva_start")), allocation.get("size_bytes")
        if not isinstance(aid, str) or not aid or kind not in KINDS or not isinstance(size, int) or size <= 0:
            raise ValueError("invalid allocation")
        ranges.append((start, start + size, aid, kind))
    ranges.sort()
    for left, right in zip(ranges, ranges[1:]):
        if right[0] < left[1]: raise ValueError(f"active range overlap: {left[2]} / {right[2]}")
    for phase in data.get("phases", []):
        if phase.get("name") not in PHASES: raise ValueError("invalid phase")
    layout = data.get("weight_layout")
    if layout is not None:
        if not isinstance(layout, dict) or layout.get("alignment_bytes") != 256:
            raise ValueError("invalid weight_layout alignment")
        weight = [r for r in ranges if r[2] == layout.get("allocation_id") and r[3] == "WEIGHT"]
        if len(weight) != 1: raise ValueError("weight_layout requires one WEIGHT allocation")
        prior = 0
        for tensor in layout.get("tensors", []):
            offset, size = tensor.get("offset_bytes"), tensor.get("size_bytes")
            if not isinstance(offset, int) or not isinstance(size, int) or size <= 0 or offset < prior or offset % 256:
                raise ValueError("invalid or overlapping weight tensor offset")
            prior = offset + size
        if prior > weight[0][1] - weight[0][0]: raise ValueError("weight layout exceeds allocation")
    coverage = {kind: 0 for kind in KINDS}
    unknown = 0
    for address in addresses or []:
        matches = [r for r in ranges if r[0] <= address < r[1]]
        if len(matches) > 1: raise ValueError("ambiguous trace address")
        if matches: coverage[matches[0][3]] += 1
        else: unknown += 1
    return {"allocations": len(ranges), "address_coverage": coverage, "unknown_addresses": unknown}


def self_test() -> None:
    sample = {"schema_version": SCHEMA, "run": {"run_id": "unit"}, "phases": [{"name": "PREFILL"}],
              "allocations": [{"allocation_id": "w", "simva_start": "0x1000", "size_bytes": 512, "object_kind": "WEIGHT"}],
              "weight_layout": {"allocation_id": "w", "alignment_bytes": 256, "tensors": [{"name": "x", "offset_bytes": 0, "size_bytes": 16}]}}
    result = validate(sample, [0x1000, 0x100f, 0x2000])
    assert result["address_coverage"]["WEIGHT"] == 2 and result["unknown_addresses"] == 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sidecar", nargs="?", type=Path)
    parser.add_argument("--addresses", type=Path, help="one hexadecimal SimVA per line")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: self_test(); print("PASS metadata self-test"); return 0
    if not args.sidecar: parser.error("sidecar is required")
    addresses = [int(x.strip(), 0) for x in args.addresses.read_text().splitlines() if x.strip()] if args.addresses else None
    result = validate(json.loads(args.sidecar.read_text()), addresses)
    print(json.dumps(result, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
