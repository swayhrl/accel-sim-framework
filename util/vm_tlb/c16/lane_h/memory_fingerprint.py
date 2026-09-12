#!/usr/bin/env python3
"""Manifest-bound NVBit address decoding and conservative C16 fingerprints.

This module treats NVBit addresses as ``GPU_VA_OBSERVED``.  Its page buckets,
line buckets, and modulo line-set projections are structural properties of that
observed address stream, never hardware page mappings, PA facts, or TLB-miss
measurements.  A post-processed ``.traceg`` CTA file also has no global-L2
arrival order; the default order model is therefore ``SET_ONLY``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Iterator

try:  # Supports both ``python path/to/script.py`` and package imports in tests.
    from .runtime_object_map_v2 import (
        ObjectMapError,
        RuntimeObjectMapV2,
        sha256_file,
    )
except ImportError:  # pragma: no cover - exercised by the documented CLI path.
    from runtime_object_map_v2 import (  # type: ignore[no-redef]
        ObjectMapError,
        RuntimeObjectMapV2,
        sha256_file,
    )


TRACE_MANIFEST_SCHEMA = "c16-trace-manifest-v1"
ADDRESS_DOMAIN = "GPU_VA_OBSERVED"
CAPTURE_ADDRESS_DOMAINS = frozenset({"GPU_VA_OBSERVED", "MIXED_MEMORY_SPACE_OBSERVED"})
ORDER_MODELS = frozenset({"SET_ONLY", "LOCAL_STREAM_ORDER", "SYNTHETIC_INTERLEAVING_PROXY"})
CAPTURE_STATUSES = frozenset({"COMPLETE", "BOUNDED_PARTIAL"})
TERMINAL_STATUSES = frozenset({"COMPLETE", "PARTIAL_TERMINAL"})
TRACE_FORMATS = frozenset({"TRACEG", "RAW_CTA", "RAW_CTA_CORE", "RAW_CTA_LINEINFO", "RAW_CTA_CORE_LINEINFO"})
ACCESS_KINDS = frozenset({"READ", "WRITE", "ATOMIC", "UNKNOWN"})
TEMPORAL_STATUSES = frozenset({"BOUND", "UNPROVEN"})


class TraceParseError(ValueError):
    """A trace record cannot be decoded with frozen tracer semantics."""


class TraceManifestError(ValueError):
    """A capture is not safely consumable through the G→H exchange contract."""


def _decimal(value: str, name: str) -> int:
    try:
        return int(value, 10)
    except ValueError as error:
        raise TraceParseError(f"{name} is not decimal: {value!r}") from error


def _hex(value: str, name: str) -> int:
    try:
        return int(value, 16)
    except ValueError as error:
        raise TraceParseError(f"{name} is not hexadecimal: {value!r}") from error


def _integer(value: object, name: str) -> int:
    try:
        return int(value, 0) if isinstance(value, str) else int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise TraceManifestError(f"{name} must be an integer") from error


def _active_lanes(mask: int) -> list[int]:
    if mask < 0 or mask > 0xFFFFFFFF:
        raise TraceParseError("active mask must be a 32-bit unsigned value")
    return [lane for lane in range(32) if mask & (1 << lane)]


def access_kind(opcode: str) -> str:
    """Classify the SASS opcode conservatively at the requested access level."""
    tokens = [token.upper() for token in opcode.split(".") if token]
    base = tokens[0] if tokens else ""
    if "ATOM" in tokens or "RED" in tokens or base.startswith("ATOM") or base.startswith("RED"):
        return "ATOMIC"
    if base.startswith("LD") or base.endswith("LD") or base in {"TEX", "TLD", "SULD"}:
        return "READ"
    if base.startswith("ST") or base.endswith("ST") or base in {"SUST"}:
        return "WRITE"
    return "UNKNOWN"


def memory_space(opcode: str) -> str:
    """Infer only explicit SASS address-space mnemonics from the frozen trace.

    The current full tracer does not serialize an independent MREF space tag.
    Generic loads/stores, atomics, surfaces, and mixed instructions therefore
    remain UNKNOWN_SPACE instead of being promoted to GLOBAL by pattern.
    """
    base = opcode.split(".", 1)[0].upper()
    if base.startswith(("LDG", "STG")) and not base.startswith("LDGSTS"):
        return "GLOBAL"
    if base.startswith(("LDL", "STL")):
        return "LOCAL"
    if base.startswith(("LDS", "STS")):
        return "SHARED"
    return "UNKNOWN_SPACE"


def space_semantics(space: str) -> tuple[str, str]:
    """Return address domain and conservative TLB eligibility for one space."""
    if space == "GLOBAL":
        return ADDRESS_DOMAIN, "TRUE"
    if space == "LOCAL":
        return "GPU_LOCAL_ADDRESS_OBSERVED", "UNKNOWN"
    if space == "SHARED":
        return "GPU_SHARED_ADDRESS_OBSERVED", "FALSE"
    if space == "UNKNOWN_SPACE":
        return "UNKNOWN_ADDRESS_DOMAIN", "UNKNOWN"
    raise TraceParseError(f"unrecognized memory space: {space}")


@dataclass(frozen=True)
class LaneAccess:
    lane_id: int
    address: int
    width: int


@dataclass(frozen=True)
class MemoryEvent:
    source_record: int
    opcode: str
    access_kind: str
    active_mask: int
    width: int
    lanes: tuple[LaneAccess, ...]
    memory_space: str
    address_domain: str
    tlb_eligible: str
    trace_format: str
    cta: tuple[int, int, int] | None = None
    warp_in_cta: int | None = None


def _prefix_width(trace_format: str) -> int:
    widths = {
        "TRACEG": 0,
        "RAW_CTA": 4,
        "RAW_CTA_CORE": 6,
        "RAW_CTA_LINEINFO": 5,
        "RAW_CTA_CORE_LINEINFO": 7,
    }
    if trace_format not in widths:
        raise TraceParseError(f"unsupported trace format: {trace_format}")
    return widths[trace_format]


def is_metadata_line(line: str) -> bool:
    stripped = line.strip()
    return not stripped or stripped.startswith(("#", "-")) or stripped.startswith(("thread block =", "warp =", "insts ="))


def parse_trace_record(line: str, source_record: int, trace_format: str = "TRACEG") -> MemoryEvent | None:
    """Decode one frozen full-tracer record without dropping inactive-lane facts.

    The full tracer serializes addresses in increasing active-lane order.  The
    lane IDs are therefore reconstructed from the predicated mask, rather than
    assuming addresses belong to lanes ``0..popcount(mask)-1``.
    """
    tokens = line.split()
    prefix_width = _prefix_width(trace_format)
    if len(tokens) <= prefix_width:
        raise TraceParseError("truncated trace record before instruction fields")
    cta: tuple[int, int, int] | None = None
    warp: int | None = None
    if prefix_width:
        try:
            cta = tuple(_decimal(tokens[index], "cta coordinate") for index in range(3))  # type: ignore[assignment]
            warp = _decimal(tokens[3], "warp_in_cta")
        except IndexError as error:
            raise TraceParseError("truncated raw CTA prefix") from error
    index = prefix_width
    pc = _hex(tokens[index], "PC")
    del pc  # PC is not a stable cross-run identity, but validating it catches shifted formats.
    index += 1
    mask = _hex(tokens[index], "active mask")
    index += 1
    destination_count = _decimal(tokens[index], "destination register count")
    index += 1
    if destination_count < 0 or len(tokens) < index + destination_count + 2:
        raise TraceParseError("truncated destination/opcode fields")
    index += destination_count
    opcode = tokens[index]
    index += 1
    source_count = _decimal(tokens[index], "source register count")
    index += 1
    if source_count < 0 or len(tokens) < index + source_count + 1:
        raise TraceParseError("truncated source/width fields")
    index += source_count
    width = _decimal(tokens[index], "memory width")
    index += 1
    if width < 0:
        raise TraceParseError("memory width cannot be negative")
    if width == 0:
        # Current full tracer writes an immediate, while older frozen traceg
        # inputs may end at width.  Neither form carries a memory address.
        if len(tokens) == index + 1:
            _integer(tokens[index], "immediate")
        elif len(tokens) != index:
            raise TraceParseError("non-memory trace record has extra fields")
        return None

    lanes = _active_lanes(mask)
    if len(tokens) < index + 1:
        raise TraceParseError("memory trace record has no address-format field")
    address_format = _decimal(tokens[index], "address format")
    index += 1
    addresses: list[int]
    if address_format == 0:  # list_all
        if len(tokens) < index + len(lanes) + 1:
            raise TraceParseError("list-all trace record has fewer addresses than active lanes")
        addresses = [_hex(token, "lane address") for token in tokens[index:index + len(lanes)]]
        index += len(lanes)
    elif address_format == 1:  # base_stride
        if len(tokens) != index + 3:
            raise TraceParseError("base-stride trace record must contain base, stride, and immediate")
        base = _hex(tokens[index], "base address")
        stride = _decimal(tokens[index + 1], "address stride")
        addresses = [base + position * stride for position in range(len(lanes))]
        index += 2
    elif address_format == 2:  # base_delta
        if len(tokens) != index + len(lanes) + 1:
            raise TraceParseError("base-delta trace record has wrong delta/immediate count")
        if not lanes:
            raise TraceParseError("base-delta encoding cannot represent an empty predicated mask")
        addresses = [_hex(tokens[index], "base address")]
        index += 1
        for token in tokens[index:index + len(lanes) - 1]:
            addresses.append(addresses[-1] + _decimal(token, "address delta"))
        index += len(lanes) - 1
    else:
        raise TraceParseError(f"unknown NVBit address format: {address_format}")
    if any(address < 0 for address in addresses):
        raise TraceParseError("decoded a negative address")
    if len(addresses) != len(lanes):
        raise TraceParseError("decoded address count differs from active-lane count")
    if len(tokens) != index + 1:
        raise TraceParseError("memory trace record is missing/has extra immediate fields")
    _integer(tokens[index], "immediate")
    resolved_space = memory_space(opcode)
    resolved_domain, resolved_tlb_eligible = space_semantics(resolved_space)
    return MemoryEvent(
        source_record=source_record,
        opcode=opcode,
        access_kind=access_kind(opcode),
        active_mask=mask,
        width=width,
        lanes=tuple(LaneAccess(lane, address, width) for lane, address in zip(lanes, addresses)),
        memory_space=resolved_space,
        address_domain=resolved_domain,
        tlb_eligible=resolved_tlb_eligible,
        trace_format=trace_format,
        cta=cta,
        warp_in_cta=warp,
    )


def canonical_memory_event(event: MemoryEvent) -> dict[str, object]:
    """Stable full-tracer memory event used by the future observer GO gate."""
    return {
        "source_record": event.source_record,
        "opcode": event.opcode,
        "access_kind": event.access_kind,
        "memory_space": event.memory_space,
        "address_domain": event.address_domain,
        "tlb_eligible": event.tlb_eligible,
        "active_mask": f"0x{event.active_mask:08x}",
        "width": event.width,
        "lanes": [{"lane_id": lane.lane_id, "address": hex(lane.address)} for lane in event.lanes],
    }


def compare_memory_only_events(full_events: Iterable[MemoryEvent], observer_payload: dict[str, Any]) -> list[str]:
    """Return exact-equivalence failures; an empty list is only a schema gate.

    It intentionally does not declare the observer GO.  A real tiny-GPU run
    must additionally bind target filtering, terminal behavior, tool versions,
    and perturbation evidence before ``MEMORY_ONLY_AUDIT.md`` may change state.
    """
    expected = [canonical_memory_event(event) for event in full_events]
    actual = observer_payload.get("events")
    failures: list[str] = []
    if observer_payload.get("terminal_status") != "COMPLETE":
        failures.append("memory-only observer terminal_status is not COMPLETE")
    if not isinstance(actual, list):
        return failures + ["memory-only observer events is not a list"]
    if actual != expected:
        failures.append("memory-only events are not bit/exact canonical full-tracer events")
    return failures


@dataclass(frozen=True)
class ManifestEntry:
    run_id: str
    deployment_id: str
    scenario_id: str
    phase: str
    kernel_identity: str
    window_ordinal: int
    trace_path: Path
    trace_sha256: str
    capture_status: str
    terminal_status: str
    tool_version: str
    trace_format: str
    order_model: str
    source_receipt: str
    capture_address_domain: str
    object_map_sha256: str
    object_map_temporal_status: str
    object_map_snapshot_id: str | None
    object_map_event_ordinal_cutoff: int | None


def _required_string(raw: dict[str, Any], name: str) -> str:
    value = raw.get(name)
    if not isinstance(value, str) or not value:
        raise TraceManifestError(f"manifest entry field {name!r} must be a nonempty string")
    return value


def load_manifest(path: Path, expected_sha256: str) -> tuple[str, list[ManifestEntry]]:
    actual_sha = sha256_file(path)
    if actual_sha.lower() != expected_sha256.lower():
        raise TraceManifestError(f"manifest SHA256 mismatch: expected {expected_sha256}, got {actual_sha}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise TraceManifestError(f"invalid trace manifest JSON: {path}") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != TRACE_MANIFEST_SCHEMA:
        raise TraceManifestError(f"expected schema_version={TRACE_MANIFEST_SCHEMA}")
    entries_raw = payload.get("entries")
    if not isinstance(entries_raw, list) or not entries_raw:
        raise TraceManifestError("trace manifest entries must be a nonempty list")
    entries: list[ManifestEntry] = []
    seen_identity: set[tuple[str, int]] = set()
    for raw in entries_raw:
        if not isinstance(raw, dict):
            raise TraceManifestError("each manifest entry must be an object")
        capture_address_domain = raw.get("address_domain")
        if capture_address_domain not in CAPTURE_ADDRESS_DOMAINS:
            raise TraceManifestError("address_domain must be GPU_VA_OBSERVED or MIXED_MEMORY_SPACE_OBSERVED")
        capture_status = _required_string(raw, "capture_status")
        terminal_status = _required_string(raw, "terminal_status")
        if capture_status not in CAPTURE_STATUSES or terminal_status not in TERMINAL_STATUSES:
            raise TraceManifestError("invalid capture_status or terminal_status")
        if capture_status == "COMPLETE" and terminal_status != "COMPLETE":
            raise TraceManifestError("a COMPLETE capture must have a COMPLETE terminal status")
        order_model = _required_string(raw, "order_model")
        if order_model == "CTA_GROUP_FILE_ORDER":
            raise TraceManifestError("CTA-group file order must be declared SET_ONLY, never a global order model")
        if order_model not in ORDER_MODELS:
            raise TraceManifestError("unrecognized order_model")
        trace_format = raw.get("trace_format", "TRACEG")
        if trace_format not in TRACE_FORMATS:
            raise TraceManifestError("unrecognized trace_format")
        # Post-processed traceg is CTA-grouped.  A manifest assertion cannot
        # recover a local chronology that the format did not preserve.
        if trace_format == "TRACEG" and order_model != "SET_ONLY":
            raise TraceManifestError("TRACEG only admits SET_ONLY; a manifest cannot enable LOCAL_STREAM_ORDER")
        # This C16 schema has no qualified local-order producer.  A later
        # schema must define a supported format and hash-bound receipt before
        # it may admit LOCAL_STREAM_ORDER or a synthetic interleaving proxy.
        if order_model != "SET_ONLY":
            raise TraceManifestError("C16 trace-manifest-v1 currently admits SET_ONLY only")
        if "order_evidence_receipt" in raw:
            receipt = raw["order_evidence_receipt"]
            if not isinstance(receipt, str) or not receipt:
                raise TraceManifestError("order_evidence_receipt must be a nonempty receipt reference when present")
        object_map_sha256 = _required_string(raw, "object_map_sha256")
        if len(object_map_sha256) != 64 or any(char not in "0123456789abcdefABCDEF" for char in object_map_sha256):
            raise TraceManifestError("object_map_sha256 must be a SHA-256 hex digest")
        temporal_status = _required_string(raw, "object_map_temporal_status")
        if temporal_status not in TEMPORAL_STATUSES:
            raise TraceManifestError("object_map_temporal_status must be BOUND or UNPROVEN")
        snapshot_id_raw = raw.get("object_map_snapshot_id")
        cutoff_raw = raw.get("object_map_event_ordinal_cutoff")
        if temporal_status == "BOUND":
            if not isinstance(snapshot_id_raw, str) or not snapshot_id_raw:
                raise TraceManifestError("BOUND object-map attribution requires object_map_snapshot_id")
            cutoff = _integer(cutoff_raw, "object_map_event_ordinal_cutoff")
            if cutoff < 0:
                raise TraceManifestError("object_map_event_ordinal_cutoff must be nonnegative")
            snapshot_id: str | None = snapshot_id_raw
        else:
            if snapshot_id_raw not in (None, "UNPROVEN") or cutoff_raw is not None:
                raise TraceManifestError("UNPROVEN attribution must not claim a snapshot ID or ordinal cutoff")
            snapshot_id = None
            cutoff = None
        trace_path_raw = _required_string(raw, "trace_path")
        trace_path = Path(trace_path_raw)
        if not trace_path.is_absolute():
            trace_path = path.parent / trace_path
        entry = ManifestEntry(
            run_id=_required_string(raw, "run_id"),
            deployment_id=_required_string(raw, "deployment_id"),
            scenario_id=_required_string(raw, "scenario_id"),
            phase=_required_string(raw, "phase"),
            kernel_identity=_required_string(raw, "kernel_identity"),
            window_ordinal=_integer(raw.get("window_ordinal"), "window_ordinal"),
            trace_path=trace_path,
            trace_sha256=_required_string(raw, "trace_sha256"),
            capture_status=capture_status,
            terminal_status=terminal_status,
            tool_version=_required_string(raw, "tool_version"),
            trace_format=str(trace_format),
            order_model=order_model,
            source_receipt=_required_string(raw, "source_receipt"),
            capture_address_domain=str(capture_address_domain),
            object_map_sha256=object_map_sha256,
            object_map_temporal_status=temporal_status,
            object_map_snapshot_id=snapshot_id,
            object_map_event_ordinal_cutoff=cutoff,
        )
        if len(entry.trace_sha256) != 64 or any(char not in "0123456789abcdefABCDEF" for char in entry.trace_sha256):
            raise TraceManifestError("trace_sha256 must be a SHA-256 hex digest")
        identity = (entry.run_id, entry.window_ordinal)
        if identity in seen_identity:
            raise TraceManifestError("run_id + window_ordinal must be unique")
        seen_identity.add(identity)
        entries.append(entry)
    return actual_sha, entries


class IntervalUnion:
    """Exact union of byte intervals, retained to report structural occupancy."""

    def __init__(self) -> None:
        self.ranges: list[tuple[int, int]] = []

    def add(self, start: int, end_exclusive: int) -> None:
        if end_exclusive <= start:
            raise ValueError("interval must be nonempty")
        result: list[tuple[int, int]] = []
        inserted = False
        for current_start, current_end in self.ranges:
            if current_end < start:
                result.append((current_start, current_end))
            elif end_exclusive < current_start:
                if not inserted:
                    result.append((start, end_exclusive))
                    inserted = True
                result.append((current_start, current_end))
            else:
                start = min(start, current_start)
                end_exclusive = max(end_exclusive, current_end)
        if not inserted:
            result.append((start, end_exclusive))
        self.ranges = result

    @property
    def byte_count(self) -> int:
        return sum(end - start for start, end in self.ranges)


def _units(address: int, width: int, unit: int) -> range:
    return range(address // unit, (address + width - 1) // unit + 1)


@dataclass
class MetricAccumulator:
    event_ids: set[int] = field(default_factory=set)
    lane_references: int = 0
    requested_bytes: int = 0
    lines: set[int] = field(default_factory=set)
    sectors: set[int] = field(default_factory=set)
    pages_4k: set[int] = field(default_factory=set)
    pages_64k: set[int] = field(default_factory=set)
    modulo_line_set_projections: set[int] = field(default_factory=set)
    intervals: IntervalUnion = field(default_factory=IntervalUnion)
    prior_lines: set[int] = field(default_factory=set)
    local_line_revisit_references: int = 0
    local_page_revisit_references: int = 0
    prior_pages_4k: set[int] = field(default_factory=set)

    def add(
        self,
        event: MemoryEvent,
        lane: LaneAccess,
        modulo_projection_set_count: int | None,
        include_gpu_va_pages: bool,
        allow_local_order: bool,
    ) -> None:
        self.event_ids.add(event.source_record)
        self.lane_references += 1
        self.requested_bytes += lane.width
        self.intervals.add(lane.address, lane.address + lane.width)
        lines = list(_units(lane.address, lane.width, 128))
        pages_4k = list(_units(lane.address, lane.width, 4 * 1024)) if include_gpu_va_pages else []
        if allow_local_order and any(line in self.prior_lines for line in lines):
            self.local_line_revisit_references += 1
        if allow_local_order and any(page in self.prior_pages_4k for page in pages_4k):
            self.local_page_revisit_references += 1
        self.lines.update(lines)
        self.sectors.update(_units(lane.address, lane.width, 32))
        self.pages_4k.update(pages_4k)
        if include_gpu_va_pages:
            self.pages_64k.update(_units(lane.address, lane.width, 64 * 1024))
        self.prior_lines.update(lines)
        self.prior_pages_4k.update(pages_4k)
        if modulo_projection_set_count is not None and include_gpu_va_pages:
            self.modulo_line_set_projections.update(line % modulo_projection_set_count for line in lines)


@dataclass
class WindowResult:
    entry: ManifestEntry
    manifest_sha256: str
    parse_status: str
    malformed_terminal_record: str
    metrics: dict[tuple[str, str, str], MetricAccumulator]
    object_lines: dict[tuple[str, str], set[int]]
    object_pages_4k: dict[tuple[str, str], set[int]]
    object_pages_64k: dict[tuple[str, str], set[int]]
    zero_active_memory_events: int


def _open_text(path: Path):
    return lzma.open(path, "rt", encoding="utf-8", errors="strict") if path.suffix == ".xz" else path.open("rt", encoding="utf-8", errors="strict")


def _process_event(
    event: MemoryEvent,
    object_map: RuntimeObjectMapV2,
    object_map_cutoff: int | None,
    metrics: dict[tuple[str, str, str], MetricAccumulator],
    object_lines: dict[tuple[str, str], set[int]],
    object_pages_4k: dict[tuple[str, str], set[int]],
    object_pages_64k: dict[tuple[str, str], set[int]],
    modulo_projection_set_count: int | None,
    capture_address_domain: str,
    allow_local_order: bool,
) -> int:
    if not event.lanes:
        return 1
    if capture_address_domain == ADDRESS_DOMAIN and event.memory_space != "GLOBAL":
        raise TraceManifestError(
            "manifest claimed GPU_VA_OBSERVED-only capture but decoder observed a non-GLOBAL memory space"
        )
    for lane in event.lanes:
        # Runtime allocation ranges are GPU-global VA evidence.  They are not
        # allowed to classify LOCAL/SHARED/UNKNOWN-space addresses, even when
        # their numeric values happen to overlap a global allocation range.
        if event.memory_space == "GLOBAL" and object_map_cutoff is not None:
            object_class = object_map.classify(lane.address, lane.width, object_map_cutoff).object_class
        else:
            object_class = "UNKNOWN_RUNTIME"
        key = (object_class, event.access_kind, event.memory_space)
        accumulator = metrics.setdefault(key, MetricAccumulator())
        include_gpu_va_pages = event.memory_space == "GLOBAL"
        accumulator.add(event, lane, modulo_projection_set_count, include_gpu_va_pages, allow_local_order)
        object_key = (object_class, event.memory_space)
        object_lines.setdefault(object_key, set()).update(_units(lane.address, lane.width, 128))
        if include_gpu_va_pages:
            object_pages_4k.setdefault(object_key, set()).update(_units(lane.address, lane.width, 4 * 1024))
            object_pages_64k.setdefault(object_key, set()).update(_units(lane.address, lane.width, 64 * 1024))
    return 0


def fingerprint_entry(
    entry: ManifestEntry,
    manifest_sha256: str,
    object_map: RuntimeObjectMapV2,
    modulo_projection_set_count: int | None,
) -> WindowResult:
    if not entry.trace_path.is_file():
        raise TraceManifestError(f"trace path does not exist: {entry.trace_path}")
    observed_sha = sha256_file(entry.trace_path)
    if observed_sha.lower() != entry.trace_sha256.lower():
        raise TraceManifestError(f"trace SHA256 mismatch for {entry.trace_path}: expected {entry.trace_sha256}, got {observed_sha}")
    if object_map.source_sha256 is None:
        raise TraceManifestError("object map must be loaded from an immutable file to verify object_map_sha256")
    if object_map.source_sha256.lower() != entry.object_map_sha256.lower():
        raise TraceManifestError(
            f"object-map SHA256 mismatch for window {entry.window_ordinal}: "
            f"expected {entry.object_map_sha256}, got {object_map.source_sha256}"
        )
    object_map_cutoff = (
        object_map.resolve_snapshot(entry.object_map_snapshot_id, entry.object_map_event_ordinal_cutoff)
        if entry.object_map_temporal_status == "BOUND"
        else None
    )
    metrics: dict[tuple[str, str, str], MetricAccumulator] = {}
    object_lines: dict[tuple[str, str], set[int]] = {}
    object_pages_4k: dict[tuple[str, str], set[int]] = {}
    object_pages_64k: dict[tuple[str, str], set[int]] = {}
    zero_active_memory_events = 0
    last_data: tuple[int, str] | None = None

    def process(record: tuple[int, str]) -> None:
        nonlocal zero_active_memory_events
        line_number, raw = record
        try:
            event = parse_trace_record(raw, line_number, entry.trace_format)
        except TraceParseError as error:
            raise TraceParseError(f"{entry.trace_path}:{line_number}: {error}") from error
        if event is not None:
            zero_active_memory_events += _process_event(
                event, object_map, object_map_cutoff, metrics, object_lines, object_pages_4k, object_pages_64k,
                modulo_projection_set_count, entry.capture_address_domain, False,
            )

    with _open_text(entry.trace_path) as source:
        for line_number, raw in enumerate(source, start=1):
            if is_metadata_line(raw):
                continue
            if last_data is not None:
                process(last_data)
            last_data = (line_number, raw)
    parse_status = "COMPLETE"
    malformed_terminal_record = ""
    if last_data is not None:
        try:
            process(last_data)
        except TraceParseError as error:
            if entry.capture_status != "BOUNDED_PARTIAL":
                raise
            parse_status = "PARTIAL_TERMINAL"
            malformed_terminal_record = str(error)
    if entry.capture_status == "COMPLETE" and parse_status != "COMPLETE":
        raise TraceManifestError("complete capture cannot have a malformed terminal trace record")
    if entry.terminal_status == "PARTIAL_TERMINAL" and parse_status != "PARTIAL_TERMINAL":
        raise TraceManifestError("manifest says PARTIAL_TERMINAL but terminal record decoded completely")
    if entry.terminal_status == "COMPLETE" and parse_status != "COMPLETE":
        raise TraceManifestError("manifest says COMPLETE but terminal record is malformed")
    return WindowResult(entry, manifest_sha256, parse_status, malformed_terminal_record, metrics,
                        object_lines, object_pages_4k, object_pages_64k, zero_active_memory_events)


FINGERPRINT_COLUMNS = [
    "manifest_sha256", "trace_sha256", "object_map_sha256", "object_map_temporal_status", "object_map_snapshot_id",
    "object_map_event_ordinal_cutoff", "run_id", "deployment_id", "scenario_id", "phase", "kernel_identity",
    "window_ordinal", "memory_space", "address_domain", "tlb_eligible", "evidence_tier", "capture_status",
    "terminal_status", "parse_status", "order_model", "object_class", "access_kind", "memory_event_count", "lane_references", "requested_bytes",
    "unique_byte_footprint", "unique_4k_va_buckets", "unique_64k_va_buckets", "unique_128b_lines",
    "unique_32b_sectors", "sector_utilization_proxy", "modulo_projection_set_count", "unique_modulo_set_projections",
    "page_occupancy_bytes_proxy", "line_occupancy_bytes_proxy", "contiguous_virtual_range_count",
    "contiguous_virtual_range_mean_bytes", "contiguous_virtual_range_max_bytes", "local_line_revisit_references",
    "local_page_revisit_references", "zero_active_memory_events", "source_receipt",
]


def _number_or_na(value: int | None) -> str | int:
    return "NA" if value is None else value


def fingerprint_rows(
    result: WindowResult,
    modulo_projection_set_count: int | None,
) -> Iterator[dict[str, str | int | float]]:
    entry = result.entry
    for (object_class, kind, space), accumulator in sorted(result.metrics.items()):
        unique_bytes = accumulator.intervals.byte_count
        contiguous_lengths = [end - start for start, end in accumulator.intervals.ranges]
        line_count = len(accumulator.lines)
        page_count = len(accumulator.pages_4k)
        address_domain, tlb_eligible = space_semantics(space)
        gpu_va_page_metric = space == "GLOBAL"
        yield {
            "manifest_sha256": result.manifest_sha256,
            "trace_sha256": entry.trace_sha256,
            "object_map_sha256": entry.object_map_sha256,
            "object_map_temporal_status": entry.object_map_temporal_status,
            "object_map_snapshot_id": entry.object_map_snapshot_id or "NA",
            "object_map_event_ordinal_cutoff": _number_or_na(entry.object_map_event_ordinal_cutoff),
            "run_id": entry.run_id,
            "deployment_id": entry.deployment_id,
            "scenario_id": entry.scenario_id,
            "phase": entry.phase,
            "kernel_identity": entry.kernel_identity,
            "window_ordinal": entry.window_ordinal,
            "memory_space": space,
            "address_domain": address_domain,
            "tlb_eligible": tlb_eligible,
            "evidence_tier": "TRACE_DERIVED_STRUCTURAL",
            "capture_status": entry.capture_status,
            "terminal_status": entry.terminal_status,
            "parse_status": result.parse_status,
            "order_model": entry.order_model,
            "object_class": object_class,
            "access_kind": kind,
            "memory_event_count": len(accumulator.event_ids),
            "lane_references": accumulator.lane_references,
            "requested_bytes": accumulator.requested_bytes,
            "unique_byte_footprint": unique_bytes,
            "unique_4k_va_buckets": page_count if gpu_va_page_metric else "NA",
            "unique_64k_va_buckets": len(accumulator.pages_64k) if gpu_va_page_metric else "NA",
            "unique_128b_lines": line_count,
            "unique_32b_sectors": len(accumulator.sectors),
            "sector_utilization_proxy": (len(accumulator.sectors) / (4 * line_count)) if line_count else 0.0,
            "modulo_projection_set_count": _number_or_na(modulo_projection_set_count if gpu_va_page_metric else None),
            "unique_modulo_set_projections": _number_or_na(
                len(accumulator.modulo_line_set_projections)
                if modulo_projection_set_count is not None and gpu_va_page_metric else None
            ),
            "page_occupancy_bytes_proxy": (unique_bytes / page_count) if page_count and gpu_va_page_metric else "NA",
            "line_occupancy_bytes_proxy": (unique_bytes / line_count) if line_count else 0.0,
            "contiguous_virtual_range_count": len(contiguous_lengths),
            "contiguous_virtual_range_mean_bytes": statistics.mean(contiguous_lengths) if contiguous_lengths else 0.0,
            "contiguous_virtual_range_max_bytes": max(contiguous_lengths, default=0),
            "local_line_revisit_references": "NA",
            "local_page_revisit_references": "NA",
            "zero_active_memory_events": result.zero_active_memory_events,
            "source_receipt": entry.source_receipt,
        }


VALIDATION_COLUMNS = [
    "manifest_sha256", "run_id", "window_ordinal", "trace_sha256", "object_map_sha256", "object_map_temporal_status",
    "object_map_snapshot_id", "object_map_event_ordinal_cutoff", "capture_status", "terminal_status", "parse_status",
    "address_domain", "order_model", "sha256_verified", "object_boundary_policy", "result",
    "detail",
]


def validation_row(result: WindowResult) -> dict[str, str | int]:
    detail = result.malformed_terminal_record or "manifest SHA, trace SHA, format, and terminal contract verified"
    return {
        "manifest_sha256": result.manifest_sha256,
        "run_id": result.entry.run_id,
        "window_ordinal": result.entry.window_ordinal,
        "trace_sha256": result.entry.trace_sha256,
        "object_map_sha256": result.entry.object_map_sha256,
        "object_map_temporal_status": result.entry.object_map_temporal_status,
        "object_map_snapshot_id": result.entry.object_map_snapshot_id or "NA",
        "object_map_event_ordinal_cutoff": _number_or_na(result.entry.object_map_event_ordinal_cutoff),
        "capture_status": result.entry.capture_status,
        "terminal_status": result.entry.terminal_status,
        "parse_status": result.parse_status,
        "address_domain": ADDRESS_DOMAIN,
        "order_model": result.entry.order_model,
        "sha256_verified": "PASS",
        "object_boundary_policy": (
            "FULL_ACCESS_SINGLE_LIVE_STORAGE_AT_BOUND_SNAPSHOT_ELSE_UNKNOWN_RUNTIME"
            if result.entry.object_map_temporal_status == "BOUND"
            else "TEMPORAL_UNPROVEN_FORCED_UNKNOWN_RUNTIME"
        ),
        "result": "STRUCTURAL_ONLY" if result.entry.capture_status == "BOUNDED_PARTIAL" else "PASS",
        "detail": detail,
    }


REUSE_COLUMNS = [
    "manifest_sha256", "run_id", "deployment_id", "scenario_id", "phase", "previous_window_ordinal",
    "current_window_ordinal", "object_class", "memory_space", "address_domain", "tlb_eligible", "metric", "order_model", "intersection_count",
    "previous_count", "current_count", "union_count", "jaccard", "evidence_tier", "limitation",
]


def reuse_rows(results: Iterable[WindowResult]) -> Iterator[dict[str, str | int | float]]:
    groups: dict[tuple[str, str, str, str], list[WindowResult]] = {}
    for result in results:
        entry = result.entry
        groups.setdefault((entry.run_id, entry.deployment_id, entry.scenario_id, entry.phase), []).append(result)
    for (run_id, deployment_id, scenario_id, phase), windows in sorted(groups.items()):
        windows.sort(key=lambda item: item.entry.window_ordinal)
        for previous, current in zip(windows, windows[1:]):
            object_spaces = set(previous.object_lines) | set(current.object_lines)
            for object_class, space in sorted(object_spaces):
                address_domain, tlb_eligible = space_semantics(space)
                metric_sets: list[tuple[str, set[int], set[int]]] = [
                    ("UNIQUE_128B_LINE_SET", previous.object_lines.get((object_class, space), set()), current.object_lines.get((object_class, space), set())),
                ]
                if space == "GLOBAL":
                    metric_sets.extend((
                        ("UNIQUE_4K_VA_BUCKET_SET", previous.object_pages_4k.get((object_class, space), set()), current.object_pages_4k.get((object_class, space), set())),
                        ("UNIQUE_64K_VA_BUCKET_SET", previous.object_pages_64k.get((object_class, space), set()), current.object_pages_64k.get((object_class, space), set())),
                    ))
                for metric, prior_values, current_values in metric_sets:
                    intersection = len(prior_values & current_values)
                    union = len(prior_values | current_values)
                    yield {
                        "manifest_sha256": current.manifest_sha256,
                        "run_id": run_id,
                        "deployment_id": deployment_id,
                        "scenario_id": scenario_id,
                        "phase": phase,
                        "previous_window_ordinal": previous.entry.window_ordinal,
                        "current_window_ordinal": current.entry.window_ordinal,
                        "object_class": object_class,
                        "memory_space": space,
                        "address_domain": address_domain,
                        "tlb_eligible": tlb_eligible,
                        "metric": metric,
                        "order_model": "SET_ONLY",
                        "intersection_count": intersection,
                        "previous_count": len(prior_values),
                        "current_count": len(current_values),
                        "union_count": union,
                        "jaccard": (intersection / union) if union else 0.0,
                        "evidence_tier": "TRACE_DERIVED_STRUCTURAL",
                        "limitation": "set overlap only; CTA-group file order is not global L2 order",
                    }


def write_tsv(path: Path, columns: list[str], rows: Iterable[dict[str, object]]) -> None:
    if path.exists():
        raise FileExistsError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute conservative C16 H page/line/object fingerprints from fixed G manifests.")
    parser.add_argument("--trace-manifest", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True,
                        help="SHA256 pinned in the committed G publish manifest/receipt")
    parser.add_argument("--object-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="fresh MEMORY_FINGERPRINTS.tsv")
    parser.add_argument("--validation-output", type=Path, required=True, help="fresh FINGERPRINT_VALIDATION.tsv")
    parser.add_argument("--reuse-output", type=Path, required=True, help="fresh REUSE_AND_OVERLAP.tsv")
    parser.add_argument("--modulo-projection-set-count", type=int, default=None,
                        help="optional line %% set-count projection proxy; never a measured hardware cache-set mapping")
    args = parser.parse_args()
    if args.modulo_projection_set_count is not None and args.modulo_projection_set_count <= 0:
        parser.error("--modulo-projection-set-count must be positive")
    try:
        manifest_sha, entries = load_manifest(args.trace_manifest, args.expected_manifest_sha256)
        object_map = RuntimeObjectMapV2.from_file(args.object_map)
        results = [fingerprint_entry(entry, manifest_sha, object_map, args.modulo_projection_set_count) for entry in entries]
        rows = [row for result in results for row in fingerprint_rows(result, args.modulo_projection_set_count)]
        write_tsv(args.output, FINGERPRINT_COLUMNS, rows)
        write_tsv(args.validation_output, VALIDATION_COLUMNS, (validation_row(result) for result in results))
        write_tsv(args.reuse_output, REUSE_COLUMNS, reuse_rows(results))
    except (ObjectMapError, TraceParseError, TraceManifestError, OSError, ValueError) as error:
        raise SystemExit(f"FAIL c16-memory-fingerprint: {error}") from error
    print(f"PASS c16-memory-fingerprint manifest_sha256={manifest_sha} windows={len(results)} rows={len(rows)}")


if __name__ == "__main__":
    main()
