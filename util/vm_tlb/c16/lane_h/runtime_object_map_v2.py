#!/usr/bin/env python3
"""Conservative Runtime Object Map V2.

The map is deliberately an attribution index, not an allocator model.  It only
classifies an access when one directly observed, live storage generation fully
contains the whole access.  Ambiguous, boundary-spanning, released, or absent
ranges are ``UNKNOWN_RUNTIME``; they are never guessed to be Activations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "c16-runtime-object-map-v2"
OBJECT_CLASSES = frozenset({"WEIGHT", "QUANT_METADATA", "KV_CACHE", "UNKNOWN_RUNTIME"})
EVENT_TYPES = frozenset({"ALLOCATE", "VIEW", "GROW", "REPLACE", "RELEASE"})
ORDER_EVIDENCE = frozenset({"HOST_ISSUE_ORDER", "CUDA_EVENT", "UNKNOWN_ORDER"})
RELEASE_EVIDENCE = frozenset({"CUDA_FREE", "RUNTIME_RELEASE", "ALLOCATOR_RELEASE"})


class ObjectMapError(ValueError):
    """The supplied runtime evidence cannot support a safe attribution."""


def _integer(value: object, field_name: str) -> int:
    try:
        if isinstance(value, str):
            return int(value, 0)
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ObjectMapError(f"{field_name} must be an integer or base-prefixed string") from error


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class Range:
    start: int
    end_exclusive: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end_exclusive <= self.start:
            raise ObjectMapError("range must be nonempty and nonnegative")

    def contains(self, address: int, width: int) -> bool:
        return self.start <= address and address + width <= self.end_exclusive

    def intersects(self, address: int, width: int) -> bool:
        return max(self.start, address) < min(self.end_exclusive, address + width)


@dataclass
class StorageGeneration:
    storage_id: str
    generation: int
    object_class: str
    allocation: Range
    allocated_ordinal: int
    views: list[Range] = field(default_factory=list)
    released_ordinal: int | None = None
    replacement_without_release: bool = False

    @property
    def key(self) -> tuple[str, int]:
        return self.storage_id, self.generation

    def is_live_at(self, ordinal: int | None) -> bool:
        if ordinal is not None and ordinal < self.allocated_ordinal:
            return False
        return self.released_ordinal is None or (ordinal is not None and ordinal < self.released_ordinal)

    def status_at(self, ordinal: int | None = None) -> str:
        if not self.is_live_at(ordinal):
            return "RELEASED"
        if self.replacement_without_release:
            return "UNKNOWN_ACTIVE"
        return "ACTIVE"

    def all_ranges(self) -> Iterable[Range]:
        # Allocation is a direct storage range.  Views are retained for audit
        # and do not turn tied/shared storage into duplicate payload.
        yield self.allocation
        yield from self.views


@dataclass(frozen=True)
class Classification:
    object_class: str
    storage_id: str | None
    generation: int | None
    reason: str


class RuntimeObjectMapV2:
    """Validated event history plus a conservative point-in-time range index."""

    def __init__(self, events: list[dict[str, Any]]) -> None:
        self._records: dict[tuple[str, int], StorageGeneration] = {}
        self._event_count = 0
        previous_ordinal = -1
        for raw_event in events:
            ordinal = self._validate_common(raw_event)
            if ordinal <= previous_ordinal:
                raise ObjectMapError("event_ordinal must be strictly increasing")
            previous_ordinal = ordinal
            self._apply(raw_event, ordinal)
            self._event_count += 1

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RuntimeObjectMapV2":
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise ObjectMapError(f"expected schema_version={SCHEMA_VERSION}")
        events = payload.get("events")
        if not isinstance(events, list) or not events:
            raise ObjectMapError("events must be a nonempty list")
        return cls(events)

    @classmethod
    def from_file(cls, path: Path) -> "RuntimeObjectMapV2":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ObjectMapError(f"invalid JSON: {path}") from error
        if not isinstance(payload, dict):
            raise ObjectMapError("object-map root must be an object")
        return cls.from_payload(payload)

    @staticmethod
    def _range(event: dict[str, Any], prefix: str = "range") -> Range:
        return Range(
            _integer(event.get(f"{prefix}_start"), f"{prefix}_start"),
            _integer(event.get(f"{prefix}_end_exclusive"), f"{prefix}_end_exclusive"),
        )

    @staticmethod
    def _key(event: dict[str, Any]) -> tuple[str, int]:
        storage_id = event.get("storage_id")
        if not isinstance(storage_id, str) or not storage_id:
            raise ObjectMapError("storage_id must be a nonempty string")
        generation = _integer(event.get("generation"), "generation")
        if generation < 0:
            raise ObjectMapError("generation must be nonnegative")
        return storage_id, generation

    @staticmethod
    def _object_class(event: dict[str, Any]) -> str:
        object_class = event.get("object_class")
        if object_class not in OBJECT_CLASSES:
            raise ObjectMapError(
                "object_class must be WEIGHT, QUANT_METADATA, KV_CACHE, or UNKNOWN_RUNTIME; "
                "ACTIVATION/WORKSPACE require a separately authorized schema revision"
            )
        return str(object_class)

    @staticmethod
    def _evidence(event: dict[str, Any]) -> str:
        evidence = event.get("allocation_evidence")
        if not isinstance(evidence, str) or not evidence:
            raise ObjectMapError("allocation_evidence must name direct runtime evidence")
        if "PYTHON" in evidence.upper() or "GC" in evidence.upper():
            raise ObjectMapError("Python object destruction/GC is not GPU allocation or release evidence")
        return evidence

    def _validate_common(self, event: dict[str, Any]) -> int:
        if not isinstance(event, dict):
            raise ObjectMapError("each event must be an object")
        if event.get("event_type") not in EVENT_TYPES:
            raise ObjectMapError(f"unknown event_type: {event.get('event_type')!r}")
        self._key(event)
        ordinal = _integer(event.get("event_ordinal"), "event_ordinal")
        if ordinal < 0:
            raise ObjectMapError("event_ordinal must be nonnegative")
        for required in ("stream_id", "context_id", "timestamp_ns", "order_evidence"):
            if required not in event:
                raise ObjectMapError(f"missing required event field: {required}")
        _integer(event["timestamp_ns"], "timestamp_ns")
        if event["order_evidence"] not in ORDER_EVIDENCE:
            raise ObjectMapError("order_evidence must preserve or explicitly mark ordering uncertainty")
        self._evidence(event)
        return ordinal

    def _new_record(self, event: dict[str, Any], ordinal: int) -> StorageGeneration:
        key = self._key(event)
        if key in self._records and self._records[key].released_ordinal is None:
            raise ObjectMapError(f"storage/generation is already live: {key}")
        record = StorageGeneration(
            storage_id=key[0],
            generation=key[1],
            object_class=self._object_class(event),
            allocation=self._range(event),
            allocated_ordinal=ordinal,
        )
        # The allocation itself is a directly observed view; a narrower view
        # may be added later without double-counting tied/shared storage.
        record.views.append(record.allocation)
        self._records[key] = record
        return record

    def _live_record(self, event: dict[str, Any]) -> StorageGeneration:
        key = self._key(event)
        record = self._records.get(key)
        if record is None or record.released_ordinal is not None:
            raise ObjectMapError(f"event refers to no live storage/generation: {key}")
        return record

    def _apply(self, event: dict[str, Any], ordinal: int) -> None:
        event_type = event["event_type"]
        if event_type == "ALLOCATE":
            self._new_record(event, ordinal)
            return
        if event_type == "REPLACE":
            replaces = event.get("replaces")
            if not isinstance(replaces, dict):
                raise ObjectMapError("REPLACE requires a replaces {storage_id,generation} record")
            old_key = self._key(replaces)
            old = self._records.get(old_key)
            if old is None:
                raise ObjectMapError("REPLACE predecessor has not been allocated")
            # Replacement does not prove a GPU free.  The predecessor remains
            # in the live index and is deliberately marked ambiguous-active.
            if old.released_ordinal is None:
                old.replacement_without_release = True
            self._new_record(event, ordinal)
            return
        record = self._live_record(event)
        if event_type == "VIEW":
            view = self._range(event, "view")
            if not record.allocation.contains(view.start, view.end_exclusive - view.start):
                raise ObjectMapError("VIEW must fall inside the directly observed allocation")
            record.views.append(view)
            return
        if event_type == "GROW":
            grown = self._range(event)
            if grown.start > record.allocation.start or grown.end_exclusive < record.allocation.end_exclusive:
                raise ObjectMapError("GROW range must contain the prior allocation range")
            record.allocation = grown
            record.views.append(grown)
            return
        if event_type == "RELEASE":
            release_evidence = event.get("release_evidence")
            if release_evidence not in RELEASE_EVIDENCE:
                raise ObjectMapError("RELEASE requires direct CUDA/runtime/allocator release evidence")
            record.released_ordinal = ordinal
            return
        raise AssertionError(f"unhandled event type: {event_type}")

    @property
    def event_count(self) -> int:
        return self._event_count

    def records(self) -> list[StorageGeneration]:
        return sorted(self._records.values(), key=lambda item: item.key)

    def classify(self, address: int, width: int, event_ordinal: int | None = None) -> Classification:
        if address < 0 or width <= 0:
            raise ObjectMapError("address must be nonnegative and width must be positive")
        complete: dict[tuple[str, int], StorageGeneration] = {}
        touching = False
        for record in self._records.values():
            if not record.is_live_at(event_ordinal):
                continue
            for observed_range in record.all_ranges():
                if observed_range.intersects(address, width):
                    touching = True
                if observed_range.contains(address, width):
                    complete[record.key] = record
        if len(complete) == 1 and not (touching and not complete):
            record = next(iter(complete.values()))
            # A range that fully contains the access wins only if no other
            # live storage has an overlapping part of it.
            overlapping_keys = {
                item.key
                for item in self._records.values()
                if item.is_live_at(event_ordinal)
                and any(candidate.intersects(address, width) for candidate in item.all_ranges())
            }
            if overlapping_keys == {record.key}:
                return Classification(record.object_class, record.storage_id, record.generation, "EXACT_LIVE_RANGE")
        if complete:
            return Classification("UNKNOWN_RUNTIME", None, None, "MULTIPLE_OR_OVERLAPPING_STORAGE")
        if touching:
            return Classification("UNKNOWN_RUNTIME", None, None, "RANGE_BOUNDARY_CROSSING")
        return Classification("UNKNOWN_RUNTIME", None, None, "NO_LIVE_DIRECT_RUNTIME_RANGE")

    def audit_rows(self) -> list[dict[str, object]]:
        rows: list[dict[str, object]] = []
        for record in self.records():
            rows.append({
                "storage_id": record.storage_id,
                "generation": record.generation,
                "object_class": record.object_class,
                "allocation_start": hex(record.allocation.start),
                "allocation_end_exclusive": hex(record.allocation.end_exclusive),
                "view_count": len(record.views),
                "state": record.status_at(),
                "released_ordinal": record.released_ordinal,
                "release_proven": record.released_ordinal is not None,
            })
        return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and audit a C16 Runtime Object Map V2 JSON payload.")
    parser.add_argument("--object-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    object_map = RuntimeObjectMapV2.from_file(args.object_map)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "object_map_sha256": sha256_file(args.object_map),
        "event_count": object_map.event_count,
        "records": object_map.audit_rows(),
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS runtime_object_map_v2 records={len(payload['records'])} output={args.output}")


if __name__ == "__main__":
    main()
