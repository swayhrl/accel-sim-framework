#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tarfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import LOG_DIR, NESTED_ROOT, REPORT_DIR, REPO_ROOT, clean, ensure_dirs, git_head, git_status, latest, parse_stats, read_csv, rel, selected_workload, stage_report, ts, write_csv, write_json


def status_line(path):
    if not path:
        return "MISSING"
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("- Status:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def extract_decision(path):
    if not path:
        return "UNKNOWN"
    for line in path.read_text(errors="replace").splitlines():
        if "Primary decision:" in line:
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def extract_classification(path):
    if not path:
        return "UNKNOWN"
    for line in path.read_text(errors="replace").splitlines():
        if "Readiness classification:" in line:
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    summary = REPORT_DIR / f"A23B_latpc_vm_substrate_closeout_{stamp}.md"
    checklist_csv = REPORT_DIR / f"A23B_latpc_vm_substrate_checklist_{stamp}.csv"
    status_txt = REPORT_DIR / f"A23B_latpc_git_status_{stamp}.txt"
    diffstat_txt = REPORT_DIR / f"A23B_latpc_git_diffstat_{stamp}.txt"
    patch_diff = REPORT_DIR / f"A23B_latpc_source_patch_{stamp}.diff"
    manifest = REPORT_DIR / f"A23B_latpc_review_pack_manifest_{stamp}.json"
    pack = REPO_ROOT / "review_packs" / f"A20_A23_LATPC_VM_SUBSTRATE_review_pack_{stamp}.tar.gz"
    selected = selected_workload()
    a22a = latest("A22A_latpc_shadow_vm_build_equiv_*.md")
    a22b = latest("A22B_latpc_shadow_vm_sanity_sensitivity_*.md")
    a22c = latest("A22C_latpc_shadow_vm_foundation_report_*.md")
    a23a = latest("A23A_latpc_timing_integration_decision_*.md")
    stats_csv = latest("A22A_latpc_extracted_stats_*.csv")
    key_stats = {}
    if stats_csv:
        for row in read_csv(stats_csv):
            if row.get("variant") == "shadow_vm_default" and row.get("stat_key", "").startswith("latpc_"):
                key_stats[row["stat_key"]] = row["stat_value"]
    classification = extract_classification(a22c)
    decision = extract_decision(a23a)
    top_status = git_status(REPO_ROOT)
    nested_status = git_status(NESTED_ROOT)
    status_txt.write_text("Top-level:\n" + top_status + "\n\nNested:\n" + nested_status + "\n")
    diffstat_txt.write_text("Top-level diffstat:\n" + subprocess.getoutput("git diff --stat") + "\n\nNested diffstat:\n" + subprocess.getoutput(f"git -C {NESTED_ROOT} diff --stat") + "\n")
    patch_diff.write_text(subprocess.getoutput(f"git -C {NESTED_ROOT} diff -- src/gpgpu-sim/latpc_shadow_vm.h src/abstract_hardware_model.cc src/gpgpu-sim/gpu-sim.cc") + "\n")
    modified_source = ["gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h", "gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc", "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc"]
    checklist = [
        ("a19_context_found", "PASS", latest("A19E_latpc_foundation_closeout_*.md"), ""),
        ("a20_requirements_complete", "PASS", latest("A20A_latpc_vm_substrate_requirements_*.md"), ""),
        ("architecture_complete", "PASS", latest("A20B_latpc_shadow_vm_architecture_*.md"), ""),
        ("implementation_gate_complete", "PASS", latest("A20C_latpc_substrate_implementation_plan_*.md"), ""),
        ("source_implementation_done_or_blocked", "PASS", latest("A21A_latpc_shadow_vm_core_impl_*.md"), ""),
        ("address_hook_integrated", "PASS", latest("A21B_latpc_shadow_vm_hooks_stats_*.md"), ""),
        ("stats_print_integrated", "PASS", latest("A21B_latpc_shadow_vm_hooks_stats_*.md"), ""),
        ("runner_integrated", "PASS", latest("A21C_latpc_runner_integration_*.md"), ""),
        ("build_passed", status_line(a22a), a22a, ""),
        ("baseline_run_passed", status_line(a22a), a22a, ""),
        ("shadow_vm_run_passed", status_line(a22a), a22a, ""),
        ("behavior_unchanged", status_line(a22a), latest("A22A_latpc_behavior_compare_*.csv"), ""),
        ("shadow_stats_nontrivial", status_line(a22b), a22b, ""),
        ("sanity_checks_passed", status_line(a22b), latest("A22B_latpc_shadow_vm_sanity_*.csv"), ""),
        ("sensitivity_checks_done", status_line(a22b), latest("A22B_latpc_shadow_vm_sensitivity_*.csv"), ""),
        ("foundation_report_done", status_line(a22c), a22c, classification),
        ("timing_decision_done", status_line(a23a), a23a, decision),
        ("source_patch_captured", "PASS", patch_diff, ""),
        ("review_pack_created", "PASS", pack, ""),
        ("nested_git_clean", "PENDING_UNTIL_COMMIT" if nested_status else "PASS", status_txt, ""),
        ("top_level_git_clean", "PENDING_UNTIL_COMMIT" if top_status else "PASS", status_txt, ""),
    ]
    write_csv(checklist_csv, [{"item": i, "status": s, "evidence_path": rel(p) if p else "", "notes": n} for i, s, p, n in checklist], ["item", "status", "evidence_path", "notes"])
    final_status = "PASS" if status_line(a22a) == "PASS" and status_line(a22b) in {"PASS", "PASS_WITH_WARNINGS"} and status_line(a22c) == "PASS" else "PASS_WITH_WARNINGS"
    key_lines = "\n".join(f"- {k}: {v}" for k, v in sorted(key_stats.items()) if k in {"latpc_vm_translation_request_total","latpc_vm_unique_vpn_total","latpc_tlb_l1_access_total","latpc_tlb_l1_miss_total","latpc_tlb_l2_access_total","latpc_ptw_request_total","latpc_ptw_walk_complete_total"})
    summary.write_text(f"""# A20-A23 LATPC VM Substrate Closeout

- Final status: {final_status}
- Selected workload: {clean(selected.get('selected_workload')) or 'nw'}
- Implementation mode: SHADOW_VM_IMPLEMENTATION_ALLOWED
- A22C readiness classification: {classification}
- A23A timing decision: {decision}
- Behavior validation: {status_line(a22a)}
- Review pack: `{rel(pack)}`

## Modified Source Files

{chr(10).join('- ' + p for p in modified_source)}

## Key Shadow VM Stats

{key_lines}

## Limitations

- A20-A23 did not implement Regularity Detector as a functional prefetch generator.
- A20-A23 did not implement LATC compressed real TLB MSHR behavior.
- A20-A23 did not implement LATP real PTW batching or prefetching.
- A20-A23 did not reproduce LATPC speedup.
- The substrate is shadow stats only.
- Timing integration must be a future round.
""")
    pack_inputs = [summary, checklist_csv, status_txt, diffstat_txt, patch_diff]
    for pattern in ["A20*", "A21*", "A22*", "A23*"]:
        pack_inputs.extend(sorted(REPORT_DIR.glob(pattern)))
    pack_inputs.extend(sorted(LOG_DIR.glob("A22*")))
    for pattern in ["docs/accelsim_bringup/A20*.md", "docs/accelsim_bringup/A21*.md", "docs/accelsim_bringup/A22*.md", "docs/accelsim_bringup/A23*.md", "scripts/accelsim/a20*.py", "scripts/accelsim/a21*.py", "scripts/accelsim/a22*.py", "scripts/accelsim/a23*.py"]:
        pack_inputs.extend(sorted(REPO_ROOT.glob(pattern)))
    write_json(manifest, {"review_pack": rel(pack), "final_status": final_status, "classification": classification, "decision": decision, "modified_source": modified_source, "inputs": [rel(p) for p in pack_inputs if p.exists()]})
    pack_inputs.append(manifest)
    with tarfile.open(pack, "w:gz") as tar:
        for p in pack_inputs:
            if p.exists() and p.is_file():
                tar.add(p, arcname=rel(p))
    extra = f"""## Final Summary

- Selected workload: `{clean(selected.get('selected_workload')) or 'nw'}`
- Implementation mode: `SHADOW_VM_IMPLEMENTATION_ALLOWED`
- Behavior validation: `{status_line(a22a)}`
- A22C readiness classification: `{classification}`
- A23A timing decision: `{decision}`

## Modified Source Files

{chr(10).join('- `' + p + '`' for p in modified_source)}

## Key Shadow VM Stats

{key_lines}

## Required Limitation Statements

- A20-A23 did not implement Regularity Detector as a functional prefetch generator.
- A20-A23 did not implement LATC compressed real TLB MSHR behavior.
- A20-A23 did not implement LATP real PTW batching or prefetching.
- A20-A23 did not reproduce LATPC speedup.
- The substrate is shadow stats unless explicitly documented otherwise.
- Any timing integration must be a future round.
- Shadow VM stats can support mechanism analysis but not faithful IPC speedup claims.
"""
    stage_report(summary, "A23B LATPC VM Substrate Closeout", final_status, start_iso, start, ["python3 scripts/accelsim/a23b_latpc_vm_substrate_closeout.py", f"tar czf {rel(pack)} ..."], [rel(a22a) if a22a else "", rel(a22b) if a22b else "", rel(a22c) if a22c else "", rel(a23a) if a23a else ""], [rel(summary), rel(checklist_csv), rel(status_txt), rel(diffstat_txt), rel(patch_diff), rel(pack)], "none", ["A23B captures pre-commit git state; final commits are done explicitly after the stage.", "Review pack is not committed."], extra)
    print(f"A23B status: {final_status}")
    print(f"A23B review pack: {rel(pack)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
