#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import REPORT_DIR, ensure_dirs, latest, rel, stage_report, ts, write_csv


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    req = latest("A20A_latpc_vm_substrate_requirements_*.csv")
    csv_path = REPORT_DIR / f"A20B_latpc_shadow_vm_architecture_matrix_{stamp}.csv"
    report = REPORT_DIR / f"A20B_latpc_shadow_vm_architecture_{stamp}.md"
    rows = [
        ("enable", "ACCELSIM_LATPC_SHADOW_VM env; disabled by default", "0", "latpc_shadow_vm.h", "DESIGN_ONLY if env unavailable", "no"),
        ("page_shift", "VPN = address >> page_shift", "12", "latpc_shadow_vm.h", "constant 12", "no"),
        ("address_observation", "effective per-lane addresses from warp_inst_t", "approximate", "abstract_hardware_model.cc", "mem_fetch address-level", "no"),
        ("l1_tlb", "fully associative LRU shadow cache", "32 entries", "latpc_shadow_vm.h", "global approximate L1", "no"),
        ("l2_tlb", "global fully associative LRU shadow cache", "1024 entries", "latpc_shadow_vm.h", "smaller capped vector", "no"),
        ("l1_mshr", "outstanding VPN vector with merge/fail counters", "16 entries", "latpc_shadow_vm.h", "unbounded stats-only", "no"),
        ("l2_mshr", "config/stat placeholders first", "128 entries", "latpc_shadow_vm.h", "defer", "no"),
        ("ptw_queue", "shadow completion queue and walker availability", "128 entries", "latpc_shadow_vm.h", "event-index ordering", "no"),
        ("ptw_latency", "fixed shadow completion latency", "300 events", "latpc_shadow_vm.h", "0-latency stats", "no"),
        ("pwc", "deferred counters printed as zero", "disabled", "latpc_shadow_vm.h", "defer", "no"),
        ("stats_print", "raw latpc_shadow/vm/tlb/ptw/pwc stats", "enabled rows only", "gpu-sim.cc", "runner parser", "no"),
        ("runner", "NW baseline/default/small/large env matrix", "bounded", "scripts/accelsim/a21c_latpc_shadow_vm_runner.py", "dry run", "no"),
    ]
    dict_rows = [{"component": r[0], "design_choice": r[1], "default_value": r[2], "implementation_location_preference": r[3], "fallback": r[4], "affects_real_timing": r[5]} for r in rows]
    write_csv(csv_path, dict_rows, ["component", "design_choice", "default_value", "implementation_location_preference", "fallback", "affects_real_timing"])
    report.write_text("""# A20B LATPC Shadow VM Architecture

The shadow VM substrate is a side model. It observes effective addresses and
updates private state only when `ACCELSIM_LATPC_SHADOW_VM=1`.

Allowed side effects: counter increments, shadow state updates, extra wall-clock
runtime, and extra stats print lines.

Forbidden side effects: real simulator data structure changes, memory request
changes, scheduler changes, queue changes, latency changes, replay, real TLB or
cache hit/miss changes, and prefetch injection.
""")
    stage_report(report, "A20B LATPC Shadow VM Architecture", "PASS", start_iso, start, ["python3 scripts/accelsim/a20b_latpc_shadow_vm_architecture.py"], [rel(req) if req else ""], [rel(csv_path), rel(report)], "none", ["Architecture only.", "PWC is deferred in first implementation."])
    print(f"A20B status: PASS")
    print(f"A20B report: {rel(report)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
