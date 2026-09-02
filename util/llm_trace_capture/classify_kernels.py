#!/usr/bin/env python3
"""Create non-destructive full and compute-only kernel-list derivatives."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

NCCL = re.compile(r"(?:nccl|allreduce|all_gather|reduce_scatter|broadcast)", re.I)
# The frozen tracer emits MemcpyHtoD; recognize other future memcpy forms
# conservatively rather than presenting them as compute.
MEMCPY = re.compile(r"(?:^|[^a-z])memcpy(?:htod|dtoh|dtod|peer|async)?", re.I)


def classify(name: str) -> str:
    if not name.strip() or name.lstrip().startswith("#"):
        return "UNKNOWN_OTHER"
    if MEMCPY.search(name):
        return "MEMCPY"
    if NCCL.search(name):
        return "NCCL_COLLECTIVE"
    return "COMPUTE"


def build(lines: list[str]) -> list[dict]:
    return [{"index": index, "raw": line, "classification": classify(line)} for index, line in enumerate(lines)]


def self_test() -> None:
    raw = ["gemm_kernel", "ncclAllReduceKernel", "MemcpyHtoD,0x0001,64", "# malformed"]
    rows = build(raw)
    assert [row["classification"] for row in rows] == ["COMPUTE", "NCCL_COLLECTIVE", "MEMCPY", "UNKNOWN_OTHER"]
    assert [row["raw"] for row in rows] == raw and [row["index"] for row in rows] == list(range(len(raw)))
    assert classify("MemcpyHtoD,0x0002,128") != "COMPUTE"
    assert [row["raw"] for row in rows if row["classification"] == "COMPUTE"] == ["gemm_kernel"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kernelslist", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test(); print("PASS kernel classifier self-test: COMPUTE/NCCL/MEMCPY/UNKNOWN"); return 0
    if not args.kernelslist or not args.output_dir:
        parser.error("--kernelslist and --output-dir are required")
    raw = args.kernelslist.read_text().splitlines()
    rows = build(raw)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": "m4a-kernel-classification-v2",
        "source": str(args.kernelslist),
        "source_sha256": hashlib.sha256(args.kernelslist.read_bytes()).hexdigest(),
        "rules": {"NCCL_COLLECTIVE": NCCL.pattern, "MEMCPY": MEMCPY.pattern,
                  "COMPUTE": "non-empty entry not matching NCCL or MEMCPY",
                  "UNKNOWN_OTHER": "empty/comment"},
        "kernels": rows,
    }
    (args.output_dir / "full-kernel-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    # Preserve raw source untouched; this list is a diagnostic derivative only.
    compute = "\n".join(row["raw"] for row in rows if row["classification"] == "COMPUTE") + "\n"
    (args.output_dir / "compute-only-kernelslist.g").write_text(compute)
    (args.output_dir / "classification-command.txt").write_text(" ".join(sys.argv) + "\n")
    print(f"PASS raw_retained={args.kernelslist} full_manifest={args.output_dir/'full-kernel-manifest.json'} compute_only={args.output_dir/'compute-only-kernelslist.g'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
