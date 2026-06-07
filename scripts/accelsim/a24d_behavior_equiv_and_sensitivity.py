#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a24_latpc_lib import REPORT_DIR, behavior_fields, compare_behavior, ensure_dirs, num, rel, run_logged, run_nw_variant, stage_report, ts, write_csv


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    equiv_csv = REPORT_DIR / f"A24D_behavior_equivalence_{stamp}.csv"
    equiv_report = REPORT_DIR / f"A24D_behavior_equivalence_report_{stamp}.md"
    sens_csv = REPORT_DIR / f"A24D_sensitivity_sanity_{stamp}.csv"
    sens_report = REPORT_DIR / f"A24D_sensitivity_sanity_report_{stamp}.md"
    derived_report = REPORT_DIR / f"A24D_derived_stats_validation_{stamp}.md"
    derived_csv = REPORT_DIR / f"A24D_detector_ready_derived_stats_{stamp}.csv"
    sample_csv = REPORT_DIR / f"A24D_latpc_shadow_vm_samples_{stamp}.csv"
    modes = [
        ("baseline", {"ACCELSIM_LATPC_SHADOW_VM": "0"}),
        ("shadow_hardened", {"ACCELSIM_LATPC_SHADOW_VM": "1"}),
        ("shadow_hardened_sample", {"ACCELSIM_LATPC_SHADOW_VM": "1", "ACCELSIM_LATPC_SAMPLE_DUMP": "1", "ACCELSIM_LATPC_SAMPLE_LIMIT": "64", "ACCELSIM_LATPC_SAMPLE_PATH": str(sample_csv)}),
    ]
    infos = {}
    stats = {}
    for mode, env in modes:
        infos[mode], stats[mode] = run_nw_variant(stamp, "A24D", mode, env)
    base = stats["baseline"]
    rows = []
    status = "PASS"
    blocker = "none"
    for mode, _ in modes:
        cmp = compare_behavior(base, stats[mode])
        row = {"workload": "nw", "mode": mode, "command": infos[mode]["command"], "status": "PASS" if infos[mode]["return_code"] == "0" else "FAIL_RUN", "log_path": infos[mode]["log_path"], "stats_path": infos[mode]["log_path"], **behavior_fields(stats[mode]), "cycles_match_baseline": str(cmp["cycles"]).lower(), "instructions_match_baseline": str(cmp["instructions"]).lower(), "IPC_match_baseline": str(cmp["IPC"]).lower(), "L2_accesses_match_baseline": str(cmp["L2_accesses"]).lower(), "L2_misses_match_baseline": str(cmp["L2_misses"]).lower(), "equivalence_status": "PASS" if all(cmp.values()) else "FAIL", "limitation": "shadow model only"}
        rows.append(row)
        if row["status"] != "PASS" or row["equivalence_status"] != "PASS":
            status = "FAIL_BEHAVIOR_CHANGED"
            blocker = f"{mode}: {row['equivalence_status']} rc={infos[mode]['return_code']}"
    write_csv(equiv_csv, rows, ["workload", "mode", "command", "status", "log_path", "stats_path", "cycles", "instructions", "IPC", "L2_accesses", "L2_misses", "cycles_match_baseline", "instructions_match_baseline", "IPC_match_baseline", "L2_accesses_match_baseline", "L2_misses_match_baseline", "equivalence_status", "limitation"])
    stage_report(equiv_report, "A24D Behavior Equivalence", status, start_iso, start, [i["command"] for i in infos.values()], [rel(equiv_csv), rel(equiv_report)], f"baseline={behavior_fields(base)}; sample_changed_behavior={rows[2]['equivalence_status'] != 'PASS'}", blocker, ["NW only.", "No speedup claim."])
    sens_modes = {
        "default": {"ACCELSIM_LATPC_SHADOW_VM": "1"},
        "small": {"ACCELSIM_LATPC_SHADOW_VM": "1", "ACCELSIM_LATPC_SHADOW_L1_ENTRIES": "8", "ACCELSIM_LATPC_SHADOW_L2_ENTRIES": "64", "ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES": "4", "ACCELSIM_LATPC_SHADOW_PTW_COUNT": "4"},
        "large": {"ACCELSIM_LATPC_SHADOW_VM": "1", "ACCELSIM_LATPC_SHADOW_L1_ENTRIES": "64", "ACCELSIM_LATPC_SHADOW_L2_ENTRIES": "2048", "ACCELSIM_LATPC_SHADOW_L1_MSHR_ENTRIES": "32", "ACCELSIM_LATPC_SHADOW_PTW_COUNT": "32"},
    }
    sens_stats = {}
    sens_infos = {}
    for mode, env in sens_modes.items():
        sens_infos[mode], sens_stats[mode] = run_nw_variant(stamp, "A24D_sens", mode, env)
    sens_rows = []
    sens_status = "PASS"
    for metric in ["latpc_tlb_l1_miss_total", "latpc_tlb_l1_mshr_reservation_fail", "latpc_ptw_queue_shadow_stall_cycle_total"]:
        small = num(sens_stats["small"], metric)
        large = num(sens_stats["large"], metric)
        default = num(sens_stats["default"], metric)
        ok = small >= large
        sens_rows.append({"metric": metric, "default_value": str(default), "small_value": str(small), "large_value": str(large), "trend_status": "PASS" if ok else "WARN_WEAK_TREND", "notes": "small should generally be >= large"})
        if not ok:
            sens_status = "PASS_WITH_WARNINGS"
    write_csv(sens_csv, sens_rows, ["metric", "default_value", "small_value", "large_value", "trend_status", "notes"])
    stage_report(sens_report, "A24D Sensitivity Sanity", sens_status, start_iso, start, [i["command"] for i in sens_infos.values()], [rel(sens_csv), rel(sens_report)], f"sensitivity_status={sens_status}", "none", ["Bounded NW sensitivity only.", "Weak trend is warning, not speedup."])
    derive_cmd = ["python3", "scripts/accelsim/a24_latpc_derive_detector_ready_stats.py", "--log", infos["shadow_hardened_sample"]["log_path"], "--run-id", "A24D", "--workload", "nw", "--variant", "shadow_hardened_sample", "--out", str(derived_csv)]
    derive = run_logged(derive_cmd, Path(".local_logs") / f"A24D_{stamp}_derive.log")
    dstatus = "PASS" if derive["return_code"] == "0" and derived_csv.exists() and all(k in derived_csv.read_text() for k in ["multi_translation_fraction", "avg_unique_stride_count", "same_l4_fraction", "l1_miss_rate", "hook_sm_id_mode"]) else "FAIL_DERIVED_VALIDATION"
    stage_report(derived_report, "A24D Derived Stats Validation", dstatus, start_iso, start, [derive["command"]], [rel(derived_csv), rel(derived_report)], "derived stats CSV generated and checked for required columns", "none" if dstatus == "PASS" else "derived stats missing required columns", ["Derived metrics only; no mechanism."])
    final = status if status != "PASS" else ("PASS" if sens_status in {"PASS", "PASS_WITH_WARNINGS"} and dstatus == "PASS" else "PASS_WITH_WARNINGS")
    print(f"A24D status: {final}")
    print(f"A24D behavior CSV: {rel(equiv_csv)}")
    return 0 if final in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
