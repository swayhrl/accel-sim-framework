#!/usr/bin/env python3
"""Prove scientific files and external raw/binary are unchanged from original commit."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--pack-rel", required=True)
    p.add_argument("--original-head", required=True)
    p.add_argument("--binary", type=Path, required=True)
    p.add_argument("--historical-binary-sha", required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    fixed = ["ANALYSIS_RECEIPT.json", "CORRECTNESS.tsv", "FINAL_DECISION.json",
             "GPU_IDENTITY.json", "GPU_LOCK_RECEIPT.json", "LAUNCH_AUDIT.tsv",
             "MAPPING_INVOCATION_RECEIPT.tsv", "NCU_KERNEL_ROWS.tsv", "RAW_INDEX.tsv",
             "RESIDUAL_PARALLELISM_SUMMARY.tsv", "SCIENTIFIC_INTERPRETATION.md",
             "TIMING_SAMPLES.tsv", "TIMING_SUMMARY.tsv", "VALIDATION_RECEIPT.json"]
    tree_names = subprocess.check_output(["git", "-C", str(args.repo), "ls-tree", "-r", "--name-only", args.original_head, args.pack_rel], text=True).splitlines()
    raw_names = [Path(x).name for x in tree_names if Path(x).name.startswith("RAW_ncu_") and x.endswith(".csv")]
    names = fixed + sorted(raw_names)
    rows = []
    pack = args.repo / args.pack_rel
    for name in names:
        spec = f"{args.original_head}:{args.pack_rel}/{name}"
        original = subprocess.check_output(["git", "-C", str(args.repo), "show", spec])
        current = (pack / name).read_bytes()
        rows.append({"file": name, "original_sha256": sha_bytes(original),
                     "current_sha256": sha_bytes(current), "unchanged": original == current})
    if not all(r["unchanged"] for r in rows):
        raise RuntimeError("scientific payload changed")
    external = []
    with (pack / "RAW_INDEX.tsv").open(newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            path = Path(row["path"])
            actual = sha_file(path)
            external.append({"artifact": row["artifact"], "path": str(path),
                             "recorded_sha256": row["sha256"], "actual_sha256": actual,
                             "unchanged": actual == row["sha256"]})
    if not all(r["unchanged"] for r in external):
        raise RuntimeError("external raw artifact changed")
    binary_sha = sha_file(args.binary)
    if binary_sha != args.historical_binary_sha:
        raise RuntimeError("binary changed")
    correctness_sha = next(r["current_sha256"] for r in rows if r["file"] == "CORRECTNESS.tsv")
    result = {"status": "PASS", "original_science_commit": args.original_head,
              "scientific_files_checked": len(rows), "scientific_files": rows,
              "external_raw_artifacts_checked": len(external), "external_raw_all_unchanged": True,
              "correctness_and_output_hash_record_sha256": correctness_sha,
              "binary": {"path": str(args.binary), "historical_sha256": args.historical_binary_sha,
                         "actual_sha256": binary_sha, "unchanged": True}}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "scientific_files_checked": len(rows),
                      "external_raw_artifacts_checked": len(external), "binary_unchanged": True}, sort_keys=True))


if __name__ == "__main__":
    main()
