#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, ensure_local_dirs, latest, read_csv, rel, ts, write_csv, write_stage_report


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    scan_path = latest("A19B_latpc_vm_module_scan_*.csv")
    spec_path = latest("A18A_latpc_stats_field_spec_*.csv")
    csv_path = REPORT_DIR / f"A19C_latpc_hook_mapping_{stamp}.csv"
    report = REPORT_DIR / f"A19C_latpc_hook_mapping_{stamp}.md"
    rows: list[dict[str, str]] = []
    status = "PASS_WITH_WARNINGS"
    blocker = "none"
    if not scan_path:
        status = "BLOCKED_NO_A19B"
        blocker = "missing A19B scan CSV"
    else:
        scan = read_csv(scan_path)
        high = {(r["module"], r["path"], r["symbol"]) for r in scan if r["confidence"] == "HIGH"}
        has_warp_addr = any(item[0] == "warp_address" for item in high)
        has_stats_print = any(item[0] == "stats_print" for item in high)
        has_tlb_decl = any(r["module"] == "tlb" and "m_num_tlb" in r["symbol"] for r in scan)
        rows = [
            {
                "hook_id": "A19C_HOOK_001",
                "target_field": "latpc_vpn_observation_total",
                "mapped_module": "warp_memory_instruction_address_source",
                "candidate_symbol": "warp_inst_t::generate_mem_accesses / memreqaddr",
                "availability": "APPROXIMATED" if has_warp_addr else "UNAVAILABLE",
                "safe_stats_only_hook": "yes_read_only_with_page_size_assumption" if has_warp_addr else "no",
                "a20_action": "derive page number from effective address only if A20 explicitly accepts approximate VM substrate",
                "risk": "effective address is not proven to be real virtual page translation state",
            },
            {
                "hook_id": "A19C_HOOK_002",
                "target_field": "latpc_regular_stream_detected_total",
                "mapped_module": "regularity_detector",
                "candidate_symbol": "future detector over address-derived page stream",
                "availability": "DEFERRED",
                "safe_stats_only_hook": "no_current_detector",
                "a20_action": "implement detector only after A20 defines semantic boundary",
                "risk": "detector would be LATPC mechanism, forbidden in A19",
            },
            {
                "hook_id": "A19C_HOOK_003",
                "target_field": "latpc_l1_tlb_access_total; latpc_l1_tlb_miss_total",
                "mapped_module": "l1_tlb",
                "candidate_symbol": "m_num_tlb_hits / m_num_tlb_accesses",
                "availability": "UNAVAILABLE",
                "safe_stats_only_hook": "no_producer_not_confirmed" if has_tlb_decl else "no",
                "a20_action": "find or add real producer before using as LATPC evidence",
                "risk": "declared counters alone do not prove an active TLB model",
            },
            {
                "hook_id": "A19C_HOOK_004",
                "target_field": "latpc_l2_tlb_access_total; latpc_l2_tlb_miss_total",
                "mapped_module": "l2_tlb",
                "candidate_symbol": "none localized",
                "availability": "UNAVAILABLE",
                "safe_stats_only_hook": "no",
                "a20_action": "requires L2 TLB substrate or explicit model addition",
                "risk": "faithful LATC hierarchy cannot be claimed without L2 TLB",
            },
            {
                "hook_id": "A19C_HOOK_005",
                "target_field": "latpc_l1_tlb_mshr_full_total; latpc_l2_tlb_mshr_full_total; latpc_mshr_merge_candidate_total",
                "mapped_module": "tlb_mshr",
                "candidate_symbol": "generic data-cache MSHR / MSHR_RC_FAIL / gpgpu_n_intrawarp_mshr_merge",
                "availability": "APPROXIMATED",
                "safe_stats_only_hook": "no_for_paper_tlb_stats",
                "a20_action": "separate data-cache MSHR from translation MSHR before mechanism work",
                "risk": "generic data-cache MSHR is not translation MSHR",
            },
            {
                "hook_id": "A19C_HOOK_006",
                "target_field": "latpc_page_walk_issued_total; latpc_page_walk_queue_occupancy_sample_total",
                "mapped_module": "ptw_page_walk_queue",
                "candidate_symbol": "none localized",
                "availability": "UNAVAILABLE",
                "safe_stats_only_hook": "no",
                "a20_action": "requires PTW/page-walk queue substrate",
                "risk": "LATP issue/complete behavior cannot be represented without PTW path",
            },
            {
                "hook_id": "A19C_HOOK_007",
                "target_field": "future latpc_pwc_*",
                "mapped_module": "page_walk_cache_pwc",
                "candidate_symbol": "none localized",
                "availability": "UNAVAILABLE",
                "safe_stats_only_hook": "no",
                "a20_action": "requires PWC substrate if paper-aligned hierarchy includes it",
                "risk": "PWC benefits cannot be separated from TLB/PTW without model support",
            },
            {
                "hook_id": "A19C_HOOK_008",
                "target_field": "latpc_stats_only_marker; latpc_stats_only_version; latpc_functional_mechanism_enabled",
                "mapped_module": "stats_print_path",
                "candidate_symbol": "gpgpu_sim::gpu_print_stat",
                "availability": "IMPLEMENTED" if has_stats_print else "UNAVAILABLE",
                "safe_stats_only_hook": "yes_print_only" if has_stats_print else "no",
                "a20_action": "continue using for validation metadata",
                "risk": "metadata only, not mechanism evidence",
            },
        ]
    write_csv(
        csv_path,
        rows,
        ["hook_id", "target_field", "mapped_module", "candidate_symbol", "availability", "safe_stats_only_hook", "a20_action", "risk"],
    )
    unavailable = len([r for r in rows if r.get("availability") == "UNAVAILABLE"])
    implemented = len([r for r in rows if r.get("availability") == "IMPLEMENTED"])
    approximated = len([r for r in rows if r.get("availability") == "APPROXIMATED"])
    extra = f"## Hook Summary\n\n- IMPLEMENTED: {implemented}\n- APPROXIMATED: {approximated}\n- UNAVAILABLE: {unavailable}\n"
    if unavailable:
        blocker = "core TLB/PTW/PWC hooks unavailable for faithful LATPC mechanism"
    write_stage_report(
        report,
        "A19C LATPC Hook Mapping",
        status,
        start_iso,
        start,
        ["python3 scripts/accelsim/a19c_latpc_hook_mapping.py"],
        [rel(scan_path) if scan_path else "", rel(spec_path) if spec_path else ""],
        [rel(csv_path), rel(report)],
        blocker,
        [
            "A19C maps hooks only; it does not add counters or modify source.",
            "Approximate hooks are not enough for faithful LATPC claims.",
        ],
        extra,
    )
    print(f"A19C status: {status}")
    print(f"A19C report: {rel(report)}")
    print(f"A19C hook mapping CSV: {rel(csv_path)}")
    return 0 if not status.startswith("BLOCKED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
