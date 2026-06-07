#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a24_latpc_lib import LOG_DIR, REPORT_DIR, REPO_ROOT, behavior_fields, compare_behavior, ensure_dirs, parse_stats, rel, run_logged, run_nw_variant, stage_report, ts


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    impl_report = REPORT_DIR / f"A24B_detector_ready_stats_impl_{stamp}.md"
    validation = REPORT_DIR / f"A24B_sample_dump_validation_{stamp}.md"
    manifest = REPORT_DIR / f"A24B_sample_dump_manifest_{stamp}.md"
    derived_csv = REPORT_DIR / f"A24B_latpc_detector_ready_derived_stats_{stamp}.csv"
    sample_csv = REPORT_DIR / f"A24B_latpc_shadow_vm_samples_{stamp}.csv"
    build_log = LOG_DIR / f"A24B_{stamp}_build.log"
    build = run_logged(["make", "-C", "./gpu-simulator/"], build_log, cwd=REPO_ROOT)
    status = "PASS" if build["return_code"] == "0" else "FAIL_BUILD"
    blocker = "none" if status == "PASS" else "build failed"
    stage_report(impl_report, "A24B Detector-Ready Stats Implementation", status, start_iso, start, [build["command"]], [rel(impl_report), rel(build_log)], "Built simulator with detector-ready shadow VM source; raw stats expected in shadow runs.", blocker, ["No detector/LATC/LATP/timing implemented.", "PWC remains deferred."])
    if status != "PASS":
        return 1
    shadow_info, shadow_stats = run_nw_variant(stamp, "A24B", "shadow_no_sample", {"ACCELSIM_LATPC_SHADOW_VM": "1"})
    sample_info, sample_stats = run_nw_variant(stamp, "A24B", "shadow_sample", {"ACCELSIM_LATPC_SHADOW_VM": "1", "ACCELSIM_LATPC_SAMPLE_DUMP": "1", "ACCELSIM_LATPC_SAMPLE_LIMIT": "64", "ACCELSIM_LATPC_SAMPLE_PATH": str(sample_csv)})
    sample_exists = sample_csv.exists()
    rows = max(0, len(sample_csv.read_text(errors="replace").splitlines()) - 1) if sample_exists else 0
    cmp = compare_behavior(shadow_stats, sample_stats)
    validation_status = "PASS" if shadow_info["return_code"] == "0" and sample_info["return_code"] == "0" and sample_exists and rows > 0 and all(cmp.values()) else "FAIL_SAMPLE_VALIDATION"
    blocker = "none" if validation_status == "PASS" else f"sample_exists={sample_exists} rows={rows} compare={cmp}"
    derive_cmd = ["python3", "scripts/accelsim/a24_latpc_derive_detector_ready_stats.py", "--log", sample_info["log_path"], "--run-id", "A24B", "--workload", "nw", "--variant", "shadow_sample", "--out", str(derived_csv)]
    derive = run_logged(derive_cmd, LOG_DIR / f"A24B_{stamp}_derive.log", cwd=REPO_ROOT)
    if derive["return_code"] != "0" and validation_status == "PASS":
        validation_status = "FAIL_DERIVED_STATS"
        blocker = "derived stats script failed"
    summary = f"sample_csv={rel(sample_csv)} rows={rows}; shadow={behavior_fields(shadow_stats)} sample={behavior_fields(sample_stats)} compare={cmp}; derived={rel(derived_csv)}"
    stage_report(validation, "A24B Sample Dump Validation", validation_status, start_iso, start, [shadow_info["command"], sample_info["command"], derive["command"]], [rel(validation), rel(sample_csv), rel(derived_csv)], summary, blocker, ["NW only.", "Sample dump is capped.", "Samples are detector-ready observations, not detector output."])
    manifest.write_text(f"""# A24B Sample Dump Manifest

- Start time: {start_iso}
- End time: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}
- Wall seconds: {int(time.time() - start)}
- Status: {validation_status}
- Commands: shadow/sample NW runs and derived stats script
- Output summary: sample dump path `{rel(sample_csv)}`, rows `{rows}`, derived CSV `{rel(derived_csv)}`
- Blocker: {blocker}
- Limitations: capped at 64 samples; no Regularity Detector, LATC, LATP, prefetch, MSHR compression, timing integration, or speedup claim.
""")
    print(f"A24B status: {validation_status}")
    print(f"A24B derived stats: {rel(derived_csv)}")
    print(f"A24B sample dump: {rel(sample_csv)}")
    return 0 if validation_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
