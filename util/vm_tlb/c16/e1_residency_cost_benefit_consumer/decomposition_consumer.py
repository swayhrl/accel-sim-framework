#!/usr/bin/env python3
"""Fail-closed consumer for the E1 residency cost/benefit decomposition.

The input is normalized raw evidence.  All differences are formed within the
same fresh-process repetition and decode index before aggregation.  Top-level
MLP timing is deliberately not added to nested gate/up/down timing.
"""
from __future__ import annotations

import math
import statistics
from typing import Any, Mapping, Sequence


class DecompositionError(ValueError):
    """Evidence violates the frozen semantic or accounting contract."""


LAYERS = tuple(range(28))
ROLES = ("gate_proj", "up_proj", "down_proj")
LAYER_CATEGORIES = (
    "input_layernorm", "self_attn", "post_attention_layernorm", "mlp"
)
OPTIONAL_FINAL_CATEGORIES = ("final_norm", "output")
DECODE_INDICES = (0, 1, 2, 3)
STABLE_DECODE_INDICES = (1, 2, 3)
EXPECTED_REPS = 7
MAX_ABS_MEDIAN_RESIDUAL_MS = 0.10
LOCAL_UP_MIN = 0.05
SYSTEM_MIN = 0.02
LOCALIZATION_MIN = 0.80


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DecompositionError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise DecompositionError(f"invalid {label}: boolean")
    try:
        result = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise DecompositionError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() not in {str(result), f"{result}.0"}:
        raise DecompositionError(f"non-integral {label}: {value!r}")
    return result


def _finite(value: Any, label: str, *, positive: bool = False,
            nonnegative: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise DecompositionError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(result):
        raise DecompositionError(f"nonfinite {label}: {value!r}")
    if positive and result <= 0:
        raise DecompositionError(f"nonpositive {label}: {value!r}")
    if nonnegative and result < 0:
        raise DecompositionError(f"negative {label}: {value!r}")
    return result


def _stats(values: Sequence[float]) -> dict[str, Any]:
    checked = [_finite(v, "sample") for v in values]
    if not checked:
        raise DecompositionError("empty sample vector")
    mean = statistics.fmean(checked)
    return {
        "sample_count": len(checked), "samples": checked,
        "min": min(checked), "median": statistics.median(checked),
        "max": max(checked), "mean": mean,
        "cv": statistics.pstdev(checked) / abs(mean) if mean else None,
    }


def _effect(control: Sequence[float], fair: Sequence[float]) -> dict[str, Any]:
    if len(control) != len(fair) or not control:
        raise DecompositionError("unmatched effect vectors")
    c, f = _stats(control), _stats(fair)
    if c["median"] <= 0:
        raise DecompositionError("nonpositive CONTROL median")
    benefit = (c["median"] - f["median"]) / c["median"]
    dispersion = math.hypot(c["cv"], f["cv"])
    return {
        "control": c, "fair": f, "benefit_fraction": benefit,
        "combined_dispersion": dispersion,
        "positive_beyond_dispersion": benefit > 0 and benefit > dispersion,
    }


def validate_module_authority(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Validate runtime-discovered names without assuming Python attributes."""
    rows = raw.get("layers")
    if not isinstance(rows, list) or len(rows) != len(LAYERS):
        raise DecompositionError("module authority must contain exactly 28 layers")
    layers: dict[int, dict[str, str]] = {}
    names: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping):
            raise DecompositionError("invalid module authority layer row")
        layer = _integer(row.get("layer_index"), "layer_index")
        if layer not in LAYERS or layer in layers:
            raise DecompositionError("duplicate/out-of-range authority layer")
        categories = row.get("categories")
        if not isinstance(categories, Mapping) or set(categories) != set(LAYER_CATEGORIES):
            raise DecompositionError(f"missing self_attn/mlp or layer category at layer {layer}")
        normalized = {}
        for category in LAYER_CATEGORIES:
            name = _text(categories.get(category), f"layer {layer} {category}")
            if name in names:
                raise DecompositionError(f"duplicate runtime semantic module name: {name}")
            names.add(name)
            normalized[category] = name
        layers[layer] = normalized
    if set(layers) != set(LAYERS):
        raise DecompositionError("layer authority index matrix mismatch")

    finals_raw = raw.get("final_stages", [])
    if not isinstance(finals_raw, list):
        raise DecompositionError("final_stages must be a list")
    finals: dict[str, str] = {}
    for row in finals_raw:
        if not isinstance(row, Mapping):
            raise DecompositionError("invalid final-stage authority row")
        category = _text(row.get("category"), "final category")
        if category not in OPTIONAL_FINAL_CATEGORIES or category in finals:
            raise DecompositionError(f"unknown/duplicate final category: {category}")
        if row.get("cleanly_hookable") is not True:
            raise DecompositionError("uninstrumented final stage must not enter authority")
        name = _text(row.get("semantic_name"), f"{category} semantic_name")
        if name in names:
            raise DecompositionError("duplicate final-stage semantic name")
        names.add(name)
        finals[category] = name
    return {"layers": layers, "final_stages": finals,
            "authority_origin": "RUNTIME_DISCOVERED_AND_VERIFIED"}


def _sha(row: Mapping[str, Any], field: str, label: str) -> str:
    value = _text(row.get(field), f"{label}.{field}").lower()
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise DecompositionError(f"invalid {label}.{field}")
    return value


def _normalize_run(run: Mapping[str, Any], authority: Mapping[str, Any],
                   condition: str) -> dict[str, Any]:
    rep = _integer(run.get("rep"), f"{condition}.rep")
    tokens = run.get("generated_tokens")
    if not isinstance(tokens, list) or any(isinstance(v, bool) for v in tokens):
        raise DecompositionError(f"missing generated_tokens in {condition}/rep{rep}")
    tokens = tuple(_integer(v, "generated token") for v in tokens)
    if len(tokens) != 4:
        raise DecompositionError("exact four-token authority required")

    top_rows = run.get("top_level_occurrences")
    if not isinstance(top_rows, list):
        raise DecompositionError("missing top_level_occurrences")
    top: dict[tuple[int | None, str, int], dict[str, Any]] = {}
    ordered: dict[int, list[tuple[int | None, str]]] = {d: [] for d in DECODE_INDICES}
    intervals: dict[int, list[tuple[float, float, tuple[int | None, str]]]] = {
        d: [] for d in DECODE_INDICES
    }
    for row in top_rows:
        if not isinstance(row, Mapping):
            raise DecompositionError("invalid top-level occurrence")
        category = _text(row.get("category"), "top-level category")
        decode = _integer(row.get("decode_index"), "decode_index")
        if decode not in DECODE_INDICES:
            raise DecompositionError("top-level decode index mismatch")
        if category in LAYER_CATEGORIES:
            layer: int | None = _integer(row.get("layer_index"), "layer_index")
            if layer not in LAYERS:
                raise DecompositionError("top-level layer index mismatch")
            expected_name = authority["layers"][layer][category]
        elif category in authority["final_stages"]:
            if row.get("layer_index") is not None:
                raise DecompositionError("final stage must not carry layer_index")
            layer = None
            expected_name = authority["final_stages"][category]
        else:
            raise DecompositionError(f"top-level category outside authority: {category}")
        key = (layer, category, decode)
        if key in top:
            raise DecompositionError(f"duplicate top-level occurrence: {key}")
        if _text(row.get("semantic_name"), "semantic_name") != expected_name:
            raise DecompositionError(f"runtime semantic identity mismatch: {key}")
        start = _finite(row.get("start_ms"), "start_ms", nonnegative=True)
        end = _finite(row.get("end_ms"), "end_ms", nonnegative=True)
        if end <= start:
            raise DecompositionError("nonpositive top-level timing interval")
        duration = _finite(row.get("timing_ms"), "timing_ms", positive=True)
        if not math.isclose(duration, end - start, rel_tol=1e-9, abs_tol=1e-9):
            raise DecompositionError("top-level timing/interval mismatch")
        top[key] = {"timing_ms": duration,
                    "input_sha256": _sha(row, "input_sha256", "top-level"),
                    "output_sha256": _sha(row, "output_sha256", "top-level")}
        ordered[decode].append((layer, category))
        intervals[decode].append((start, end, (layer, category)))

    expected_top = {(layer, category, decode) for layer in LAYERS
                    for category in LAYER_CATEGORIES for decode in DECODE_INDICES}
    expected_top |= {(None, category, decode) for category in authority["final_stages"]
                     for decode in DECODE_INDICES}
    if set(top) != expected_top:
        raise DecompositionError("missing self_attn/mlp or top-level occurrence")
    for decode, values in intervals.items():
        by_start = sorted(values)
        for previous, current in zip(by_start, by_start[1:]):
            if current[0] < previous[1] - 1e-12:
                raise DecompositionError(
                    f"overlapping top-level ranges at D{decode}: {previous[2]} / {current[2]}")

    child_rows = run.get("ffn_child_occurrences")
    if not isinstance(child_rows, list):
        raise DecompositionError("missing ffn_child_occurrences")
    children: dict[tuple[int, str, int], dict[str, Any]] = {}
    for row in child_rows:
        if not isinstance(row, Mapping):
            raise DecompositionError("invalid FFN child occurrence")
        layer = _integer(row.get("layer_index"), "FFN layer_index")
        role = _text(row.get("role"), "FFN role")
        decode = _integer(row.get("decode_index"), "FFN decode_index")
        key = (layer, role, decode)
        if layer not in LAYERS or role not in ROLES or decode not in DECODE_INDICES:
            raise DecompositionError(f"wrong FFN child identity: {key}")
        if key in children:
            raise DecompositionError(f"duplicate FFN child: {key}")
        children[key] = {
            "timing_ms": _finite(row.get("timing_ms"), "FFN timing_ms", positive=True),
            "input_sha256": _sha(row, "input_sha256", "FFN child"),
            "output_sha256": _sha(row, "output_sha256", "FFN child"),
            "module_name": _text(row.get("module_name"), "FFN module_name"),
            "backend": _text(row.get("backend"), "FFN backend"),
        }
    expected_children = {(layer, role, decode) for layer in LAYERS
                         for role in ROLES for decode in DECODE_INDICES}
    if set(children) != expected_children:
        raise DecompositionError("all-84 D0-D3 FFN child matrix mismatch")

    decode_rows = run.get("decode_steps")
    if not isinstance(decode_rows, list):
        raise DecompositionError("missing decode_steps")
    decode_steps: dict[int, dict[str, Any]] = {}
    for row in decode_rows:
        decode = _integer(row.get("decode_index"), "decode index")
        if decode not in DECODE_INDICES or decode in decode_steps:
            raise DecompositionError("duplicate/out-of-range decode step")
        decode_steps[decode] = {
            "timing_ms": _finite(row.get("timing_ms"), "decode timing_ms", positive=True),
            "input_sha256": _sha(row, "input_sha256", "decode"),
            "output_sha256": _sha(row, "output_sha256", "decode"),
        }
    if set(decode_steps) != set(DECODE_INDICES):
        raise DecompositionError("D0-D3 decode matrix mismatch")

    overhead_rows = run.get("policy_overheads")
    if not isinstance(overhead_rows, list) or not overhead_rows:
        raise DecompositionError("missing policy_overheads")
    overhead = []
    for index, row in enumerate(overhead_rows):
        if not isinstance(row, Mapping) or _integer(row.get("update_index"), "update_index") != index:
            raise DecompositionError("policy overhead update order mismatch")
        if _text(row.get("unit"), "policy overhead unit") != "us":
            raise DecompositionError("policy overhead unit mismatch; exact unit must be us")
        overhead.append(_finite(row.get("duration"), "policy overhead", nonnegative=True))
    return {"rep": rep, "tokens": tokens, "top": top, "children": children,
            "decode_steps": decode_steps, "order": ordered,
            "policy_overhead_us": overhead}


def _conditions(document: Mapping[str, Any], authority: Mapping[str, Any]) -> dict[str, Any]:
    rows = document.get("conditions")
    if not isinstance(rows, list) or not rows:
        raise DecompositionError("conditions must be a nonempty list")
    result = {}
    semantic_baseline = None
    order_baseline = None
    token_baseline = None
    for condition in rows:
        if not isinstance(condition, Mapping):
            raise DecompositionError("invalid condition")
        name = _text(condition.get("condition"), "condition")
        if name in result:
            raise DecompositionError(f"duplicate condition: {name}")
        runs = condition.get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise DecompositionError(f"{name} must contain exactly seven fresh runs")
        normalized = {}
        for run in runs:
            item = _normalize_run(run, authority, name)
            rep = item["rep"]
            if rep not in range(EXPECTED_REPS) or rep in normalized:
                raise DecompositionError(f"duplicate/out-of-range rep in {name}")
            normalized[rep] = item
            identity = (
                tuple((key, value["input_sha256"], value["output_sha256"])
                      for key, value in sorted(item["top"].items(), key=str)),
                tuple((key, value["input_sha256"], value["output_sha256"],
                       value["module_name"], value["backend"])
                      for key, value in sorted(item["children"].items())),
                tuple((key, value["input_sha256"], value["output_sha256"])
                      for key, value in sorted(item["decode_steps"].items())),
            )
            order = tuple(tuple(item["order"][d]) for d in DECODE_INDICES)
            if semantic_baseline is None:
                semantic_baseline, order_baseline = identity, order
                token_baseline = item["tokens"]
            if identity != semantic_baseline:
                raise DecompositionError("semantic SHA/module identity drift")
            if order != order_baseline:
                raise DecompositionError("cross-run top-level call order drift")
            if item["tokens"] != token_baseline:
                raise DecompositionError("token sequence drift")
        if set(normalized) != set(range(EXPECTED_REPS)):
            raise DecompositionError(f"rep matrix mismatch in {name}")
        result[name] = normalized
    return result


def _sum_top(run: Mapping[str, Any], decode: int, categories: Sequence[str]) -> float:
    return sum(value["timing_ms"] for (layer, category, d), value in run["top"].items()
               if d == decode and category in categories)


def _analyze_pair(control: Mapping[int, Any], fair: Mapping[int, Any],
                  budget_bytes: int, authority: Mapping[str, Any]) -> dict[str, Any]:
    rows = []
    for rep in range(EXPECTED_REPS):
        for decode in STABLE_DECODE_INDICES:
            c, f = control[rep], fair[rep]
            role_saving = {}
            role_control = {}
            role_fair = {}
            for role in ROLES:
                role_control[role] = sum(c["children"][(layer, role, decode)]["timing_ms"]
                                         for layer in LAYERS)
                role_fair[role] = sum(f["children"][(layer, role, decode)]["timing_ms"]
                                      for layer in LAYERS)
                role_saving[role] = role_control[role] - role_fair[role]
            total_ffn = sum(role_saving.values())
            mlp = _sum_top(c, decode, ("mlp",)) - _sum_top(f, decode, ("mlp",))
            self_attn = (_sum_top(c, decode, ("self_attn",)) -
                         _sum_top(f, decode, ("self_attn",)))
            norm = (_sum_top(c, decode, ("input_layernorm", "post_attention_layernorm")) -
                    _sum_top(f, decode, ("input_layernorm", "post_attention_layernorm")))
            final = (_sum_top(c, decode, tuple(authority["final_stages"])) -
                     _sum_top(f, decode, tuple(authority["final_stages"])))
            observed = c["decode_steps"][decode]["timing_ms"] - f["decode_steps"][decode]["timing_ms"]
            accounted = mlp + self_attn + norm + final
            direct_up = role_saving["up_proj"]
            negative_offset = direct_up - observed
            measured_non_up = direct_up - accounted
            localization = measured_non_up / negative_offset if negative_offset > 0 else None
            rows.append({
                "budget_bytes": budget_bytes, "rep": rep, "decode_index": decode,
                "DIRECT_UP_SAVING": direct_up,
                "GATE_SAVING": role_saving["gate_proj"],
                "DOWN_SAVING": role_saving["down_proj"],
                "TOTAL_FFN_PROJECTION_SAVING": total_ffn,
                "MLP_TOP_SAVING": mlp,
                "MLP_INTERNAL_RESIDUAL": mlp - total_ffn,
                "SELF_ATTN_SAVING": self_attn,
                "NORM_SAVING": norm,
                "FINAL_STAGE_SAVING": final,
                "OBSERVED_DECODE_SAVING": observed,
                "ACCOUNTED_TOPLEVEL_SAVING": accounted,
                "UNEXPLAINED_RESIDUAL": observed - accounted,
                "NEGATIVE_OFFSET_RELATIVE_TO_DIRECT_UP": negative_offset,
                "DIRECTLY_MEASURED_NON_UP_OFFSET": measured_non_up,
                "LOCALIZED_NEGATIVE_OFFSET_FRACTION": localization,
                "localization_ratio_unclamped": True,
            })
    summaries = {field: _stats([row[field] for row in rows]) for field in (
        "DIRECT_UP_SAVING", "GATE_SAVING", "DOWN_SAVING",
        "TOTAL_FFN_PROJECTION_SAVING", "MLP_TOP_SAVING", "MLP_INTERNAL_RESIDUAL",
        "SELF_ATTN_SAVING", "NORM_SAVING", "FINAL_STAGE_SAVING",
        "OBSERVED_DECODE_SAVING", "ACCOUNTED_TOPLEVEL_SAVING", "UNEXPLAINED_RESIDUAL",
        "NEGATIVE_OFFSET_RELATIVE_TO_DIRECT_UP", "DIRECTLY_MEASURED_NON_UP_OFFSET")}
    residual = summaries["UNEXPLAINED_RESIDUAL"]["median"]
    # Decimal millisecond evidence is represented as binary float; the tiny
    # tolerance preserves the frozen inclusive 0.10-ms boundary only.
    qualified = abs(residual) <= MAX_ABS_MEDIAN_RESIDUAL_MS + 1e-12

    # Frozen effects: local is D3 summed up timing; system is all run-aligned D1--D3.
    cup, fup, cdecode, fdecode = [], [], [], []
    for rep in range(EXPECTED_REPS):
        for decode in STABLE_DECODE_INDICES:
            cdecode.append(control[rep]["decode_steps"][decode]["timing_ms"])
            fdecode.append(fair[rep]["decode_steps"][decode]["timing_ms"])
        cup.append(sum(control[rep]["children"][(layer, "up_proj", 3)]["timing_ms"] for layer in LAYERS))
        fup.append(sum(fair[rep]["children"][(layer, "up_proj", 3)]["timing_ms"] for layer in LAYERS))
    local_effect, system_effect = _effect(cup, fup), _effect(cdecode, fdecode)
    local_effect["material"] = (local_effect["benefit_fraction"] >= LOCAL_UP_MIN and
                                local_effect["benefit_fraction"] > local_effect["combined_dispersion"])
    system_effect["material"] = (system_effect["benefit_fraction"] >= SYSTEM_MIN and
                                 system_effect["benefit_fraction"] > system_effect["combined_dispersion"])
    localization_values = [row["LOCALIZED_NEGATIVE_OFFSET_FRACTION"] for row in rows
                           if row["LOCALIZED_NEGATIVE_OFFSET_FRACTION"] is not None]
    localization_stats = _stats(localization_values) if localization_values else None
    return {
        "budget_bytes": budget_bytes, "run_aligned_rows": rows, "summaries": summaries,
        "decomposition_qualified": qualified,
        "decomposition_status": "PASS" if qualified else "TOPLEVEL_DECOMPOSITION_INCOMPLETE",
        "qualification_threshold_ms": MAX_ABS_MEDIAN_RESIDUAL_MS,
        "local_up_d3_effect": local_effect, "whole_decode_stable_effect": system_effect,
        "negative_offset_localization": localization_stats,
    }


def analyze_decomposition(document: Mapping[str, Any]) -> dict[str, Any]:
    if document.get("schema_version") != 1:
        raise DecompositionError("unsupported schema_version")
    authority = validate_module_authority(document.get("module_authority", {}))
    conditions = _conditions(document, authority)
    pairs = document.get("budget_pairs")
    if not isinstance(pairs, list) or not pairs:
        raise DecompositionError("budget_pairs must be a nonempty list")
    points = {}
    used = set()
    for pair in pairs:
        if not isinstance(pair, Mapping):
            raise DecompositionError("invalid budget pair")
        budget = _integer(pair.get("budget_bytes"), "budget_bytes")
        control_name = _text(pair.get("control_condition"), "control condition")
        fair_name = _text(pair.get("fair_condition"), "fair condition")
        if budget <= 0 or budget in points or control_name == fair_name:
            raise DecompositionError("duplicate/invalid budget pair")
        if control_name not in conditions or fair_name not in conditions:
            raise DecompositionError("budget pair references missing condition")
        used.update((control_name, fair_name))
        points[budget] = _analyze_pair(conditions[control_name], conditions[fair_name],
                                       budget, authority)
    if used != set(conditions):
        raise DecompositionError("unpaired condition evidence")

    overhead = {}
    for name, runs in conditions.items():
        per_update = [v for run in runs.values() for v in run["policy_overhead_us"]]
        per_run = [sum(run["policy_overhead_us"]) for run in runs.values()]
        overhead[name] = {"unit": "us", "per_update": _stats(per_update),
                          "total_per_run": _stats(per_run),
                          "subtracted_from_gpu_timing": False}
    return {"status": "PASS", "module_authority": authority, "points": points,
            "host_policy_overhead": overhead,
            "accounting_rule": "NONOVERLAPPING_TOPLEVEL_ONLY; FFN_CHILDREN_NESTED_DIAGNOSTIC",
            "host_api_timing_rule": "REPORTED_SEPARATELY_NEVER_SUBTRACTED_FROM_GPU"}


def classify_stage(analysis: Mapping[str, Any], *, policy_qualified: bool = True,
                   semantic_qualified: bool = True) -> dict[str, Any]:
    points = analysis.get("points")
    if not isinstance(points, Mapping) or not points:
        raise DecompositionError("analysis points missing")
    decomposition_qualified = all(p.get("decomposition_qualified") is True
                                  for p in points.values())
    system_relevant = any(p["whole_decode_stable_effect"]["material"] is True
                          for p in points.values())
    positive_subthreshold = any(
        p["whole_decode_stable_effect"]["positive_beyond_dispersion"] is True and
        p["whole_decode_stable_effect"]["benefit_fraction"] < SYSTEM_MIN
        for p in points.values())
    localized = any(
        p.get("negative_offset_localization") is not None and
        p["negative_offset_localization"]["median"] >= LOCALIZATION_MIN and
        p["summaries"]["NEGATIVE_OFFSET_RELATIVE_TO_DIRECT_UP"]["median"] > 0
        for p in points.values())
    if not policy_qualified or not semantic_qualified or not decomposition_qualified:
        label = "RESIDENCY_COST_DIAGNOSTIC_UNQUALIFIED"
    elif system_relevant:
        label = "RESIDENCY_COST_AWARE_SYSTEM_RELEVANT"
    elif positive_subthreshold:
        label = "RESIDENCY_COST_AWARE_POSITIVE_SUBTHRESHOLD"
    elif localized:
        label = "RESIDENCY_OFFSET_LOCALIZED"
    else:
        label = "RESIDENCY_SYSTEM_CASE_WEAK"
    return {
        "stage_label": label,
        "precedence": [
            "RESIDENCY_COST_DIAGNOSTIC_UNQUALIFIED",
            "RESIDENCY_COST_AWARE_SYSTEM_RELEVANT",
            "RESIDENCY_COST_AWARE_POSITIVE_SUBTHRESHOLD",
            "RESIDENCY_OFFSET_LOCALIZED", "RESIDENCY_SYSTEM_CASE_WEAK"],
        "policy_qualified": policy_qualified, "semantic_qualified": semantic_qualified,
        "decomposition_qualified": decomposition_qualified,
        "localization_threshold": LOCALIZATION_MIN,
        "simulator_auto_authorized": False,
    }
