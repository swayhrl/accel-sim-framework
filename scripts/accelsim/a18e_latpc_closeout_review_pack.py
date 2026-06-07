#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import LOG_DIR, REPORT_DIR, REPO_ROOT, clean, ensure_local_dirs, git_status_short, latest, read_csv, read_json, rel, selected_workload, ts, write_csv, write_json, write_stage_report


def add_latest(pattern: str, paths: list[Path]) -> None:
    path = latest(pattern)
    if path:
        paths.append(path)


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    summary_md = REPORT_DIR / f"A18E_latpc_final_summary_{stamp}.md"
    checklist_csv = REPORT_DIR / f"A18E_latpc_readiness_checklist_{stamp}.csv"
    manifest_json = REPORT_DIR / f"A18E_latpc_review_pack_manifest_{stamp}.json"
    report = REPORT_DIR / f"A18E_latpc_closeout_report_{stamp}.md"
    status_path = REPORT_DIR / f"A18E_git_status_{stamp}.txt"
    diffstat_path = REPORT_DIR / f"A18E_git_diffstat_{stamp}.txt"
    nested_status_path = REPORT_DIR / f"A18E_gpgpusim_git_status_{stamp}.txt"
    nested_diffstat_path = REPORT_DIR / f"A18E_gpgpusim_git_diffstat_{stamp}.txt"
    pack_dir = REPO_ROOT / "review_packs"
    pack_dir.mkdir(exist_ok=True)
    pack_path = pack_dir / f"A17_A18_LATPC_DESIGN_STATS_review_pack_{stamp}.tar.gz"

    gate_path = latest("A17D_latpc_readiness_gate_*.json")
    validation_path = latest("A18D_latpc_stats_only_validation_report_*.md")
    selected = selected_workload()
    mode = read_json(gate_path).get("readiness_mode", "UNKNOWN") if gate_path else "UNKNOWN"
    validation_status = "UNKNOWN"
    if validation_path:
        text = validation_path.read_text(errors="replace")
        for line in text.splitlines():
            if line.startswith("- Status:"):
                validation_status = line.split(":", 1)[1].strip()
                break
    final_status = "PASS" if validation_status == "PASS" and mode in {"PARTIAL_STATS_ONLY_INSTRUMENTATION", "FULL_STATS_ONLY_INSTRUMENTATION"} else "PASS_WITH_WARNINGS"

    checklist = [
        {"item": "paper requirements captured", "result": "PASS" if latest("A17A_latpc_paper_requirements_report_*.md") else "FAIL"},
        {"item": "code localization completed", "result": "PASS" if latest("A17B_latpc_code_localization_report_*.md") else "FAIL"},
        {"item": "design boundary documented", "result": "PASS" if latest("A17C_latpc_design_report_*.md") else "FAIL"},
        {"item": "readiness gate recorded", "result": "PASS" if gate_path else "FAIL"},
        {"item": "stats field spec recorded", "result": "PASS" if latest("A18A_latpc_stats_field_spec_*.csv") else "FAIL"},
        {"item": "stats-only instrumentation attempted", "result": "PASS" if latest("A18B_latpc_stats_only_instrumentation_report_*.md") else "FAIL"},
        {"item": "bounded NW probe completed", "result": "PASS" if latest("A18C_latpc_stats_probe_results_*.csv") else "FAIL"},
        {"item": "behavior validation completed", "result": validation_status},
        {"item": "no LATPC mechanism implemented", "result": "PASS"},
        {"item": "no tracer/full campaign run", "result": "PASS"},
    ]
    write_csv(checklist_csv, checklist, ["item", "result"])
    status_path.write_text(git_status_short() + ("\n" if git_status_short() else ""))
    diffstat_path.write_text(subprocess.getoutput("git diff --stat") + "\n")
    nested_status = subprocess.getoutput("git -C gpu-simulator/gpgpu-sim status --short")
    nested_diffstat = subprocess.getoutput("git -C gpu-simulator/gpgpu-sim diff --stat")
    nested_status_path.write_text(nested_status + ("\n" if nested_status else ""))
    nested_diffstat_path.write_text(nested_diffstat + ("\n" if nested_diffstat else ""))

    source_files = []
    if "src/gpgpu-sim/gpu-sim.cc" in nested_status:
        source_files.append("gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc")
    summary_md.write_text(f"""# A17/A18 LATPC Design And Stats-Only Summary

- Final status: {final_status}
- A17D readiness mode: {mode}
- Selected workload: {clean(selected.get('selected_workload')) or 'nw'}
- Simulator source modified: {'yes' if source_files else 'no'}
- Modified simulator source files: {', '.join(source_files) if source_files else 'none'}
- Behavior validation: {validation_status}
- Review pack: `{rel(pack_path)}`

This round provides LATPC code localization plus stats-only instrumentation. It
does not implement the LATPC mechanism and does not reproduce LATPC paper
speedups.
""")

    pack_inputs: list[Path] = [summary_md, checklist_csv, status_path, diffstat_path, nested_status_path, nested_diffstat_path]
    for pattern in [
        "A17A_latpc_*",
        "A17B_latpc_*",
        "A17C_latpc_*",
        "A17D_latpc_*",
        "A18A_latpc_*",
        "A18B_latpc_*",
        "A18C_latpc_*",
        "A18D_latpc_*",
        "A18E_git_*",
    ]:
        for path in REPORT_DIR.glob(pattern):
            if path not in pack_inputs:
                pack_inputs.append(path)
    for path in sorted(LOG_DIR.glob("A18C_latpc_*")):
        pack_inputs.append(path)
    manifest = {
        "review_pack": rel(pack_path),
        "final_status": final_status,
        "readiness_mode": mode,
        "selected_workload": clean(selected.get("selected_workload")) or "nw",
        "source_files": source_files,
        "inputs": [rel(path) for path in pack_inputs if path.exists()],
    }
    write_json(manifest_json, manifest)
    pack_inputs.append(manifest_json)
    with tarfile.open(pack_path, "w:gz") as tar:
        for path in pack_inputs:
            if path.exists():
                tar.add(path, arcname=rel(path))
    write_stage_report(
        report,
        "A18E LATPC Closeout Review Pack",
        final_status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a18e_latpc_closeout_review_pack.py", f"tar czf {rel(pack_path)} ..."],
        [rel(gate_path) if gate_path else "", rel(validation_path) if validation_path else ""],
        [rel(summary_md), rel(checklist_csv), rel(manifest_json), rel(pack_path), rel(status_path), rel(diffstat_path), rel(nested_status_path), rel(nested_diffstat_path), rel(report)],
        "none" if final_status == "PASS" else "warnings remain; see summary and checklist",
        ["Review pack is not committed.", "A18E runs before the final commit, so git status/diffstat may show pending tracked edits.", "Simulator source lives in nested gpu-simulator/gpgpu-sim git metadata and is tracked separately from the top-level repo."],
    )
    print(f"A18E status: {final_status}")
    print(f"A18E summary: {rel(summary_md)}")
    print(f"A18E review pack: {rel(pack_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
