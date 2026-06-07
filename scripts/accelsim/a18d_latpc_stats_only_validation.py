#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, ensure_local_dirs, latest, read_csv, rel, ts, write_csv, write_stage_report


def as_float(value: str) -> float | None:
    try:
        if value in {"", "NA"}:
            return None
        return float(value)
    except ValueError:
        return None


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    results_path = latest("A18C_latpc_stats_probe_results_*.csv")
    latpc_path = latest("A18C_latpc_extracted_latpc_stats_*.csv")
    spec_path = latest("A18A_latpc_stats_field_spec_*.csv")
    matrix_csv = REPORT_DIR / f"A18D_latpc_behavior_validation_matrix_{stamp}.csv"
    summary_csv = REPORT_DIR / f"A18D_latpc_stats_presence_{stamp}.csv"
    report = REPORT_DIR / f"A18D_latpc_stats_only_validation_report_{stamp}.md"
    status = "PASS"
    blocker = "none"
    matrix_rows: list[dict[str, str]] = []
    presence_rows: list[dict[str, str]] = []
    if not results_path or not latpc_path or not spec_path:
        status = "BLOCKED_MISSING_INPUT"
        blocker = "missing A18C results/latpc stats or A18A spec"
    else:
        results = read_csv(results_path)
        by_variant = {row["variant"]: row for row in results}
        base = by_variant.get("baseline")
        probe = by_variant.get("latpc_stats_only")
        if not base or not probe:
            status = "BLOCKED_MISSING_VARIANTS"
            blocker = "baseline and latpc_stats_only rows are required"
        else:
            for field in ["cycles", "instructions", "ipc", "l2_accesses", "l2_misses"]:
                b = as_float(base.get(field, ""))
                p = as_float(probe.get(field, ""))
                if b is None or p is None:
                    result = "WARN_UNPARSED"
                    delta = "NA"
                else:
                    delta_v = p - b
                    delta = str(delta_v)
                    result = "PASS" if abs(delta_v) <= 0.0001 else "FAIL_BEHAVIOR_CHANGED"
                if result == "FAIL_BEHAVIOR_CHANGED":
                    status = "FAIL_BEHAVIOR_CHANGED"
                    blocker = f"{field} changed between baseline and stats-only"
                matrix_rows.append({"field": field, "baseline": base.get(field, ""), "latpc_stats_only": probe.get(field, ""), "delta": delta, "result": result})
        latpc_stats = read_csv(latpc_path)
        printed = {row["stat_key"] for row in latpc_stats}
        spec = read_csv(spec_path)
        for row in spec:
            if row.get("required_in_a18_probe") == "yes":
                present = row["stat_key"] in printed
                presence_rows.append({"stat_key": row["stat_key"], "required": "yes", "present": str(present).lower(), "result": "PASS" if present else "FAIL_MISSING_IMPLEMENTED_STAT"})
                if not present and not status.startswith("FAIL"):
                    status = "FAIL_MISSING_IMPLEMENTED_STAT"
                    blocker = f"missing implemented stat {row['stat_key']}"
    write_csv(matrix_csv, matrix_rows, ["field", "baseline", "latpc_stats_only", "delta", "result"])
    write_csv(summary_csv, presence_rows, ["stat_key", "required", "present", "result"])
    write_stage_report(
        report,
        "A18D LATPC Stats-Only Validation",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a18d_latpc_stats_only_validation.py"],
        [rel(results_path) if results_path else "", rel(latpc_path) if latpc_path else "", rel(spec_path) if spec_path else ""],
        [rel(matrix_csv), rel(summary_csv), rel(report)],
        blocker,
        ["Behavior validation compares bounded probe rows only.", "Implemented stats are metadata/sentinel fields, not LATPC mechanism counters."],
    )
    print(f"A18D status: {status}")
    print(f"A18D behavior matrix: {rel(matrix_csv)}")
    print(f"A18D stats presence: {rel(summary_csv)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
