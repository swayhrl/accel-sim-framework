#!/usr/bin/env python3
"""Low-memory integrity audit for atomically completed B1 partials."""
from __future__ import annotations

import argparse
import csv
import lzma
import pickle
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--roi", required=True)
    parser.add_argument("--trace-list", type=Path, required=True)
    parser.add_argument("--partial-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"FAIL output exists: {args.output}")
    names = [x for x in args.trace_list.read_text().splitlines() if x]
    partials = sorted(args.partial_dir.glob("*.pkl.xz"))
    rows = []
    passed = 0
    seen: set[int] = set()
    for path in partials:
        try:
            index = int(path.name.split(".", 1)[0])
        except ValueError:
            rows.append({"roi": args.roi, "index": "MALFORMED", "partial": str(path), "trace": "MISSING", "result": "FAIL"})
            continue
        if index >= len(names):
            rows.append({"roi": args.roi, "index": index, "partial": str(path), "trace": "OUT_OF_RANGE", "result": "FAIL"})
            continue
        with lzma.open(path, "rb") as stream:
            record = pickle.load(stream)
        ok = record.get("schema") == "VM_SPEC_FARM_TRACE_PARTIAL_V1" and record.get("index") == index and record.get("trace") == names[index]
        rows.append({"roi": args.roi, "index": index, "partial": str(path), "trace": record.get("trace", "MISSING"), "result": "PASS" if ok else "FAIL"})
        if ok:
            passed += 1
            seen.add(index)
    for index in range(len(names)):
        if index not in seen:
            rows.append({"roi": args.roi, "index": index, "partial": "NONE", "trace": names[index], "result": "MISSING"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("roi", "index", "partial", "trace", "result"), delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    print(f"PASS roi={args.roi} valid_partials={passed} missing={len(names) - len(seen)} output={args.output}")
    if passed != len(partials):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
