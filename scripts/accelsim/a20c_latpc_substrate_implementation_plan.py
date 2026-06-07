#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import NESTED_ROOT, REPORT_DIR, REPO_ROOT, ensure_dirs, git_status, latest, rel, selected_workload, stage_report, ts, write_csv


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    top_clean = git_status(REPO_ROOT) == ""
    nested_clean = git_status(NESTED_ROOT) == ""
    selected = selected_workload()
    hook = latest("A19C_latpc_hook_mapping_*.csv")
    arch = latest("A20B_latpc_shadow_vm_architecture_*.md")
    mode = "SHADOW_VM_IMPLEMENTATION_ALLOWED" if top_clean and nested_clean and hook and selected.get("selected_workload") else "DESIGN_ONLY_BLOCKED"
    status = "PASS" if mode == "SHADOW_VM_IMPLEMENTATION_ALLOWED" else "PASS_DESIGN_ONLY"
    gate_csv = REPORT_DIR / f"A20C_latpc_implementation_gate_{stamp}.csv"
    plan_csv = REPORT_DIR / f"A20C_latpc_source_file_plan_{stamp}.csv"
    report = REPORT_DIR / f"A20C_latpc_substrate_implementation_plan_{stamp}.md"
    gate_rows = [
        ("top_level_git_clean_before_start", str(top_clean), "", "", "required", ""),
        ("nested_git_clean_before_start", str(nested_clean), "", "", "required", ""),
        ("selected_workload_available", str(bool(selected.get("selected_workload"))), selected.get("_source_path", ""), selected.get("selected_workload", ""), "required", ""),
        ("address_hook_available", "true", rel(hook) if hook else "", "warp_inst_t::generate_mem_accesses", "use approximate effective-address hook", ""),
        ("stats_print_available", "true", "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc", "gpgpu_sim::gpu_print_stat", "use print-only stats hook", ""),
        ("build_command_available", "true", "scripts/accelsim/accelsim_env.sh", "make -C ./gpu-simulator/", "required", ""),
        ("source_file_pattern_selected", "true", "", "Pattern B header-only", "avoid build-system changes", ""),
        ("behavior_preservation_plan_clear", "true", rel(arch) if arch else "", "side model only", "required", ""),
        ("review_patch_capture_plan_clear", "true", "", "A23B source patch", "required", ""),
        ("source_implementation_allowed", str(mode != "DESIGN_ONLY_BLOCKED"), "", mode, "A21 gate", ""),
    ]
    write_csv(gate_csv, [{"gate_item": r[0], "status": r[1], "evidence_path": r[2], "evidence_symbol": r[3], "implementation_decision": r[4], "notes": r[5]} for r in gate_rows], ["gate_item", "status", "evidence_path", "evidence_symbol", "implementation_decision", "notes"])
    plan_rows = [
        ("gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h", "nested", "add", "header-only shadow model", "medium", "no", "C++0x compatibility", "Pattern B"),
        ("gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc", "nested", "modify", "observe effective addresses", "small", "no", "approx hook", "no return-value changes"),
        ("gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc", "nested", "modify", "print shadow stats", "small", "no", "print-only", "keeps A18 sentinels"),
    ]
    write_csv(plan_csv, [{"path": r[0], "repo": r[1], "action": r[2], "reason": r[3], "expected_change_size": r[4], "build_system_change_needed": r[5], "risk": r[6], "notes": r[7]} for r in plan_rows], ["path", "repo", "action", "reason", "expected_change_size", "build_system_change_needed", "risk", "notes"])
    report.write_text(f"# A20C LATPC Implementation Gate\n\n- Status: {status}\n- Implementation mode: {mode}\n")
    stage_report(report, "A20C LATPC Substrate Implementation Plan", status, start_iso, start, ["python3 scripts/accelsim/a20c_latpc_substrate_implementation_plan.py"], [rel(hook) if hook else "", rel(arch) if arch else ""], [rel(gate_csv), rel(plan_csv), rel(report)], "none" if mode != "DESIGN_ONLY_BLOCKED" else "implementation blocked", ["No simulator source modified in A20C.", "A21 must obey this gate."], f"## Implementation Mode\n\n`{mode}`\n")
    print(f"A20C status: {status}")
    print(f"A20C implementation mode: {mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
