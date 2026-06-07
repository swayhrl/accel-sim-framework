#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, ensure_local_dirs, latest, read_csv, rel, ts, write_csv, write_stage_report


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    loc = latest("A17B_latpc_localization_matrix_*.csv")
    design_md = REPORT_DIR / f"A17C_latpc_minimal_mechanism_design_{stamp}.md"
    plan_csv = REPORT_DIR / f"A17C_latpc_future_implementation_plan_{stamp}.csv"
    report = REPORT_DIR / f"A17C_latpc_design_report_{stamp}.md"
    status = "PASS_WITH_WARNINGS"
    blocker = "none"
    if not loc:
        status = "BLOCKED_NO_A17B"
        blocker = "missing A17B localization matrix"
        rows = []
    else:
        rows = read_csv(loc)
    future_rows = [
        {"component": "Regularity Detector", "future_hook": "warp memory instruction address/VPN observation", "required_guardrail": "no timing changes until mechanism implementation round", "a18_action": "defer functional detector; document unavailable raw target stats"},
        {"component": "LATC", "future_hook": "translation cache/coalescer state and miss merge path", "required_guardrail": "must be attached to real TLB/PTW model", "a18_action": "do not implement"},
        {"component": "LATP", "future_hook": "translation prefetch issue path and page-walk queue model", "required_guardrail": "must not be modeled as data prefetch or scheduler shortcut", "a18_action": "do not implement"},
        {"component": "Stats-only instrumentation", "future_hook": "gpgpu_sim::gpu_print_stat", "required_guardrail": "print-only latpc_* fields; no queue/scheduler/cache/TLB mutation", "a18_action": "allowed if A17D permits PARTIAL/FULL"},
    ]
    write_csv(plan_csv, future_rows, ["component", "future_hook", "required_guardrail", "a18_action"])
    design_md.write_text(f"""# A17C LATPC Minimal Mechanism Design

This document defines the design boundary for A17/A18. It does not implement
LATPC and does not claim paper speedup reproduction.

## Current Localization Summary

Source localization found safe address-observation and stats-printing code, but
did not localize a complete page-walk, PWC, or TLB-MSHR control path suitable for
mechanism work.

## Minimal Future Mechanism Shape

- Regularity Detector: observe per-warp memory-reference page numbers, classify
  regular page strides, and expose confidence/coverage counters.
- LATC: model translation coalescing/cache state only after the repository's
  actual TLB and translation-miss structures are identified.
- LATP: issue translation prefetches through the real translation miss/page-walk
  pipeline, never through data-cache prefetch or scheduler shortcuts.

## A18 Boundary

A18 may add print-only `latpc_*` metadata/sentinel stats if A17D allows
`PARTIAL_STATS_ONLY_INSTRUMENTATION` or `FULL_STATS_ONLY_INSTRUMENTATION`.
It must not modify queue capacity, latency, scheduling, TLB hit/miss behavior,
MSHR allocation, PTW issue policy, replay behavior, or prefetch behavior.

## Inputs

- A17B localization matrix: `{rel(loc) if loc else ''}`
- Localized rows: {len(rows)}
""")
    write_stage_report(
        report,
        "A17C LATPC Minimal Mechanism Design",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a17c_latpc_minimal_design.py"],
        [rel(loc) if loc else ""],
        [rel(design_md), rel(plan_csv), rel(report)],
        blocker,
        ["A17C is design-only.", "Functional LATPC mechanism work is explicitly deferred."],
    )
    print(f"A17C status: {status}")
    print(f"A17C design: {rel(design_md)}")
    return 0 if not status.startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
