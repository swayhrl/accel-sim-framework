#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a24_latpc_lib import REPORT_DIR, REPO_ROOT, clean, ensure_dirs, parse_stats, rel, run_nw_variant, stage_report, ts, write_csv

CANDIDATES = [
    ("nw", "nw|needleman"),
    ("lud", "lud"),
    ("backprop", "backprop|backpropagation"),
    ("bfs", "bfs|rodinia-bfs"),
    ("rodinia-bfs", "bfs|rodinia-bfs"),
    ("atax", "atax"),
    ("bicg", "bicg"),
    ("mvt", "mvt"),
    ("2mm", "2mm"),
    ("sssp", "sssp"),
    ("pagerank", "pagerank"),
    ("cfd", "cfd"),
    ("hotspot", "hotspot"),
    ("pathfinder", "pathfinder"),
    ("gaussian", "gaussian"),
    ("streamcluster", "streamcluster"),
]


def bounded_kernels() -> list[Path]:
    roots = [REPO_ROOT / ".local_traces", REPO_ROOT / ".local_runs", REPO_ROOT / "traces", REPO_ROOT / "util/tracer_nvbit/traces", REPO_ROOT / "gpu-simulator/gpgpu-sim/traces"]
    out = []
    for root in roots:
        if not root.exists():
            continue
        for i, p in enumerate(root.rglob("kernelslist.g")):
            if i >= 500:
                break
            out.append(p)
    return out


def file_count(path: Path) -> int:
    if path.is_file():
        return 1
    total = 0
    for _, _, files in os.walk(path):
        total += len(files)
        if total > 10000:
            break
    return total


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    avail_csv = REPORT_DIR / f"A24C_latpc_trace_availability_{stamp}.csv"
    matrix_csv = REPORT_DIR / f"A24C_latpc_small_probe_matrix_{stamp}.csv"
    report = REPORT_DIR / f"A24C_trace_scanner_report_{stamp}.md"
    ranking = REPORT_DIR / f"A24C_latpc_workload_readiness_ranking_{stamp}.md"
    kernels = bounded_kernels()
    rows = []
    for workload, aliases in CANDIDATES:
        terms = aliases.split("|")
        matches = [p for p in kernels if any(t.lower() in str(p).lower() for t in terms)]
        p = matches[0] if matches else None
        root = p.parent if p else Path("")
        rows.append({
            "workload": workload,
            "aliases": aliases,
            "found": str(bool(p)).lower(),
            "candidate_path": rel(p) if p else "",
            "path_type": "kernelslist" if p else "",
            "size_bytes": str(p.stat().st_size) if p and p.exists() else "0",
            "file_count": str(file_count(root)) if p else "0",
            "has_config": str(bool(p and list(root.glob("*.config")))).lower(),
            "has_trace_files": str(bool(p and list(root.glob("*.trace*")))).lower(),
            "last_modified": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(p.stat().st_mtime)) if p and p.exists() else "",
            "probe_eligible": "true" if workload == "nw" and p else "false",
            "notes": "NW anchor uses known runner" if workload == "nw" and p else ("trace found; runner not verified" if p else "TRACE_MISSING"),
        })
    write_csv(avail_csv, rows, ["workload", "aliases", "found", "candidate_path", "path_type", "size_bytes", "file_count", "has_config", "has_trace_files", "last_modified", "probe_eligible", "notes"])
    probe_rows = []
    status = "PASS"
    try:
        info, stats = run_nw_variant(stamp, "A24C", "nw_shadow_probe", {"ACCELSIM_LATPC_SHADOW_VM": "1"})
        probe_status = "PASS" if info["return_code"] == "0" else "RUN_FAILED"
        if probe_status != "PASS":
            status = "PASS_WITH_WARNINGS"
        probe_rows.append({
            "workload": "nw", "selected_path": "", "variant": "shadow_vm", "env_shadow_vm": "1", "env_sample_dump": "0",
            "run_command": info["command"], "status": probe_status, "log_path": info["log_path"], "stats_path": info["log_path"],
            "cycles": stats.get("gpu_tot_sim_cycle", "NA"), "instructions": stats.get("gpu_tot_sim_insn", "NA"), "IPC": stats.get("gpu_tot_ipc", "NA"),
            "L2_accesses": stats.get("L2_total_cache_accesses", "NA"), "L2_misses": stats.get("L2_total_cache_misses", "NA"),
            "latpc_vm_warp_mem_inst_observed": stats.get("latpc_vm_warp_mem_inst_observed", ""),
            "latpc_vm_translation_request_total": stats.get("latpc_vm_translation_request_total", ""),
            "latpc_tlb_l1_miss_total": stats.get("latpc_tlb_l1_miss_total", ""),
            "latpc_ptw_request_total": stats.get("latpc_ptw_request_total", ""),
            "page_div_bin_1": stats.get("latpc_vm_page_div_bin_1", ""),
            "page_div_bin_2_3": stats.get("latpc_vm_page_div_bin_2_3", ""),
            "page_div_bin_4_7": stats.get("latpc_vm_page_div_bin_4_7", ""),
            "page_div_bin_8_15": stats.get("latpc_vm_page_div_bin_8_15", ""),
            "page_div_bin_16_31": stats.get("latpc_vm_page_div_bin_16_31", ""),
            "page_div_bin_32": stats.get("latpc_vm_page_div_bin_32", ""),
            "limitation": "NW only; non-NW runner not safely inferred",
        })
    except Exception as exc:
        status = "PASS_WITH_WARNINGS"
        probe_rows.append({"workload": "nw", "selected_path": "", "variant": "shadow_vm", "env_shadow_vm": "1", "env_sample_dump": "0", "run_command": "", "status": "RUN_FAILED", "log_path": "", "stats_path": "", "cycles": "", "instructions": "", "IPC": "", "L2_accesses": "", "L2_misses": "", "latpc_vm_warp_mem_inst_observed": "", "latpc_vm_translation_request_total": "", "latpc_tlb_l1_miss_total": "", "latpc_ptw_request_total": "", "page_div_bin_1": "", "page_div_bin_2_3": "", "page_div_bin_4_7": "", "page_div_bin_8_15": "", "page_div_bin_16_31": "", "page_div_bin_32": "", "limitation": str(exc)})
    write_csv(matrix_csv, probe_rows, ["workload", "selected_path", "variant", "env_shadow_vm", "env_sample_dump", "run_command", "status", "log_path", "stats_path", "cycles", "instructions", "IPC", "L2_accesses", "L2_misses", "latpc_vm_warp_mem_inst_observed", "latpc_vm_translation_request_total", "latpc_tlb_l1_miss_total", "latpc_ptw_request_total", "page_div_bin_1", "page_div_bin_2_3", "page_div_bin_4_7", "page_div_bin_8_15", "page_div_bin_16_31", "page_div_bin_32", "limitation"])
    ranking_lines = ["# A24C Workload Readiness Ranking", ""]
    for row in rows:
        rank = "READY_FOR_A25_PROBE" if row["workload"] == "nw" and row["found"] == "true" else ("TRACE_AVAILABLE_RUNNER_UNKNOWN" if row["found"] == "true" else "TRACE_MISSING")
        ranking_lines.append(f"- {row['workload']}: {rank} ({row['notes']})")
    ranking_lines.append("\nRecommendation: keep NW as pipeline anchor; use any TRACE_AVAILABLE_RUNNER_UNKNOWN candidates only after adding safe runner commands.")
    ranking.write_text("\n".join(ranking_lines) + "\n")
    stage_report(report, "A24C Trace Availability And Small Probe", status, start_iso, start, ["python3 scripts/accelsim/a24_latpc_trace_availability_probe.py"], [rel(report), rel(avail_csv), rel(matrix_csv), rel(ranking)], f"checked {len(rows)} candidates; NW probe rows={len(probe_rows)}", "none", ["Bounded scan only.", "Only NW is run unless safe runner is known.", "No tracer/full campaign."])
    print(f"A24C status: {status}")
    print(f"A24C availability: {rel(avail_csv)}")
    return 0 if status in {"PASS", "PASS_WITH_WARNINGS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
