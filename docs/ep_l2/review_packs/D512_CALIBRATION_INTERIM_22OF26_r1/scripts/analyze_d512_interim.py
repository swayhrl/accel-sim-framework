#!/usr/bin/env python3
"""Produce a partial D512 review table using the final C7e parser semantics.

This is intentionally a consumer of the checked-in C7e final analyzer rather
than a second metric implementation.  It emits only locally COMPLETE_VALID
D512 rows, while retaining all 26 rows in the run-status table.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

REVIEW_PACKS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REVIEW_PACKS / "TARGET_BASELINE_FINAL_26OF26_C7E_r1" / "scripts"))
from analyze_target_baseline import maximum, rows, run_record, weighted, write_csv  # noqa: E402

ARTIFACTS = ("target_summary.csv", "target_slice.csv", "target_kernel.csv", "target_bank.csv",
             "target_window.csv", "target_l1.csv", "target_dram.csv")
VARIANTS = ("B0-Legacy", "B0-Banked")
WORKLOADS = ("vectorAdd_4M", "scan", "spmv", "convolutionSeparable", "cfd_097k", "dwt2d",
             "sad", "sgemm", "btree", "3mm", "gemm", "FWT_7_21", "FWT_11_19")


def integer(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def d512_dir(root: Path, variant: str, workload: str) -> Path:
    return root / "speculative_rows" / f"{variant}__{workload}" / variant / workload


def config_audit(status: dict, directory: Path) -> dict:
    audit = status.get("audit", {})
    summary = rows(directory / "target_summary.csv")[0]
    return {
        "workload": status.get("workload"), "variant": status.get("variant"),
        "run_status": status.get("status"), "normal_simulator_exit": status.get("normal_simulator_exit"),
        "exit_code": status.get("exit_code"), "cycles": status.get("terminal_gpu_tot_sim_cycle"),
        "instructions": status.get("terminal_gpu_tot_sim_insn"),
        "core_sha": audit.get("core_authoritative_source"),
        "framework_sha": audit.get("framework_authoritative_source"),
        "runtime_config_composite_sha256": audit.get("runtime_config_composite_sha256"),
        "descriptor_pool_size": audit.get("descriptor_pool_size"),
        "frequency_mhz": status.get("frequency_mhz"), "trace": status.get("trace"),
        "terminal_clean": summary.get("invariants_terminal_clean"),
        "payload_consistent": summary.get("invariants_payload_consistent"),
        "parser_success": True, "required_artifacts_present": all((directory / x).is_file() for x in ARTIFACTS),
        "maturity": "SPECULATIVE_PENDING_GATE",
        "promotion_dependencies": "D256_EQ_SCAN_PASS;D512_PREFLIGHT_PASS",
        "audit_result": "PASS" if status.get("status") == "COMPLETE_VALID" and
                        status.get("normal_simulator_exit") and summary.get("invariants_terminal_clean") == "1" and
                        summary.get("invariants_payload_consistent") == "1" and
                        all((directory / x).is_file() for x in ARTIFACTS) else "FAIL",
        "result_path": str(directory),
    }


def temporal(directory: Path, workload: str, variant: str, capacity: str) -> dict:
    window_rows = rows(directory / "target_window.csv")
    def stat(field: str, which: str) -> int:
        values = [integer(row.get(field)) for row in window_rows]
        if not values:
            return 0
        if which == "max":
            return max(values)
        if which == "p95":
            return sorted(values)[(len(values) * 95 + 99) // 100 - 1]
        return min(values)
    return {"workload": workload, "variant": variant, "descriptor_capacity": capacity,
            "window_records": len(window_rows),
            "descriptor_avg_min": stat("descriptor_avg", "min"), "descriptor_avg_p95": stat("descriptor_avg", "p95"),
            "descriptor_avg_max": stat("descriptor_avg", "max"),
            "line_mshr_avg_min": stat("line_mshr_avg", "min"), "line_mshr_avg_p95": stat("line_mshr_avg", "p95"),
            "line_mshr_avg_max": stat("line_mshr_avg", "max"),
            "lowerq_avg_min": stat("lowerq_avg", "min"), "lowerq_avg_p95": stat("lowerq_avg", "p95"),
            "lowerq_avg_max": stat("lowerq_avg", "max")}


def prefixed(record: dict, prefix: str, fields: tuple[str, ...]) -> dict:
    return {f"{prefix}_{field}": record.get(field, "NOT_EMITTED") for field in fields}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--d512-root", type=Path, required=True)
    parser.add_argument("--d256-root", type=Path, required=True)
    parser.add_argument("--d256-equivalence-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(); args.out.mkdir(parents=True, exist_ok=True)
    status_rows, audits, resources, temporals, comparisons = [], [], [], [], []
    complete: dict[tuple[str, str], tuple[dict, Path]] = {}
    d256_records: dict[tuple[str, str], dict] = {}
    for workload in WORKLOADS:
        for variant in VARIANTS:
            directory = d512_dir(args.d512_root, variant, workload)
            status_path = directory / "run_status.json"
            if not status_path.is_file():
                status_rows.append({"workload": workload, "variant": variant, "run_status": "RUNNING",
                                    "maturity": "SPECULATIVE_PENDING_GATE",
                                    "promotion_dependencies": "D256_EQ_SCAN_PASS;D512_PREFLIGHT_PASS",
                                    "result_path": str(directory)})
                continue
            status = json.loads(status_path.read_text())
            audit = config_audit(status, directory)
            status_rows.append({key: audit[key] for key in ("workload", "variant", "run_status", "maturity",
                "promotion_dependencies", "cycles", "instructions", "result_path")})
            audits.append(audit)
            if audit["audit_result"] != "PASS":
                raise SystemExit(f"audit failure {workload}/{variant}")
            record = run_record(directory, status)
            complete[workload, variant] = record, directory
            resources.append({"workload": workload, "variant": variant, "descriptor_capacity": 512} | record)
            temporals.append(temporal(directory, workload, variant, "512"))
            d256_directory = args.d256_root / variant / workload
            d256_status = json.loads((d256_directory / "run_status.json").read_text())
            d256_records[workload, variant] = run_record(d256_directory, d256_status)
            temporals.append(temporal(d256_directory, workload, variant, "256"))
    fields = ("cycles", "descriptor_need", "descriptor_avg", "descriptor_p95", "descriptor_max",
              "descriptor_pool_full_block", "line_mshr_avg", "line_mshr_p95", "line_mshr_max",
              "line_mshr_full_block", "per_address_cap_block", "l1d_misses", "l1d_line_alloc_fail",
              "l1d_miss_queue_full", "wad_avg", "wad_p95", "wad_max", "wad_full_events",
              "resident_payload_avg", "resident_payload_p95", "resident_payload_max", "bank_logical_ops",
              "bank_true_conflict_ops", "bank_wait_cycles", "l2_to_dram_full_block", "scheduler_occ_avg",
              "scheduler_full_cycles", "dram_bandwidth_util", "dram_successful_read_bytes",
              "dram_successful_write_bytes")
    for (workload, variant), (d512, _) in sorted(complete.items()):
        d256 = d256_records[workload, variant]
        comparisons.append({"workload": workload, "variant": variant,
                            "d512_status": "COMPLETE_VALID",
                            "maturity": "SPECULATIVE_PENDING_GATE",
                            "d256_to_d512_speedup": "%.9f" % (d256["cycles"] / d512["cycles"])} |
                           prefixed(d256, "d256", fields) | prefixed(d512, "d512", fields))
    write_csv(args.out / "D512_RUN_STATUS_22OF26.csv", status_rows)
    write_csv(args.out / "D512_PROVENANCE_AUDIT_22OF26.csv", audits)
    write_csv(args.out / "D512_INTERIM_RESOURCE_PRESSURE.csv", resources)
    write_csv(args.out / "D512_INTERIM_TEMPORAL.csv", temporals)
    write_csv(args.out / "D512_INTERIM_COMPARISON.csv", comparisons)
    equivalence = []
    for workload in ("vectorAdd_4M", "spmv", "scan"):
        reference_dir = args.d256_root / "B0-Banked" / workload
        generalized_dir = args.d256_equivalence_root / "B0-Banked" / workload
        reference_status = json.loads((reference_dir / "run_status.json").read_text())
        generalized_status = json.loads((generalized_dir / "run_status.json").read_text())
        reference = run_record(reference_dir, reference_status)
        generalized = run_record(generalized_dir, generalized_status)
        artifact_hashes = {name: hashlib.sha256((generalized_dir / name).read_bytes()).hexdigest()
                           for name in ARTIFACTS}
        identical = all((reference_dir / name).read_bytes() == (generalized_dir / name).read_bytes()
                        for name in ARTIFACTS)
        equivalence.append({
            "workload": workload, "reference_status": reference_status["status"],
            "generalized_status": generalized_status["status"],
            "reference_core_sha": reference_status["audit"]["core_authoritative_source"],
            "reference_framework_sha": reference_status["audit"]["framework_authoritative_source"],
            "reference_runtime_config_sha": reference_status["audit"]["runtime_config_composite_sha256"],
            "generalized_core_sha": generalized_status["audit"]["core_authoritative_source"],
            "generalized_framework_sha": generalized_status["audit"]["framework_authoritative_source"],
            "generalized_runtime_config_sha": generalized_status["audit"]["runtime_config_composite_sha256"],
            "cycles_reference": reference["cycles"], "cycles_generalized": generalized["cycles"],
            "instructions_reference": reference["instructions"], "instructions_generalized": generalized["instructions"],
            "l1_misses_reference": reference["l1d_misses"], "l1_misses_generalized": generalized["l1d_misses"],
            "dram_reads_reference": reference["dram_successful_read_issues"],
            "dram_reads_generalized": generalized["dram_successful_read_issues"],
            "dram_writes_reference": reference["dram_successful_write_issues"],
            "dram_writes_generalized": generalized["dram_successful_write_issues"],
            "l2_descriptor_pool_full_reference": reference["descriptor_pool_full_block"],
            "l2_descriptor_pool_full_generalized": generalized["descriptor_pool_full_block"],
            "terminal_clean_reference": reference["invariants_terminal_clean"],
            "terminal_clean_generalized": generalized["invariants_terminal_clean"],
            "payload_consistent_reference": reference["invariants_payload_consistent"],
            "payload_consistent_generalized": generalized["invariants_payload_consistent"],
            "seven_parsed_artifacts_byte_identical": identical,
        } | {f"{name}_sha256": value for name, value in artifact_hashes.items()})
    write_csv(args.out / "D256_EQUIVALENCE_STATUS.csv", equivalence)
    (args.out / "analysis_manifest.json").write_text(json.dumps({
        "kind": "D512_INTERIM_22_OF_26", "complete_rows": len(complete), "running_rows": 26 - len(complete),
        "metric_semantics": "run_record imported from TARGET_BASELINE_FINAL_26OF26_C7E_r1 analyzer",
        "maturity": "SPECULATIVE_PENDING_GATE"}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
