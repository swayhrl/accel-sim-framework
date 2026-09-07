#!/usr/bin/env python3
"""Generate a fresh-run retry TSV only for semantically missing farm rows."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        rows = list(csv.DictReader(source, delimiter="\t"))
    if not rows:
        raise SystemExit(f"FAIL empty jobs source: {path}")
    return rows


def key(row: dict[str, str]) -> tuple[str, str, str]:
    return row["stage"].replace("_SMOKE", "").replace("_FULL", ""), row["config_id"], row["roi"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--jobs-source", type=Path, action="append", required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.attempt.startswith("retry"):
        raise SystemExit("FAIL output must be fresh and attempt must begin retry")
    all_rows = [row for source in args.jobs_source for row in read_rows(source)]
    by_run = {row["run_id"]: row for row in all_rows}
    complete: set[tuple[str, str, str]] = set()
    with args.summary.open(newline="") as source:
        for result in csv.DictReader(source, delimiter="\t"):
            job = by_run.get(result["run_id"])
            if job and result.get("exit_status") == "0" and result.get("status") != "FAILED":
                complete.add(key(job))
    canonical = read_rows(args.jobs_source[0])
    missing = [row.copy() for row in canonical if key(row) not in complete]
    for row in missing:
        old_run_id = row["run_id"]
        row["run_id"] = f"{old_run_id}-{args.attempt}"
        # Jobs from build_spec_farm_jobs have a stable stage-kind run directory.
        stage_kind = Path(row["run_dir"]).parts[-3]
        row["run_dir"] = str(Path(row["run_dir"]).parents[2] / f"{stage_kind}-{args.attempt}" /
                             Path(row["run_dir"]).parts[-2] / Path(row["run_dir"]).name)
    if not missing:
        raise SystemExit("PASS no semantic rows missing")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(missing[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(missing)
    print(f"PASS missing_jobs={len(missing)} output={args.output}")


if __name__ == "__main__":
    main()
