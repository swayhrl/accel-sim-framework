#!/usr/bin/env python3
"""Fail-closed raw NCU consumer for C16 E1 operator-family expansion.

Only BASE, SESSION, PROFILE, runtime-query, module-authority, and complete
natural-call policy-history evidence are accepted as computation authority.
Producer summary tables are deliberately outside this interface.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping, Sequence


class OperatorNCUError(ValueError):
    """Raw operator-family NCU evidence is absent or inconsistent."""


ROLES = ("gate_proj", "up_proj", "down_proj")
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
REQUESTED_SETASIDE_BYTES = 33_947_648
ACTUAL_SETASIDE_BYTES = 37_748_736
PRIMARY_MATRIX = frozenset(
    (condition, role)
    for role, family in (("gate_proj", "GATE28"),
                         ("up_proj", "UP28"),
                         ("down_proj", "DOWN28"))
    for condition in (f"CONTROL_{family}", f"FAIR_{family}",
                      "CONTROL_GUD84", "FAIR_GUD84")
)
FULLHINT_MATRIX = frozenset(
    (condition, role)
    for condition in ("CONTROL_FULL_GUD84", "FULLHINT_GUD84")
    for role in ROLES
)
BASE_METRICS = {
    "L1_TEX_BYTES": ("l1tex__t_bytes.sum", {"byte", "bytes"}),
    "L2_BYTES": ("lts__t_bytes.sum", {"byte", "bytes"}),
    "DRAM_BYTES": ("dram__bytes.sum", {"byte", "bytes"}),
}
ADDITIVE_UNITS = {
    "L1_TEX_BYTES": {"byte", "bytes"},
    "L2_BYTES": {"byte", "bytes"},
    "DRAM_BYTES": {"byte", "bytes"},
    "KERNEL_ELAPSED_CYCLES": {"cycle", "cycles"},
    "L2_READ_HIT_SECTORS": {"sector", "sectors"},
    "L2_READ_MISS_SECTORS": {"sector", "sectors"},
    "DRAM_READ_SECTORS": {"sector", "sectors"},
    "DRAM_READ_BYTES": {"byte", "bytes"},
}
PER_KERNEL_UNITS = {
    "L2_READ_HIT_RATE": {"%", "percent"},
    "LONG_SCOREBOARD_STALL": {"%", "percent"},
    "MEMORY_DEPENDENCY_STALL": {"%", "percent"},
    "MEMORY_PIPE_UTILIZATION": {"%", "percent"},
    "LSU_UTILIZATION": {"%", "percent"},
    "ACHIEVED_ACTIVE_WARPS": {"warp", "warps"},
    "ACHIEVED_OCCUPANCY": {"%", "percent"},
}
KNOWN_CATEGORIES = frozenset((*ADDITIVE_UNITS, *PER_KERNEL_UNITS))
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OperatorNCUError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise OperatorNCUError(f"invalid {label}")
    token = str(value).strip()
    try:
        result = int(token)
    except (TypeError, ValueError) as exc:
        raise OperatorNCUError(f"invalid {label}: {value!r}") from exc
    if str(result) != token or result < minimum:
        raise OperatorNCUError(f"invalid {label}: {value!r}")
    return result


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise OperatorNCUError(f"invalid {label}") from exc
    if not math.isfinite(result):
        raise OperatorNCUError(f"nonfinite {label}")
    return result


def _sha(value: Any, label: str) -> str:
    result = str(value).strip().lower()
    if not HEX64.fullmatch(result):
        raise OperatorNCUError(f"invalid {label}")
    return result


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path(root: Path, value: Any, label: str) -> Path:
    result = root / _text(value, label)
    if not result.is_file() or result.stat().st_size == 0:
        raise OperatorNCUError(f"missing or empty {label}: {result}")
    return result


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise OperatorNCUError(f"invalid metric value {label}") from exc
    if not result.is_finite():
        raise OperatorNCUError(f"nonfinite metric value {label}")
    return result


def _number(value: Decimal) -> int | float:
    return int(value) if value == value.to_integral_value() else float(value)


def _options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text,
                      re.MULTILINE)


def _exact_range(cell: str, target: str) -> bool:
    return len(re.findall(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)",
                          cell.strip())) == 1


def _query(raw: Any, root: Path) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS":
        raise OperatorNCUError("runtime metric query receipt must be one PASS object")
    command = _text(raw.get("command"), "runtime_metric_query.command")
    if "query" not in command.lower() or "metric" not in command.lower():
        raise OperatorNCUError("runtime query command is ambiguous")
    version = _text(raw.get("ncu_version"), "runtime_metric_query.ncu_version")
    path = _path(root, raw.get("path"), "runtime_metric_query.path")
    claimed = _sha(raw.get("sha256"), "runtime_metric_query.sha256")
    if claimed != _file_sha(path):
        raise OperatorNCUError("runtime metric query SHA mismatch")
    if version not in path.read_text(encoding="utf-8", errors="replace"):
        raise OperatorNCUError("runtime metric query/version identity ambiguity")
    return {"status": "PASS", "command": command, "ncu_version": version,
            "path": str(path), "sha256": claimed}


def _catalog(raw: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(raw, list) or not raw:
        raise OperatorNCUError("metric_availability must be nonempty")
    available, unavailable, categories, names = [], [], set(), set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise OperatorNCUError("metric catalog row must be an object")
        category = _text(item.get("category"), "metric.category")
        if category not in KNOWN_CATEGORIES or category in categories:
            raise OperatorNCUError("unknown/duplicate metric category")
        categories.add(category)
        if not isinstance(item.get("available"), bool):
            raise OperatorNCUError("metric availability must be boolean")
        policy = "SEMANTIC_SUM" if category in ADDITIVE_UNITS else "PER_KERNEL_ONLY"
        if item.get("aggregation", policy) != policy:
            raise OperatorNCUError(f"aggregation mismatch for {category}")
        if not item["available"]:
            if item.get("metric_name") not in (None, "") or item.get("unit") not in (None, ""):
                raise OperatorNCUError("unavailable metric claims name/unit")
            unavailable.append({"category": category, "available": False,
                                "reason": _text(item.get("reason"), f"{category}.reason"),
                                "aggregation": policy})
            continue
        name = _text(item.get("metric_name"), f"{category}.metric_name")
        unit = _text(item.get("unit"), f"{category}.unit")
        if name in names:
            raise OperatorNCUError("duplicate exact metric name")
        names.add(name)
        allowed = ADDITIVE_UNITS.get(category, PER_KERNEL_UNITS.get(category, set()))
        if unit not in allowed:
            raise OperatorNCUError(f"unit mismatch for category {category}")
        available.append({"category": category, "available": True,
                          "metric_name": name, "unit": unit, "aggregation": policy})
    by_category = {row["category"]: row for row in available}
    for category, (exact_name, _units) in BASE_METRICS.items():
        if category not in by_category or by_category[category]["metric_name"] != exact_name:
            raise OperatorNCUError(f"missing required base metric {exact_name}")
    return available, unavailable


def _module_key(raw: Mapping[str, Any], label: str) -> tuple[int, str]:
    layer = _integer(raw.get("layer_index"), f"{label}.layer_index")
    role = _text(raw.get("role"), f"{label}.role")
    if layer not in range(28) or role not in ROLES:
        raise OperatorNCUError(f"invalid {label} module identity")
    return layer, role


def _module_authority(raw: Any) -> tuple[
        dict[tuple[int, str], dict[str, Any]],
        dict[str, list[tuple[int, str]]]]:
    if not isinstance(raw, Mapping):
        raise OperatorNCUError("module_authority must be an object")
    modules = raw.get("modules")
    order = raw.get("natural_call_order")
    if not isinstance(modules, list) or len(modules) != 84:
        raise OperatorNCUError("module authority requires exact 84 modules")
    normalized: dict[tuple[int, str], dict[str, Any]] = {}
    intervals = []
    for index, item in enumerate(modules):
        if not isinstance(item, Mapping):
            raise OperatorNCUError("module authority row must be an object")
        key = _module_key(item, f"modules[{index}]")
        if key in normalized:
            raise OperatorNCUError("duplicate module authority identity")
        if _text(item.get("module_class"), "module_class") != "WQLinear_GEMM":
            raise OperatorNCUError("module class/backend drift")
        if _text(item.get("backend"), "backend") != "AWQ":
            raise OperatorNCUError("module class/backend drift")
        if item.get("qweight_contiguous") is not True:
            raise OperatorNCUError("qweight region is not contiguous")
        pointer = _integer(item.get("qweight_pointer"), "qweight_pointer", 1)
        size = _integer(item.get("qweight_bytes"), "qweight_bytes", 1)
        normalized[key] = {"layer_index": key[0], "role": key[1],
                           "module_class": "WQLinear_GEMM", "backend": "AWQ",
                           "qweight_pointer": pointer, "qweight_bytes": size,
                           "qweight_contiguous": True}
        intervals.append((pointer, pointer + size, key))
    expected = {(layer, role) for layer in range(28) for role in ROLES}
    if set(normalized) != expected:
        raise OperatorNCUError("module authority missing layer/role identity")
    intervals.sort()
    if any(left[1] > right[0] for left, right in zip(intervals, intervals[1:])):
        raise OperatorNCUError("qweight exact intervals overlap")
    if not isinstance(order, Mapping) or set(order) != set(PHASES):
        raise OperatorNCUError("natural_call_order requires exact PREFILL/D0-D3 phases")
    normalized_order = {}
    for phase in PHASES:
        rows = order[phase]
        if not isinstance(rows, list) or len(rows) != 84:
            raise OperatorNCUError(f"natural_call_order.{phase} requires exact 84 calls")
        phase_order = []
        for index, item in enumerate(rows):
            if not isinstance(item, Mapping):
                raise OperatorNCUError("natural_call_order row must be an object")
            key = _module_key(item, f"natural_call_order.{phase}[{index}]")
            if _integer(item.get("call_index"), "call_index") != index:
                raise OperatorNCUError("natural call index/order mismatch")
            phase_order.append(key)
        if len(set(phase_order)) != 84 or set(phase_order) != expected:
            raise OperatorNCUError("natural call order missing/duplicates 84-module authority")
        normalized_order[phase] = phase_order
    return normalized, normalized_order


def _condition_contract(condition: str) -> tuple[str, tuple[str, ...], float]:
    mode = "CONTROL" if condition.startswith("CONTROL_") else "FAIR"
    if condition == "FULLHINT_GUD84":
        mode = "FAIR"
    if condition in ("CONTROL_FULL_GUD84", "FULLHINT_GUD84"):
        return mode, ROLES, 1.0
    suffix = condition.split("_", 1)[1]
    roles = {
        "GATE28": ("gate_proj",), "UP28": ("up_proj",),
        "DOWN28": ("down_proj",), "GUD84": ROLES,
    }.get(suffix)
    if roles is None:
        raise OperatorNCUError("unknown operator-family condition")
    return mode, roles, 1.0 / (28 * len(roles))


def _reset(raw: Any, label: str, event_index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS" or raw.get("performed") is not True:
        raise OperatorNCUError(f"missing/failed {label}")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise OperatorNCUError(f"{label} is not a persistence reset")
    if _integer(raw.get("event_index"), f"{label}.event_index") != event_index:
        raise OperatorNCUError(f"{label} event order mismatch")
    return {"status": "PASS", "performed": True, "operation": operation,
            "event_index": event_index}


def _policy(path: Path, condition: str,
            modules: Mapping[tuple[int, str], Mapping[str, Any]],
            natural_order: Mapping[str, Sequence[tuple[int, str]]]) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise OperatorNCUError("invalid policy history JSON") from exc
    if isinstance(raw, Mapping) and "policy_receipt" in raw:
        raw = raw["policy_receipt"]
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS":
        raise OperatorNCUError("policy history must be one PASS object")
    if _text(raw.get("condition"), "policy.condition").upper() != condition:
        raise OperatorNCUError("policy condition mismatch")
    mode, roles, ratio = _condition_contract(condition)
    selected = {(layer, role) for layer in range(28) for role in roles}
    selected_json = [{"layer_index": layer, "role": role} for layer, role in sorted(selected)]
    raw_selected = raw.get("selected_modules")
    if (not isinstance(raw_selected, list) or len(raw_selected) != len(selected) or
            {(_integer(row.get("layer_index"), "selected.layer_index"),
              _text(row.get("role"), "selected.role"))
             for row in raw_selected if isinstance(row, Mapping)} != selected):
        raise OperatorNCUError("policy selected-module set/order mismatch")
    if _integer(raw.get("requested_setaside_bytes"), "requested_setaside_bytes") != REQUESTED_SETASIDE_BYTES:
        raise OperatorNCUError("requested set-aside drift")
    if _integer(raw.get("actual_setaside_bytes"), "actual_setaside_bytes") != ACTUAL_SETASIDE_BYTES:
        raise OperatorNCUError("actual set-aside drift")
    stream = _text(raw.get("stream_identity"), "stream_identity")
    before = _reset(raw.get("reset_before"), "reset_before", 0)
    updates = raw.get("updates")
    expected = [(phase, natural_index, key)
                for phase in PHASES
                for natural_index, key in enumerate(natural_order[phase])
                if key in selected]
    if not isinstance(updates, list) or len(updates) != len(expected):
        raise OperatorNCUError("missing/duplicate complete natural policy history")
    normalized = []
    for index, (event, (phase, call_index, key)) in enumerate(zip(updates, expected), 1):
        if not isinstance(event, Mapping):
            raise OperatorNCUError("invalid policy update")
        observed_key = _module_key(event, f"updates[{index - 1}]")
        observed = (_integer(event.get("sequence_index"), "sequence_index"),
                    _text(event.get("phase"), "phase").upper(),
                    _integer(event.get("natural_call_index"), "natural_call_index"),
                    observed_key)
        if observed != (index, phase, call_index, key):
            raise OperatorNCUError("policy update attached to wrong natural module call")
        if event.get("attached_immediately_before") is not True:
            raise OperatorNCUError("policy update is not immediately before natural call")
        authority = modules[key]
        if (_integer(event.get("base_pointer"), "base_pointer", 1) != authority["qweight_pointer"] or
                _integer(event.get("num_bytes"), "num_bytes", 1) != authority["qweight_bytes"]):
            raise OperatorNCUError("policy update is not exact qweight window")
        if _text(event.get("stream_identity"), "update.stream_identity") != stream:
            raise OperatorNCUError("policy stream identity mismatch")
        if event.get("reset_performed") is not False:
            raise OperatorNCUError("forbidden in-run reset")
        if not math.isclose(_finite(event.get("hit_ratio"), "hit_ratio"), ratio,
                            rel_tol=0.0, abs_tol=1e-12):
            raise OperatorNCUError("policy hitRatio mismatch")
        hit = _text(event.get("hit_prop"), "hit_prop").upper()
        miss = _text(event.get("miss_prop"), "miss_prop").upper()
        persisting = event.get("target_persisting")
        expected_policy = (("NORMAL", "NORMAL", False) if mode == "CONTROL"
                           else ("PERSISTING", "STREAMING", True))
        if (hit, miss, persisting) != expected_policy:
            raise OperatorNCUError("CONTROL/FAIR policy semantics mismatch")
        normalized.append({"sequence_index": index, "phase": phase,
                           "natural_call_index": call_index,
                           "layer_index": key[0], "role": key[1],
                           "base_pointer": authority["qweight_pointer"],
                           "num_bytes": authority["qweight_bytes"],
                           "hit_ratio": ratio, "hit_prop": hit, "miss_prop": miss,
                           "target_persisting": persisting})
    after = _reset(raw.get("reset_after"), "reset_after", len(expected) + 1)
    if raw.get("other_reset_events", []) != []:
        raise OperatorNCUError("reset allowed only before/after profile")
    return {"status": "PASS", "condition": condition,
            "selected_modules": selected_json, "selected_module_count": len(selected),
            "requested_setaside_bytes": REQUESTED_SETASIDE_BYTES,
            "actual_setaside_bytes": ACTUAL_SETASIDE_BYTES,
            "stream_identity": stream, "reset_before": before,
            "updates": normalized, "reset_after": after,
            "sha256": _file_sha(path)}


def _profile_spec(raw: Any, root: Path, allowed: frozenset[tuple[str, str]]) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise OperatorNCUError("profile specification must be an object")
    condition = _text(raw.get("condition"), "condition").upper()
    role = _text(raw.get("role"), "role")
    if (condition, role) not in allowed:
        raise OperatorNCUError("profile is outside frozen NCU matrix")
    layer = _integer(raw.get("layer_index"), "layer_index")
    decode = _integer(raw.get("decode_index"), "decode_index")
    if layer != 0 or decode != 3:
        raise OperatorNCUError("wrong semantic occurrence; NCU requires exact L0 D3")
    kernels = raw.get("expected_kernel_names")
    if (not isinstance(kernels, list) or not kernels or
            any(not isinstance(x, str) or not x.strip() for x in kernels) or
            len(kernels) != len(set(kernels))):
        raise OperatorNCUError("invalid/duplicate expected kernel inventory")
    return {"condition": condition, "layer_index": layer, "role": role,
            "decode_index": decode,
            "generated_token_id": _integer(raw.get("generated_token_id"), "generated_token_id"),
            "accepted_prefix_sha256": _sha(raw.get("accepted_prefix_sha256"), "accepted_prefix_sha256"),
            "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
            "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
            "range_name": _text(raw.get("range_name"), "range_name"),
            "expected_kernel_names": kernels,
            "base_path": _path(root, raw.get("base_path"), "base_path"),
            "session_path": _path(root, raw.get("session_path"), "session_path"),
            "profile_path": _path(root, raw.get("profile_path"), "profile_path"),
            "policy_history_path": _path(root, raw.get("policy_history_path"),
                                         "policy_history_path")}


def _session(path: Path, spec: Mapping[str, Any], metrics: set[str]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if set(_options(text, "--replay-mode")) != {"application"}:
        raise OperatorNCUError("SESSION replay mode mismatch")
    if set(_options(text, "--cache-control")) != {"none"}:
        raise OperatorNCUError("SESSION cache-control mismatch")
    if {value.rstrip("/") for value in _options(text, "--nvtx-include")} != {spec["range_name"]}:
        raise OperatorNCUError("SESSION semantic range mismatch")
    metric_args = set(_options(text, "--metrics"))
    if len(metric_args) != 1 or set(next(iter(metric_args)).split(",")) != metrics:
        raise OperatorNCUError("SESSION metric set mismatch")
    return {"sha256": _file_sha(path), "replay_mode": "application",
            "cache_control": "none", "range_name": spec["range_name"]}


def _profile_receipts(path: Path, spec: Mapping[str, Any], policy_sha: str) -> list[dict[str, Any]]:
    receipts = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(raw, Mapping) and raw.get("status") == "PASS":
            observed = {
                "condition": raw.get("condition"), "layer_index": raw.get("layer_index"),
                "role": raw.get("role"), "decode_index": raw.get("decode_index"),
                "generated_token_id": raw.get("generated_token_id"),
                "accepted_prefix_sha256": raw.get("accepted_prefix_sha256"),
                "input_sha256": raw.get("input_sha256"),
                "output_sha256": raw.get("output_sha256"),
                "range_name": raw.get("range", raw.get("range_name")),
                "policy_history_sha256": raw.get("policy_history_sha256",
                                                   raw.get("policy_receipt_sha256")),
            }
            expected = {key: spec[key] for key in observed if key != "policy_history_sha256"}
            expected["policy_history_sha256"] = policy_sha
            if observed != expected:
                raise OperatorNCUError("PROFILE PASS semantic/token/policy identity mismatch")
            receipts.append(observed)
    if not receipts:
        raise OperatorNCUError("PROFILE contains no PASS receipt")
    if any(receipt != receipts[0] for receipt in receipts[1:]):
        raise OperatorNCUError("PROFILE PASS receipt identity drift")
    return receipts


def _base(path: Path, spec: Mapping[str, Any], metrics: list[dict[str, Any]],
          pass_count: int) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise OperatorNCUError("BASE lacks header/unit/data rows")
    header, units, *data = table
    if (len(header) != len(set(header)) or len(units) != len(header) or
            any(len(row) != len(header) for row in data)):
        raise OperatorNCUError("BASE ambiguous/ragged header")
    range_columns = [name for name in header if "Push/Pop_Range" in name]
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes",
                *[row["metric_name"] for row in metrics]}
    if len(range_columns) != 1 or required - set(header):
        raise OperatorNCUError("BASE missing/ambiguous required columns")
    index = {name: header.index(name) for name in (*required, range_columns[0])}
    for metric in metrics:
        if units[index[metric["metric_name"]]].strip() != metric["unit"]:
            raise OperatorNCUError(f"BASE unit mismatch for {metric['metric_name']}")
    selected = [row for row in data if _exact_range(row[index[range_columns[0]]], spec["range_name"])]
    names = [row[index["Kernel Name"]].strip() for row in selected]
    if not selected or sorted(names) != sorted(spec["expected_kernel_names"]):
        raise OperatorNCUError("BASE exact kernel inventory mismatch")
    ids = [(row[index["Process ID"]].strip(), row[index["ID"]].strip()) for row in selected]
    if (any(not a or not b for a, b in ids) or len(ids) != len(set(ids)) or
            len({a for a, _ in ids}) != 1):
        raise OperatorNCUError("BASE duplicate row/kernel/process identity ambiguity")
    sums = {row["category"]: Decimal(0) for row in metrics
            if row["aggregation"] == "SEMANTIC_SUM"}
    kernel_metrics = []
    for row in selected:
        if _decimal(row[index["profiler__replayer_passes"]], "replayer passes") != Decimal(pass_count):
            raise OperatorNCUError("BASE replayer passes/PASS receipt count mismatch")
        values = []
        for metric in metrics:
            value = _decimal(row[index[metric["metric_name"]]], metric["metric_name"])
            values.append({"category": metric["category"], "metric_name": metric["metric_name"],
                           "unit": metric["unit"], "aggregation": metric["aggregation"],
                           "value": _number(value)})
            if metric["aggregation"] == "SEMANTIC_SUM":
                sums[metric["category"]] += value
        kernel_metrics.append({"kernel_id": row[index["ID"]].strip(),
                               "kernel_name": row[index["Kernel Name"]].strip(),
                               "metrics": values})
    return {"sha256": _file_sha(path), "process_id": ids[0][0],
            "profiler_replayer_passes": pass_count, "kernel_inventory": names,
            "kernel_metrics": kernel_metrics,
            "additive_semantic_sums": {key: _number(value) for key, value in sums.items()}}


def _fullhint_contract(raw: Any) -> tuple[bool, float, list[Any]]:
    if not isinstance(raw, Mapping):
        raise OperatorNCUError("fullhint_ncu must be an object")
    fair = _finite(raw.get("fair_gud84_whole_decode_benefit"),
                   "fair_gud84_whole_decode_benefit")
    full = _finite(raw.get("fullhint_gud84_whole_decode_benefit"),
                   "fullhint_gud84_whole_decode_benefit")
    delta_pp = abs(full - fair) * 100.0
    triggered = delta_pp >= 0.5
    if raw.get("triggered") is not triggered:
        raise OperatorNCUError("FULLHINT NCU trigger mismatch")
    profiles = raw.get("profiles")
    if not isinstance(profiles, list):
        raise OperatorNCUError("fullhint profiles must be a list")
    if (triggered and len(profiles) != 6) or (not triggered and profiles):
        raise OperatorNCUError("FULLHINT false/true evidence matrix mismatch")
    return triggered, delta_pp, profiles


def _consume_matrix(raw_profiles: Any, expected_matrix: frozenset[tuple[str, str]],
                    root: Path, metrics: list[dict[str, Any]],
                    modules: Mapping[tuple[int, str], Mapping[str, Any]],
                    natural_order: Mapping[str, Sequence[tuple[int, str]]]) -> list[dict[str, Any]]:
    if not isinstance(raw_profiles, list) or len(raw_profiles) != len(expected_matrix):
        raise OperatorNCUError(f"NCU requires exact {len(expected_matrix)}-profile matrix")
    specs, identities = [], set()
    for raw in raw_profiles:
        spec = _profile_spec(raw, root, expected_matrix)
        key = (spec["condition"], spec["role"])
        if key in identities:
            raise OperatorNCUError("duplicate operator-family NCU matrix point")
        identities.add(key)
        specs.append(spec)
    if identities != expected_matrix:
        raise OperatorNCUError("operator-family NCU frozen matrix mismatch")
    output = []
    metric_names = {row["metric_name"] for row in metrics}
    for spec in specs:
        policy = _policy(spec["policy_history_path"], spec["condition"],
                         modules, natural_order)
        receipts = _profile_receipts(spec["profile_path"], spec, policy["sha256"])
        output.append({"condition": spec["condition"], "layer_index": 0,
                       "role": spec["role"], "decode_index": 3,
                       "range_name": spec["range_name"],
                       "input_sha256": spec["input_sha256"],
                       "output_sha256": spec["output_sha256"],
                       "session": _session(spec["session_path"], spec, metric_names),
                       "profile": {"sha256": _file_sha(spec["profile_path"]),
                                   "pass_receipt_count": len(receipts),
                                   "identical_identity": True},
                       "base": _base(spec["base_path"], spec, metrics, len(receipts)),
                       "policy_history": policy})
    return output


def consume(document: Mapping[str, Any], root: Path | str = Path(".")) -> dict[str, Any]:
    """Validate the exact 12 primary profiles and conditional FULLHINT six."""
    if not isinstance(document, Mapping) or document.get("schema_version") != 1:
        raise OperatorNCUError("schema_version must equal 1")
    root = Path(root)
    query = _query(document.get("runtime_metric_query"), root)
    metrics, unavailable = _catalog(document.get("metric_availability"))
    modules, natural_order = _module_authority(document.get("module_authority"))
    primary = _consume_matrix(document.get("profiles"), PRIMARY_MATRIX, root,
                              metrics, modules, natural_order)
    triggered, delta_pp, fullhint_raw = _fullhint_contract(document.get("fullhint_ncu"))
    fullhint = (_consume_matrix(fullhint_raw, FULLHINT_MATRIX, root, metrics,
                                modules, natural_order) if triggered else [])
    return {"schema_version": 1, "status": "PASS",
            "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_COMPLETE_NATURAL_POLICY_HISTORY_ONLY",
            "matrix_contract": "FROZEN_PRIMARY_12_L0_D3_PROFILES",
            "profile_count": 12, "runtime_metric_query": query,
            "metric_availability": [*metrics, *unavailable],
            "natural_call_order": {
                phase: [{"call_index": index, "layer_index": key[0], "role": key[1]}
                        for index, key in enumerate(natural_order[phase])]
                for phase in PHASES},
            "profiles": primary, "non_additive_policy": "PER_KERNEL_ONLY",
            "fullhint_ncu": {"triggered": triggered,
                             "absolute_whole_decode_benefit_delta_percentage_points": delta_pp,
                             "threshold_percentage_points": 0.5,
                             "profile_count": len(fullhint), "profiles": fullhint}}


__all__ = ["ACTUAL_SETASIDE_BYTES", "FULLHINT_MATRIX", "OperatorNCUError",
           "PHASES", "PRIMARY_MATRIX", "REQUESTED_SETASIDE_BYTES", "ROLES",
           "consume"]
