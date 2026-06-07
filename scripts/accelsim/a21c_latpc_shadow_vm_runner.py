#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import REPORT_DIR, REPO_ROOT, clean, ensure_dirs, rel, repo_path, selected_workload, stage_report, ts, write_csv


def rows_for(stamp: str) -> list[dict[str, str]]:
    selected = selected_workload()
    workload = clean(selected.get("selected_workload")) or "nw"
    kernels = repo_path(selected.get("kernelslist_path", ""))
    run_base = REPO_ROOT / ".local_runs" / f"A21C_latpc_shadow_vm_{stamp}"
    sim = REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out"
    variants = [
        ("baseline_no_shadow", "ACCELSIM_LATPC_SHADOW_VM=0", "baseline behavior"),
        ("shadow_vm_default", "ACCELSIM_LATPC_SHADOW_VM=1;ACCELSIM_LATPC_SHADOW_PAGE_SHIFT=12", "default shadow VM"),
        ("shadow_vm_small_tlb", "ACCELSIM_LATPC_SHADOW_VM=1;ACCELSIM_LATPC_SHADOW_L1_ENTRIES=8;ACCELSIM_LATPC_SHADOW_L2_ENTRIES=64;ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES=4;ACCELSIM_LATPC_SHADOW_PTW_COUNT=4", "small TLB sensitivity"),
        ("shadow_vm_large_tlb", "ACCELSIM_LATPC_SHADOW_VM=1;ACCELSIM_LATPC_SHADOW_L1_ENTRIES=64;ACCELSIM_LATPC_SHADOW_L2_ENTRIES=2048;ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES=32;ACCELSIM_LATPC_SHADOW_PTW_COUNT=32", "large TLB sensitivity"),
    ]
    out = []
    for i, (variant, env, notes) in enumerate(variants, 1):
        cwd = run_base / variant
        log = REPO_ROOT / ".local_logs" / f"A21C_{stamp}_{variant}.log"
        cmd = f"{sim} -config ./gpgpusim.config -trace ./traces/kernelslist.g"
        out.append({"run_id": f"A21C_{i:02d}_{variant}", "workload": workload, "variant": variant, "env": env, "command": cmd, "cwd": rel(cwd), "log_path": rel(log), "expected_behavior_change": "none", "notes": notes + f"; kernels={rel(kernels)}"})
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    matrix = REPORT_DIR / f"A21C_latpc_runner_matrix_{stamp}.csv"
    report = REPORT_DIR / f"A21C_latpc_runner_integration_{stamp}.md"
    rows = rows_for(stamp)
    write_csv(matrix, rows, ["run_id", "workload", "variant", "env", "command", "cwd", "log_path", "expected_behavior_change", "notes"])
    status = "PASS"
    stage_report(report, "A21C LATPC Shadow VM Runner Integration", status, start_iso, start, ["python3 scripts/accelsim/a21c_latpc_shadow_vm_runner.py" + (" --dry-run" if args.dry_run else "")], [".local_reports/A16A_latpc_selected_workload_*.json", ".local_reports/A21B_latpc_shadow_vm_hooks_stats_*.md"], [rel(matrix), rel(report)], "none", ["Runner integration only; does not execute simulation.", "A22 scripts execute bounded rows."])
    print(f"A21C status: {status}")
    print(f"A21C matrix: {rel(matrix)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
