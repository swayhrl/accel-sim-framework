#!/usr/bin/env python3
"""Freeze one deterministic replacement for a proven predicated-off target.

This is deliberately separate from the direct-MREF-zero fallback: its sole
admission evidence is an offline trace proving the prior exact instruction was
emitted with an all-zero predicate conjunction.  It chooses the first
*unpredicated* direct GLOBAL MREF in the same immutable NVBit-native map.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_PREDICATED_OFF_REPLACEMENT_TARGET_V1"


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path} is not an object")
    return value


def select(map_path: Path, *, function: str, lib_sha: str, prior_index: int) -> dict[str, Any]:
    lines = map_path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space"):
        raise ContractError("NVBit-native map schema differs")
    candidates: list[list[str]] = []
    for line in lines[1:]:
        fields = line.split("\t")
        if len(fields) < 13:
            raise ContractError("malformed NVBit-native map row")
        index = int(fields[0])
        opcode, space, has_mref, sass, mangled, row_sha = fields[3], fields[4], fields[7], fields[8], fields[10], fields[12]
        if (index != prior_index and opcode.startswith(("LDG", "STG", "ATOM")) and space == "GLOBAL"
                and has_mref == "1" and not sass.lstrip().startswith("@")
                and mangled == function and row_sha == lib_sha):
            candidates.append(fields)
    if not candidates:
        raise ContractError("no unpredicated direct GLOBAL MREF is available in the bound function map")
    fields = min(candidates, key=lambda row: int(row[0]))
    return {
        "nvbit_static_index": int(fields[0]), "vector_ordinal": int(fields[1]),
        "instruction_offset": int(fields[2]), "opcode": fields[3], "memory_space": fields[4],
        "is_load": fields[5] == "1", "is_store": fields[6] == "1", "has_mref": fields[7] == "1", "sass": fields[8],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--prior-target", type=Path, required=True)
    parser.add_argument("--forensics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("FAIL predicated-off target: refuses to overwrite frozen target")
    prior, forensic = load(args.prior_target), load(args.forensics)
    if forensic.get("classification") != "PREDICATED_OFF_TARGET":
        raise SystemExit("FAIL predicated-off target: forensic evidence is not a predicate-off proof")
    try:
        function = prior["function"]
        instruction = prior["target_instruction"]
        mangled = str(function["mangled_name"])
        lib_sha = str(function["libtorch_cuda_sha256"])
        prior_index = int(instruction["nvbit_static_index"])
    except (KeyError, TypeError, ValueError) as exc:
        raise SystemExit("FAIL predicated-off target: malformed frozen prior target") from exc
    target = select(args.map, function=mangled, lib_sha=lib_sha, prior_index=prior_index)
    value = {
        "schema_version": SCHEMA,
        "status": "PREDICATED_OFF_TARGET_REPLACEMENT_SELECTED",
        "scientific_eligible": False,
        "selection_basis": "EARLIEST_UNPREDICATED_DIRECT_GLOBAL_MREF_IN_SAME_EXACT_FUNCTION_AFTER_PREDICATE_OFF_PROOF",
        "function": function,
        "target_instruction": target,
        "range_contract": {"instr_begin": target["nvbit_static_index"], "instr_end_exclusive": target["nvbit_static_index"] + 1},
        "prior_target": {"path": str(args.prior_target), "sha256": sha256_file(args.prior_target), "static_index": prior_index},
        "predicate_off_forensics": {"path": str(args.forensics), "sha256": sha256_file(args.forensics),
                                      "predicate_mask_nonzero_rows": forensic["predicate_mask_nonzero_rows"],
                                      "predicate_mask_zero_rows": forensic["predicate_mask_zero_rows"]},
        "map": {"path": str(args.map), "sha256": sha256_file(args.map)},
        "forbidden": ["WIDEN_PRIOR_RANGE", "KERNEL_NAME_ONLY_SUBSTITUTION", "PERFORMANCE_OUTCOME_SELECTION", "STATIC_ORDINAL_REUSE"],
    }
    atomic_json(args.output, value)
    print(f"PASS PREDICATED_OFF_TARGET_REPLACEMENT_SELECTED index={target['nvbit_static_index']}")


if __name__ == "__main__":
    main()
