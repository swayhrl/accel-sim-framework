#!/usr/bin/env python3
"""Freeze a new phase-specific target after a direct, instrumented zero.

This tool never widens an instruction range and never rewrites the prior
target.  It accepts only a closed exact-function diagnostic proving the prior
NVBit-native instruction was launched/instrumented but produced zero direct
records.  It then applies one deterministic, outcome-independent fallback:
the earliest *unpredicated* GLOBAL MREF store in the same per-phase NVBit map.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, repo_root, sha256_file


SCHEMA = "C16_G_RECOVERY_V3_NVBIT_NATIVE_MEMORY_TARGET_V2"


def git_head() -> str:
    return subprocess.check_output(["git", "-C", str(repo_root()), "rev-parse", "HEAD"], text=True).strip()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("cannot read closed target evidence") from exc
    if not isinstance(value, dict):
        raise ContractError("closed target evidence must be an object")
    return value


def select(map_path: Path, *, prior_index: int, function: str, lib_sha: str) -> dict[str, Any]:
    rows = map_path.read_text(encoding="utf-8", errors="strict").splitlines()
    if not rows or not rows[0].startswith("nvbit_static_index\tvector_ordinal\tinstruction_offset\topcode\tmemory_space"):
        raise ContractError("NVBit-native map schema differs")
    candidates = []
    for line in rows[1:]:
        fields = line.split("\t")
        if len(fields) < 13:
            raise ContractError("NVBit-native map contains a malformed row")
        index = int(fields[0])
        opcode, space, is_store, has_mref, sass, mangled, row_sha = fields[3], fields[4], fields[6], fields[7], fields[8], fields[10], fields[12]
        if (index != prior_index and opcode.startswith("STG") and space == "GLOBAL" and is_store == "1"
                and has_mref == "1" and not sass.lstrip().startswith("@") and mangled == function and row_sha == lib_sha):
            candidates.append(fields)
    if not candidates:
        raise ContractError("no unpredicated direct GLOBAL store remains after the closed prior target")
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
    parser.add_argument("--zero-record-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ContractError("next static target refuses to overwrite a frozen target receipt")
    prior, zero = read_json(args.prior_target), read_json(args.zero_record_receipt)
    if zero.get("status") != "COMPLETE_ZERO_DIRECT_MEMORY_RECORD":
        raise ContractError("next target requires a complete direct-instrumented zero-record receipt")
    try:
        instruction = prior["target_instruction"]
        function = prior["function"]
        direct = zero["direct_memory_record"]
        prior_index = int(instruction["nvbit_static_index"])
        mangled, lib_sha = str(function["mangled_name"]), str(function["libtorch_cuda_sha256"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError("prior target or zero-record receipt is malformed") from exc
    if (direct.get("memory_record_present") is not False or direct.get("exact_function_launch_count", 0) <= 0
            or zero.get("reproduced_static_target", {}).get("static_index") != prior_index
            or zero.get("reproduced_static_target", {}).get("function_mangled_name") != mangled):
        raise ContractError("prior direct-instrumented zero does not bind this exact function/static target")
    target = select(args.map, prior_index=prior_index, function=mangled, lib_sha=lib_sha)
    value = {
        "schema_version": SCHEMA, "status": "NVBIT_NATIVE_STATIC_INDEX_SELECTED_V2",
        "scientific_eligible": False, "producer_code_commit": git_head(),
        "selection_basis": "EARLIEST_UNPREDICATED_GLOBAL_MREF_STORE_AFTER_DIRECT_INSTRUMENTED_ZERO",
        "function": {**function, "static_instruction_count": prior["function"]["static_instruction_count"]},
        "target_instruction": target,
        "map_path": str(args.map), "map_sha256": sha256_file(args.map),
        "prior_target": {"path": str(args.prior_target), "sha256": sha256_file(args.prior_target), "static_index": prior_index},
        "prior_zero_record_diagnostic": {"path": str(args.zero_record_receipt), "sha256": sha256_file(args.zero_record_receipt),
                                          "exact_function_launch_count": direct["exact_function_launch_count"]},
        "range_contract": {"instr_begin": target["nvbit_static_index"], "instr_end_exclusive": target["nvbit_static_index"] + 1},
        "forbidden": ["WIDEN_PRIOR_RANGE", "KERNEL_NAME_ONLY_SUBSTITUTION", "PERFORMANCE_OUTCOME_SELECTION"],
    }
    atomic_json(args.output, value)
    print(f"PASS NVBIT_NATIVE_STATIC_INDEX_SELECTED_V2 index={target['nvbit_static_index']}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Recovery-V3 next static target: {exc}")
