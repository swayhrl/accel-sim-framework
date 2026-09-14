#!/usr/bin/env python3
"""Offline-only structural bridge from frozen Route-A receipts to Route-B Q2.

This tool deliberately never derives a Route-A reference from Route-B input.
It consumes a separately frozen reference and checks only identity, selected-PC
presence, lane/request cardinality, and VA bucket *cardinality*.  GPU virtual
addresses are never compared for equality.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


class BridgeError(RuntimeError):
    """A missing or malformed evidence field closes the bridge."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _histogram(values: list[int]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items())}


def _signature(summary: dict[str, Any]) -> dict[str, Any]:
    """The comparison domain; excludes launch IDs and absolute GPU VAs."""
    fields = (
        "selected_event_count", "selected_request_count",
        "executing_lane_cardinality_histogram", "unique_exact_gpu_va_count",
        "unique_32b_block_count", "unique_64b_block_count",
        "unique_128b_line_count", "unique_4k_va_bucket_count",
        "unique_64k_va_bucket_count", "unique_2m_va_bucket_count",
    )
    return {field: summary[field] for field in fields}


def _validate_static_map(static_map: Path, phase: dict[str, Any]) -> dict[str, Any]:
    required = {
        "nvbit_static_index", "instruction_offset", "opcode", "memory_space",
        "is_load", "is_store", "has_mref", "mref_count", "width_bytes",
        "function_mangled_name", "code_object_sha256",
    }
    match: dict[str, str] | None = None
    with static_map.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise BridgeError("Q2 static map lacks required exact-function authority")
        for row in reader:
            if (row["function_mangled_name"] == phase["exact_function_mangled_name"]
                    and int(row["nvbit_static_index"]) == phase["selected_static_index"]):
                if match is not None:
                    raise BridgeError("Q2 static map has duplicate selected static index")
                match = row
    if match is None:
        raise BridgeError("Q2 static map does not contain the frozen Route-A selected PC")
    expected = phase["selected_instruction"]
    actual = {
        "instruction_offset": int(match["instruction_offset"]),
        "opcode": match["opcode"],
        "memory_space": match["memory_space"],
        "is_load": int(match["is_load"]),
        "is_store": int(match["is_store"]),
        "has_mref": int(match["has_mref"]),
        "mref_count": int(match["mref_count"]),
        "width_bytes": int(match["width_bytes"]),
        "code_object_sha256": match["code_object_sha256"],
    }
    if actual != expected:
        raise BridgeError("Q2 selected PC does not match the frozen Route-A instruction identity")
    return {"path": str(static_map), "sha256": _sha256(static_map), "selected_instruction": actual}


def summarize_selected(raw_path: Path, phase: dict[str, Any]) -> dict[str, Any]:
    """Validate the whole stream terminal, then summarize the selected PC by launch."""
    selected: dict[int, list[dict[str, Any]]] = defaultdict(list)
    lane_event_count = 0
    terminal: dict[str, Any] | None = None
    with raw_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            record = json.loads(line)
            kind = record.get("record_kind")
            if kind == "LANE_EVENT":
                if terminal is not None:
                    raise BridgeError("LANE_EVENT follows terminal")
                lane_event_count += 1
                if (record.get("function_mangled_name") == phase["exact_function_mangled_name"]
                        and record.get("static_index") == phase["selected_static_index"]):
                    if not isinstance(record.get("gpu_va"), int) or record["gpu_va"] == 0:
                        raise BridgeError("selected Route-B event has zero or invalid gpu_va")
                    if record.get("memory_space") != "GLOBAL":
                        raise BridgeError("selected Route-B event is not GLOBAL")
                    if record.get("mref_ordinal") != phase["selected_mref_ordinal"]:
                        raise BridgeError("selected Route-B event has an unexpected MREF ordinal")
                    mask = record.get("executing_mask")
                    lane = record.get("lane_id")
                    if not isinstance(mask, int) or not isinstance(lane, int) or not (mask & (1 << lane)):
                        raise BridgeError("selected Route-B lane is not predicate-true executing")
                    selected[record["kernel_launch_id"]].append(record)
            elif kind == "TERMINAL":
                if terminal is not None or line_number == 1:
                    raise BridgeError("stream has an invalid terminal layout")
                terminal = record
            else:
                raise BridgeError("stream has an unknown record kind")
    if terminal is None:
        raise BridgeError("stream has no terminal")
    if (terminal.get("terminal_status") != "COMPLETE" or terminal.get("overflow_count") != 0
            or terminal.get("drop_count") != 0 or terminal.get("event_count") != lane_event_count):
        raise BridgeError("stream terminal does not close the actual LANE_EVENT count")
    if not selected:
        raise BridgeError("stream has no frozen Route-A selected-PC events")

    per_launch: list[dict[str, Any]] = []
    for launch_id, events in sorted(selected.items()):
        instances: dict[int, set[int]] = defaultdict(set)
        vas: set[int] = set()
        for event in events:
            instances[event["warp_instruction_instance_id"]].add(event["lane_id"])
            vas.add(event["gpu_va"])
        per_launch.append({
            "kernel_launch_id": launch_id,
            "selected_event_count": len(events),
            "selected_request_count": len(instances),
            "executing_lane_cardinality_histogram": _histogram([len(lanes) for lanes in instances.values()]),
            "unique_exact_gpu_va_count": len(vas),
            "unique_32b_block_count": len({va >> 5 for va in vas}),
            "unique_64b_block_count": len({va >> 6 for va in vas}),
            "unique_128b_line_count": len({va >> 7 for va in vas}),
            "unique_4k_va_bucket_count": len({va >> 12 for va in vas}),
            "unique_64k_va_bucket_count": len({va >> 16 for va in vas}),
            "unique_2m_va_bucket_count": len({va >> 21 for va in vas}),
        })
    return {
        "raw_path": str(raw_path), "raw_sha256": _sha256(raw_path),
        "terminal": {key: terminal[key] for key in ("terminal_status", "overflow_count", "drop_count", "event_count")},
        "selected_per_launch": per_launch,
    }


def _receipt_terminal(receipt: dict[str, Any]) -> dict[str, Any]:
    result = receipt.get("result", {})
    return result.get("terminal") or result.get("parse", {}).get("terminal") or {}


def check_phase(reference_phase: dict[str, Any], raw_path: Path, static_map: Path, receipt_path: Path) -> dict[str, Any]:
    static_binding = _validate_static_map(static_map, reference_phase)
    observed = summarize_selected(raw_path, reference_phase)
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_raw = receipt.get("raw", {})
    receipt_terminal = _receipt_terminal(receipt)
    terminal_keys = ("terminal_status", "overflow_count", "drop_count", "event_count")
    if (receipt_raw.get("sha256") != observed["raw_sha256"]
            or any(receipt_terminal.get(key) != observed["terminal"][key] for key in terminal_keys)):
        raise BridgeError("Q2 capture receipt does not bind the raw stream terminal and SHA256")
    expected = reference_phase["historical_capture_signatures"]
    observed_signatures = [_signature(item) for item in observed["selected_per_launch"]]
    if sorted(expected, key=lambda item: json.dumps(item, sort_keys=True)) != sorted(observed_signatures, key=lambda item: json.dumps(item, sort_keys=True)):
        raise BridgeError("Q2 selected-PC structural footprint differs from frozen Route-A receipt")
    return {
        "status": "PASS",
        "comparison": "IDENTITY_SELECTED_PC_EXECUTING_LANES_AND_BUCKET_CARDINALITIES_ONLY",
        "absolute_gpu_va_comparison": "PROHIBITED",
        "capture_receipt": {"path": str(receipt_path), "sha256": _sha256(receipt_path)},
        "static_binding": static_binding,
        "dynamic_observation": observed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--prefill-raw", type=Path, required=True)
    parser.add_argument("--prefill-static-map", type=Path, required=True)
    parser.add_argument("--prefill-receipt", type=Path, required=True)
    parser.add_argument("--decode-raw", type=Path, required=True)
    parser.add_argument("--decode-static-map", type=Path, required=True)
    parser.add_argument("--decode-receipt", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    reference = json.loads(args.reference.read_text(encoding="utf-8"))
    if reference.get("schema_version") != "C16_ROUTE_A_BRIDGE_REFERENCE_V1":
        raise BridgeError("reference schema is not frozen Route-A V1")
    result = {
        "schema_version": "ROUTE_B_Q2_BRIDGE_CLOSEOUT_V1",
        "route_a_reference": {"path": args.reference.name, "sha256": _sha256(args.reference)},
        "prefill": check_phase(reference["phases"]["PREFILL"], args.prefill_raw, args.prefill_static_map, args.prefill_receipt),
        "decode": check_phase(reference["phases"]["DECODE"], args.decode_raw, args.decode_static_map, args.decode_receipt),
    }
    result["status"] = "PASS" if all(result[name]["status"] == "PASS" for name in ("prefill", "decode")) else "FAIL_CLOSED"
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
