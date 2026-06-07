#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, clean, ensure_local_dirs, latest, read_csv, rel, selected_workload, ts, write_json, write_stage_report


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    loc = latest("A17B_latpc_localization_matrix_*.csv")
    design = latest("A17C_latpc_minimal_mechanism_design_*.md")
    gate_json = REPORT_DIR / f"A17D_latpc_readiness_gate_{stamp}.json"
    report = REPORT_DIR / f"A17D_latpc_readiness_gate_report_{stamp}.md"
    selected = selected_workload()
    mode = "DESIGN_ONLY_BLOCKED"
    status = "BLOCKED"
    blocker = "missing A17B localization"
    reasons: list[str] = []
    if loc:
        rows = read_csv(loc)
        print_only = any(row.get("area") == "stats_print" and row.get("a18_safe_stats_only_hook") == "YES_PRINT_ONLY" for row in rows)
        ptw_missing = any(row.get("area") == "page_walk_queue_ptw_pwc" and row.get("confidence") == "LOW" for row in rows)
        selected_ok = bool(clean(selected.get("selected_workload")))
        if print_only and selected_ok:
            mode = "PARTIAL_STATS_ONLY_INSTRUMENTATION"
            status = "PASS_WITH_WARNINGS"
            blocker = "no blocker for print-only stats; functional LATPC hooks remain unavailable"
            reasons = [
                "stats print path is localized with high confidence",
                "selected workload is available from A16",
                "page-walk/PTW/PWC and TLB-MSHR paths are not localized enough for functional or raw target counters",
            ]
            if ptw_missing:
                reasons.append("PTW/PWC missing keeps mode below FULL")
        else:
            reasons = ["required safe print path or selected workload was not available"]
    gate = {
        "round": "A17_A18",
        "readiness_mode": mode,
        "status": status,
        "a18b_simulator_source_modification_allowed": mode in {"PARTIAL_STATS_ONLY_INSTRUMENTATION", "FULL_STATS_ONLY_INSTRUMENTATION"},
        "a18b_allowed_change_scope": "print-only latpc_* metadata/sentinel stats in stats output path",
        "a18b_forbidden_change_scope": "queue size, latency, scheduling, TLB hit/miss, MSHR allocation, PTW issue, replay, prefetch behavior",
        "selected_workload": clean(selected.get("selected_workload")),
        "selected_workload_source": clean(selected.get("_source_path")),
        "reasons": reasons,
        "blocker": blocker,
        "localization_matrix": rel(loc) if loc else "",
        "design_doc": rel(design) if design else "",
    }
    write_json(gate_json, gate)
    extra = "\n".join(["## Gate Reasons", ""] + [f"- {reason}" for reason in reasons])
    write_stage_report(
        report,
        "A17D LATPC Readiness Gate",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a17d_latpc_readiness_gate.py"],
        [rel(loc) if loc else "", rel(design) if design else ""],
        [rel(gate_json), rel(report)],
        blocker,
        ["A17D only authorizes print-only A18B changes; it does not authorize functional mechanism work."],
        extra,
    )
    print(f"A17D status: {status}")
    print(f"A17D readiness mode: {mode}")
    print(f"A17D gate: {rel(gate_json)}")
    return 0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
