"""Post-recomputation-only producer comparison; never computational authority."""
from __future__ import annotations

from math import isfinite


def compare_native_summary(independent: list[dict], producer_summary: list[dict[str, str]], complete_points: set[str]) -> list[dict]:
    lookup = {(r["point_id"], r["arm"]): r for r in producer_summary if r["point_id"] in complete_points}
    if len(lookup) != sum(r["point_id"] in complete_points for r in producer_summary):
        raise ValueError("duplicate producer native summary key")
    expected = {(r["point_id"], r["arm"]) for r in independent}
    if set(lookup) != expected:
        raise ValueError("producer native summary row matrix mismatch")
    mapping = {
        "measured_n": "cuda_sample_count",
        "median_request_cuda_event_ms": "cuda_median",
        "minimum_request_cuda_event_ms": "cuda_min",
        "maximum_request_cuda_event_ms": "cuda_max",
    }
    rows = []
    for point, arm in sorted(expected):
        prod = lookup[(point, arm)]
        own = next(r for r in independent if (r["point_id"], r["arm"]) == (point, arm))
        for p_field, c_field in mapping.items():
            try:
                theirs = float(prod[p_field])
                ours = float(own[c_field])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError("missing/non-numeric producer summary field") from exc
            if not isfinite(theirs) or not isfinite(ours):
                raise ValueError("nonfinite summary comparison")
            tolerance = 0 if p_field == "measured_n" else 1e-6  # ms; raw cells have finer precision
            rows.append({
                "point_id": point, "arm": arm, "metric": p_field,
                "consumer": ours, "producer": theirs,
                "absolute_difference": abs(ours - theirs),
                "status": "MATCH" if abs(ours - theirs) <= tolerance else "CONSUMER_PRODUCER_NUMERIC_MISMATCH",
            })
    return rows


def compare_headroom_summary(independent: list[dict], producer_rows: list[dict[str, str]], complete_points: set[str]) -> list[dict]:
    """Match producer display rows only after raw family unions are computed."""
    own = {(r["point_id"], r["family"]): r for r in independent}
    checks = []
    mapping = {
        "graph_off_candidate_union_ns": "candidate_graph_off_union_ns",
        "graph_off_parent_cuda_union_ns": "parent_graph_off_cuda_union_ns",
        "f_graph_off": "f_graph_off",
        "s_zero_graph_off_screen": "s_zero_graph_off_screen",
    }
    for row in producer_rows:
        if row["point_id"] not in complete_points or row["graph_off_candidate_union_ns"] == "NA":
            continue
        key = (row["point_id"], row["candidate_id"])
        if key not in own:
            raise ValueError("producer headroom candidate absent from independent raw union")
        for p_field, c_field in mapping.items():
            p_value = float(row[p_field])
            c_value = float(own[key][c_field])
            if not isfinite(p_value) or not isfinite(c_value):
                raise ValueError("nonfinite headroom crosscheck")
            tolerance = 0 if p_field.endswith("_ns") else 1e-12
            checks.append({
                "point_id": key[0], "question_id": row["question_id"], "candidate_id": key[1],
                "metric": p_field, "consumer": c_value, "producer": p_value,
                "absolute_difference": abs(c_value - p_value),
                "status": "MATCH" if abs(c_value - p_value) <= tolerance else "CONSUMER_PRODUCER_NUMERIC_MISMATCH",
            })
    return checks


def compare_launch_gaps(independent_by_point: dict[str, dict], producer_rows: list[dict[str, str]], complete_points: set[str]) -> list[dict]:
    own = {}
    for point in complete_points:
        for row in independent_by_point[point]["global_launch_gaps"]:
            key = (point, row["predecessor"], row["successor"])
            if key in own:
                raise ValueError("duplicate independent launch pair")
            own[key] = row
    theirs = {}
    for row in producer_rows:
        point = row["point_id"]
        if point not in complete_points:
            continue
        key = (point, row["preceding_cuda_interval_id"], row["following_cuda_interval_id"])
        if key in theirs:
            raise ValueError("duplicate producer launch pair")
        theirs[key] = row
    if set(own) != set(theirs):
        raise ValueError("producer/consumer launch pair matrix mismatch")
    rows = []
    for key in sorted(own):
        a, b = own[key], theirs[key]
        fields = (("gap_duration_ns", a["positive_gap_ns"]),
                  ("gap_start_ns", a["gap_start_ns"]),
                  ("gap_end_ns", a["gap_end_ns"]))
        for metric, value in fields:
            text_value = b[metric]
            theirs_num = None if text_value == "NA" else int(text_value)
            rows.append({
                "point_id": key[0], "question_id": "CHRONOLOGY", "candidate_id": key[1] + "->" + key[2],
                "metric": metric, "consumer": value, "producer": theirs_num,
                "absolute_difference": abs(value - theirs_num) if value is not None and theirs_num is not None else None,
                "status": "MATCH" if value == theirs_num else "CONSUMER_PRODUCER_NUMERIC_MISMATCH",
            })
    return rows


def compare_handoff_boundaries(independent_by_point: dict[str, dict], producer_rows: list[dict[str, str]], complete_points: set[str]) -> list[dict]:
    own = {}
    for point in complete_points:
        for row in independent_by_point[point]["sibling_boundaries"]:
            key = (point, row["producer_ordinal"], row["consumer_ordinal"])
            if key in own:
                raise ValueError("duplicate independent handoff boundary")
            own[key] = row
    theirs = {}
    for row in producer_rows:
        point = row["point_id"]
        if point not in complete_points:
            continue
        key = (point, row["producer_ordinal"], row["consumer_ordinal"])
        if key in theirs:
            raise ValueError("duplicate producer handoff boundary")
        theirs[key] = row
    if set(own) != set(theirs):
        raise ValueError("producer/consumer handoff boundary matrix mismatch")
    rows = []
    for key in sorted(own):
        a, b = own[key], theirs[key]
        expected = (("boundary_gap_ns", a["signed_gap_ns"], 0),
                    ("boundary_gap_parent_cuda_union_fraction",
                     a["signed_gap_ns"] / a["parent_cuda_union_ns"] if a["signed_gap_ns"] is not None else None,
                     1e-12))
        for metric, value, tolerance in expected:
            theirs_num = float(b[metric]) if value is not None and b[metric] != "NA" else None
            match = value is None and theirs_num is None or value is not None and theirs_num is not None and abs(value - theirs_num) <= tolerance
            rows.append({
                "point_id": key[0], "question_id": "DQ4a", "candidate_id": key[1] + "->" + key[2],
                "metric": metric, "consumer": value, "producer": theirs_num,
                "absolute_difference": abs(value - theirs_num) if value is not None and theirs_num is not None else None,
                "status": "MATCH" if match else "CONSUMER_PRODUCER_NUMERIC_MISMATCH",
            })
    return rows
