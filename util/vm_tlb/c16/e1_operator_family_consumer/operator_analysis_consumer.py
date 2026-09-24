#!/usr/bin/env python3
"""Run-aligned analysis for the frozen C16 E1 operator-family experiment.

The consumer deliberately accepts normalized raw rows, not producer summary
tables.  Sums and ratios are formed inside each (rep, decode-index) alignment
cell before stable D1--D3 and cross-run aggregation.  Host API durations are
reported separately and are never subtracted from GPU event timings.
"""
from __future__ import annotations

import math
import statistics
from typing import Any, Mapping, Sequence


class OperatorAnalysisError(ValueError):
    """Raw evidence does not satisfy the frozen consumer contract."""


EXPECTED_REPS = 7
LAYERS = tuple(range(28))
ROLES = ("gate_proj", "up_proj", "down_proj")
DECODE_INDICES = (0, 1, 2, 3)
STABLE_DECODE_INDICES = (1, 2, 3)
LOCAL_BENEFIT_MIN = 0.05
SYSTEM_BENEFIT_MIN = 0.02
FULLHINT_MATERIAL_FRACTION = 0.50
FULLHINT_BENEFIT_MAX_EXCLUSIVE = 0.02
FULLHINT_NCU_CHANGE_MIN = 0.005

FAMILY_ROLES = {
    "GATE28": ("gate_proj",),
    "UP28": ("up_proj",),
    "DOWN28": ("down_proj",),
    "GU56": ("gate_proj", "up_proj"),
    "GD56": ("gate_proj", "down_proj"),
    "UD56": ("up_proj", "down_proj"),
    "GUD84": ROLES,
}
FAMILY_ORDER = tuple(FAMILY_ROLES)
PRIMARY_PAIRS = {
    family: (f"CONTROL_{family}", f"FAIR_{family}")
    for family in FAMILY_ORDER
}
FULLHINT_PAIR = ("CONTROL_FULL_GUD84", "FULLHINT_GUD84")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorAnalysisError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise OperatorAnalysisError(f"invalid {label}: boolean")
    token = str(value).strip()
    try:
        result = int(token)
    except (TypeError, ValueError) as exc:
        raise OperatorAnalysisError(f"invalid {label}: {value!r}") from exc
    if token not in {str(result), f"{result}.0"}:
        raise OperatorAnalysisError(f"non-integral {label}: {value!r}")
    return result


def _finite(value: Any, label: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise OperatorAnalysisError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(result):
        raise OperatorAnalysisError(f"nonfinite {label}: {value!r}")
    if positive and result <= 0.0:
        raise OperatorAnalysisError(f"nonpositive {label}: {value!r}")
    if nonnegative and result < 0.0:
        raise OperatorAnalysisError(f"negative {label}: {value!r}")
    return result


def _percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower, upper = math.floor(position), math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _stats(values: Sequence[float]) -> dict[str, Any]:
    checked = [_finite(value, "sample") for value in values]
    if not checked:
        raise OperatorAnalysisError("empty sample vector")
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


def _effect(control: Sequence[float], fair: Sequence[float]) -> dict[str, Any]:
    if len(control) != len(fair) or not control:
        raise OperatorAnalysisError("unmatched timing vectors")
    cstats, fstats = _stats(control), _stats(fair)
    if cstats["median"] <= 0.0:
        raise OperatorAnalysisError("nonpositive CONTROL median")
    benefit = (cstats["median"] - fstats["median"]) / cstats["median"]
    combined = math.hypot(cstats["cv"], fstats["cv"])
    return {
        "control": cstats,
        "fair": fstats,
        "benefit_fraction": benefit,
        "combined_dispersion": combined,
        "positive_beyond_dispersion": benefit > 0.0 and benefit > combined,
    }


def _ratio(numerator: float, denominator: float) -> tuple[float | None, str]:
    if denominator > 0.0:
        return numerator / denominator, "DEFINED_POSITIVE_DENOMINATOR"
    if denominator == 0.0:
        return None, "UNDEFINED_ZERO_DENOMINATOR"
    return None, "UNDEFINED_NEGATIVE_DENOMINATOR"


def _selected_roles(raw: Any, expected: Sequence[str], label: str) -> tuple[str, ...]:
    if not isinstance(raw, list):
        raise OperatorAnalysisError(f"{label} selected_roles must be a list")
    result = tuple(_text(value, f"{label}.selected_roles") for value in raw)
    if len(set(result)) != len(result) or result != tuple(expected):
        raise OperatorAnalysisError(f"{label} selected role family mismatch")
    return result


def _normalize_run(run: Mapping[str, Any], condition: str,
                   selected_roles: Sequence[str]) -> dict[str, Any]:
    rep = _integer(run.get("rep"), f"{condition}.rep")
    rows = run.get("ffn_occurrences", run.get("occurrences"))
    if not isinstance(rows, list):
        raise OperatorAnalysisError(f"missing ffn_occurrences in {condition}/rep{rep}")
    occurrences: dict[tuple[int, str, int], float] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise OperatorAnalysisError("invalid FFN occurrence row")
        layer = _integer(row.get("layer_index"), "layer_index")
        role = _text(row.get("role"), "role")
        decode = _integer(row.get("decode_index"), "decode_index")
        key = (layer, role, decode)
        if layer not in LAYERS or role not in ROLES or decode not in DECODE_INDICES:
            raise OperatorAnalysisError(f"wrong FFN occurrence identity: {key!r}")
        if key in occurrences:
            raise OperatorAnalysisError(f"duplicate FFN occurrence: {key!r}")
        occurrences[key] = _finite(row.get("timing_ms"), "FFN timing_ms", positive=True)
    expected = {(layer, role, decode) for layer in LAYERS
                for role in ROLES for decode in DECODE_INDICES}
    if set(occurrences) != expected:
        raise OperatorAnalysisError(f"all-84 D0-D3 FFN matrix mismatch in {condition}/rep{rep}")

    decode_rows = run.get("decode_steps")
    if not isinstance(decode_rows, list):
        raise OperatorAnalysisError(f"missing decode_steps in {condition}/rep{rep}")
    decode_steps: dict[int, float] = {}
    for row in decode_rows:
        if not isinstance(row, Mapping):
            raise OperatorAnalysisError("invalid decode-step row")
        decode = _integer(row.get("decode_index"), "decode_index")
        if decode not in DECODE_INDICES or decode in decode_steps:
            raise OperatorAnalysisError(f"duplicate/out-of-range decode step: {decode}")
        decode_steps[decode] = _finite(row.get("timing_ms"), "decode timing_ms", positive=True)
    if set(decode_steps) != set(DECODE_INDICES):
        raise OperatorAnalysisError(f"D0-D3 decode-step matrix mismatch in {condition}/rep{rep}")

    overhead_rows = run.get("policy_overheads")
    receipt = run.get("policy_receipt")
    raw_receipt_mode = overhead_rows is None and isinstance(receipt, Mapping)
    if raw_receipt_mode:
        if tuple(receipt.get("selected_roles", ())) != tuple(selected_roles):
            raise OperatorAnalysisError(f"{condition} receipt selected role family mismatch")
        overhead_rows = receipt.get("switches")
    if not isinstance(overhead_rows, list):
        raise OperatorAnalysisError(
            f"missing policy_overheads or policy_receipt.switches in {condition}/rep{rep}")
    expected_updates = 5 * 28 * len(selected_roles)  # PREFILL plus D0--D3.
    if len(overhead_rows) != expected_updates:
        raise OperatorAnalysisError(
            f"policy overhead update count mismatch in {condition}/rep{rep}: "
            f"expected {expected_updates}, got {len(overhead_rows)}")
    overhead_us = []
    seen_updates: set[int] = set()
    for position, row in enumerate(overhead_rows):
        if not isinstance(row, Mapping):
            raise OperatorAnalysisError("invalid policy overhead row")
        # Raw policy receipts attach updates by phase/natural-call index; their
        # list position is the already validated ordered update index.  The
        # normalized schema carries update_index explicitly.
        index = position if raw_receipt_mode else _integer(row.get("update_index"), "update_index")
        if index not in range(expected_updates) or index in seen_updates:
            raise OperatorAnalysisError("duplicate/out-of-range policy overhead update")
        seen_updates.add(index)
        if raw_receipt_mode:
            if "api_duration_us" not in row:
                raise OperatorAnalysisError("raw policy receipt lacks api_duration_us")
            value = row.get("api_duration_us")
        else:
            if _text(row.get("unit"), "policy overhead unit") != "us":
                raise OperatorAnalysisError("policy overhead unit mismatch; exact unit must be us")
            value = row.get("duration")
        overhead_us.append(_finite(value, "policy overhead duration", nonnegative=True))
    if raw_receipt_mode:
        reported_total = _finite(receipt.get("total_api_duration_us"),
                                 "total_api_duration_us", nonnegative=True)
        if not math.isclose(reported_total, sum(overhead_us), rel_tol=1e-12, abs_tol=1e-9):
            raise OperatorAnalysisError("raw policy API total duration mismatch")
    return {
        "rep": rep,
        "occurrences": occurrences,
        "decode_steps": decode_steps,
        "policy_overhead_us": overhead_us,
    }


def _normalize_condition(raw: Mapping[str, Any], condition: str,
                         selected_roles: Sequence[str], *,
                         fullhint: bool = False) -> dict[int, dict[str, Any]]:
    if "selected_roles" in raw:
        _selected_roles(raw.get("selected_roles"), selected_roles, condition)
    else:
        runs_for_identity = raw.get("runs")
        if not isinstance(runs_for_identity, list) or any(
                not isinstance(run, Mapping) or
                not isinstance(run.get("policy_receipt"), Mapping) or
                tuple(run["policy_receipt"].get("selected_roles", ())) != tuple(selected_roles)
                for run in runs_for_identity):
            raise OperatorAnalysisError(f"{condition} selected role family authority missing")
    if fullhint:
        if "hit_ratio" in raw:
            ratios = [_finite(raw.get("hit_ratio"), f"{condition}.hit_ratio")]
        else:
            ratios = []
            for run in raw.get("runs", []):
                receipt = run.get("policy_receipt") if isinstance(run, Mapping) else None
                switches = receipt.get("switches") if isinstance(receipt, Mapping) else None
                if not isinstance(switches, list):
                    raise OperatorAnalysisError("FULLHINT hitRatio authority missing")
                ratios.extend(_finite(row.get("hit_ratio"), "FULLHINT hit_ratio")
                              for row in switches if isinstance(row, Mapping))
        if not ratios or any(not math.isclose(ratio, 1.0, rel_tol=0.0, abs_tol=1e-12)
                             for ratio in ratios):
            raise OperatorAnalysisError("FULLHINT matrix must use hitRatio=1")
    runs = raw.get("runs")
    if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
        raise OperatorAnalysisError(f"{condition} must contain exactly {EXPECTED_REPS} runs")
    result: dict[int, dict[str, Any]] = {}
    for raw_run in runs:
        if not isinstance(raw_run, Mapping):
            raise OperatorAnalysisError(f"invalid run in {condition}")
        run = _normalize_run(raw_run, condition, selected_roles)
        rep = run["rep"]
        if rep not in range(EXPECTED_REPS) or rep in result:
            raise OperatorAnalysisError(f"duplicate/out-of-range rep in {condition}: {rep}")
        result[rep] = run
    if set(result) != set(range(EXPECTED_REPS)):
        raise OperatorAnalysisError(f"rep matrix mismatch in {condition}")
    return result


def _normalize_document(document: Mapping[str, Any],
                        pairs: Mapping[str, tuple[str, str]], *,
                        fullhint: bool = False) -> dict[str, dict[int, dict[str, Any]]]:
    if document.get("schema_version") != 1:
        raise OperatorAnalysisError("unsupported operator analysis schema_version")
    rows = document.get("conditions")
    if not isinstance(rows, list):
        raise OperatorAnalysisError("conditions must be a list")
    expected_names = {name for pair in pairs.values() for name in pair}
    raw_by_name: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise OperatorAnalysisError("invalid condition row")
        name = _text(row.get("condition"), "condition")
        if name not in expected_names or name in raw_by_name:
            raise OperatorAnalysisError(f"unknown/duplicate condition: {name}")
        raw_by_name[name] = row
    if set(raw_by_name) != expected_names:
        raise OperatorAnalysisError("condition matrix mismatch")
    result = {}
    for family, pair in pairs.items():
        roles = FAMILY_ROLES[family]
        for name in pair:
            result[name] = _normalize_condition(raw_by_name[name], name, roles,
                                                fullhint=fullhint)
    return result


def _analyze_pair(family: str, control_name: str, fair_name: str,
                  conditions: Mapping[str, Mapping[int, Mapping[str, Any]]]) -> dict[str, Any]:
    selected_roles = FAMILY_ROLES[family]
    unselected_roles = tuple(role for role in ROLES if role not in selected_roles)
    control, fair = conditions[control_name], conditions[fair_name]
    decode_rows: list[dict[str, Any]] = []
    stable_rows: list[dict[str, Any]] = []
    for rep in range(EXPECTED_REPS):
        current_rows = []
        for decode in STABLE_DECODE_INDICES:
            cocc, focc = control[rep]["occurrences"], fair[rep]["occurrences"]
            role_savings = {}
            role_control = {}
            role_fair = {}
            for role in ROLES:
                role_control[role] = sum(cocc[(layer, role, decode)] for layer in LAYERS)
                role_fair[role] = sum(focc[(layer, role, decode)] for layer in LAYERS)
                role_savings[role] = role_control[role] - role_fair[role]
            cselected = sum(role_control[role] for role in selected_roles)
            fselected = sum(role_fair[role] for role in selected_roles)
            cunselected = sum(role_control[role] for role in unselected_roles)
            funselected = sum(role_fair[role] for role in unselected_roles)
            cdecode = control[rep]["decode_steps"][decode]
            fdecode = fair[rep]["decode_steps"][decode]
            direct = cselected - fselected
            unselected = cunselected - funselected
            total = direct + unselected
            observed = cdecode - fdecode
            residual = observed - total
            selected_realization, selected_status = _ratio(observed, direct)
            ffn_realization, ffn_status = _ratio(observed, total)
            row = {
                "rep": rep,
                "decode_index": decode,
                "control_selected_timing_ms": cselected,
                "selected_share": cselected / cdecode,
                "direct_selected_saving_ms": direct,
                "unselected_ffn_saving_ms": unselected,
                "total_ffn_saving_ms": total,
                "observed_decode_saving_ms": observed,
                "outside_ffn_residual_ms": residual,
                "outside_ffn_residual_interpretation":
                    "UNATTRIBUTED_OUTSIDE_MEASURED_FFN_OR_OVERLAP_ACCOUNTING",
                "selected_realization": selected_realization,
                "selected_realization_status": selected_status,
                "ffn_realization": ffn_realization,
                "ffn_realization_status": ffn_status,
                "control_decode_timing_ms": cdecode,
                "fair_decode_timing_ms": fdecode,
                "role_saving_ms": role_savings,
            }
            decode_rows.append(row)
            current_rows.append(row)

        def mean(field: str) -> float:
            return statistics.fmean(row[field] for row in current_rows)

        direct, total, observed = (mean("direct_selected_saving_ms"),
                                   mean("total_ffn_saving_ms"),
                                   mean("observed_decode_saving_ms"))
        control_selected = mean("control_selected_timing_ms")
        control_decode = mean("control_decode_timing_ms")
        selected_realization, selected_status = _ratio(observed, direct)
        ffn_realization, ffn_status = _ratio(observed, total)
        stable_rows.append({
            "rep": rep,
            "selected_share": control_selected / control_decode,
            "direct_selected_saving_ms": direct,
            "direct_selected_saving_fraction_of_control_decode": direct / control_decode,
            "unselected_ffn_saving_ms": mean("unselected_ffn_saving_ms"),
            "total_ffn_saving_ms": total,
            "observed_decode_saving_ms": observed,
            "outside_ffn_residual_ms": mean("outside_ffn_residual_ms"),
            "outside_ffn_residual_interpretation":
                "UNATTRIBUTED_OUTSIDE_MEASURED_FFN_OR_OVERLAP_ACCOUNTING",
            "selected_realization": selected_realization,
            "selected_realization_status": selected_status,
            "ffn_realization": ffn_realization,
            "ffn_realization_status": ffn_status,
            "control_decode_timing_ms": control_decode,
            "fair_decode_timing_ms": mean("fair_decode_timing_ms"),
            "role_saving_ms": {role: statistics.fmean(row["role_saving_ms"][role]
                                                       for row in current_rows)
                               for role in ROLES},
        })

    local_effects = []
    for role in selected_roles:
        for layer in LAYERS:
            c = [control[rep]["occurrences"][(layer, role, 3)]
                 for rep in range(EXPECTED_REPS)]
            f = [fair[rep]["occurrences"][(layer, role, 3)]
                 for rep in range(EXPECTED_REPS)]
            effect = _effect(c, f)
            material = (effect["benefit_fraction"] >= LOCAL_BENEFIT_MIN and
                        effect["benefit_fraction"] > effect["combined_dispersion"])
            local_effects.append({"layer_index": layer, "role": role,
                                  **effect, "material_local": material})

    cstable = [statistics.fmean(control[rep]["decode_steps"][d]
                                for d in STABLE_DECODE_INDICES)
               for rep in range(EXPECTED_REPS)]
    fstable = [statistics.fmean(fair[rep]["decode_steps"][d]
                                for d in STABLE_DECODE_INDICES)
               for rep in range(EXPECTED_REPS)]
    whole = _effect(cstable, fstable)
    whole["material_system"] = (whole["benefit_fraction"] >= SYSTEM_BENEFIT_MIN and
                                whole["benefit_fraction"] > whole["combined_dispersion"])
    material_count = sum(bool(row["material_local"]) for row in local_effects)
    summaries = {}
    for field in ("selected_share", "direct_selected_saving_ms",
                  "direct_selected_saving_fraction_of_control_decode",
                  "unselected_ffn_saving_ms", "total_ffn_saving_ms",
                  "observed_decode_saving_ms", "outside_ffn_residual_ms"):
        summaries[field] = _stats([row[field] for row in stable_rows])
    for field in ("selected_realization", "ffn_realization"):
        defined = [row[field] for row in stable_rows if row[field] is not None]
        summaries[field] = {
            "unclamped": True,
            "defined_run_count": len(defined),
            "undefined_run_count": EXPECTED_REPS - len(defined),
            "defined_run_summary": _stats(defined) if defined else None,
        }
    role_summary = {role: _stats([row["role_saving_ms"][role] for row in stable_rows])
                    for role in ROLES}
    return {
        "family": family,
        "selected_roles": list(selected_roles),
        "selected_module_count": len(selected_roles) * len(LAYERS),
        "control_condition": control_name,
        "fair_condition": fair_name,
        "aggregation_authority": "RUN_ALIGNED_D1_D3_BEFORE_CROSS_RUN_AGGREGATION",
        "run_decode_metrics": decode_rows,
        "run_stable_metrics": stable_rows,
        "summaries": summaries,
        "role_saving_ms": role_summary,
        "selected_d3_module_effects": local_effects,
        "material_selected_count": material_count,
        "material_selected_fraction": material_count / len(local_effects),
        "whole_decode_stable_effect": whole,
    }


def analyze_operator_family(document: Mapping[str, Any]) -> dict[str, Any]:
    """Consume the exact fourteen-condition primary matrix."""
    conditions = _normalize_document(document, PRIMARY_PAIRS)
    points = {family: _analyze_pair(family, *PRIMARY_PAIRS[family], conditions)
              for family in FAMILY_ORDER}
    return {
        "schema_version": 1,
        "status": "PASS",
        "authority": "NORMALIZED_RAW_RUN_ALIGNED_TIMING_AND_OVERHEAD_ROWS",
        "points": points,
        "host_policy_overhead": analyze_host_overhead(conditions),
        "host_overhead_not_subtracted_from_gpu_timing": True,
    }


def analyze_host_overhead(
        conditions: Mapping[str, Mapping[int, Mapping[str, Any]]]) -> dict[str, Any]:
    """Report per-update, total-run, and matched CONTROL/FAIR CPU overhead."""
    points = {}
    for family, (control_name, fair_name) in PRIMARY_PAIRS.items():
        ctotals, ftotals = [], []
        cper, fper = [], []
        run_rows = []
        for rep in range(EXPECTED_REPS):
            cvalues = conditions[control_name][rep]["policy_overhead_us"]
            fvalues = conditions[fair_name][rep]["policy_overhead_us"]
            ctotal, ftotal = sum(cvalues), sum(fvalues)
            ctotals.append(ctotal)
            ftotals.append(ftotal)
            cper.extend(cvalues)
            fper.extend(fvalues)
            run_rows.append({
                "rep": rep,
                "control_total_us": ctotal,
                "fair_total_us": ftotal,
                "fair_minus_control_total_us": ftotal - ctotal,
            })
        deltas = [fair - control for control, fair in zip(ctotals, ftotals)]
        points[family] = {
            "unit": "us",
            "per_update": {"control": _stats(cper), "fair": _stats(fper)},
            "total_per_run": {"control": _stats(ctotals), "fair": _stats(ftotals)},
            "fair_minus_control_total_per_run_us": _stats(deltas),
            "run_aligned_totals": run_rows,
            "subtracted_from_gpu_timing": False,
        }
    return {"status": "PASS", "unit": "us", "points": points,
            "diagnostic_not_correction_formula": True}


def fullhint_trigger(gud84_point: Mapping[str, Any]) -> bool:
    try:
        fraction = _finite(gud84_point["material_selected_fraction"],
                           "GUD84 material selected fraction")
        benefit = _finite(gud84_point["whole_decode_stable_effect"]["benefit_fraction"],
                          "GUD84 whole-decode benefit")
    except (KeyError, TypeError) as exc:
        raise OperatorAnalysisError("incomplete GUD84 FULLHINT trigger authority") from exc
    if not 0.0 <= fraction <= 1.0:
        raise OperatorAnalysisError("GUD84 material selected fraction outside [0,1]")
    return fraction >= FULLHINT_MATERIAL_FRACTION and benefit < FULLHINT_BENEFIT_MAX_EXCLUSIVE


def consume_fullhint(gud84_point: Mapping[str, Any],
                     evidence: Mapping[str, Any] | None) -> dict[str, Any]:
    """Enforce the conditional two-condition FULLHINT_GUD84 matrix."""
    triggered = fullhint_trigger(gud84_point)
    if not triggered:
        if evidence is not None and evidence.get("conditions"):
            raise OperatorAnalysisError("FULLHINT evidence present when frozen trigger is false")
        return {"status": "PASS", "triggered": False,
                "producer_run_required": False, "producer_run_observed": False,
                "analysis": None, "additional_ncu_required": False}
    if evidence is None:
        raise OperatorAnalysisError("FULLHINT trigger true but evidence is missing")
    pairs = {"GUD84": FULLHINT_PAIR}
    conditions = _normalize_document(evidence, pairs, fullhint=True)
    point = _analyze_pair("GUD84", *FULLHINT_PAIR, conditions)
    fair_benefit = _finite(gud84_point["whole_decode_stable_effect"]["benefit_fraction"],
                           "FAIR_GUD84 benefit")
    full_benefit = point["whole_decode_stable_effect"]["benefit_fraction"]
    delta = full_benefit - fair_benefit
    return {
        "status": "PASS",
        "triggered": True,
        "producer_run_required": True,
        "producer_run_observed": True,
        "required_condition_matrix": list(FULLHINT_PAIR),
        "hit_ratio": 1.0,
        "hit_ratio_interpretation": "OVERSUBSCRIBED_POLICY_INTENT_NOT_EFFECTIVE_CAPACITY",
        "point": point,
        "fair_gud84_benefit_fraction": fair_benefit,
        "fullhint_gud84_benefit_fraction": full_benefit,
        "benefit_change_fraction": delta,
        "absolute_benefit_change_fraction": abs(delta),
        "additional_ncu_required": (
            abs(delta) >= FULLHINT_NCU_CHANGE_MIN or
            math.isclose(abs(delta), FULLHINT_NCU_CHANGE_MIN,
                         rel_tol=0.0, abs_tol=1e-9)
        ),
    }


def classify_stage(analysis: Mapping[str, Any], *,
                   policy_qualified: bool) -> dict[str, Any]:
    """Apply the exact frozen precedence and strict comparison boundaries."""
    if not policy_qualified:
        return {"status": "PASS",
                "stage_label": "POLICY_FAMILY_SCALING_UNQUALIFIED",
                "policy_qualified": False, "simulator_auto_authorized": False}
    try:
        points = analysis["points"]
        if set(points) != set(FAMILY_ORDER):
            raise OperatorAnalysisError("stage authority point matrix mismatch")
        system_relevant = []
        positive = []
        for family in FAMILY_ORDER:
            whole = points[family]["whole_decode_stable_effect"]
            benefit = _finite(whole["benefit_fraction"], f"{family} benefit")
            dispersion = _finite(whole["combined_dispersion"], f"{family} dispersion",
                                 nonnegative=True)
            if benefit >= SYSTEM_BENEFIT_MIN and benefit > dispersion:
                system_relevant.append(family)
            if benefit > 0.0 and benefit > dispersion:
                positive.append(family)
        gud = points["GUD84"]
        direct_fraction = _finite(
            gud["summaries"]["direct_selected_saving_fraction_of_control_decode"]["median"],
            "GUD84 run-aligned direct saving fraction")
        material_fraction = _finite(gud["material_selected_fraction"],
                                    "GUD84 material fraction")
        residual = _finite(gud["summaries"]["outside_ffn_residual_ms"]["median"],
                           "GUD84 residual")
    except (KeyError, TypeError) as exc:
        raise OperatorAnalysisError("incomplete stage-decision authority") from exc
    if not 0.0 <= material_fraction <= 1.0:
        raise OperatorAnalysisError("GUD84 material fraction outside [0,1]")
    collateral = (not system_relevant and direct_fraction >= SYSTEM_BENEFIT_MIN and
                  material_fraction >= FULLHINT_MATERIAL_FRACTION and residual < 0.0)
    if system_relevant:
        label = "OPERATOR_FAMILY_SYSTEM_RELEVANT"
    elif collateral:
        label = "OPERATOR_FAMILY_COLLATERAL_LIMITED"
    elif positive:
        label = "OPERATOR_FAMILY_POSITIVE_BUT_SUBTHRESHOLD"
    else:
        label = "OPERATOR_FAMILY_NOT_SUPPORTED"
    return {
        "status": "PASS",
        "stage_label": label,
        "policy_qualified": True,
        "system_relevant_families": system_relevant,
        "positive_beyond_dispersion_families": positive,
        "gud84_direct_selected_saving_fraction_of_control_decode": direct_fraction,
        "gud84_material_selected_fraction": material_fraction,
        "gud84_outside_ffn_residual_median_ms": residual,
        "negative_residual_interpretation":
            "MEASURED_FFN_SAVING_OFFSET_OUTSIDE_FFN_ACCOUNTING_CAUSE_UNESTABLISHED",
        "simulator_auto_authorized": False,
    }


def consume_stage(analysis: Mapping[str, Any], *, policy_qualified: bool,
                  fullhint_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    decision = classify_stage(analysis, policy_qualified=policy_qualified)
    if policy_qualified:
        try:
            fullhint = consume_fullhint(analysis["points"]["GUD84"], fullhint_evidence)
        except (KeyError, TypeError) as exc:
            raise OperatorAnalysisError("analysis lacks GUD84") from exc
    else:
        fullhint = {"status": "NOT_EVALUATED_POLICY_UNQUALIFIED", "triggered": None}
    return {"schema_version": 1, **decision, "fullhint": fullhint}
