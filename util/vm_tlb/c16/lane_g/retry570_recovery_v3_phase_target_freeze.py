#!/usr/bin/env python3
"""Freeze the first direct NVBit memory target for one explicit phase.

This is a map-only target plan, never a kernel-name heuristic and never an
ordinal join to an nsys catalog.  The selected instruction is the earliest
unpredicated direct GLOBAL MREF in the already phase-bound exact function.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_PHASE_DIRECT_MEMORY_TARGET_V1"
FIELDS = ("nvbit_static_index", "vector_ordinal", "instruction_offset", "opcode", "memory_space",
          "is_load", "is_store", "has_mref", "sass", "function_full_name", "function_mangled_name",
          "function_address", "libtorch_cuda_sha256")


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path} is not an object")
    return value


def phase_function(binding: dict[str, Any], phase: str) -> dict[str, Any]:
    if binding.get("status") != "DIRECT_FUNCTION_BINDING_READY_FOR_STATIC_MAP":
        raise ContractError("direct phase binding is not closed for static-map work")
    rows = [row for row in binding.get("bindings", []) if row.get("phase") == phase]
    if len(rows) != 1:
        raise ContractError("direct phase binding must contain exactly one requested phase function")
    row = rows[0]
    required = ("direct_function_mangled_name", "direct_function_full_name", "deployment_id", "scenario_id", "grid", "block")
    if any(not isinstance(row.get(field), str) or not row[field] for field in required):
        raise ContractError("direct phase binding lacks exact identity/geometry")
    return row


def select(map_path: Path, *, mangled: str, code_sha: str) -> tuple[dict[str, Any], int]:
    with map_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ContractError("NVBit static map schema differs")
        rows = list(reader)
    if not rows:
        raise ContractError("NVBit static map is empty")
    seen: set[int] = set(); candidates: list[dict[str, str]] = []
    for row in rows:
        try:
            index = int(row["nvbit_static_index"])
        except ValueError as exc:
            raise ContractError("NVBit static map has an unparsable index") from exc
        if index in seen:
            raise ContractError("NVBit static map repeats a static index")
        seen.add(index)
        if row["function_mangled_name"] != mangled or row["libtorch_cuda_sha256"] != code_sha:
            raise ContractError("NVBit static map does not bind the exact phase function/code object")
        if (row["opcode"].startswith(("LDG", "STG", "ATOM")) and row["memory_space"] == "GLOBAL"
                and row["has_mref"] == "1" and not row["sass"].lstrip().startswith("@")):
            candidates.append(row)
    if not candidates:
        raise ContractError("no unpredicated direct GLOBAL MREF in exact phase map")
    row = min(candidates, key=lambda candidate: int(candidate["nvbit_static_index"]))
    return ({"nvbit_static_index": int(row["nvbit_static_index"]), "vector_ordinal": int(row["vector_ordinal"]),
             "instruction_offset": int(row["instruction_offset"]), "opcode": row["opcode"],
             "memory_space": row["memory_space"], "is_load": row["is_load"] == "1",
             "is_store": row["is_store"] == "1", "has_mref": row["has_mref"] == "1", "sass": row["sass"]}, len(rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--direct-function-binding", type=Path, required=True)
    parser.add_argument("--phase", choices=("PREFILL", "DECODE"), required=True)
    parser.add_argument("--code-object-sha256", required=True)
    parser.add_argument("--target-plan-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("refuses to overwrite a frozen phase target")
    direct = phase_function(load(args.direct_function_binding), args.phase)
    target, count = select(args.map, mangled=direct["direct_function_mangled_name"], code_sha=args.code_object_sha256)
    value = {
        "schema_version": SCHEMA, "status": "PHASE_DIRECT_MEMORY_TARGET_FROZEN", "scientific_eligible": False,
        "target_plan_id": args.target_plan_id, "phase": args.phase,
        "selection_basis": "EARLIEST_UNPREDICATED_DIRECT_GLOBAL_MREF_IN_EXACT_PHASE_FUNCTION_NVBIT_MAP",
        "function": {"mangled_name": direct["direct_function_mangled_name"], "full_name": direct["direct_function_full_name"],
                     "libtorch_cuda_sha256": args.code_object_sha256, "static_instruction_count": count},
        "phase_identity": {field: direct[field] for field in ("deployment_id", "scenario_id", "grid", "block")},
        "target_instruction": target,
        "range_contract": {"instr_begin": target["nvbit_static_index"], "instr_end_exclusive": target["nvbit_static_index"] + 1},
        "map": {"path": str(args.map), "sha256": sha256_file(args.map)},
        "direct_function_binding": {"path": str(args.direct_function_binding), "sha256": sha256_file(args.direct_function_binding)},
        "forbidden": ["KERNEL_NAME_ONLY_SUBSTITUTION", "NSYS_ORDINAL_EQUALS_NVBIT_ORDINAL", "WIDEN_TARGET_RANGE", "CROSS_PHASE_TARGET_REUSE"],
    }
    atomic_json(args.output, value)
    print(f"PASS PHASE_DIRECT_MEMORY_TARGET_FROZEN phase={args.phase} index={target['nvbit_static_index']}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL phase target freeze: {exc}")
