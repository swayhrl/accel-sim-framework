"""Independent raw semantic/CUDA chronology, no producer-derived union imports."""
from __future__ import annotations

from collections import defaultdict
import re

from core import Interval, chronological_gaps, union_length_ns


def role_family(module: str) -> str:
    if module.endswith(".self_attn"):
        return "ATTENTION"
    if module.endswith(".mlp.gate_up_proj"):
        return "GATE_UP_PROJECTION"
    if module.endswith(".mlp.down_proj"):
        return "DOWN_PROJECTION"
    if module.endswith(".mlp.act_fn"):
        return "ACTIVATION"
    return "OTHER:" + module


def parse_observed_intervals(semantic_rows: list[dict[str, str]], cuda_rows: list[dict[str, str]], point_id: str, request_id: str) -> dict:
    sem = [r for r in semantic_rows if r["point_id"] == point_id and r["observed_request_id"] == request_id]
    cuda = [r for r in cuda_rows if r["point_id"] == point_id and r["observed_request_id"] == request_id]
    if not sem or not cuda:
        raise ValueError("missing NSYS semantic/CUDA point or request")
    ordinal_to_sem = {}
    for row in sem:
        ordinal = row["ordinal"]
        if ordinal in ordinal_to_sem or row["status"] != "PASS" or not row["module"]:
            raise ValueError("duplicate/invalid semantic ordinal")
        interval = Interval(int(row["nvtx_start_ns"]), int(row["nvtx_end_ns"]), ordinal)
        ordinal_to_sem[ordinal] = (row, interval)
    semantic_roots = [interval for row, interval in ordinal_to_sem.values() if row["parent_ordinal_or_NA"] == "NA"]
    cuda_intervals = []
    by_module = defaultdict(list)
    by_family = defaultdict(list)
    by_phase_family = defaultdict(list)
    by_phase_family_kernel = defaultdict(set)
    by_ordinal = defaultdict(list)
    unassigned = []
    ids = set()
    for row in cuda:
        identity = row["cuda_interval_id"]
        if identity in ids or row["parent_request_id"] != request_id or not re.fullmatch(r"[0-9a-fA-F]{64}", row["source_capture_sha256"]):
            raise ValueError("duplicate/invalid CUDA interval identity")
        ids.add(identity)
        interval = Interval(int(row["start_ns"]), int(row["end_ns"]), identity)
        cuda_intervals.append(interval)
        ordinal = row["correlated_nvtx_ordinal_or_NA"]
        if ordinal == "NA":
            unassigned.append(interval)
        else:
            if ordinal not in ordinal_to_sem:
                raise ValueError("CUDA correlation points to absent semantic ordinal")
            module = ordinal_to_sem[ordinal][0]["module"]
            phase = ordinal_to_sem[ordinal][0]["phase"]
            family = role_family(module)
            by_module[module].append(interval)
            by_family[family].append(interval)
            by_phase_family[(phase, family)].append(interval)
            by_phase_family_kernel[(phase, family)].add(row["kernel_name"])
            by_ordinal[ordinal].append(interval)
    parent = Interval(min(i.start_ns for i in cuda_intervals), max(i.end_ns for i in cuda_intervals), request_id)
    parent_union = union_length_ns(cuda_intervals, parent)
    parent_span = parent.duration_ns
    if parent_union <= 0:
        raise ValueError("zero parent CUDA union")
    module_rows = []
    ordinal_rows = []
    for ordinal, intervals in sorted(by_ordinal.items(), key=lambda kv: int(kv[0])):
        sem_row = ordinal_to_sem[ordinal][0]
        summed = sum(i.duration_ns for i in intervals)
        unioned = union_length_ns(intervals, parent)
        ordinal_rows.append({
            "point_id": point_id, "observed_request_id": request_id,
            "ordinal": ordinal, "module": sem_row["module"], "phase": sem_row["phase"],
            "family": role_family(sem_row["module"]), "cuda_event_count": len(intervals),
            "cuda_sum_ns": summed, "cuda_union_ns": unioned,
            "overlap_double_count_ns": summed - unioned,
            "parent_full_request_cuda_union_ns": parent_union,
            "f_of_full_request_graph_off": unioned / parent_union,
        })
    for module, intervals in sorted(by_module.items()):
        summed = sum(i.duration_ns for i in intervals)
        unioned = union_length_ns(intervals, parent)
        module_rows.append({
            "point_id": point_id, "observed_request_id": request_id,
            "module": module, "cuda_event_count": len(intervals),
            "cuda_sum_ns": summed, "cuda_union_ns": unioned,
            "overlap_double_count_ns": summed - unioned,
            "parent_cuda_union_ns": parent_union,
            "f_graph_off": unioned / parent_union,
        })
    family_rows = []
    for (phase, family), intervals in sorted(by_phase_family.items()):
        summed = sum(i.duration_ns for i in intervals)
        unioned = union_length_ns(intervals, parent)
        family_rows.append({
            "point_id": point_id, "observed_request_id": request_id,
            "phase": phase, "family": family, "cuda_event_count": len(intervals),
            "unique_kernel_names": sorted(by_phase_family_kernel[(phase, family)]),
            "cuda_sum_ns": summed, "cuda_union_ns": unioned,
            "overlap_double_count_ns": summed - unioned,
            "parent_full_request_cuda_union_ns": parent_union,
            "f_of_full_request_graph_off": unioned / parent_union,
        })
    all_phase_family_rows = []
    for family, intervals in sorted(by_family.items()):
        summed = sum(i.duration_ns for i in intervals)
        unioned = union_length_ns(intervals, parent)
        all_phase_family_rows.append({
            "point_id": point_id, "observed_request_id": request_id,
            "phase": "ALL", "family": family, "cuda_event_count": len(intervals),
            "cuda_sum_ns": summed, "cuda_union_ns": unioned,
            "overlap_double_count_ns": summed - unioned,
            "parent_full_request_cuda_union_ns": parent_union,
            "f_of_full_request_graph_off": unioned / parent_union,
        })
    all_phase_family_sum = sum(row["cuda_union_ns"] for row in family_rows)
    all_gaps = [
        {"point_id": point_id, "observed_request_id": request_id, "gap_kind": "GLOBAL_CHRONOLOGY", **gap}
        for gap in chronological_gaps(cuda_intervals, parent)
    ]
    # Sibling semantic ranges are the only automatic handoff candidates. A
    # nested parent/child is not a producer->consumer boundary.
    siblings = defaultdict(list)
    for ordinal, (row, sem_interval) in ordinal_to_sem.items():
        siblings[row["parent_ordinal_or_NA"]].append((sem_interval.start_ns, ordinal, row["module"]))
    boundaries = []
    for sibling_parent, members in siblings.items():
        members.sort()
        for (_, prior_ord, prior_module), (_, next_ord, next_module) in zip(members, members[1:]):
            prior_gpu, next_gpu = by_ordinal.get(prior_ord), by_ordinal.get(next_ord)
            if not prior_gpu or not next_gpu:
                boundaries.append({
                    "point_id": point_id, "observed_request_id": request_id,
                    "semantic_parent_ordinal": sibling_parent,
                    "producer_ordinal": prior_ord, "consumer_ordinal": next_ord,
                    "producer_module": prior_module, "consumer_module": next_module,
                    "signed_gap_ns": None, "positive_gap_ns": None,
                    "gap_start_ns": None, "gap_end_ns": None,
                    "parent_cuda_union_ns": parent_union,
                    "positive_gap_parent_fraction": None,
                    "status": "BOUNDARY_GAP_NOT_IDENTIFIABLE",
                })
                continue
            gap = min(i.start_ns for i in next_gpu) - max(i.end_ns for i in prior_gpu)
            boundaries.append({
                "point_id": point_id, "observed_request_id": request_id,
                "semantic_parent_ordinal": sibling_parent,
                "producer_ordinal": prior_ord, "consumer_ordinal": next_ord,
                "producer_module": prior_module, "consumer_module": next_module,
                "signed_gap_ns": gap, "positive_gap_ns": max(0, gap),
                "gap_start_ns": max(i.end_ns for i in prior_gpu) if gap > 0 else None,
                "gap_end_ns": min(i.start_ns for i in next_gpu) if gap > 0 else None,
                "parent_cuda_union_ns": parent_union,
                "positive_gap_parent_fraction": max(0, gap) / parent_union,
                "status": "OVERLAP" if gap < 0 else ("TOUCH" if gap == 0 else "GAP"),
            })
    return {
        "module_unions": module_rows,
        "ordinal_unions": ordinal_rows,
        "phase_family_unions": family_rows,
        "all_phase_family_unions": all_phase_family_rows,
        "phase_family_union_sum_ns": all_phase_family_sum,
        "correlated_all_family_union_ns": union_length_ns(
            [interval for group in by_family.values() for interval in group], parent),
        "global_launch_gaps": all_gaps,
        "sibling_boundaries": boundaries,
        "parent_cuda_union_ns": parent_union,
        "parent_cuda_span_ns": parent_span,
        "semantic_root_count": len(semantic_roots),
        "semantic_root_span_ns": semantic_roots[0].duration_ns if len(semantic_roots) == 1 else None,
        "uncorrelated_cuda_intervals": len(unassigned),
        "cuda_interval_count": len(cuda_intervals),
        "semantic_interval_count": len(sem),
    }


def handoff_chronology_summary(parsed: dict) -> dict:
    """Graph-OFF observed chronology only; never a causal handoff oracle."""
    relevant = {
        ("ATTENTION", "GATE_UP_PROJECTION"),
        ("GATE_UP_PROJECTION", "ACTIVATION"),
        ("ACTIVATION", "DOWN_PROJECTION"),
        ("DOWN_PROJECTION", "ATTENTION"),
    }
    boundaries = [row for row in parsed["sibling_boundaries"]
                  if (role_family(row["producer_module"]), role_family(row["consumer_module"])) in relevant]
    positive = [row for row in boundaries if row["status"] == "GAP"]
    spans = [Interval(row["gap_start_ns"], row["gap_end_ns"],
                      f"{row['producer_ordinal']}->{row['consumer_ordinal']}") for row in positive]
    union_ns = union_length_ns(spans)
    summed_ns = sum(span.duration_ns for span in spans)
    parent_span = parsed["parent_cuda_span_ns"]
    if parent_span <= 0:
        raise ValueError("no Graph-OFF observed parent span")
    fraction = union_ns / parent_span
    return {
        "boundary_count": len(boundaries),
        "identifiable_count": sum(row["status"] != "BOUNDARY_GAP_NOT_IDENTIFIABLE" for row in boundaries),
        "unknown_count": sum(row["status"] == "BOUNDARY_GAP_NOT_IDENTIFIABLE" for row in boundaries),
        "overlap_count": sum(row["status"] == "OVERLAP" for row in boundaries),
        "positive_gap_count": len(positive),
        "positive_gap_sum_ns": summed_ns,
        "positive_gap_union_ns": union_ns,
        "parent_observed_cuda_span_ns": parent_span,
        "positive_gap_fraction_of_observed_cuda_span": fraction,
        "positive_gap_fraction_of_parent_cuda_union": union_ns / parsed["parent_cuda_union_ns"],
        "status": "HANDOFF_CHRONOLOGY_MATERIAL" if union_ns / parsed["parent_cuda_union_ns"] >= 0.03 else "HANDOFF_CHRONOLOGY_NOT_MATERIAL",
        "claim_boundary": "GRAPH_OFF_OBSERVED_CHRONOLOGY_ONLY_NOT_HARDWARE_CAUSALITY",
    }
