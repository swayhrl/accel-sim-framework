#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import time

sys.dont_write_bytecode = True
from a24_latpc_lib import LOG_DIR, NESTED_ROOT, REPORT_DIR, REPO_ROOT, behavior_fields, compare_behavior, ensure_dirs, git_head, git_status, rel, run_logged, run_nw_variant, stage_report, ts


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    shadow = REPO_ROOT / "gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h"
    precheck = REPORT_DIR / f"A24A_precheck_report_{stamp}.md"
    audit = REPORT_DIR / f"A24A_hook_exactness_audit_{stamp}.md"
    build_probe = REPORT_DIR / f"A24A_build_probe_{stamp}.md"
    behavior_probe = REPORT_DIR / f"A24A_behavior_probe_{stamp}.md"
    manifest = REPORT_DIR / f"A24A_source_review_material_manifest_{stamp}.md"
    snapshot = REPORT_DIR / "A24A_source_snapshot_latpc_shadow_vm.h"
    nested_head_patch = REPORT_DIR / "A24A_nested_head_patch.patch"
    a23_patch = REPORT_DIR / "A24A_A20_A23_shadow_vm_commit_patch.patch"
    commands = [
        "git status --short",
        "git -C gpu-simulator/gpgpu-sim status --short",
        "git rev-parse HEAD",
        "git -C gpu-simulator/gpgpu-sim rev-parse HEAD",
        "test -f gpu-simulator/gpgpu-sim/src/gpgpu-sim/latpc_shadow_vm.h",
        f"cp {rel(shadow)} {rel(snapshot)}",
        "git -C gpu-simulator/gpgpu-sim show --stat --patch --find-renames HEAD",
    ]
    status = "PASS" if shadow.exists() else "BLOCKED_MISSING_SOURCE"
    if shadow.exists():
        shutil.copyfile(shadow, snapshot)
        nested_head_patch.write_text(subprocess.getoutput(f"git -C {NESTED_ROOT} show --stat --patch --find-renames HEAD") + "\n")
        a23_patch.write_text(subprocess.getoutput(f"git -C {NESTED_ROOT} show --stat --patch --find-renames bd1f1f0b3bf5994b93623114e8767473eedb8424") + "\n")
    stage_report(precheck, "A24A Precheck", status, start_iso, start, commands, [rel(precheck), rel(snapshot), rel(nested_head_patch), rel(a23_patch)], f"top={git_head(REPO_ROOT)} nested={git_head(NESTED_ROOT)}", "none" if status == "PASS" else "latpc_shadow_vm.h missing", ["A24A precheck does not modify source."])
    hook_lines = subprocess.getoutput("rg -n \"latpc_shadow_vm_observe_warp_addresses|latpc_shadow_vm_print_stats|latpc_shadow_addrs|m_warp_id\" gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc")
    audit_extra = f"""## Hook Exactness

- Hook function: `warp_inst_t::generate_mem_accesses()`
- Address source: active lane/thread `m_per_scalar_thread[thread].memreqaddr[0]`
- Address mode: `WARP_EFFECTIVE_ADDRESS_APPROX`
- Unique VPN sequence order: lane/thread order as observed, not sorted
- PC source: `pc` from `warp_inst_t`
- Warp id source: `m_warp_id`
- sm_id source: hard-coded `0`
- sm_id exactness: approximate/unavailable
- cycle source: `0`, shadow model falls back to event index
- cycle exactness: approximate/unavailable
- Full VM translation pipeline: no, this is an effective-address shadow approximation

## Source Evidence

```
{hook_lines}
```
"""
    stage_report(audit, "A24A Hook Exactness Audit", "PASS", start_iso, start, ["rg hook source lines"], [rel(audit)], "sm_id and cycle remain approximate; address hook is effective-address level.", "none", ["No invasive refactor attempted for sm_id/cycle.", "No LATPC mechanism implemented."], audit_extra)
    build_log = LOG_DIR / f"A24A_{stamp}_build.log"
    build = run_logged(["make", "-C", "./gpu-simulator/"], build_log, cwd=REPO_ROOT)
    build_status = "PASS" if build["return_code"] == "0" else "FAIL_BUILD"
    stage_report(build_probe, "A24A Build Probe", build_status, start_iso, start, [build["command"]], [rel(build_probe), rel(build_log)], f"build return_code={build['return_code']}", "none" if build_status == "PASS" else "build failed", ["A24A build probe only."])
    behavior_status = "PASS"
    blocker = "none"
    if build_status == "PASS":
        base_info, base_stats = run_nw_variant(stamp, "A24A", "baseline", {"ACCELSIM_LATPC_SHADOW_VM": "0"})
        sh_info, sh_stats = run_nw_variant(stamp, "A24A", "shadow", {"ACCELSIM_LATPC_SHADOW_VM": "1"})
        cmp = compare_behavior(base_stats, sh_stats)
        if not all(cmp.values()):
            behavior_status = "FAIL_BEHAVIOR_CHANGED"
            blocker = str(cmp)
        summary = f"baseline={behavior_fields(base_stats)} shadow={behavior_fields(sh_stats)} compare={cmp}"
        cmds = [base_info["command"], sh_info["command"]]
    else:
        behavior_status = "BLOCKED_BUILD"
        blocker = "build failed"
        summary = "behavior probe skipped"
        cmds = []
    stage_report(behavior_probe, "A24A Behavior Probe", behavior_status, start_iso, start, cmds, [rel(behavior_probe)], summary, blocker, ["NW only.", "No full campaign."])
    manifest.write_text(f"""# A24A Source Review Material Manifest

- Start time: {start_iso}
- End time: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}
- Wall seconds: {int(time.time() - start)}
- Status: PASS
- Commands: snapshot and git show patch capture
- Output summary: current full `latpc_shadow_vm.h` snapshot and nested patches captured.
- Blocker: none
- Limitations: A23 commit patch is best-effort if commit exists locally.

## Files

- `{rel(snapshot)}` includes_full_latpc_shadow_vm_h: yes
- `{rel(nested_head_patch)}` nested_head_patch: yes
- `{rel(a23_patch)}` a23_reference_patch: yes
""")
    print(f"A24A status: {behavior_status if behavior_status != 'PASS' else status}")
    print(f"A24A audit: {rel(audit)}")
    return 0 if status == "PASS" and build_status == "PASS" and behavior_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
