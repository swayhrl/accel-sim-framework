#!/usr/bin/env python3
"""Write a tiny B-owned host-pressure snapshot for an opportunistic job."""
from __future__ import annotations

import argparse
import csv
import shutil
import time
from pathlib import Path


def field(path: str, wanted: set[str]) -> dict[str, int]:
    result: dict[str, int] = {}
    for raw in Path(path).read_text().splitlines():
        parts = raw.replace(":", "").split()
        if parts and parts[0] in wanted:
            result[parts[0]] = int(parts[1])
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("before", "after"), required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"FAIL snapshot exists: {args.output}")
    mem = field("/proc/meminfo", {"MemAvailable", "SwapFree"})
    vm = field("/proc/vmstat", {"pswpin", "pswpout", "pgmajfault"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("timestamp_utc", "phase", "memavailable_kb", "swapfree_kb", "swapins", "swapouts", "major_faults", "scratch_free_bytes"), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerow({"timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "phase": args.phase,
                         "memavailable_kb": mem.get("MemAvailable", 0), "swapfree_kb": mem.get("SwapFree", 0),
                         "swapins": vm.get("pswpin", 0), "swapouts": vm.get("pswpout", 0),
                         "major_faults": vm.get("pgmajfault", 0), "scratch_free_bytes": shutil.disk_usage('/workspace/vm-spec-farm').free})


if __name__ == "__main__":
    main()
