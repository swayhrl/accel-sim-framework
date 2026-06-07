#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a24_latpc_lib import NESTED_ROOT, REPORT_DIR, REPO_ROOT, clean, ensure_dirs, git_head, git_status, latest, read_csv, rel, selected_workload, stage_report, ts, write_csv


def latest_text(pattern: str) -> Path | None:
    return latest(pattern)


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    selected = selected_workload()
    summary = REPORT_DIR / f"A24E_latpc_shadow_vm_hardening_final_summary_{stamp}.md"
    contents = REPORT_DIR / f"A24E_review_pack_contents_{stamp}.txt"
    verification = REPORT_DIR / f"A24E_review_pack_verification_{stamp}.md"
    checklist = REPORT_DIR / f"A24E_closeout_checklist_{stamp}.csv"
    nested_patch = REPORT_DIR / f"A24E_nested_head_patch_{stamp}.patch"
    top_patch = REPORT_DIR / f"A24E_top_level_head_patch_{stamp}.patch"
    nested_log = REPORT_DIR / f"A24E_nested_log_{stamp}.txt"
    source_copy = REPORT_DIR / f"A24E_latpc_shadow_vm_full_source_{stamp}.h"
    pack = REPO_ROOT / "review_packs" / f"A24_LATPC_SHADOW_VM_HARDENING_AND_DETECTOR_READINESS_review_pack_{stamp}.tar.gz"
    shadow_source = REPO_ROOT / "gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h"
    shutil.copyfile(shadow_source, source_copy)
    nested_patch.write_text(subprocess.getoutput(f"git -C {NESTED_ROOT} show --stat --patch --find-renames HEAD") + "\n")
    top_patch.write_text(subprocess.getoutput(f"git -C {REPO_ROOT} show --stat --patch --find-renames HEAD") + "\n")
    nested_log.write_text(subprocess.getoutput(f"git -C {NESTED_ROOT} log --oneline -n 10") + "\n")
    behavior_csv = latest("A24D_behavior_equivalence_*.csv")
    derived_csv = latest("A24B_latpc_detector_ready_derived_stats_*.csv") or latest("A24D_detector_ready_derived_stats_*.csv")
    trace_csv = latest("A24C_latpc_trace_availability_*.csv")
    sample = latest("A24B_sample_dump_manifest_*.md")
    audit = latest("A24A_hook_exactness_audit_*.md")
    status = "PASS"
    behavior_summary = "missing"
    if behavior_csv:
        rows = read_csv(behavior_csv)
        behavior_summary = "; ".join(f"{r['mode']} cycles={r['cycles']} instructions={r['instructions']} IPC={r['IPC']} L2={r['L2_accesses']}/{r['L2_misses']} eq={r['equivalence_status']}" for r in rows)
        if any(r.get("equivalence_status") != "PASS" for r in rows):
            status = "FAIL_BEHAVIOR_CHANGED"
    scripts_changed = [str(p) for p in sorted((REPO_ROOT / "scripts/accelsim").glob("a24*.py"))]
    source_changed = [
        "gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h",
        "gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc",
        "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc",
    ]
    summary.write_text(f"""# A24 LATPC Shadow VM Hardening Final Summary

## Final Status

{status}

## Top-Level Commit

{git_head(REPO_ROOT)}

## Nested Simulator Commit

{git_head(NESTED_ROOT)}

## Source Files Changed

{chr(10).join('- ' + p for p in source_changed)}

## Scripts Changed

{chr(10).join('- ' + rel(p) for p in scripts_changed)}

## Review Pack Path

`{rel(pack)}`

## Hook Exactness Summary

- address: WARP_EFFECTIVE_ADDRESS_APPROX (`latpc_hook_address_mode=1`)
- sm_id: approximate zero (`latpc_hook_sm_id_mode=0`)
- cycle: event-index approximation (`latpc_hook_cycle_mode=0`)
- exact fields: PC, warp id, lane-order effective address list
- approximate fields: sm_id, cycle, virtual translation semantics
- deferred fields: full VM translation path, exact SM id, exact simulator cycle

## Detector-Ready Stats Summary

Derived stats CSV: `{rel(derived_csv) if derived_csv else 'missing'}`

## Sample Dump Summary

Sample manifest: `{rel(sample) if sample else 'missing'}`

## Trace Availability Summary

Trace availability CSV: `{rel(trace_csv) if trace_csv else 'missing'}`

## Behavior Equivalence Summary

{behavior_summary}

## Sensitivity Sanity Summary

`{rel(latest('A24D_sensitivity_sanity_*.csv')) if latest('A24D_sensitivity_sanity_*.csv') else 'missing'}`

## A25 Readiness

Proceed to A25 Regularity Detector over shadow VM only after reviewing this pack.

## Things Not Implemented

- A24 does not implement LATPC Regularity Detector.
- A24 does not implement LATC.
- A24 does not implement LATP.
- A24 does not integrate timing behavior.
- A24 does not reproduce IPC speedup.
- A24 output is detector-ready shadow analysis substrate, not faithful LATPC reproduction.
""")
    pack_inputs = [summary, source_copy, nested_patch, top_patch, nested_log]
    for pattern in ["A24A_*", "A24B_*", "A24C_*", "A24D_*", "A24E_*"]:
        pack_inputs.extend(sorted(REPORT_DIR.glob(pattern)))
    for path in [
        "gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h",
        "gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc",
        "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc",
        "docs/accelsim_bringup/A24A_LATPC_SOURCE_PATCH_AND_HOOK_EXACTNESS.md",
        "docs/accelsim_bringup/A24B_LATPC_DETECTOR_READY_STATS_AND_SAMPLE_DUMP.md",
        "docs/accelsim_bringup/A24C_LATPC_TRACE_AVAILABILITY_AND_SMALL_PROBE.md",
        "docs/accelsim_bringup/A24D_LATPC_BEHAVIOR_EQUIV_AND_SENSITIVITY.md",
        "docs/accelsim_bringup/A24E_LATPC_CLOSEOUT_REVIEW_PACK_AND_HANDOFF.md",
    ]:
        pack_inputs.append(REPO_ROOT / path)
    pack_inputs.extend(sorted((REPO_ROOT / "scripts/accelsim").glob("a24*.py")))
    manifest = REPORT_DIR / "A24_review_pack_manifest.txt"
    manifest.write_text(f"""A24 review pack manifest
created={time.strftime('%Y-%m-%dT%H:%M:%S%z')}
includes_full_latpc_shadow_vm_h=yes
nested_patch={rel(nested_patch)}
top_level_patch={rel(top_patch)}
behavior_csv={rel(behavior_csv) if behavior_csv else 'missing'}
derived_csv={rel(derived_csv) if derived_csv else 'missing'}
trace_csv={rel(trace_csv) if trace_csv else 'missing'}
sample_manifest={rel(sample) if sample else 'missing'}
hook_audit={rel(audit) if audit else 'missing'}
""")
    pack_inputs.append(manifest)
    with tarfile.open(pack, "w:gz") as tar:
        for p in pack_inputs:
            if p.exists() and p.is_file():
                tar.add(p, arcname=f"A24_review_pack/{rel(p)}")
    contents.write_text(subprocess.getoutput(f"tar -tzf {pack}") + "\n")
    content_text = contents.read_text(errors="replace")
    required = ["latpc_shadow_vm.h", "nested_head_patch", "top_level_head_patch", "final_summary", "behavior_equivalence", "detector_ready_derived_stats", "trace_availability", "sample_dump", "hook_exactness"]
    checks = {
        "latpc_shadow_vm.h": "latpc_shadow_vm.h" in content_text,
        "nested patch file": "nested_head_patch" in content_text,
        "top-level patch file": "top_level_head_patch" in content_text,
        "final summary": "final_summary" in content_text or "hardening_final_summary" in content_text,
        "behavior equivalence CSV": "behavior_equivalence" in content_text,
        "derived stats CSV": "detector_ready_derived_stats" in content_text,
        "trace availability CSV": "trace_availability" in content_text,
        "sample dump/manifest": "sample_dump" in content_text,
        "hook exactness audit": "hook_exactness" in content_text,
    }
    verify_status = "PASS" if all(checks.values()) and status == "PASS" else "FAIL_PACK_INCOMPLETE"
    verification.write_text("# A24E Review Pack Verification\n\n" + "\n".join(f"- {k}: {'PASS' if v else 'FAIL'}" for k, v in checks.items()) + f"\n\n- Status: {verify_status}\n- Review pack: `{rel(pack)}`\n")
    write_csv(checklist, [{"item": k, "status": "PASS" if v else "FAIL", "evidence": rel(pack)} for k, v in checks.items()], ["item", "status", "evidence"])
    stage_report(summary, "A24E LATPC Closeout Review Pack And Handoff", verify_status, start_iso, start, ["python3 scripts/accelsim/a24e_closeout_review_pack.py", f"tar -tzf {rel(pack)}"], [rel(summary), rel(pack), rel(contents), rel(verification), rel(checklist)], f"review_pack={rel(pack)} status={verify_status}", "none" if verify_status == "PASS" else "review pack missing required content", ["Review pack is not committed.", "A24 remains shadow substrate hardening only."])
    print(f"A24E status: {verify_status}")
    print(f"A24E review pack: {rel(pack)}")
    return 0 if verify_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
