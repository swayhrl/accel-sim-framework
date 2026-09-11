#!/usr/bin/env python3
"""Read-only C12 operator-aware mechanism deep dive.

Consumes the frozen 22-arm C12 raw logs plus the accepted operator-aware map.
It never invokes a simulator or trace scanner.  Every per-kernel value comes
from an explicit raw marker checkpoint; full-ROI anchors remain separate.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "util" / "vm_tlb"))
from analyze_c12_operator_aware import raw_kernels  # accepted immutable-log parser


SOURCE_COMMIT = "a268aba0d01310294074ded5bb8017e2092394c0"
BASE = ROOT / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_CHARACTERIZATION"
OUT = ROOT / "docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_OPERATOR_AWARE_MECHANISM_DEEP_DIVE"
FORMAL = Path("/workspace/worktrees/accel-sim-vm-m4b-speculative/docs/vm_tlb/review_packs/M4B_SPECULATIVE_DEVELOPMENT/C12_C5_FULL_ROI_FAIR_PERFORMANCE")


# All fields below are monotonic counters when present in every kernel marker.
# Values outside this list (gauges/maxima/fixed-window data) are not attributed.
COUNTERS = {
    "l1_tlb_accesses": "vm_l1_tlb_accesses",
    "l1_tlb_misses": "vm_l1_tlb_misses",
    "l2_tlb_accesses": "vm_l2_tlb_accesses",
    "l2_tlb_misses": "vm_l2_tlb_misses",
    "l2_tlb_port_stalls": "vm_l2_tlb_port_stalls",
    "translation_mshr_allocations": "vm_translation_mshr_allocations",
    "translation_mshr_merges": "vm_translation_mshr_merges",
    "translation_mshr_full_events": "vm_translation_mshr_full_events",
    "requester_mshr_wait_cycles": "vm_translation_requester_mshr_wait_cycles_total",
    "requester_translation_latency_cycles": "vm_translation_requester_latency_cycles_total",
    "translation_walk_starts": "vm_translation_walk_starts",
    "pte_requests": "vm_pte_requests",
    "pte_l2_only_responses": "vm_pte_l2_only_responses",
    "pte_dram_responses": "vm_pte_dram_responses",
    "pte_memory_wait_cycles": "vm_pte_memory_wait_cycles_total",
    "pwc_accesses": "vm_pwc_accesses",
    "pwc_hits": "vm_pwc_hits",
    "pwc_misses": "vm_pwc_misses",
    "weight_segment_lookup_attempts": "vm_weight_segment_lookup_attempts",
    "weight_segment_hits": "vm_weight_segment_hits",
    "weight_segment_l2_suppressed": "vm_weight_segment_l2_suppressed",
    "subentry_hits": "vm_l2_tlb_subentry_hits",
    "subentry_misses": "vm_l2_tlb_subentry_misses",
}

KEY_METRICS = (
    "l1_tlb_misses", "l2_tlb_misses", "translation_walk_starts", "pte_requests",
    "pte_dram_responses", "requester_translation_latency_cycles",
    "weight_segment_hits", "weight_segment_l2_suppressed", "subentry_hits", "subentry_misses",
)

COMPARISONS = []
for roi in ("prefill", "decode1"):
    COMPARISONS.extend([
        (roi, "F1_vs_F2", ("F2", "NONE"), ("F1", "NONE")),
        (roi, "F5_vs_F0", ("F0", "NONE"), ("F5", "NONE")),
        *[(roi, f"F7-L{x}_vs_F0", ("F0", "NONE"), ("F7", x)) for x in ("5", "10", "20")],
        *[(roi, f"F8-L{x}_vs_F0", ("F0", "NONE"), ("F8", x)) for x in ("5", "10", "20")],
        *[(roi, f"F8-L{x}_vs_F7-L{x}", ("F7", x), ("F8", x)) for x in ("5", "10", "20")],
        (roi, "F8-L10_vs_F9", ("F9", "NONE"), ("F8", "10")),
    ])


@dataclass
class Meta:
    roi: str
    index: int
    trace: str
    semantic: str
    operator: str
    layer: str
    evidence: str
    weight_refs: int
    weight_pages: set[int]

    @property
    def direct_layer(self) -> bool:
        return self.evidence == "DIRECT_PARAMETER_RANGE" and self.layer.isdigit() and 0 <= int(self.layer) <= 15


@dataclass
class Arm:
    roi: str
    arm: str
    lseg: str
    result: dict[str, str]
    raw: list[Any]
    values: dict[str, list[int] | None]

    @property
    def key(self) -> tuple[str, str, str]:
        return self.roi, self.arm, self.lseg

    @property
    def cycles(self) -> list[int]:
        value = self.values["gpu_sim_cycle"]
        assert value is not None
        return value


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source, delimiter="\t"))


def write_tsv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", newline="") as sink:
        writer = csv.DictWriter(sink, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def fmt(value: float | int | None) -> str:
    if value is None:
        return "UNATTRIBUTED"
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.12g}"


def parse_pages(value: str) -> set[int]:
    return {int(part) for part in value.split(",") if part}


def counter_deltas(raw: list[Any], raw_name: str) -> list[int] | None:
    """Return exact per-marker deltas only for complete monotonic snapshots."""
    if not raw or raw_name not in raw[-1].cumulative:
        return None
    prior = 0
    result: list[int] = []
    for row in raw:
        if raw_name not in row.cumulative or row.cumulative_occurrences[raw_name] != 1:
            return None
        current = row.cumulative[raw_name]
        if current < prior:
            return None
        result.append(current - prior)
        prior = current
    if sum(result) != raw[-1].cumulative[raw_name]:
        return None
    return result


def cache_total(row: Any, level: str | None = None, outcome: str | None = None) -> int:
    return sum(value for (row_level, _object, row_outcome), value in row.cache.items()
               if (level is None or row_level == level) and (outcome is None or row_outcome == outcome))


def cache_compact(left: Any, right: Any) -> str:
    entries = []
    for key in sorted(set(left.cache) | set(right.cache)):
        delta = right.cache[key] - left.cache[key]
        if delta:
            level, object_class, outcome = key
            entries.append(f"{level}:{object_class}:{outcome}={delta}")
    return ";".join(entries) if entries else "NONE"


def cache_by_operator(arm: Arm, meta: list[Meta]) -> dict[tuple[str, str, str, str], int]:
    result: Counter = Counter()
    for kernel, row in zip(meta, arm.raw):
        for (level, object_class, outcome), value in row.cache.items():
            result[(kernel.operator, level, object_class, outcome)] += value
    return dict(result)


def sums_by_operator(arm: Arm, meta: list[Meta], metric: str) -> dict[str, int] | None:
    values = arm.values.get(metric)
    if values is None:
        return None
    result: Counter = Counter()
    for kernel, value in zip(meta, values):
        result[kernel.operator] += value
    return dict(result)


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    pos = (len(ordered) - 1) * fraction
    low, high = math.floor(pos), math.ceil(pos)
    return ordered[low] + (ordered[high] - ordered[low]) * (pos - low)


def threshold_count(values: list[int], fraction: float) -> int | str:
    total = sum(values)
    if total == 0:
        return "NA_ZERO_TOTAL"
    cumulative = 0
    for index, value in enumerate(values, 1):
        cumulative += value
        if cumulative / total >= fraction:
            return index
    return len(values)


def make_arm(status: dict[str, str], result: dict[str, str]) -> Arm:
    raw = raw_kernels(Path(status["run_dir"]) / "run.log")
    expected = int(status["expected_kernels"])
    if len(raw) != expected:
        raise RuntimeError(f"{status['roi']} {status['arm']} {status['lseg']}: expected {expected} raw markers, got {len(raw)}")
    cycles = []
    for index, row in enumerate(raw):
        if row.exact_occurrences["gpu_sim_cycle"] != 1:
            raise RuntimeError(f"{status['roi']} {status['arm']} {status['lseg']}: missing/duplicate cycle at {index}")
        cycles.append(row.exact["gpu_sim_cycle"])
    if sum(cycles) != int(result["gpu_tot_sim_cycle"]):
        raise RuntimeError(f"{status['roi']} {status['arm']} {status['lseg']}: exact cycle sum disagrees with accepted formal total")
    values: dict[str, list[int] | None] = {"gpu_sim_cycle": cycles}
    for output_name, raw_name in COUNTERS.items():
        values[output_name] = counter_deltas(raw, raw_name)
    return Arm(status["roi"], status["arm"], status["lseg"], result, raw, values)


def build_inputs() -> tuple[dict[str, list[Meta]], dict[tuple[str, str, str], Arm], dict[str, dict[int, set[int]]]]:
    maps = read_tsv(BASE / "KERNEL_OPERATOR_MAP.tsv")
    scans = {roi: {int(row["compute_index"]): parse_pages(row["weight_pages"])
                   for row in read_tsv(BASE / f"TRACE_SCAN_{roi}.tsv")}
             for roi in ("prefill", "decode1")}
    meta: dict[str, list[Meta]] = {"prefill": [], "decode1": []}
    for row in maps:
        item = Meta(row["roi"], int(row["compute_index"]), row["trace_filename"], row["semantic_kernel_name"],
                    row["operator_class"], row["layer_id"], row["evidence_kind"], int(row["weight_refs"]),
                    scans[row["roi"]][int(row["compute_index"])])
        meta[item.roi].append(item)
    for roi, rows in meta.items():
        rows.sort(key=lambda row: row.index)
        expected = 692 if roi == "prefill" else 740
        if [row.index for row in rows] != list(range(expected)):
            raise RuntimeError(f"{roi}: accepted operator map is not a dense frozen index map")

    status = read_tsv(FORMAL / "ARM_STATUS.tsv")
    results = {tuple(row[field] for field in ("roi", "arm", "lseg")): row for row in read_tsv(FORMAL / "ARM_RESULTS.tsv")}
    arms: dict[tuple[str, str, str], Arm] = {}
    for row in status:
        if row["terminal_status"] != "PASS":
            continue
        key = tuple(row[field] for field in ("roi", "arm", "lseg"))
        result = results.get(key)
        if not result or result["terminal_status"] != "PASS":
            raise RuntimeError(f"terminal status/result mismatch {key}")
        arms[key] = make_arm(row, result)
    if len(arms) != 22:
        raise RuntimeError(f"expected 22 accepted arms, got {len(arms)}")
    return meta, arms, scans


def ranking_rows(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[tuple[str, str], dict[str, Any]]]:
    ranking: list[dict[str, Any]] = []
    pareto: list[dict[str, Any]] = []
    summaries: dict[tuple[str, str], dict[str, Any]] = {}
    for roi, comparison, left_suffix, right_suffix in COMPARISONS:
        left, right = arms[(roi, *left_suffix)], arms[(roi, *right_suffix)]
        kernel_meta = meta[roi]
        total = sum(left.cycles)
        deltas = [candidate - baseline for baseline, candidate in zip(left.cycles, right.cycles)]
        modes = {
            "IMPROVEMENT": [i for i, delta in enumerate(deltas) if delta < 0],
            "REGRESSION": [i for i, delta in enumerate(deltas) if delta > 0],
            "ABSOLUTE": [i for i, delta in enumerate(deltas) if delta != 0],
        }
        for mode, indices in modes.items():
            indices.sort(key=lambda i: (-(-deltas[i] if mode == "IMPROVEMENT" else deltas[i] if mode == "REGRESSION" else abs(deltas[i])), i))
            magnitudes = [(-deltas[i] if mode == "IMPROVEMENT" else deltas[i] if mode == "REGRESSION" else abs(deltas[i])) for i in indices]
            total_magnitude = sum(magnitudes)
            thresholds = {fraction: threshold_count(magnitudes, fraction) for fraction in (0.5, 0.8, 0.9)}
            cumulative = 0
            if not indices:
                pareto.append({"row_kind": "ZERO_DELTA_IDENTITY", "roi": roi, "comparison": comparison,
                               "ranking_mode": mode, "rank": 0, "compute_index": "NA", "operator_class": "NA",
                               "layer_id": "NA", "cycle_delta": 0, "contribution_magnitude": 0,
                               "cumulative_magnitude": 0, "cumulative_fraction": "NA_ZERO_TOTAL",
                               "top10_cumulative_fraction": "NA_ZERO_TOTAL", "top20_cumulative_fraction": "NA_ZERO_TOTAL",
                               "top50_cumulative_fraction": "NA_ZERO_TOTAL", "kernels_to_50pct": "NA_ZERO_TOTAL",
                               "kernels_to_80pct": "NA_ZERO_TOTAL", "kernels_to_90pct": "NA_ZERO_TOTAL"})
                continue
            top_fraction: dict[int, float] = {}
            for rank, index in enumerate(indices, 1):
                magnitude = magnitudes[rank - 1]
                cumulative += magnitude
                item = kernel_meta[index]
                baseline = left.cycles[index]
                candidate = right.cycles[index]
                row = {
                    "roi": roi, "comparison": comparison, "ranking_mode": mode, "rank": rank,
                    "compute_index": index, "trace_filename": item.trace, "semantic_kernel_name": item.semantic,
                    "operator_class": item.operator, "layer_id": item.layer, "evidence_kind": item.evidence,
                    "baseline_cycle": baseline, "candidate_cycle": candidate, "cycle_delta": candidate - baseline,
                    "baseline_cycle_share": baseline / total if total else 0,
                    "l1_tlb_miss_delta": delta_at(left, right, "l1_tlb_misses", index),
                    "l2_tlb_miss_delta": delta_at(left, right, "l2_tlb_misses", index),
                    "translation_walk_delta": delta_at(left, right, "translation_walk_starts", index),
                    "pte_request_delta": delta_at(left, right, "pte_requests", index),
                    "pte_dram_response_delta": delta_at(left, right, "pte_dram_responses", index),
                    "requester_translation_latency_delta": delta_at(left, right, "requester_translation_latency_cycles", index),
                    "segment_hit_delta": delta_at(left, right, "weight_segment_hits", index),
                    "segment_l2_suppressed_delta": delta_at(left, right, "weight_segment_l2_suppressed", index),
                    "subentry_hit_delta": delta_at(left, right, "subentry_hits", index),
                    "subentry_miss_delta": delta_at(left, right, "subentry_misses", index),
                    "l1d_cache_tx_delta": cache_total(right.raw[index], "m4c_telemetry") - cache_total(left.raw[index], "m4c_telemetry"),
                    "l2_cache_tx_delta": cache_total(right.raw[index], "m4c_telemetry_l2") - cache_total(left.raw[index], "m4c_telemetry_l2"),
                    "l1d_reservation_fail_delta": cache_total(right.raw[index], "m4c_telemetry", "RESERVATION_FAIL") - cache_total(left.raw[index], "m4c_telemetry", "RESERVATION_FAIL"),
                    "l2_reservation_fail_delta": cache_total(right.raw[index], "m4c_telemetry_l2", "RESERVATION_FAIL") - cache_total(left.raw[index], "m4c_telemetry_l2", "RESERVATION_FAIL"),
                    "kernel_cache_outcome_delta": cache_compact(left.raw[index], right.raw[index]),
                }
                ranking.append(row)
                if rank <= 10:
                    top_fraction[10] = cumulative / total_magnitude
                if rank <= 20:
                    top_fraction[20] = cumulative / total_magnitude
                if rank <= 50:
                    top_fraction[50] = cumulative / total_magnitude
                pareto.append({"row_kind": "KERNEL", "roi": roi, "comparison": comparison, "ranking_mode": mode,
                               "rank": rank, "compute_index": index, "operator_class": item.operator, "layer_id": item.layer,
                               "cycle_delta": candidate - baseline, "contribution_magnitude": magnitude,
                               "cumulative_magnitude": cumulative, "cumulative_fraction": cumulative / total_magnitude,
                               "top10_cumulative_fraction": "", "top20_cumulative_fraction": "", "top50_cumulative_fraction": "",
                               "kernels_to_50pct": thresholds[0.5], "kernels_to_80pct": thresholds[0.8],
                               "kernels_to_90pct": thresholds[0.9]})
            # Put top-N aggregate answers in one explicit summary row.
            pareto.append({"row_kind": "SUMMARY", "roi": roi, "comparison": comparison, "ranking_mode": mode,
                           "rank": 0, "compute_index": "NA", "operator_class": "NA", "layer_id": "NA", "cycle_delta": sum(deltas),
                           "contribution_magnitude": total_magnitude, "cumulative_magnitude": total_magnitude,
                           "cumulative_fraction": 1, "top10_cumulative_fraction": sum(magnitudes[:10]) / total_magnitude,
                           "top20_cumulative_fraction": sum(magnitudes[:20]) / total_magnitude,
                           "top50_cumulative_fraction": sum(magnitudes[:50]) / total_magnitude,
                           "kernels_to_50pct": thresholds[0.5], "kernels_to_80pct": thresholds[0.8], "kernels_to_90pct": thresholds[0.9]})
        absolute = [abs(value) for value in deltas if value]
        summaries[(roi, comparison)] = {
            "total_delta": sum(deltas), "changed_kernels": len(absolute), "kernel_count": len(deltas),
            "top10_abs_fraction": sum(sorted(absolute, reverse=True)[:10]) / sum(absolute) if absolute else 0,
            "n50_abs": threshold_count(sorted(absolute, reverse=True), 0.5),
            "n80_abs": threshold_count(sorted(absolute, reverse=True), 0.8),
            "n90_abs": threshold_count(sorted(absolute, reverse=True), 0.9),
        }
    return ranking, pareto, summaries


def delta_at(left: Arm, right: Arm, metric: str, index: int) -> int | str:
    a, b = left.values.get(metric), right.values.get(metric)
    return b[index] - a[index] if a is not None and b is not None else "UNATTRIBUTED"


def cross_layer_rows(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for roi, comparison, left_suffix, right_suffix in COMPARISONS:
        left, right = arms[(roi, *left_suffix)], arms[(roi, *right_suffix)]
        classes = sorted({item.operator for item in meta[roi]})
        for metric in ("gpu_sim_cycle", *COUNTERS):
            baseline = sums_by_operator(left, meta[roi], metric)
            candidate = sums_by_operator(right, meta[roi], metric)
            for operator in classes:
                if baseline is None or candidate is None:
                    rows.append({"roi": roi, "comparison": comparison, "row_kind": "OPERATOR", "operator_class": operator,
                                 "metric": metric, "metric_scope": "UNATTRIBUTED", "baseline_value": "UNATTRIBUTED",
                                 "candidate_value": "UNATTRIBUTED", "delta": "UNATTRIBUTED", "note": "counter is not complete monotonic per-kernel evidence in one or both arms"})
                else:
                    rows.append({"roi": roi, "comparison": comparison, "row_kind": "OPERATOR", "operator_class": operator,
                                 "metric": metric, "metric_scope": "EXACT_PER_KERNEL", "baseline_value": baseline.get(operator, 0),
                                 "candidate_value": candidate.get(operator, 0), "delta": candidate.get(operator, 0) - baseline.get(operator, 0),
                                 "note": "exact marker checkpoint delta; association only"})
        left_cache, right_cache = cache_by_operator(left, meta[roi]), cache_by_operator(right, meta[roi])
        for operator, level, object_class, outcome in sorted(set(left_cache) | set(right_cache)):
            rows.append({"roi": roi, "comparison": comparison, "row_kind": "CACHE", "operator_class": operator,
                         "metric": f"{level}:{object_class}:{outcome}", "metric_scope": "EXACT_PER_KERNEL",
                         "baseline_value": left_cache.get((operator, level, object_class, outcome), 0),
                         "candidate_value": right_cache.get((operator, level, object_class, outcome), 0),
                         "delta": right_cache.get((operator, level, object_class, outcome), 0) - left_cache.get((operator, level, object_class, outcome), 0),
                         "note": "KERNEL-scope cache transactions; not TLB accesses"})
        rows.append({"roi": roi, "comparison": comparison, "row_kind": "FULL_ROI", "operator_class": "FULL_ROI",
                     "metric": "gpu_tot_sim_cycle", "metric_scope": "FULL_ROI_ONLY",
                     "baseline_value": left.result["gpu_tot_sim_cycle"], "candidate_value": right.result["gpu_tot_sim_cycle"],
                     "delta": int(right.result["gpu_tot_sim_cycle"]) - int(left.result["gpu_tot_sim_cycle"]),
                     "note": "formal anchor; never apportioned by cycle share"})
    return rows


def segment_rows(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    sensitivity: list[dict[str, Any]] = []
    break_even: list[dict[str, Any]] = []
    targets = ["FULL_ROI", "FFN_MLP", "ATTENTION_PROJECTION", "EMBEDDING_OUTPUT", "NORM"]
    for roi in ("prefill", "decode1"):
        base = arms[(roi, "F0", "NONE")]
        for family in ("F7", "F8"):
            values: dict[str, dict[str, int]] = {target: {} for target in targets}
            for lseg in ("5", "10", "20"):
                arm = arms[(roi, family, lseg)]
                by_op = sums_by_operator(arm, meta[roi], "gpu_sim_cycle") or {}
                base_by_op = sums_by_operator(base, meta[roi], "gpu_sim_cycle") or {}
                for target in targets:
                    candidate = int(arm.result["gpu_tot_sim_cycle"]) if target == "FULL_ROI" else by_op.get(target, 0)
                    baseline = int(base.result["gpu_tot_sim_cycle"]) if target == "FULL_ROI" else base_by_op.get(target, 0)
                    values[target][lseg] = candidate - baseline
                    sensitivity.append({"roi": roi, "family": family, "lseg": lseg, "operator_class": target,
                                        "metric": "gpu_sim_cycle", "metric_scope": "FULL_ROI_ONLY" if target == "FULL_ROI" else "EXACT_PER_KERNEL",
                                        "baseline_f0_value": baseline, "candidate_value": candidate, "delta_vs_f0": candidate - baseline,
                                        "segment_hits": sum(arm.values["weight_segment_hits"] or []),
                                        "segment_l2_suppressed": sum(arm.values["weight_segment_l2_suppressed"] or []),
                                        "finite_difference_from_prior": "NA_AT_L5" if lseg == "5" else "",
                                        "note": "measured point only; no extrapolation"})
            # Fill finite slopes after all points exist.
            for target in targets:
                y5, y10, y20 = values[target]["5"], values[target]["10"], values[target]["20"]
                points = [(5.0, y5), (10.0, y10), (20.0, y20)]
                crossings = []
                for (x0, y0), (x1, y1) in zip(points, points[1:]):
                    if y0 == 0:
                        crossings.append((x0, "MEASURED_POINT"))
                    elif y0 * y1 < 0:
                        crossings.append((x0 + (-y0) * (x1 - x0) / (y1 - y0), "EMPIRICAL_INTERPOLATION_ONLY"))
                    elif y1 == 0:
                        crossings.append((x1, "MEASURED_POINT"))
                if crossings:
                    crossing, kind = crossings[0]
                    determination = kind
                else:
                    crossing, determination = "UNDETERMINED_IN_MEASURED_RANGE", "NO_SIGN_CROSSING_AT_5_10_20"
                signs = ["IMPROVE" if value < 0 else "REGRESS" if value > 0 else "TIE" for _, value in points]
                monotonic = "MONOTONIC_NONDECREASING" if y5 <= y10 <= y20 else "NON_MONOTONIC"
                break_even.append({"roi": roi, "family": family, "operator_class": target,
                                   "delta_lseg5": y5, "delta_lseg10": y10, "delta_lseg20": y20,
                                   "signs": ">".join(signs), "monotonicity": monotonic,
                                   "break_even_lseg": fmt(crossing) if isinstance(crossing, float) else crossing,
                                   "determination": determination,
                                   "evidence_tier": "EMPIRICAL_INTERPOLATION_ONLY" if determination == "EMPIRICAL_INTERPOLATION_ONLY" else "MEASURED_DEEP_DIVE_FACT",
                                   "note": "only bracketed 5/10/20 interpolation; no out-of-range extrapolation"})
    # populate finite-difference values in stable second pass
    for row in sensitivity:
        if row["lseg"] == "5":
            continue
        prior_lseg = "5" if row["lseg"] == "10" else "10"
        prior = next(item for item in sensitivity if item["roi"] == row["roi"] and item["family"] == row["family"] and item["operator_class"] == row["operator_class"] and item["lseg"] == prior_lseg)
        row["finite_difference_from_prior"] = (row["delta_vs_f0"] - prior["delta_vs_f0"]) / (int(row["lseg"]) - int(prior_lseg))
    return sensitivity, break_even


def subentry_rows(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm]) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    rows: list[dict[str, Any]] = []
    identity: dict[str, bool] = {}
    selected = [item for item in COMPARISONS if item[1] in {"F1_vs_F2", "F8-L5_vs_F7-L5", "F8-L10_vs_F7-L10", "F8-L20_vs_F7-L20"}]
    for roi, comparison, left_suffix, right_suffix in selected:
        left, right = arms[(roi, *left_suffix)], arms[(roi, *right_suffix)]
        for operator in sorted({item.operator for item in meta[roi]}):
            chosen = [item.index for item in meta[roi] if item.operator == operator]
            for metric in ("gpu_sim_cycle", "subentry_hits", "subentry_misses", "l2_tlb_misses", "translation_walk_starts", "pte_dram_responses", "requester_translation_latency_cycles"):
                a, b = left.values.get(metric), right.values.get(metric)
                rows.append({"row_kind": "OPERATOR", "roi": roi, "comparison": comparison, "rank": "",
                             "compute_index": "", "operator_class": operator, "layer_id": "", "metric": metric,
                             "baseline_value": sum(a[index] for index in chosen) if a is not None else "UNATTRIBUTED",
                             "candidate_value": sum(b[index] for index in chosen) if b is not None else "UNATTRIBUTED",
                             "delta": sum(b[index] - a[index] for index in chosen) if a is not None and b is not None else "UNATTRIBUTED",
                             "note": "exact marker checkpoints; activity is not critical-path proof"})
        hits = right.values.get("subentry_hits")
        if hits is not None:
            for rank, index in enumerate(sorted(range(len(hits)), key=lambda i: (-hits[i], i))[:20], 1):
                item = meta[roi][index]
                rows.append({"row_kind": "TOP_CANDIDATE_HIT_KERNEL", "roi": roi, "comparison": comparison, "rank": rank,
                             "compute_index": index, "operator_class": item.operator, "layer_id": item.layer, "metric": "subentry_hits",
                             "baseline_value": left.values["subentry_hits"][index] if left.values.get("subentry_hits") is not None else "UNATTRIBUTED",
                             "candidate_value": hits[index], "delta": hits[index] - (left.values["subentry_hits"][index] if left.values.get("subentry_hits") is not None else 0),
                             "note": "candidate-ranked activity; do not infer critical-path benefit"})
        if roi == "decode1" and comparison.startswith("F8-L"):
            identity[comparison] = left.cycles == right.cycles
    return rows, identity


def pwc_rows(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for roi in ("prefill", "decode1"):
        base, candidate = arms[(roi, "F0", "NONE")], arms[(roi, "F5", "NONE")]
        for operator in sorted({item.operator for item in meta[roi]}):
            chosen = [item.index for item in meta[roi] if item.operator == operator]
            for metric in ("gpu_sim_cycle", "l2_tlb_misses", "translation_walk_starts", "pte_requests", "pte_dram_responses", "pwc_accesses", "pwc_hits", "pwc_misses", "requester_translation_latency_cycles"):
                a, b = base.values.get(metric), candidate.values.get(metric)
                rows.append({"row_kind": "OPERATOR", "roi": roi, "operator_class": operator, "rank": "", "compute_index": "",
                             "metric": metric, "baseline_f0": sum(a[i] for i in chosen) if a is not None else "UNATTRIBUTED",
                             "candidate_f5": sum(b[i] for i in chosen) if b is not None else "UNATTRIBUTED",
                             "delta_f5_minus_f0": sum(b[i] - a[i] for i in chosen) if a is not None and b is not None else "UNATTRIBUTED",
                             "note": "exact per-kernel checkpoint delta"})
        for rank, index in enumerate(sorted(range(len(base.cycles)), key=lambda i: (-(candidate.cycles[i] - base.cycles[i]), i))[:20], 1):
            item = meta[roi][index]
            rows.append({"row_kind": "TOP_REGRESSION_KERNEL", "roi": roi, "operator_class": item.operator, "rank": rank, "compute_index": index,
                         "metric": "gpu_sim_cycle", "baseline_f0": base.cycles[index], "candidate_f5": candidate.cycles[index],
                         "delta_f5_minus_f0": candidate.cycles[index] - base.cycles[index], "note": "exact cycle delta"})
        rows.append({"row_kind": "FULL_ROI", "roi": roi, "operator_class": "FULL_ROI", "rank": "", "compute_index": "",
                     "metric": "gpu_tot_sim_cycle", "baseline_f0": base.result["gpu_tot_sim_cycle"], "candidate_f5": candidate.result["gpu_tot_sim_cycle"],
                     "delta_f5_minus_f0": int(candidate.result["gpu_tot_sim_cycle"]) - int(base.result["gpu_tot_sim_cycle"]), "note": "FULL_ROI_ONLY anchor"})
    return rows


def layer_rows(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summary: list[dict[str, Any]] = []
    robustness: list[dict[str, Any]] = []
    for roi in ("prefill", "decode1"):
        f0 = arms[(roi, "F0", "NONE")]
        for operator in ("ATTENTION_PROJECTION", "FFN_MLP", "NORM"):
            layer_to_indices: dict[int, list[int]] = defaultdict(list)
            for item in meta[roi]:
                if item.operator == operator and item.direct_layer:
                    layer_to_indices[int(item.layer)].append(item.index)
            for layer, indices in sorted(layer_to_indices.items()):
                pages = set().union(*(meta[roi][index].weight_pages for index in indices))
                row: dict[str, Any] = {"roi": roi, "operator_class": operator, "layer_id": layer, "kernel_count": len(indices),
                                       "f0_cycles": sum(f0.cycles[index] for index in indices),
                                       "weight_refs": sum(meta[roi][index].weight_refs for index in indices),
                                       "weight_unique_64kb_pages": len(pages)}
                for metric in ("l1_tlb_misses", "l2_tlb_misses", "translation_walk_starts", "pte_requests", "pte_dram_responses"):
                    values = f0.values.get(metric)
                    row[f"f0_{metric}"] = sum(values[index] for index in indices) if values is not None else "UNATTRIBUTED"
                for family in ("F7", "F8"):
                    for lseg in ("5", "10", "20"):
                        candidate = arms[(roi, family, lseg)]
                        row[f"{family.lower()}_l{lseg}_cycle_delta_vs_f0"] = sum(candidate.cycles[index] - f0.cycles[index] for index in indices)
                        segment = candidate.values.get("weight_segment_hits")
                        row[f"{family.lower()}_l{lseg}_segment_hits"] = sum(segment[index] for index in indices) if segment is not None else "UNATTRIBUTED"
                        if family == "F8":
                            f7 = arms[(roi, "F7", lseg)]
                            row[f"f8_l{lseg}_cycle_delta_vs_f7"] = sum(candidate.cycles[index] - f7.cycles[index] for index in indices)
                summary.append(row)
            for family in ("F7", "F8"):
                for lseg in ("5", "10", "20"):
                    per_layer = []
                    for layer, indices in sorted(layer_to_indices.items()):
                        candidate = arms[(roi, family, lseg)]
                        per_layer.append((layer, sum(candidate.cycles[index] - f0.cycles[index] for index in indices)))
                    deltas = [value for _, value in per_layer]
                    if not deltas:
                        continue
                    magnitude = sum(abs(value) for value in deltas)
                    sorted_abs = sorted((abs(value) for value in deltas), reverse=True)
                    maximum = max(per_layer, key=lambda item: abs(item[1]))
                    robustness.append({"roi": roi, "operator_class": operator, "family": family, "lseg": lseg,
                                       "layer_count": len(deltas), "improve_layers": sum(value < 0 for value in deltas),
                                       "regress_layers": sum(value > 0 for value in deltas), "tie_layers": sum(value == 0 for value in deltas),
                                       "median_cycle_delta": fmt(statistics.median(deltas)), "p25_cycle_delta": fmt(percentile(deltas, .25)),
                                       "p75_cycle_delta": fmt(percentile(deltas, .75)), "min_cycle_delta": min(deltas), "max_cycle_delta": max(deltas),
                                       "max_abs_layer_id": maximum[0], "max_abs_layer_delta": maximum[1],
                                       "max_abs_layer_share": fmt(abs(maximum[1]) / magnitude if magnitude else 0),
                                       "top4_abs_layer_share": fmt(sum(sorted_abs[:4]) / magnitude if magnitude else 0),
                                       "outlier_signal": "YES" if magnitude and abs(maximum[1]) / magnitude >= .35 else "NO",
                                       "scope": "DIRECT_PARAMETER_RANGE_LAYER_ONLY"})
    return summary, robustness


def write_documents(meta: dict[str, list[Meta]], arms: dict[tuple[str, str, str], Arm], summaries: dict[tuple[str, str], dict[str, Any]],
                    break_even: list[dict[str, Any]], identity: dict[str, bool], pwc: list[dict[str, Any]], robustness: list[dict[str, Any]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "PROVENANCE.md").write_text(f"""# C12 operator-aware mechanism deep-dive provenance

- Formal C12 source commit: `{SOURCE_COMMIT}` (`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`, 22/22 terminal PASS).
- Analysis branch input: accepted operator-aware final-review commit `247f11a9c52174d3294e701fca38a7e2aaa00dba`.
- Read-only inputs: 22 immutable `run.log` / `C12_ARM_VALIDATION.json` pairs, accepted 692/740 operator map, and existing trace-scan TSVs.
- No `accel-sim.out`, simulator replay, or trace scanner was invoked. No formal C12 asset was modified.
- Scope contract: lane references are not cache transactions; KERNEL-scope cache records are not TLB accesses; FULL_ROI_ONLY and FIXED_WINDOW_PARTIAL records are not apportioned to kernels.
""")
    (OUT / "CHANGED_FILES.md").write_text("""# C12 operator-aware mechanism deep-dive changed files

- `util/vm_tlb/analyze_c12_operator_aware_deep_dive.py` — read-only raw-log and accepted-table deep-dive parser.
- This review pack's TSVs and reports — lightweight derived analysis only.

No raw log, trace, configuration, registration, binary, Core, or formal C12 review artifact is modified or committed.
""")
    summary_lines = []
    for (roi, comparison), value in sorted(summaries.items()):
        summary_lines.append(f"| {roi} | {comparison} | {value['changed_kernels']}/{value['kernel_count']} | {value['top10_abs_fraction']:.3f} | {value['n50_abs']} / {value['n80_abs']} / {value['n90_abs']} |")
    (OUT / "KERNEL_CRITICALITY_FINDINGS.md").write_text("""# Kernel criticality / Pareto findings

`KERNEL_DELTA_RANKING.tsv` ranks each exact per-kernel cycle delta independently as improvement, regression, and absolute contribution. `KERNEL_DELTA_PARETO.tsv` records cumulative shares and the kernel counts required to reach 50/80/90% of each contribution magnitude.

| ROI | comparison | changed kernels | Top-10 absolute share | kernels to 50/80/90% |
| --- | --- | ---: | ---: | --- |
""" + "\n".join(summary_lines) + """

Interpretation boundary: concentration describes where the measured cycle delta occurs. It is not a causal attribution to a single translation/cache mechanism. Zero-delta Decode F8-vs-F7 rows are represented explicitly rather than ranked as artificial ties.
""")
    full_break = [row for row in break_even if row["operator_class"] == "FULL_ROI"]
    break_lines = "\n".join(f"| {row['roi']} | {row['family']} | {row['delta_lseg5']} | {row['delta_lseg10']} | {row['delta_lseg20']} | {row['break_even_lseg']} | {row['determination']} |" for row in full_break)
    (OUT / "SEGMENT_BREAK_EVEN_FINDINGS.md").write_text("""# Segment empirical break-even findings

Only measured Lseg=5/10/20 points and bracketed piecewise-linear crossings are used. A crossing is `EMPIRICAL_INTERPOLATION_ONLY`, not an extrapolated physical law.

| ROI | family | delta@5 | delta@10 | delta@20 | empirical break-even Lseg | status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
""" + break_lines + """

The full-ROI rows bound the observed setting range in which Segment can be positive relative to F0. Operator rows in `SEGMENT_BREAK_EVEN.tsv` may differ; they localize exact cycle changes but do not establish a causal critical path.
""")
    identities = "; ".join(f"{name}={'IDENTICAL_ALL_740_KERNELS' if passed else 'NOT_IDENTICAL'}" for name, passed in sorted(identity.items()))
    (OUT / "SUBENTRY_EFFECTIVENESS_AUDIT.md").write_text(f"""# Sub-entry effectiveness audit

`SUBENTRY_EFFECTIVENESS.tsv` separates exact Sub-entry activity from exact per-kernel cycle and translation deltas for F1-vs-F2 and F8-vs-F7.

Decode F7/F8 kernel-cycle identity checks: {identities}.

High Sub-entry hit counts are not interpreted as critical-path savings. The audit only tests whether those same comparisons also show L2-TLB miss, PTW, PTE-DRAM, requester-latency, and cycle changes; any relationship remains an association unless directly observable as the same event.
""")
    pwc_full = [row for row in pwc if row["row_kind"] == "FULL_ROI"]
    pwc_lines = "\n".join(f"| {row['roi']} | {row['baseline_f0']} | {row['candidate_f5']} | {row['delta_f5_minus_f0']} |" for row in pwc_full)
    (OUT / "PWC_TRADEOFF_AUDIT.md").write_text("""# PWC tradeoff audit

F5-vs-F0 is compared with exact per-kernel TLB/PTW/PTE/PWC counters and a separate FULL_ROI cycle anchor. The physical configuration reduces L2-TLB capacity from 768 to 656 entries; the tables show the measured associated tradeoff but do not claim it is the unique causal mechanism.

| ROI | F0 full-ROI cycles | F5 full-ROI cycles | delta |
| --- | ---: | ---: | ---: |
""" + pwc_lines + """

`PWC_TRADEOFF.tsv` includes PWC accesses/hits/misses and top exact regression kernels. It can support a `SUPPORTED_MECHANISM_SIGNAL` when increased translation pressure and cycle regression co-occur; it cannot by itself prove counterfactual replacement causality.
""")
    outlier_count = sum(row["outlier_signal"] == "YES" for row in robustness)
    (OUT / "LAYER_ROBUSTNESS_FINDINGS.md").write_text(f"""# Layer robustness findings

Only kernels with `DIRECT_PARAMETER_RANGE` evidence and a direct layer id in 0–15 are included. Attention Core and Other Compute receive no layer assignment by execution order.

`LAYER_OPERATOR_SUMMARY.tsv` reports layer aggregates; `LAYER_ROBUSTNESS.tsv` reports improve/regress/tie counts, distribution statistics, and concentration. Across the reported (ROI, operator, family, Lseg) summaries, `{outlier_count}` meet the predeclared single-layer absolute-share outlier signal (>=35%). That is a concentration diagnostic, not a causal explanation.
""")
    (OUT / "CROSS_LAYER_DEEP_DIVE.md").write_text("""# Cross-layer mechanism deep dive

`OPERATOR_CROSS_LAYER_DECOMPOSITION.tsv` traces exact per-kernel aggregates through L1/L2 TLB, MSHR, PTW/PTE, requester latency, Segment/Sub-entry, and KERNEL-scope cache outcomes for every requested comparison.

The table supports measured co-movement only: cache transactions are not TLB accesses, TLB misses are not walks, and a counter change is not assigned as the cause of a cycle change. Queue/native-memory summaries remain excluded when their scope is not exact per kernel.
""")
    (OUT / "FINAL_REPORT.md").write_text("""# C12 operator-aware mechanism deep dive — final report

## Status

`C12_OPERATOR_AWARE_MECHANISM_DEEP_DIVE_COMPLETE_READY_FOR_REVIEW`

This is a read-only offline deep dive over the accepted 22-arm C12 data. It reuses the frozen 692/740 map and existing trace scan; it launches neither simulator nor trace scanner.

## MEASURED_DEEP_DIVE_FACT

- `KERNEL_DELTA_RANKING.tsv` and `KERNEL_DELTA_PARETO.tsv` identify exact per-kernel cycle-delta concentration for all requested comparisons.
- `OPERATOR_CROSS_LAYER_DECOMPOSITION.tsv` preserves exact per-kernel scope for translation and KERNEL cache outcomes, and preserves formal cycle anchors as `FULL_ROI_ONLY`.
- `SEGMENT_LATENCY_SENSITIVITY.tsv` uses only observed Lseg=5/10/20 points; `SEGMENT_BREAK_EVEN.tsv` labels each bracketed crossing as empirical interpolation only.
- Sub-entry and PWC analyses separate observable activity from performance benefit and retain zero-delta Decode F7/F8 identities explicitly.
- Layer analysis is restricted to frozen direct parameter-range layer evidence.

## SUPPORTED_MECHANISM_SIGNAL

Translation slow-path suppression, cache outcomes, and cycle movement can co-occur in the tables. The data support mechanism hypotheses and hotspot targeting, but not a unique causal path from a counter to performance.

## EMPIRICAL_INTERPOLATION_ONLY

Any Segment break-even value is a piecewise-linear crossing inside adjacent measured Lseg points. It is not extrapolated beyond 5–20 or claimed as a universal hardware law.

## UNRESOLVED

The raw evidence cannot make FULL_ROI-only queue/native-memory fields per-kernel, cannot turn KV-range/cache-class observations into semantic FFN/Embedding KV use, and cannot prove that a high-activity mechanism lies on the critical path.

## Next simulator hypotheses

1. Sweep Segment lookup latency tightly around the observed, bracketed full-ROI break-even for Prefill and Decode separately.
2. Instrument / perturb the highest absolute-delta FFN and Attention Projection kernels to test whether their translation-to-cycle association is critical-path causal.
3. Re-run F5 with independent L2-TLB-capacity and PWC toggles to separate capacity cost from physical-PWC benefit.
""")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    meta, arms, _scans = build_inputs()
    ranking, pareto, summaries = ranking_rows(meta, arms)
    cross = cross_layer_rows(meta, arms)
    sensitivity, break_even = segment_rows(meta, arms)
    subentry, identity = subentry_rows(meta, arms)
    pwc = pwc_rows(meta, arms)
    layer_summary, robustness = layer_rows(meta, arms)
    write_tsv(OUT / "KERNEL_DELTA_RANKING.tsv", [
        "roi", "comparison", "ranking_mode", "rank", "compute_index", "trace_filename", "semantic_kernel_name", "operator_class", "layer_id", "evidence_kind",
        "baseline_cycle", "candidate_cycle", "cycle_delta", "baseline_cycle_share", "l1_tlb_miss_delta", "l2_tlb_miss_delta", "translation_walk_delta",
        "pte_request_delta", "pte_dram_response_delta", "requester_translation_latency_delta", "segment_hit_delta", "segment_l2_suppressed_delta",
        "subentry_hit_delta", "subentry_miss_delta", "l1d_cache_tx_delta", "l2_cache_tx_delta", "l1d_reservation_fail_delta", "l2_reservation_fail_delta", "kernel_cache_outcome_delta",
    ], ranking)
    write_tsv(OUT / "KERNEL_DELTA_PARETO.tsv", [
        "row_kind", "roi", "comparison", "ranking_mode", "rank", "compute_index", "operator_class", "layer_id", "cycle_delta", "contribution_magnitude",
        "cumulative_magnitude", "cumulative_fraction", "top10_cumulative_fraction", "top20_cumulative_fraction", "top50_cumulative_fraction", "kernels_to_50pct", "kernels_to_80pct", "kernels_to_90pct",
    ], pareto)
    write_tsv(OUT / "OPERATOR_CROSS_LAYER_DECOMPOSITION.tsv", ["roi", "comparison", "row_kind", "operator_class", "metric", "metric_scope", "baseline_value", "candidate_value", "delta", "note"], cross)
    write_tsv(OUT / "SEGMENT_LATENCY_SENSITIVITY.tsv", ["roi", "family", "lseg", "operator_class", "metric", "metric_scope", "baseline_f0_value", "candidate_value", "delta_vs_f0", "segment_hits", "segment_l2_suppressed", "finite_difference_from_prior", "note"], sensitivity)
    write_tsv(OUT / "SEGMENT_BREAK_EVEN.tsv", ["roi", "family", "operator_class", "delta_lseg5", "delta_lseg10", "delta_lseg20", "signs", "monotonicity", "break_even_lseg", "determination", "evidence_tier", "note"], break_even)
    write_tsv(OUT / "SUBENTRY_EFFECTIVENESS.tsv", ["row_kind", "roi", "comparison", "rank", "compute_index", "operator_class", "layer_id", "metric", "baseline_value", "candidate_value", "delta", "note"], subentry)
    write_tsv(OUT / "PWC_TRADEOFF.tsv", ["row_kind", "roi", "operator_class", "rank", "compute_index", "metric", "baseline_f0", "candidate_f5", "delta_f5_minus_f0", "note"], pwc)
    write_tsv(OUT / "LAYER_OPERATOR_SUMMARY.tsv", [
        "roi", "operator_class", "layer_id", "kernel_count", "f0_cycles", "weight_refs", "weight_unique_64kb_pages",
        "f0_l1_tlb_misses", "f0_l2_tlb_misses", "f0_translation_walk_starts", "f0_pte_requests", "f0_pte_dram_responses",
        *[f"{family.lower()}_l{lseg}_cycle_delta_vs_f0" for family in ("F7", "F8") for lseg in ("5", "10", "20")],
        *[f"{family.lower()}_l{lseg}_segment_hits" for family in ("F7", "F8") for lseg in ("5", "10", "20")],
        *[f"f8_l{lseg}_cycle_delta_vs_f7" for lseg in ("5", "10", "20")],
    ], layer_summary)
    write_tsv(OUT / "LAYER_ROBUSTNESS.tsv", ["roi", "operator_class", "family", "lseg", "layer_count", "improve_layers", "regress_layers", "tie_layers", "median_cycle_delta", "p25_cycle_delta", "p75_cycle_delta", "min_cycle_delta", "max_cycle_delta", "max_abs_layer_id", "max_abs_layer_delta", "max_abs_layer_share", "top4_abs_layer_share", "outlier_signal", "scope"], robustness)
    write_documents(meta, arms, summaries, break_even, identity, pwc, robustness)
    print(f"PASS deep-dive outputs: {OUT}")
    print(f"accepted_arms={len(arms)} no_trace_scan_or_replay=true")


if __name__ == "__main__":
    main()
