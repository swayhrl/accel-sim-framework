#!/usr/bin/env python3
"""Fail-closed consumer for targeted L2-persistence natural evidence.

Only raw fresh-process rows, raw NCU BASE/SESSION/PROFILE triples, and policy
receipts are accepted. Producer summaries are deliberately not inputs.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

try:
    from policy_receipt import validate_policy_receipt
except ImportError:
    from .policy_receipt import validate_policy_receipt


class NaturalPersistenceError(ValueError):
    pass


CONDITIONS = ("BASELINE", "SETASIDE_ONLY", "PERSIST_L0_UP", "PERSIST_L14_UP", "PERSIST_L0_DOWN")
TARGET_BY_CONDITION = {
    "BASELINE": None, "SETASIDE_ONLY": None, "PERSIST_L0_UP": "L0_UP",
    "PERSIST_L14_UP": "L14_UP", "PERSIST_L0_DOWN": "L0_DOWN",
}
NATURAL_MATRIX = frozenset(
    [(0, "up_proj", d) for d in range(4)]
    + [(14, "up_proj", d) for d in range(4)]
    + [(0, "down_proj", d) for d in range(4)]
)
PRIMARY_POINTS = ((0, "up_proj", 1), (0, "up_proj", 3), (14, "up_proj", 3), (0, "down_proj", 3))
PROFILE_CONDITIONS = {
    (0, "up_proj", 1): ("BASELINE", "SETASIDE_ONLY", "PERSIST_L0_UP", "PERSIST_L14_UP"),
    (0, "up_proj", 3): ("BASELINE", "SETASIDE_ONLY", "PERSIST_L0_UP", "PERSIST_L14_UP"),
    (14, "up_proj", 3): ("BASELINE", "SETASIDE_ONLY", "PERSIST_L14_UP", "PERSIST_L0_UP"),
    (0, "down_proj", 3): ("BASELINE", "SETASIDE_ONLY", "PERSIST_L0_DOWN", "PERSIST_L0_UP"),
}
NCU_MATRIX = frozenset((c, *p) for p, cs in PROFILE_CONDITIONS.items() for c in cs)
TARGET_CONDITION = {(0, "up_proj"): "PERSIST_L0_UP", (14, "up_proj"): "PERSIST_L14_UP", (0, "down_proj"): "PERSIST_L0_DOWN"}
UNRELATED_CONDITION = {(0, "up_proj"): "PERSIST_L14_UP", (14, "up_proj"): "PERSIST_L0_UP", (0, "down_proj"): "PERSIST_L0_UP"}
METRICS = ("l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum")
EXPECTED_REPS = 7
MIB = 1024 * 1024
SWEEP_MIB = (8, 16, 24, 32)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_FINAL_STATES = frozenset({
    "MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW", "TARGETED_PERSISTENCE_TRAFFIC_ONLY",
    "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED", "CUDA_PERSISTENCE_POLICY_UNQUALIFIED",
})


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise NaturalPersistenceError(f"missing or empty {label}")
    return value.strip()


def _int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise NaturalPersistenceError(f"invalid {label}")
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise NaturalPersistenceError(f"invalid {label}: {value!r}") from exc
    if str(value).strip() not in {str(parsed), f"{parsed}.0"}:
        raise NaturalPersistenceError(f"non-integral {label}: {value!r}")
    return parsed


def _finite(value: Any, label: str, *, positive: bool = False) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise NaturalPersistenceError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(parsed) or (positive and parsed <= 0):
        raise NaturalPersistenceError(f"nonfinite/nonpositive {label}: {value!r}")
    return parsed


def _sha(value: Any, label: str) -> str:
    parsed = str(value).strip().lower()
    if not HEX64.fullmatch(parsed):
        raise NaturalPersistenceError(f"invalid {label}: expected lowercase SHA256")
    return parsed


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _tokens(value: Any, label: str) -> tuple[int, ...]:
    if not isinstance(value, list) or len(value) != 4:
        raise NaturalPersistenceError(f"{label} must contain exactly D0..D3")
    parsed = tuple(_int(item, f"{label}[{i}]") for i, item in enumerate(value))
    if any(item < 0 for item in parsed):
        raise NaturalPersistenceError(f"negative token in {label}")
    return parsed


def _occurrence(raw: Mapping[str, Any], *, require_timing: bool) -> dict:
    layer, role, decode = _int(raw.get("layer_index"), "layer_index"), _text(raw.get("role"), "role"), _int(raw.get("decode_index"), "decode_index")
    key = (layer, role, decode)
    if key not in NATURAL_MATRIX:
        raise NaturalPersistenceError(f"wrong natural occurrence: {key!r}")
    if _int(raw.get("M"), "M") != 1:
        raise NaturalPersistenceError(f"natural occurrence is not M1: {key!r}")
    implementation = _text(raw.get("implementation"), "implementation")
    if implementation != "AWQ_FP16_INPUT":
        raise NaturalPersistenceError(f"wrong natural implementation: {implementation}")
    result = {
        "layer_index": layer, "role": role, "decode_index": decode, "M": 1,
        "implementation": implementation, "generated_token_id": _int(raw.get("generated_token_id"), "generated_token_id"),
        "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
        "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
        "range_name": _text(raw.get("range_name"), "range_name"),
    }
    if require_timing:
        result["timing_ms"] = _finite(raw.get("timing_ms"), "timing_ms", positive=True)
    return result


def _identity(item: Mapping[str, Any]) -> dict:
    return {key: item[key] for key in (
        "layer_index", "role", "decode_index", "M", "implementation", "generated_token_id",
        "input_sha256", "output_sha256", "range_name",
    )}


def _authority(document: Mapping[str, Any]) -> tuple[str, tuple[int, ...], dict]:
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    tokens = _tokens(document.get("generated_token_ids"), "generated_token_ids")
    raw = document.get("occurrence_authority")
    if not isinstance(raw, list):
        raise NaturalPersistenceError("occurrence_authority must be a list")
    authority = {}
    for entry in raw:
        item = _occurrence(entry, require_timing=False)
        key = (item["layer_index"], item["role"], item["decode_index"])
        if key in authority:
            raise NaturalPersistenceError(f"duplicate authority occurrence: {key!r}")
        if item["generated_token_id"] != tokens[key[2]]:
            raise NaturalPersistenceError(f"authority token mismatch: {key!r}")
        authority[key] = _identity(item)
    if set(authority) != NATURAL_MATRIX:
        raise NaturalPersistenceError("authority occurrence matrix mismatch")
    if len({item["range_name"] for item in authority.values()}) != 12:
        raise NaturalPersistenceError("authority ranges are not unique")
    return prefix, tokens, authority


def _stats(samples: Sequence[float]) -> dict:
    if not samples:
        raise NaturalPersistenceError("empty timing samples")
    values = [float(item) for item in samples]
    mean = statistics.fmean(values)
    return {"sample_count": len(values), "samples_ms": values, "min_ms": min(values),
            "median_ms": statistics.median(values), "max_ms": max(values), "mean_ms": mean,
            "cv": statistics.pstdev(values) / mean}


def _load_receipt(value: Any, root: Path) -> tuple[dict, str | None]:
    if isinstance(value, Mapping):
        return dict(value), None
    path = root / _text(value, "policy_receipt_path")
    if not path.is_file():
        raise NaturalPersistenceError(f"missing policy receipt: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise NaturalPersistenceError("policy receipt must be an object")
    return data, _hash(path)


def _policy(value: Any, root: Path, condition: str, budget: int | None, validator: Callable[..., dict]) -> dict:
    receipt, digest = _load_receipt(value, root)
    try:
        if condition in TARGET_BY_CONDITION:
            target = TARGET_BY_CONDITION[condition]
        elif condition.startswith("PERSIST_L0_UP_BUDGET_"):
            target = "L0_UP"
        else:
            raise NaturalPersistenceError(f"unsupported consumer policy condition: {condition}")
        result = validator(receipt, expected_condition=condition,
                           expected_target=target, expected_budget_bytes=budget)
    except Exception as exc:
        raise NaturalPersistenceError(f"policy receipt failed for {condition}: {exc}") from exc
    if not isinstance(result, dict) or result.get("status") != "PASS":
        raise NaturalPersistenceError(f"policy validator did not PASS for {condition}")
    result = dict(result)
    if digest is not None:
        result["receipt_sha256"] = digest
    return result


def _budget_policy(value: Any, root: Path, budget: int, validator: Callable[..., dict]) -> dict:
    receipt, _ = _load_receipt(value, root)
    condition = receipt.get("condition")
    if condition is None and isinstance(receipt.get("policy"), Mapping):
        condition = receipt["policy"].get("condition")
    condition = _text(condition, "budget policy condition").upper()
    if condition != "PERSIST_L0_UP" and not condition.startswith("PERSIST_L0_UP_BUDGET_"):
        raise NaturalPersistenceError(f"wrong budget policy condition: {condition}")
    return _policy(value, root, condition, budget, validator)


def consume_natural_runs(document: Mapping[str, Any], root: Path = Path("."),
                         policy_validator: Callable[..., dict] = validate_policy_receipt) -> dict:
    """Validate five conditions x seven fresh processes and recompute timings."""
    if document.get("schema_version") != 1:
        raise NaturalPersistenceError("unsupported natural run schema_version")
    prefix, tokens, authority = _authority(document)
    budget = _int(document.get("primary_budget_bytes"), "primary_budget_bytes")
    if budget <= 0:
        raise NaturalPersistenceError("primary_budget_bytes must be positive")
    conditions = document.get("conditions")
    if not isinstance(conditions, list):
        raise NaturalPersistenceError("conditions must be a list")
    by_condition, points, decode_points = {}, defaultdict(list), defaultdict(list)
    run_receipts, all_process_ids = [], set()
    for condition_raw in conditions:
        condition = _text(condition_raw.get("condition"), "condition")
        if condition not in CONDITIONS or condition in by_condition:
            raise NaturalPersistenceError(f"unknown/duplicate condition: {condition}")
        by_condition[condition] = condition_raw
        runs = condition_raw.get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise NaturalPersistenceError(f"{condition} must contain exactly 7 fresh runs")
        reps = set()
        for run in runs:
            rep = _int(run.get("rep"), "rep")
            if rep in reps or rep not in range(EXPECTED_REPS):
                raise NaturalPersistenceError(f"duplicate/out-of-range rep in {condition}: {rep}")
            reps.add(rep)
            process_id = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process_id in all_process_ids:
                raise NaturalPersistenceError("fresh_process_id reused across runs")
            all_process_ids.add(process_id)
            if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
                raise NaturalPersistenceError(f"prefix mismatch in {condition}/rep{rep}")
            if _tokens(run.get("generated_token_ids"), "generated_token_ids") != tokens:
                raise NaturalPersistenceError(f"token sequence mismatch in {condition}/rep{rep}")
            raw_occurrences = run.get("occurrences")
            if not isinstance(raw_occurrences, list):
                raise NaturalPersistenceError("run occurrences must be a list")
            seen = set()
            for raw in raw_occurrences:
                item = _occurrence(raw, require_timing=True)
                key = (item["layer_index"], item["role"], item["decode_index"])
                if key in seen:
                    raise NaturalPersistenceError(f"duplicate run occurrence: {key!r}")
                seen.add(key)
                if _identity(item) != authority[key]:
                    raise NaturalPersistenceError(f"occurrence SHA/identity mismatch: {condition}/{key!r}")
                points[(condition, *key)].append(item["timing_ms"])
            if seen != NATURAL_MATRIX:
                raise NaturalPersistenceError(f"12-occurrence matrix mismatch in {condition}/rep{rep}")
            decode_rows = run.get("decode_steps")
            if not isinstance(decode_rows, list):
                raise NaturalPersistenceError("decode_steps must be a list")
            decode_seen = set()
            for row in decode_rows:
                decode = _int(row.get("decode_index"), "decode_index")
                if decode in decode_seen or decode not in range(4):
                    raise NaturalPersistenceError("duplicate/out-of-range decode step")
                decode_seen.add(decode)
                if _int(row.get("generated_token_id"), "generated_token_id") != tokens[decode]:
                    raise NaturalPersistenceError("decode-step token mismatch")
                decode_points[(condition, decode)].append(_finite(row.get("timing_ms"), "decode timing_ms", positive=True))
            if decode_seen != set(range(4)):
                raise NaturalPersistenceError("decode-step matrix mismatch")
            normalized = _policy(run.get("policy_receipt", run.get("policy_receipt_path")), root,
                                 condition, 0 if condition == "BASELINE" else budget, policy_validator)
            run_receipts.append({"condition": condition, "rep": rep, "fresh_process_id": process_id, "policy": normalized})
    if set(by_condition) != set(CONDITIONS):
        raise NaturalPersistenceError("five-condition matrix mismatch")
    timing = []
    for key in sorted(points):
        if len(points[key]) != EXPECTED_REPS:
            raise NaturalPersistenceError(f"missing target timing samples: {key!r}")
        timing.append({"condition": key[0], **authority[key[1:]], "statistics": _stats(points[key])})
    decode_timing = []
    for key in sorted(decode_points):
        if len(decode_points[key]) != EXPECTED_REPS:
            raise NaturalPersistenceError(f"missing decode timing samples: {key!r}")
        decode_timing.append({"condition": key[0], "decode_index": key[1],
                              "generated_token_id": tokens[key[1]], "statistics": _stats(decode_points[key])})
    return {"status": "PASS", "authority": "RAW_FRESH_PROCESS_RUNS_AND_POLICY_RECEIPTS_ONLY",
            "accepted_prefix_sha256": prefix, "generated_token_ids": list(tokens),
            "primary_budget_bytes": budget, "fresh_process_count": len(all_process_ids),
            "timing_points": timing, "decode_step_timing": decode_timing, "policy_receipts": run_receipts}


def _session_options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text, re.MULTILINE)


def _audit_session(path: Path, range_name: str) -> dict:
    text = path.read_text(encoding="utf-8", errors="strict")
    if set(_session_options(text, "--replay-mode")) != {"application"}:
        raise NaturalPersistenceError("SESSION replay mode is not uniquely application")
    if set(_session_options(text, "--cache-control")) != {"none"}:
        raise NaturalPersistenceError("SESSION cache control is not uniquely none")
    if {item.rstrip("/") for item in _session_options(text, "--nvtx-include")} != {range_name}:
        raise NaturalPersistenceError("SESSION exact NVTX range mismatch")
    metrics = set(_session_options(text, "--metrics"))
    if len(metrics) != 1 or set(next(iter(metrics)).split(",")) != set(METRICS):
        raise NaturalPersistenceError("SESSION exact metric set mismatch")
    return {"sha256": _hash(path), "replay_mode": "application", "cache_control": "none"}


def _decimal(value: str, label: str) -> Decimal:
    try:
        parsed = Decimal(value.replace(",", "").strip())
    except InvalidOperation as exc:
        raise NaturalPersistenceError(f"invalid {label}") from exc
    if not parsed.is_finite() or parsed < 0:
        raise NaturalPersistenceError(f"invalid/nonfinite {label}")
    return parsed


def _exact_range(cell: str, target: str) -> bool:
    return len(re.findall(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)", cell.strip())) == 1


def _read_base(path: Path, range_name: str, kernel_names: list[str], passes: int) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise NaturalPersistenceError("BASE missing header/unit/data rows")
    header, units = table[:2]
    if len(header) != len(set(header)) or len(units) != len(header):
        raise NaturalPersistenceError("BASE malformed header/unit rows")
    index = {name: i for i, name in enumerate(header)}
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes", *METRICS}
    if required - set(index):
        raise NaturalPersistenceError("BASE missing required metric/identity column")
    range_columns = [i for i, name in enumerate(header) if "Push/Pop_Range" in name]
    if len(range_columns) != 1:
        raise NaturalPersistenceError("BASE ambiguous NVTX range column")
    for metric in METRICS:
        if units[index[metric]].strip() != "byte":
            raise NaturalPersistenceError(f"BASE metric unit mismatch: {metric}")
    selected = [row for row in table[2:] if len(row) == len(header)
                and row[index["ID"]].strip() and _exact_range(row[range_columns[0]], range_name)]
    if not selected:
        raise NaturalPersistenceError("BASE has no exact target range rows")
    names = [row[index["Kernel Name"]].strip() for row in selected]
    if names != kernel_names and sorted(names) != sorted(kernel_names):
        raise NaturalPersistenceError("BASE exact kernel inventory mismatch")
    process_ids = {row[index["Process ID"]].strip() for row in selected}
    ids = [row[index["ID"]].strip() for row in selected]
    if "" in process_ids or len(process_ids) != 1 or "" in ids or len(ids) != len(set(ids)):
        raise NaturalPersistenceError("BASE ambiguous process/kernel identity")
    sums = {metric: Decimal(0) for metric in METRICS}
    for row in selected:
        if _decimal(row[index["profiler__replayer_passes"]], "replayer passes") != Decimal(passes):
            raise NaturalPersistenceError("BASE replay pass mismatch")
        for metric in METRICS:
            sums[metric] += _decimal(row[index[metric]], metric)
    return {"sha256": _hash(path), "kernel_names": names, "kernel_count": len(names),
            "process_id": next(iter(process_ids)),
            "metric_sums": {key: str(value) for key, value in sums.items()}}


def _profile_receipt(path: Path, expected: Mapping[str, Any], condition: str,
                     prefix: str, tokens: tuple[int, ...]) -> dict:
    receipts = []
    for line in path.read_text(encoding="utf-8", errors="strict").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("status") == "PASS":
            receipts.append(item)
    if len(receipts) != 1:
        raise NaturalPersistenceError("PROFILE must contain exactly one PASS receipt")
    receipt = receipts[0]
    checks = {
        "condition": condition, "layer_index": expected["layer_index"], "role": expected["role"],
        "decode_index": expected["decode_index"], "M": 1, "implementation": "AWQ_FP16_INPUT",
        "generated_token_id": expected["generated_token_id"], "range": expected["range_name"],
        "input_sha256": expected["input_sha256"], "output_sha256": expected["output_sha256"],
        "prefix_token_sha256": prefix, "generated_token_ids": list(tokens),
    }
    mismatches = {key: (value, receipt.get(key)) for key, value in checks.items() if receipt.get(key) != value}
    if mismatches:
        raise NaturalPersistenceError("PROFILE semantic identity mismatch: " + repr(mismatches))
    return {"sha256": _hash(path), "status": "PASS", **checks}


def consume_natural_ncu(document: Mapping[str, Any], root: Path = Path("."),
                        policy_validator: Callable[..., dict] = validate_policy_receipt) -> dict:
    """Consume exactly the frozen sixteen raw NCU triples."""
    if document.get("schema_version") != 1:
        raise NaturalPersistenceError("unsupported natural NCU schema_version")
    prefix, tokens, authority = _authority(document)
    budget = _int(document.get("primary_budget_bytes"), "primary_budget_bytes")
    profiles = document.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != 16:
        raise NaturalPersistenceError("natural NCU matrix must contain exactly 16 profiles")
    seen, output = set(), []
    for raw in profiles:
        condition = _text(raw.get("condition"), "condition")
        key3 = (_int(raw.get("layer_index"), "layer_index"), _text(raw.get("role"), "role"),
                _int(raw.get("decode_index"), "decode_index"))
        key = (condition, *key3)
        if key not in NCU_MATRIX or key in seen:
            raise NaturalPersistenceError(f"wrong/duplicate NCU semantic point: {key!r}")
        seen.add(key)
        expected = authority[key3]
        for field in ("M", "implementation", "generated_token_id", "input_sha256", "output_sha256", "range_name"):
            observed = raw.get(field)
            if field in {"M", "generated_token_id"}:
                observed = _int(observed, field)
            elif field.endswith("sha256"):
                observed = _sha(observed, field)
            else:
                observed = _text(observed, field)
            if observed != expected[field]:
                raise NaturalPersistenceError(f"NCU {field} mismatch: {key!r}")
        names = raw.get("expected_kernel_names")
        if not isinstance(names, list) or not names or len(names) != len(set(names)):
            raise NaturalPersistenceError("invalid expected kernel inventory")
        passes = _int(raw.get("expected_pass_count"), "expected_pass_count")
        paths = {kind: root / _text(raw.get(f"{kind}_path"), f"{kind}_path")
                 for kind in ("base", "session", "profile")}
        if not all(path.is_file() for path in paths.values()):
            raise NaturalPersistenceError("missing raw BASE/SESSION/PROFILE evidence")
        policy = _policy(raw.get("policy_receipt", raw.get("policy_receipt_path")), root, condition,
                         0 if condition == "BASELINE" else budget, policy_validator)
        output.append({"condition": condition, "semantic_identity": expected,
                       "session": _audit_session(paths["session"], expected["range_name"]),
                       "profile": _profile_receipt(paths["profile"], expected, condition, prefix, tokens),
                       "base": _read_base(paths["base"], expected["range_name"], names, passes),
                       "policy": policy})
    if seen != NCU_MATRIX:
        raise NaturalPersistenceError("natural NCU frozen matrix mismatch")
    return {"status": "PASS", "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_POLICY_RECEIPT_ONLY",
            "profile_count": 16, "accepted_prefix_sha256": prefix,
            "generated_token_ids": list(tokens), "profiles": output}


def _benefit(reference: float, intervention: float) -> float:
    if reference <= 0:
        raise NaturalPersistenceError("effect reference must be positive")
    return (reference - intervention) / reference


def compute_policy_effects(native: Mapping[str, Any], ncu: Mapping[str, Any]) -> dict:
    """Compute reservation, target, unrelated, materiality, and specificity."""
    timing = {}
    for point in native.get("timing_points", []):
        key = (point["condition"], point["layer_index"], point["role"], point["decode_index"])
        if key in timing:
            raise NaturalPersistenceError(f"duplicate timing effect point: {key!r}")
        timing[key] = point["statistics"]
    dram = {}
    for point in ncu.get("profiles", []):
        identity = point["semantic_identity"]
        key = (point["condition"], identity["layer_index"], identity["role"], identity["decode_index"])
        if key in dram:
            raise NaturalPersistenceError(f"duplicate NCU effect point: {key!r}")
        dram[key] = float(Decimal(point["base"]["metric_sums"]["dram__bytes.sum"]))
    rows = []
    for layer, role, decode in PRIMARY_POINTS:
        target, unrelated = TARGET_CONDITION[(layer, role)], UNRELATED_CONDITION[(layer, role)]
        keys = [(condition, layer, role, decode) for condition in ("BASELINE", "SETASIDE_ONLY", target, unrelated)]
        if any(key not in timing or key not in dram for key in keys):
            raise NaturalPersistenceError(f"missing effect authority for {(layer, role, decode)!r}")
        base_t, set_t, target_t, unrelated_t = [timing[key] for key in keys]
        base_d, set_d, target_d, unrelated_d = [dram[key] for key in keys]
        reservation_t = _benefit(base_t["median_ms"], set_t["median_ms"])
        target_t_benefit = _benefit(set_t["median_ms"], target_t["median_ms"])
        unrelated_t_benefit = _benefit(set_t["median_ms"], unrelated_t["median_ms"])
        target_dispersion = math.hypot(set_t["cv"], target_t["cv"])
        unrelated_dispersion = math.hypot(set_t["cv"], unrelated_t["cv"])
        material_timing = target_t_benefit >= 0.05 and target_t_benefit > target_dispersion
        timing_specific = (material_timing and target_t_benefit - unrelated_t_benefit >= 0.05
                           and target_t_benefit - unrelated_t_benefit > math.hypot(target_dispersion, unrelated_dispersion))
        reservation_d = _benefit(base_d, set_d)
        target_d_benefit = _benefit(set_d, target_d)
        unrelated_d_benefit = _benefit(set_d, unrelated_d)
        target_d_reduction, unrelated_d_reduction = set_d - target_d, set_d - unrelated_d
        material_dram = target_d_benefit >= 0.20 and target_d_reduction >= 4 * MIB
        dram_specific = (material_dram and target_d_benefit - unrelated_d_benefit >= 0.20
                         and target_d_reduction - unrelated_d_reduction >= 4 * MIB)
        rows.append({
            "layer_index": layer, "role": role, "decode_index": decode,
            "target_condition": target, "unrelated_condition": unrelated,
            "reservation_effect": {"timing_benefit_fraction": reservation_t, "dram_benefit_fraction": reservation_d},
            "target_persistence_effect": {
                "timing_benefit_fraction": target_t_benefit, "timing_combined_dispersion": target_dispersion,
                "dram_benefit_fraction": target_d_benefit, "dram_reduction_bytes": target_d_reduction},
            "unrelated_persistence_effect": {
                "timing_benefit_fraction": unrelated_t_benefit, "timing_combined_dispersion": unrelated_dispersion,
                "dram_benefit_fraction": unrelated_d_benefit, "dram_reduction_bytes": unrelated_d_reduction},
            "MATERIAL_TIMING_BENEFIT": material_timing, "MATERIAL_DRAM_BENEFIT": material_dram,
            "TIMING_TARGET_SPECIFIC": timing_specific, "DRAM_TARGET_SPECIFIC": dram_specific,
            "TARGET_SPECIFIC": timing_specific or dram_specific,
        })
    return {"status": "PASS", "comparison_reference": "SETASIDE_ONLY",
            "materiality": {
                "timing": ">=5% benefit and benefit > hypot(CV_setaside,CV_target)",
                "dram": ">=20% reduction and >=4MiB absolute",
                "target_specific_timing": "target minus unrelated >=5pp and exceeds combined comparison dispersion",
                "target_specific_dram": "target minus unrelated >=20pp and >=4MiB extra reduction"},
            "effects": rows}


def _sweep_budget_labels(qweight_bytes: int) -> list[int]:
    values = [mib * MIB for mib in SWEEP_MIB] + [qweight_bytes]
    if len(values) != len(set(values)):
        raise NaturalPersistenceError("full qweight budget duplicates a fixed tested budget")
    return values


def consume_budget_sweep(document: Mapping[str, Any], root: Path = Path("."),
                         policy_validator: Callable[..., dict] = validate_policy_receipt) -> dict:
    """Validate and recompute conditional L0-up D3 persistence-budget sweep."""
    if document.get("schema_version") != 1:
        raise NaturalPersistenceError("unsupported budget schema_version")
    triggered = document.get("triggered")
    if not isinstance(triggered, bool):
        raise NaturalPersistenceError("budget triggered must be boolean")
    trigger_material = bool(document.get("full_qweight_material_timing")) or bool(document.get("full_qweight_material_dram"))
    if triggered != trigger_material:
        raise NaturalPersistenceError("budget sweep trigger disagrees with full-qweight materiality")
    if not triggered:
        if document.get("points") not in (None, []):
            raise NaturalPersistenceError("untriggered budget sweep contains points")
        return {"status": "PASS", "triggered": False, "trigger_condition_verified_false": True,
                "first_tested_material_budget_bytes": None}
    prefix, tokens, authority = _authority(document)
    qweight = _int(document.get("qweight_bytes"), "qweight_bytes")
    if qweight <= 0:
        raise NaturalPersistenceError("qweight_bytes must be positive")
    expected_budgets = _sweep_budget_labels(qweight)
    points = document.get("points")
    if not isinstance(points, list) or len(points) != 5:
        raise NaturalPersistenceError("triggered sweep must contain five tested budgets")
    reference = document.get("setaside_only_reference")
    if not isinstance(reference, Mapping):
        raise NaturalPersistenceError("missing SETASIDE_ONLY sweep reference")
    reference_timing = _finite(reference.get("timing_median_ms"), "reference timing", positive=True)
    reference_cv = _finite(reference.get("timing_cv"), "reference CV")
    reference_dram = _finite(reference.get("dram_bytes"), "reference DRAM", positive=True)
    expected_identity, seen_budgets, output, all_processes = authority[(0, "up_proj", 3)], set(), [], set()
    for point in points:
        budget = _int(point.get("budget_bytes"), "budget_bytes")
        if budget not in expected_budgets or budget in seen_budgets:
            raise NaturalPersistenceError(f"wrong/duplicate tested budget: {budget}")
        seen_budgets.add(budget)
        expected_ratio = min(1.0, budget / qweight)
        runs = point.get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise NaturalPersistenceError("every tested budget requires seven fresh runs")
        samples, reps, policy_outputs = [], set(), []
        for run in runs:
            rep = _int(run.get("rep"), "rep")
            if rep in reps or rep not in range(EXPECTED_REPS):
                raise NaturalPersistenceError("budget duplicate/out-of-range rep")
            reps.add(rep)
            process_id = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process_id in all_processes:
                raise NaturalPersistenceError("budget fresh_process_id reused")
            all_processes.add(process_id)
            if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
                raise NaturalPersistenceError("budget prefix mismatch")
            if _tokens(run.get("generated_token_ids"), "generated_token_ids") != tokens:
                raise NaturalPersistenceError("budget token sequence mismatch")
            occurrence = _occurrence(run.get("d3_occurrence"), require_timing=True)
            if _identity(occurrence) != expected_identity:
                raise NaturalPersistenceError("budget D3 occurrence identity mismatch")
            normalized = _budget_policy(run.get("policy_receipt", run.get("policy_receipt_path")),
                                        root, budget, policy_validator)
            if _int(normalized.get("access_window_num_bytes"), "access_window_num_bytes") != qweight:
                raise NaturalPersistenceError("budget sweep changed full qweight window")
            if not math.isclose(_finite(normalized.get("hit_ratio"), "hit_ratio"), expected_ratio,
                                rel_tol=0.0, abs_tol=1e-12):
                raise NaturalPersistenceError("budget hitRatio formula mismatch")
            samples.append(occurrence["timing_ms"])
            policy_outputs.append(normalized)
        profile = point.get("ncu_profile")
        if not isinstance(profile, Mapping):
            raise NaturalPersistenceError("budget point missing raw NCU profile")
        paths = {kind: root / _text(profile.get(f"{kind}_path"), f"{kind}_path")
                 for kind in ("base", "session", "profile")}
        if not all(path.is_file() for path in paths.values()):
            raise NaturalPersistenceError("budget point missing BASE/SESSION/PROFILE")
        names = profile.get("expected_kernel_names")
        if not isinstance(names, list) or not names:
            raise NaturalPersistenceError("budget invalid kernel inventory")
        ncu_policy = _budget_policy(profile.get("policy_receipt", profile.get("policy_receipt_path")),
                                    root, budget, policy_validator)
        if _int(ncu_policy.get("access_window_num_bytes"), "access_window_num_bytes") != qweight:
            raise NaturalPersistenceError("budget NCU changed full qweight window")
        if not math.isclose(_finite(ncu_policy.get("hit_ratio"), "hit_ratio"), expected_ratio,
                            rel_tol=0.0, abs_tol=1e-12):
            raise NaturalPersistenceError("budget NCU hitRatio mismatch")
        base = _read_base(paths["base"], expected_identity["range_name"], names,
                          _int(profile.get("expected_pass_count"), "expected_pass_count"))
        _audit_session(paths["session"], expected_identity["range_name"])
        _profile_receipt(paths["profile"], expected_identity, "PERSIST_L0_UP", prefix, tokens)
        point_stats = _stats(samples)
        dram = float(Decimal(base["metric_sums"]["dram__bytes.sum"]))
        timing_benefit, dram_benefit = _benefit(reference_timing, point_stats["median_ms"]), _benefit(reference_dram, dram)
        material_timing = timing_benefit >= 0.05 and timing_benefit > math.hypot(reference_cv, point_stats["cv"])
        material_dram = dram_benefit >= 0.20 and reference_dram - dram >= 4 * MIB
        output.append({"budget_bytes": budget, "budget_label": "FULL_QWEIGHT" if budget == qweight else f"{budget // MIB}MiB",
                       "hit_ratio": expected_ratio, "full_window_bytes": qweight, "timing": point_stats,
                       "dram_bytes": dram, "timing_benefit_fraction": timing_benefit,
                       "dram_benefit_fraction": dram_benefit, "MATERIAL_TIMING_BENEFIT": material_timing,
                       "MATERIAL_DRAM_BENEFIT": material_dram, "policy_receipts": policy_outputs,
                       "ncu_policy": ncu_policy})
    if seen_budgets != set(expected_budgets):
        raise NaturalPersistenceError("budget tested matrix mismatch")
    ordered = sorted(output, key=lambda row: row["budget_bytes"])
    material = [row["budget_bytes"] for row in ordered if row["MATERIAL_TIMING_BENEFIT"] or row["MATERIAL_DRAM_BENEFIT"]]
    return {"status": "PASS", "triggered": True,
            "authority": "RAW_7_FRESH_RUNS_AND_BASE_SESSION_PROFILE_POLICY_PER_TESTED_BUDGET",
            "tested_budgets_bytes": expected_budgets, "points": ordered,
            "first_tested_material_budget_bytes": min(material) if material else None,
            "threshold_claim": "FIRST_TESTED_MATERIAL_BUDGET_ONLY_NO_EXACT_HARDWARE_THRESHOLD"}


def derive_final_state(policy_qualified: bool, effects: Mapping[str, Any]) -> str:
    if not policy_qualified:
        return "CUDA_PERSISTENCE_POLICY_UNQUALIFIED"
    rows = effects.get("effects")
    if not isinstance(rows, list) or not rows:
        raise NaturalPersistenceError("missing effects for final-state decision")
    requirements_ready = any(
        row.get("MATERIAL_TIMING_BENEFIT")
        and row.get("MATERIAL_DRAM_BENEFIT")
        and row.get("TARGET_SPECIFIC")
        for row in rows
    )
    any_dram = any(row.get("MATERIAL_DRAM_BENEFIT") for row in rows)
    if requirements_ready:
        state = "MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW"
    elif any_dram:
        state = "TARGETED_PERSISTENCE_TRAFFIC_ONLY"
    else:
        state = "TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED"
    if state not in ALLOWED_FINAL_STATES:
        raise AssertionError("internal final-state contract violation")
    return state
