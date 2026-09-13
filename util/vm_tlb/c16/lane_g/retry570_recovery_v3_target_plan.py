#!/usr/bin/env python3
"""Freeze conservative per-phase Recovery-V3 NVBit candidates from a G1 catalog.

The catalog's Nsight kernel name is a second-pass structural key, not an NVBit
static function identity.  This tool deliberately leaves static ranges pending
until an NVBit-native map has independently observed the live function.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


FIELDS = (
    "target_plan_id", "plan_kind", "deployment_id", "scenario_id", "phase",
    "source_run_id", "source_catalog_sha256", "kernel_name", "grid", "block",
    "dtype_key", "launch_count", "aggregate_duration_ns", "selection_reason",
    "second_pass_validation_key", "nvbit_exact_function_identity",
    "nvbit_static_instruction_range", "target_status",
)


def read_catalog(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle, delimiter="\t"))
    except OSError as exc:
        raise ContractError(f"cannot read catalog: {exc}") from exc
    required = {"run_id", "deployment_id", "scenario_id", "phase", "kernel_name", "grid", "block", "dtype_key", "duration_ns"}
    if not rows or not required.issubset(rows[0]):
        raise ContractError("catalog is empty or lacks the G1 structural fields")
    return rows


def choose(rows: list[dict[str, str]], phase: str) -> dict[str, Any]:
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = defaultdict(lambda: {"duration": 0, "count": 0, "rows": []})
    for row in rows:
        if row["phase"] != phase:
            continue
        key = (row["kernel_name"], row["grid"], row["block"], row["dtype_key"])
        grouped[key]["duration"] += int(row["duration_ns"])
        grouped[key]["count"] += 1
        grouped[key]["rows"].append(row)
    if not grouped:
        raise ContractError(f"catalog has no {phase} launches")
    key, value = min(grouped.items(), key=lambda item: (-item[1]["duration"], item[0]))
    source = min(value["rows"], key=lambda row: int(row["launch_ordinal"]))
    return {"key": key, "duration": value["duration"], "count": value["count"], "source": source}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--plan-id", required=True)
    parser.add_argument("--output-tsv", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    if args.output_tsv.exists() or args.receipt.exists():
        raise ContractError("recovery target-plan outputs are immutable and must not be overwritten")
    rows = read_catalog(args.catalog)
    catalog_sha = sha256_file(args.catalog)
    output: list[dict[str, str]] = []
    for phase in ("PREFILL", "DECODE"):
        candidate = choose(rows, phase)
        kernel, grid, block, dtype = candidate["key"]
        source = candidate["source"]
        structural = {
            "phase": phase, "kernel_name": kernel, "grid": grid, "block": block,
            "dtype_key": dtype, "source_run_id": source["run_id"],
            "source_launch_ordinal": source["launch_ordinal"],
            "source_context": source["context"], "source_stream": source["stream"],
            "source_correlation_id": source["correlation_id"],
        }
        output.append({
            "target_plan_id": args.plan_id, "plan_kind": "RECOVERY_V3_TARGET_PLAN",
            "deployment_id": source["deployment_id"], "scenario_id": source["scenario_id"], "phase": phase,
            "source_run_id": source["run_id"], "source_catalog_sha256": catalog_sha,
            "kernel_name": kernel, "grid": grid, "block": block, "dtype_key": dtype,
            "launch_count": str(candidate["count"]), "aggregate_duration_ns": str(candidate["duration"]),
            "selection_reason": "MAX_AGGREGATE_PHASE_GPU_DURATION_PRE_OUTCOME",
            "second_pass_validation_key": json.dumps(structural, sort_keys=True, separators=(",", ":")),
            "nvbit_exact_function_identity": "PENDING_R5_NVBIT_NATIVE_MAP",
            "nvbit_static_instruction_range": "PENDING_R5_NVBIT_NATIVE_MAP",
            "target_status": "FROZEN_PENDING_EXACT_NVBIT_FUNCTION_REQUALIFICATION",
        })
    args.output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_tsv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(output)
    atomic_json(args.receipt, {
        "schema_version": "C16_G_RECOVERY_V3_TARGET_PLAN_V1",
        "status": "RECOVERY_V3_TARGET_PLAN_FROZEN_PENDING_R5",
        "scientific_eligible": False,
        "plan_kind": "RECOVERY_V3_TARGET_PLAN",
        "plan_id": args.plan_id,
        "catalog": {"path": str(args.catalog), "sha256": catalog_sha},
        "output_tsv": {"path": str(args.output_tsv), "sha256": sha256_file(args.output_tsv)},
        "phase_targets": output,
        "prohibitions": ["no_kernel_name_only_capture", "no_cross_model_static_range", "no_static_range_before_nvbit_native_map"],
    })
    print(f"PASS Recovery-V3 phase target plan: {args.output_tsv}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 target plan: {exc}")
