#!/usr/bin/env python3
"""Fail-closed raw representative-NCU consumer for E1 cost/benefit closure."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


class RepresentativeNCUError(ValueError):
    """The raw NCU evidence is absent, ambiguous, or inconsistent."""


BUDGET_REQUESTS = {"B16": 16 * 1024 * 1024, "BFULL": 33_947_648}
MODES = ("CONTROL", "FAIR")
TARGETS = ("up_proj", "self_attn")
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
PROFILE_MATRIX = frozenset((b, m, t) for b in BUDGET_REQUESTS for m in MODES for t in TARGETS)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
BASE_METRICS = {
    "L1_TEX_BYTES": ("l1tex__t_bytes.sum", {"byte", "bytes"}),
    "L2_BYTES": ("lts__t_bytes.sum", {"byte", "bytes"}),
    "DRAM_BYTES": ("dram__bytes.sum", {"byte", "bytes"}),
}
ADDITIVE_UNITS = {
    **{key: units for key, (_name, units) in BASE_METRICS.items()},
    "KERNEL_DURATION": {"ns", "us", "cycle", "cycles"},
    "KERNEL_ELAPSED_CYCLES": {"cycle", "cycles"},
    "L2_READ_HIT_SECTORS": {"sector", "sectors"},
    "L2_READ_MISS_SECTORS": {"sector", "sectors"},
    "DRAM_READ_BYTES": {"byte", "bytes"},
}
PER_KERNEL_UNITS = {
    "LONG_SCOREBOARD_STALL": {"%", "percent"},
    "LSU_UTILIZATION": {"%", "percent"},
    "ACHIEVED_ACTIVE_WARPS": {"warp", "warps"},
}
KNOWN_CATEGORIES = frozenset((*ADDITIVE_UNITS, *PER_KERNEL_UNITS))


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RepresentativeNCUError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise RepresentativeNCUError(f"invalid {label}")
    token = str(value).strip()
    try:
        result = int(token)
    except (TypeError, ValueError) as exc:
        raise RepresentativeNCUError(f"invalid {label}: {value!r}") from exc
    if str(result) != token or result < minimum:
        raise RepresentativeNCUError(f"invalid {label}: {value!r}")
    return result


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RepresentativeNCUError(f"invalid {label}") from exc
    if not math.isfinite(result):
        raise RepresentativeNCUError(f"nonfinite {label}")
    return result


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise RepresentativeNCUError(f"invalid numeric {label}") from exc
    if not result.is_finite():
        raise RepresentativeNCUError(f"nonfinite numeric {label}")
    return result


def _number(value: Decimal) -> int | float:
    return int(value) if value == value.to_integral_value() else float(value)


def _sha(value: Any, label: str) -> str:
    result = str(value).strip().lower()
    if not HEX64.fullmatch(result):
        raise RepresentativeNCUError(f"invalid {label}")
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
        raise RepresentativeNCUError(f"missing or empty {label}: {result}")
    return result


def _options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text, re.MULTILINE)


def _exact_range(cell: str, target: str) -> bool:
    return len(re.findall(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)", cell.strip())) == 1


def _query(raw: Any, root: Path) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS":
        raise RepresentativeNCUError("runtime metric query must be one PASS receipt")
    command = _text(raw.get("command"), "runtime_metric_query.command")
    version = _text(raw.get("ncu_version"), "runtime_metric_query.ncu_version")
    if "query" not in command.lower() or "metric" not in command.lower():
        raise RepresentativeNCUError("runtime query command is ambiguous")
    path = _path(root, raw.get("path"), "runtime_metric_query.path")
    claimed = _sha(raw.get("sha256"), "runtime_metric_query.sha256")
    if claimed != _file_sha(path):
        raise RepresentativeNCUError("runtime metric query SHA mismatch")
    if version not in path.read_text(encoding="utf-8", errors="replace"):
        raise RepresentativeNCUError("runtime metric query/version identity mismatch")
    return {"status": "PASS", "command": command, "ncu_version": version,
            "path": str(path), "sha256": claimed}


def _catalog(raw: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(raw, list) or not raw:
        raise RepresentativeNCUError("metric_availability must be nonempty")
    available, unavailable, categories, names = [], [], set(), set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise RepresentativeNCUError("metric catalog row must be an object")
        category = _text(item.get("category"), "metric.category")
        if category not in KNOWN_CATEGORIES or category in categories:
            raise RepresentativeNCUError("unknown/duplicate metric category")
        categories.add(category)
        if not isinstance(item.get("available"), bool):
            raise RepresentativeNCUError("metric availability must be boolean")
        aggregation = "SEMANTIC_SUM" if category in ADDITIVE_UNITS else "PER_KERNEL_ONLY"
        if item.get("aggregation", aggregation) != aggregation:
            raise RepresentativeNCUError(f"aggregation mismatch for {category}")
        if not item["available"]:
            if item.get("metric_name") not in (None, "") or item.get("unit") not in (None, ""):
                raise RepresentativeNCUError("unavailable metric claims name/unit")
            unavailable.append({"category": category, "available": False, "aggregation": aggregation,
                                "reason": _text(item.get("reason"), f"{category}.reason")})
            continue
        name = _text(item.get("metric_name"), f"{category}.metric_name")
        unit = _text(item.get("unit"), f"{category}.unit")
        if name in names or unit not in ADDITIVE_UNITS.get(category, PER_KERNEL_UNITS.get(category, set())):
            raise RepresentativeNCUError(f"duplicate metric name or unit mismatch for {category}")
        names.add(name)
        available.append({"category": category, "available": True, "metric_name": name,
                          "unit": unit, "aggregation": aggregation})
    by_category = {row["category"]: row for row in available}
    for category, (name, _units) in BASE_METRICS.items():
        if category not in by_category or by_category[category]["metric_name"] != name:
            raise RepresentativeNCUError(f"missing required base metric {name}")
    return available, unavailable


def _budgets(raw: Any) -> dict[str, dict[str, int]]:
    if not isinstance(raw, list) or len(raw) != 2:
        raise RepresentativeNCUError("budget_authority requires exact B16/BFULL rows")
    result = {}
    for row in raw:
        if not isinstance(row, Mapping):
            raise RepresentativeNCUError("budget authority row must be an object")
        budget = _text(row.get("budget"), "budget_authority.budget").upper()
        if budget not in BUDGET_REQUESTS or budget in result:
            raise RepresentativeNCUError("unknown/duplicate budget authority")
        requested = _integer(row.get("requested_setaside_bytes"), "requested_setaside_bytes", 1)
        actual = _integer(row.get("actual_setaside_bytes"), "actual_setaside_bytes", 1)
        maximum = _integer(row.get("runtime_max_setaside_bytes"), "runtime_max_setaside_bytes", 1)
        if requested != BUDGET_REQUESTS[budget]:
            raise RepresentativeNCUError("requested budget drift")
        if actual > maximum:
            raise RepresentativeNCUError("runtime actual set-aside exceeds runtime maximum")
        result[budget] = {"requested_setaside_bytes": requested, "actual_setaside_bytes": actual,
                          "runtime_max_setaside_bytes": maximum}
    return result


def _reset(raw: Any, label: str, event_index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS" or raw.get("performed") is not True:
        raise RepresentativeNCUError(f"missing/failed {label}")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise RepresentativeNCUError(f"{label} is not a persistence reset")
    if _integer(raw.get("event_index"), f"{label}.event_index") != event_index:
        raise RepresentativeNCUError(f"{label} event order mismatch")
    return {"status": "PASS", "performed": True, "operation": operation, "event_index": event_index}


def _policy(path: Path, spec: Mapping[str, Any], budget: Mapping[str, int], qweight_bytes: int) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RepresentativeNCUError("invalid policy history JSON") from exc
    if isinstance(raw, Mapping) and "policy_receipt" in raw:
        raw = raw["policy_receipt"]
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS":
        raise RepresentativeNCUError("policy history must be one PASS object")
    for key in ("condition", "budget", "process_identity"):
        if _text(raw.get(key), f"policy.{key}") != spec[key]:
            raise RepresentativeNCUError(f"policy {key} mismatch")
    for key in ("requested_setaside_bytes", "actual_setaside_bytes", "runtime_max_setaside_bytes"):
        if _integer(raw.get(key), f"policy.{key}", 1) != budget[key]:
            raise RepresentativeNCUError(f"policy runtime {key} query-back drift")
    selected = raw.get("selected_modules")
    if not isinstance(selected, list) or len(selected) != 28:
        raise RepresentativeNCUError("policy requires exact 28 process-local up_proj modules")
    modules, intervals = {}, []
    for index, item in enumerate(selected):
        if not isinstance(item, Mapping):
            raise RepresentativeNCUError("selected module row must be an object")
        layer = _integer(item.get("layer_index"), f"selected[{index}].layer_index")
        if layer not in range(28) or _text(item.get("role"), "selected.role") != "up_proj" or layer in modules:
            raise RepresentativeNCUError("selected family/layer identity mismatch")
        if (_text(item.get("module_class"), "module_class") != "WQLinear_GEMM" or
                _text(item.get("backend"), "backend") != "AWQ" or
                item.get("qweight_contiguous") is not True or
                _text(item.get("process_identity"), "selected.process_identity") != spec["process_identity"]):
            raise RepresentativeNCUError("process-local qweight authority mismatch")
        pointer = _integer(item.get("qweight_pointer"), "qweight_pointer", 1)
        size = _integer(item.get("qweight_bytes"), "qweight_bytes", 1)
        if size != qweight_bytes:
            raise RepresentativeNCUError("exact up_proj qweight byte authority mismatch")
        modules[layer] = {"qweight_pointer": pointer, "qweight_bytes": size}
        intervals.append((pointer, pointer + size))
    if set(modules) != set(range(28)):
        raise RepresentativeNCUError("missing process-local up_proj layer")
    intervals.sort()
    if any(left[1] > right[0] for left, right in zip(intervals, intervals[1:])):
        raise RepresentativeNCUError("process-local qweight windows overlap")
    expected_ratio = min(1.0, budget["requested_setaside_bytes"] / (28 * qweight_bytes))
    if not math.isclose(_finite(raw.get("hit_ratio"), "policy.hit_ratio"), expected_ratio, rel_tol=0, abs_tol=1e-12):
        raise RepresentativeNCUError("policy hitRatio mismatch")
    stream = _text(raw.get("stream_identity"), "policy.stream_identity")
    before = _reset(raw.get("reset_before"), "reset_before", 0)
    updates = raw.get("updates")
    if not isinstance(updates, list) or len(updates) != 140:
        raise RepresentativeNCUError("policy requires complete 140-update history")
    seen = {phase: set() for phase in PHASES}
    natural_indices = {phase: set() for phase in PHASES}
    expected_policy = (("NORMAL", "NORMAL", False) if spec["mode"] == "CONTROL"
                       else ("PERSISTING", "STREAMING", True))
    normalized = []
    for sequence, event in enumerate(updates, 1):
        if not isinstance(event, Mapping) or _integer(event.get("sequence_index"), "update.sequence_index") != sequence:
            raise RepresentativeNCUError("policy update sequence mismatch")
        phase = _text(event.get("phase"), "update.phase").upper()
        layer = _integer(event.get("layer_index"), "update.layer_index")
        role = _text(event.get("role"), "update.role")
        call_index = _integer(event.get("natural_call_index"), "update.natural_call_index")
        if phase not in seen or layer not in range(28) or role != "up_proj":
            raise RepresentativeNCUError("policy update family/phase mismatch")
        if layer in seen[phase] or call_index in natural_indices[phase]:
            raise RepresentativeNCUError("duplicate update attachment")
        seen[phase].add(layer); natural_indices[phase].add(call_index)
        authority = modules[layer]
        if event.get("attached_immediately_before") is not True:
            raise RepresentativeNCUError("policy update is not attached immediately before natural call")
        if (_integer(event.get("base_pointer"), "update.base_pointer", 1) != authority["qweight_pointer"] or
                _integer(event.get("num_bytes"), "update.num_bytes", 1) != qweight_bytes):
            raise RepresentativeNCUError("policy update is not exact full qweight window")
        if (_text(event.get("process_identity"), "update.process_identity") != spec["process_identity"] or
                _text(event.get("stream_identity"), "update.stream_identity") != stream):
            raise RepresentativeNCUError("policy update process/stream identity mismatch")
        if event.get("reset_performed") is not False:
            raise RepresentativeNCUError("forbidden in-run reset")
        if not math.isclose(_finite(event.get("hit_ratio"), "update.hit_ratio"), expected_ratio,
                            rel_tol=0, abs_tol=1e-12):
            raise RepresentativeNCUError("policy update hitRatio mismatch")
        observed_policy = (_text(event.get("hit_prop"), "hit_prop").upper(),
                           _text(event.get("miss_prop"), "miss_prop").upper(), event.get("target_persisting"))
        if observed_policy != expected_policy:
            raise RepresentativeNCUError("CONTROL/FAIR policy semantics mismatch")
        normalized.append({"sequence_index": sequence, "phase": phase, "natural_call_index": call_index,
                           "layer_index": layer, "role": role, "base_pointer": authority["qweight_pointer"],
                           "num_bytes": qweight_bytes, "hit_ratio": expected_ratio,
                           "hit_prop": observed_policy[0], "miss_prop": observed_policy[1],
                           "target_persisting": observed_policy[2]})
    if any(layers != set(range(28)) for layers in seen.values()):
        raise RepresentativeNCUError("policy history missing one or more 28-up phase updates")
    after = _reset(raw.get("reset_after"), "reset_after", 141)
    if raw.get("other_reset_events", []) != []:
        raise RepresentativeNCUError("reset allowed only before/after profile")
    return {"status": "PASS", "condition": spec["condition"], "budget": spec["budget"],
            "mode": spec["mode"], "pointer_scope": "PROCESS_LOCAL", "process_identity": spec["process_identity"],
            "selected_module_count": 28, **budget, "hit_ratio": expected_ratio,
            "stream_identity": stream, "reset_before": before, "updates": normalized,
            "reset_after": after, "sha256": _file_sha(path)}


def _profile_spec(raw: Any, root: Path) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise RepresentativeNCUError("profile specification must be an object")
    budget = _text(raw.get("budget"), "profile.budget").upper()
    mode = _text(raw.get("mode"), "profile.mode").upper()
    target = _text(raw.get("target_semantic"), "profile.target_semantic")
    if (budget, mode, target) not in PROFILE_MATRIX:
        raise RepresentativeNCUError("profile outside frozen 8-profile matrix")
    condition = f"{mode}_UP28_{budget}"
    if _text(raw.get("condition"), "profile.condition").upper() != condition:
        raise RepresentativeNCUError("profile condition/budget mismatch")
    if _integer(raw.get("layer_index"), "layer_index") != 0 or _integer(raw.get("decode_index"), "decode_index") != 3:
        raise RepresentativeNCUError("wrong semantic occurrence; requires exact L0 D3")
    kernels = raw.get("expected_kernel_names")
    if not isinstance(kernels, list) or not kernels or any(not isinstance(x, str) or not x.strip() for x in kernels):
        raise RepresentativeNCUError("invalid expected kernel inventory")
    return {"budget": budget, "mode": mode, "condition": condition, "target_semantic": target,
            "layer_index": 0, "decode_index": 3,
            "generated_token_id": _integer(raw.get("generated_token_id"), "generated_token_id"),
            "accepted_prefix_sha256": _sha(raw.get("accepted_prefix_sha256"), "accepted_prefix_sha256"),
            "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
            "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
            "process_identity": _text(raw.get("process_identity"), "process_identity"),
            "ncu_process_id": str(_integer(raw.get("ncu_process_id"), "ncu_process_id", 1)),
            "range_name": _text(raw.get("range_name"), "range_name"),
            "expected_kernel_names": [x.strip() for x in kernels],
            "base_path": _path(root, raw.get("base_path"), "base_path"),
            "session_path": _path(root, raw.get("session_path"), "session_path"),
            "profile_path": _path(root, raw.get("profile_path"), "profile_path"),
            "policy_history_path": _path(root, raw.get("policy_history_path"), "policy_history_path")}


def _session(path: Path, spec: Mapping[str, Any], metrics: set[str]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if set(_options(text, "--replay-mode")) != {"application"}:
        raise RepresentativeNCUError("SESSION replay mode mismatch")
    if set(_options(text, "--cache-control")) != {"none"}:
        raise RepresentativeNCUError("SESSION cache-control mismatch")
    if {value.rstrip("/") for value in _options(text, "--nvtx-include")} != {spec["range_name"]}:
        raise RepresentativeNCUError("SESSION semantic range mismatch")
    metric_args = set(_options(text, "--metrics"))
    if len(metric_args) != 1 or set(next(iter(metric_args)).split(",")) != metrics:
        raise RepresentativeNCUError("SESSION metric set mismatch")
    return {"sha256": _file_sha(path), "replay_mode": "application", "cache_control": "none",
            "range_name": spec["range_name"]}


def _profile_receipts(path: Path, spec: Mapping[str, Any], policy_sha: str) -> list[dict[str, Any]]:
    keys = ("budget", "mode", "condition", "target_semantic", "layer_index", "decode_index",
            "generated_token_id", "accepted_prefix_sha256", "input_sha256", "output_sha256",
            "process_identity", "ncu_process_id", "range_name")
    receipts = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            raw = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(raw, Mapping) and raw.get("status") == "PASS":
            observed = {key: raw.get(key) for key in keys}; observed["ncu_process_id"] = str(observed["ncu_process_id"])
            if observed != {key: spec[key] for key in keys} or raw.get("policy_history_sha256") != policy_sha:
                raise RepresentativeNCUError("PROFILE PASS semantic/token/process/policy identity mismatch")
            receipts.append({**observed, "policy_history_sha256": policy_sha})
    if not receipts:
        raise RepresentativeNCUError("PROFILE contains no PASS receipt")
    if any(row != receipts[0] for row in receipts[1:]):
        raise RepresentativeNCUError("PROFILE PASS receipt identity drift across multipass replay")
    return receipts


def _base(path: Path, spec: Mapping[str, Any], metrics: list[dict[str, Any]], pass_count: int) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise RepresentativeNCUError("BASE lacks header/unit/data rows")
    header, units, *data = table
    if len(header) != len(set(header)) or len(units) != len(header) or any(len(row) != len(header) for row in data):
        raise RepresentativeNCUError("BASE ambiguous/ragged header")
    ranges = [name for name in header if "Push/Pop_Range" in name]
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes",
                *[metric["metric_name"] for metric in metrics]}
    if len(ranges) != 1 or required - set(header):
        raise RepresentativeNCUError("BASE missing/ambiguous required columns")
    index = {name: header.index(name) for name in (*required, ranges[0])}
    for metric in metrics:
        if units[index[metric["metric_name"]]].strip() != metric["unit"]:
            raise RepresentativeNCUError(f"BASE unit mismatch for {metric['metric_name']}")
    selected = [row for row in data if _exact_range(row[index[ranges[0]]], spec["range_name"])]
    names = [row[index["Kernel Name"]].strip() for row in selected]
    if not selected or names != spec["expected_kernel_names"]:
        raise RepresentativeNCUError("BASE exact ordered kernel inventory mismatch")
    ids = [(row[index["Process ID"]].strip(), row[index["ID"]].strip()) for row in selected]
    if any(not x or not y for x, y in ids) or len(ids) != len(set(ids)) or {x for x, _y in ids} != {spec["ncu_process_id"]}:
        raise RepresentativeNCUError("BASE kernel/process identity mismatch or duplicate row")
    sums = {metric["category"]: Decimal(0) for metric in metrics if metric["aggregation"] == "SEMANTIC_SUM"}
    per_kernel = []
    for launch_index, row in enumerate(selected):
        if _decimal(row[index["profiler__replayer_passes"]], "replayer passes") != Decimal(pass_count):
            raise RepresentativeNCUError("BASE replayer passes/PASS receipt count mismatch")
        values = []
        for metric in metrics:
            value = _decimal(row[index[metric["metric_name"]]], metric["metric_name"])
            values.append({"category": metric["category"], "metric_name": metric["metric_name"],
                           "unit": metric["unit"], "aggregation": metric["aggregation"], "value": _number(value)})
            if metric["aggregation"] == "SEMANTIC_SUM":
                sums[metric["category"]] += value
        per_kernel.append({"launch_index": launch_index, "kernel_id": ids[launch_index][1],
                           "kernel_name": names[launch_index], "metrics": values})
    return {"sha256": _file_sha(path), "process_id": spec["ncu_process_id"],
            "profiler_replayer_passes": pass_count, "kernel_inventory": names,
            "kernel_name_multiplicity": dict(Counter(names)), "per_kernel_metrics": per_kernel,
            "additive_semantic_sums": {key: _number(value) for key, value in sums.items()}}


def consume(document: Mapping[str, Any], root: Path | str = Path(".")) -> dict[str, Any]:
    """Validate and aggregate the exact eight frozen representative profiles."""
    if not isinstance(document, Mapping) or document.get("schema_version") != 1:
        raise RepresentativeNCUError("schema_version must equal 1")
    root = Path(root)
    query = _query(document.get("runtime_metric_query"), root)
    metrics, unavailable = _catalog(document.get("metric_availability"))
    budgets = _budgets(document.get("budget_authority"))
    qweight_bytes = _integer(document.get("exact_up_proj_qweight_bytes"), "exact_up_proj_qweight_bytes", 1)
    raw_profiles = document.get("profiles")
    if not isinstance(raw_profiles, list) or len(raw_profiles) != 8:
        raise RepresentativeNCUError("NCU requires exact 8-profile matrix")
    specs, identities = [], set()
    for raw in raw_profiles:
        spec = _profile_spec(raw, root)
        identity = (spec["budget"], spec["mode"], spec["target_semantic"])
        if identity in identities:
            raise RepresentativeNCUError("duplicate representative NCU matrix point")
        identities.add(identity); specs.append(spec)
    if identities != PROFILE_MATRIX:
        raise RepresentativeNCUError("representative NCU frozen matrix mismatch")
    metric_names = {metric["metric_name"] for metric in metrics}
    output = []
    for spec in specs:
        policy = _policy(spec["policy_history_path"], spec, budgets[spec["budget"]], qweight_bytes)
        receipts = _profile_receipts(spec["profile_path"], spec, policy["sha256"])
        output.append({"budget": spec["budget"], "mode": spec["mode"], "condition": spec["condition"],
                       "target_semantic": spec["target_semantic"], "layer_index": 0, "decode_index": 3,
                       "range_name": spec["range_name"], "input_sha256": spec["input_sha256"],
                       "output_sha256": spec["output_sha256"], "process_identity": spec["process_identity"],
                       "session": _session(spec["session_path"], spec, metric_names),
                       "profile": {"sha256": _file_sha(spec["profile_path"]),
                                   "pass_receipt_count": len(receipts), "multipass_identity": "IDENTICAL"},
                       "base": _base(spec["base_path"], spec, metrics, len(receipts)),
                       "policy_history": policy})
    return {"schema_version": 1, "status": "PASS",
            "authority": "DIRECT_RAW_QUERY_BUDGET_BASE_SESSION_PROFILE_POLICY_ONLY",
            "matrix_contract": "B16_BFULL_X_CONTROL_FAIR_X_L0_UP_SELF_ATTN_D3",
            "profile_count": 8, "runtime_metric_query": query,
            "metric_availability": [*metrics, *unavailable], "budget_authority": budgets,
            "exact_up_proj_qweight_bytes": qweight_bytes,
            "qweight_pointer_scope": "PROCESS_LOCAL_NO_CROSS_PROFILE_EQUALITY_REQUIRED",
            "profiles": output, "non_additive_policy": "PER_KERNEL_ONLY"}


__all__ = ["BUDGET_REQUESTS", "MODES", "PHASES", "PROFILE_MATRIX",
           "RepresentativeNCUError", "TARGETS", "consume"]
