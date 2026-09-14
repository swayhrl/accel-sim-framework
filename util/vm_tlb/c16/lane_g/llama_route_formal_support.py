#!/usr/bin/env python3
"""Fail-closed CPU support for Llama S0 Route-B/Route-C formal capture.

All commands consume already-frozen evidence.  They deliberately have no GPU
launching or model-running path and refuse to invent input, owner, or outcome
authority.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from route_b_memory_event_contract import RouteBContractError, WhitelistRow, validate_event, validate_terminal, validate_whitelist


MAX_RAW_BYTES = 4 * 1024**3
MAX_CAPTURE_SECONDS = 20 * 60
PRIMARY_IDENTITY = {"model": "meta-llama/Llama-3.2-1B", "scenario": "S0/B1/T128/Decode4", "gpu": "RTX3090/SM86"}


def fail(message: str) -> None:
    raise RouteBContractError(message)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteBContractError(f"unreadable JSON: {path}") from exc


def digest(path: Path) -> str:
    if not path.is_file():
        fail(f"required file is absent: {path}")
    hasher = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def atomic_write(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        fail(f"refuses to overwrite frozen output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical(value) + "\n", encoding="utf-8")


def require_identity(value: Any) -> None:
    if value != PRIMARY_IDENTITY:
        fail("artifact identity is not the frozen Llama S0 identity")


STATIC_REQUIRED = {"nvbit_static_index", "instruction_offset", "opcode", "memory_space", "is_load", "is_store", "has_mref", "mref_count", "width_bytes", "function_mangled_name"}


def integer(row: dict[str, str], field: str, *, positive: bool = False) -> int:
    try:
        result = int(row[field])
    except (KeyError, ValueError) as exc:
        raise RouteBContractError(f"static map malformed {field}") from exc
    if result < 0 or (positive and result == 0):
        fail(f"static map has invalid {field}")
    return result


def read_exact_map(row: dict[str, Any]) -> list[WhitelistRow]:
    required = {"request_id", "exact_function_mangled_name", "static_map", "static_map_sha256", "code_object_sha256"}
    if not required.issubset(row) or any(not isinstance(row[key], str) or not row[key] for key in required):
        fail("map index row lacks exact identity closure")
    static_map = Path(row["static_map"])
    if digest(static_map) != row["static_map_sha256"]:
        fail("static map hash differs from map index")
    try:
        with static_map.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if reader.fieldnames is None or not STATIC_REQUIRED.issubset(reader.fieldnames):
                fail("static map lacks width_bytes/mref_count authority")
            units: list[WhitelistRow] = []
            for source in reader:
                if source["function_mangled_name"] != row["exact_function_mangled_name"]:
                    fail("map index is not an exact one-function map")
                if source["memory_space"] != "GLOBAL" or integer(source, "has_mref") != 1:
                    continue
                count = integer(source, "mref_count", positive=True)
                index, width = integer(source, "nvbit_static_index"), integer(source, "width_bytes", positive=True)
                pair = (integer(source, "is_load"), integer(source, "is_store"))
                access = {(1, 0): "READ", (0, 1): "WRITE", (1, 1): "ATOMIC"}.get(pair)
                if access is None:
                    fail("GLOBAL+MREF static row lacks exact access kind")
                units.extend(WhitelistRow(index, source["opcode"], "GLOBAL", True, access, width, ordinal, count) for ordinal in range(count))
    except OSError as exc:
        raise RouteBContractError("static map unreadable") from exc
    return list(validate_whitelist(sorted(units, key=lambda unit: (unit.static_index, unit.mref_ordinal))))


def selection_ids(document: dict[str, Any]) -> set[str]:
    if document.get("schema_version") != "C16_ROUTE_B_FINAL_SELECTION_V2" or document.get("status") != "FROZEN_PRE_OUTCOME_SELECTION":
        fail("requires an admissible frozen Route-B final selection")
    ids = document.get("final_request_ids")
    if not isinstance(ids, list) or not ids or any(not isinstance(item, str) or not item for item in ids) or len(set(ids)) != len(ids):
        fail("selection lacks unique runnable final request IDs")
    return set(ids)


def freeze_whitelists(selection: Path, index: Path, output: Path) -> None:
    selected = selection_ids(load_json(selection))
    source = load_json(index)
    if not isinstance(source, dict) or source.get("schema_version") != "C16_ROUTE_B_SELECTED_MAP_INDEX_V1":
        fail("requires C16_ROUTE_B_SELECTED_MAP_INDEX_V1")
    require_identity(source.get("identity"))
    rows = source.get("maps")
    if not isinstance(rows, list): fail("map index lacks map rows")
    by_id = {row.get("request_id"): row for row in rows if isinstance(row, dict)}
    if set(by_id) != {row.get("request_id") for row in rows if isinstance(row, dict)} or not selected.issubset(by_id):
        fail("map index duplicates or misses selected request")
    frozen = []
    for request_id in sorted(selected):
        row = by_id[request_id]; units = read_exact_map(row)
        frozen.append({"request_id": request_id, "exact_function_mangled_name": row["exact_function_mangled_name"],
                       "static_map_sha256": row["static_map_sha256"], "code_object_sha256": row["code_object_sha256"],
                       "whitelist": [asdict(unit) for unit in units]})
    result = {"schema_version": "C16_ROUTE_B_REPRESENTATIVE_WHITELISTS_V1", "status": "FROZEN_PRE_OUTCOME_ALL_GLOBAL_MREF",
              "identity": PRIMARY_IDENTITY, "selection_sha256": digest(selection), "map_index_sha256": digest(index), "functions": frozen}
    atomic_write(output, result)


def function_whitelists(document: dict[str, Any]) -> dict[str, tuple[str, tuple[WhitelistRow, ...]]]:
    if document.get("schema_version") != "C16_ROUTE_B_REPRESENTATIVE_WHITELISTS_V1" or document.get("status") != "FROZEN_PRE_OUTCOME_ALL_GLOBAL_MREF":
        fail("requires frozen representative whitelists")
    require_identity(document.get("identity")); functions: dict[str, tuple[str, tuple[WhitelistRow, ...]]] = {}
    for function in document.get("functions", []):
        request_id = function.get("request_id") if isinstance(function, dict) else None
        mangled = function.get("exact_function_mangled_name") if isinstance(function, dict) else None
        if not isinstance(request_id, str) or not isinstance(mangled, str) or not mangled: fail("whitelist function lacks exact identity")
        rows = [WhitelistRow(**row) for row in function.get("whitelist", [])]
        if mangled in functions: fail("whitelist manifest duplicates exact function")
        functions[mangled] = (request_id, validate_whitelist(rows))
    if not functions: fail("whitelist manifest is empty")
    return functions


def units_from_manifest(document: dict[str, Any]) -> dict[str, WhitelistRow]:
    units: dict[str, WhitelistRow] = {}
    for _, (request_id, rows) in function_whitelists(document).items():
        for row in rows:
            key = f"{request_id}:{row.static_index}:{row.mref_ordinal}"
            if key in units: fail("whitelist unit duplicates")
            units[key] = row
    return units


def freeze_partitions(whitelists: Path, assignments: Path, output: Path) -> None:
    units = units_from_manifest(load_json(whitelists)); document = load_json(assignments)
    if document.get("schema_version") != "C16_ROUTE_B_PARTITION_ASSIGNMENTS_V1" or not isinstance(document.get("assignments"), list):
        fail("requires C16_ROUTE_B_PARTITION_ASSIGNMENTS_V1")
    found: dict[str, str] = {}
    for entry in document["assignments"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("unit_id"), str) or not isinstance(entry.get("partition_id"), str) or not entry["partition_id"]:
            fail("partition assignment is malformed")
        if entry["unit_id"] not in units or entry["unit_id"] in found: fail("partition assignment is unknown or duplicate")
        found[entry["unit_id"]] = entry["partition_id"]
    if set(found) != set(units): fail("partitions do not cover every selected whitelist unit exactly once")
    groups: dict[str, list[str]] = {}
    for unit, partition in found.items(): groups.setdefault(partition, []).append(unit)
    result = {"schema_version": "C16_ROUTE_B_FORMAL_PARTITIONS_V1", "status": "FROZEN_PRE_OUTCOME_PARTITIONS",
              "whitelist_manifest_sha256": digest(whitelists), "assignment_sha256": digest(assignments),
              "partitions": [{"partition_id": name, "unit_ids": sorted(values)} for name, values in sorted(groups.items())]}
    atomic_write(output, result)


def load_events(path: Path) -> list[dict[str, Any]]:
    events = []
    try:
        with path.open(encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                if not line.strip(): fail(f"raw JSONL has an empty line {number}")
                event = json.loads(line)
                if not isinstance(event, dict): fail("raw JSONL record is not an object")
                events.append(event)
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteBContractError("raw JSONL is unreadable or truncated") from exc
    if not events: fail("raw JSONL has no LANE_EVENT records")
    return events


def partition_units(whitelists: Path, partitions: Path, partition_id: str) -> set[str]:
    document = load_json(partitions)
    if document.get("schema_version") != "C16_ROUTE_B_FORMAL_PARTITIONS_V1" or document.get("status") != "FROZEN_PRE_OUTCOME_PARTITIONS":
        fail("requires frozen formal Route-B partitions")
    if document.get("whitelist_manifest_sha256") != digest(whitelists): fail("partition manifest is not bound to this whitelist")
    matches = [item for item in document.get("partitions", []) if isinstance(item, dict) and item.get("partition_id") == partition_id]
    if len(matches) != 1 or not isinstance(matches[0].get("unit_ids"), list) or not matches[0]["unit_ids"]: fail("formal capture partition is missing or empty")
    units = set(matches[0]["unit_ids"])
    if len(units) != len(matches[0]["unit_ids"]): fail("formal capture partition repeats a unit")
    if not units.issubset(units_from_manifest(load_json(whitelists))): fail("formal capture partition has an unknown unit")
    return units


def validate_multi_function_stream(events: list[dict[str, Any]], functions: dict[str, tuple[str, tuple[WhitelistRow, ...]]], terminal: dict[str, Any], allowed_units: set[str] | None) -> int:
    previous: int | None = None; count = 0
    instances: dict[tuple[int, int], tuple[tuple[Any, ...], set[int], int]] = {}
    for event in events:
        mangled = event.get("function_mangled_name")
        if not isinstance(mangled, str) or mangled not in functions: fail("raw event function is outside frozen representative whitelist")
        request_id, rows = functions[mangled]
        previous = validate_event(event, rows, previous_sequence=previous)
        unit_id = f"{request_id}:{event['static_index']}:{event['mref_ordinal']}"
        if allowed_units is not None and unit_id not in allowed_units: fail("raw event is outside the requested formal partition")
        scope = (event["kernel_launch_id"], event["warp_instruction_instance_id"])
        signature = (mangled, event["kernel_launch_id"], tuple(event["cta"]), event["warp_id"], event["static_index"], event["mref_ordinal"], event["instruction_offset"], event["opcode"], event["access_kind"], event["width_bytes"], event["active_mask"], event["predicate_mask"], event["predicate_semantics"])
        expected = event["active_mask"] & event["predicate_mask"]
        if scope not in instances: instances[scope] = (signature, set(), expected)
        known, lanes, known_expected = instances[scope]
        if known != signature or known_expected != expected or event["lane_id"] in lanes: fail("raw event has inconsistent/repeated launch-scoped warp instance")
        lanes.add(event["lane_id"]); count += 1
    for _, (_, lanes, expected) in instances.items():
        if lanes != {lane for lane in range(32) if expected & (1 << lane)}: fail("raw event misses an executing lane")
    validate_terminal(terminal, count)
    return count


def validate_capture(whitelists: Path, raw: Path, terminal: Path, metadata: Path, output: Path, kind: str, partitions: Path | None = None, partition_id: str | None = None) -> None:
    functions = function_whitelists(load_json(whitelists))
    if (partitions is None) != (partition_id is None): fail("formal capture requires both partition manifest and partition ID")
    allowed_units = partition_units(whitelists, partitions, partition_id) if partitions is not None and partition_id is not None else None
    events, terminal_doc, meta = load_events(raw), load_json(terminal), load_json(metadata)
    if not isinstance(terminal_doc, dict) or not isinstance(meta, dict): fail("terminal/metadata are malformed")
    require_identity(meta.get("identity"))
    if meta.get("raw_schema") != "C16_ROUTE_B_LANE_EVENT_V1" or meta.get("capture_duration_seconds") is None:
        fail("capture metadata lacks schema/duration")
    if not isinstance(meta["capture_duration_seconds"], (int, float)) or not 0 < meta["capture_duration_seconds"] <= MAX_CAPTURE_SECONDS:
        fail("capture duration exceeds the bounded window")
    bytes_on_disk = raw.stat().st_size
    if bytes_on_disk > MAX_RAW_BYTES or meta.get("serialized_raw_bytes") != bytes_on_disk or meta.get("raw_byte_cap") != MAX_RAW_BYTES:
        fail("actual serialized raw bytes are not within the frozen cap")
    count = validate_multi_function_stream(events, functions, terminal_doc, allowed_units)
    result = {"schema_version": "C16_ROUTE_B_CAPTURE_VALIDATION_V1", "status": f"PASS_{kind}", "identity": PRIMARY_IDENTITY,
              "raw_jsonl_sha256": digest(raw), "terminal_sha256": digest(terminal), "whitelist_manifest_sha256": digest(whitelists),
              "metadata_sha256": digest(metadata), "actual_serialized_raw_bytes": bytes_on_disk, "lane_event_count": count,
              "terminal_event_count": terminal_doc["event_count"], "capture_duration_seconds": meta["capture_duration_seconds"],
              "formal_partition_id": partition_id}
    atomic_write(output, result)


def analyze_route_c(census: Path, records: Path, output: Path) -> None:
    frozen, observed = load_json(census), load_json(records)
    if frozen.get("schema_version") != "C16_LLAMA_S0_FULL_CENSUS_V1" or not isinstance(frozen.get("rows"), list): fail("requires full frozen Llama S0 census")
    if observed.get("schema_version") != "C16_ROUTE_C_PHASE_COVERAGE_V1" or not isinstance(observed.get("covered_request_ids"), list): fail("requires Route-C phase coverage reference")
    require_identity(frozen.get("identity")); require_identity(observed.get("identity"))
    covered = set(observed["covered_request_ids"])
    totals: dict[str, int] = {}; hit: dict[str, int] = {}; ids: set[str] = set()
    for row in frozen["rows"]:
        if not isinstance(row, dict) or row.get("phase") not in {"PREFILL", "DECODE"} or not isinstance(row.get("request_id"), str) or not isinstance(row.get("duration_ns"), int) or row["duration_ns"] <= 0: fail("full census row is malformed")
        if row["request_id"] in ids: fail("full census duplicates request ID")
        ids.add(row["request_id"]); phase = row["phase"]; totals[phase] = totals.get(phase, 0) + row["duration_ns"]
        if row["request_id"] in covered: hit[phase] = hit.get(phase, 0) + row["duration_ns"]
    if not covered.issubset(ids) or set(totals) != {"PREFILL", "DECODE"}: fail("Route-C reference is outside full census or phase-incomplete")
    result = {"schema_version": "C16_ROUTE_C_COVERAGE_ANALYSIS_V1", "status": "ROUTE_C_COVERAGE_QUANTIFIED", "identity": PRIMARY_IDENTITY,
              "full_census_sha256": digest(census), "route_c_reference_sha256": digest(records),
              "phases": {phase: {"full_census_duration_ns": totals[phase], "route_c_covered_duration_ns": hit.get(phase, 0), "coverage": hit.get(phase, 0) / totals[phase]} for phase in sorted(totals)}}
    atomic_write(output, result)


REQUIRED_CLOSEOUT_STAGES = ("S0_CENSUS", "Q1", "Q2_PREFILL", "Q2_DECODE", "CUTLASS_OWNER", "SELECTION", "ROUTEB_CANARY", "ROUTEB_PARTITIONS", "ROUTEC", "REMOTE_CLOSURE")


def closeout(inputs: Path, output: Path) -> None:
    document = load_json(inputs)
    if document.get("schema_version") != "C16_LLAMA_MODEL_CLOSEOUT_INPUTS_V1" or not isinstance(document.get("artifacts"), list): fail("requires closeout input manifest")
    require_identity(document.get("identity")); seen: dict[str, dict[str, Any]] = {}
    for entry in document["artifacts"]:
        if not isinstance(entry, dict) or not all(isinstance(entry.get(key), str) and entry[key] for key in ("stage", "path", "sha256", "required_status")): fail("closeout artifact is malformed")
        if entry["stage"] in seen: fail("closeout stage duplicates")
        path = Path(entry["path"])
        if digest(path) != entry["sha256"]: fail("closeout artifact SHA differs")
        artifact = load_json(path)
        if not isinstance(artifact, dict) or artifact.get("status") != entry["required_status"]: fail("closeout artifact does not have its required terminal status")
        seen[entry["stage"]] = entry
    if set(seen) != set(REQUIRED_CLOSEOUT_STAGES): fail("closeout lacks a required completion stage")
    result = {"schema_version": "C16_LLAMA_MODEL_TRACE_COMPLETE_V1", "status": "MODEL_TRACE_COMPLETE", "model_trace_complete": "LLAMA_3P2_1B_S0_ROUTE_B_ROUTE_C_COMPLETE", "identity": PRIMARY_IDENTITY,
              "closeout_inputs_sha256": digest(inputs), "artifacts": [{"stage": stage, "path": seen[stage]["path"], "sha256": seen[stage]["sha256"], "status": seen[stage]["required_status"]} for stage in REQUIRED_CLOSEOUT_STAGES]}
    atomic_write(output, result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("freeze-whitelists"); p.add_argument("--selection", type=Path, required=True); p.add_argument("--map-index", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("freeze-partitions"); p.add_argument("--whitelists", type=Path, required=True); p.add_argument("--assignments", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    for name, kind in (("validate-canary", "ROUTEB_CANARY"), ("formal-capture", "ROUTEB_FORMAL_CAPTURE")):
        p = sub.add_parser(name); p.set_defaults(kind=kind); p.add_argument("--whitelists", type=Path, required=True); p.add_argument("--raw-jsonl", type=Path, required=True); p.add_argument("--terminal", type=Path, required=True); p.add_argument("--metadata", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
        if name == "formal-capture": p.add_argument("--partitions", type=Path); p.add_argument("--partition-id")
    p = sub.add_parser("analyze-route-c"); p.add_argument("--full-census", type=Path, required=True); p.add_argument("--route-c-reference", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    p = sub.add_parser("closeout"); p.add_argument("--inputs", type=Path, required=True); p.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "freeze-whitelists": freeze_whitelists(args.selection, args.map_index, args.output)
    elif args.command == "freeze-partitions": freeze_partitions(args.whitelists, args.assignments, args.output)
    elif args.command in {"validate-canary", "formal-capture"}: validate_capture(args.whitelists, args.raw_jsonl, args.terminal, args.metadata, args.output, args.kind, getattr(args, "partitions", None), getattr(args, "partition_id", None))
    elif args.command == "analyze-route-c": analyze_route_c(args.full_census, args.route_c_reference, args.output)
    else: closeout(args.inputs, args.output)


if __name__ == "__main__":
    try: main()
    except RouteBContractError as exc: raise SystemExit(f"FAIL Llama formal support: {exc}")
