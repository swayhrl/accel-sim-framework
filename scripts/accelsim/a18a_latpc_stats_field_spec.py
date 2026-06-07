#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, ensure_local_dirs, latest, read_csv, read_json, rel, ts, write_csv, write_stage_report


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    gate_path = latest("A17D_latpc_readiness_gate_*.json")
    target_path = latest("A17A_latpc_target_stats_*.csv")
    spec_csv = REPORT_DIR / f"A18A_latpc_stats_field_spec_{stamp}.csv"
    report = REPORT_DIR / f"A18A_latpc_stats_field_spec_report_{stamp}.md"
    status = "PASS"
    blocker = "none"
    mode = "UNKNOWN"
    if not gate_path or not target_path:
        status = "BLOCKED_MISSING_INPUT"
        blocker = "missing A17D gate or A17A target stats"
        rows = []
    else:
        mode = read_json(gate_path).get("readiness_mode", "UNKNOWN")
        targets = read_csv(target_path)
        rows = []
        for row in targets:
            key = row["stat_key"]
            if key in {"latpc_stats_only_marker", "latpc_stats_only_version", "latpc_functional_mechanism_enabled"} and mode != "DESIGN_ONLY_BLOCKED":
                cls = "IMPLEMENTED"
                source = "gpu_print_stat print-only sentinel"
            elif key in {"latpc_tlb_miss_rate_l1", "latpc_tlb_miss_rate_l2"}:
                cls = "DERIVED"
                source = "derived only when raw TLB counters become available"
            elif "prefetch" in key or "regular_stream" in key or "merge_candidate" in key:
                cls = "DEFERRED"
                source = "future LATPC mechanism or detector"
            else:
                cls = "UNAVAILABLE"
                source = "no safe localized TLB/PTW/MSHR runtime hook in A17B"
            rows.append({
                "stat_key": key,
                "status_class": cls,
                "unit": "count_or_ratio",
                "source_or_formula": source,
                "required_in_a18_probe": "yes" if cls == "IMPLEMENTED" else "no",
                "notes": row.get("semantic", ""),
            })
    write_csv(spec_csv, rows, ["stat_key", "status_class", "unit", "source_or_formula", "required_in_a18_probe", "notes"])
    implemented = len([row for row in rows if row.get("status_class") == "IMPLEMENTED"])
    extra = f"## Field Counts\n\n- Readiness mode: `{mode}`\n- IMPLEMENTED fields required in A18 probe: {implemented}\n"
    write_stage_report(
        report,
        "A18A LATPC Stats Field Spec",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a18a_latpc_stats_field_spec.py"],
        [rel(gate_path) if gate_path else "", rel(target_path) if target_path else ""],
        [rel(spec_csv), rel(report)],
        blocker,
        ["All fields use the latpc_ prefix.", "Most paper-target counters remain unavailable or deferred until real TLB/PTW hooks exist."],
        extra,
    )
    print(f"A18A status: {status}")
    print(f"A18A spec: {rel(spec_csv)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
