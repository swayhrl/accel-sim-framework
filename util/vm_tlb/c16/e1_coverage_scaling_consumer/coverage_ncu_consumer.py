#!/usr/bin/env python3
"""Fail-closed raw NCU consumer for C16 E1 coverage scaling.

The consumer accepts only BASE/SESSION/PROFILE evidence plus the complete
ordered CUDA persistence-policy history.  Producer summary tables are not an
input.  Additive categories are summed over the exact semantic occurrence;
non-additive categories remain per-kernel.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


class CoverageNCUError(ValueError):
    """Raw coverage NCU evidence is absent, ambiguous, or inconsistent."""


LAYER_ORDER = (0, 14, 27, 7, 20, 3, 10, 17, 23, 5, 12, 25, 1, 2,
               4, 6, 8, 9, 11, 13, 15, 16, 18, 19, 21, 22, 24, 26)
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
REQUESTED_SETASIDE_BYTES = 33_947_648
ACTUAL_SETASIDE_BYTES = 37_748_736
MATRIX = frozenset(
    [(condition, 0) for count in (1, 8, 28)
     for condition in (f"CONTROL_N{count}", f"FAIR_N{count}")]
    + [(condition, 14) for count in (2, 8, 28)
       for condition in (f"CONTROL_N{count}", f"FAIR_N{count}")]
    + [(condition, 27) for count in (4, 28)
       for condition in (f"CONTROL_N{count}", f"FAIR_N{count}")]
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
    "KERNEL_DURATION": {"ns"},
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
CONDITION_RE = re.compile(r"^(CONTROL|FAIR)_N(1|2|4|8|14|28)$")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CoverageNCUError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise CoverageNCUError(f"invalid {label}")
    token = str(value).strip()
    try:
        result = int(token)
    except (TypeError, ValueError) as exc:
        raise CoverageNCUError(f"invalid {label}: {value!r}") from exc
    if str(result) != token or result < minimum:
        raise CoverageNCUError(f"invalid {label}: {value!r}")
    return result


def _finite(value: Any, label: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise CoverageNCUError(f"invalid {label}") from exc
    if not math.isfinite(result):
        raise CoverageNCUError(f"nonfinite {label}")
    return result


def _sha(value: Any, label: str) -> str:
    result = str(value).strip().lower()
    if not HEX64.fullmatch(result):
        raise CoverageNCUError(f"invalid {label}")
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
        raise CoverageNCUError(f"missing or empty {label}: {result}")
    return result


def _decimal(value: Any, label: str) -> Decimal:
    try:
        result = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise CoverageNCUError(f"invalid metric value {label}") from exc
    if not result.is_finite():
        raise CoverageNCUError(f"nonfinite metric value {label}")
    return result


def _number(value: Decimal) -> int | float:
    return int(value) if value == value.to_integral_value() else float(value)


def _options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text,
                      re.MULTILINE)


def _exact_range(cell: str, target: str) -> bool:
    pattern = re.compile(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)")
    return len(pattern.findall(cell.strip())) == 1


def _query(raw: Any, root: Path) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS":
        raise CoverageNCUError("runtime metric query receipt must be one PASS object")
    command = _text(raw.get("command"), "runtime_metric_query.command")
    if "query" not in command.lower() or "metric" not in command.lower():
        raise CoverageNCUError("runtime query command is ambiguous")
    version = _text(raw.get("ncu_version"), "runtime_metric_query.ncu_version")
    path = _path(root, raw.get("path"), "runtime_metric_query.path")
    claimed = _sha(raw.get("sha256"), "runtime_metric_query.sha256")
    if claimed != _file_sha(path):
        raise CoverageNCUError("runtime metric query SHA mismatch")
    if version not in path.read_text(encoding="utf-8", errors="replace"):
        raise CoverageNCUError("runtime metric query/version identity ambiguity")
    return {"status": "PASS", "command": command, "ncu_version": version,
            "path": str(path), "sha256": claimed}


def _catalog(raw: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(raw, list) or not raw:
        raise CoverageNCUError("metric_availability must be nonempty")
    available, unavailable, categories, names = [], [], set(), set()
    for item in raw:
        if not isinstance(item, Mapping):
            raise CoverageNCUError("metric catalog row must be an object")
        category = _text(item.get("category"), "metric.category")
        if category not in KNOWN_CATEGORIES or category in categories:
            raise CoverageNCUError("unknown/duplicate metric category")
        categories.add(category)
        if not isinstance(item.get("available"), bool):
            raise CoverageNCUError("metric availability must be boolean")
        policy = "SEMANTIC_SUM" if category in ADDITIVE_UNITS else "PER_KERNEL_ONLY"
        if item.get("aggregation", policy) != policy:
            raise CoverageNCUError(f"aggregation mismatch for {category}")
        if not item["available"]:
            if item.get("metric_name") not in (None, "") or item.get("unit") not in (None, ""):
                raise CoverageNCUError("unavailable metric claims name/unit")
            unavailable.append({"category": category, "available": False,
                                "reason": _text(item.get("reason"), f"{category}.reason"),
                                "aggregation": policy})
            continue
        name = _text(item.get("metric_name"), f"{category}.metric_name")
        unit = _text(item.get("unit"), f"{category}.unit")
        if name in names:
            raise CoverageNCUError("duplicate exact metric name")
        names.add(name)
        allowed = ADDITIVE_UNITS.get(category, PER_KERNEL_UNITS.get(category, set()))
        if unit not in allowed:
            raise CoverageNCUError(f"unit mismatch for category {category}")
        available.append({"category": category, "available": True,
                          "metric_name": name, "unit": unit, "aggregation": policy})
    by_category = {row["category"]: row for row in available}
    for category, (exact_name, _units) in BASE_METRICS.items():
        if category not in by_category or by_category[category]["metric_name"] != exact_name:
            raise CoverageNCUError(f"missing required base metric {exact_name}")
    return available, unavailable


def _regions(raw: Any) -> dict[int, dict[str, Any]]:
    if not isinstance(raw, Mapping) or set(map(str, range(28))) != set(map(str, raw)):
        raise CoverageNCUError("qweight_regions must contain exactly layers 0..27")
    output = {}
    for layer in range(28):
        item = raw.get(str(layer), raw.get(layer))
        if not isinstance(item, Mapping) or item.get("contiguous") is not True:
            raise CoverageNCUError(f"invalid/noncontiguous qweight region L{layer}")
        output[layer] = {"pointer": _integer(item.get("pointer"), "pointer", 1),
                         "bytes": _integer(item.get("bytes"), "bytes", 1)}
    return output


def _reset(raw: Any, label: str, event_index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS" or raw.get("performed") is not True:
        raise CoverageNCUError(f"missing/failed {label}")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise CoverageNCUError(f"{label} is not a persistence reset")
    if _integer(raw.get("event_index"), f"{label}.event_index") != event_index:
        raise CoverageNCUError(f"{label} event order mismatch")
    return {"status": "PASS", "performed": True, "operation": operation,
            "event_index": event_index}


def _policy(path: Path, condition: str, regions: Mapping[int, Mapping[str, Any]]) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise CoverageNCUError("invalid policy history JSON") from exc
    if isinstance(raw, Mapping) and "policy_receipt" in raw:
        raw = raw["policy_receipt"]
    if not isinstance(raw, Mapping) or raw.get("status") != "PASS":
        raise CoverageNCUError("policy history must be one PASS object")
    if _text(raw.get("condition"), "policy.condition").upper() != condition:
        raise CoverageNCUError("policy condition mismatch")
    match = CONDITION_RE.fullmatch(condition)
    assert match is not None
    mode, count_text = match.groups()
    count = int(count_text)
    selected = list(LAYER_ORDER[:count])
    if raw.get("selected_layers") != selected:
        raise CoverageNCUError("policy selected-layer set/order mismatch")
    if _integer(raw.get("requested_setaside_bytes"), "requested_setaside_bytes") != REQUESTED_SETASIDE_BYTES:
        raise CoverageNCUError("requested set-aside drift")
    if _integer(raw.get("actual_setaside_bytes"), "actual_setaside_bytes") != ACTUAL_SETASIDE_BYTES:
        raise CoverageNCUError("actual set-aside drift")
    stream = _text(raw.get("stream_identity"), "stream_identity")
    before = _reset(raw.get("reset_before"), "reset_before", 0)
    updates = raw.get("updates", raw.get("switches"))
    expected = [(phase, layer) for phase in PHASES for layer in sorted(selected)]
    if not isinstance(updates, list) or len(updates) != len(expected):
        raise CoverageNCUError("missing/duplicate complete policy history")
    normalized = []
    for index, (event, (phase, layer)) in enumerate(zip(updates, expected), 1):
        if not isinstance(event, Mapping):
            raise CoverageNCUError("invalid policy update")
        observed = (_integer(event.get("sequence_index"), "sequence_index"),
                    _text(event.get("phase"), "phase").upper(),
                    _integer(event.get("layer_index"), "layer_index"))
        if observed != (index, phase, layer):
            raise CoverageNCUError("policy update order/identity mismatch")
        region = regions[layer]
        if (_integer(event.get("base_pointer"), "base_pointer", 1) != region["pointer"] or
                _integer(event.get("num_bytes"), "num_bytes", 1) != region["bytes"]):
            raise CoverageNCUError("policy update is not exact full qweight window")
        if _text(event.get("stream_identity"), "update.stream_identity") != stream:
            raise CoverageNCUError("policy stream identity mismatch")
        if event.get("reset_performed") is not False:
            raise CoverageNCUError("forbidden in-run reset")
        ratio = _finite(event.get("hit_ratio"), "hit_ratio")
        if not math.isclose(ratio, 1.0 / count, rel_tol=0.0, abs_tol=1e-12):
            raise CoverageNCUError("policy hitRatio is not exact 1/N")
        hit = _text(event.get("hit_prop"), "hit_prop").upper()
        miss = _text(event.get("miss_prop"), "miss_prop").upper()
        persisting = event.get("target_persisting")
        expected_policy = ("NORMAL", "NORMAL", False) if mode == "CONTROL" else ("PERSISTING", "STREAMING", True)
        if (hit, miss, persisting) != expected_policy:
            raise CoverageNCUError("CONTROL/FAIR policy semantics mismatch")
        normalized.append({"sequence_index": index, "phase": phase,
                           "layer_index": layer, "base_pointer": region["pointer"],
                           "num_bytes": region["bytes"], "hit_ratio": ratio,
                           "hit_prop": hit, "miss_prop": miss,
                           "target_persisting": persisting})
    after = _reset(raw.get("reset_after"), "reset_after", len(expected) + 1)
    if raw.get("other_reset_events", []) != []:
        raise CoverageNCUError("reset allowed only before/after profile")
    return {"status": "PASS", "condition": condition, "selected_layers": selected,
            "requested_setaside_bytes": REQUESTED_SETASIDE_BYTES,
            "actual_setaside_bytes": ACTUAL_SETASIDE_BYTES,
            "stream_identity": stream, "reset_before": before, "updates": normalized,
            "reset_after": after, "sha256": _file_sha(path)}


def _profile_spec(raw: Any, root: Path) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise CoverageNCUError("profile specification must be an object")
    condition = _text(raw.get("condition"), "condition").upper()
    layer = _integer(raw.get("layer_index"), "layer_index")
    if (condition, layer) not in MATRIX:
        raise CoverageNCUError("profile is outside frozen 16-point matrix")
    role = _text(raw.get("role"), "role")
    decode = _integer(raw.get("decode_index"), "decode_index")
    if role != "up_proj" or decode != 3:
        raise CoverageNCUError("wrong semantic occurrence; coverage NCU is exact up_proj D3")
    kernels = raw.get("expected_kernel_names")
    if not isinstance(kernels, list) or not kernels or any(not isinstance(x, str) or not x.strip() for x in kernels):
        raise CoverageNCUError("invalid expected kernel inventory")
    if len(kernels) != len(set(kernels)):
        raise CoverageNCUError("duplicate expected kernel inventory")
    local_regions = _regions(raw.get("qweight_regions")) if raw.get("qweight_regions") is not None else None
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
            "policy_history_path": _path(root, raw.get("policy_history_path"), "policy_history_path"),
            "qweight_regions": local_regions}


def _session(path: Path, spec: Mapping[str, Any], metrics: set[str]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if set(_options(text, "--replay-mode")) != {"application"}:
        raise CoverageNCUError("SESSION replay mode mismatch")
    if set(_options(text, "--cache-control")) != {"none"}:
        raise CoverageNCUError("SESSION cache-control mismatch")
    if {value.rstrip("/") for value in _options(text, "--nvtx-include")} != {spec["range_name"]}:
        raise CoverageNCUError("SESSION semantic range mismatch")
    metric_args = set(_options(text, "--metrics"))
    if len(metric_args) != 1 or set(next(iter(metric_args)).split(",")) != metrics:
        raise CoverageNCUError("SESSION metric set mismatch")
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
                "input_sha256": raw.get("input_sha256"), "output_sha256": raw.get("output_sha256"),
                "range_name": raw.get("range", raw.get("range_name")),
                "policy_history_sha256": raw.get("policy_history_sha256",
                                                   raw.get("policy_receipt_sha256")),
            }
            expected = {key: spec[key] for key in observed if key != "policy_history_sha256"}
            expected["policy_history_sha256"] = policy_sha
            if observed != expected:
                raise CoverageNCUError("PROFILE PASS semantic/token/policy identity mismatch")
            receipts.append(observed)
    if not receipts:
        raise CoverageNCUError("PROFILE contains no PASS receipt")
    if any(receipt != receipts[0] for receipt in receipts[1:]):
        raise CoverageNCUError("PROFILE PASS receipt identity drift")
    return receipts


def _base(path: Path, spec: Mapping[str, Any], metrics: list[dict[str, Any]],
          pass_count: int) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise CoverageNCUError("BASE lacks header/unit/data rows")
    header, units, *data = table
    if len(header) != len(set(header)) or len(units) != len(header) or any(len(row) != len(header) for row in data):
        raise CoverageNCUError("BASE ambiguous/ragged header")
    range_columns = [name for name in header if "Push/Pop_Range" in name]
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes",
                *[row["metric_name"] for row in metrics]}
    if len(range_columns) != 1 or required - set(header):
        raise CoverageNCUError("BASE missing/ambiguous required columns")
    index = {name: header.index(name) for name in (*required, range_columns[0])}
    for metric in metrics:
        if units[index[metric["metric_name"]]].strip() != metric["unit"]:
            raise CoverageNCUError(f"BASE unit mismatch for {metric['metric_name']}")
    selected = [row for row in data if _exact_range(row[index[range_columns[0]]], spec["range_name"])]
    names = [row[index["Kernel Name"]].strip() for row in selected]
    if not selected or sorted(names) != sorted(spec["expected_kernel_names"]):
        raise CoverageNCUError("BASE exact kernel inventory mismatch")
    ids = [(row[index["Process ID"]].strip(), row[index["ID"]].strip()) for row in selected]
    if any(not a or not b for a, b in ids) or len(ids) != len(set(ids)) or len({a for a, _ in ids}) != 1:
        raise CoverageNCUError("BASE duplicate row/kernel/process identity ambiguity")
    kernel_metrics, sums = [], {row["category"]: Decimal(0) for row in metrics
                               if row["aggregation"] == "SEMANTIC_SUM"}
    for row in selected:
        if _decimal(row[index["profiler__replayer_passes"]], "replayer passes") != Decimal(pass_count):
            raise CoverageNCUError("BASE replayer passes/PASS receipt count mismatch")
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
            "profiler_replayer_passes": pass_count,
            "kernel_inventory": names, "kernel_metrics": kernel_metrics,
            "additive_semantic_sums": {category: _number(value)
                                       for category, value in sums.items()}}


def consume(document: Mapping[str, Any], root: Path | str = Path(".")) -> dict[str, Any]:
    """Validate and independently normalize the exact primary 16-profile matrix."""
    if not isinstance(document, Mapping) or document.get("schema_version") != 1:
        raise CoverageNCUError("schema_version must equal 1")
    root = Path(root)
    query = _query(document.get("runtime_metric_query"), root)
    metrics, unavailable = _catalog(document.get("metric_availability"))
    regions = _regions(document.get("qweight_regions")) if document.get("qweight_regions") is not None else None
    raw_profiles = document.get("profiles")
    if not isinstance(raw_profiles, list) or len(raw_profiles) != 16:
        raise CoverageNCUError("coverage NCU requires exact 16-profile matrix")
    specs, identities = [], set()
    for raw in raw_profiles:
        spec = _profile_spec(raw, root)
        key = (spec["condition"], spec["layer_index"])
        if key in identities:
            raise CoverageNCUError("duplicate coverage NCU matrix point")
        identities.add(key)
        specs.append(spec)
    if identities != MATRIX:
        raise CoverageNCUError("coverage NCU frozen matrix mismatch")
    output = []
    metric_names = {row["metric_name"] for row in metrics}
    for spec in specs:
        profile_regions = spec["qweight_regions"] or regions
        if profile_regions is None:
            raise CoverageNCUError("profile lacks process-local qweight region authority")
        policy = _policy(spec["policy_history_path"], spec["condition"], profile_regions)
        receipts = _profile_receipts(spec["profile_path"], spec, policy["sha256"])
        output.append({"condition": spec["condition"], "layer_index": spec["layer_index"],
                       "role": "up_proj", "decode_index": 3,
                       "range_name": spec["range_name"],
                       "input_sha256": spec["input_sha256"],
                       "output_sha256": spec["output_sha256"],
                       "session": _session(spec["session_path"], spec, metric_names),
                       "profile": {"sha256": _file_sha(spec["profile_path"]),
                                   "pass_receipt_count": len(receipts),
                                   "identical_identity": True},
                       "base": _base(spec["base_path"], spec, metrics, len(receipts)),
                       "policy_history": policy})
    return {"schema_version": 1, "status": "PASS",
            "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_COMPLETE_POLICY_HISTORY_ONLY",
            "matrix_contract": "FROZEN_PRIMARY_16_D3_PROFILES",
            "profile_count": 16, "runtime_metric_query": query,
            "metric_availability": [*metrics, *unavailable], "profiles": output,
            "non_additive_policy": "PER_KERNEL_ONLY"}


__all__ = ["CoverageNCUError", "LAYER_ORDER", "MATRIX", "consume"]
