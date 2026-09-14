#!/usr/bin/env python3
"""Freeze Q1's exact static map into an all-GLOBAL+MREF Route-B whitelist.

This utility is CPU-only.  Lane A supplies the one-function NVBit static map
after it has built the tiny fixture; this tool refuses all ambiguous map rows
and emits both the JSON preflight whitelist and the nine-column TSV consumed
by the NVBit producer.
"""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

from route_b_memory_event_contract import RouteBContractError, WhitelistRow, validate_whitelist
from route_b_producer_q0 import sha256_file, whitelist_sha256


Q1_EXACT_FUNCTION = "c16_route_b_q1_global_ldst_predicate"
Q1_DIRECT_ACCESS_WIDTH_BYTES = 4
TSV_COLUMNS = ("static_index", "mref_ordinal", "instruction_offset", "width_bytes", "access_kind", "opcode", "memory_space", "has_mref", "mref_count")


def _integer(row: dict[str, str], name: str) -> int:
    try:
        value = int(row[name])
    except (KeyError, ValueError) as exc:
        raise RouteBContractError(f"Q1 static map has malformed {name}") from exc
    if value < 0:
        raise RouteBContractError(f"Q1 static map has negative {name}")
    return value


def _access_kind(row: dict[str, str]) -> str:
    load, store = _integer(row, "is_load"), _integer(row, "is_store")
    if (load, store) == (1, 0): return "READ"
    if (load, store) == (0, 1): return "WRITE"
    if (load, store) == (1, 1): return "ATOMIC"
    raise RouteBContractError("Q1 GLOBAL+MREF row has no explicit access kind")


def whitelist_from_static_map(static_map: Path) -> tuple[WhitelistRow, ...]:
    try:
        with static_map.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None:
                raise RouteBContractError("Q1 static map has no TSV header")
            required = {"nvbit_static_index", "instruction_offset", "opcode", "memory_space", "is_load", "is_store", "has_mref", "mref_count", "function_mangled_name"}
            if not required.issubset(reader.fieldnames):
                raise RouteBContractError("Q1 static map misses required Route-B authority columns")
            selected: list[WhitelistRow] = []
            all_exact = True
            for source in reader:
                if source["function_mangled_name"] != Q1_EXACT_FUNCTION:
                    all_exact = False
                    continue
                if source["memory_space"] != "GLOBAL" or _integer(source, "has_mref") != 1:
                    continue
                mref_count = _integer(source, "mref_count")
                if mref_count == 0:
                    raise RouteBContractError("Q1 GLOBAL+MREF static row declares zero MREF operands")
                for ordinal in range(mref_count):
                    selected.append(WhitelistRow(
                        static_index=_integer(source, "nvbit_static_index"), opcode=source["opcode"],
                        memory_space="GLOBAL", has_mref=True, access_kind=_access_kind(source),
                        width_bytes=_width_bytes(source), mref_ordinal=ordinal, mref_count=mref_count))
    except OSError as exc:
        raise RouteBContractError(f"Q1 static map is unreadable: {static_map}") from exc
    if not selected:
        raise RouteBContractError("Q1 static map has no exact GLOBAL+MREF rows")
    if not all_exact:
        # One-function map output is mandatory; accepting a mixed map would
        # make the exact-function whitelist authority ambiguous.
        raise RouteBContractError("Q1 static map contains a non-Q1 exact function")
    return validate_whitelist(tuple(sorted(selected, key=lambda item: (item.static_index, item.mref_ordinal))))


def _width_bytes(row: dict[str, str]) -> int:
    # This fixture's source declares uint32_t direct GLOBAL source/destination
    # operands.  The frozen exact fixture source is therefore the width
    # authority; no width is guessed from opcode/SASS text.  A future generic
    # producer must instead receive an explicit per-static-row width field.
    del row
    return Q1_DIRECT_ACCESS_WIDTH_BYTES


def freeze(static_map: Path, code_object: Path, json_out: Path, tsv_out: Path) -> dict[str, object]:
    rows = whitelist_from_static_map(static_map)
    # Instruction offset is retained in the producer TSV for the NVBit-side
    # static-map equality check.  It is not part of the cross-language
    # WhitelistRow identity, so recover it only from this same SHA-closed map.
    offsets: dict[int, int] = {}
    with static_map.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            if source["function_mangled_name"] == Q1_EXACT_FUNCTION and source["memory_space"] == "GLOBAL" and _integer(source, "has_mref") == 1:
                index = _integer(source, "nvbit_static_index")
                offset = _integer(source, "instruction_offset")
                if index in offsets and offsets[index] != offset:
                    raise RouteBContractError("Q1 static map repeats an index with conflicting instruction offsets")
                offsets[index] = offset
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps({"whitelist": [asdict(row) for row in rows]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with tsv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({"static_index": row.static_index, "mref_ordinal": row.mref_ordinal,
                             "instruction_offset": offsets[row.static_index], "width_bytes": row.width_bytes,
                             "access_kind": row.access_kind, "opcode": row.opcode, "memory_space": row.memory_space,
                             "has_mref": 1, "mref_count": row.mref_count})
    return {"checkpoint": "ROUTE_B_Q1_STATIC_WHITELIST_READY", "exact_function_mangled_name": Q1_EXACT_FUNCTION,
            "code_object_path": str(code_object), "code_object_sha256": sha256_file(code_object),
            "static_map_path": str(static_map), "static_map_sha256": sha256_file(static_map),
            "whitelist_path": str(json_out), "whitelist_tsv_path": str(tsv_out), "whitelist_sha256": whitelist_sha256(rows),
            "whitelist_row_count": len(rows)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--static-map", type=Path, required=True)
    parser.add_argument("--code-object", type=Path, required=True)
    parser.add_argument("--whitelist-json", type=Path, required=True)
    parser.add_argument("--whitelist-tsv", type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(freeze(arguments.static_map, arguments.code_object, arguments.whitelist_json, arguments.whitelist_tsv), sort_keys=True))


if __name__ == "__main__":
    main()
