#!/usr/bin/env python3
"""Rebuild portable L2CHARV1 CSVs from canonical Round-1 raw logs.

This is intentionally parser-only: it neither starts a simulator nor changes
`run_status.json`.  The recorded source revisions are passed back to the
parser so an aggregation repair cannot rewrite run provenance to the host's
current Git HEAD.
"""
import argparse
import csv
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]


def summary(path):
    with path.open(newline="") as source:
        return next(csv.DictReader(source))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=pathlib.Path, default=ROOT / "docs/l2_char_v1/round1_results")
    parser.add_argument("--status", default="COMPLETE_VALID")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    selected = []
    for status_path in sorted(args.results.rglob("run_status.json")):
        status = json.loads(status_path.read_text())
        if status.get("status") == args.status:
            selected.append(status_path.parent)
    print(f"selected={len(selected)} status={args.status}")
    for directory in selected:
        row, manifest = summary(directory / "summary.csv"), json.loads((directory / "manifest.json").read_text())
        char = manifest["characterization"]
        command = [sys.executable, str(ROOT / "util/l2_char/parse_l2_char.py"), str(directory / "raw.log"),
                   "--out", str(directory), "--workload", row["workload"], "--input", row["input"],
                   "--kernel", row["kernel"], "--kernel-id", row["kernel_id"], "--config", row["gpu_config"],
                   "--trace", row["trace"], "--framework-repo", str(ROOT), "--core-repo",
                   str(pathlib.Path(row["gpu_config"]).parents[3]), "--framework-commit", row["framework_commit"],
                   "--core-commit", row["core_commit"], "--framework-branch", row["framework_branch"],
                   "--core-branch", row["core_branch"], "--command", row["command"], "--production",
                   "--window-l2-cycles", str(char["window_l2_cycles"]), "--set-detail", "1" if char["set_detail"] else "0",
                   "--emit-windows", "1" if char["emit_windows"] else "0"]
        print(f"REPARSE\t{directory}", flush=True)
        if not args.dry_run:
            subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
