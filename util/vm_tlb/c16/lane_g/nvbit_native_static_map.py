#!/usr/bin/env python3
"""Validate an NVBit-native instruction map and select one exact memory Instr*.

The map is emitted by ``retry570_targeted_memory_tool.cu`` from NVBit's
``Instr`` vector.  This module deliberately has no SASS-text-line or
user-supplied-ordinal fallback: only ``nvbit_static_index`` in the emitted map
can become a target index.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from c16_native_common import ContractError, atomic_json, sha256_file


MAP_FIELDS = (
    "nvbit_static_index",
    "vector_ordinal",
    "instruction_offset",
    "opcode",
    "memory_space",
    "is_load",
    "is_store",
    "has_mref",
    "sass",
    "function_full_name",
    "function_mangled_name",
    "function_address",
    "libtorch_cuda_sha256",
)
MEMORY_OPCODE_PREFIXES = ("LDG", "STG", "ATOM")


@dataclass(frozen=True)
class NativeInstruction:
    nvbit_static_index: int
    vector_ordinal: int
    instruction_offset: int
    opcode: str
    memory_space: str
    is_load: bool
    is_store: bool
    has_mref: bool
    sass: str
    function_full_name: str
    function_mangled_name: str
    function_address: str
    libtorch_cuda_sha256: str

    def is_targetable_global_memory(self) -> bool:
        return (
            self.memory_space == "GLOBAL"
            and self.opcode.startswith(MEMORY_OPCODE_PREFIXES)
            and self.has_mref
            and bool(self.sass.strip())
        )


def _as_nonnegative_int(value: str, field: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"NVBit map {field} is not an integer") from exc
    if parsed < 0:
        raise ContractError(f"NVBit map {field} must be non-negative")
    return parsed


def _as_bool(value: str, field: str) -> bool:
    if value not in {"0", "1"}:
        raise ContractError(f"NVBit map {field} must be 0 or 1")
    return value == "1"


def read_native_map(path: Path, expected_mangled_name: str) -> list[NativeInstruction]:
    """Read a single-function map with strict field and identity closure."""
    if not path.is_file():
        raise ContractError("NVBit-native map is absent")
    if not expected_mangled_name:
        raise ContractError("exact mangled function identity is required")
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != MAP_FIELDS:
            raise ContractError("NVBit-native map fields differ from the fixed schema")
        rows = list(reader)
    if not rows:
        raise ContractError("NVBit-native map has no static instructions")
    mapped: list[NativeInstruction] = []
    indices: set[int] = set()
    vector_ordinals: set[int] = set()
    addresses: set[str] = set()
    code_object_hashes: set[str] = set()
    for row in rows:
        if set(row) != set(MAP_FIELDS) or any(row[field] is None for field in MAP_FIELDS):
            raise ContractError("NVBit-native map row is malformed")
        if row["function_mangled_name"] != expected_mangled_name:
            raise ContractError("NVBit-native map includes a non-exact function identity")
        instruction = NativeInstruction(
            nvbit_static_index=_as_nonnegative_int(row["nvbit_static_index"], "nvbit_static_index"),
            vector_ordinal=_as_nonnegative_int(row["vector_ordinal"], "vector_ordinal"),
            instruction_offset=_as_nonnegative_int(row["instruction_offset"], "instruction_offset"),
            opcode=row["opcode"],
            memory_space=row["memory_space"],
            is_load=_as_bool(row["is_load"], "is_load"),
            is_store=_as_bool(row["is_store"], "is_store"),
            has_mref=_as_bool(row["has_mref"], "has_mref"),
            sass=row["sass"],
            function_full_name=row["function_full_name"],
            function_mangled_name=row["function_mangled_name"],
            function_address=row["function_address"],
            libtorch_cuda_sha256=row["libtorch_cuda_sha256"],
        )
        if not instruction.opcode or not instruction.sass or not instruction.function_full_name:
            raise ContractError("NVBit-native map lacks direct instruction/function evidence")
        if not instruction.function_address:
            raise ContractError("NVBit-native map lacks the loaded function address")
        if len(instruction.libtorch_cuda_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in instruction.libtorch_cuda_sha256
        ):
            raise ContractError("NVBit-native map lacks an exact libtorch_cuda SHA256")
        if instruction.nvbit_static_index in indices or instruction.vector_ordinal in vector_ordinals:
            raise ContractError("NVBit-native map has duplicate static/vector indices")
        indices.add(instruction.nvbit_static_index)
        vector_ordinals.add(instruction.vector_ordinal)
        addresses.add(instruction.function_address)
        code_object_hashes.add(instruction.libtorch_cuda_sha256)
        mapped.append(instruction)
    if len(addresses) != 1:
        raise ContractError("NVBit-native map spans multiple loaded function addresses")
    if len(code_object_hashes) != 1:
        raise ContractError("NVBit-native map spans multiple libtorch_cuda code identities")
    if sorted(vector_ordinals) != list(range(len(mapped))):
        raise ContractError("NVBit-native map vector ordinals are not contiguous from zero")
    return mapped


def select_memory_instruction(instructions: Iterable[NativeInstruction]) -> NativeInstruction:
    """Choose deterministically from directly reported GLOBAL LDG/STG/ATOM rows."""
    candidates = [instruction for instruction in instructions if instruction.is_targetable_global_memory()]
    if not candidates:
        raise ContractError("NVBit-native map has no directly evidenced GLOBAL LDG/STG/ATOM instruction")
    priority = {"LDG": 0, "STG": 1, "ATOM": 2}
    return min(candidates, key=lambda item: (priority[next(prefix for prefix in MEMORY_OPCODE_PREFIXES if item.opcode.startswith(prefix))], item.nvbit_static_index))


def target_receipt(map_path: Path, expected_mangled_name: str) -> dict[str, object]:
    instructions = read_native_map(map_path, expected_mangled_name)
    target = select_memory_instruction(instructions)
    return {
        "schema_version": "C16_G_RETRY570_NVBIT_NATIVE_MEMORY_TARGET_V1",
        "status": "NVBIT_NATIVE_STATIC_INDEX_SELECTED",
        "scientific_eligible": False,
        "selection_basis": "NVBIT_GET_INSTRS_DIRECT_OPCODE_AND_MEMORY_SPACE",
        "map_path": str(map_path),
        "map_sha256": sha256_file(map_path),
        "function": {
            "full_name": target.function_full_name,
            "mangled_name": target.function_mangled_name,
            "loaded_function_address": target.function_address,
            "static_instruction_count": len(instructions),
            "libtorch_cuda_sha256": target.libtorch_cuda_sha256,
        },
        "target_instruction": {
            "nvbit_static_index": target.nvbit_static_index,
            "vector_ordinal": target.vector_ordinal,
            "instruction_offset": target.instruction_offset,
            "opcode": target.opcode,
            "memory_space": target.memory_space,
            "is_load": target.is_load,
            "is_store": target.is_store,
            "has_mref": target.has_mref,
            "sass": target.sass,
        },
        "historical_candidates": {
            "348": "HISTORICAL_CANDIDATE_ORDINAL_NOT_USED_AS_NVBIT_INDEX",
            "34": "SASS_TEXT_LINE_COUNTER_NOT_USED_AS_NVBIT_INDEX",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--exact-mangled-function", required=True)
    parser.add_argument("--target-receipt", type=Path, required=True)
    args = parser.parse_args()
    atomic_json(args.target_receipt, target_receipt(args.map, args.exact_mangled_function))
    print(f"PASS NVBit-native static target: {args.target_receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL NVBit-native static target: {exc}")
