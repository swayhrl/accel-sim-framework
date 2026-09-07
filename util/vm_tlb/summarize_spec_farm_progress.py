#!/usr/bin/env python3
"""Low-memory semantic progress ledger across fresh retry job lists."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["stage"].replace("_SMOKE", "").replace("_FULL", ""), row["config_id"], row["roi"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--canonical-jobs", type=Path, required=True)
    parser.add_argument("--jobs-source", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"FAIL output exists: {args.output}")
    sources = [row for source in args.jobs_source for row in read(source)]
    by_run = {row["run_id"]: row for row in sources}
    terminal: dict[tuple[str, str, str], dict[str, str]] = {}
    for result in read(args.summary):
        job = by_run.get(result["run_id"])
        if job and result.get("exit_status") == "0" and result.get("status") != "FAILED":
            terminal[key(job)] = result
    rows=[]
    for job in read(args.canonical_jobs):
        result=terminal.get(key(job))
        rows.append({"stage":job["stage"],"config_id":job["config_id"],"roi":job["roi"],
                     "semantic_status":"COMPLETE" if result else "MISSING",
                     "realized_run_id":result["run_id"] if result else "NONE",
                     "rss_kb":result["rss_kb"] if result else "NONE",
                     "wall_seconds":result["wall_seconds"] if result else "NONE",
                     "ipc":result["gpu_tot_ipc"] if result else "NONE",
                     "l2_tlb_misses":result["vm_l2_tlb_misses"] if result else "NONE"})
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),delimiter="\t",lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
    print(f"PASS complete={sum(r['semantic_status']=='COMPLETE' for r in rows)} missing={sum(r['semantic_status']=='MISSING' for r in rows)} output={args.output}")


if __name__ == '__main__':
    main()
