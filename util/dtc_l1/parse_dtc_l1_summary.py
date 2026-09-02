#!/usr/bin/env python3
"""Extract a compact, provenance-bearing DTC-L1 summary from a simulator log.

This intentionally uses only Python's standard library so review packs can be
re-created on a normal Framework checkout. It is a parser, not a result
classifier: callers must supply the classification and provenance they used.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path


KEY_VALUE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$")
NUMBER = re.compile(r"^-?\d+$")


SUMMARY_KEYS = (
    "gpu_tot_sim_insn",
    "gpu_tot_sim_cycle",
    "L1D_total_cache_accesses",
    "L1D_total_cache_misses",
    "DTC_L1_mode",
    "DTC_L1_pib_admits",
    "DTC_L1_pib_retires",
    "DTC_L1_pib_occupancy",
    "DTC_L1_pib_peak_per_sm",
    "DTC_L1_pib_full_events",
    "DTC_L1_primary_stall_pib_full",
    "DTC_L1_primary_stall_tag_bank",
    "DTC_L1_primary_stall_lower_cap",
    "DTC_L1_nonexclusive_pib_full_cycles",
    "DTC_L1_nonexclusive_tag_bank_conflict_cycles",
    "DTC_L1_nonexclusive_lower_cap_full_cycles",
    "DTC_L1_nonexclusive_mshr_entry_full_cycles",
    "DTC_L1_nonexclusive_mshr_merge_full_cycles",
    "DTC_L1_baseline_mshr_entry_full_events",
    "DTC_L1_baseline_mshr_merge_full_events",
    "DTC_L1_frontend_stall_cycles",
    "DTC_L1_baseline_mshr_entries",
    "DTC_L1_lower_outstanding_cap",
    "DTC_L1_lower_outstanding",
    "DTC_L1_lower_outstanding_peak",
    "DTC_L1_lower_cap_full_events",
    "DTC_L1_lower_requests_acquired",
    "DTC_L1_lower_requests_released",
    "DTC_L1_tag_requests",
    "DTC_L1_tag_conflicts",
    "DTC_L1_io_lower_created",
    "DTC_L1_io_lower_issued",
    "DTC_L1_io_lower_responses",
    "DTC_L1_io_inflight_current",
    "DTC_L1_io_inflight_peak_per_sm",
    "DTC_L1_io_inflight_identity_mismatch",
    "DTC_L1_io_responses_routed_dtc",
    "DTC_L1_io_responses_routed_conventional",
    "DTC_L1_io_pib_occupancy",
    "DTC_L1_io_pib_peak_per_sm",
    "DTC_L1_io_head_not_ready_cycles",
    "DTC_L1_io_hol_ready_younger_cycles",
    "DTC_L1_io_hol_ready_younger_count_sum",
    "DTC_L1_io_hol_ready_younger_peak_per_sm",
    "DTC_L1_io_tag_requests",
    "DTC_L1_io_tag_conflicts",
    "DTC_L1_io_retire_count",
    "DTC_L1_io_completion_dependency_count",
    "DTC_L1_io_completion_dependency_closed",
    "DTC_L1_io_valid_hits",
    "DTC_L1_io_pending_hits",
    "DTC_L1_io_physical_allocations",
    "DTC_L1_io_physical_releases",
    "DTC_L1_io_tag_evictions",
    "DTC_L1_io_duplicate_after_eviction",
    "DTC_L1_io_partial_allocation_events",
    "DTC_L1_io_allocation_width_limited_events",
    "DTC_L1_io_no_free_physical_events",
    "DTC_L1_io_physical_allocated_current",
    "DTC_L1_io_physical_allocated_peak_per_sm",
    "DTC_L1_io_physical_free_current",
    "DTC_L1_io_physical_free_minimum_per_sm",
    "DTC_L1_io_partial_entries_current",
    "DTC_L1_io_partial_entries_peak_per_sm",
    "DTC_L1_io_partial_lines_held_current",
    "DTC_L1_io_partial_lines_held_peak_per_sm",
    "DTC_L1_lower_credit_acquired",
    "DTC_L1_lower_credit_released",
    "DTC_L1_lower_outstanding",
    "DTC_L1_lower_cap_full_events",
    "DTC_L1_conventional_l1d_mshr_entry_full_events",
    "DTC_L1_conventional_l1d_mshr_merge_full_events",
    "DTC_L1_oo_lower_created",
    "DTC_L1_oo_lower_issued",
    "DTC_L1_oo_lower_responses",
    "DTC_L1_oo_inflight_current",
    "DTC_L1_oo_pib_occupancy",
    "DTC_L1_oo_retire_count",
    "DTC_L1_oo_out_of_order_retires",
    "DTC_L1_oo_completion_dependency_count",
    "DTC_L1_oo_completion_dependency_closed",
    "DTC_L1_oo_active_refs",
    "DTC_L1_sector_lower_created",
    "DTC_L1_sector_lower_issued",
    "DTC_L1_sector_lower_responses",
    "DTC_L1_sector_inflight_current",
    "DTC_L1_sector_pib_occupancy",
    "DTC_L1_sector_retire_count",
    "DTC_L1_sector_out_of_order_retires",
    "DTC_L1_sector_completion_dependency_count",
    "DTC_L1_sector_completion_dependency_closed",
    "DTC_L1_sector_valid_hits",
    "DTC_L1_sector_pending_hits",
    "DTC_L1_sector_new_line_misses",
    "DTC_L1_sector_new_requests",
    "DTC_L1_sector_fill_wakeups",
    "DTC_L1_sector_active_refs",
    "DTC_L1_sector_physical_allocated",
)


def parse_value(value):
    return int(value) if NUMBER.fullmatch(value) else value


def extract(log_path):
    values = {}
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = KEY_VALUE.match(line)
        if match:
            values[match.group(1)] = parse_value(match.group(2))
    return values


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--core-sha", required=True)
    parser.add_argument("--framework-sha", required=True)
    parser.add_argument("--config-id", required=True)
    parser.add_argument("--config-file", type=Path)
    parser.add_argument("--workload-id", required=True)
    parser.add_argument("--workload-file", type=Path)
    parser.add_argument("--result-classification", required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    values = extract(args.log)
    metrics = {key: values[key] for key in SUMMARY_KEYS if key in values}
    metrics.update(
        {
            key: value
            for key, value in values.items()
            if key.startswith("DTC_L1_tag_bank_") and key.endswith("_requests")
        }
    )
    metrics.update(
        {
            key: value
            for key, value in values.items()
            if key.startswith("DTC_L1_io_tag_bank_") and
            key.endswith("_requests")
        }
    )
    if args.strict:
        for required in ("gpu_tot_sim_insn", "gpu_tot_sim_cycle"):
            if required not in metrics:
                parser.error("missing required simulator metric: " + required)
        if args.config_file is None or args.workload_file is None:
            parser.error("--strict requires --config-file and --workload-file")
        if metrics.get("DTC_L1_mode") == "PAPER_BASE":
            for required in (
                "DTC_L1_pib_admits",
                "DTC_L1_pib_retires",
                "DTC_L1_lower_outstanding",
                "DTC_L1_lower_requests_acquired",
                "DTC_L1_lower_requests_released",
            ):
                if required not in metrics:
                    parser.error("missing required Paper Base metric: " + required)
        if metrics.get("DTC_L1_mode") == "PAPER_IO":
            for required in (
                "DTC_L1_io_lower_created",
                "DTC_L1_io_lower_issued",
                "DTC_L1_io_lower_responses",
                "DTC_L1_io_inflight_current",
                "DTC_L1_io_pib_occupancy",
                "DTC_L1_io_retire_count",
                "DTC_L1_io_completion_dependency_count",
                "DTC_L1_io_completion_dependency_closed",
                "DTC_L1_lower_credit_acquired",
                "DTC_L1_lower_credit_released",
            ):
                if required not in metrics:
                    parser.error("missing required Paper IO metric: " + required)
        if metrics.get("DTC_L1_mode") == "PAPER_OO":
            for required in (
                "DTC_L1_oo_lower_created",
                "DTC_L1_oo_lower_issued",
                "DTC_L1_oo_lower_responses",
                "DTC_L1_oo_inflight_current",
                "DTC_L1_oo_pib_occupancy",
                "DTC_L1_oo_retire_count",
                "DTC_L1_oo_completion_dependency_count",
                "DTC_L1_oo_completion_dependency_closed",
                "DTC_L1_oo_active_refs",
                "DTC_L1_lower_credit_acquired",
                "DTC_L1_lower_credit_released",
            ):
                if required not in metrics:
                    parser.error("missing required Paper OO metric: " + required)
        if metrics.get("DTC_L1_mode") == "MODERN_OO_SECTOR":
            for required in (
                "DTC_L1_sector_lower_created",
                "DTC_L1_sector_lower_issued",
                "DTC_L1_sector_lower_responses",
                "DTC_L1_sector_inflight_current",
                "DTC_L1_sector_pib_occupancy",
                "DTC_L1_sector_retire_count",
                "DTC_L1_sector_completion_dependency_count",
                "DTC_L1_sector_completion_dependency_closed",
                "DTC_L1_sector_new_requests",
                "DTC_L1_sector_fill_wakeups",
                "DTC_L1_sector_active_refs",
                "DTC_L1_lower_credit_acquired",
                "DTC_L1_lower_credit_released",
            ):
                if required not in metrics:
                    parser.error("missing required OO sector metric: " + required)

    result = {
        "schema": "dtc_l1_summary_v1",
        "provenance": {
            "core_sha": args.core_sha,
            "framework_sha": args.framework_sha,
            "config_id": args.config_id,
            "config_sha256": sha256(args.config_file)
            if args.config_file is not None
            else None,
            "workload_id": args.workload_id,
            "workload_sha256": sha256(args.workload_file)
            if args.workload_file is not None
            else None,
            "source_log": str(args.log),
            "result_classification": args.result_classification,
        },
        "metrics": metrics,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
