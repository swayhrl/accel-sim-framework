#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import LOG_DIR, REPORT_DIR, REPO_ROOT, ensure_dirs, parse_stats, prepare_accelsim_run_dir, rel, repo_path, run_logged, selected_workload, source_env, stage_report, stat, ts, write_csv


def run_shadow(stamp: str, variant: str, env_vars: dict[str, str]) -> dict[str, str]:
    selected = selected_workload()
    kernels = repo_path(selected.get("kernelslist_path", ""))
    config = repo_path(selected.get("config_path", "gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config"))
    trace_config = REPO_ROOT / "gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
    run_dir = REPO_ROOT / ".local_runs" / f"A22B_latpc_shadow_vm_{stamp}" / variant
    prepare_accelsim_run_dir(run_dir, kernels, config, trace_config)
    log = LOG_DIR / f"A22B_{stamp}_{variant}.log"
    sim = REPO_ROOT / "gpu-simulator/bin/release/accel-sim.out"
    info = run_logged(["timeout", os.environ.get("ACCELSIM_A22_TIMEOUT_SEC", "900"), str(sim), "-config", "./gpgpusim.config", "-trace", "./traces/kernelslist.g"], log, cwd=run_dir, env=source_env({"ACCELSIM_LATPC_SHADOW_VM": "1", **env_vars}))
    stats = parse_stats(log)
    stats["_return_code"] = info["return_code"]
    stats["_log_path"] = rel(log)
    return stats


def num(stats: dict[str, str], key: str) -> float:
    try:
        return float(stats.get(key, "0"))
    except ValueError:
        return 0.0


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    report = REPORT_DIR / f"A22B_latpc_shadow_vm_sanity_sensitivity_{stamp}.md"
    sanity_csv = REPORT_DIR / f"A22B_latpc_shadow_vm_sanity_{stamp}.csv"
    sens_csv = REPORT_DIR / f"A22B_latpc_shadow_vm_sensitivity_{stamp}.csv"
    variants = {
        "default": {"ACCELSIM_LATPC_SHADOW_PAGE_SHIFT": "12"},
        "small_tlb": {"ACCELSIM_LATPC_SHADOW_L1_ENTRIES": "8", "ACCELSIM_LATPC_SHADOW_L2_ENTRIES": "64", "ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES": "4", "ACCELSIM_LATPC_SHADOW_PTW_COUNT": "4"},
        "large_tlb": {"ACCELSIM_LATPC_SHADOW_L1_ENTRIES": "64", "ACCELSIM_LATPC_SHADOW_L2_ENTRIES": "2048", "ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES": "32", "ACCELSIM_LATPC_SHADOW_PTW_COUNT": "32"},
    }
    all_stats = {name: run_shadow(stamp, name, env) for name, env in variants.items()}
    status = "PASS"
    blocker = "none"
    if any(s.get("_return_code") != "0" for s in all_stats.values()):
        status = "FAIL_RUN"
        blocker = "one or more sensitivity runs failed"
    d = all_stats["default"]
    checks = []
    def check(name, ok, value, expected, stat_key, notes=""):
        nonlocal status, blocker
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "value": str(value), "expected": expected, "evidence_stat": stat_key, "notes": notes})
        if not ok and status == "PASS":
            status = "FAIL_STATS_EMPTY" if "presence" in name or "nontrivial" in name else "FAIL_INCONSISTENT_STATS"
            blocker = name
    check("presence_enabled", d.get("latpc_shadow_vm_enabled") == "1", d.get("latpc_shadow_vm_enabled"), "1", "latpc_shadow_vm_enabled")
    check("presence_translation_requests", "latpc_vm_translation_request_total" in d, d.get("latpc_vm_translation_request_total"), "exists", "latpc_vm_translation_request_total")
    check("nontrivial_translation_requests", num(d, "latpc_vm_translation_request_total") > 0, num(d, "latpc_vm_translation_request_total"), ">0", "latpc_vm_translation_request_total")
    check("nontrivial_l1_access", num(d, "latpc_tlb_l1_access_total") > 0, num(d, "latpc_tlb_l1_access_total"), ">0", "latpc_tlb_l1_access_total")
    div_sum = sum(num(d, k) for k in ["latpc_vm_page_div_bin_1","latpc_vm_page_div_bin_2_3","latpc_vm_page_div_bin_4_7","latpc_vm_page_div_bin_8_15","latpc_vm_page_div_bin_16_31","latpc_vm_page_div_bin_32"])
    check("nontrivial_page_divergence", div_sum > 0, div_sum, ">0", "latpc_vm_page_div_bin_*")
    check("l1_hit_miss_sum", num(d,"latpc_tlb_l1_hit_total")+num(d,"latpc_tlb_l1_miss_total") == num(d,"latpc_tlb_l1_access_total"), num(d,"latpc_tlb_l1_access_total"), "hit+miss==access", "latpc_tlb_l1_*")
    check("l2_hit_miss_sum", num(d,"latpc_tlb_l2_hit_total")+num(d,"latpc_tlb_l2_miss_total") == num(d,"latpc_tlb_l2_access_total"), num(d,"latpc_tlb_l2_access_total"), "hit+miss==access", "latpc_tlb_l2_*")
    check("same_l4pt_bound", num(d,"latpc_vm_same_l4pt_translation_total") <= num(d,"latpc_vm_l4pt_translation_total"), num(d,"latpc_vm_same_l4pt_translation_total"), "<= l4pt total", "latpc_vm_same_l4pt_translation_total")
    check("mshr_fail_bound", num(d,"latpc_tlb_l1_mshr_reservation_fail") <= num(d,"latpc_tlb_l1_mshr_alloc_attempt"), num(d,"latpc_tlb_l1_mshr_reservation_fail"), "<= attempts", "latpc_tlb_l1_mshr_*")
    check("ptw_complete_bound", num(d,"latpc_ptw_walk_complete_total") <= num(d,"latpc_ptw_walk_issue_total"), num(d,"latpc_ptw_walk_complete_total"), "<= issue", "latpc_ptw_walk_*")
    small, large = all_stats["small_tlb"], all_stats["large_tlb"]
    sens = []
    for metric in ["latpc_tlb_l1_miss_total", "latpc_tlb_l2_miss_total", "latpc_tlb_l1_mshr_reservation_fail", "latpc_ptw_queue_shadow_stall_cycle_total"]:
        sv, dv, lv = num(small, metric), num(d, metric), num(large, metric)
        ok = sv >= lv
        sens.append({"metric": metric, "default_value": str(dv), "small_tlb_value": str(sv), "large_tlb_value": str(lv), "trend_status": "PASS" if ok else "WARN_WEAK_TREND", "notes": "small should generally be >= large"})
        if not ok and status == "PASS":
            status = "PASS_WITH_WARNINGS"
            blocker = "weak sensitivity trend"
    write_csv(sanity_csv, checks, ["check", "status", "value", "expected", "evidence_stat", "notes"])
    write_csv(sens_csv, sens, ["metric", "default_value", "small_tlb_value", "large_tlb_value", "trend_status", "notes"])
    stage_report(report, "A22B LATPC Shadow VM Sanity And Sensitivity", status, start_iso, start, ["python3 scripts/accelsim/a22b_latpc_shadow_vm_sanity_sensitivity.py"], [".local_reports/A22A_latpc_shadow_vm_build_equiv_*.md"], [rel(report), rel(sanity_csv), rel(sens_csv)], blocker, ["Bounded NW only.", "Sensitivity trends may be approximate but stats must be non-empty."])
    print(f"A22B status: {status}")
    print(f"A22B report: {rel(report)}")
    return 0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
