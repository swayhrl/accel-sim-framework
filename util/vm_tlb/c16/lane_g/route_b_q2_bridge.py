#!/usr/bin/env python3
"""Fail-closed Q2 Llama Route-A bridge preparation and structural checker."""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from route_b_memory_event_contract import RouteBContractError, WhitelistRow, validate_whitelist
from route_b_producer_q0 import sha256_file, whitelist_sha256


PREFILL_MANGLED = "_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21indexSelectLargeIndexIN3c104HalfEljLi2ELi2ELin2ELb1EEEvNS_4cuda6detail10TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_S9_l"
DECODE_MANGLED = "_ZN2at6native44_GLOBAL__N__50c743a2_11_Indexing_cu_89862edb21indexSelectSmallIndexIN3c104HalfEljLi2ELi2ELin2EEEvNS_4cuda6detail10TensorInfoIT_T1_EENS7_IKS8_S9_EENS7_IKT0_S9_EEiiS9_l"
ANCHORS = {"PREFILL": (PREFILL_MANGLED, 101), "DECODE": (DECODE_MANGLED, 17)}
TSV_FIELDS = ("static_index", "mref_ordinal", "instruction_offset", "width_bytes", "access_kind", "opcode", "memory_space", "has_mref", "mref_count")


def _int(row: dict[str, str], field: str) -> int:
    try: value = int(row[field])
    except (KeyError, ValueError) as exc: raise RouteBContractError(f"Q2 map has malformed {field}") from exc
    if value < 0: raise RouteBContractError(f"Q2 map has negative {field}")
    return value


def _access(row: dict[str, str]) -> str:
    pair = (_int(row, "is_load"), _int(row, "is_store"))
    if pair == (1, 0): return "READ"
    if pair == (0, 1): return "WRITE"
    if pair == (1, 1): return "ATOMIC"
    raise RouteBContractError("Q2 GLOBAL+MREF row has no static access kind")


def all_global_mref_rows(static_map: Path, anchor: str) -> tuple[WhitelistRow, ...]:
    if anchor not in ANCHORS: raise RouteBContractError("Q2 anchor must be PREFILL or DECODE")
    exact, _ = ANCHORS[anchor]
    required = {"nvbit_static_index", "instruction_offset", "opcode", "memory_space", "is_load", "is_store", "has_mref", "mref_count", "width_bytes", "function_mangled_name"}
    try:
        with static_map.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise RouteBContractError("Q2 requires an exact static map with mref_count and width_bytes authority")
            rows: list[WhitelistRow] = []; mixed = False
            for source in reader:
                if source["function_mangled_name"] != exact:
                    mixed = True; continue
                if source["memory_space"] != "GLOBAL" or _int(source, "has_mref") != 1: continue
                count = _int(source, "mref_count"); width = _int(source, "width_bytes")
                if count == 0 or width == 0: raise RouteBContractError("Q2 GLOBAL+MREF row has zero count/width")
                for ordinal in range(count):
                    rows.append(WhitelistRow(_int(source, "nvbit_static_index"), source["opcode"], "GLOBAL", True,
                                             _access(source), width, ordinal, count))
    except OSError as exc: raise RouteBContractError(f"Q2 static map unreadable: {static_map}") from exc
    if mixed: raise RouteBContractError("Q2 static map must contain one exact anchor function")
    if not rows: raise RouteBContractError("Q2 exact anchor has no GLOBAL+MREF rows")
    return validate_whitelist(tuple(sorted(rows, key=lambda row: (row.static_index, row.mref_ordinal))))


def freeze_whitelist(static_map: Path, code_object: Path, anchor: str, json_out: Path, tsv_out: Path) -> dict[str, Any]:
    rows = all_global_mref_rows(static_map, anchor)
    offsets: dict[int, int] = {}
    with static_map.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle, delimiter="\t"):
            if source["function_mangled_name"] == ANCHORS[anchor][0] and source["memory_space"] == "GLOBAL" and _int(source, "has_mref") == 1:
                offsets[_int(source, "nvbit_static_index")] = _int(source, "instruction_offset")
    json_out.write_text(json.dumps({"whitelist": [asdict(row) for row in rows]}, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    with tsv_out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TSV_FIELDS, delimiter="\t", lineterminator="\n"); writer.writeheader()
        for row in rows: writer.writerow({"static_index": row.static_index, "mref_ordinal": row.mref_ordinal, "instruction_offset": offsets[row.static_index], "width_bytes": row.width_bytes, "access_kind": row.access_kind, "opcode": row.opcode, "memory_space": "GLOBAL", "has_mref": 1, "mref_count": row.mref_count})
    return {"checkpoint": f"ROUTE_B_Q2_{anchor}_WHITELIST_READY", "anchor": anchor, "exact_function_mangled_name": ANCHORS[anchor][0], "route_a_selected_static_index": ANCHORS[anchor][1], "static_map_sha256": sha256_file(static_map), "code_object_sha256": sha256_file(code_object), "whitelist_sha256": whitelist_sha256(rows), "whitelist_row_count": len(rows)}


def check_bridge(raw_events: list[dict[str, Any]], reference: dict[str, Any]) -> dict[str, Any]:
    """Compare only structural lanes and VA-bucket cardinality, never VAs."""
    required = {"exact_function_mangled_name", "selected_static_index", "bucket_shift", "selected_instance_lane_cardinalities", "selected_address_bucket_cardinality"}
    if reference.get("schema_version") != "C16_ROUTE_A_BRIDGE_REFERENCE_V1" or not required.issubset(reference):
        raise RouteBContractError("Q2 bridge reference is absent or incomplete; do not invent Route-A authority")
    selected = [event for event in raw_events if event.get("function_mangled_name") == reference["exact_function_mangled_name"] and event.get("static_index") == reference["selected_static_index"]]
    if not selected: raise RouteBContractError("Q2 raw has no Route-A selected-PC subset")
    lanes: dict[tuple[Any, ...], set[int]] = {}
    for event in selected:
        key = (event["kernel_launch_id"], event["warp_instruction_instance_id"])
        lanes.setdefault(key, set()).add(event["lane_id"])
    observed_cardinalities = sorted(len(value) for value in lanes.values())
    shift = reference["bucket_shift"]
    if not isinstance(shift, int) or shift < 0: raise RouteBContractError("Q2 bridge bucket_shift is invalid")
    bucket_cardinality = len({event["gpu_va"] >> shift for event in selected})
    if observed_cardinalities != reference["selected_instance_lane_cardinalities"] or bucket_cardinality != reference["selected_address_bucket_cardinality"]:
        raise RouteBContractError("Q2 Route-A selected-PC structural/bucket comparison failed")
    return {"result": "PASS_Q2_ROUTE_A_BRIDGE_STRUCTURE", "selected_event_count": len(selected), "selected_instance_lane_cardinalities": observed_cardinalities, "selected_address_bucket_cardinality": bucket_cardinality, "raw_sha256": sha256(json.dumps(raw_events, sort_keys=True).encode()).hexdigest()}


def main() -> None:
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze"); freeze.add_argument("--anchor", choices=sorted(ANCHORS), required=True); freeze.add_argument("--static-map", type=Path, required=True); freeze.add_argument("--code-object", type=Path, required=True); freeze.add_argument("--whitelist-json", type=Path, required=True); freeze.add_argument("--whitelist-tsv", type=Path, required=True)
    check = sub.add_parser("check"); check.add_argument("--raw-events-json", type=Path, required=True); check.add_argument("--route-a-reference", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "freeze": print(json.dumps(freeze_whitelist(args.static_map, args.code_object, args.anchor, args.whitelist_json, args.whitelist_tsv), sort_keys=True))
    if args.command == "check":
        raw = json.loads(args.raw_events_json.read_text(encoding="utf-8")); reference = json.loads(args.route_a_reference.read_text(encoding="utf-8"))
        if not isinstance(raw, list): raise RouteBContractError("Q2 raw-events JSON must be a list emitted after parser closure")
        print(json.dumps(check_bridge(raw, reference), sort_keys=True))


if __name__ == "__main__": main()
