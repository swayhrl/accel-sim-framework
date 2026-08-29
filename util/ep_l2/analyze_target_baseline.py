#!/usr/bin/env python3
"""Create exact-field, analysis-ready tables for a complete EP-L2 campaign.

This consumer refuses an incomplete campaign and never maps an old coarse
``block_*`` field onto a specific C7e resource. Each labelled resource field
is emitted by its named C7e producer or is explicitly ``NOT_EMITTED``.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from run_target_baseline import ROSTER, VARIANTS

ROOT = Path(__file__).resolve().parents[2]
NA = "NOT_EMITTED"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def integer(row: dict[str, str], key: str) -> int:
    try:
        return int(row.get(key, "0"))
    except (TypeError, ValueError):
        return 0


def emitted(records: list[dict[str, str]], key: str) -> bool:
    return any(row.get(key) not in (None, "", "NA", NA) for row in records)


def total(records: list[dict[str, str]], key: str) -> int | str:
    return sum(integer(row, key) for row in records) if emitted(records, key) else NA


def weighted(records: list[dict[str, str]], key: str,
             weight: str = "samples") -> int | str:
    if not emitted(records, key):
        return NA
    denominator = sum(integer(row, weight) for row in records)
    return (sum(integer(row, key) * integer(row, weight) for row in records) // denominator
            if denominator else 0)


def maximum(records: list[dict[str, str]], key: str) -> int | str:
    return max((integer(row, key) for row in records), default=0) if emitted(records, key) else NA


def dram_metric(records: list[dict[str, str]], key: str,
                weighted_avg: bool = False) -> int | str:
    app = [row for row in records if row.get("scope") == "application"]
    return weighted(app, key, "dram_cycles") if weighted_avg else total(app, key)


def run_record(directory: Path, status: dict) -> dict[str, str | int]:
    slices = rows(directory / "target_slice.csv")
    summary = rows(directory / "target_summary.csv")[0]
    l1 = [row for row in rows(directory / "target_l1.csv") if row.get("scope") == "application"]
    dram = rows(directory / "target_dram.csv")
    app_dram = [row for row in dram if row.get("scope") == "application"]
    windows = [row for row in dram if row.get("scope") == "window"]
    result: dict[str, str | int] = {
        "cycles": int(status["terminal_gpu_tot_sim_cycle"]),
        "instructions": status.get("terminal_gpu_tot_sim_insn") or NA,
        "wall_seconds": status.get("wall_seconds", NA),
        "invariants_terminal_clean": summary.get("invariants_terminal_clean", "0"),
        "invariants_payload_consistent": summary.get("invariants_payload_consistent", "0"),
        "l1d_accesses": total(l1, "accesses"), "l1d_misses": total(l1, "misses"),
        "l1d_line_alloc_fail": total(l1, "line_alloc_fail"),
        "l1d_miss_queue_full": total(l1, "miss_queue_full"),
        "l1d_mshr_entry_fail": total(l1, "mshr_entry_fail"),
        "l1d_mshr_merge_fail": total(l1, "mshr_merge_fail"),
        "l1d_mshr_rw_pending": total(l1, "mshr_rw_pending"),
        "l1d_bank_latency_queue_conflict": total(l1, "bank_latency_queue_conflict"),
        "tag_way_alloc_need": total(slices, "c7e_tag_way_alloc_need"),
        "tag_way_alloc_block": total(slices, "c7e_tag_way_alloc_block"),
        "tag_set_all_reserved_block": total(slices, "c7d_tag_set_all_reserved_block"),
        "line_mshr_need": total(slices, "c7e_line_mshr_need"),
        "line_mshr_avg": weighted(slices, "line_mshr_avg"),
        "line_mshr_p95": maximum(slices, "line_mshr_p95"),
        "line_mshr_max": maximum(slices, "line_mshr_max"),
        "line_mshr_full_block": total(slices, "c7d_line_mshr_full_block"),
        "descriptor_need": total(slices, "c7e_descriptor_need"),
        "descriptor_avg": weighted(slices, "descriptor_avg"),
        "descriptor_p95": maximum(slices, "descriptor_p95"),
        "descriptor_max": maximum(slices, "descriptor_max"),
        "descriptor_pool_full_block": total(slices, "c7d_descriptor_pool_full_block"),
        "per_address_cap_check": total(slices, "c7e_per_address_cap_check"),
        "per_address_cap_block": total(slices, "c7d_per_address_cap_block"),
        "chain_depth_avg": weighted(slices, "c7d_descriptor_chain_depth_avg"),
        "chain_depth_p95": maximum(slices, "c7d_descriptor_chain_depth_p95"),
        "chain_depth_max": maximum(slices, "c7d_descriptor_chain_depth_max"),
        "wad_avg": weighted(slices, "wad_avg"), "wad_p95": maximum(slices, "wad_p95"),
        "wad_max": maximum(slices, "wad_max"),
        "wad_full_events": total(slices, "c7d_wad_full_events"),
        "wad_hazard_events": total(slices, "c7d_wad_hazard_events"),
        "wad_hazard_wait_cycles": total(slices, "c7d_wad_hazard_wait_cycles"),
        "resident_payload_avg": weighted(slices, "resident_payload_avg"),
        "resident_payload_p95": maximum(slices, "resident_payload_p95"),
        "resident_payload_max": maximum(slices, "resident_payload_max"),
        "resident_valid_avg": weighted(slices, "c7d_resident_valid_avg"),
        "resident_dirty_avg": weighted(slices, "c7d_resident_dirty_avg"),
        "resident_pending_sector_avg": weighted(slices, "c7d_resident_pending_sector_avg"),
        "bypass_pending_avg": weighted(slices, "c7d_bypass_pending_avg"),
        "bypass_ready_avg": weighted(slices, "c7d_bypass_ready_avg"),
        "payload_service_port_denial": total(slices, "c7d_payload_service_port_denial"),
        "payload_capacity_allocation_denial": total(slices, "c7d_payload_capacity_allocation_denial"),
        "bank_logical_ops": total(slices, "bank_logical_ops"),
        "bank_attempts": total(slices, "bank_attempts"),
        "bank_grants": total(slices, "bank_grants"),
        "bank_retry_attempts": total(slices, "bank_retry_attempts"),
        "bank_true_conflict_ops": total(slices, "bank_true_conflict_ops"),
        "bank_true_conflict_events": total(slices, "bank_true_conflict_events"),
        "bank_wait_cycles": total(slices, "bank_wait_cycles"),
        "missq_avg": weighted(slices, "missq_avg"), "missq_p95": maximum(slices, "missq_p95"),
        "missq_max": maximum(slices, "missq_max"),
        "missq_full_block": total(slices, "c7d_missq_full_block"),
        "l2_to_dram_full_block": total(slices, "c7d_l2_to_dram_full_block"),
        "dram_issue_attempt": total(slices, "c7e_dram_issue_attempt"),
        "dram_successful_read_issues": dram_metric(dram, "successful_read_issues"),
        "dram_successful_write_issues": dram_metric(dram, "successful_write_issues"),
        "dram_successful_read_bytes": dram_metric(dram, "successful_read_bytes"),
        "dram_successful_write_bytes": dram_metric(dram, "successful_write_bytes"),
        "scheduler_occ_avg": dram_metric(dram, "scheduler_occ_avg", True),
        "scheduler_occ_max": maximum(app_dram, "scheduler_occ_max"),
        "scheduler_full_cycles": dram_metric(dram, "scheduler_full_cycles"),
        "scheduler_full_observed": total(slices, "c7e_dram_scheduler_full_observed"),
        "scheduler_causal_block": total(slices, "c7e_dram_scheduler_causal_block"),
        "returnq_occ_avg": dram_metric(dram, "returnq_occ_avg", True),
        "returnq_occ_max": maximum(app_dram, "returnq_occ_max"),
        "returnq_full_cycles": dram_metric(dram, "returnq_full_cycles"),
        "dram_to_l2_return_path_block": total(slices, "c7e_dram_to_l2_return_path_block"),
        "window_records": len(windows),
    }
    numerator = dram_metric(dram, "bandwidth_util_numerator_bytes")
    denominator = dram_metric(dram, "bandwidth_util_denominator_bytes")
    result["dram_bandwidth_util"] = ("%.9f" % (int(numerator) / int(denominator))
                                      if isinstance(numerator, int) and isinstance(denominator, int) and denominator else NA)
    if isinstance(result["bank_true_conflict_ops"], int) and isinstance(result["bank_logical_ops"], int):
        result["bank_true_conflict_rate"] = (
            "%.9f" % (result["bank_true_conflict_ops"] / result["bank_logical_ops"])
            if result["bank_logical_ops"] else "0.000000000")
    else:
        result["bank_true_conflict_rate"] = NA
    for bank in range(4):
        for suffix in ("logical_ops", "grants", "true_conflict_ops", "wait_cycles"):
            result[f"bank{bank}_{suffix}"] = total(slices, f"c7d_bank{bank}_{suffix}")
    return result


def write_csv(path: Path, data: list[dict]) -> None:
    fields = list(dict.fromkeys(key for row in data for key in row))
    with path.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader(); writer.writerows(data)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records: dict[tuple[str, str], dict] = {}
    for workload, _ in ROSTER:
        for variant, _ in VARIANTS:
            directory = args.out / variant / workload
            try:
                status = json.loads((directory / "run_status.json").read_text())
                if status.get("status") != "COMPLETE_VALID":
                    raise ValueError(status.get("status"))
                records[workload, variant] = run_record(directory, status)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                raise SystemExit(f"incomplete final run {workload}/{variant}: {error}")

    comparison, resource, blocking, bank_pressure, lower = [], [], [], [], []
    for workload, _ in ROSTER:
        legacy, banked = records[workload, "B0-Legacy"], records[workload, "B0-Banked"]
        pair = {"workload": workload, "legacy_cycles": legacy["cycles"], "banked_cycles": banked["cycles"],
                "banked_speedup": "%.9f" % (legacy["cycles"] / banked["cycles"])}
        for prefix, record in (("legacy", legacy), ("banked", banked)):
            for key, value in record.items():
                pair[prefix + "_" + key] = value
        comparison.append(pair)
        for variant, record in (("B0-Legacy", legacy), ("B0-Banked", banked)):
            base = {"workload": workload, "variant": variant}
            resource.append(base | {key: record[key] for key in (
                "tag_way_alloc_need", "tag_way_alloc_block", "tag_set_all_reserved_block", "line_mshr_need",
                "line_mshr_avg", "line_mshr_p95", "line_mshr_max", "descriptor_need", "descriptor_avg",
                "descriptor_p95", "descriptor_max", "chain_depth_avg", "chain_depth_p95", "chain_depth_max",
                "wad_avg", "wad_p95", "wad_max", "resident_payload_avg", "resident_payload_p95",
                "resident_payload_max", "resident_pending_sector_avg", "bypass_pending_avg", "bypass_ready_avg")})
            for label, eligible, block in (
                ("TagWay", "tag_way_alloc_need", "tag_way_alloc_block"),
                ("LineMSHR", "line_mshr_need", "line_mshr_full_block"),
                ("DescriptorPool", "descriptor_need", "descriptor_pool_full_block"),
                ("PerAddressCap", "per_address_cap_check", "per_address_cap_block"),
                ("WAD", "wad_avg", "wad_full_events"),
                ("PayloadCapacity", "resident_payload_avg", "payload_capacity_allocation_denial"),
                ("PayloadServicePort", "resident_payload_avg", "payload_service_port_denial"),
                ("Bank", "bank_logical_ops", "bank_true_conflict_ops"),
                ("L1MissQ", "l1d_accesses", "l1d_miss_queue_full"),
                ("LowerL2ToDRAM", "dram_issue_attempt", "l2_to_dram_full_block"),
                ("SchedulerCausal", "dram_issue_attempt", "scheduler_causal_block"),
                ("DRAMToL2ReturnPath", "dram_issue_attempt", "dram_to_l2_return_path_block")):
                value = record[block]
                ratio = ("%.9f" % (value / record[eligible])
                         if isinstance(value, int) and isinstance(record[eligible], int) and record[eligible] else NA)
                blocking.append(base | {"blocker": label, "eligible": record[eligible], "blocked_events": value,
                                         "blocking_ratio": ratio,
                                         "definition": "exact C7e producer field; events are not exclusive blocked cycles"})
            bank_pressure.append(base | {key: record[key] for key in (
                "bank_logical_ops", "bank_attempts", "bank_grants", "bank_retry_attempts", "bank_true_conflict_ops",
                "bank_true_conflict_events", "bank_true_conflict_rate", "bank_wait_cycles", "bank0_logical_ops",
                "bank1_logical_ops", "bank2_logical_ops", "bank3_logical_ops", "bank0_grants", "bank1_grants",
                "bank2_grants", "bank3_grants", "bank0_true_conflict_ops", "bank1_true_conflict_ops",
                "bank2_true_conflict_ops", "bank3_true_conflict_ops", "bank0_wait_cycles", "bank1_wait_cycles",
                "bank2_wait_cycles", "bank3_wait_cycles")})
            lower.append(base | {key: record[key] for key in (
                "missq_avg", "missq_p95", "missq_max", "missq_full_block", "l2_to_dram_full_block",
                "dram_issue_attempt", "dram_successful_read_issues", "dram_successful_write_issues",
                "dram_successful_read_bytes", "dram_successful_write_bytes", "scheduler_occ_avg", "scheduler_occ_max",
                "scheduler_full_cycles", "scheduler_full_observed", "scheduler_causal_block", "returnq_occ_avg",
                "returnq_occ_max", "returnq_full_cycles", "dram_to_l2_return_path_block", "dram_bandwidth_util",
                "window_records")})

    write_csv(args.out / "target_baseline_comparison.csv", comparison)
    write_csv(args.out / "target_resource_pressure.csv", resource)
    write_csv(args.out / "target_blocking_matrix.csv", blocking)
    write_csv(args.out / "target_bank_pressure.csv", bank_pressure)
    write_csv(args.out / "target_lower_path.csv", lower)
    manifest = {"kind": "final_target_baseline_analysis", "runs": len(records),
                "paired_workloads": len(comparison), "frequency_mhz": 850,
                "field_contract": "C7e exact fields only; legacy coarse block fields are not reinterpreted"}
    (args.out / "target_baseline_analysis_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(args.out / "target_baseline_comparison.csv")


if __name__ == "__main__":
    main()
