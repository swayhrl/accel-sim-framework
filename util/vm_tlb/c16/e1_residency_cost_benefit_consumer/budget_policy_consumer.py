#!/usr/bin/env python3
"""Fail-closed native/policy consumer for the residency cost/benefit stage.

This module consumes a normalized raw-evidence document.  It freezes only facts
that were preregistered: four requested budgets, all 28 ``up_proj`` qweight
windows, the budget-scaled CUDA policy hint, matched CONTROL/FAIR conditions,
and seven fresh processes per condition.  Runtime query-back values remain raw
authority; in particular, this code deliberately does not infer an alignment
rule from them.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any, Mapping, Sequence


class BudgetPolicyError(ValueError):
    """Raw evidence does not close the frozen budget/policy contract."""


LAYERS = tuple(range(28))
ROLES = ("gate_proj", "up_proj", "down_proj")
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
DECODE_PHASES = ("D0", "D1", "D2", "D3")
DECODE_INDICES = tuple(range(4))
EXPECTED_TOKENS = (23578, 11, 323, 3950)
EXPECTED_REPS = 7
EXPECTED_MODULE_CLASS = "WQLinear_GEMM"
EXPECTED_IMPLEMENTATION = "AWQ_FP16_INPUT"
UP_QWEIGHT_BYTES = 1_212_416
FULL_UP28_BYTES = 33_947_648
BUDGETS = {
    "B8": 8 * 1024 * 1024,
    "B16": 16 * 1024 * 1024,
    "B24": 24 * 1024 * 1024,
    "BFULL": FULL_UP28_BYTES,
}
CONDITIONS = tuple(
    f"{mode}_UP28_{budget}"
    for budget in BUDGETS
    for mode in ("CONTROL", "FAIR")
)
CORE_TOPLEVEL = (
    "input_layernorm",
    "self_attn",
    "post_attention_layernorm",
    "mlp",
)
OPTIONAL_FINAL = ("final_norm", "output")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BudgetPolicyError(f"missing/empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise BudgetPolicyError(f"invalid {label}")
    try:
        result = int(str(value).strip(), 10)
    except (TypeError, ValueError) as exc:
        raise BudgetPolicyError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() != str(result) or result < minimum:
        raise BudgetPolicyError(f"invalid {label}: {value!r}")
    return result


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise BudgetPolicyError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        raise BudgetPolicyError(f"nonfinite/nonpositive {label}: {value!r}")
    return result


def _bool(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return value.strip().lower() == "true"
    raise BudgetPolicyError(f"invalid boolean {label}")


def _sha(value: Any, label: str) -> str:
    result = str(value).strip().lower()
    if not HEX64.fullmatch(result):
        raise BudgetPolicyError(f"invalid {label}")
    return result


def _tokens(value: Any) -> tuple[int, ...]:
    if not isinstance(value, list):
        raise BudgetPolicyError("generated_token_ids must be a list")
    result = tuple(_integer(x, "generated_token_id") for x in value)
    if result != EXPECTED_TOKENS:
        raise BudgetPolicyError("token sequence drift")
    return result


def _reset(raw: Any, label: str) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise BudgetPolicyError(f"missing {label}")
    if _text(raw.get("status"), f"{label}.status").upper() != "PASS" or not _bool(
        raw.get("performed"), f"{label}.performed"
    ):
        raise BudgetPolicyError(f"missing/failed {label}")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise BudgetPolicyError(f"{label} is not a persistence reset")
    return {"status": "PASS", "performed": True, "operation": operation}


def _condition_identity(condition: str) -> tuple[str, str, int]:
    if condition not in CONDITIONS:
        raise BudgetPolicyError("unsupported frozen budget condition")
    mode, _, budget = condition.split("_", 2)
    return mode, budget, BUDGETS[budget]


def _module_authority(rows: Any) -> dict[tuple[int, str], dict[str, Any]]:
    if not isinstance(rows, list):
        raise BudgetPolicyError("module_authority must be a list")
    result: dict[tuple[int, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            raise BudgetPolicyError("invalid module authority row")
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"))
        if key[0] not in LAYERS or key[1] not in ROLES or key in result:
            raise BudgetPolicyError("wrong/duplicate module authority")
        if _text(row.get("module_class"), "module_class") != EXPECTED_MODULE_CLASS:
            raise BudgetPolicyError("module class drift")
        if _text(row.get("implementation"), "implementation") != EXPECTED_IMPLEMENTATION:
            raise BudgetPolicyError("implementation drift")
        size = _integer(row.get("qweight_bytes"), "qweight_bytes", 1)
        shape = row.get("qweight_shape")
        if not isinstance(shape, list) or not shape or not _bool(row.get("contiguous"), "contiguous"):
            raise BudgetPolicyError("invalid/noncontiguous qweight authority")
        if key[1] == "up_proj" and size != UP_QWEIGHT_BYTES:
            raise BudgetPolicyError("up_proj exact qweight bytes drift")
        result[key] = {
            "layer_index": key[0],
            "role": key[1],
            "module_class": EXPECTED_MODULE_CLASS,
            "implementation": EXPECTED_IMPLEMENTATION,
            "backend": _text(row.get("backend"), "backend"),
            "qweight_bytes": size,
            "qweight_shape": [_integer(x, "qweight_shape", 1) for x in shape],
            "contiguous": True,
        }
    expected = {(layer, role) for layer in LAYERS for role in ROLES}
    if set(result) != expected:
        raise BudgetPolicyError("missing role/module from exact 84-module authority")
    if sum(result[(layer, "up_proj")]["qweight_bytes"] for layer in LAYERS) != FULL_UP28_BYTES:
        raise BudgetPolicyError("all-28 up_proj qweight byte total drift")
    return result


def _natural_order(rows: Any, modules: Mapping[tuple[int, str], Mapping[str, Any]]) -> dict[str, tuple[tuple[int, str], ...]]:
    if not isinstance(rows, Mapping) or set(rows) != set(PHASES):
        raise BudgetPolicyError("natural_order must contain exact PREFILL/D0-D3 phases")
    expected = set(modules)
    result: dict[str, tuple[tuple[int, str], ...]] = {}
    for phase in PHASES:
        phase_rows = rows[phase]
        if not isinstance(phase_rows, list) or len(phase_rows) != 84:
            raise BudgetPolicyError("natural order phase must contain exact 84 modules")
        keys: list[tuple[int, str]] = []
        for i, row in enumerate(phase_rows):
            if _integer(row.get("natural_order_index"), "natural_order_index") != i:
                raise BudgetPolicyError("wrong natural order index")
            key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"))
            keys.append(key)
        if set(keys) != expected or len(set(keys)) != 84:
            raise BudgetPolicyError("wrong/duplicate/missing natural module order")
        result[phase] = tuple(keys)
    return result


def _sha_authority(rows: Any, expected: set[tuple[int, str, int]]) -> dict[tuple[int, str, int], tuple[str, str]]:
    if not isinstance(rows, list):
        raise BudgetPolicyError("occurrence_authority must be a list")
    result: dict[tuple[int, str, int], tuple[str, str]] = {}
    for row in rows:
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"),
               _integer(row.get("decode_index"), "decode_index"))
        if key not in expected or key in result:
            raise BudgetPolicyError("wrong/duplicate occurrence authority")
        if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[key[2]]:
            raise BudgetPolicyError("occurrence authority token drift")
        result[key] = (_sha(row.get("input_sha256"), "input_sha256"),
                       _sha(row.get("output_sha256"), "output_sha256"))
    if set(result) != expected:
        raise BudgetPolicyError("missing occurrence authority")
    return result


def _top_authority(rows: Any) -> dict[tuple[int | None, str, int], tuple[str, str]]:
    if not isinstance(rows, list):
        raise BudgetPolicyError("top_level_authority must be a list")
    result: dict[tuple[int | None, str, int], tuple[str, str]] = {}
    for row in rows:
        category = _text(row.get("category"), "top_level.category")
        decode = _integer(row.get("decode_index"), "top_level.decode_index")
        if decode not in DECODE_INDICES:
            raise BudgetPolicyError("wrong top-level decode index")
        if category in CORE_TOPLEVEL:
            layer: int | None = _integer(row.get("layer_index"), "top_level.layer_index")
            if layer not in LAYERS:
                raise BudgetPolicyError("wrong top-level layer")
        elif category in OPTIONAL_FINAL:
            if row.get("layer_index") is not None:
                raise BudgetPolicyError("final top-level stage must have null layer_index")
            layer = None
        else:
            raise BudgetPolicyError("unsupported top-level semantic category")
        key = (layer, category, decode)
        if key in result:
            raise BudgetPolicyError("duplicate top-level authority")
        if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[decode]:
            raise BudgetPolicyError("top-level authority token drift")
        result[key] = (_sha(row.get("input_sha256"), "input_sha256"),
                       _sha(row.get("output_sha256"), "output_sha256"))
    core = {(layer, category, d) for layer in LAYERS for category in CORE_TOPLEVEL for d in DECODE_INDICES}
    if not core.issubset(result):
        raise BudgetPolicyError("missing required top-level semantic authority")
    extras = set(result) - core
    for category in OPTIONAL_FINAL:
        category_keys = {(None, category, d) for d in DECODE_INDICES}
        if extras & category_keys and not category_keys.issubset(result):
            raise BudgetPolicyError("partial optional final-stage authority")
    allowed = core | {(None, category, d) for category in OPTIONAL_FINAL for d in DECODE_INDICES}
    if not set(result).issubset(allowed):
        raise BudgetPolicyError("extra top-level authority")
    return result


def _budget_authority(rows: Any, runtime_max: int) -> dict[str, dict[str, int]]:
    if not isinstance(rows, list):
        raise BudgetPolicyError("budget_authority must be a list")
    result: dict[str, dict[str, int]] = {}
    for row in rows:
        name = _text(row.get("budget_name"), "budget_name")
        if name not in BUDGETS or name in result:
            raise BudgetPolicyError("wrong/duplicate budget authority")
        requested = _integer(row.get("requested_bytes"), "requested_bytes", 1)
        actual = _integer(row.get("runtime_actual_setaside_bytes"), "runtime_actual_setaside_bytes", 1)
        maximum = _integer(row.get("runtime_max_setaside_bytes"), "runtime_max_setaside_bytes", 1)
        if requested != BUDGETS[name]:
            raise BudgetPolicyError("wrong frozen requested budget")
        if maximum != runtime_max or actual > maximum:
            raise BudgetPolicyError("runtime set-aside query-back exceeds/drifts from max authority")
        result[name] = {"requested_bytes": requested, "runtime_actual_setaside_bytes": actual,
                        "runtime_max_setaside_bytes": maximum}
    if set(result) != set(BUDGETS):
        raise BudgetPolicyError("missing/extra four-budget authority")
    return result


def _qweight_region(raw: Any, expected_bytes: int) -> dict[str, int | bool]:
    if not isinstance(raw, Mapping):
        raise BudgetPolicyError("missing qweight region")
    pointer = _integer(raw.get("pointer"), "qweight.pointer", 1)
    size = _integer(raw.get("bytes"), "qweight.bytes", 1)
    start = _integer(raw.get("span_start"), "qweight.span_start", 1)
    end = _integer(raw.get("span_end"), "qweight.span_end", 1)
    if size != expected_bytes or start != pointer or end != pointer + size:
        raise BudgetPolicyError("exact qweight window drift")
    if not _bool(raw.get("contiguous"), "qweight.contiguous"):
        raise BudgetPolicyError("qweight region is not contiguous")
    return {"pointer": pointer, "bytes": size, "span_start": start, "span_end": end,
            "contiguous": True}


def _validate_run_policy(
    receipt: Any,
    condition: str,
    budget: Mapping[str, int],
    modules: Mapping[tuple[int, str], Mapping[str, Any]],
    natural: Mapping[str, tuple[tuple[int, str], ...]],
    calls: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    mode, budget_name, requested = _condition_identity(condition)
    if not isinstance(receipt, Mapping) or _text(receipt.get("condition"), "condition") != condition:
        raise BudgetPolicyError("policy condition mismatch")
    if _text(receipt.get("status"), "policy status").upper() != "PASS":
        raise BudgetPolicyError("policy receipt did not PASS")
    if _text(receipt.get("budget_name"), "budget_name") != budget_name:
        raise BudgetPolicyError("policy budget name mismatch")
    observed = (
        _integer(receipt.get("requested_setaside_bytes"), "requested_setaside_bytes", 1),
        _integer(receipt.get("actual_setaside_bytes"), "actual_setaside_bytes", 1),
        _integer(receipt.get("query_back_actual_setaside_bytes"), "query_back_actual_setaside_bytes", 1),
        _integer(receipt.get("runtime_max_setaside_bytes"), "runtime_max_setaside_bytes", 1),
    )
    expected_budget = (requested, budget["runtime_actual_setaside_bytes"],
                       budget["runtime_actual_setaside_bytes"], budget["runtime_max_setaside_bytes"])
    if observed != expected_budget:
        raise BudgetPolicyError("runtime requested/query-back set-aside drift")
    selected = receipt.get("selected_modules")
    expected_selected = {(layer, "up_proj") for layer in LAYERS}
    if not isinstance(selected, list):
        raise BudgetPolicyError("selected_modules must be a list")
    observed_selected = {(_integer(x.get("layer_index"), "layer_index"),
                          _text(x.get("role"), "role")) for x in selected}
    if len(selected) != 28 or observed_selected != expected_selected:
        raise BudgetPolicyError("wrong exact 28-up selected module set")
    stream = _text(receipt.get("stream_identity"), "stream_identity")
    _reset(receipt.get("reset_before"), "reset_before")
    _reset(receipt.get("reset_after"), "reset_after")
    if receipt.get("other_reset_events") != []:
        raise BudgetPolicyError("reset allowed only before/after condition")
    switches = receipt.get("switches")
    if not isinstance(switches, list) or len(switches) != 28 * len(PHASES):
        raise BudgetPolicyError("missing/duplicate exact 140 policy updates")
    ratio = min(1.0, requested / FULL_UP28_BYTES)
    by_attachment: dict[tuple[str, int], Mapping[str, Any]] = {}
    durations: list[float] = []
    region_by_key: dict[tuple[int, str], dict[str, int | bool]] = {}
    for update in switches:
        phase = _text(update.get("phase"), "phase").upper()
        if phase not in PHASES:
            raise BudgetPolicyError("wrong update phase")
        index = _integer(update.get("attached_natural_order_index"), "attached_natural_order_index")
        if index >= 84:
            raise BudgetPolicyError("wrong update attachment")
        key = (_integer(update.get("layer_index"), "layer_index"), _text(update.get("role"), "role"))
        attachment = (phase, index)
        if attachment in by_attachment or natural[phase][index] != key or key not in expected_selected:
            raise BudgetPolicyError("wrong/duplicate update attachment")
        call = calls[phase][index]
        if _integer(update.get("timeline_event_index"), "timeline_event_index", 1) + 1 != _integer(
            call.get("timeline_event_index"), "timeline_event_index", 1
        ):
            raise BudgetPolicyError("policy update is not immediately before natural call")
        region = _qweight_region(call.get("qweight"), modules[key]["qweight_bytes"])
        update_pointer = _integer(update.get("base_pointer"), "base_pointer", 1)
        update_bytes = _integer(update.get("num_bytes"), "num_bytes", 1)
        if update_pointer != region["pointer"] or update_bytes != region["bytes"]:
            raise BudgetPolicyError("policy update is not exact full qweight window")
        if key in region_by_key and region_by_key[key] != region:
            raise BudgetPolicyError("qweight pointer/span drift within fresh run")
        region_by_key[key] = region
        if _text(update.get("stream_identity"), "stream_identity") != stream:
            raise BudgetPolicyError("stream identity drift")
        if _bool(update.get("reset_performed"), "reset_performed"):
            raise BudgetPolicyError("forbidden in-run reset")
        hit_ratio = _finite(update.get("hit_ratio"), "hit_ratio", positive=True)
        if not math.isclose(hit_ratio, ratio, rel_tol=0, abs_tol=1e-12):
            raise BudgetPolicyError("wrong budget-scaled hitRatio")
        observed_policy = (_text(update.get("hit_prop"), "hit_prop").upper(),
                           _text(update.get("miss_prop"), "miss_prop").upper(),
                           _bool(update.get("target_persisting"), "target_persisting"))
        expected_policy = ("NORMAL", "NORMAL", False) if mode == "CONTROL" else (
            "PERSISTING", "STREAMING", True
        )
        if observed_policy != expected_policy:
            raise BudgetPolicyError(f"{mode} policy mismatch")
        duration = _finite(update.get("api_duration_us"), "api_duration_us")
        if duration < 0:
            raise BudgetPolicyError("negative API duration")
        durations.append(duration)
        by_attachment[attachment] = update
    expected_attachments = {(phase, i) for phase in PHASES for i, key in enumerate(natural[phase])
                            if key[1] == "up_proj"}
    if set(by_attachment) != expected_attachments:
        raise BudgetPolicyError("policy updates do not match all 28 natural up calls")
    for phase in PHASES:
        timeline = 1
        for i, call in enumerate(calls[phase]):
            if natural[phase][i][1] == "up_proj":
                if _integer(by_attachment[(phase, i)].get("timeline_event_index"),
                            "timeline_event_index", 1) != timeline:
                    raise BudgetPolicyError("policy/call timeline gap")
                timeline += 1
            if _integer(call.get("timeline_event_index"), "timeline_event_index", 1) != timeline:
                raise BudgetPolicyError("policy/call timeline gap or unrecorded update")
            timeline += 1
    reported = _finite(receipt.get("total_api_duration_us"), "total_api_duration_us")
    if reported < 0 or not math.isclose(reported, sum(durations), rel_tol=1e-12, abs_tol=1e-9):
        raise BudgetPolicyError("policy API total duration mismatch")
    return {"mode": mode, "budget_name": budget_name, "requested_setaside_bytes": requested,
            "actual_setaside_bytes": budget["runtime_actual_setaside_bytes"],
            "runtime_max_setaside_bytes": budget["runtime_max_setaside_bytes"],
            "selected_module_count": 28, "update_count": 140, "hit_ratio": ratio,
            "stream_identity": stream, "api_update_durations_us": durations,
            "total_api_duration_us": reported}


def _validate_calls(raw: Any, modules: Mapping[tuple[int, str], Mapping[str, Any]],
                    natural: Mapping[str, tuple[tuple[int, str], ...]]) -> dict[str, Sequence[Mapping[str, Any]]]:
    if not isinstance(raw, Mapping) or set(raw) != set(PHASES):
        raise BudgetPolicyError("missing/extra natural-call phase")
    result = {}
    for phase in PHASES:
        rows = raw[phase]
        if not isinstance(rows, list) or len(rows) != 84:
            raise BudgetPolicyError("natural-call phase must contain exact 84 modules")
        observed = []
        for i, row in enumerate(rows):
            if _integer(row.get("natural_order_index"), "natural_order_index") != i:
                raise BudgetPolicyError("natural call order index drift")
            key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"))
            if key not in modules:
                raise BudgetPolicyError("unknown natural-call module")
            if (_text(row.get("module_class"), "module_class") != modules[key]["module_class"] or
                    _text(row.get("implementation"), "implementation") != modules[key]["implementation"] or
                    _text(row.get("backend"), "backend") != modules[key]["backend"]):
                raise BudgetPolicyError("natural-call module identity drift")
            _qweight_region(row.get("qweight"), modules[key]["qweight_bytes"])
            observed.append(key)
        if tuple(observed) != natural[phase]:
            raise BudgetPolicyError("natural call order drift")
        result[phase] = rows
    return result


def _validate_occurrences(rows: Any, authority: Mapping[tuple[int, str, int], tuple[str, str]],
                          modules: Mapping[tuple[int, str], Mapping[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != len(authority):
        raise BudgetPolicyError("missing all-84 FFN child timing event")
    result = []
    seen = set()
    for row in rows:
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"),
               _integer(row.get("decode_index"), "decode_index"))
        if key not in authority or key in seen:
            raise BudgetPolicyError("wrong/duplicate FFN child timing event")
        seen.add(key)
        module = modules[key[:2]]
        if (_text(row.get("module_class"), "module_class") != module["module_class"] or
                _text(row.get("implementation"), "implementation") != module["implementation"] or
                _text(row.get("backend"), "backend") != module["backend"]):
            raise BudgetPolicyError("FFN child module identity drift")
        if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[key[2]]:
            raise BudgetPolicyError("FFN child token drift")
        shas = (_sha(row.get("input_sha256"), "input_sha256"),
                _sha(row.get("output_sha256"), "output_sha256"))
        if shas != authority[key]:
            raise BudgetPolicyError("FFN child SHA drift")
        result.append({"layer_index": key[0], "role": key[1], "decode_index": key[2],
                       "timing_ms": _finite(row.get("timing_ms"), "FFN child timing", positive=True)})
    return result


def _validate_top(rows: Any, authority: Mapping[tuple[int | None, str, int], tuple[str, str]]) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != len(authority):
        raise BudgetPolicyError("missing top-level timing event")
    result = []
    seen = set()
    for row in rows:
        category = _text(row.get("category"), "top_level.category")
        decode = _integer(row.get("decode_index"), "top_level.decode_index")
        if category in OPTIONAL_FINAL:
            if row.get("layer_index") is not None:
                raise BudgetPolicyError("final top-level timing must have null layer_index")
            layer = None
        else:
            layer = _integer(row.get("layer_index"), "top_level.layer_index")
        key = (layer, category, decode)
        if key not in authority or key in seen:
            raise BudgetPolicyError("wrong/duplicate top-level timing event")
        seen.add(key)
        if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[decode]:
            raise BudgetPolicyError("top-level token drift")
        shas = (_sha(row.get("input_sha256"), "input_sha256"),
                _sha(row.get("output_sha256"), "output_sha256"))
        if shas != authority[key]:
            raise BudgetPolicyError("top-level SHA drift")
        result.append({"layer_index": layer, "category": category, "decode_index": decode,
                       "timing_ms": _finite(row.get("timing_ms"), "top-level timing", positive=True)})
    return result


def consume_budget_policy_runs(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the complete 4-budget x CONTROL/FAIR x 7 native matrix."""
    if document.get("schema_version") != 1:
        raise BudgetPolicyError("unsupported budget policy schema")
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    _tokens(document.get("generated_token_ids"))
    runtime_max = _integer(document.get("runtime_max_setaside_bytes"), "runtime_max_setaside_bytes", 1)
    budgets = _budget_authority(document.get("budget_authority"), runtime_max)
    modules = _module_authority(document.get("module_authority"))
    natural = _natural_order(document.get("natural_order"), modules)
    ffn_expected = {(layer, role, d) for layer in LAYERS for role in ROLES for d in DECODE_INDICES}
    ffn_authority = _sha_authority(document.get("occurrence_authority"), ffn_expected)
    top_authority = _top_authority(document.get("top_level_authority"))
    decode_authority = document.get("decode_authority")
    if not isinstance(decode_authority, list) or len(decode_authority) != 4:
        raise BudgetPolicyError("decode_authority must contain exact D0-D3 rows")
    decode_shas: dict[int, tuple[str, str]] = {}
    for row in decode_authority:
        d = _integer(row.get("decode_index"), "decode_index")
        if d not in DECODE_INDICES or d in decode_shas:
            raise BudgetPolicyError("wrong/duplicate decode authority")
        if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[d]:
            raise BudgetPolicyError("decode authority token drift")
        decode_shas[d] = (_sha(row.get("input_sha256"), "input_sha256"),
                          _sha(row.get("output_sha256"), "output_sha256"))
    conditions = document.get("conditions")
    if not isinstance(conditions, list):
        raise BudgetPolicyError("conditions must be a list")
    by_condition: dict[str, Mapping[str, Any]] = {}
    for item in conditions:
        name = _text(item.get("condition"), "condition")
        if name in by_condition:
            raise BudgetPolicyError("duplicate condition")
        by_condition[name] = item
    if set(by_condition) != set(CONDITIONS):
        raise BudgetPolicyError("missing/extra frozen eight-condition matrix")
    processes: set[str] = set()
    points: list[dict[str, Any]] = []
    actual_by_budget: dict[str, set[int]] = defaultdict(set)
    for condition in CONDITIONS:
        mode, budget_name, _ = _condition_identity(condition)
        runs = by_condition[condition].get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise BudgetPolicyError("each condition requires exactly 7 fresh runs")
        reps = set()
        for run in runs:
            rep = _integer(run.get("rep"), "rep")
            if rep not in range(EXPECTED_REPS) or rep in reps:
                raise BudgetPolicyError("missing/duplicate condition rep")
            reps.add(rep)
            process = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process in processes:
                raise BudgetPolicyError("fresh process reused across matrix")
            processes.add(process)
            if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
                raise BudgetPolicyError("prefix SHA drift")
            _tokens(run.get("generated_token_ids"))
            calls = _validate_calls(run.get("natural_calls"), modules, natural)
            policy = _validate_run_policy(run.get("policy_receipt"), condition, budgets[budget_name],
                                          modules, natural, calls)
            actual_by_budget[budget_name].add(policy["actual_setaside_bytes"])
            api_total = _finite(run.get("policy_api_duration_us"), "policy_api_duration_us")
            if not math.isclose(api_total, policy["total_api_duration_us"], rel_tol=1e-12, abs_tol=1e-9):
                raise BudgetPolicyError("run policy API duration mismatch")
            ffn = _validate_occurrences(run.get("occurrences"), ffn_authority, modules)
            top = _validate_top(run.get("top_level_occurrences"), top_authority)
            decode_rows = run.get("decode_steps")
            if not isinstance(decode_rows, list) or len(decode_rows) != 4:
                raise BudgetPolicyError("missing decode timing event")
            decode = {}
            for row in decode_rows:
                d = _integer(row.get("decode_index"), "decode_index")
                if d not in DECODE_INDICES or d in decode:
                    raise BudgetPolicyError("wrong/duplicate decode timing event")
                if _integer(row.get("generated_token_id"), "generated_token_id") != EXPECTED_TOKENS[d]:
                    raise BudgetPolicyError("decode token drift")
                if (_sha(row.get("input_sha256"), "input_sha256"),
                        _sha(row.get("output_sha256"), "output_sha256")) != decode_shas[d]:
                    raise BudgetPolicyError("decode SHA drift")
                decode[d] = _finite(row.get("timing_ms"), "decode timing", positive=True)
            points.append({"condition": condition, "mode": mode, "budget_name": budget_name,
                           "rep": rep, "fresh_process_id": process,
                           "requested_setaside_bytes": policy["requested_setaside_bytes"],
                           "actual_setaside_bytes": policy["actual_setaside_bytes"],
                           "runtime_max_setaside_bytes": policy["runtime_max_setaside_bytes"],
                           "hit_ratio": policy["hit_ratio"],
                           "decode_step_ms": {f"D{d}": decode[d] for d in DECODE_INDICES},
                           "ffn_child_timing": ffn, "top_level_timing": top,
                           "policy_api_update_durations_us": policy["api_update_durations_us"],
                           "policy_api_duration_us": policy["total_api_duration_us"]})
    if any(len(values) != 1 for values in actual_by_budget.values()):
        raise BudgetPolicyError("runtime actual set-aside query-back drift within budget")
    return {"status": "PASS", "authority": "RAW_4_BUDGET_NATIVE_POLICY_EVIDENCE_ONLY",
            "condition_count": len(CONDITIONS), "fresh_process_count": len(processes),
            "module_count": len(modules), "selected_module_count": 28,
            "budget_authority": budgets,
            "no_alignment_law_inferred": True,
            "run_aligned_points": points}
