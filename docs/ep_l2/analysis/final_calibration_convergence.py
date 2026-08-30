#!/usr/bin/env python3
"""Build the read-only EP-L2 final-convergence matrix from promoted review packs."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parents[3]
OUT = ROOT / "docs/ep_l2/review_packs/FINAL_CALIBRATION_CONVERGENCE_r1"
CONTRACTS = ROOT / "docs/ep_l2/calibration/contracts"
PACK = ROOT / "docs/ep_l2/review_packs"
CELLS = ("D256_BASE", "D512_BASE", "D256_META_HR", "D256_BANK_HR", "D512_META_HR", "D512_BANK_HR")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def write(path: Path, records: list[dict[str, object]]) -> None:
    keys = list(dict.fromkeys(key for row in records for key in row))
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, keys, lineterminator="\n")
        writer.writeheader(); writer.writerows(records)


def contract(name: str) -> dict[str, object]:
    value = json.loads((CONTRACTS / f"{name}.json").read_text())
    gate = value.get("config_delta_gate", {})
    if value.get("schema") != "EP_L2_CALIBRATION_CONTRACT_V2" or value.get("cell") != name:
        raise ValueError(f"invalid contract {name}")
    if gate.get("status") != "PASS" or not gate.get("evidence_path"):
        raise ValueError(f"unbound config contract {name}")
    return value


def require(rows: list[dict[str, str]], expected: int, label: str) -> None:
    if len(rows) != expected:
        raise ValueError(f"{label}: expected {expected}, found {len(rows)}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    contracts = {name: contract(name) for name in CELLS}
    formal = read(PACK / "TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1/FORMAL_PROVENANCE_AUDIT.csv")
    d512_audit = read(PACK / "D512_CALIBRATION_r1/D512_PROVENANCE_AUDIT_26OF26.csv")
    require(formal, 26, "formal provenance")
    require(d512_audit, 26, "D512 provenance")
    for row in formal:
        if row["runtime_config_composite_sha256"] != contracts["D256_BASE"]["runtime_config_composite_sha256"]:
            raise ValueError("formal runtime-config mismatch")
    for row in d512_audit:
        if (row["runtime_config_composite_sha256"] != contracts["D512_BASE"]["runtime_config_composite_sha256"] or
                row["maturity"] != "PROMOTED_VALID_CALIBRATION" or row["audit_result"] != "PASS"):
            raise ValueError("D512 promotion/config mismatch")

    comparison = read(PACK / "D512_CALIBRATION_r1/D512_CALIBRATION_COMPARISON.csv")
    require(comparison, 26, "D256/D512 comparison")
    matrix: list[dict[str, object]] = []
    native: list[dict[str, object]] = []
    for row in comparison:
        for cell, prefix in (("D256_BASE", "d256"), ("D512_BASE", "d512")):
            matrix.append({"cell": cell, "workload": row["workload"], "variant": row["variant"],
                           "binding": "DIRECT_RUN_AUDIT_PLUS_PROMOTED_REVIEW", "runtime_config_composite_sha256": contracts[cell]["runtime_config_composite_sha256"],
                           "cycles": row[f"{prefix}_cycles"], "descriptor_need": row[f"{prefix}_descriptor_need"],
                           "descriptor_pool_full_block": row[f"{prefix}_descriptor_pool_full_block"], "descriptor_avg": row[f"{prefix}_descriptor_avg"],
                           "descriptor_p95": row[f"{prefix}_descriptor_p95"], "line_mshr_avg": row[f"{prefix}_line_mshr_avg"],
                           "line_mshr_p95": row[f"{prefix}_line_mshr_p95"], "line_mshr_full_block": row[f"{prefix}_line_mshr_full_block"],
                           "per_address_cap_block": row[f"{prefix}_per_address_cap_block"], "wad_full_events": row[f"{prefix}_wad_full_events"],
                           "bank_true_conflict_ops": row[f"{prefix}_bank_true_conflict_ops"], "l2_to_dram_full_block": row[f"{prefix}_l2_to_dram_full_block"],
                           "scheduler_full_cycles": row[f"{prefix}_scheduler_full_cycles"], "lower_admission_byte_rate_norm": row[f"{prefix}_lower_admission_byte_rate_norm"],
                           "native_dram_snapshot_status": row[f"{prefix}_native_dram_snapshot_status"], "native_dram_channels_observed": row[f"{prefix}_native_dram_channels_observed"],
                           "native_dram_data_bus_util_weighted_mean": row[f"{prefix}_native_dram_data_bus_util_weighted_mean"]})
            native.append({"cell": cell, "workload": row["workload"], "variant": row["variant"],
                           "snapshot_status": row[f"{prefix}_native_dram_snapshot_status"], "channels": row[f"{prefix}_native_dram_channels_observed"],
                           "weighted_mean": row[f"{prefix}_native_dram_data_bus_util_weighted_mean"],
                           "p50": row[f"{prefix}_native_dram_data_bus_util_p50"], "p95": row[f"{prefix}_native_dram_data_bus_util_p95"],
                           "max": row[f"{prefix}_native_dram_data_bus_util_max"], "n_cmd_sum": row[f"{prefix}_native_dram_n_cmd_sum"]})

    l1_deltas: list[dict[str, object]] = []
    l1_sources = (("D256", "D256_L1_CAUSALITY_COMPARISON.csv", {"META-HR": "D256_META_HR", "BANK-HR": "D256_BANK_HR"}),
                  ("D512", "D512_L1_CAUSALITY_COMPARISON.csv", {"D512-META-HR": "D512_META_HR", "D512-BANK-HR": "D512_BANK_HR"}))
    for _, filename, mapping in l1_sources:
        rows = read(PACK / "L1_CAUSALITY_CALIBRATION_r1" / filename)
        require(rows, 14, filename)
        for row in rows:
            cell = mapping[row["cell"]]
            matrix.append({"cell": cell, "workload": row["workload"], "variant": "B0-Banked", "binding": "REVIEW_PACK_BOUND_CONTRACT_PLUS_PROMOTION_STATUS",
                           "runtime_config_composite_sha256": contracts[cell]["runtime_config_composite_sha256"], "cycles": row["cell_cycles"],
                           "descriptor_pool_full_block": row["cell_c7d_descriptor_pool_full_block"], "line_mshr_full_block": row["cell_c7d_line_mshr_full_block"],
                           "l2_to_dram_full_block": row["cell_c7d_l2_to_dram_full_block"], "scheduler_full_cycles": row["cell_c7d_dram_scheduler_full_block"],
                           "lower_admission_byte_rate_norm": row["cell_dram_bandwidth_util"], "l1_mshr_entry_fail": row["cell_l1_mshr_entry_fail"],
                           "l1_miss_queue_full": row["cell_l1_miss_queue_full"], "l1_bank_latency_queue_conflict": row["cell_l1_bank_latency_queue_conflict"],
                           "native_dram_snapshot_status": "NOT_RETAINED_IN_COMPACT_L1_REVIEW_TABLE"})
            l1_deltas.append({"workload": row["workload"], "variant": "B0-Banked", "comparison": f"{cell}_VS_PROMOTED_PARENT",
                              "speedup_percent": row["speedup_pct"], "descriptor_block_base": row["base_c7d_descriptor_pool_full_block"],
                              "descriptor_block_cell": row["cell_c7d_descriptor_pool_full_block"], "line_mshr_full_base": row["base_c7d_line_mshr_full_block"],
                              "line_mshr_full_cell": row["cell_c7d_line_mshr_full_block"], "l2d_full_base": row["base_c7d_l2_to_dram_full_block"],
                              "l2d_full_cell": row["cell_c7d_l2_to_dram_full_block"]})

    if len(matrix) != 80:
        raise ValueError(f"matrix expected 80 records, found {len(matrix)}")
    write(OUT / "CALIBRATION_MATRIX_FINAL.csv", matrix)
    write(OUT / "NATIVE_DRAM_SUMMARY_FINAL.csv", native)
    temporal = []
    for source, filename in (("D512_PROMOTED", "D512_CALIBRATION_r1/D512_TEMPORAL.csv"),
                             ("D256_L1_PROMOTED", "L1_CAUSALITY_CALIBRATION_r1/D256_TEMPORAL_SUMMARY.csv"),
                             ("D512_L1_PROMOTED", "L1_CAUSALITY_CALIBRATION_r1/D512_TEMPORAL_SUMMARY.csv")):
        for row in read(PACK / filename):
            temporal.append({"source": source, **row})
    write(OUT / "TEMPORAL_SUMMARY_FINAL.csv", temporal)
    deltas = [{"workload": row["workload"], "variant": row["variant"], "comparison": "D256_BASE_TO_D512_BASE",
               "speedup": row["d256_to_d512_speedup"], "descriptor_block_d256": row["d256_descriptor_pool_full_block"],
               "descriptor_block_d512": row["d512_descriptor_pool_full_block"], "line_mshr_full_d256": row["d256_line_mshr_full_block"],
               "line_mshr_full_d512": row["d512_line_mshr_full_block"], "l2d_full_d256": row["d256_l2_to_dram_full_block"],
               "l2d_full_d512": row["d512_l2_to_dram_full_block"]} for row in comparison]
    write(OUT / "CALIBRATION_DELTAS_FINAL.csv", deltas + l1_deltas)
    manifest = {"schema": "EP_L2_FINAL_CONVERGENCE_V1", "analysis_source": "hrl/ep-l2-cal-analysis-v0", "reviewed_v3_source_sha": "cb83606eb8640382b7c1932d8981b70608d9d130", "convergence_tool": "docs/ep_l2/analysis/final_calibration_convergence.py", "promoted_cells": list(CELLS),
                "record_counts": {"D256_BASE": 26, "D512_BASE": 26, "D256_META_HR": 7, "D256_BANK_HR": 7, "D512_META_HR": 7, "D512_BANK_HR": 7},
                "matrix_records": len(matrix), "native_records": len(native), "temporal_records": len(temporal)}
    (OUT / "ANALYSIS_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
