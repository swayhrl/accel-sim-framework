#!/usr/bin/env python3
"""Fail-closed Route-B all-GLOBAL+MREF LANE_EVENT contract.

This is the CPU-side half of the versioned NVBit 1.7.5 producer.  The device
tool is required to emit these fields; this module deliberately refuses to
repair or infer missing lane, mask, memory-space, or terminal information.
It is also used by the Q0 parser fixture before a GPU capture is admitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


class RouteBContractError(ValueError):
    """Raised for an unrepresentable or scientifically unsafe Route-B event."""


ACCESS_KINDS = frozenset(("READ", "WRITE", "ATOMIC"))
MEMORY_SPACE = "GLOBAL"
OBSERVED_ORDER = "OBSERVED_CALLBACK_ORDER"
LANE_EVENT = "LANE_EVENT"
RAW_SCHEMA = "C16_ROUTE_B_LANE_EVENT_V1"
PREDICATE_SEMANTICS = "GUARD_PREDICATE_MASK"


@dataclass(frozen=True)
class WhitelistRow:
    static_index: int
    opcode: str
    memory_space: str
    has_mref: bool
    access_kind: str
    width_bytes: int
    mref_ordinal: int
    # The Route-B producer supports a distinct event stream for each MREF
    # operand.  A selected multi-MREF instruction is lawful only when this
    # count and the ordinal are explicit in the frozen static-map row.
    mref_count: int = 1


def validate_whitelist(rows: Iterable[WhitelistRow]) -> tuple[WhitelistRow, ...]:
    """Return the canonical whitelist or reject an unsafe/staticly ambiguous one."""
    result = tuple(rows)
    if not result:
        raise RouteBContractError("Route-B whitelist must contain at least one GLOBAL+MREF instruction")
    keys = [(row.static_index, row.mref_ordinal) for row in result]
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise RouteBContractError("Route-B whitelist (static-index, MREF-ordinal) keys must be sorted and unique")
    for row in result:
        if row.static_index < 0 or row.mref_ordinal < 0 or row.width_bytes <= 0 or row.mref_count <= 0:
            raise RouteBContractError("Route-B whitelist has an invalid static index, MREF ordinal, or width")
        if row.mref_ordinal >= row.mref_count:
            raise RouteBContractError("Route-B whitelist MREF ordinal is outside the explicit static-map MREF count")
        if row.memory_space != MEMORY_SPACE or not row.has_mref:
            raise RouteBContractError("Route-B whitelist may contain only GLOBAL && has_mref rows")
        if row.access_kind not in ACCESS_KINDS:
            raise RouteBContractError("Route-B whitelist has an unrecognised access kind")
    return result


def _mask_lanes(mask: int) -> list[int]:
    if not isinstance(mask, int) or mask < 0 or mask >= (1 << 32):
        raise RouteBContractError("Route-B active/predicate mask is not a uint32")
    return [lane for lane in range(32) if mask & (1 << lane)]


def validate_event(event: dict[str, Any], whitelist: tuple[WhitelistRow, ...], *, previous_sequence: int | None) -> int:
    """Validate one decoded event and return its monotonic observed sequence."""
    required = {
        "observed_event_sequence", "sequence_label", "kernel_launch_id", "function_mangled_name",
        "cta", "warp_id", "static_index", "instruction_offset", "opcode", "mref_ordinal",
        "access_kind", "width_bytes", "memory_space", "active_mask", "predicate_mask", "predicate_semantics",
        "record_kind", "raw_schema", "warp_instruction_instance_id", "lane_id", "gpu_va",
    }
    missing = sorted(required.difference(event))
    if missing:
        raise RouteBContractError("Route-B event misses required fields: " + ",".join(missing))
    sequence = event["observed_event_sequence"]
    if not isinstance(sequence, int) or sequence < 0 or (previous_sequence is not None and sequence <= previous_sequence):
        raise RouteBContractError("Route-B event sequence is not strictly monotonic")
    if event["sequence_label"] != OBSERVED_ORDER:
        raise RouteBContractError("Route-B event order must be labelled OBSERVED_CALLBACK_ORDER")
    if event["record_kind"] != LANE_EVENT or event["raw_schema"] != RAW_SCHEMA:
        raise RouteBContractError("Route-B raw event is not the versioned LANE_EVENT schema")
    if not isinstance(event["warp_instruction_instance_id"], int) or event["warp_instruction_instance_id"] < 0:
        raise RouteBContractError("Route-B LANE_EVENT lacks a nonnegative explicit warp instruction instance id")
    allowed = {(row.static_index, row.mref_ordinal): row for row in whitelist}
    key = (event["static_index"], event["mref_ordinal"])
    row = allowed.get(key)
    if row is None:
        raise RouteBContractError("Route-B event static-index/MREF pair is outside the frozen whitelist")
    if event["memory_space"] != MEMORY_SPACE or event["access_kind"] != row.access_kind:
        raise RouteBContractError("Route-B event memory space/access kind differs from static whitelist")
    if event["opcode"] != row.opcode or event["width_bytes"] != row.width_bytes:
        raise RouteBContractError("Route-B event opcode/width differs from static whitelist")
    active_mask = event["active_mask"]
    predicate_mask = event["predicate_mask"]
    active_lanes = _mask_lanes(active_mask)
    predicate_lanes = _mask_lanes(predicate_mask)
    if event["predicate_semantics"] != PREDICATE_SEMANTICS:
        raise RouteBContractError("Route-B predicate semantics are not explicit guard-mask semantics")
    executing_lanes = _mask_lanes(active_mask & predicate_mask)
    lane = event["lane_id"]
    if not isinstance(lane, int) or lane not in executing_lanes:
        raise RouteBContractError("Route-B LANE_EVENT lane is not an executing lane")
    if not isinstance(event["gpu_va"], int) or event["gpu_va"] <= 0:
        raise RouteBContractError("Route-B LANE_EVENT contains a non-GPU-VA address")
    if not set(predicate_lanes).issubset(active_lanes):
        raise RouteBContractError("Route-B predicate mask names inactive lanes")
    cta = event["cta"]
    if not isinstance(cta, list) or len(cta) != 3 or any(not isinstance(value, int) or value < 0 for value in cta):
        raise RouteBContractError("Route-B CTA identity is malformed")
    if not isinstance(event["warp_id"], int) or event["warp_id"] < 0:
        raise RouteBContractError("Route-B warp identity is malformed")
    return sequence


def validate_terminal(terminal: dict[str, Any]) -> None:
    if terminal.get("terminal_status") != "COMPLETE":
        raise RouteBContractError("Route-B producer terminal status is not COMPLETE")
    if terminal.get("overflow_count") != 0 or terminal.get("drop_count") != 0:
        raise RouteBContractError("Route-B producer overflow/drop is nonzero")


def validate_stream(events: Iterable[dict[str, Any]], whitelist: Iterable[WhitelistRow], terminal: dict[str, Any]) -> int:
    """Validate independent lane records without using adjacent order as grouping.

    Each dynamic warp instruction is grouped only by its explicit producer
    supplied ``warp_instruction_instance_id``.  This deliberately permits
    interleaving in OBSERVED_CALLBACK_ORDER while still rejecting a missing or
    duplicate executing lane in every instance.
    """
    frozen = validate_whitelist(whitelist)
    previous: int | None = None
    count = 0
    instances: dict[int, tuple[tuple[Any, ...], set[int], int]] = {}
    for event in events:
        previous = validate_event(event, frozen, previous_sequence=previous)
        instance = event["warp_instruction_instance_id"]
        signature = (event["kernel_launch_id"], tuple(event["cta"]), event["warp_id"], event["static_index"],
                     event["mref_ordinal"], event["instruction_offset"], event["opcode"], event["access_kind"],
                     event["width_bytes"], event["active_mask"], event["predicate_mask"], event["predicate_semantics"])
        expected = event["active_mask"] & event["predicate_mask"]
        if instance not in instances:
            instances[instance] = (signature, set(), expected)
        known_signature, lanes, known_expected = instances[instance]
        if signature != known_signature or expected != known_expected:
            raise RouteBContractError("Route-B LANE_EVENT instance identity is internally inconsistent")
        if event["lane_id"] in lanes:
            raise RouteBContractError("Route-B LANE_EVENT instance repeats an executing lane")
        lanes.add(event["lane_id"])
        count += 1
    for _, (_, lanes, expected) in instances.items():
        if lanes != set(_mask_lanes(expected)):
            raise RouteBContractError("Route-B LANE_EVENT instance is missing an executing lane")
    validate_terminal(terminal)
    return count
