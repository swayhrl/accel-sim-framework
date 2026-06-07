#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

from a17_a18_latpc_lib import REPORT_DIR, clean, ensure_local_dirs, rel, selected_workload, ts, write_csv, write_json, write_stage_report

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    ensure_local_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    pdf = REPO_ROOT / "docs/accelsim_bringup/paper/2025_MICRO_LATPC_TLB_Prefetch_MSHR.pdf"
    text_path = REPORT_DIR / f"A17A_latpc_paper_text_extract_{stamp}.txt"
    req_csv = REPORT_DIR / f"A17A_latpc_mechanism_requirements_{stamp}.csv"
    stats_csv = REPORT_DIR / f"A17A_latpc_target_stats_{stamp}.csv"
    profile_json = REPORT_DIR / f"A17A_latpc_paper_requirements_profile_{stamp}.json"
    report = REPORT_DIR / f"A17A_latpc_paper_requirements_report_{stamp}.md"
    commands = [f"pdftotext {rel(pdf)} {rel(text_path)}"]
    status = "PASS"
    blocker = "none"
    if pdf.exists():
        proc = subprocess.run(["pdftotext", str(pdf), str(text_path)], cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if proc.returncode != 0:
            status = "PASS_WITH_WARNINGS"
            blocker = "pdftotext failed; requirements use manually encoded paper facts and guidance"
            text_path.write_text("")
    else:
        status = "BLOCKED_NO_PAPER"
        blocker = f"missing paper PDF: {pdf}"
        text_path.write_text("")

    selected = selected_workload()
    mechanism_rows = [
        {
            "requirement_id": "LATPC_REQ_001",
            "paper_component": "Regularity Detector",
            "manual_fact": "LATPC detects regular virtual page number behavior in memory-reference streams to predict future translation demand.",
            "minimal_design_implication": "Need warp-level or memory-instruction-level VPN observation and stride/regularity metadata.",
            "a18_stats_need": "latpc_vpn_observation_total; latpc_regular_stream_detected_total",
            "implementation_scope_this_round": "design_only",
        },
        {
            "requirement_id": "LATPC_REQ_002",
            "paper_component": "LATC",
            "manual_fact": "LATC is a translation coalescing/cache-side structure in the LATPC design space, not an output-only statistic.",
            "minimal_design_implication": "Needs explicit translation cache/coalescer state before real mechanism work.",
            "a18_stats_need": "latpc_l1_tlb_miss_total; latpc_l2_tlb_miss_total; latpc_mshr_merge_candidate_total",
            "implementation_scope_this_round": "deferred_mechanism",
        },
        {
            "requirement_id": "LATPC_REQ_003",
            "paper_component": "LATP",
            "manual_fact": "LATP prefetches translations ahead of demand using regularity rather than changing demand instruction scheduling.",
            "minimal_design_implication": "Future implementation must model translation prefetch requests without pretending data prefetch speedup.",
            "a18_stats_need": "latpc_prefetch_candidate_translation_total; latpc_page_walk_queue_occupancy_sample_total",
            "implementation_scope_this_round": "deferred_mechanism",
        },
        {
            "requirement_id": "LATPC_REQ_004",
            "paper_component": "MSHR/Page-walk pressure",
            "manual_fact": "LATPC motivation is tied to translation miss handling pressure and page-walk concurrency, not general L2 data cache hit rate alone.",
            "minimal_design_implication": "Need TLB/PTW/MSHR hooks before claiming paper mechanism behavior.",
            "a18_stats_need": "latpc_l1_tlb_mshr_full_total; latpc_l2_tlb_mshr_full_total; latpc_page_walk_issued_total",
            "implementation_scope_this_round": "stats_only_if_hooks_exist",
        },
        {
            "requirement_id": "LATPC_REQ_005",
            "paper_component": "Evaluation workloads",
            "manual_fact": "For this repo pipeline, NW is the selected bounded LATPC workload because A16 found an existing trace and it is in the LATPC/Rodinia candidate set.",
            "minimal_design_implication": "A18 probe must stay bounded to selected workload NW and not run the full campaign.",
            "a18_stats_need": "latpc_stats_only_marker",
            "implementation_scope_this_round": "metadata_stats_only",
        },
    ]
    stats_rows = [
        {"stat_key": "latpc_stats_only_marker", "paper_target": "no", "semantic": "confirms stats-only instrumentation path printed", "desired_class": "IMPLEMENTED"},
        {"stat_key": "latpc_stats_only_version", "paper_target": "no", "semantic": "records instrumentation generation", "desired_class": "IMPLEMENTED"},
        {"stat_key": "latpc_functional_mechanism_enabled", "paper_target": "no", "semantic": "must remain 0 in A18", "desired_class": "IMPLEMENTED"},
        {"stat_key": "latpc_vpn_observation_total", "paper_target": "yes", "semantic": "observed virtual/page-number samples from memory instructions", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_regular_stream_detected_total", "paper_target": "yes", "semantic": "detected regular streams for future LATP", "desired_class": "DEFERRED"},
        {"stat_key": "latpc_prefetch_candidate_translation_total", "paper_target": "yes", "semantic": "candidate translations that a future LATP might prefetch", "desired_class": "DEFERRED"},
        {"stat_key": "latpc_l1_tlb_access_total", "paper_target": "yes", "semantic": "L1 TLB accesses", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_l1_tlb_miss_total", "paper_target": "yes", "semantic": "L1 TLB misses", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_l2_tlb_access_total", "paper_target": "yes", "semantic": "L2 TLB accesses", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_l2_tlb_miss_total", "paper_target": "yes", "semantic": "L2 TLB misses", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_l1_tlb_mshr_full_total", "paper_target": "yes", "semantic": "L1 TLB MSHR full events", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_l2_tlb_mshr_full_total", "paper_target": "yes", "semantic": "L2 TLB MSHR full events", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_page_walk_issued_total", "paper_target": "yes", "semantic": "page walks issued", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_page_walk_queue_occupancy_sample_total", "paper_target": "yes", "semantic": "PTW queue occupancy samples", "desired_class": "UNAVAILABLE_IF_NO_SAFE_HOOK"},
        {"stat_key": "latpc_mshr_merge_candidate_total", "paper_target": "yes", "semantic": "candidate translation requests that could coalesce", "desired_class": "DEFERRED"},
        {"stat_key": "latpc_tlb_miss_rate_l1", "paper_target": "yes", "semantic": "derived L1 TLB miss rate", "desired_class": "DERIVED"},
        {"stat_key": "latpc_tlb_miss_rate_l2", "paper_target": "yes", "semantic": "derived L2 TLB miss rate", "desired_class": "DERIVED"},
    ]
    profile = {
        "paper": "2025 MICRO LATPC TLB Prefetch MSHR",
        "round": "A17_A18",
        "selected_workload": clean(selected.get("selected_workload")),
        "paper_workload": clean(selected.get("paper_workload")),
        "selected_workload_source": clean(selected.get("_source_path")),
        "manual_fact_policy": "requirements are manually encoded from round guidance and paper-specific facts; pdftotext is supporting evidence only",
        "paper_pdf": rel(pdf),
        "paper_text_extract": rel(text_path),
        "status": status,
    }
    write_csv(req_csv, mechanism_rows, ["requirement_id", "paper_component", "manual_fact", "minimal_design_implication", "a18_stats_need", "implementation_scope_this_round"])
    write_csv(stats_csv, stats_rows, ["stat_key", "paper_target", "semantic", "desired_class"])
    write_json(profile_json, profile)
    write_stage_report(
        report,
        "A17A LATPC Paper Requirements",
        status,
        start_iso,
        start,
        commands,
        [rel(pdf), clean(selected.get("_source_path"))],
        [rel(req_csv), rel(stats_csv), rel(profile_json), rel(text_path)],
        blocker,
        ["Manual facts are intentionally used; this stage does not claim a full paper reproduction.", "A18 remains stats-only and bounded to the selected workload."],
        "## Selected Workload\n\n" + f"- `{clean(selected.get('selected_workload')) or 'nw'}`\n",
    )
    print(f"A17A status: {status}")
    print(f"A17A report: {rel(report)}")
    print(f"A17A requirements CSV: {rel(req_csv)}")
    print(f"A17A target stats CSV: {rel(stats_csv)}")
    return 0 if status != "BLOCKED_NO_PAPER" else 1


if __name__ == "__main__":
    raise SystemExit(main())
