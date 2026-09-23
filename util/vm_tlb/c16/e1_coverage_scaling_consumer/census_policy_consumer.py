#!/usr/bin/env python3
"""Fail-closed raw consumers for the C16 E1 FFN census and coverage policy."""
from __future__ import annotations

import math
import re
import statistics
from collections import defaultdict
from typing import Any, Mapping, Sequence


class CoverageIdentityError(ValueError):
    pass


LAYERS = tuple(range(28))
ROLES = ("gate_proj", "up_proj", "down_proj")
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
DECODE_INDICES = tuple(range(4))
EXPECTED_TOKENS = (23578, 11, 323, 3950)
EXPECTED_REPS = 7
REQUESTED_SETASIDE_BYTES = 33_947_648
ACTUAL_SETASIDE_BYTES = 37_748_736
EXPECTED_MODULE_CLASS = "WQLinear_GEMM"
EXPECTED_IMPLEMENTATION = "AWQ_FP16_INPUT"
SELECTION_ORDER = (0, 14, 27, 7, 20, 3, 10, 17, 23, 5, 12, 25, 1, 2,
                   4, 6, 8, 9, 11, 13, 15, 16, 18, 19, 21, 22, 24, 26)
LAYER_SETS = {
    "N1": SELECTION_ORDER[:1], "N2": SELECTION_ORDER[:2],
    "N4": SELECTION_ORDER[:4], "N8": SELECTION_ORDER[:8],
    "N14A": SELECTION_ORDER[:14],
    "N14B": tuple(x for x in LAYERS if x not in SELECTION_ORDER[:14]),
    "N28": SELECTION_ORDER,
}
SET_NAMES = ("N1", "N2", "N4", "N8", "N14A", "N14B", "N28")
CONDITIONS = tuple(f"{m}_{n}" for n in SET_NAMES for m in ("CONTROL", "FAIR"))
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _text(v: Any, label: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise CoverageIdentityError(f"missing/empty {label}")
    return v.strip()


def _integer(v: Any, label: str, minimum: int = 0) -> int:
    if isinstance(v, bool):
        raise CoverageIdentityError(f"invalid {label}")
    try:
        out = int(str(v).strip(), 10)
    except (TypeError, ValueError) as exc:
        raise CoverageIdentityError(f"invalid {label}: {v!r}") from exc
    if str(v).strip() != str(out) or out < minimum:
        raise CoverageIdentityError(f"invalid {label}: {v!r}")
    return out


def _finite(v: Any, label: str, positive: bool = False) -> float:
    try:
        out = float(v)
    except (TypeError, ValueError) as exc:
        raise CoverageIdentityError(f"invalid {label}: {v!r}") from exc
    if not math.isfinite(out) or (positive and out <= 0):
        raise CoverageIdentityError(f"nonfinite/nonpositive {label}: {v!r}")
    return out


def _bool(v: Any, label: str) -> bool:
    if isinstance(v, bool):
        return v
    if v in (0, 1):
        return bool(v)
    if isinstance(v, str) and v.strip().lower() in {"true", "false"}:
        return v.strip().lower() == "true"
    raise CoverageIdentityError(f"invalid boolean {label}")


def _sha(v: Any, label: str) -> str:
    out = str(v).strip().lower()
    if not HEX64.fullmatch(out):
        raise CoverageIdentityError(f"invalid {label}")
    return out


def _tokens(v: Any) -> tuple[int, ...]:
    if not isinstance(v, list):
        raise CoverageIdentityError("generated_token_ids must be a list")
    out = tuple(_integer(x, "generated_token_id") for x in v)
    if out != EXPECTED_TOKENS:
        raise CoverageIdentityError("token sequence drift")
    return out


def _stats(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        raise CoverageIdentityError("empty samples")
    xs = [_finite(x, "sample", True) for x in values]
    mean = statistics.fmean(xs)
    return {"sample_count": len(xs), "min_ms": min(xs),
            "median_ms": statistics.median(xs), "max_ms": max(xs),
            "mean_ms": mean, "cv": statistics.pstdev(xs) / mean}


def _qweight(v: Any, label: str = "qweight") -> dict[str, Any]:
    if not isinstance(v, Mapping):
        raise CoverageIdentityError(f"missing {label}")
    shape = v.get("shape")
    if not isinstance(shape, list) or not shape:
        raise CoverageIdentityError(f"invalid {label}.shape")
    out = {"pointer": _integer(v.get("pointer"), f"{label}.pointer", 1),
           "bytes": _integer(v.get("bytes"), f"{label}.bytes", 1),
           "shape": [_integer(x, f"{label}.shape", 1) for x in shape],
           "contiguous": _bool(v.get("contiguous"), f"{label}.contiguous")}
    if not out["contiguous"]:
        raise CoverageIdentityError(f"{label} is not contiguous")
    return out


def _module_authority(rows: Any) -> tuple[dict[tuple[int, str], dict[str, Any]], dict[str, bool]]:
    if not isinstance(rows, list):
        raise CoverageIdentityError("module_authority must be a list")
    out, support = {}, defaultdict(set)
    for row in rows:
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"))
        if key[0] not in LAYERS or key[1] not in ROLES or key in out:
            raise CoverageIdentityError("wrong/duplicate layer/module")
        supported = _bool(row.get("supported"), "supported")
        item = {"supported": supported,
                "module_class": _text(row.get("module_class"), "module_class"),
                "backend": _text(row.get("backend"), "backend"),
                "implementation": row.get("implementation"),
                "qweight": _qweight(row.get("qweight"))}
        if supported and item["module_class"] != EXPECTED_MODULE_CLASS:
            raise CoverageIdentityError("supported role has wrong module class")
        if supported and _text(item["implementation"], "implementation") != EXPECTED_IMPLEMENTATION:
            raise CoverageIdentityError("supported role has wrong implementation")
        out[key] = item
        support[key[1]].add(supported)
    if set(out) != {(l, r) for l in LAYERS for r in ROLES}:
        raise CoverageIdentityError("missing layer/module from 28x3 census")
    if any(len(support[r]) != 1 for r in ROLES):
        raise CoverageIdentityError("inconsistent support within role")
    return out, {r: next(iter(support[r])) for r in ROLES}


def validate_layer_selection_manifest(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise CoverageIdentityError("missing layer selection manifest")
    if _text(raw.get("status"), "selection status") != "FROZEN_BEFORE_COVERAGE_PRODUCER":
        raise CoverageIdentityError("layer selection was not frozen before producer data")
    if not _bool(raw.get("no_post_data_selection"), "no_post_data_selection") or \
            _bool(raw.get("selected_after_observing_data", False), "selected_after_observing_data"):
        raise CoverageIdentityError("post-data layer selection attempt")
    if tuple(raw.get("selection_order", ())) != SELECTION_ORDER:
        raise CoverageIdentityError("selection order drift")
    sets = raw.get("sets")
    if not isinstance(sets, Mapping) or set(sets) != set(LAYER_SETS):
        raise CoverageIdentityError("wrong layer set names")
    for name, expected in LAYER_SETS.items():
        if tuple(sets[name]) != expected:
            raise CoverageIdentityError(f"wrong frozen layer set {name}")
    return {"status": "PASS", "authority": "FROZEN_PRECONTRACT",
            "selection_order": list(SELECTION_ORDER),
            "sets": {n: list(LAYER_SETS[n]) for n in SET_NAMES},
            "no_post_data_selection": True}


def consume_ffn_census(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate 28x3 FFN census x seven runs and compute run-aligned shares."""
    if document.get("schema_version") != 1:
        raise CoverageIdentityError("unsupported census schema")
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    tokens = _tokens(document.get("generated_token_ids"))
    modules, role_support = _module_authority(document.get("module_authority"))
    expected = {(l, r, d) for (l, r), m in modules.items() if m["supported"] for d in DECODE_INDICES}
    authority = {}
    if not isinstance(document.get("occurrence_authority"), list):
        raise CoverageIdentityError("occurrence_authority must be a list")
    for row in document["occurrence_authority"]:
        key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"),
               _integer(row.get("decode_index"), "decode_index"))
        if key not in expected or key in authority:
            raise CoverageIdentityError("wrong/duplicate occurrence authority")
        if _integer(row.get("generated_token_id"), "generated_token_id") != tokens[key[2]]:
            raise CoverageIdentityError("occurrence authority token drift")
        authority[key] = (_sha(row.get("input_sha256"), "input_sha256"),
                          _sha(row.get("output_sha256"), "output_sha256"))
    if set(authority) != expected:
        raise CoverageIdentityError("missing occurrence authority")
    runs = document.get("runs")
    if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
        raise CoverageIdentityError("census requires exactly 7 fresh runs")
    reps, processes, shares = set(), set(), []
    layer_values = defaultdict(list)
    for run in runs:
        rep = _integer(run.get("rep"), "rep")
        if rep not in range(EXPECTED_REPS) or rep in reps:
            raise CoverageIdentityError("missing/duplicate rep")
        reps.add(rep)
        process = _text(run.get("fresh_process_id"), "fresh_process_id")
        if process in processes:
            raise CoverageIdentityError("fresh process reused")
        processes.add(process)
        if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
            raise CoverageIdentityError("prefix SHA drift")
        _tokens(run.get("generated_token_ids"))
        decode = {}
        if not isinstance(run.get("decode_steps"), list) or len(run["decode_steps"]) != 4:
            raise CoverageIdentityError("missing/duplicate decode step")
        for row in run["decode_steps"]:
            d = _integer(row.get("decode_index"), "decode_index")
            if d not in DECODE_INDICES or d in decode:
                raise CoverageIdentityError("wrong/duplicate decode step")
            if _integer(row.get("generated_token_id"), "generated_token_id") != tokens[d]:
                raise CoverageIdentityError("decode token drift")
            decode[d] = _finite(row.get("timing_ms"), "decode timing", True)
        events = run.get("occurrences")
        if not isinstance(events, list) or len(events) != len(expected):
            raise CoverageIdentityError("missing layer event")
        observed = {}
        for row in events:
            key = (_integer(row.get("layer_index"), "layer_index"), _text(row.get("role"), "role"),
                   _integer(row.get("decode_index"), "decode_index"))
            if key not in expected or key in observed:
                raise CoverageIdentityError("wrong/duplicate layer event")
            module = modules[key[:2]]
            if (_text(row.get("module_class"), "module_class") != module["module_class"] or
                    _text(row.get("backend"), "backend") != module["backend"] or
                    _text(row.get("implementation"), "implementation") != module["implementation"]):
                raise CoverageIdentityError("module identity drift")
            if _qweight(row.get("qweight")) != module["qweight"]:
                raise CoverageIdentityError("qweight identity drift")
            if _integer(row.get("generated_token_id"), "generated_token_id") != tokens[key[2]]:
                raise CoverageIdentityError("occurrence token drift")
            if (_sha(row.get("input_sha256"), "input_sha256"),
                    _sha(row.get("output_sha256"), "output_sha256")) != authority[key]:
                raise CoverageIdentityError("occurrence SHA drift")
            observed[key] = _finite(row.get("timing_ms"), "occurrence timing", True)
        for (l, r, _d), value in observed.items():
            layer_values[(r, l)].append(value)
        for d in DECODE_INDICES:
            sums = {r: sum(observed[(l, r, d)] for l in LAYERS) if role_support[r] else 0.0
                    for r in ROLES}
            shares.append({"rep": rep, "decode_index": d, "decode_step_ms": decode[d],
                           "role_share": {r: sums[r] / decode[d] if role_support[r] else None for r in ROLES},
                           "total_supported_ffn_share": sum(sums.values()) / decode[d]})
    role_analysis = {}
    for role in ROLES:
        if not role_support[role]:
            role_analysis[role] = {"supported": False, "per_layer": []}
            continue
        per_layer = [{"layer_index": l, **_stats(layer_values[(role, l)])} for l in LAYERS]
        ranked = sorted(per_layer, key=lambda x: x["median_ms"], reverse=True)
        medians, total = [x["median_ms"] for x in per_layer], sum(x["median_ms"] for x in per_layer)
        role_analysis[role] = {"supported": True, "per_layer": per_layer,
            "layer_median_distribution_ms": {"min": min(medians),
                "median": statistics.median(medians), "max": max(medians)},
            "top1_share": ranked[0]["median_ms"] / total,
            "top4_share": sum(x["median_ms"] for x in ranked[:4]) / total,
            "top_layers": [x["layer_index"] for x in ranked[:4]]}
    return {"status": "PASS", "authority": "RAW_RUN_ALIGNED_CENSUS_ONLY",
            "fresh_process_count": len(processes), "role_support": role_support,
            "run_aligned_shares": sorted(shares, key=lambda x: (x["rep"], x["decode_index"])),
            "role_analysis": role_analysis}


def _reset(raw: Any, label: str, index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or _text(raw.get("status"), f"{label}.status").upper() != "PASS" or \
            not _bool(raw.get("performed"), f"{label}.performed"):
        raise CoverageIdentityError(f"missing/failed {label}")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise CoverageIdentityError(f"{label} is not a persistence reset")
    if _integer(raw.get("event_index"), f"{label}.event_index") != index:
        raise CoverageIdentityError(f"wrong {label} event index")
    return {"status": "PASS", "performed": True, "operation": operation, "event_index": index}


def validate_coverage_policy_receipt(receipt: Mapping[str, Any], condition: str,
                                     regions: Mapping[int, Mapping[str, Any]]) -> dict[str, Any]:
    if condition not in CONDITIONS:
        raise CoverageIdentityError("unsupported coverage condition")
    mode, set_name = condition.split("_", 1)
    selected = LAYER_SETS[set_name]
    if not isinstance(receipt, Mapping) or _text(receipt.get("condition"), "condition") != condition:
        raise CoverageIdentityError("policy condition mismatch")
    if _text(receipt.get("status"), "status").upper() != "PASS":
        raise CoverageIdentityError("policy receipt did not PASS")
    if tuple(receipt.get("selected_layers", ())) != selected:
        raise CoverageIdentityError("wrong selected layer set")
    if _integer(receipt.get("requested_setaside_bytes"), "requested_setaside_bytes") != REQUESTED_SETASIDE_BYTES:
        raise CoverageIdentityError("requested set-aside drift")
    if _integer(receipt.get("actual_setaside_bytes"), "actual_setaside_bytes") != ACTUAL_SETASIDE_BYTES:
        raise CoverageIdentityError("actual set-aside drift")
    stream = _text(receipt.get("stream_identity"), "stream_identity")
    sequence = tuple((p, l) for p in PHASES for l in selected)
    switches = receipt.get("switches")
    if not isinstance(switches, list) or len(switches) != len(sequence):
        raise CoverageIdentityError("missing/duplicate policy update")
    before = _reset(receipt.get("reset_before"), "reset_before", 0)
    normalized, ratio = [], 1.0 / len(selected)
    for i, (row, (phase, layer)) in enumerate(zip(switches, sequence), 1):
        if _integer(row.get("sequence_index"), "sequence_index") != i or \
                _text(row.get("phase"), "phase").upper() != phase or \
                _integer(row.get("layer_index"), "layer_index") != layer:
            raise CoverageIdentityError("wrong PREFILL/D0-D3 layer update order")
        if _text(row.get("role"), "role") != "up_proj":
            raise CoverageIdentityError("policy update targets wrong module")
        region = regions[layer]
        if (_integer(row.get("base_pointer"), "base_pointer", 1) != region["pointer"] or
                _integer(row.get("num_bytes"), "num_bytes", 1) != region["bytes"]):
            raise CoverageIdentityError("policy update is not exact full up qweight window")
        if _text(row.get("stream_identity"), "stream_identity") != stream:
            raise CoverageIdentityError("stream identity drift")
        if _bool(row.get("reset_performed"), "reset_performed"):
            raise CoverageIdentityError("forbidden in-run reset")
        observed_ratio = _finite(row.get("hit_ratio"), "hit_ratio")
        if not math.isclose(observed_ratio, ratio, rel_tol=0, abs_tol=1e-12):
            raise CoverageIdentityError("wrong 1/N hitRatio")
        policy = (_text(row.get("hit_prop"), "hit_prop").upper(),
                  _text(row.get("miss_prop"), "miss_prop").upper(),
                  _bool(row.get("target_persisting"), "target_persisting"))
        if mode == "CONTROL" and policy != ("NORMAL", "NORMAL", False):
            raise CoverageIdentityError("CONTROL must be NORMAL/NORMAL and non-persisting")
        if mode == "FAIR" and policy != ("PERSISTING", "STREAMING", True):
            raise CoverageIdentityError("FAIR must be PERSISTING/STREAMING")
        duration = _finite(row.get("api_duration_us"), "api_duration_us")
        if duration < 0:
            raise CoverageIdentityError("negative API duration")
        normalized.append({"sequence_index": i, "phase": phase, "layer_index": layer,
                           "hit_ratio": observed_ratio, "api_duration_us": duration})
    after = _reset(receipt.get("reset_after"), "reset_after", len(sequence) + 1)
    if receipt.get("other_reset_events", []) != []:
        raise CoverageIdentityError("reset allowed only before/after condition")
    return {"status": "PASS", "condition": condition, "selected_layers": list(selected),
            "requested_setaside_bytes": REQUESTED_SETASIDE_BYTES,
            "actual_setaside_bytes": ACTUAL_SETASIDE_BYTES, "stream_identity": stream,
            "reset_before": before, "switches": normalized, "reset_after": after,
            "api_overhead_us": sum(x["api_duration_us"] for x in normalized)}


def consume_coverage_policy_runs(document: Mapping[str, Any]) -> dict[str, Any]:
    if document.get("schema_version") != 1:
        raise CoverageIdentityError("unsupported policy run schema")
    manifest = validate_layer_selection_manifest(document.get("layer_selection_manifest"))
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    tokens = _tokens(document.get("generated_token_ids"))
    regions = {}
    rows = document.get("up_qweight_regions")
    if not isinstance(rows, list):
        raise CoverageIdentityError("up_qweight_regions must be a list")
    for row in rows:
        layer = _integer(row.get("layer_index"), "layer_index")
        if layer not in LAYERS or layer in regions:
            raise CoverageIdentityError("wrong/duplicate up qweight layer")
        if (_text(row.get("role"), "role") != "up_proj" or
                _text(row.get("module_class"), "module_class") != EXPECTED_MODULE_CLASS or
                _text(row.get("implementation"), "implementation") != EXPECTED_IMPLEMENTATION):
            raise CoverageIdentityError("wrong up_proj module identity")
        regions[layer] = _qweight(row.get("qweight"))
    if set(regions) != set(LAYERS):
        raise CoverageIdentityError("missing up qweight layer")
    expected = {(l, d) for l in LAYERS for d in DECODE_INDICES}
    authority = {}
    if not isinstance(document.get("occurrence_authority"), list):
        raise CoverageIdentityError("occurrence_authority must be a list")
    for row in document["occurrence_authority"]:
        key = (_integer(row.get("layer_index"), "layer_index"),
               _integer(row.get("decode_index"), "decode_index"))
        if key not in expected or key in authority or _text(row.get("role"), "role") != "up_proj":
            raise CoverageIdentityError("wrong/duplicate up occurrence authority")
        if _integer(row.get("generated_token_id"), "generated_token_id") != tokens[key[1]]:
            raise CoverageIdentityError("occurrence authority token drift")
        authority[key] = (_sha(row.get("input_sha256"), "input_sha256"),
                          _sha(row.get("output_sha256"), "output_sha256"))
    if set(authority) != expected:
        raise CoverageIdentityError("missing up occurrence authority")
    blocks = document.get("conditions")
    if not isinstance(blocks, list):
        raise CoverageIdentityError("conditions must be a list")
    seen, processes, points = set(), set(), []
    for block in blocks:
        condition = _text(block.get("condition"), "condition")
        if condition not in CONDITIONS or condition in seen:
            raise CoverageIdentityError("wrong/duplicate condition")
        seen.add(condition)
        runs = block.get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise CoverageIdentityError("condition requires exactly 7 fresh runs")
        reps = set()
        for run in runs:
            rep = _integer(run.get("rep"), "rep")
            if rep not in range(EXPECTED_REPS) or rep in reps:
                raise CoverageIdentityError("missing/duplicate rep")
            reps.add(rep)
            process = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process in processes:
                raise CoverageIdentityError("fresh process reused")
            processes.add(process)
            if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
                raise CoverageIdentityError("prefix SHA drift")
            _tokens(run.get("generated_token_ids"))
            policy = validate_coverage_policy_receipt(run.get("policy_receipt"), condition, regions)
            events = run.get("occurrences")
            if not isinstance(events, list) or len(events) != len(expected):
                raise CoverageIdentityError("all 28 up occurrences per decode must be present")
            observed = {}
            for row in events:
                key = (_integer(row.get("layer_index"), "layer_index"),
                       _integer(row.get("decode_index"), "decode_index"))
                if key not in expected or key in observed or _text(row.get("role"), "role") != "up_proj":
                    raise CoverageIdentityError("wrong/duplicate up occurrence")
                if _integer(row.get("generated_token_id"), "generated_token_id") != tokens[key[1]]:
                    raise CoverageIdentityError("occurrence token drift")
                identity = (_sha(row.get("input_sha256"), "input_sha256"),
                            _sha(row.get("output_sha256"), "output_sha256"))
                if identity != authority[key]:
                    raise CoverageIdentityError("occurrence SHA drift")
                if _qweight(row.get("qweight")) != regions[key[0]]:
                    raise CoverageIdentityError("qweight identity drift")
                observed[key] = _finite(row.get("timing_ms"), "up timing", True)
            decode = {}
            if not isinstance(run.get("decode_steps"), list) or len(run["decode_steps"]) != 4:
                raise CoverageIdentityError("missing decode step")
            for row in run["decode_steps"]:
                d = _integer(row.get("decode_index"), "decode_index")
                if d not in DECODE_INDICES or d in decode:
                    raise CoverageIdentityError("wrong/duplicate decode step")
                if _integer(row.get("generated_token_id"), "generated_token_id") != tokens[d]:
                    raise CoverageIdentityError("decode token drift")
                decode[d] = _finite(row.get("timing_ms"), "decode timing", True)
            set_name = condition.split("_", 1)[1]
            points.append({"condition": condition, "rep": rep,
                "selected_layers": list(LAYER_SETS[set_name]),
                "up_timing_ms": [{"layer_index": l, "decode_index": d,
                                  "timing_ms": observed[(l, d)]}
                                 for d in DECODE_INDICES for l in LAYERS],
                "decode_step_ms": [{"decode_index": d, "timing_ms": decode[d]} for d in DECODE_INDICES],
                "api_overhead_us": policy["api_overhead_us"]})
    if seen != set(CONDITIONS):
        raise CoverageIdentityError("coverage condition matrix mismatch")
    return {"status": "PASS", "authority": "RAW_RUN_AND_ORDERED_POLICY_RECEIPTS_ONLY",
            "manifest": manifest, "condition_count": len(seen),
            "fresh_process_count": len(processes), "run_aligned_points": points}
