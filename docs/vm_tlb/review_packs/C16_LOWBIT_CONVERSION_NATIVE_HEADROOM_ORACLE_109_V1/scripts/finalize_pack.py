#!/usr/bin/env python3
"""Validate bounded oracle outputs, copy evidence, index raw, and seal pack."""

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


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--raw", type=Path, required=True)
    p.add_argument("--failed-raw", type=Path, required=True)
    p.add_argument("--pack", type=Path, required=True)
    p.add_argument("--build-root", type=Path, required=True)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--binary-sha", required=True)
    args = p.parse_args()
    copies = {
        "CORRECTNESS.tsv": "CORRECTNESS.tsv", "DISCOVERY_GATE.json": "DISCOVERY_GATE.json",
        "GPU_IDENTITY.json": "GPU_IDENTITY.json", "GPU_LOCK_RECEIPT.json": "GPU_LOCK_RECEIPT.json",
        "ORACLE_DEPENDENCY_CANARIES.tsv": "ORACLE_DEPENDENCY_CANARIES.tsv",
        "TARGET_SUMMARY.json": "TARGET_SUMMARY.json", "TIMING_SAMPLES.tsv": "TIMING_SAMPLES.tsv",
        "TIMING_SUMMARY.tsv": "TIMING_SUMMARY.tsv",
    }
    for src, dst in copies.items():
        shutil.copyfile(args.raw / src, args.pack / dst)
    shutil.copyfile(args.failed_raw / "GPU_LOCK_RECEIPT.json", args.pack / "FAILED_PREFLIGHT_GPU_LOCK_RECEIPT.json")

    with (args.pack / "TIMING_SAMPLES.tsv").open(newline="") as f:
        timing = list(csv.DictReader(f, delimiter="\t"))
    counts = {}
    for row in timing:
        counts[(row["target"], row["condition"])] = counts.get((row["target"], row["condition"]), 0) + 1
    if len(timing) != 150 or set(counts) != {("discovery", x) for x in ("A", "B", "C")} or set(counts.values()) != {50}:
        raise RuntimeError("timing closure failed or validation was unexpectedly executed")
    gate = json.loads((args.pack / "DISCOVERY_GATE.json").read_text())
    if gate["validation_authorized"] or gate["decision"] != "STOP_AFTER_DISCOVERY":
        raise RuntimeError("discovery gate closure failed")
    with (args.pack / "CORRECTNESS.tsv").open(newline="") as f:
        correctness = list(csv.DictReader(f, delimiter="\t"))
    if len(correctness) != 1 or correctness[0]["baseline_authority_pass"] != "True" or correctness[0]["predecoded_correct"] != "True":
        raise RuntimeError("correctness closure failed")
    with (args.pack / "ORACLE_DEPENDENCY_CANARIES.tsv").open(newline="") as f:
        canaries = list(csv.DictReader(f, delimiter="\t"))
    if len(canaries) != 3 or not all(r["pass"] == "True" and int(r["changed_output_elements"]) > 0 for r in canaries):
        raise RuntimeError("oracle dependency canary closure failed")
    if sha(args.binary) != args.binary_sha:
        raise RuntimeError("binary identity changed")

    raw_index = []
    committed = {str(args.raw / src): dst for src, dst in copies.items()}
    committed[str(args.failed_raw / "GPU_LOCK_RECEIPT.json")] = "FAILED_PREFLIGHT_GPU_LOCK_RECEIPT.json"
    roots = (("formal_raw", args.raw), ("failed_preflight_raw", args.failed_raw))
    for group, root in roots:
        for path in sorted(x for x in root.iterdir() if x.is_file()):
            raw_index.append((group, path.name, str(path), path.stat().st_size, sha(path), committed.get(str(path), "INDEX_ONLY")))
    build_files = [args.build_root / name for name in (
        "build.log", "oracle_full.sass", "accepted_target.sass", "baseline_target.sass", "oracle_target.sass",
        "resource_usage.txt", "accepted_resource_usage.txt")]
    build_files.append(args.binary)
    for path in build_files:
        raw_index.append(("static_build", path.name, str(path), path.stat().st_size, sha(path), "INDEX_ONLY"))
    with (args.pack / "RAW_INDEX.tsv").open("w", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(("group", "artifact", "path", "bytes", "sha256", "committed_copy"))
        w.writerows(raw_index)
    receipt = {"status": "PASS", "timing_samples": len(timing), "timing_cells": len(counts),
               "samples_per_cell": sorted(set(counts.values())), "validation_executed": False,
               "correctness_rows": len(correctness), "dependency_canaries": len(canaries),
               "failed_preflight_timing_samples": 0, "raw_index_rows": len(raw_index),
               "binary_sha256": args.binary_sha}
    (args.pack / "VALIDATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    lines = []
    for path in sorted(x for x in args.pack.rglob("*") if x.is_file() and x.name != "SHA256SUMS" and "__pycache__" not in x.parts):
        lines.append(f"{sha(path)}  {path.relative_to(args.pack)}")
    (args.pack / "SHA256SUMS").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
