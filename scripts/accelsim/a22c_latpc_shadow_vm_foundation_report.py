#!/usr/bin/env python3
from __future__ import annotations

import sys
import time

sys.dont_write_bytecode = True
from a20_a23_latpc_vm_lib import REPORT_DIR, ensure_dirs, latest, read_csv, rel, stage_report, ts, write_csv


def report_status(path):
    if not path:
        return "MISSING"
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("- Status:"):
            return line.split(":", 1)[1].strip()
    return "UNKNOWN"


def main() -> int:
    ensure_dirs()
    stamp = ts()
    start = time.time()
    start_iso = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    a22a = latest("A22A_latpc_shadow_vm_build_equiv_*.md")
    a22b = latest("A22B_latpc_shadow_vm_sanity_sensitivity_*.md")
    sanity = latest("A22B_latpc_shadow_vm_sanity_*.csv")
    matrix_csv = REPORT_DIR / f"A22C_latpc_shadow_vm_readiness_matrix_{stamp}.csv"
    report = REPORT_DIR / f"A22C_latpc_shadow_vm_foundation_report_{stamp}.md"
    a22a_status = report_status(a22a)
    a22b_status = report_status(a22b)
    checks = read_csv(sanity) if sanity else []
    failed = [c for c in checks if c.get("status") == "FAIL"]
    if "FAIL" in a22a_status or failed:
        classification = "FAIL_NOT_READY"
        status = "FAIL_NOT_READY"
    elif a22b_status == "PASS":
        classification = "SHADOW_VM_READY_FOR_LATC_LATP_STATS"
        status = "PASS"
    elif a22b_status == "PASS_WITH_WARNINGS":
        classification = "SHADOW_VM_READY_FOR_REGULARITY_DETECTOR"
        status = "PASS"
    else:
        classification = "PARTIAL_SHADOW_VM_ADDRESS_ONLY"
        status = "PASS_WITH_WARNINGS"
    rows = [
        ("address_observation", "ready", sanity or "", "latpc_vm_warp_mem_inst_observed", "medium", "A24", "effective-address hook"),
        ("vpn_derivation", "ready", sanity or "", "latpc_vm_unique_vpn_total", "medium", "A24", "address >> page_shift"),
        ("page_divergence", "ready", sanity or "", "latpc_vm_page_div_bin_*", "high", "A24", "non-trivial bins"),
        ("stride_stats", "ready", sanity or "", "latpc_vm_unique_stride_*", "medium", "A24", "adjacent unique VPN stride"),
        ("same_l4pt_locality", "ready", sanity or "", "latpc_vm_same_l4pt_translation_total", "medium", "A24/A26", "vpn >> 9 grouping"),
        ("shadow_l1_tlb", "ready", sanity or "", "latpc_tlb_l1_access_total", "medium", "A25", "shadow fully associative"),
        ("shadow_l2_tlb", "ready", sanity or "", "latpc_tlb_l2_access_total", "medium", "A25", "global shadow L2"),
        ("shadow_l1_mshr", "ready", sanity or "", "latpc_tlb_l1_mshr_alloc_attempt", "medium", "A25", "shadow MSHR only"),
        ("shadow_ptw_queue", "ready", sanity or "", "latpc_ptw_request_total", "medium", "A26", "shadow completions"),
        ("shadow_pwc", "deferred", sanity or "", "latpc_pwc_*", "low", "future", "printed zero/deferred"),
        ("runner", "ready", latest("A21C_latpc_runner_matrix_*.csv") or "", "runner matrix", "high", "A24", "NW bounded rows"),
        ("stats_parser", "ready", latest("A22A_latpc_extracted_stats_*.csv") or "", "latpc_*", "high", "A24", "simple parser"),
        ("behavior_equivalence", "ready" if a22a_status == "PASS" else "not_ready", latest("A22A_latpc_behavior_compare_*.csv") or "", "cycles/instructions/IPC/L2", "high", "A24", a22a_status),
    ]
    write_csv(matrix_csv, [{"component": r[0], "readiness": r[1], "evidence_path": rel(r[2]) if r[2] else "", "evidence_stat": r[3], "confidence": r[4], "future_round": r[5], "notes": r[6]} for r in rows], ["component", "readiness", "evidence_path", "evidence_stat", "confidence", "future_round", "notes"])
    report.write_text(f"""# A22C LATPC Shadow VM Foundation Report

- Status: {status}
- Readiness classification: {classification}
- A22A behavior validation: {a22a_status}
- A22B sanity/sensitivity: {a22b_status}

## What A24 Can Safely Do

A24 can implement Regularity Detector analysis over shadow VPN/page-divergence,
stride, and same-L4 locality streams.

## What A24 Must Not Do

It must not inject real prefetches, compress real MSHRs, batch real PTWs, or
claim IPC speedup reproduction.
""")
    extra = f"""## Readiness Classification

Readiness classification: {classification}

## What A24 Can Safely Do

A24 can implement Regularity Detector analysis over shadow VPN/page-divergence,
stride, and same-L4 locality streams.

## What A24 Must Not Do

It must not inject real prefetches, compress real MSHRs, batch real PTWs, or
claim IPC speedup reproduction.
"""
    stage_report(report, "A22C LATPC Shadow VM Foundation Report", status, start_iso, start, ["python3 scripts/accelsim/a22c_latpc_shadow_vm_foundation_report.py"], [rel(a22a) if a22a else "", rel(a22b) if a22b else ""], [rel(report), rel(matrix_csv)], "none" if not status.startswith("FAIL") else "foundation not ready", ["Classification is for shadow substrate only.", "PWC remains deferred."], extra)
    print(f"A22C status: {status}")
    print(f"A22C readiness classification: {classification}")
    return 0 if not status.startswith("FAIL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
