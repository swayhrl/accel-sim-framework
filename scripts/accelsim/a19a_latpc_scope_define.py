#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import (
    REPORT_DIR,
    clean,
    ensure_local_dirs,
    latest,
    rel,
    selected_workload,
    ts,
    write_csv,
    write_stage_report,
)


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    selected = selected_workload()
    scope_csv = REPORT_DIR / f"A19A_latpc_vm_tlb_ptw_scope_{stamp}.csv"
    report = REPORT_DIR / f"A19A_latpc_vm_tlb_ptw_scope_{stamp}.md"
    a18_spec = latest("A18A_latpc_stats_field_spec_*.csv")
    rows = [
        {
            "candidate_module": "warp_memory_instruction_address_source",
            "expected_construct": "per-lane effective address and derived VPN",
            "candidate_files": "gpu-simulator/gpgpu-sim/src/abstract_hardware_model.{h,cc}; gpu-simulator/trace-driven/trace_driven.cc; gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.cc",
            "candidate_hook": "warp_inst_t::set_addr, warp_inst_t::generate_mem_accesses, trace_shader_core_ctx::checkExecutionStatusAndUpdate",
            "target_stats_fields": "latpc_vpn_observation_total; latpc_regular_stream_detected_total",
            "a19_scope": "inspect_only",
            "a20_relevance": "Regularity Detector input",
        },
        {
            "candidate_module": "l1_tlb",
            "expected_construct": "L1 TLB access/hit/miss accounting",
            "candidate_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.h; gpu-simulator/gpgpu-sim/src/accelwattch/*.xml",
            "candidate_hook": "m_num_tlb_hits; m_num_tlb_accesses if producer exists",
            "target_stats_fields": "latpc_l1_tlb_access_total; latpc_l1_tlb_miss_total; latpc_tlb_miss_rate_l1",
            "a19_scope": "inspect_only",
            "a20_relevance": "LATC/LATP demand translation baseline",
        },
        {
            "candidate_module": "l2_tlb",
            "expected_construct": "L2 TLB access/hit/miss accounting",
            "candidate_files": "bounded scan required",
            "candidate_hook": "L2 TLB lookup path if present",
            "target_stats_fields": "latpc_l2_tlb_access_total; latpc_l2_tlb_miss_total; latpc_tlb_miss_rate_l2",
            "a19_scope": "inspect_only",
            "a20_relevance": "LATC hierarchy modeling",
        },
        {
            "candidate_module": "tlb_mshr",
            "expected_construct": "translation MSHR allocation/full/merge events",
            "candidate_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.{h,cc}; cache/mshr files if present",
            "candidate_hook": "MSHR_RC_FAIL; gpgpu_n_intrawarp_mshr_merge if translation-specific producer exists",
            "target_stats_fields": "latpc_l1_tlb_mshr_full_total; latpc_l2_tlb_mshr_full_total; latpc_mshr_merge_candidate_total",
            "a19_scope": "inspect_only",
            "a20_relevance": "LATPC MSHR pressure and coalescing",
        },
        {
            "candidate_module": "page_walk_queue",
            "expected_construct": "translation miss enqueue/dequeue/stall queue",
            "candidate_files": "bounded scan required",
            "candidate_hook": "page-walk queue enqueue/dequeue/sample points",
            "target_stats_fields": "latpc_page_walk_queue_occupancy_sample_total",
            "a19_scope": "inspect_only",
            "a20_relevance": "LATP issue and pressure modeling",
        },
        {
            "candidate_module": "page_table_walker_ptw",
            "expected_construct": "page walk issue/complete/latency",
            "candidate_files": "bounded scan required",
            "candidate_hook": "PTW issue/complete path if present",
            "target_stats_fields": "latpc_page_walk_issued_total",
            "a19_scope": "inspect_only",
            "a20_relevance": "LATP translation prefetch service path",
        },
        {
            "candidate_module": "page_walk_cache_pwc",
            "expected_construct": "PWC lookup/insert/hit/miss",
            "candidate_files": "bounded scan required",
            "candidate_hook": "PWC lookup/insert path if present",
            "target_stats_fields": "future latpc_pwc_* fields if foundation exists",
            "a19_scope": "inspect_only",
            "a20_relevance": "LATPC paper VM hierarchy alignment",
        },
        {
            "candidate_module": "ldst_coalescer_and_data_mshr",
            "expected_construct": "LD/ST coalescer, generic data cache MSHR and memory queue",
            "candidate_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.cc; gpu-simulator/gpgpu-sim/src/gpgpu-sim/l2cache.cc; gpu-simulator/gpgpu-sim/src/gpgpu-sim/mem_fetch.*",
            "candidate_hook": "ldst_unit::process_memory_access_queue*, mem_fetch::get_addr, L2 cache access path",
            "target_stats_fields": "approximate only; not TLB/PTW paper counters",
            "a19_scope": "inspect_only",
            "a20_relevance": "do not confuse data-cache MSHR with TLB/PTW MSHR",
        },
        {
            "candidate_module": "stats_print_path",
            "expected_construct": "safe print-only reporting",
            "candidate_files": "gpu-simulator/gpgpu-sim/src/gpgpu-sim/gpu-sim.cc; gpu-simulator/gpgpu-sim/src/gpgpu-sim/shader.cc",
            "candidate_hook": "gpgpu_sim::gpu_print_stat; shader_core_stats::print",
            "target_stats_fields": "latpc_* print fields",
            "a19_scope": "inspect_only",
            "a20_relevance": "safe validation/reporting path",
        },
    ]
    write_csv(
        scope_csv,
        rows,
        [
            "candidate_module",
            "expected_construct",
            "candidate_files",
            "candidate_hook",
            "target_stats_fields",
            "a19_scope",
            "a20_relevance",
        ],
    )
    status = "PASS"
    workload = clean(selected.get("selected_workload")) or "nw"
    write_stage_report(
        report,
        "A19A LATPC VM/TLB/PTW Scope",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a19a_latpc_scope_define.py"],
        [
            "docs/accelsim_bringup/A19A_latpc_vm_tlb_ptw_scope.md",
            clean(selected.get("_source_path")),
            rel(a18_spec) if a18_spec else "",
        ],
        [rel(scope_csv), rel(report)],
        "none",
        [
            "A19A defines inspection scope only.",
            "No simulator source is changed and no LATPC mechanism is implemented.",
        ],
        f"## Workload Anchor\n\n- Selected workload: `{workload}`\n- Paper workload label: `{clean(selected.get('paper_workload')) or 'NW'}`\n",
    )
    print(f"A19A status: {status}")
    print(f"A19A report: {rel(report)}")
    print(f"A19A scope CSV: {rel(scope_csv)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
