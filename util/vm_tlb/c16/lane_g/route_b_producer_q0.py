#!/usr/bin/env python3
"""CPU-only admission helpers for the Route-B append-only producer."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from route_b_memory_event_contract import RouteBContractError, WhitelistRow, validate_whitelist


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise RouteBContractError(f"Route-B identity path is absent: {path}")
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def whitelist_sha256(rows: Iterable[WhitelistRow]) -> str:
    canonical = [asdict(row) for row in validate_whitelist(rows)]
    return sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class ProducerBinding:
    exact_function_mangled_name: str
    code_object_path: Path
    code_object_sha256: str
    static_map_path: Path
    static_map_sha256: str
    whitelist_sha256: str
    host_output_cap_bytes: int


def verify_binding(binding: ProducerBinding, whitelist: Iterable[WhitelistRow]) -> None:
    """Verify file and whitelist identities before any producer may be loaded."""
    if not binding.exact_function_mangled_name:
        raise RouteBContractError("Route-B binding lacks exact mangled function identity")
    for expected, actual, label in (
        (binding.code_object_sha256, sha256_file(binding.code_object_path), "code-object"),
        (binding.static_map_sha256, sha256_file(binding.static_map_path), "static-map"),
        (binding.whitelist_sha256, whitelist_sha256(whitelist), "whitelist"),
    ):
        if expected != actual:
            raise RouteBContractError(f"Route-B {label} SHA256 differs from the frozen binding")
    if binding.host_output_cap_bytes <= 0:
        raise RouteBContractError("Route-B host output cap must be positive")


def deterministic_partitions(static_indices: Iterable[int], max_indices_per_partition: int) -> tuple[tuple[int, ...], ...]:
    """Create contiguous sorted groups; reject an ambiguous/overlapping input."""
    indices = tuple(static_indices)
    if max_indices_per_partition <= 0 or not indices:
        raise RouteBContractError("Route-B partition requires positive cap and nonempty indices")
    if any(not isinstance(index, int) or index < 0 for index in indices):
        raise RouteBContractError("Route-B partition index is invalid")
    if indices != tuple(sorted(indices)) or len(indices) != len(set(indices)):
        raise RouteBContractError("Route-B partition input must be sorted and non-overlapping")
    return tuple(tuple(indices[start:start + max_indices_per_partition]) for start in range(0, len(indices), max_indices_per_partition))


def validate_partition_union(static_indices: Iterable[int], partitions: Iterable[Iterable[int]]) -> None:
    expected = tuple(static_indices)
    flattened = tuple(index for partition in partitions for index in partition)
    if flattened != expected or len(flattened) != len(set(flattened)):
        raise RouteBContractError("Route-B partition union differs from the frozen static-index set")
