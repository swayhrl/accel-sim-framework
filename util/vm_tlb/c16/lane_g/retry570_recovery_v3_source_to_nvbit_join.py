#!/usr/bin/env python3
"""Close an R4 source-catalog to R5 direct-NVBit identity join without ordinal/time joins.

Nsight and NVBit runs are intentionally distinct.  This utility only accepts a
phase-local, exact function identity after normalising the two known ABI text
renderings (NVBit's C++ booleans versus Nsight's ``(bool)0/1`` decorations),
and then requires the frozen phase geometry and structural occurrence evidence.
It expressly never compares an Nsight launch ordinal or timestamp to an NVBit
static instruction ordinal.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_R4_SOURCE_TO_R5_NVBIT_IDENTITY_JOIN_V1"
RENDERING_RULE = "REMOVE_(int)_TOKENS;_(bool)0_TO_false;_(bool)1_TO_true;_REMOVE_WHITESPACE"
FORBIDDEN = ["NSYS_SOURCE_LAUNCH_ORDINAL_EQUALS_NVBIT_STATIC_INDEX", "CROSS_RUN_ABSOLUTE_TIMESTAMP_JOIN", "KERNEL_NAME_ONLY_MATCH"]


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def canonical_function(value: str) -> str:
    """Canonicalise only the documented profiler-vs-NVBit ABI spelling delta."""
    return re.sub(r"\s+", "", re.sub(r"\(bool\)1", "true", re.sub(r"\(bool\)0", "false", re.sub(r"\(int\)", "", value))))


def binding_for_phase(binding: dict[str, Any], phase: str) -> dict[str, Any]:
    rows = [row for row in binding.get("bindings", []) if row.get("phase") == phase]
    if len(rows) != 1:
        raise ContractError(f"direct function binding must contain one {phase} row")
    row = rows[0]
    required = ("deployment_id", "scenario_id", "direct_function_full_name", "direct_function_mangled_name", "grid", "block")
    if any(not isinstance(row.get(key), str) or not row[key] for key in required):
        raise ContractError("direct function binding misses exact identity or geometry")
    return row


def target_for_phase(target: dict[str, Any], direct: dict[str, Any], phase: str) -> dict[str, Any]:
    status = target.get("status")
    if status == "PHASE_DIRECT_MEMORY_TARGET_FROZEN":
        if target.get("phase") != phase:
            raise ContractError("target plan phase differs from requested phase")
    elif status == "PREDICATED_OFF_TARGET_REPLACEMENT_SELECTED":
        # V2 predates the explicit --phase field.  Its exact function identity
        # below is therefore the authority; callers must still supply phase.
        if target.get("phase") not in (None, phase):
            raise ContractError("legacy V2 target phase differs from requested phase")
    else:
        raise ContractError("target plan is not a frozen requested-phase plan")
    function = target.get("function")
    if not isinstance(function, dict) or function.get("mangled_name") != direct["direct_function_mangled_name"]:
        raise ContractError("target plan and direct function binding disagree")
    target_instruction = target.get("target_instruction")
    range_contract = target.get("range_contract")
    if not isinstance(target_instruction, dict) or not isinstance(range_contract, dict):
        raise ContractError("target plan lacks static instruction/range")
    index = target_instruction.get("nvbit_static_index")
    if not isinstance(index, int) or range_contract != {"instr_begin": index, "instr_end_exclusive": index + 1}:
        raise ContractError("target range is not an exact one-instruction frozen range")
    return target_instruction


def matching_source_rows(catalog: Path, direct: dict[str, Any], phase: str) -> list[dict[str, str]]:
    with catalog.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        needed = {"deployment_id", "scenario_id", "phase", "kernel_name", "grid", "block", "launch_ordinal", "correlation_id"}
        if not needed.issubset(set(reader.fieldnames or ())):
            raise ContractError("G1 catalog lacks source identity columns")
        rows = list(reader)
    expected = canonical_function(direct["direct_function_full_name"])
    result = [row for row in rows if row["deployment_id"] == direct["deployment_id"]
              and row["scenario_id"] == direct["scenario_id"] and row["phase"] == phase
              and row["grid"] == direct["grid"] and row["block"] == direct["block"]
              and canonical_function(row["kernel_name"]) == expected]
    if not result:
        raise ContractError("no source-catalog row has exact canonical function plus phase/geometry")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--target-plan", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--phase", choices=("PREFILL", "DECODE"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refuses to overwrite identity join receipt")
    direct = binding_for_phase(load_json(args.binding), args.phase)
    target = target_for_phase(load_json(args.target_plan), direct, args.phase)
    rows = matching_source_rows(args.catalog, direct, args.phase)
    occurrences = Counter(row["correlation_id"] for row in rows)
    value = {
        "schema_version": SCHEMA,
        "status": "R4_SOURCE_TO_R5_NVBIT_IDENTITY_JOIN_CLOSED",
        "scientific_eligible_for_timing": False,
        "phase": args.phase,
        "join_contract": {
            "keys": ["phase", "canonical_full_function_identity", "grid", "block", "source_occurrence_and_correlation_evidence"],
            "canonical_function_rendering_rule": RENDERING_RULE,
            "forbidden": FORBIDDEN,
        },
        "direct_nvbit_function": {
            "full_name": direct["direct_function_full_name"],
            "canonical_full_name": canonical_function(direct["direct_function_full_name"]),
            "mangled_name": direct["direct_function_mangled_name"],
            "deployment_id": direct["deployment_id"], "scenario_id": direct["scenario_id"],
            "grid": direct["grid"], "block": direct["block"],
        },
        "frozen_target": {"target_plan_id": load_json(args.target_plan).get("target_plan_id"),
                            "nvbit_static_index": target["nvbit_static_index"], "opcode": target.get("opcode"),
                            "range": [target["nvbit_static_index"], target["nvbit_static_index"] + 1]},
        "source_catalog_evidence": {
            "path": str(args.catalog), "sha256": sha256_file(args.catalog), "matching_row_count": len(rows),
            "unique_correlation_count": len(occurrences), "occurrence_count_by_correlation": dict(sorted(occurrences.items())),
            "source_function_full_name_examples": sorted({row["kernel_name"] for row in rows}),
            "geometry": {"grid": direct["grid"], "block": direct["block"]},
            "launch_ordinals_retained_as_source_evidence_only": [row["launch_ordinal"] for row in rows],
        },
        "inputs": {"binding": {"path": str(args.binding), "sha256": sha256_file(args.binding)},
                   "target_plan": {"path": str(args.target_plan), "sha256": sha256_file(args.target_plan)}},
    }
    atomic_json(args.output, value)
    print(f"PASS R4_SOURCE_TO_R5_NVBIT_IDENTITY_JOIN_CLOSED phase={args.phase} source_rows={len(rows)}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL source-to-NVBit identity join: {exc}")
