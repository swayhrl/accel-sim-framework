#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from a24_latpc_lib import REPORT_DIR, clean, div, ensure_dirs, num, parse_stats, rel, ts, write_csv


FIELDS = [
    "run_id", "workload", "variant", "stat_source_path", "warp_mem_inst_observed",
    "translation_request_total", "unique_vpn_total", "multi_translation_fraction",
    "avg_unique_vpn_per_warp", "avg_unique_stride_count", "same_l4_fraction",
    "l1_miss_rate", "l2_miss_rate", "l1_mshr_fail_rate",
    "ptw_request_per_translation", "ptw_shadow_stall_avg_per_ptw_request",
    "page_div_bin_1_fraction", "page_div_bin_2_3_fraction", "page_div_bin_4_7_fraction",
    "page_div_bin_8_15_fraction", "page_div_bin_16_31_fraction", "page_div_bin_32_fraction",
    "stride_zero_fraction", "stride_pos_1_fraction", "stride_neg_1_fraction",
    "stride_pos_2_7_fraction", "stride_neg_2_7_fraction", "stride_pos_8_31_fraction",
    "stride_neg_8_31_fraction", "stride_pos_32_511_fraction", "stride_neg_32_511_fraction",
    "stride_out_of_9bit_fraction", "hook_address_mode", "hook_sm_id_mode", "hook_cycle_mode",
    "limitation",
]


def derive(path: Path, run_id: str, workload: str, variant: str) -> dict[str, str]:
    s = parse_stats(path)
    warp = num(s, "latpc_detector_warp_sample_total", num(s, "latpc_vm_warp_mem_inst_observed"))
    translations = num(s, "latpc_vm_translation_request_total")
    stride_samples = num(s, "latpc_detector_stride_adjacent_sample_total", num(s, "latpc_vm_unique_stride_sample_total"))
    l1_access = num(s, "latpc_tlb_l1_access_total")
    l2_access = num(s, "latpc_tlb_l2_access_total")
    mshr_attempt = num(s, "latpc_tlb_l1_mshr_alloc_attempt")
    ptw_req = num(s, "latpc_ptw_request_total")
    l4_total = num(s, "latpc_detector_l4_translation_total", num(s, "latpc_vm_l4pt_translation_total"))
    return {
        "run_id": run_id,
        "workload": workload,
        "variant": variant,
        "stat_source_path": rel(path),
        "warp_mem_inst_observed": str(warp),
        "translation_request_total": str(translations),
        "unique_vpn_total": s.get("latpc_vm_unique_vpn_total", ""),
        "multi_translation_fraction": div(num(s, "latpc_detector_multivpn_warp_total"), warp),
        "avg_unique_vpn_per_warp": div(num(s, "latpc_detector_unique_vpn_per_warp_sum", translations), warp),
        "avg_unique_stride_count": div(num(s, "latpc_detector_unique_stride_per_warp_sum", num(s, "latpc_vm_unique_stride_sum")), warp if "latpc_detector_unique_stride_per_warp_sum" in s else stride_samples),
        "same_l4_fraction": div(num(s, "latpc_detector_same_l4_translation_total", num(s, "latpc_vm_same_l4pt_translation_total")), l4_total),
        "l1_miss_rate": div(num(s, "latpc_tlb_l1_miss_total"), l1_access),
        "l2_miss_rate": div(num(s, "latpc_tlb_l2_miss_total"), l2_access),
        "l1_mshr_fail_rate": div(num(s, "latpc_tlb_l1_mshr_reservation_fail"), mshr_attempt),
        "ptw_request_per_translation": div(ptw_req, translations),
        "ptw_shadow_stall_avg_per_ptw_request": div(num(s, "latpc_ptw_queue_shadow_stall_cycle_total"), ptw_req),
        "page_div_bin_1_fraction": div(num(s, "latpc_vm_page_div_bin_1"), warp),
        "page_div_bin_2_3_fraction": div(num(s, "latpc_vm_page_div_bin_2_3"), warp),
        "page_div_bin_4_7_fraction": div(num(s, "latpc_vm_page_div_bin_4_7"), warp),
        "page_div_bin_8_15_fraction": div(num(s, "latpc_vm_page_div_bin_8_15"), warp),
        "page_div_bin_16_31_fraction": div(num(s, "latpc_vm_page_div_bin_16_31"), warp),
        "page_div_bin_32_fraction": div(num(s, "latpc_vm_page_div_bin_32"), warp),
        "stride_zero_fraction": div(num(s, "latpc_detector_stride_zero_total"), stride_samples),
        "stride_pos_1_fraction": div(num(s, "latpc_detector_stride_pos_1_total"), stride_samples),
        "stride_neg_1_fraction": div(num(s, "latpc_detector_stride_neg_1_total"), stride_samples),
        "stride_pos_2_7_fraction": div(num(s, "latpc_detector_stride_pos_2_7_total"), stride_samples),
        "stride_neg_2_7_fraction": div(num(s, "latpc_detector_stride_neg_2_7_total"), stride_samples),
        "stride_pos_8_31_fraction": div(num(s, "latpc_detector_stride_pos_8_31_total"), stride_samples),
        "stride_neg_8_31_fraction": div(num(s, "latpc_detector_stride_neg_8_31_total"), stride_samples),
        "stride_pos_32_511_fraction": div(num(s, "latpc_detector_stride_pos_32_511_total"), stride_samples),
        "stride_neg_32_511_fraction": div(num(s, "latpc_detector_stride_neg_32_511_total"), stride_samples),
        "stride_out_of_9bit_fraction": div(num(s, "latpc_detector_stride_out_of_9bit_total"), stride_samples),
        "hook_address_mode": s.get("latpc_hook_address_mode", "1"),
        "hook_sm_id_mode": s.get("latpc_hook_sm_id_mode", "0"),
        "hook_cycle_mode": s.get("latpc_hook_cycle_mode", "0"),
        "limitation": "shadow effective-address substrate; not LATPC mechanism",
    }


def main() -> int:
    ensure_dirs()
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", action="append", required=True)
    parser.add_argument("--run-id", default="A24")
    parser.add_argument("--workload", default="nw")
    parser.add_argument("--variant", default="shadow")
    parser.add_argument("--out")
    args = parser.parse_args()
    out = Path(args.out) if args.out else REPORT_DIR / f"A24B_latpc_detector_ready_derived_stats_{ts()}.csv"
    rows = [derive(Path(p), args.run_id, args.workload, args.variant) for p in args.log]
    write_csv(out, rows, FIELDS)
    print(f"derived_stats_csv: {rel(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
