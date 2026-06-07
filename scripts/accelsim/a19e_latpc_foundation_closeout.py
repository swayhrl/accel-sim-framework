#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tarfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, REPO_ROOT, clean, ensure_local_dirs, git_status_short, latest, read_json, rel, selected_workload, ts, write_csv, write_json, write_stage_report


def stage_status(report: Path | None) -> str:
    if not report or not report.exists():
        return "MISSING"
    for line in report.read_text(errors="replace").splitlines():
        if line.startswith("- Status:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    summary = REPORT_DIR / f"A19E_latpc_foundation_closeout_{stamp}.md"
    checklist_csv = REPORT_DIR / f"A19E_latpc_readiness_checklist_{stamp}.csv"
    manifest_json = REPORT_DIR / f"A19E_latpc_review_pack_manifest_{stamp}.json"
    status_path = REPORT_DIR / f"A19E_git_status_{stamp}.txt"
    nested_status_path = REPORT_DIR / f"A19E_gpgpusim_git_status_{stamp}.txt"
    pack_dir = REPO_ROOT / "review_packs"
    pack_dir.mkdir(exist_ok=True)
    pack = pack_dir / f"A19_LATPC_VM_TLB_PTW_FOUNDATION_review_pack_{stamp}.tar.gz"
    selected = selected_workload()
    readiness_path = latest("A19D_latpc_foundation_readiness_*.json")
    readiness = read_json(readiness_path) if readiness_path else {}
    mode = clean(readiness.get("readiness_mode")) or "UNKNOWN"
    reports = {
        "A19A": latest("A19A_latpc_vm_tlb_ptw_scope_*.md"),
        "A19B": latest("A19B_latpc_vm_module_scan_*.md"),
        "A19C": latest("A19C_latpc_hook_mapping_*.md"),
        "A19D": latest("A19D_latpc_foundation_assessment_*.md"),
    }
    checklist = [
        {"stage": stage, "report": rel(path) if path else "", "status": stage_status(path)}
        for stage, path in reports.items()
    ]
    top_status = git_status_short()
    nested_status = subprocess.getoutput("git -C gpu-simulator/gpgpu-sim status --short")
    status_path.write_text(top_status + ("\n" if top_status else ""))
    nested_status_path.write_text(nested_status + ("\n" if nested_status else ""))
    checklist.extend(
        [
            {"stage": "git_top_level_clean", "report": rel(status_path), "status": "PASS" if not top_status else "WARN_DIRTY"},
            {"stage": "git_gpgpusim_clean", "report": rel(nested_status_path), "status": "PASS" if not nested_status else "WARN_DIRTY"},
            {"stage": "no_simulator_source_change", "report": "", "status": "PASS" if not nested_status else "WARN_SOURCE_DIRTY"},
        ]
    )
    write_csv(checklist_csv, checklist, ["stage", "report", "status"])
    final_status = "PASS" if all(row["status"] in {"PASS", "PASS_WITH_WARNINGS"} for row in checklist[:4]) and not top_status and not nested_status else "PASS_WITH_WARNINGS"
    summary.write_text(f"""# A19 LATPC VM/TLB/PTW Foundation Closeout

- Final status: {final_status}
- Selected workload: {clean(selected.get('selected_workload')) or 'nw'} / {clean(selected.get('paper_workload')) or 'NW'}
- A19D readiness mode: {mode}
- Review pack: `{rel(pack)}`
- Simulator source modified: no

## Recommendation

A19 found address-observation and stats-print foundations, plus generic
data-cache/MSHR structures. It did not localize a complete, active VM/TLB/PTW/PWC
foundation sufficient for faithful LATPC mechanism implementation. A20 should
first add or explicitly define the VM/TLB/PTW/PWC substrate before claiming
LATPC mechanism behavior.

This is a foundation assessment only. It is not LATPC mechanism implementation.
""")
    pack_inputs: list[Path] = [summary, checklist_csv, status_path, nested_status_path]
    for pattern in [
        "A19A_latpc_vm_tlb_ptw_scope_*",
        "A19B_latpc_vm_module_scan_*",
        "A19C_latpc_hook_mapping_*",
        "A19D_latpc_foundation_*",
    ]:
        pack_inputs.extend(sorted(REPORT_DIR.glob(pattern)))
    manifest = {
        "review_pack": rel(pack),
        "final_status": final_status,
        "readiness_mode": mode,
        "selected_workload": clean(selected.get("selected_workload")) or "nw",
        "simulator_source_modified": False,
        "inputs": [rel(path) for path in pack_inputs if path.exists()],
    }
    write_json(manifest_json, manifest)
    pack_inputs.append(manifest_json)
    with tarfile.open(pack, "w:gz") as tar:
        for path in pack_inputs:
            if path.exists():
                tar.add(path, arcname=rel(path))
    write_stage_report(
        summary,
        "A19E LATPC Foundation Closeout",
        final_status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a19e_latpc_foundation_closeout.py", f"tar czf {rel(pack)} ..."],
        [rel(readiness_path) if readiness_path else ""],
        [rel(summary), rel(checklist_csv), rel(manifest_json), rel(pack), rel(status_path), rel(nested_status_path)],
        "none" if final_status == "PASS" else "warnings remain; see checklist",
        [
            "Review pack is not committed.",
            "A19 does not modify simulator source or implement LATPC mechanism.",
        ],
        f"## A19D Readiness Mode\n\n`{mode}`\n",
    )
    print(f"A19E status: {final_status}")
    print(f"A19E summary: {rel(summary)}")
    print(f"A19E review pack: {rel(pack)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
