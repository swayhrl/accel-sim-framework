#!/usr/bin/env python3
"""Fail-closed V2 Route-B duration and memory-proxy selection."""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


class RouteBSelectionError(ValueError):
    pass


def _product(value: object, label: str) -> int:
    if not isinstance(value, str):
        raise RouteBSelectionError(f"{label} must be AxBxC")
    try:
        dims = tuple(int(part) for part in value.split("x"))
    except ValueError as exc:
        raise RouteBSelectionError(f"{label} is malformed") from exc
    if len(dims) != 3 or any(dim <= 0 for dim in dims):
        raise RouteBSelectionError(f"{label} is malformed")
    return dims[0] * dims[1] * dims[2]


def _sha(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise RouteBSelectionError(f"{label} must be lowercase SHA256")
    return value


def _rank(rows: list[dict[str, Any]], metric: str) -> list[dict[str, Any]]:
    return sorted(rows, key=lambda row: (-row[metric], row["exact_full_function"], row["request_id"]))


def _prefix(rows: list[dict[str, Any]], metric: str, denominator: int, threshold: float) -> tuple[list[str], int]:
    if denominator <= 0:
        raise RouteBSelectionError(f"invalid {metric} denominator")
    total, selected = 0, []
    for row in _rank(rows, metric):
        total += row[metric]
        selected.append(row["request_id"])
        if total / denominator >= threshold:
            return selected, total
    raise RouteBSelectionError(f"complete frozen census cannot reach {threshold:.0%}")


def normalize_active_map_results_v2(document: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize active-G evidence without altering its JSON or its authority.

    Active V2 map evidence deliberately uses mapper-facing names such as
    ``full_mangled_function`` and ``global_mref_count``.  Selection consumes a
    small internal schema, but that translation must be explicit and
    fail-closed: it is not a license to fill an unresolved owner/count.
    """
    if document.get("schema_version") != "C16_ROUTE_B_MAP_RESULTS_V2_V2":
        raise RouteBSelectionError("requires active ROUTE_B_MAP_RESULTS_V2_V2 evidence")
    results = document.get("results")
    if not isinstance(results, list) or not results:
        raise RouteBSelectionError("active map results are absent")
    normalized: list[dict[str, Any]] = []
    for result in results:
        if not isinstance(result, dict):
            raise RouteBSelectionError("active map result is malformed")
        status = result.get("status")
        request_id, function = result.get("request_id"), result.get("exact_full_function")
        if not isinstance(request_id, str) or not request_id or not isinstance(function, str) or not function:
            raise RouteBSelectionError("active map result lacks request/exact function")
        if status == "FAILED_CLOSED":
            reason = result.get("failure_reason")
            if not isinstance(reason, str) or not reason:
                raise RouteBSelectionError("failed active map has no closed reason")
            normalized.append({"request_id": request_id, "terminal_status": status,
                               "exact_full_function": function, "failure_reason": reason})
            continue
        if status != "MAPPED_EXACT":
            raise RouteBSelectionError("active map result is not terminal")
        mangle = result.get("full_mangled_function")
        count = result.get("global_mref_count")
        if not isinstance(mangle, str) or not mangle or not isinstance(count, int) or count <= 0:
            raise RouteBSelectionError("mapped active result lacks exact mangle/GLOBAL MREF count")
        normalized.append({
            "request_id": request_id, "terminal_status": status, "exact_full_function": function,
            "function_mangled_name": mangle, "static_global_mref_count": count,
            "static_map_sha256": _sha(result.get("static_map_sha256"), "active static map"),
            "code_object_sha256": _sha(result.get("actual_owning_code_object_sha256"), "active code object"),
        })
    if len({item["request_id"] for item in normalized}) != len(normalized):
        raise RouteBSelectionError("active map results contain duplicate request ids")
    return normalized


def freeze_final_selection_v2(request_document: dict[str, Any], map_summaries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Freeze only from terminal V2 maps; failed maps retain full-census gaps."""
    if request_document.get("schema_version") != "C16_ROUTE_B_MAP_REQUESTS_V2":
        raise RouteBSelectionError("requires ROUTE_B_MAP_REQUESTS_V2")
    requests = request_document.get("requests")
    if not isinstance(requests, list) or not requests:
        raise RouteBSelectionError("empty V2 request document")
    request_by_id, phase_rows = {}, defaultdict(list)
    for request in requests:
        if not isinstance(request, dict) or not isinstance(request.get("request_id"), str):
            raise RouteBSelectionError("malformed request")
        request_id, function = request["request_id"], request.get("exact_full_function")
        if request_id in request_by_id or not isinstance(function, str) or not function:
            raise RouteBSelectionError("duplicate/missing exact function")
        if request.get("known_mangled_name") != "MAP_DISCOVERY_REQUIRED" or request.get("code_object_sha256") != "MAP_DISCOVERY_REQUIRED":
            raise RouteBSelectionError("map-discovery authority is malformed")
        _sha(request.get("source_catalog_sha"), "source catalog")
        request_by_id[request_id] = request
        observations = request.get("phase_observations")
        if not isinstance(observations, dict):
            raise RouteBSelectionError("missing phase observations")
        for phase, observation in observations.items():
            geometries = observation.get("geometries") if isinstance(observation, dict) else None
            if phase not in {"PREFILL", "DECODE"} or not isinstance(geometries, list) or not geometries:
                raise RouteBSelectionError("malformed phase geometry observations")
            launches = duration = 0
            geometry_complete = True
            for geometry in geometries:
                if not isinstance(geometry, dict): raise RouteBSelectionError("malformed geometry")
                _product(geometry.get("grid"), "grid"); _product(geometry.get("block"), "block")
                if not all(isinstance(geometry.get(field), str) and geometry[field] for field in ("shape_key", "dtype_key")):
                    raise RouteBSelectionError("geometry lacks shape/dtype")
                if not isinstance(geometry.get("launch_count"), int) or geometry["launch_count"] <= 0 or not isinstance(geometry.get("duration_ns"), int) or geometry["duration_ns"] <= 0:
                    geometry_complete = False
                    continue
                launches += geometry["launch_count"]; duration += geometry["duration_ns"]
            phase_duration = observation.get("phase_duration_ns")
            if not isinstance(phase_duration, int) or phase_duration <= 0:
                raise RouteBSelectionError("phase lacks frozen duration evidence")
            if geometry_complete:
                if observation.get("launch_count") != launches or phase_duration != duration:
                    raise RouteBSelectionError("phase aggregate disagrees with frozen geometries")
            # Legacy source authority may have an exact phase aggregate and
            # geometries, but no per-geometry launch/duration allocation.  It
            # is sufficient to prove an already failed duration prefix, never
            # to calculate or claim a memory proxy.
            phase_rows[phase].append({"request_id": request_id, "exact_full_function": function,
                                      "duration_ns": phase_duration, "geometries": geometries,
                                      "geometry_observations_complete": geometry_complete})

    summaries, forbidden = {}, {"gpu_va", "gpu_va_by_address_lane", "address", "locality", "cache_outcome", "tlb_outcome"}
    for summary in map_summaries:
        if not isinstance(summary, dict) or any(field in summary for field in forbidden):
            raise RouteBSelectionError("map summary contains forbidden outcome data")
        request_id = summary.get("request_id")
        status = summary.get("terminal_status", summary.get("status"))
        if not isinstance(request_id, str) or request_id not in request_by_id or request_id in summaries or status not in {"MAPPED_EXACT", "FAILED_CLOSED"}:
            raise RouteBSelectionError("map summary is unknown, duplicate, or nonterminal")
        if summary.get("exact_full_function") != request_by_id[request_id]["exact_full_function"]:
            raise RouteBSelectionError("map exact function differs from request")
        summaries[request_id] = summary
    if set(summaries) != set(request_by_id):
        raise RouteBSelectionError("all V2 requests must be terminal before final freeze")

    maps, failures = {}, []
    for request_id, summary in summaries.items():
        if summary.get("terminal_status", summary.get("status")) == "FAILED_CLOSED":
            if not isinstance(summary.get("failure_reason"), str) or not summary["failure_reason"]: raise RouteBSelectionError("failed map lacks reason")
            failures.append({"request_id": request_id, "failure_reason": summary["failure_reason"]}); continue
        if not isinstance(summary.get("function_mangled_name"), str) or not summary["function_mangled_name"] or not isinstance(summary.get("static_global_mref_count"), int) or summary["static_global_mref_count"] <= 0:
            raise RouteBSelectionError("mapped result lacks exact identity/GLOBAL+MREF count")
        maps[request_id] = {"function_mangled_name": summary["function_mangled_name"], "static_global_mref_count": summary["static_global_mref_count"], "static_map_sha256": _sha(summary.get("static_map_sha256"), "static map"), "code_object_sha256": _sha(summary.get("code_object_sha256"), "code object")}

    phases, final_ids = {}, set()
    for phase, rows in sorted(phase_rows.items()):
        duration_denominator = sum(row["duration_ns"] for row in rows)
        duration_ids, duration_cutoff = _prefix(rows, "duration_ns", duration_denominator, .7)
        mapped_rows = []
        for row in rows:
            if row["request_id"] not in maps: continue
            if not row["geometry_observations_complete"]:
                continue
            map_data = maps[row["request_id"]]
            proxy = sum(g["launch_count"] * _product(g["grid"], "grid") * ((_product(g["block"], "block") + 31) // 32) * map_data["static_global_mref_count"] for g in row["geometries"])
            mapped_rows.append(dict(row, memory_proxy=proxy, **map_data))
        required_duration_failures = sorted(request_id for request_id in duration_ids if request_id not in maps)
        incomplete_geometry_ids = sorted(row["request_id"] for row in rows if not row["geometry_observations_complete"])
        outcome = {"full_frozen_duration_denominator_ns": duration_denominator, "duration_ranking": _rank(rows, "duration_ns"), "duration_prefix_request_ids": duration_ids, "duration_prefix_cutoff_ns": duration_cutoff, "duration_prefix_coverage": duration_cutoff / duration_denominator, "geometry_observations_incomplete_request_ids": incomplete_geometry_ids, "memory_proxy_ranking": _rank(mapped_rows, "memory_proxy")}
        if failures:
            outcome.update({"duration_coverage_status": "FAILED_CLOSED_REQUIRED_MEMBER" if required_duration_failures else "NUMERIC_ONLY_UNMAPPED_PROXY_GAP",
                            "required_duration_failed_closed_request_ids": required_duration_failures,
                            "memory_proxy_coverage_status": "NOT_PROVABLE_FAILED_CLOSED", "memory_proxy_coverage": None,
                            # An analysis prefix is not a runnable capture set.
                            "final_request_ids": []})
        else:
            if incomplete_geometry_ids:
                raise RouteBSelectionError("cannot freeze runnable selection from incomplete per-geometry observations")
            denominator = sum(row["memory_proxy"] for row in mapped_rows)
            proxy_ids, proxy_cutoff = _prefix(mapped_rows, "memory_proxy", denominator, .8)
            selected = sorted(set(duration_ids).union(proxy_ids))
            outcome.update({"full_frozen_memory_proxy_denominator": denominator, "memory_proxy_prefix_request_ids": proxy_ids, "memory_proxy_prefix_cutoff": proxy_cutoff, "memory_proxy_coverage": proxy_cutoff / denominator, "memory_proxy_coverage_status": "PROVEN", "final_request_ids": selected})
        final_ids.update(outcome["final_request_ids"]); phases[phase] = outcome
    return {"schema_version": "C16_ROUTE_B_FINAL_SELECTION_V2",
            "status": "FROZEN_PRE_OUTCOME_SELECTION" if not failures else "SELECTION_NOT_ADMISSIBLE_DUE_TO_FAILED_CLOSED_COVERAGE",
            "selection_rule": "minimum duration-prefix >=70% U minimum memory-proxy-prefix >=80% U observed semantic anchors",
            "map_failures_closed": sorted(failures, key=lambda row: row["request_id"]), "phases": phases,
            "final_request_ids": sorted(final_ids) if not failures else []}
