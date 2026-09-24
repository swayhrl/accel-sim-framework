#!/usr/bin/env python3
"""Fail-closed consumer for C16 E1 operator-family native policy evidence.

The module deliberately derives the natural module order from raw probe runs.  It
never encodes a gate/up/down call order.  The frozen 14-condition *membership*
matrix is encoded here because it was preregistered before producer data.
"""
from __future__ import annotations

import math
import re
import statistics
from collections import defaultdict
from typing import Any, Mapping, Sequence


class OperatorPolicyError(ValueError):
    """Raw evidence does not close the frozen operator-family contract."""


LAYERS = tuple(range(28))
ROLES = ("gate_proj", "up_proj", "down_proj")
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
DECODE_PHASES = ("D0", "D1", "D2", "D3")
DECODE_INDICES = tuple(range(4))
EXPECTED_TOKENS = (23578, 11, 323, 3950)
EXPECTED_REPS = 7
REQUESTED_SETASIDE_BYTES = 33_947_648
ACTUAL_SETASIDE_BYTES = 37_748_736
EXPECTED_MODULE_CLASS = "WQLinear_GEMM"
EXPECTED_IMPLEMENTATION = "AWQ_FP16_INPUT"
CONDITION_SETS = {
    "GATE28": ("gate_proj",),
    "UP28": ("up_proj",),
    "DOWN28": ("down_proj",),
    "GU56": ("gate_proj", "up_proj"),
    "GD56": ("gate_proj", "down_proj"),
    "UD56": ("up_proj", "down_proj"),
    "GUD84": ROLES,
}
CONDITIONS = tuple(
    f"{mode}_{family}"
    for family in CONDITION_SETS
    for mode in ("CONTROL", "FAIR")
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorPolicyError(f"missing/empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise OperatorPolicyError(f"invalid {label}")
    try:
        result = int(str(value).strip(), 10)
    except (TypeError, ValueError) as exc:
        raise OperatorPolicyError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() != str(result) or result < minimum:
        raise OperatorPolicyError(f"invalid {label}: {value!r}")
    return result


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise OperatorPolicyError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        raise OperatorPolicyError(f"nonfinite/nonpositive {label}: {value!r}")
    return result


def _bool(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return value.strip().lower() == "true"
    raise OperatorPolicyError(f"invalid boolean {label}")


def _sha(value: Any, label: str) -> str:
    result = str(value).strip().lower()
    if not HEX64.fullmatch(result):
        raise OperatorPolicyError(f"invalid {label}")
    return result


def _tokens(value: Any) -> tuple[int, ...]:
    if not isinstance(value, list):
        raise OperatorPolicyError("generated_token_ids must be a list")
    result = tuple(_integer(x, "generated_token_id") for x in value)
    if result != EXPECTED_TOKENS:
        raise OperatorPolicyError("token sequence drift")
    return result


def _stats(values: Sequence[float]) -> dict[str, float | int]:
    xs = [_finite(x, "sample", positive=True) for x in values]
    if not xs:
        raise OperatorPolicyError("empty samples")
    mean = statistics.fmean(xs)
    return {
        "sample_count": len(xs),
        "min_ms": min(xs),
        "median_ms": statistics.median(xs),
        "max_ms": max(xs),
        "mean_ms": mean,
        "cv": statistics.pstdev(xs) / mean,
    }


def _qweight(raw: Any, label: str = "qweight") -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise OperatorPolicyError(f"missing {label}")
    pointer = _integer(raw.get("pointer"), f"{label}.pointer", 1)
    size = _integer(raw.get("bytes"), f"{label}.bytes", 1)
    start = _integer(raw.get("span_start"), f"{label}.span_start", 1)
    end = _integer(raw.get("span_end"), f"{label}.span_end", 1)
    shape = raw.get("shape")
    if not isinstance(shape, list) or not shape:
        raise OperatorPolicyError(f"invalid {label}.shape")
    if not _bool(raw.get("contiguous"), f"{label}.contiguous"):
        raise OperatorPolicyError(f"{label} is not contiguous")
    if start != pointer or end != pointer + size:
        raise OperatorPolicyError(f"{label} exact span drift")
    return {
        "pointer": pointer,
        "bytes": size,
        "span_start": start,
        "span_end": end,
        "shape": [_integer(x, f"{label}.shape", 1) for x in shape],
        "contiguous": True,
    }


def validate_module_authority(rows: Any) -> dict[tuple[int, str], dict[str, Any]]:
    """Validate the exact 28 x 3 AWQ qweight-backed module universe."""
    if not isinstance(rows, list):
        raise OperatorPolicyError("module_authority must be a list")
    result: dict[tuple[int, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise OperatorPolicyError("invalid module authority row")
        key = (
            _integer(row.get("layer_index"), "layer_index"),
            _text(row.get("role"), "role"),
        )
        if key[0] not in LAYERS or key[1] not in ROLES or key in result:
            raise OperatorPolicyError("wrong/duplicate module authority")
        if _text(row.get("module_class"), "module_class") != EXPECTED_MODULE_CLASS:
            raise OperatorPolicyError("module class drift")
        if _text(row.get("implementation"), "implementation") != EXPECTED_IMPLEMENTATION:
            raise OperatorPolicyError("implementation drift")
        backend = _text(row.get("backend"), "backend")
        result[key] = {
            "layer_index": key[0],
            "role": key[1],
            "module_class": EXPECTED_MODULE_CLASS,
            "implementation": EXPECTED_IMPLEMENTATION,
            "backend": backend,
            "qweight": _qweight(row.get("qweight")),
        }
    expected = {(layer, role) for layer in LAYERS for role in ROLES}
    if set(result) != expected:
        raise OperatorPolicyError("missing role/module from exact 84-module authority")
    return result


def _sequence(raw: Any, phase: str, modules: Mapping[tuple[int, str], Mapping[str, Any]],
              *, policy_timeline: bool = False) -> tuple[tuple[int, str], ...]:
    if not isinstance(raw, list) or len(raw) != 84:
        raise OperatorPolicyError(f"{phase} must contain exact 84 natural calls")
    result: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    last_timeline = 0
    for position, row in enumerate(raw):
        if not isinstance(row, Mapping):
            raise OperatorPolicyError("invalid natural call row")
        if _integer(row.get("natural_order_index"), "natural_order_index") != position:
            raise OperatorPolicyError("wrong natural call order index")
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"))
        if key not in modules or key in seen:
            raise OperatorPolicyError("duplicate/missing/wrong natural module call")
        if _text(row.get("module_class"), "module_class") != modules[key]["module_class"] or \
                _text(row.get("implementation"), "implementation") != modules[key]["implementation"] or \
                _text(row.get("backend"), "backend") != modules[key]["backend"] or \
                _qweight(row.get("qweight")) != modules[key]["qweight"]:
            raise OperatorPolicyError("natural call module identity drift")
        if policy_timeline:
            timeline = _integer(row.get("timeline_event_index"), "timeline_event_index", 1)
            if timeline <= last_timeline:
                raise OperatorPolicyError("non-monotonic natural call timeline")
            last_timeline = timeline
        seen.add(key)
        result.append(key)
    if seen != set(modules):
        raise OperatorPolicyError("missing natural module call")
    return tuple(result)


def consume_natural_call_order_authority(document: Mapping[str, Any]) -> dict[str, Any]:
    """Derive, then hold constant, PREFILL/D0-D3 natural order across 7 probes."""
    if document.get("schema_version") != 1:
        raise OperatorPolicyError("unsupported natural call-order schema")
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    _tokens(document.get("generated_token_ids"))
    modules = validate_module_authority(document.get("module_authority"))
    probes = document.get("probe_runs")
    if not isinstance(probes, list) or len(probes) != EXPECTED_REPS:
        raise OperatorPolicyError("natural call order requires exactly 7 fresh probes")
    reps: set[int] = set()
    processes: set[str] = set()
    canonical: dict[str, tuple[tuple[int, str], ...]] = {}
    for run in probes:
        rep = _integer(run.get("rep"), "rep")
        if rep not in range(EXPECTED_REPS) or rep in reps:
            raise OperatorPolicyError("missing/duplicate natural-order rep")
        reps.add(rep)
        process = _text(run.get("fresh_process_id"), "fresh_process_id")
        if process in processes:
            raise OperatorPolicyError("natural-order fresh process reused")
        processes.add(process)
        if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
            raise OperatorPolicyError("natural-order prefix SHA drift")
        _tokens(run.get("generated_token_ids"))
        phases = run.get("phases")
        if not isinstance(phases, Mapping) or set(phases) != set(PHASES):
            raise OperatorPolicyError("missing/extra natural call-order phase")
        for phase in PHASES:
            observed = _sequence(phases[phase], phase, modules)
            if phase not in canonical:
                canonical[phase] = observed
            elif observed != canonical[phase]:
                raise OperatorPolicyError("natural call order drift across fresh processes")
    return {
        "status": "PASS",
        "authority": "RAW_NATURAL_CALL_ORDER",
        "fresh_process_count": len(processes),
        "module_count": len(modules),
        "accepted_prefix_sha256": prefix,
        "generated_token_ids": list(EXPECTED_TOKENS),
        "derived_order": {
            phase: [{"natural_order_index": i, "layer_index": key[0], "role": key[1]}
                    for i, key in enumerate(canonical[phase])]
            for phase in PHASES
        },
    }


def _canonical_sequences(authority: Mapping[str, Any]) -> dict[str, tuple[tuple[int, str], ...]]:
    raw = authority.get("derived_order")
    if not isinstance(raw, Mapping) or set(raw) != set(PHASES):
        raise OperatorPolicyError("invalid consumed natural-order authority")
    result = {}
    for phase in PHASES:
        rows = raw[phase]
        if not isinstance(rows, list) or len(rows) != 84:
            raise OperatorPolicyError("invalid consumed natural-order sequence")
        result[phase] = tuple((_integer(x.get("layer_index"), "layer_index"),
                               _text(x.get("role"), "role")) for x in rows)
    return result


def _reset(raw: Any, label: str) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or _text(raw.get("status"), f"{label}.status").upper() != "PASS" or \
            not _bool(raw.get("performed"), f"{label}.performed"):
        raise OperatorPolicyError(f"missing/failed {label}")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise OperatorPolicyError(f"{label} is not a persistence reset")
    return {"status": "PASS", "performed": True, "operation": operation}


def _condition_identity(condition: str) -> tuple[str, str, tuple[str, ...], set[tuple[int, str]]]:
    if condition not in CONDITIONS:
        raise OperatorPolicyError("unsupported or missing frozen condition")
    mode, family = condition.split("_", 1)
    roles = CONDITION_SETS[family]
    selected = {(layer, role) for layer in LAYERS for role in roles}
    return mode, family, roles, selected


def validate_policy_receipt(receipt: Mapping[str, Any], condition: str,
                            modules: Mapping[tuple[int, str], Mapping[str, Any]],
                            canonical: Mapping[str, tuple[tuple[int, str], ...]],
                            calls_by_phase: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, Any]:
    """Validate selected updates against the raw natural-call timeline."""
    mode, family, roles, selected = _condition_identity(condition)
    if not isinstance(receipt, Mapping) or _text(receipt.get("condition"), "condition") != condition:
        raise OperatorPolicyError("policy condition mismatch")
    if _text(receipt.get("status"), "status").upper() != "PASS":
        raise OperatorPolicyError("policy receipt did not PASS")
    if tuple(receipt.get("selected_roles", ())) != roles:
        raise OperatorPolicyError("wrong selected family")
    selected_rows = receipt.get("selected_modules")
    if not isinstance(selected_rows, list):
        raise OperatorPolicyError("selected_modules must be a list")
    observed_selected = {(_integer(x.get("layer_index"), "layer_index"),
                          _text(x.get("role"), "role")) for x in selected_rows}
    if len(selected_rows) != len(observed_selected) or observed_selected != selected:
        raise OperatorPolicyError("wrong selected module set")
    if _integer(receipt.get("requested_setaside_bytes"), "requested_setaside_bytes") != REQUESTED_SETASIDE_BYTES:
        raise OperatorPolicyError("requested set-aside drift")
    if _integer(receipt.get("actual_setaside_bytes"), "actual_setaside_bytes") != ACTUAL_SETASIDE_BYTES:
        raise OperatorPolicyError("actual set-aside drift")
    stream = _text(receipt.get("stream_identity"), "stream_identity")
    _reset(receipt.get("reset_before"), "reset_before")
    _reset(receipt.get("reset_after"), "reset_after")
    if receipt.get("other_reset_events", []) != []:
        raise OperatorPolicyError("reset allowed only before/after condition")
    switches = receipt.get("switches")
    expected_switch_count = len(selected) * len(PHASES)
    if not isinstance(switches, list) or len(switches) != expected_switch_count:
        raise OperatorPolicyError("missing/duplicate selected policy update")
    by_attachment: dict[tuple[str, int], Mapping[str, Any]] = {}
    ratio = 1.0 / len(selected)
    durations: list[float] = []
    for update in switches:
        phase = _text(update.get("phase"), "phase").upper()
        if phase not in PHASES:
            raise OperatorPolicyError("wrong policy update phase")
        natural_index = _integer(update.get("attached_natural_order_index"),
                                 "attached_natural_order_index")
        key = (_integer(update.get("layer_index"), "layer_index"),
               _text(update.get("role"), "role"))
        attachment = (phase, natural_index)
        if attachment in by_attachment or natural_index >= 84 or canonical[phase][natural_index] != key:
            raise OperatorPolicyError("wrong update attachment")
        if key not in selected:
            raise OperatorPolicyError("unselected module has policy update")
        call = calls_by_phase[phase][natural_index]
        if _integer(update.get("timeline_event_index"), "timeline_event_index", 1) + 1 != \
                _integer(call.get("timeline_event_index"), "timeline_event_index", 1):
            raise OperatorPolicyError("policy update is not immediately before natural call")
        module = modules[key]
        if _integer(update.get("base_pointer"), "base_pointer", 1) != module["qweight"]["pointer"] or \
                _integer(update.get("num_bytes"), "num_bytes", 1) != module["qweight"]["bytes"]:
            raise OperatorPolicyError("policy update is not exact qweight window")
        if _text(update.get("stream_identity"), "stream_identity") != stream:
            raise OperatorPolicyError("stream identity drift")
        if _bool(update.get("reset_performed"), "reset_performed"):
            raise OperatorPolicyError("forbidden in-run reset")
        hit_ratio = _finite(update.get("hit_ratio"), "hit_ratio", positive=True)
        if not math.isclose(hit_ratio, ratio, rel_tol=0, abs_tol=1e-12):
            raise OperatorPolicyError("wrong 1/K hitRatio")
        policy = (_text(update.get("hit_prop"), "hit_prop").upper(),
                  _text(update.get("miss_prop"), "miss_prop").upper(),
                  _bool(update.get("target_persisting"), "target_persisting"))
        expected_policy = ("NORMAL", "NORMAL", False) if mode == "CONTROL" else \
                          ("PERSISTING", "STREAMING", True)
        if policy != expected_policy:
            raise OperatorPolicyError(f"{mode} policy mismatch")
        duration = _finite(update.get("api_duration_us"), "api_duration_us")
        if duration < 0:
            raise OperatorPolicyError("negative API duration")
        durations.append(duration)
        by_attachment[attachment] = update
    expected_attachments = {(phase, i) for phase in PHASES
                            for i, key in enumerate(canonical[phase]) if key in selected}
    if set(by_attachment) != expected_attachments:
        raise OperatorPolicyError("policy updates do not match all selected natural calls")
    # The combined timeline must be gap-free: selected calls have one UPDATE just before;
    # unselected calls have no update and therefore no unaccounted event.
    for phase in PHASES:
        expected_timeline = 1
        for i, call in enumerate(calls_by_phase[phase]):
            key = canonical[phase][i]
            if key in selected:
                update_index = _integer(by_attachment[(phase, i)].get("timeline_event_index"),
                                        "timeline_event_index", 1)
                if update_index != expected_timeline:
                    raise OperatorPolicyError("policy/call timeline has gap or wrong attachment")
                expected_timeline += 1
            if _integer(call.get("timeline_event_index"), "timeline_event_index", 1) != expected_timeline:
                raise OperatorPolicyError("policy/call timeline has gap or unrecorded update")
            expected_timeline += 1
    reported_total = _finite(receipt.get("total_api_duration_us"), "total_api_duration_us")
    if reported_total < 0 or not math.isclose(reported_total, sum(durations), rel_tol=1e-12, abs_tol=1e-9):
        raise OperatorPolicyError("policy API total duration mismatch")
    return {
        "status": "PASS", "condition": condition, "mode": mode, "family": family,
        "selected_roles": list(roles), "selected_module_count": len(selected),
        "update_count": len(switches), "hit_ratio": ratio,
        "requested_setaside_bytes": REQUESTED_SETASIDE_BYTES,
        "actual_setaside_bytes": ACTUAL_SETASIDE_BYTES,
        "stream_identity": stream, "api_update_durations_us": durations,
        "total_api_duration_us": reported_total,
    }


def _occurrence_authority(rows: Any) -> dict[tuple[int, str, int], tuple[str, str]]:
    if not isinstance(rows, list):
        raise OperatorPolicyError("occurrence_authority must be a list")
    expected = {(layer, role, d) for layer in LAYERS for role in ROLES for d in DECODE_INDICES}
    result = {}
    for row in rows:
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"),
               _integer(row.get("decode_index"), "decode_index"))
        if key not in expected or key in result:
            raise OperatorPolicyError("wrong/duplicate occurrence authority")
        if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[key[2]]:
            raise OperatorPolicyError("occurrence authority token drift")
        result[key] = (_sha(row.get("input_sha256"), "input_sha256"),
                       _sha(row.get("output_sha256"), "output_sha256"))
    if set(result) != expected:
        raise OperatorPolicyError("missing occurrence authority")
    return result


def consume_operator_policy_runs(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate all 14 x 7 fresh runs and return normalized run-aligned timing."""
    if document.get("schema_version") != 1:
        raise OperatorPolicyError("unsupported operator policy schema")
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    _tokens(document.get("generated_token_ids"))
    modules = validate_module_authority(document.get("module_authority"))
    call_authority_doc = document.get("natural_call_order_authority")
    if not isinstance(call_authority_doc, Mapping):
        raise OperatorPolicyError("missing natural_call_order_authority")
    natural = consume_natural_call_order_authority(call_authority_doc)
    # The nested authority must use the exact same module rows, not an alternate universe.
    if validate_module_authority(call_authority_doc.get("module_authority")) != modules:
        raise OperatorPolicyError("natural/order module authority mismatch")
    if natural["accepted_prefix_sha256"] != prefix:
        raise OperatorPolicyError("natural/order accepted prefix mismatch")
    canonical = _canonical_sequences(natural)
    authority = _occurrence_authority(document.get("occurrence_authority"))
    conditions = document.get("conditions")
    if not isinstance(conditions, list):
        raise OperatorPolicyError("conditions must be a list")
    by_condition: dict[str, Mapping[str, Any]] = {}
    for item in conditions:
        name = _text(item.get("condition"), "condition")
        if name in by_condition:
            raise OperatorPolicyError("duplicate condition")
        by_condition[name] = item
    if set(by_condition) != set(CONDITIONS):
        raise OperatorPolicyError("missing/extra frozen 14-condition matrix")
    processes: set[str] = set()
    normalized_runs: list[dict[str, Any]] = []
    timing_samples: dict[tuple[str, int, str], list[float]] = defaultdict(list)
    for condition in CONDITIONS:
        mode, family, roles, selected = _condition_identity(condition)
        runs = by_condition[condition].get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise OperatorPolicyError("each condition requires exactly 7 fresh runs")
        reps: set[int] = set()
        for run in runs:
            rep = _integer(run.get("rep"), "rep")
            if rep not in range(EXPECTED_REPS) or rep in reps:
                raise OperatorPolicyError("missing/duplicate condition rep")
            reps.add(rep)
            process = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process in processes:
                raise OperatorPolicyError("fresh process reused across matrix")
            processes.add(process)
            if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
                raise OperatorPolicyError("prefix SHA drift")
            _tokens(run.get("generated_token_ids"))
            calls = run.get("natural_calls")
            if not isinstance(calls, Mapping) or set(calls) != set(PHASES):
                raise OperatorPolicyError("missing/extra run natural-call phase")
            calls_by_phase = {}
            for phase in PHASES:
                if _sequence(calls[phase], phase, modules, policy_timeline=True) != canonical[phase]:
                    raise OperatorPolicyError("condition natural call order drift")
                calls_by_phase[phase] = calls[phase]
            policy = validate_policy_receipt(run.get("policy_receipt"), condition, modules,
                                             canonical, calls_by_phase)
            if not math.isclose(_finite(run.get("policy_api_duration_us"), "policy_api_duration_us"),
                                policy["total_api_duration_us"], rel_tol=1e-12, abs_tol=1e-9):
                raise OperatorPolicyError("run policy API duration mismatch")
            all84 = run.get("all_84_event")
            if not isinstance(all84, Mapping) or _text(all84.get("status"), "all_84_event.status").upper() != "PASS":
                raise OperatorPolicyError("missing all-84 event receipt")
            counts = all84.get("decode_phase_counts")
            if not isinstance(counts, Mapping) or set(counts) != set(DECODE_PHASES) or \
                    any(_integer(counts[p], f"{p} event count") != 84 for p in DECODE_PHASES):
                raise OperatorPolicyError("missing all-84 event")
            decode_rows = run.get("decode_steps")
            if not isinstance(decode_rows, list) or len(decode_rows) != 4:
                raise OperatorPolicyError("missing/duplicate decode timing")
            decode = {}
            for row in decode_rows:
                d = _integer(row.get("decode_index"), "decode_index")
                if d not in DECODE_INDICES or d in decode:
                    raise OperatorPolicyError("wrong/duplicate decode timing")
                if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[d]:
                    raise OperatorPolicyError("decode token drift")
                decode[d] = _finite(row.get("timing_ms"), "decode timing", positive=True)
            rows = run.get("occurrences")
            if not isinstance(rows, list) or len(rows) != 336:
                raise OperatorPolicyError("every run requires exact all-84 D0-D3 timing events")
            observed: dict[tuple[int, str, int], float] = {}
            for row in rows:
                key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"),
                       _integer(row.get("decode_index"), "decode_index"))
                if key not in authority or key in observed:
                    raise OperatorPolicyError("wrong/duplicate FFN timing event")
                module = modules[key[:2]]
                if _text(row.get("module_class"), "module_class") != module["module_class"] or \
                        _text(row.get("implementation"), "implementation") != module["implementation"] or \
                        _text(row.get("backend"), "backend") != module["backend"] or \
                        _qweight(row.get("qweight")) != module["qweight"]:
                    raise OperatorPolicyError("FFN timing module identity drift")
                if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[key[2]]:
                    raise OperatorPolicyError("FFN timing token drift")
                if (_sha(row.get("input_sha256"), "input_sha256"),
                        _sha(row.get("output_sha256"), "output_sha256")) != authority[key]:
                    raise OperatorPolicyError("FFN timing SHA drift")
                value = _finite(row.get("timing_ms"), "FFN timing", positive=True)
                observed[key] = value
                timing_samples[(condition, key[0], key[1])].append(value)
            if set(observed) != set(authority):
                raise OperatorPolicyError("missing FFN timing event")
            normalized_runs.append({
                "condition": condition, "mode": mode, "family": family, "rep": rep,
                "fresh_process_id": process, "selected_roles": list(roles),
                "selected_module_count": len(selected),
                "decode_step_ms": {f"D{d}": decode[d] for d in DECODE_INDICES},
                "stable_decode_ms": statistics.fmean(decode[d] for d in (1, 2, 3)),
                "policy_api_update_durations_us": policy["api_update_durations_us"],
                "policy_api_duration_us": policy["total_api_duration_us"],
                "occurrence_timing_ms": [
                    {"decode_index": d, "layer_index": layer, "role": role,
                     "selected": (layer, role) in selected, "timing_ms": observed[(layer, role, d)]}
                    for d in DECODE_INDICES for layer, role in canonical[f"D{d}"]
                ],
            })
    module_stats = [
        {"condition": condition, "layer_index": layer, "role": role,
         **_stats(values)}
        for (condition, layer, role), values in sorted(timing_samples.items())
    ]
    return {
        "status": "PASS",
        "authority": "RAW_14_CONDITION_84_MODULE_NATIVE_EVIDENCE_ONLY",
        "condition_count": len(CONDITIONS),
        "fresh_process_count": len(processes),
        "natural_call_order": natural,
        "run_aligned_points": normalized_runs,
        "module_timing_statistics": module_stats,
        "requested_setaside_bytes": REQUESTED_SETASIDE_BYTES,
        "actual_setaside_bytes": ACTUAL_SETASIDE_BYTES,
    }
