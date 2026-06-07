#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import REPORT_DIR, ensure_dirs, latest, rel, stage_report, ts, write_csv


def classification(path):
    if not path:
        return ""
    for line in path.read_text(errors="replace").splitlines():
        if "Readiness classification:" in line:
            return line.split(":", 1)[1].strip()
    return ""


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    a22c = latest("A22C_latpc_shadow_vm_foundation_report_*.md")
    cls = classification(a22c)
    decision = "SHADOW_FIRST_MECHANISM_PATH" if cls in {"SHADOW_VM_READY_FOR_LATC_LATP_STATS", "SHADOW_VM_READY_FOR_REGULARITY_DETECTOR"} else "FOUNDATION_REWORK_REQUIRED"
    status = "PASS" if a22c else "FAIL_NO_A22C"
    report = REPORT_DIR / f"A23A_latpc_timing_integration_decision_{stamp}.md"
    plan_csv = REPORT_DIR / f"A23A_latpc_timing_integration_plan_{stamp}.csv"
    rows = [
        ("A24", decision, "Regularity Detector over shadow VM", "A22C ready", "shadow stride/page divergence CSVs", "cannot claim IPC speedup", "shadow-first"),
        ("A25", decision, "LATC over shadow MSHR", "shadow MSHR counters", "reservation fail reduction", "not real MSHR compression", "shadow-first"),
        ("A26", decision, "LATP over shadow PTW", "shadow PTW queue", "shadow batching/prefetch potential", "not real PTW batching", "shadow-first"),
        ("A28", "TIMING_INTEGRATION_PREP_PATH", "Design real timing VM", "shadow results stable", "timing design", "high behavior risk", "needed for paper speedup"),
        ("A29", "TIMING_INTEGRATION_PREP_PATH", "Implement baseline timing VM", "A28 design", "disabled baseline identical", "deadlock/replay risk", "before LATPC timing"),
    ]
    write_csv(plan_csv, [{"future_round": r[0], "path": r[1], "task": r[2], "prerequisite": r[3], "expected_output": r[4], "risk": r[5], "notes": r[6]} for r in rows], ["future_round", "path", "task", "prerequisite", "expected_output", "risk", "notes"])
    report.write_text(f"""# A23A LATPC Timing Integration Decision

- Status: {status}
- A22C classification: {cls}
- Primary decision: {decision}

Timing integration is not implemented in A23A. Faithful LATPC paper speedup
reproduction will require a future timing-affecting VM model after shadow
mechanisms are validated.
""")
    stage_report(report, "A23A LATPC Timing Integration Decision", status, start_iso, start, ["python3 scripts/accelsim/a23a_latpc_timing_integration_decision.py"], [rel(a22c) if a22c else ""], [rel(report), rel(plan_csv)], "none" if a22c else "missing A22C", ["Decision only; no timing implementation.", "Shadow model can support mechanism potential analysis, not IPC speedup claims."], f"## Decision\n\n`{decision}`\n")
    print(f"A23A status: {status}")
    print(f"A23A decision: {decision}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
