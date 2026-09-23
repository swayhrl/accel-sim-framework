#!/usr/bin/env python3
"""Fail-closed run-aligned analysis for C16 E1 coverage scaling.

This module consumes normalized *raw per-run* timing evidence.  In
particular, it never reconstructs an Amdahl numerator from independently
aggregated layer medians.  Every selected/non-selected sum is formed inside a
single (condition, repetition, decode-index) row before any cross-run
aggregation.

Policy-receipt and semantic-SHA qualification are intentionally separate
consumers.  Their result is an explicit input to :func:`classify_stage`; it is
never inferred from timing data.
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from typing import Any, Mapping, Sequence


class CoverageAnalysisError(ValueError):
    """Raised when raw evidence or its frozen matrix fails closed."""


EXPECTED_REPS = 7
LAYERS = tuple(range(28))
STABLE_DECODE_INDICES = (1, 2, 3)
MATERIAL_TIMING_BENEFIT = 0.05
SYSTEM_BENEFIT = 0.02
FULLHINT_MATERIAL_FRACTION = 0.50
FULLHINT_BENEFIT_MAX_EXCLUSIVE = 0.02

SELECTION_ORDER = (
    0, 14, 27, 7, 20, 3, 10, 17, 23, 5, 12, 25, 1, 2,
    4, 6, 8, 9, 11, 13, 15, 16, 18, 19, 21, 22, 24, 26,
)
LAYER_SETS = {
    "N1": (0,),
    "N2": (0, 14),
    "N4": (0, 14, 27, 7),
    "N8": (0, 14, 27, 7, 20, 3, 10, 17),
    "N14A": (0, 14, 27, 7, 20, 3, 10, 17, 23, 5, 12, 25, 1, 2),
    "N28": SELECTION_ORDER,
    "N14B": (4, 6, 8, 9, 11, 13, 15, 16, 18, 19, 21, 22, 24, 26),
}
PRIMARY_AND_HOLDOUT = ("N1", "N2", "N4", "N8", "N14A", "N28", "N14B")
FULLHINT_CONDITIONS = (
    "CONTROL_FULL_N8", "FULLHINT_N8", "CONTROL_FULL_N28", "FULLHINT_N28",
)


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoverageAnalysisError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise CoverageAnalysisError(f"invalid {label}: boolean")
    token = str(value).strip()
    try:
        parsed = int(token)
    except (TypeError, ValueError) as exc:
        raise CoverageAnalysisError(f"invalid {label}: {value!r}") from exc
    if token not in {str(parsed), f"{parsed}.0"}:
        raise CoverageAnalysisError(f"non-integral {label}: {value!r}")
    return parsed


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise CoverageAnalysisError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed) or (positive and parsed <= 0.0):
        raise CoverageAnalysisError(f"nonfinite/nonpositive {label}: {value!r}")
    return parsed


def _stats(values: Sequence[float]) -> dict[str, Any]:
    checked = [_finite(value, "sample") for value in values]
    if not checked:
        raise CoverageAnalysisError("empty sample vector")
    mean = statistics.fmean(checked)
    return {
        "sample_count": len(checked),
        "samples": checked,
        "min": min(checked),
        "p25": _percentile(checked, 0.25),
        "median": statistics.median(checked),
        "p75": _percentile(checked, 0.75),
        "max": max(checked),
        "mean": mean,
        "cv": statistics.pstdev(checked) / abs(mean) if mean != 0.0 else None,
    }


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _timing_effect(control: Sequence[float], intervention: Sequence[float]) -> dict[str, Any]:
    if len(control) != len(intervention) or not control:
        raise CoverageAnalysisError("unmatched timing vectors")
    control_stats, intervention_stats = _stats(control), _stats(intervention)
    baseline = control_stats["median"]
    if baseline <= 0:
        raise CoverageAnalysisError("nonpositive control timing median")
    benefit = (baseline - intervention_stats["median"]) / baseline
    combined = math.hypot(control_stats["cv"], intervention_stats["cv"])
    return {
        "control": control_stats,
        "intervention": intervention_stats,
        "benefit_fraction": benefit,
        "combined_dispersion": combined,
        "positive_beyond_dispersion": benefit > 0.0 and benefit > combined,
    }


def _realization(observed: float, local_saving: float) -> tuple[float | None, str]:
    if local_saving > 0.0:
        # Deliberately not clamped: values below zero or above one are evidence.
        return observed / local_saving, "DEFINED_POSITIVE_DENOMINATOR"
    return None, "UNDEFINED_ZERO_DENOMINATOR" if local_saving == 0.0 else "UNDEFINED_NEGATIVE_DENOMINATOR"


def _selected_layers(raw: Any, expected: Sequence[int], label: str) -> tuple[int, ...]:
    if not isinstance(raw, list):
        raise CoverageAnalysisError(f"{label} selected_layers must be a list")
    parsed = tuple(_integer(value, f"{label}.selected_layers") for value in raw)
    if len(set(parsed)) != len(parsed):
        raise CoverageAnalysisError(f"duplicate layer in {label}")
    if parsed != tuple(expected):
        raise CoverageAnalysisError(f"{label} selected layer set mismatch")
    return parsed


def _condition_runs(raw: Mapping[str, Any], condition: str, expected_layers: Sequence[int]) -> dict[int, dict[str, Any]]:
    _selected_layers(raw.get("selected_layers"), expected_layers, condition)
    runs = raw.get("runs")
    if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
        raise CoverageAnalysisError(f"{condition} must contain exactly {EXPECTED_REPS} runs")
    out: dict[int, dict[str, Any]] = {}
    for run in runs:
        if not isinstance(run, Mapping):
            raise CoverageAnalysisError(f"invalid run in {condition}")
        rep = _integer(run.get("rep"), f"{condition}.rep")
        if rep not in range(EXPECTED_REPS) or rep in out:
            raise CoverageAnalysisError(f"duplicate/out-of-range rep in {condition}: {rep}")
        occurrences = run.get("occurrences")
        if not isinstance(occurrences, list):
            raise CoverageAnalysisError(f"missing occurrences in {condition}/rep{rep}")
        by_occurrence: dict[tuple[int, int], float] = {}
        for row in occurrences:
            if not isinstance(row, Mapping):
                raise CoverageAnalysisError("invalid occurrence row")
            layer = _integer(row.get("layer_index"), "layer_index")
            decode = _integer(row.get("decode_index"), "decode_index")
            if layer not in LAYERS or decode not in range(4):
                raise CoverageAnalysisError(f"wrong occurrence identity: {(layer, decode)!r}")
            if _text(row.get("role"), "role") != "up_proj":
                raise CoverageAnalysisError("coverage occurrence is not up_proj")
            key = (layer, decode)
            if key in by_occurrence:
                raise CoverageAnalysisError(f"duplicate occurrence in {condition}/rep{rep}: {key!r}")
            by_occurrence[key] = _finite(row.get("timing_ms"), "timing_ms", positive=True)
        expected_occurrences = {(layer, decode) for layer in LAYERS for decode in range(4)}
        if set(by_occurrence) != expected_occurrences:
            raise CoverageAnalysisError(f"all-28 occurrence matrix mismatch in {condition}/rep{rep}")
        decode_rows = run.get("decode_steps")
        if not isinstance(decode_rows, list):
            raise CoverageAnalysisError(f"missing decode_steps in {condition}/rep{rep}")
        by_decode: dict[int, float] = {}
        for row in decode_rows:
            if not isinstance(row, Mapping):
                raise CoverageAnalysisError("invalid decode row")
            decode = _integer(row.get("decode_index"), "decode_index")
            if decode not in range(4) or decode in by_decode:
                raise CoverageAnalysisError(f"duplicate/out-of-range decode step in {condition}/rep{rep}")
            by_decode[decode] = _finite(row.get("timing_ms"), "decode timing_ms", positive=True)
        if set(by_decode) != set(range(4)):
            raise CoverageAnalysisError(f"decode-step matrix mismatch in {condition}/rep{rep}")
        out[rep] = {"occurrences": by_occurrence, "decode_steps": by_decode}
    if set(out) != set(range(EXPECTED_REPS)):
        raise CoverageAnalysisError(f"rep matrix mismatch in {condition}")
    return out


def _normalize_conditions(document: Mapping[str, Any], pairs: Mapping[str, tuple[str, str]]) -> dict[str, dict[int, dict[str, Any]]]:
    if document.get("schema_version") != 1:
        raise CoverageAnalysisError("unsupported coverage analysis schema_version")
    raw_conditions = document.get("conditions")
    if not isinstance(raw_conditions, list):
        raise CoverageAnalysisError("conditions must be a list")
    expected_names = {name for pair in pairs.values() for name in pair}
    by_name: dict[str, Mapping[str, Any]] = {}
    for raw in raw_conditions:
        if not isinstance(raw, Mapping):
            raise CoverageAnalysisError("invalid condition entry")
        name = _text(raw.get("condition"), "condition")
        if name not in expected_names or name in by_name:
            raise CoverageAnalysisError(f"unknown/duplicate condition: {name}")
        by_name[name] = raw
    if set(by_name) != expected_names:
        missing = sorted(expected_names - set(by_name))
        raise CoverageAnalysisError(f"condition matrix mismatch; missing={missing}")
    normalized = {}
    for set_name, pair in pairs.items():
        expected_layers = LAYER_SETS[set_name]
        for name in pair:
            normalized[name] = _condition_runs(by_name[name], name, expected_layers)
    return normalized


def _analyze_pair(set_name: str, control_name: str, fair_name: str,
                  conditions: Mapping[str, Mapping[int, Mapping[str, Any]]]) -> dict[str, Any]:
    selected = LAYER_SETS[set_name]
    nonselected = tuple(layer for layer in LAYERS if layer not in set(selected))
    control, fair = conditions[control_name], conditions[fair_name]
    aligned_rows = []
    stable_by_run = []
    for rep in range(EXPECTED_REPS):
        per_decode = []
        for decode in STABLE_DECODE_INDICES:
            c_occ, f_occ = control[rep]["occurrences"], fair[rep]["occurrences"]
            c_selected = sum(c_occ[(layer, decode)] for layer in selected)
            f_selected = sum(f_occ[(layer, decode)] for layer in selected)
            c_nonselected = sum(c_occ[(layer, decode)] for layer in nonselected)
            f_nonselected = sum(f_occ[(layer, decode)] for layer in nonselected)
            c_decode = control[rep]["decode_steps"][decode]
            f_decode = fair[rep]["decode_steps"][decode]
            local_saving = c_selected - f_selected
            observed = c_decode - f_decode
            realization, status = _realization(observed, local_saving)
            row = {
                "rep": rep,
                "decode_index": decode,
                "control_selected_timing_ms": c_selected,
                "fair_selected_timing_ms": f_selected,
                "selected_target_share": c_selected / c_decode,
                "summed_local_saving_ms": local_saving,
                "control_decode_timing_ms": c_decode,
                "fair_decode_timing_ms": f_decode,
                "observed_decode_saving_ms": observed,
                "realization_ratio": realization,
                "realization_status": status,
                "control_nonselected_timing_ms": c_nonselected,
                "fair_nonselected_timing_ms": f_nonselected,
                "nonselected_saving_ms": c_nonselected - f_nonselected,
                "nonselected_benefit_fraction": ((c_nonselected - f_nonselected) / c_nonselected)
                if c_nonselected > 0.0 else None,
            }
            aligned_rows.append(row)
            per_decode.append(row)
        selected_control = statistics.fmean(row["control_selected_timing_ms"] for row in per_decode)
        selected_fair = statistics.fmean(row["fair_selected_timing_ms"] for row in per_decode)
        control_decode = statistics.fmean(row["control_decode_timing_ms"] for row in per_decode)
        fair_decode = statistics.fmean(row["fair_decode_timing_ms"] for row in per_decode)
        nonselected_control = statistics.fmean(row["control_nonselected_timing_ms"] for row in per_decode)
        nonselected_fair = statistics.fmean(row["fair_nonselected_timing_ms"] for row in per_decode)
        local_saving = selected_control - selected_fair
        observed = control_decode - fair_decode
        realization, status = _realization(observed, local_saving)
        stable_by_run.append({
            "rep": rep,
            "selected_target_share": selected_control / control_decode,
            "summed_local_saving_ms": local_saving,
            "observed_decode_saving_ms": observed,
            "realization_ratio": realization,
            "realization_status": status,
            "nonselected_saving_ms": nonselected_control - nonselected_fair,
            "nonselected_benefit_fraction": ((nonselected_control - nonselected_fair) / nonselected_control)
            if nonselected_control > 0.0 else None,
        })

    layer_effects = []
    for layer in selected:
        control_samples = [control[rep]["occurrences"][(layer, 3)] for rep in range(EXPECTED_REPS)]
        fair_samples = [fair[rep]["occurrences"][(layer, 3)] for rep in range(EXPECTED_REPS)]
        effect = _timing_effect(control_samples, fair_samples)
        material = (effect["benefit_fraction"] >= MATERIAL_TIMING_BENEFIT
                    and effect["benefit_fraction"] > effect["combined_dispersion"])
        layer_effects.append({"layer_index": layer, **effect, "material_local": material})
    material_count = sum(bool(item["material_local"]) for item in layer_effects)

    control_stable = [statistics.fmean(control[rep]["decode_steps"][d] for d in STABLE_DECODE_INDICES)
                      for rep in range(EXPECTED_REPS)]
    fair_stable = [statistics.fmean(fair[rep]["decode_steps"][d] for d in STABLE_DECODE_INDICES)
                   for rep in range(EXPECTED_REPS)]
    whole_effect = _timing_effect(control_stable, fair_stable)
    local_savings = [row["summed_local_saving_ms"] for row in stable_by_run]
    observed_savings = [row["observed_decode_saving_ms"] for row in stable_by_run]
    aggregate_local = statistics.median(local_savings)
    aggregate_observed = statistics.median(observed_savings)
    aggregate_realization, aggregate_status = _realization(aggregate_observed, aggregate_local)
    defined_realizations = [row["realization_ratio"] for row in stable_by_run
                            if row["realization_ratio"] is not None]
    nonselected_benefits = [row["nonselected_benefit_fraction"] for row in stable_by_run
                            if row["nonselected_benefit_fraction"] is not None]
    local_benefits = [item["benefit_fraction"] for item in layer_effects]
    return {
        "set_name": set_name,
        "selected_layers": list(selected),
        "control_condition": control_name,
        "intervention_condition": fair_name,
        "stable_decode_indices": list(STABLE_DECODE_INDICES),
        "aggregation_authority": "RUN_ALIGNED_RAW_ROWS_BEFORE_CROSS_RUN_AGGREGATION",
        "run_decode_metrics": aligned_rows,
        "run_stable_metrics": stable_by_run,
        "selected_target_share": _stats([row["selected_target_share"] for row in stable_by_run]),
        "summed_local_saving_ms": _stats(local_savings),
        "observed_decode_saving_ms": _stats(observed_savings),
        "realization_ratio": {
            "unclamped": True,
            "defined_run_count": len(defined_realizations),
            "undefined_run_count": EXPECTED_REPS - len(defined_realizations),
            "defined_run_summary": _stats(defined_realizations) if defined_realizations else None,
            "ratio_of_median_run_aligned_observed_to_local": aggregate_realization,
            "aggregate_status": aggregate_status,
        },
        "nonselected_aggregate_effect": {
            "nonselected_layer_count": len(nonselected),
            "benefit_fraction": _stats(nonselected_benefits) if nonselected_benefits else None,
            "saving_ms": _stats([row["nonselected_saving_ms"] for row in stable_by_run]),
        },
        "selected_layer_d3_effects": layer_effects,
        "selected_layer_benefit_distribution": _stats(local_benefits),
        "material_selected_layer_count": material_count,
        "material_selected_layer_fraction": material_count / len(selected),
        "whole_decode_stable_effect": whole_effect,
    }


def consume_coverage_runs(document: Mapping[str, Any]) -> dict[str, Any]:
    """Analyze frozen N1..N28 FAIR pairs plus N14B composition holdout."""
    pairs = {name: (f"CONTROL_{name}", f"FAIR_{name}") for name in PRIMARY_AND_HOLDOUT}
    conditions = _normalize_conditions(document, pairs)
    points = {name: _analyze_pair(name, *pairs[name], conditions) for name in PRIMARY_AND_HOLDOUT}
    return {
        "schema_version": 1,
        "status": "PASS",
        "authority": "RAW_RUN_ALIGNED_TIMING_ONLY",
        "selection_order": list(SELECTION_ORDER),
        "points": points,
        "n14_holdout": analyze_n14_holdout(points),
    }


def analyze_n14_holdout(points: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Publish N14A/N14B identically, without selecting or ranking a winner."""
    if set(("N14A", "N14B")) - set(points):
        raise CoverageAnalysisError("N14A/N14B holdout points are both required")
    out = {}
    for name in ("N14A", "N14B"):
        point = points[name]
        if tuple(point.get("selected_layers", ())) != LAYER_SETS[name]:
            raise CoverageAnalysisError(f"{name} holdout set mismatch")
        out[name] = {
            "selected_layers": list(LAYER_SETS[name]),
            "selected_target_share": point["selected_target_share"],
            "median_local_benefit": point["selected_layer_benefit_distribution"]["median"],
            "material_selected_layer_fraction": point["material_selected_layer_fraction"],
            "whole_decode_stable_effect": point["whole_decode_stable_effect"],
            "realization_ratio": point["realization_ratio"],
        }
    return {
        "status": "PASS",
        "comparison": out,
        "winner_selected": False,
        "ranking_performed": False,
        "interpretation": "SAME_COUNT_COMPOSITION_HOLDOUT_NO_WINNER_SELECTION",
    }


def fullhint_trigger(n28_point: Mapping[str, Any]) -> bool:
    try:
        fraction = _finite(n28_point["material_selected_layer_fraction"], "N28 material fraction")
        benefit = _finite(n28_point["whole_decode_stable_effect"]["benefit_fraction"], "N28 decode benefit")
    except (KeyError, TypeError) as exc:
        raise CoverageAnalysisError("incomplete N28 trigger authority") from exc
    return fraction >= FULLHINT_MATERIAL_FRACTION and benefit < FULLHINT_BENEFIT_MAX_EXCLUSIVE


def consume_fullhint(n28_point: Mapping[str, Any], evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    """Enforce the conditional four-condition N8/N28 FULLHINT matrix."""
    triggered = fullhint_trigger(n28_point)
    if not triggered:
        if evidence is not None:
            conditions = evidence.get("conditions") if isinstance(evidence, Mapping) else None
            if conditions:
                raise CoverageAnalysisError("FULLHINT was run when frozen trigger was false")
        return {
            "status": "PASS", "triggered": False, "producer_run_required": False,
            "producer_run_observed": False, "analysis": None,
        }
    if evidence is None:
        raise CoverageAnalysisError("FULLHINT trigger true but evidence is missing")
    pairs = {
        "N8": ("CONTROL_FULL_N8", "FULLHINT_N8"),
        "N28": ("CONTROL_FULL_N28", "FULLHINT_N28"),
    }
    raw_conditions = evidence.get("conditions") if isinstance(evidence, Mapping) else None
    if not isinstance(raw_conditions, list):
        raise CoverageAnalysisError("FULLHINT conditions must be a list")
    for raw in raw_conditions:
        if not isinstance(raw, Mapping):
            raise CoverageAnalysisError("invalid FULLHINT condition")
        if not math.isclose(_finite(raw.get("hit_ratio"), "FULLHINT hit_ratio"), 1.0,
                            rel_tol=0.0, abs_tol=1e-12):
            raise CoverageAnalysisError("FULLHINT matrix must use hitRatio=1 oversubscribed intent")
    conditions = _normalize_conditions(evidence, pairs)
    points = {name: _analyze_pair(name, *pairs[name], conditions) for name in ("N8", "N28")}
    return {
        "status": "PASS",
        "triggered": True,
        "producer_run_required": True,
        "producer_run_observed": True,
        "required_condition_matrix": list(FULLHINT_CONDITIONS),
        "hit_ratio": 1.0,
        "hit_ratio_interpretation": "OVERSUBSCRIBED_INTENT_UNDER_FIXED_TOTAL_SETASIDE_NOT_EFFECTIVE_CAPACITY",
        "points": points,
    }


def classify_stage(n28_point: Mapping[str, Any], *, policy_qualified: bool) -> dict[str, Any]:
    """Apply STAGE_DECISION_PRECONTRACT exactly at its strict boundaries."""
    if not policy_qualified:
        return {
            "status": "PASS",
            "stage_label": "POLICY_SCALING_UNQUALIFIED",
            "policy_qualified": False,
            "simulator_auto_authorized": False,
        }
    try:
        whole = n28_point["whole_decode_stable_effect"]
        benefit = _finite(whole["benefit_fraction"], "N28 benefit")
        dispersion = _finite(whole["combined_dispersion"], "N28 combined dispersion")
        material_fraction = _finite(n28_point["material_selected_layer_fraction"], "N28 material fraction")
    except (KeyError, TypeError) as exc:
        raise CoverageAnalysisError("incomplete N28 stage authority") from exc
    if not 0.0 <= material_fraction <= 1.0:
        raise CoverageAnalysisError("N28 material fraction outside [0,1]")
    materially_positive = benefit > 0.0 and benefit > dispersion
    if materially_positive and benefit >= SYSTEM_BENEFIT:
        label = "COVERAGE_SCALING_SYSTEM_RELEVANT"
    elif materially_positive and benefit < SYSTEM_BENEFIT:
        label = "COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD"
    elif material_fraction >= FULLHINT_MATERIAL_FRACTION:
        label = "COVERAGE_SCALING_LOCAL_BUT_NOT_SYSTEMIC"
    else:
        label = "COVERAGE_SCALING_NOT_SUPPORTED"
    return {
        "status": "PASS",
        "stage_label": label,
        "policy_qualified": True,
        "n28_whole_decode_benefit_fraction": benefit,
        "n28_combined_dispersion": dispersion,
        "n28_materially_positive": materially_positive,
        "n28_material_selected_layer_fraction": material_fraction,
        "simulator_auto_authorized": False,
    }


def consume_stage_decision(coverage_analysis: Mapping[str, Any],
                           *, policy_qualified: bool,
                           fullhint_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Close timing label and conditional FULLHINT gate in one deterministic call."""
    try:
        n28 = coverage_analysis["points"]["N28"]
    except (KeyError, TypeError) as exc:
        raise CoverageAnalysisError("coverage analysis lacks N28") from exc
    decision = classify_stage(n28, policy_qualified=policy_qualified)
    fullhint = consume_fullhint(n28, fullhint_evidence) if policy_qualified else {
        "status": "NOT_EVALUATED_POLICY_UNQUALIFIED", "triggered": None,
    }
    return {"schema_version": 1, **decision, "fullhint": fullhint}
