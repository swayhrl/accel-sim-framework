#!/usr/bin/env python3
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, REPO_ROOT, clean, ensure_local_dirs, latest, read_json, rel, ts, write_csv, write_stage_report

SOURCE = REPO_ROOT / "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc"
MARKER_BEGIN = "  // A18 LATPC stats-only metadata: print-only, no simulator behavior changes.\n"
INSERT = (
    MARKER_BEGIN
    +
    '  printf("latpc_stats_only_marker = 1\\n");\n'
    '  printf("latpc_stats_only_version = 18\\n");\n'
    '  printf("latpc_functional_mechanism_enabled = 0\\n");\n'
)


def patch_source() -> tuple[bool, str]:
    text = SOURCE.read_text()
    if "latpc_stats_only_marker" in text:
        return False, "already_instrumented"
    needle = '  printf("kernel_stream_id = %llu\\n", streamID);\n\n'
    if needle not in text:
        return False, "needle_not_found"
    SOURCE.write_text(text.replace(needle, needle + INSERT + "\n", 1))
    return True, "patched"


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    gate_path = latest("A17D_latpc_readiness_gate_*.json")
    summary_csv = REPORT_DIR / f"A18B_latpc_stats_only_instrumentation_{stamp}.csv"
    report = REPORT_DIR / f"A18B_latpc_stats_only_instrumentation_report_{stamp}.md"
    status = "BLOCKED_NO_A17D"
    blocker = "missing A17D readiness gate"
    mode = "UNKNOWN"
    changed = False
    action = "none"
    if gate_path:
        gate = read_json(gate_path)
        mode = clean(gate.get("readiness_mode"))
        if not gate.get("a18b_simulator_source_modification_allowed"):
            status = "DESIGN_ONLY_BLOCKED"
            blocker = "A17D did not allow simulator source modification"
            action = "no_source_change"
        else:
            changed, action = patch_source()
            if action == "needle_not_found":
                status = "BLOCKED_PATCH_TARGET_NOT_FOUND"
                blocker = f"could not find insertion point in {rel(SOURCE)}"
            else:
                status = "PASS"
                blocker = "none"
    rows = [{
        "source_file": rel(SOURCE),
        "readiness_mode": mode,
        "action": action,
        "changed_this_run": str(changed).lower(),
        "behavior_scope": "print-only latpc_* metadata stats",
        "forbidden_scope_touched": "no",
    }]
    write_csv(summary_csv, rows, ["source_file", "readiness_mode", "action", "changed_this_run", "behavior_scope", "forbidden_scope_touched"])
    write_stage_report(
        report,
        "A18B LATPC Stats-Only Instrumentation",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a18b_latpc_stats_only_instrumentation.py"],
        [rel(gate_path) if gate_path else ""],
        [rel(summary_csv), rel(report), rel(SOURCE) if status == "PASS" else ""],
        blocker,
        ["Instrumentation only prints metadata/sentinel stats.", "No LATPC detector, LATC, LATP, TLB, MSHR, PTW, replay, scheduling, or prefetch behavior is implemented."],
    )
    print(f"A18B status: {status}")
    print(f"A18B source action: {action}")
    print(f"A18B report: {rel(report)}")
    return 0 if status in {"PASS", "DESIGN_ONLY_BLOCKED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
