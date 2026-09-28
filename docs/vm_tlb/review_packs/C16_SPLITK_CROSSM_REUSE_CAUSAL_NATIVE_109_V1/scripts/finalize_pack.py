#!/usr/bin/env python3
"""Copy bounded evidence, validate closure, and generate durable hashes."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def truth(value):
    return value.lower() == "true"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    args = p.parse_args()

    copies = {
        "CAMPAIGN_GPU_IDENTITY.json": "GPU_IDENTITY.json",
        "CORRECTNESS.tsv": "CORRECTNESS.tsv",
        "GPU_LOCK_RECEIPT.json": "GPU_LOCK_RECEIPT.json",
        "REPLICA_BINDINGS.tsv": "REPLICA_BINDINGS.tsv",
        "TIMING_SAMPLES.tsv": "TIMING_SAMPLES.tsv",
        "TIMING_SUMMARY.tsv": "TIMING_SUMMARY.tsv",
    }
    for src, dst in copies.items():
        shutil.copyfile(args.raw / src, args.pack / dst)
    for src in sorted(args.raw.glob("ncu_*.csv")):
        copies[src.name] = "RAW_" + src.name
        shutil.copyfile(src, args.pack / copies[src.name])

    with (args.pack / "CORRECTNESS.tsv").open(newline="") as f:
        correctness = list(csv.DictReader(f, delimiter="\t"))
    if len(correctness) != 6 or not all(truth(r["pass"]) for r in correctness):
        raise RuntimeError("correctness closure failed")

    with (args.pack / "REPLICA_BINDINGS.tsv").open(newline="") as f:
        bindings = list(csv.DictReader(f, delimiter="\t"))
    if len(bindings) != 96 or not all(truth(r["identity_pass"]) for r in bindings):
        raise RuntimeError("replica identity closure failed")
    for k in (2560, 3072):
        for tensor in ("qweight", "qzeros", "scales"):
            ranges = sorted((int(r["va_start"]), int(r["va_end"])) for r in bindings
                            if int(r["K"]) == k and r["tensor"] == tensor)
            if len(ranges) != 16 or any(a[1] > b[0] for a, b in zip(ranges, ranges[1:])):
                raise RuntimeError(f"VA range overlap K={k} tensor={tensor}")

    with (args.pack / "TIMING_SAMPLES.tsv").open(newline="") as f:
        timing = list(csv.DictReader(f, delimiter="\t"))
    counts = {}
    for row in timing:
        key = (int(row["K"]), int(row["split"]), row["state"])
        counts[key] = counts.get(key, 0) + 1
    if len(timing) != 400 or len(counts) != 8 or set(counts.values()) != {50}:
        raise RuntimeError("timing matrix closure failed")
    if len({r["function_identity"] for r in timing}) != 1:
        raise RuntimeError("runtime function identity differs")

    raw_index = []
    for path in sorted(p for p in args.raw.iterdir() if p.is_file()):
        raw_index.append((path.name, str(path), path.stat().st_size, sha(path), copies.get(path.name, "INDEX_ONLY")))
    with (args.pack / "RAW_INDEX.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(("artifact", "path", "bytes", "sha256", "committed_copy"))
        w.writerows(raw_index)

    receipt = {
        "status": "PASS",
        "correctness_rows": len(correctness),
        "replica_binding_rows": len(bindings),
        "timing_samples": len(timing),
        "timing_cells": len(counts),
        "samples_per_cell": sorted(set(counts.values())),
        "ncu_csv_profiles": len(list(args.raw.glob("ncu_*.csv"))),
        "runtime_function_identities": len({r["function_identity"] for r in timing}),
        "raw_root": str(args.raw),
    }
    if receipt["ncu_csv_profiles"] != 8:
        raise RuntimeError("NCU profile closure failed")
    (args.pack / "VALIDATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    entries = []
    for path in sorted(p for p in args.pack.rglob("*") if p.is_file() and p.name != "SHA256SUMS" and "__pycache__" not in p.parts):
        entries.append(f"{sha(path)}  {path.relative_to(args.pack)}")
    (args.pack / "SHA256SUMS").write_text("\n".join(entries) + "\n")


if __name__ == "__main__":
    main()
