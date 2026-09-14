#!/usr/bin/env python3
"""CPU-side manifest, whitelist, and LANE_EVENT parser for Route-B Q0/Q1.

This module is deliberately GPU-free.  The NVBit host tool uses the immutable
manifest produced here as its preflight authority; this parser then validates
raw JSONL emitted after device-buffer readback.  Dynamic warp instances are
joined only on the explicit producer-supplied instance id, never on adjacent
callback sequence numbers.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable

from route_b_memory_event_contract import (
    RAW_SCHEMA,
    RouteBContractError,
    WhitelistRow,
    validate_stream,
    validate_whitelist,
)
from route_b_producer_q0 import ProducerBinding, verify_binding, whitelist_sha256


MANIFEST_SCHEMA = "C16_ROUTE_B_LANE_EVENT_PRODUCER_MANIFEST_V1"
PARSER_SCHEMA = "C16_ROUTE_B_LANE_EVENT_PARSE_MANIFEST_V1"


def load_whitelist(path: Path) -> tuple[WhitelistRow, ...]:
    """Load the only accepted JSON whitelist representation and fail closed."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteBContractError(f"Route-B whitelist is unreadable: {path}") from exc
    rows = document.get("whitelist") if isinstance(document, dict) else document
    if not isinstance(rows, list):
        raise RouteBContractError("Route-B whitelist must be a JSON list or a whitelist field")
    try:
        return validate_whitelist(tuple(WhitelistRow(**row) for row in rows))
    except (TypeError, ValueError) as exc:
        raise RouteBContractError("Route-B whitelist row is malformed") from exc


def _atomic_json(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    payload = json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n"
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def write_verified_producer_manifest(path: Path, binding: ProducerBinding, whitelist_path: Path) -> dict[str, Any]:
    """Preflight files/whitelist and atomically publish host-tool authority."""
    rows = load_whitelist(whitelist_path)
    verify_binding(binding, rows)
    document: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA,
        "raw_schema": RAW_SCHEMA,
        "exact_function_mangled_name": binding.exact_function_mangled_name,
        "code_object_path": str(binding.code_object_path),
        "code_object_sha256": binding.code_object_sha256,
        "static_map_path": str(binding.static_map_path),
        "static_map_sha256": binding.static_map_sha256,
        "whitelist_path": str(whitelist_path),
        "whitelist_sha256": whitelist_sha256(rows),
        "whitelist": [asdict(row) for row in rows],
        "host_output_cap_bytes": binding.host_output_cap_bytes,
        "event_kind": "LANE_EVENT",
        "sequence_label": "OBSERVED_CALLBACK_ORDER",
        "terminal_required": True,
        "fail_closed": {"overflow_count": 0, "drop_count": 0, "terminal_status": "COMPLETE"},
    }
    _atomic_json(path, document)
    return document


def parse_raw_jsonl(raw_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate host readback and emit a compact parser manifest.

    The raw stream must contain LANE_EVENT records and exactly one terminal
    record.  Event grouping is delegated to ``validate_stream`` which uses the
    explicit instance ID contained in every lane event.
    """
    if manifest.get("schema_version") != MANIFEST_SCHEMA or manifest.get("raw_schema") != RAW_SCHEMA:
        raise RouteBContractError("Route-B producer manifest does not authorize the LANE_EVENT schema")
    rows = validate_whitelist(tuple(WhitelistRow(**row) for row in manifest.get("whitelist", [])))
    if manifest.get("whitelist_sha256") != whitelist_sha256(rows):
        raise RouteBContractError("Route-B producer manifest whitelist SHA mismatch")
    events: list[dict[str, Any]] = []
    terminals: list[dict[str, Any]] = []
    try:
        lines = raw_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RouteBContractError(f"Route-B raw stream is unreadable: {raw_path}") from exc
    for line_number, line in enumerate(lines, 1):
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RouteBContractError(f"Route-B raw JSONL is malformed at line {line_number}") from exc
        if record.get("record_kind") == "TERMINAL":
            terminals.append(record)
        elif record.get("record_kind") == "LANE_EVENT":
            events.append(record)
        else:
            raise RouteBContractError("Route-B raw stream has an unknown record kind")
    if len(terminals) != 1:
        raise RouteBContractError("Route-B raw stream requires exactly one terminal record")
    event_count = validate_stream(events, rows, terminals[0])
    return {
        "schema_version": PARSER_SCHEMA,
        "raw_schema": RAW_SCHEMA,
        "raw_path": str(raw_path),
        "raw_sha256": sha256(raw_path.read_bytes()).hexdigest(),
        "event_count": event_count,
        "terminal": terminals[0],
        "whitelist_sha256": manifest["whitelist_sha256"],
        "result": "PASS_LANE_EVENT_STREAM",
    }


def write_parse_manifest(path: Path, raw_path: Path, producer_manifest: dict[str, Any]) -> dict[str, Any]:
    result = parse_raw_jsonl(raw_path, producer_manifest)
    _atomic_json(path, result)
    return result
