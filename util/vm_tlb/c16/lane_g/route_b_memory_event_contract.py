#!/usr/bin/env python3
"""Fail-closed Route-B all-GLOBAL+MREF memory-event contract.

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


@dataclass(frozen=True)
class WhitelistRow:
    static_index: int
    opcode: str
    memory_space: str
    has_mref: bool
    access_kind: str
    width_bytes: int
    mref_ordinal: int


def validate_whitelist(rows: Iterable[WhitelistRow]) -> tuple[WhitelistRow, ...]:
    """Return the canonical whitelist or reject an unsafe/staticly ambiguous one."""
    result = tuple(rows)
    if not result:
        raise RouteBContractError("Route-B whitelist must contain at least one GLOBAL+MREF instruction")
    indices = [row.static_index for row in result]
    if indices != sorted(indices) or len(indices) != len(set(indices)):
        raise RouteBContractError("Route-B whitelist static indices must be sorted and unique")
    for row in result:
        if row.static_index < 0 or row.mref_ordinal < 0 or row.width_bytes <= 0:
            raise RouteBContractError("Route-B whitelist has an invalid static index, MREF ordinal, or width")
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
        "access_kind", "width_bytes", "memory_space", "active_mask", "predicate_mask",
        "active_lane_ids", "gpu_va_by_active_lane",
    }
    missing = sorted(required.difference(event))
    if missing:
        raise RouteBContractError("Route-B event misses required fields: " + ",".join(missing))
    sequence = event["observed_event_sequence"]
    if not isinstance(sequence, int) or sequence < 0 or (previous_sequence is not None and sequence <= previous_sequence):
        raise RouteBContractError("Route-B event sequence is not strictly monotonic")
    if event["sequence_label"] != OBSERVED_ORDER:
        raise RouteBContractError("Route-B event order must be labelled OBSERVED_CALLBACK_ORDER")
    allowed = {(row.static_index, row.mref_ordinal): row for row in whitelist}
    key = (event["static_index"], event["mref_ordinal"])
    row = allowed.get(key)
    if row is None:
        raise RouteBContractError("Route-B event static-index/MREF pair is outside the frozen whitelist")
    if event["memory_space"] != MEMORY_SPACE or event["access_kind"] != row.access_kind:
        raise RouteBContractError("Route-B event memory space/access kind differs from static whitelist")
    if event["opcode"] != row.opcode or event["width_bytes"] != row.width_bytes:
        raise RouteBContractError("Route-B event opcode/width differs from static whitelist")
    active_lanes = _mask_lanes(event["active_mask"])
    predicate_lanes = _mask_lanes(event["predicate_mask"])
    lane_ids = event["active_lane_ids"]
    addresses = event["gpu_va_by_active_lane"]
    if lane_ids != active_lanes or not isinstance(addresses, list) or len(addresses) != len(active_lanes):
        raise RouteBContractError("Route-B event active-mask popcount/lane/address serialization differs")
    if any(not isinstance(address, int) or address <= 0 for address in addresses):
        raise RouteBContractError("Route-B event contains a non-GPU-VA address")
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
    frozen = validate_whitelist(whitelist)
    previous: int | None = None
    count = 0
    for event in events:
        previous = validate_event(event, frozen, previous_sequence=previous)
        count += 1
    validate_terminal(terminal)
    return count
