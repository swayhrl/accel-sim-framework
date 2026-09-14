#!/usr/bin/env python3
"""Fail-closed CPU selection for the pre-outcome Route-B map pipeline.

This module deliberately consumes compact map *summaries*, never address
events.  A request that cannot be identity-resolved is terminally
``FAILED_CLOSED`` and is never replaced by a short-name match.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


class RouteBSelectionError(ValueError):
    """Raised when a request/map cannot lawfully enter Route-B selection."""


def _sha256(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise RouteBSelectionError(f"{field} must be a lowercase SHA256")
    return value


def _geometry_product(value: object, field: str) -> int:
    if not isinstance(value, str):
        raise RouteBSelectionError(f"{field} must use AxBxC geometry")
    parts = value.split("x")
    if len(parts) != 3:
        raise RouteBSelectionError(f"{field} must use AxBxC geometry")
    try:
        dimensions = [int(part) for part in parts]
    except ValueError as exc:
        raise RouteBSelectionError(f"{field} contains a non-integer dimension") from exc
    if any(dimension <= 0 for dimension in dimensions):
        raise RouteBSelectionError(f"{field} dimensions must be positive")
    return dimensions[0] * dimensions[1] * dimensions[2]


def _request_key(request: dict[str, Any]) -> tuple[str, str, str, str, str]:
    required = ("phase", "exact_full_function", "grid", "block", "shape_key", "dtype_key")
    if any(not isinstance(request.get(field), str) or not request[field] for field in required):
        raise RouteBSelectionError("map request lacks exact phase/function/geometry/shape identity")
    return tuple(request[field] for field in required)  # type: ignore[return-value]


def _rank_key(item: dict[str, Any], metric: str) -> tuple[object, ...]:
    return (-item[metric], item["exact_full_function"], item["grid"], item["block"], item["shape_key"], item["dtype_key"])


def freeze_final_selection(request_document: dict[str, Any], map_summaries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Freeze duration U memory-proxy Route-B selection from terminal map summaries.

    Each requested identity must appear exactly once with terminal status
    ``MAPPED_EXACT`` or ``FAILED_CLOSED``.  No GPU VA, locality, cache, or TLB
    field is accepted in a summary.
    """
    requests = request_document.get("requests")
    if not isinstance(requests, list) or not requests:
        raise RouteBSelectionError("request document has no map requests")
    request_by_id: dict[str, dict[str, Any]] = {}
    for request in requests:
        if not isinstance(request, dict) or not isinstance(request.get("request_id"), str):
            raise RouteBSelectionError("map request has no request_id")
        request_id = request["request_id"]
        if request_id in request_by_id:
            raise RouteBSelectionError("map request IDs must be unique")
        _request_key(request)
        _sha256(request.get("source_catalog_sha"), "source_catalog_sha")
        if request.get("known_mangled_name") != "MAP_DISCOVERY_REQUIRED":
            raise RouteBSelectionError("first Route-B map batch must require mangled-name discovery")
        request_by_id[request_id] = request

    summaries_by_id: dict[str, dict[str, Any]] = {}
    forbidden = {"gpu_va", "gpu_va_by_active_lane", "address", "locality", "cache_outcome", "tlb_outcome"}
    for summary in map_summaries:
        if not isinstance(summary, dict) or any(field in summary for field in forbidden):
            raise RouteBSelectionError("map summary includes forbidden address/outcome data")
        request_id = summary.get("request_id")
        if not isinstance(request_id, str) or request_id not in request_by_id or request_id in summaries_by_id:
            raise RouteBSelectionError("map summary request_id is unknown or duplicated")
        status = summary.get("status")
        if status not in {"MAPPED_EXACT", "FAILED_CLOSED"}:
            raise RouteBSelectionError("map summary is not terminal")
        summaries_by_id[request_id] = summary
    if set(summaries_by_id) != set(request_by_id):
        raise RouteBSelectionError("final selection requires terminal map summary for every requested identity")

    mapped: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for request_id, request in request_by_id.items():
        summary = summaries_by_id[request_id]
        if summary["status"] == "FAILED_CLOSED":
            reason = summary.get("failure_reason")
            if not isinstance(reason, str) or not reason:
                raise RouteBSelectionError("failed map summary lacks failure_reason")
            failures.append({"request_id": request_id, "failure_reason": reason})
            continue
        for field in ("exact_full_function", "grid", "block", "shape_key", "dtype_key"):
            if summary.get(field) != request[field]:
                raise RouteBSelectionError("mapped summary differs from frozen request identity")
        mangled = summary.get("function_mangled_name")
        if not isinstance(mangled, str) or not mangled:
            raise RouteBSelectionError("mapped summary did not resolve the exact mangled function")
        static_count = summary.get("static_global_mref_count")
        if not isinstance(static_count, int) or static_count <= 0:
            raise RouteBSelectionError("mapped summary has no GLOBAL+MREF instructions")
        map_sha = _sha256(summary.get("static_map_sha256"), "static_map_sha256")
        code_sha = _sha256(summary.get("code_object_sha256"), "code_object_sha256")
        cta_count = _geometry_product(request["grid"], "grid")
        warps_per_cta = (_geometry_product(request["block"], "block") + 31) // 32
        row = dict(request)
        row.update({
            "function_mangled_name": mangled,
            "static_map_sha256": map_sha,
            "code_object_sha256": code_sha,
            "static_global_mref_count": static_count,
            "cta_count": cta_count,
            "warps_per_cta": warps_per_cta,
            "memory_proxy": request["launch_count"] * cta_count * warps_per_cta * static_count,
        })
        mapped.append(row)

    if not mapped:
        raise RouteBSelectionError("all Route-B map candidates failed closed")
    by_phase: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in mapped:
        by_phase[row["phase"]].append(row)
    phase_results: dict[str, Any] = {}
    selected_ids: set[str] = set()
    for phase, rows in sorted(by_phase.items()):
        duration_ranked = sorted(rows, key=lambda row: _rank_key(row, "phase_duration_ns"))
        proxy_ranked = sorted(rows, key=lambda row: _rank_key(row, "memory_proxy"))
        proxy_total = sum(row["memory_proxy"] for row in proxy_ranked)
        cutoff = 0
        proxy_selected: list[str] = []
        for row in proxy_ranked:
            cutoff += row["memory_proxy"]
            proxy_selected.append(row["request_id"])
            if cutoff / proxy_total >= 0.8:
                break
        duration_selected = [row["request_id"] for row in duration_ranked]
        final_ids = sorted(set(duration_selected).union(proxy_selected))
        selected_ids.update(final_ids)
        phase_results[phase] = {
            "duration_ranking": duration_ranked,
            "memory_proxy_ranking": proxy_ranked,
            "memory_proxy_total": proxy_total,
            "memory_proxy_prefix_cutoff": cutoff,
            "memory_proxy_prefix_fraction": cutoff / proxy_total,
            "duration_prefix_request_ids": duration_selected,
            "memory_proxy_prefix_request_ids": proxy_selected,
            "observed_semantic_class_anchor_request_ids": [],
            "final_request_ids": final_ids,
        }
    return {
        "schema_version": "C16_ROUTE_B_FINAL_SELECTION_V1",
        "status": "FROZEN_PRE_OUTCOME_SELECTION",
        "selection_rule": "duration-prefix U memory-proxy-prefix U observed-semantic-class-anchors",
        "forbidden_selection_inputs": ["GPU_VA", "address locality", "cache outcome", "TLB outcome", "Route-B address outcome"],
        "map_failures_closed": sorted(failures, key=lambda row: row["request_id"]),
        "phases": phase_results,
        "final_request_ids": sorted(selected_ids),
    }
