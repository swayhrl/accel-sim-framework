#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, ensure_local_dirs, rel, ts, write_csv, write_stage_report

REPO_ROOT = Path(__file__).resolve().parents[2]

TERMS = [
    "warp_inst_t",
    "generate_mem_accesses",
    "memory_coalescing_arch",
    "mem_fetch",
    "tlb",
    "TLB",
    "mshr",
    "MSHR",
    "page_walk",
    "page walk",
    "PTW",
    "PWC",
    "new_addr_type",
    "print_stats",
    "gpu_tot_sim_cycle",
]


def scan_files() -> list[dict[str, str]]:
    roots = [REPO_ROOT / "gpu-simulator/gpgpu-sim/src", REPO_ROOT / "gpu-simulator/trace-driven", REPO_ROOT / "scripts/accelsim"]
    rows: list[dict[str, str]] = []
    pattern = re.compile("|".join(re.escape(term) for term in TERMS))
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".cc", ".cpp", ".h", ".hpp", ".py", ".sh", ".config", ".xml", ".md"}:
                continue
            if any(part in {"build", ".git"} for part in path.parts):
                continue
            try:
                lines = path.read_text(errors="replace").splitlines()
            except OSError:
                continue
            for line_no, line in enumerate(lines, 1):
                if pattern.search(line):
                    rows.append({"file": rel(path), "line": str(line_no), "match": line.strip()[:220]})
                    if len(rows) >= 1200:
                        return rows
    return rows


def matrix_rows() -> list[dict[str, str]]:
    return [
        {
            "area": "warp_memory_instruction_address_vpn",
            "primary_files": "gpu-simulator/gpgpu-sim/src/abstract_hardware_model.cc; gpu-simulator/gpgpu-sim/src/abstract_hardware_model.h; gpu-simulator/trace-driven/trace_driven.cc",
            "evidence": "warp_inst_t::generate_mem_accesses, memory_coalescing_arch, memreqaddr, new_addr_type, trace instruction set_addr",
            "confidence": "HIGH_FOR_ADDRESS_OBSERVATION_LOW_FOR_TRUE_VPN",
            "a18_safe_stats_only_hook": "NO_SOURCE_HOOK_THIS_ROUND",
            "notes": "address observations are visible, but virtual-to-physical/TLB semantics are not isolated enough for behavior-safe counters",
        },
        {
            "area": "tlb_coalescer_or_l1_l2_tlb",
            "primary_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.h; gpu-simulator/gpgpu-sim/src/accelwattch/*.xml",
            "evidence": "m_num_tlb_hits/m_num_tlb_accesses members exist; many XML itlb/dtlb references are power-model metadata",
            "confidence": "PARTIAL",
            "a18_safe_stats_only_hook": "NO",
            "notes": "no clear LATPC-ready TLB coalescer or PTW control path was localized",
        },
        {
            "area": "l1_l2_tlb_mshr",
            "primary_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.h; gpu-simulator/gpgpu-sim/src/gpgpu-sim/l2cache.cc",
            "evidence": "generic MSHR and cache reservation structures exist; TLB-specific MSHR path not localized",
            "confidence": "LOW",
            "a18_safe_stats_only_hook": "NO",
            "notes": "adding counters here could accidentally imply a TLB MSHR model that is not proven",
        },
        {
            "area": "page_walk_queue_ptw_pwc",
            "primary_files": "",
            "evidence": "bounded scan did not find a concrete page walk queue, PTW, or PWC implementation path",
            "confidence": "LOW",
            "a18_safe_stats_only_hook": "NO",
            "notes": "future LATPC mechanism needs deeper design before implementation",
        },
        {
            "area": "stats_print",
            "primary_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc",
            "evidence": "gpgpu_sim::gpu_print_stat prints key = value simulator stats",
            "confidence": "HIGH",
            "a18_safe_stats_only_hook": "YES_PRINT_ONLY",
            "notes": "safe location for latpc_* metadata/sentinel stats with no control-flow or timing impact",
        },
        {
            "area": "build_run_command",
            "primary_files": "scripts/accelsim/run_a16_latpc_variant_matrix.py; scripts/accelsim/a13_experiment_matrix_runner.py",
            "evidence": "combined gpgpusim.config and accel-sim.out -config ./gpgpusim.config -trace ./traces/kernelslist.g",
            "confidence": "HIGH",
            "a18_safe_stats_only_hook": "N/A",
            "notes": "A18C can reuse the bounded A16 selected workload command pattern",
        },
    ]


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    scan_csv = REPORT_DIR / f"A17B_latpc_symbol_scan_{stamp}.csv"
    matrix_csv = REPORT_DIR / f"A17B_latpc_localization_matrix_{stamp}.csv"
    report = REPORT_DIR / f"A17B_latpc_code_localization_report_{stamp}.md"
    scan = scan_files()
    matrix = matrix_rows()
    write_csv(scan_csv, scan, ["file", "line", "match"])
    write_csv(matrix_csv, matrix, ["area", "primary_files", "evidence", "confidence", "a18_safe_stats_only_hook", "notes"])
    status = "PASS_WITH_WARNINGS"
    blocker = "no concrete PTW/PWC/page-walk queue path localized; A18 must be print-only or blocked"
    write_stage_report(
        report,
        "A17B LATPC Code Localization",
        status,
        start_iso,
        start,
        ["bounded file scan of gpu-simulator/gpgpu-sim/src, gpu-simulator/trace-driven, scripts/accelsim"],
        ["A17A requirements", "LATPC paper guidance"],
        [rel(scan_csv), rel(matrix_csv), rel(report)],
        blocker,
        ["Search is bounded to simulator source, trace-driven source, and existing scripts.", "No simulator source is changed in A17B."],
    )
    print(f"A17B status: {status}")
    print(f"A17B report: {rel(report)}")
    print(f"A17B localization matrix: {rel(matrix_csv)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
