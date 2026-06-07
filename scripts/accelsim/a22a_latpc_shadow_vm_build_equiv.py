#!/usr/bin/env python3
from __future__ import annotations

import math
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import LOG_DIR, REPORT_DIR, REPO_ROOT, clean, ensure_dirs, parse_stats, prepare_accelsim_run_dir, rel, repo_path, run_logged, selected_workload, source_env, stage_report, stat, ts, write_csv


def run_variant(stamp: str, variant: str, env_vars: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    selected = selected_workload()
    kernels = repo_path(selected.get("kernelslist_path", ""))
    config = repo_path(selected.get("config_path", "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"))
    trace_config = REPO_ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    run_dir = REPO_ROOT / ".local_runs" / f"A22A_latpc_shadow_vm_{stamp}" / variant
    prepare_accelsim_run_dir(run_dir, kernels, config, trace_config)
    log = LOG_DIR / f"A22A_{stamp}_{variant}.log"
    sim = REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out"
    env = source_env({"ACCELSIM_ROUND": "A22A", **env_vars})
    info = run_logged(["timeout", os.environ.get("ACCELSIM_A22_TIMEOUT_SEC", "900"), str(sim), "-config", "./gpgpusim.config", "-trace", "./traces/kernelslist.g"], log, cwd=run_dir, env=env)
    stats = parse_stats(log)
    return info, stats


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    report = REPORT_DIR / f"A22A_latpc_shadow_vm_build_equiv_{stamp}.md"
    compare_csv = REPORT_DIR / f"A22A_latpc_behavior_compare_{stamp}.csv"
    stats_csv = REPORT_DIR / f"A22A_latpc_extracted_stats_{stamp}.csv"
    build_log = LOG_DIR / f"A22A_{stamp}_build.log"
    build = run_logged(["make", "-C", "./gpu-simulator/"], build_log, cwd=REPO_ROOT, env=source_env({"ACCELSIM_ROUND": "A22A"}))
    status = "PASS"
    blocker = "none"
    compare_rows = []
    stat_rows = []
    commands = [build["command"]]
    if build["return_code"] != "0":
        status = "FAIL_BUILD"
        blocker = "build failed"
    else:
        base_info, base_stats = run_variant(stamp, "baseline_no_shadow", {"ACCELSIM_LATPC_SHADOW_VM": "0"})
        shadow_info, shadow_stats = run_variant(stamp, "shadow_vm_default", {"ACCELSIM_LATPC_SHADOW_VM": "1", "ACCELSIM_LATPC_SHADOW_PAGE_SHIFT": "12"})
        commands += [base_info["command"], shadow_info["command"]]
        if base_info["return_code"] != "0" or shadow_info["return_code"] != "0":
            status = "FAIL_RUN"
            blocker = f"baseline rc {base_info['return_code']}, shadow rc {shadow_info['return_code']}"
        fields = [
            ("cycles", "gpu_tot_sim_cycle", "int"),
            ("instructions", "gpu_tot_sim_insn", "int"),
            ("ipc", "gpu_tot_ipc", "float"),
            ("l2_accesses", "L2_total_cache_accesses", "int"),
            ("l2_misses", "L2_total_cache_misses", "int"),
        ]
        for name, key, kind in fields:
            b = stat(base_stats, key)
            s = stat(shadow_stats, key)
            try:
                bf, sf = float(b), float(s)
                absd = abs(sf - bf)
                reld = absd / max(abs(bf), 1.0)
                ok = absd == 0 if kind == "int" else (absd <= 1e-9 or reld <= 1e-6)
            except ValueError:
                absd, reld, ok = "NA", "NA", False
            if not ok and status == "PASS":
                status = "FAIL_BEHAVIOR_CHANGED"
                blocker = f"{name} changed"
            compare_rows.append({"field": name, "baseline_value": b, "shadow_value": s, "abs_diff": str(absd), "rel_diff": str(reld), "tolerance_abs": "0" if kind == "int" else "1e-9", "tolerance_rel": "0" if kind == "int" else "1e-6", "status": "PASS" if ok else "FAIL", "notes": key})
        latpc_keys = [k for k in shadow_stats if k.startswith("latpc_")]
        if status == "PASS" and (not latpc_keys or float(shadow_stats.get("latpc_vm_translation_request_total", "0")) <= 0):
            status = "FAIL_STATS_EMPTY"
            blocker = "shadow latpc stats missing or empty"
        for source, stats in [("baseline_no_shadow", base_stats), ("shadow_vm_default", shadow_stats)]:
            for k, v in sorted(stats.items()):
                if k.startswith("latpc_") or k in {"gpu_tot_sim_cycle", "gpu_tot_sim_insn", "gpu_tot_ipc", "L2_total_cache_accesses", "L2_total_cache_misses"}:
                    stat_rows.append({"variant": source, "stat_key": k, "stat_value": v})
    write_csv(compare_csv, compare_rows, ["field", "baseline_value", "shadow_value", "abs_diff", "rel_diff", "tolerance_abs", "tolerance_rel", "status", "notes"])
    write_csv(stats_csv, stat_rows, ["variant", "stat_key", "stat_value"])
    stage_report(report, "A22A LATPC Shadow VM Build And Equivalence", status, start_iso, start, commands, [".local_reports/A21C_latpc_runner_matrix_*.csv"], [rel(report), rel(compare_csv), rel(stats_csv), rel(build_log)], blocker, ["Only NW baseline and default shadow rows are run.", "No tracer/full campaign."])
    print(f"A22A status: {status}")
    print(f"A22A report: {rel(report)}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
