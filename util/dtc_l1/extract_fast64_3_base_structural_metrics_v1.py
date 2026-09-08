#!/usr/bin/env python3
"""Extract source-defined conventional Base structural counters from perf CSV.

This is a future-only FAST64.3 companion extractor.  It intentionally does
not modify the frozen R2 parser or any row result.  ``LINE_ALLOC_FAIL`` is a
conventional L1D cache-line reservation failure, not a Tag-bank conflict.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path


FAMILY = {
    "cacheline_all_lines_reserved_events": re.compile(
        r"^L1D_\d+_GLOBAL_ACC_[RW]_LINE_ALLOC_FAIL$"),
    "miss_queue_downstream_full_events": re.compile(
        r"^L1D_\d+_GLOBAL_ACC_[RW]_MISS_QUEUE_FULL$"),
    "mshr_entry_full_events": re.compile(
        r"^L1D_\d+_GLOBAL_ACC_[RW]_MSHR_ENRTY_FAIL$"),
    "mshr_merge_full_events": re.compile(
        r"^L1D_\d+_GLOBAL_ACC_[RW]_MSHR_MERGE_ENRTY_FAIL$"),
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_perf(path: Path) -> tuple[list[str], list[str], int]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = next(reader)
        except StopIteration as error:
            raise SystemExit("empty perf CSV") from error
        rows = [row for row in reader if row]
    if not rows:
        raise SystemExit("perf CSV has no data row")
    if any(len(row) != len(header) for row in rows):
        raise SystemExit("perf CSV has ragged data rows")
    return header, rows[-1], len(rows)


def family_total(header: list[str], row: list[str], regex: re.Pattern[str]) -> tuple[int, int]:
    indices = [i for i, key in enumerate(header) if regex.fullmatch(key)]
    if not indices:
        raise SystemExit("required perf field family absent: " + regex.pattern)
    try:
        values = [int(row[i]) for i in indices]
    except ValueError as error:
        raise SystemExit("nonnumeric terminal perf counter") from error
    return sum(values), len(indices)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--perf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    metrics = summary.get("metrics", {})
    if metrics.get("DTC_L1_mode") != "PAPER_BASE":
        raise SystemExit("structural extractor applies only to PAPER_BASE")
    header, last, row_count = parse_perf(args.perf)
    totals: dict[str, int] = {}
    columns: dict[str, int] = {}
    for name, regex in FAMILY.items():
        totals[name], columns[name] = family_total(header, last, regex)

    # Core prints these same aggregate L1D MSHR counters in the terminal log.
    for extracted, terminal in (
        ("mshr_entry_full_events", "DTC_L1_baseline_mshr_entry_full_events"),
        ("mshr_merge_full_events", "DTC_L1_baseline_mshr_merge_full_events"),
    ):
        if metrics.get(terminal) != totals[extracted]:
            raise SystemExit(f"terminal summary disagrees with perf {extracted}")

    result = {
        "schema": "FAST64_3_BASE_STRUCTURAL_METRICS_V1",
        "classification": "PRECOMPUTED_STRUCTURAL_METRIC_COMPANION_NOT_FAST64_3_PASS",
        "metric_semantics": {
            "cacheline_all_lines_reserved_events": (
                "L1D GLOBAL LINE_ALLOC_FAIL; cache_reservation_fail_reason "
                "defines this as all lines reserved"),
            "tag_bank_conflicts": "terminal DTC_L1_tag_conflicts; diagnostic only",
            "mshr_entry_full_events": "L1D GLOBAL MSHR_ENRTY_FAIL",
            "mshr_merge_full_events": "L1D GLOBAL MSHR_MERGE_ENRTY_FAIL",
            "miss_queue_downstream_full_events": "L1D GLOBAL MISS_QUEUE_FULL",
            "live_miss_lifecycle": "terminal lower requests acquired/released",
        },
        "source_summary": str(args.summary),
        "source_summary_sha256": digest(args.summary),
        "source_perf": str(args.perf),
        "source_perf_sha256": digest(args.perf),
        "terminal_perf_rows": row_count,
        "perf_columns_per_family": columns,
        "metrics": {
            **totals,
            "tag_bank_conflicts": metrics.get("DTC_L1_tag_conflicts"),
            "tag_requests": metrics.get("DTC_L1_tag_requests"),
            "live_miss_lower_acquired": metrics.get("DTC_L1_lower_requests_acquired"),
            "live_miss_lower_released": metrics.get("DTC_L1_lower_requests_released"),
            "terminal_lower_outstanding": metrics.get("DTC_L1_lower_outstanding"),
            "terminal_pib_occupancy": metrics.get("DTC_L1_pib_occupancy"),
            "cycles": metrics.get("gpu_tot_sim_cycle"),
            "instructions": metrics.get("gpu_tot_sim_insn"),
        },
    }
    required = result["metrics"]
    if any(value is None for value in required.values()):
        raise SystemExit("terminal summary lacks a required Base companion metric")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("FAST64_3_BASE_STRUCTURAL_METRICS_V1_PASS output=" + str(args.output))


if __name__ == "__main__":
    main()
