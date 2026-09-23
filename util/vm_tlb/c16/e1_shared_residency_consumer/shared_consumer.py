#!/usr/bin/env python3
"""Fail-closed consumer for C16 E1 shared persisting-L2 evidence.

Only raw per-run evidence and raw NCU BASE/SESSION/PROFILE/policy receipts are
accepted.  Producer summaries are intentionally not inputs.  The receipt
schema makes reset boundaries and every in-run policy update explicit so that
an apparently valid final window cannot hide a stale reset or missing switch.
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
from typing import Any, Mapping, Sequence


class SharedConsumerError(ValueError):
    pass


FIXED_SETASIDE_BYTES = 33_947_648
EXPECTED_ACTUAL_SETASIDE_BYTES = 37_748_736
EXPECTED_REPS = 7
ROTATING_REPS = 9
CONDITIONS = (
    "SETASIDE_ONLY", "ROTATE_CONTROL_3", "SINGLE_L0_UP",
    "SHARE2_UP", "SHARE2_L0", "SHARE3",
)
TARGETS = ("L0_UP", "L14_UP", "L0_DOWN")
SWITCH_ORDER_TARGETS = ("L0_UP", "L0_DOWN", "L14_UP")
PHASES = ("PREFILL", "D0", "D1", "D2", "D3")
TARGET_KEY = {"L0_UP": (0, "up_proj"), "L14_UP": (14, "up_proj"), "L0_DOWN": (0, "down_proj")}
NATURAL_MATRIX = frozenset((layer, role, d) for layer, role in TARGET_KEY.values() for d in range(4))
FULL_SWITCH_SEQUENCE = tuple((phase, target) for phase in PHASES for target in SWITCH_ORDER_TARGETS)
SELECTED_TARGETS = {
    "SETASIDE_ONLY": (),
    "ROTATE_CONTROL_3": (),
    "SINGLE_L0_UP": ("L0_UP",),
    "SHARE2_UP": ("L0_UP", "L14_UP"),
    "SHARE2_L0": ("L0_UP", "L0_DOWN"),
    "SHARE3": ("L0_UP", "L14_UP", "L0_DOWN"),
}
HIT_RATIO = {
    "SETASIDE_ONLY": None, "ROTATE_CONTROL_3": 1.0 / 3.0, "SINGLE_L0_UP": 1.0,
    "SHARE2_UP": 0.5, "SHARE2_L0": 0.5, "SHARE3": 1.0 / 3.0,
}
NCU_MATRIX = frozenset(
    [("SETASIDE_ONLY", "L0_UP"), ("ROTATE_CONTROL_3", "L0_UP"),
     ("SINGLE_L0_UP", "L0_UP"), ("SHARE2_UP", "L0_UP"),
     ("SHARE2_L0", "L0_UP"), ("SHARE3", "L0_UP")]
    + [(c, "L14_UP") for c in ("SETASIDE_ONLY", "ROTATE_CONTROL_3", "SHARE2_UP", "SHARE3")]
    + [(c, "L0_DOWN") for c in ("SETASIDE_ONLY", "ROTATE_CONTROL_3", "SHARE2_L0", "SHARE3")]
)
BASE_METRICS = ("l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SharedConsumerError(f"missing or empty {label}")
    return value.strip()


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if isinstance(value, bool):
        raise SharedConsumerError(f"invalid {label}")
    token = str(value).strip()
    try:
        result = int(token, 0)
    except (TypeError, ValueError) as exc:
        raise SharedConsumerError(f"invalid {label}: {value!r}") from exc
    if token.lower() not in {str(result), hex(result).lower()} or result < minimum:
        raise SharedConsumerError(f"invalid {label}: {value!r}")
    return result


def _finite(value: Any, label: str, positive: bool = False) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise SharedConsumerError(f"invalid {label}: {value!r}") from exc
    if not math.isfinite(result) or (positive and result <= 0):
        raise SharedConsumerError(f"nonfinite/nonpositive {label}: {value!r}")
    return result


def _boolean(value: Any, label: str) -> bool:
    if isinstance(value, bool):
        return value
    if value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value.strip().lower() in {"true", "false"}:
        return value.strip().lower() == "true"
    raise SharedConsumerError(f"invalid boolean {label}")


def _sha(value: Any, label: str) -> str:
    result = str(value).strip().lower()
    if not HEX64.fullmatch(result):
        raise SharedConsumerError(f"invalid {label}")
    return result


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stats(values: Sequence[float], unit: str = "ms") -> dict[str, Any]:
    if not values:
        raise SharedConsumerError("empty timing samples")
    checked = [_finite(value, "timing", positive=True) for value in values]
    mean = statistics.fmean(checked)
    return {"sample_count": len(checked), f"samples_{unit}": checked,
            f"min_{unit}": min(checked), f"median_{unit}": statistics.median(checked),
            f"max_{unit}": max(checked), f"mean_{unit}": mean,
            "cv": statistics.pstdev(checked) / mean}


def _regions(document: Mapping[str, Any], required_targets: Sequence[str] = TARGETS) -> dict[str, dict[str, Any]]:
    raw = document.get("qweight_regions")
    required = tuple(required_targets)
    if not isinstance(raw, Mapping) or not set(required).issubset(raw):
        raise SharedConsumerError("qweight_regions missing required target")
    out: dict[str, dict[str, Any]] = {}
    spans = []
    for target in required:
        item = raw[target]
        if not isinstance(item, Mapping):
            raise SharedConsumerError(f"invalid qweight region {target}")
        pointer = _integer(item.get("pointer"), f"{target}.pointer", 1)
        size = _integer(item.get("bytes"), f"{target}.bytes", 1)
        if not _boolean(item.get("contiguous"), f"{target}.contiguous"):
            raise SharedConsumerError(f"{target} is not contiguous")
        out[target] = {"pointer": pointer, "bytes": size, "contiguous": True}
        spans.append((pointer, pointer + size, target))
    for i, (begin, end, name) in enumerate(spans):
        if any(begin < other_end and other_begin < end for other_begin, other_end, other in spans[i + 1:]):
            raise SharedConsumerError(f"overlapping qweight region: {name}")
    return out


def _reset(raw: Any, label: str, event_index: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        raise SharedConsumerError(f"missing {label} reset receipt")
    if _text(raw.get("status"), f"{label}.status").upper() != "PASS":
        raise SharedConsumerError(f"{label} reset did not PASS")
    if not _boolean(raw.get("performed"), f"{label}.performed"):
        raise SharedConsumerError(f"{label} reset was not performed")
    operation = _text(raw.get("operation"), f"{label}.operation")
    if "reset" not in operation.lower() or "persist" not in operation.lower():
        raise SharedConsumerError(f"{label} is not a persisting reset")
    if _integer(raw.get("event_index"), f"{label}.event_index") != event_index:
        raise SharedConsumerError(f"stale/out-of-order {label} reset")
    return {"status": "PASS", "performed": True, "operation": operation, "event_index": event_index}


def validate_policy_receipt(receipt: Mapping[str, Any], condition: str,
                            regions: Mapping[str, Mapping[str, Any]],
                            *, rotating: bool = False) -> dict[str, Any]:
    """Validate exact fixed-budget state transitions for one process/profile."""
    if not isinstance(receipt, Mapping):
        raise SharedConsumerError("policy receipt must be an object")
    expected_condition = condition.upper()
    allowed = {"ROTATING_PERSIST", "ROTATING_CONTROL"} if rotating else set(CONDITIONS)
    if expected_condition not in allowed:
        raise SharedConsumerError(f"unsupported condition: {condition}")
    if _text(receipt.get("condition"), "condition").upper() != expected_condition:
        raise SharedConsumerError("policy condition mismatch")
    if _text(receipt.get("status"), "status").upper() != "PASS":
        raise SharedConsumerError("policy receipt status is not PASS")
    requested = _integer(receipt.get("requested_setaside_bytes"), "requested_setaside_bytes", 1)
    actual = _integer(receipt.get("actual_setaside_bytes"), "actual_setaside_bytes", requested)
    if requested != FIXED_SETASIDE_BYTES:
        raise SharedConsumerError("fixed total requested set-aside changed")
    if actual != EXPECTED_ACTUAL_SETASIDE_BYTES:
        raise SharedConsumerError(
            f"runtime query-back set-aside drift: expected {EXPECTED_ACTUAL_SETASIDE_BYTES}, got {actual}"
        )
    stream = _text(receipt.get("stream_identity"), "stream_identity")
    switches = receipt.get("switches")
    if not isinstance(switches, list):
        raise SharedConsumerError("switches must be a list")
    if rotating:
        expected_sequence = ((None, "L0_UP"), (None, "L14_UP"), (None, "L0_UP"))
        expected_ratio = 0.5
        selected_targets = {"L0_UP", "L14_UP"} if expected_condition == "ROTATING_PERSIST" else set()
    else:
        expected_sequence = () if expected_condition == "SETASIDE_ONLY" else FULL_SWITCH_SEQUENCE
        expected_ratio = HIT_RATIO[expected_condition]
        selected_targets = set(SELECTED_TARGETS[expected_condition])
    if len(switches) != len(expected_sequence):
        raise SharedConsumerError("missing/duplicate policy switch")
    before = _reset(receipt.get("reset_before"), "reset_before", 0)
    normalized = []
    durations = []
    for index, (raw, expected) in enumerate(zip(switches, expected_sequence), 1):
        if not isinstance(raw, Mapping):
            raise SharedConsumerError("invalid policy switch")
        phase, target = expected
        if _integer(raw.get("sequence_index"), "switch.sequence_index") != index:
            raise SharedConsumerError("wrong/duplicate switch order")
        if phase is not None and _text(raw.get("phase"), "switch.phase").upper() != phase:
            raise SharedConsumerError("wrong switch phase/order")
        if _text(raw.get("target"), "switch.target").upper() != target:
            raise SharedConsumerError("wrong switch target/order")
        region = regions[target]
        if _integer(raw.get("base_pointer"), "switch.base_pointer", 1) != region["pointer"]:
            raise SharedConsumerError("switch window pointer is not exact qweight pointer")
        if _integer(raw.get("num_bytes"), "switch.num_bytes", 1) != region["bytes"]:
            raise SharedConsumerError("switch window is not full exact qweight interval")
        if _text(raw.get("stream_identity"), "switch.stream_identity") != stream:
            raise SharedConsumerError("switch stream identity mismatch")
        if _boolean(raw.get("reset_performed"), "switch.reset_performed"):
            raise SharedConsumerError("in-run switch performed forbidden reset")
        ratio = _finite(raw.get("hit_ratio"), "switch.hit_ratio")
        if expected_ratio is None or not math.isclose(ratio, float(expected_ratio), rel_tol=0.0, abs_tol=1e-12):
            raise SharedConsumerError("wrong switch hitRatio")
        hit_prop = _text(raw.get("hit_prop"), "switch.hit_prop").upper()
        miss_prop = _text(raw.get("miss_prop"), "switch.miss_prop").upper()
        persisting = _boolean(raw.get("target_persisting"), "switch.target_persisting")
        should_persist = target in selected_targets
        if not should_persist:
            if persisting or hit_prop == "PERSISTING":
                raise SharedConsumerError("non-selected/API-control switch accidentally marks persistence")
            if hit_prop != "NORMAL" or miss_prop != "NORMAL":
                raise SharedConsumerError("non-selected/API-control switch must use unambiguous NORMAL policy")
        else:
            if not persisting or hit_prop != "PERSISTING" or miss_prop not in {"NORMAL", "STREAMING"}:
                raise SharedConsumerError("selected shared switch lacks exact persisting policy")
        duration = _finite(raw.get("api_duration_us"), "switch.api_duration_us")
        if duration < 0:
            raise SharedConsumerError("negative API switch duration")
        durations.append(duration)
        normalized.append({"sequence_index": index, "phase": phase, "target": target,
                           "base_pointer": region["pointer"], "num_bytes": region["bytes"],
                           "hit_ratio": ratio, "hit_prop": hit_prop, "miss_prop": miss_prop,
                           "target_persisting": persisting, "api_duration_us": duration})
    after = _reset(receipt.get("reset_after"), "reset_after", len(expected_sequence) + 1)
    other = receipt.get("other_reset_events", [])
    if not isinstance(other, list) or other:
        raise SharedConsumerError("reset is allowed only before and after condition")
    return {"status": "PASS", "authority": "RAW_ORDERED_POLICY_RECEIPT_ONLY",
            "condition": expected_condition, "requested_setaside_bytes": requested,
            "actual_setaside_bytes": actual,
            "runtime_query_back_matches_accepted_full_budget": True,
            "stream_identity": stream,
            "reset_before": before, "switches": normalized, "reset_after": after,
            "api_switch_overhead": _stats(durations, "us") if durations else None}


def _authority(document: Mapping[str, Any]) -> tuple[str, tuple[int, ...], dict[tuple[int, str, int], dict[str, Any]]]:
    prefix = _sha(document.get("accepted_prefix_sha256"), "accepted_prefix_sha256")
    raw_tokens = document.get("generated_token_ids")
    if not isinstance(raw_tokens, list) or len(raw_tokens) != 4:
        raise SharedConsumerError("generated_token_ids must contain D0..D3")
    tokens = tuple(_integer(x, "generated_token_id") for x in raw_tokens)
    rows = document.get("occurrence_authority")
    if not isinstance(rows, list):
        raise SharedConsumerError("occurrence_authority must be a list")
    out = {}
    for raw in rows:
        key = (_integer(raw.get("layer_index"), "layer_index"), _text(raw.get("role"), "role"),
               _integer(raw.get("decode_index"), "decode_index"))
        if key not in NATURAL_MATRIX or key in out:
            raise SharedConsumerError("wrong/duplicate occurrence authority")
        item = {"layer_index": key[0], "role": key[1], "decode_index": key[2],
                "M": _integer(raw.get("M"), "M"),
                "implementation": _text(raw.get("implementation"), "implementation"),
                "generated_token_id": _integer(raw.get("generated_token_id"), "generated_token_id"),
                "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
                "output_sha256": _sha(raw.get("output_sha256"), "output_sha256")}
        if item["M"] != 1 or item["implementation"] != "AWQ_FP16_INPUT" or item["generated_token_id"] != tokens[key[2]]:
            raise SharedConsumerError("occurrence authority semantic mismatch")
        out[key] = item
    if set(out) != NATURAL_MATRIX:
        raise SharedConsumerError("occurrence authority matrix mismatch")
    return prefix, tokens, out


def _occurrence(raw: Mapping[str, Any], expected: Mapping[str, Any]) -> float:
    checks = {"layer_index": _integer(raw.get("layer_index"), "layer_index"),
              "role": _text(raw.get("role"), "role"),
              "decode_index": _integer(raw.get("decode_index"), "decode_index"),
              "M": _integer(raw.get("M"), "M"),
              "implementation": _text(raw.get("implementation"), "implementation"),
              "generated_token_id": _integer(raw.get("generated_token_id"), "generated_token_id"),
              "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
              "output_sha256": _sha(raw.get("output_sha256"), "output_sha256")}
    if checks != expected:
        raise SharedConsumerError("occurrence identity/SHA drift")
    return _finite(raw.get("timing_ms"), "occurrence timing_ms", positive=True)


def consume_shared_runs(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate 6 conditions x 7 fresh processes and independently recompute timing."""
    if document.get("schema_version") != 1:
        raise SharedConsumerError("unsupported shared run schema")
    if _integer(document.get("fixed_setaside_bytes"), "fixed_setaside_bytes") != FIXED_SETASIDE_BYTES:
        raise SharedConsumerError("wrong fixed total set-aside")
    document_regions = _regions(document) if isinstance(document.get("qweight_regions"), Mapping) else None
    prefix, tokens, authority = _authority(document)
    conditions = document.get("conditions")
    if not isinstance(conditions, list):
        raise SharedConsumerError("conditions must be a list")
    timing, decode, overhead = defaultdict(list), defaultdict(list), defaultdict(list)
    seen_conditions, process_ids, policies = set(), set(), []
    for block in conditions:
        condition = _text(block.get("condition"), "condition").upper()
        if condition not in CONDITIONS or condition in seen_conditions:
            raise SharedConsumerError("wrong/duplicate condition")
        seen_conditions.add(condition)
        runs = block.get("runs")
        if not isinstance(runs, list) or len(runs) != EXPECTED_REPS:
            raise SharedConsumerError(f"{condition} requires exactly 7 fresh reps")
        reps = set()
        for run in runs:
            rep = _integer(run.get("rep"), "rep")
            if rep not in range(EXPECTED_REPS) or rep in reps:
                raise SharedConsumerError("missing/duplicate/out-of-range rep")
            reps.add(rep)
            process = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process in process_ids:
                raise SharedConsumerError("fresh process identity reused")
            process_ids.add(process)
            if _sha(run.get("prefix_token_sha256"), "prefix_token_sha256") != prefix:
                raise SharedConsumerError("accepted prefix drift")
            run_tokens = run.get("generated_token_ids")
            if not isinstance(run_tokens, list) or tuple(_integer(x, "token") for x in run_tokens) != tokens:
                raise SharedConsumerError("token sequence drift")
            occurrences = run.get("occurrences")
            if not isinstance(occurrences, list):
                raise SharedConsumerError("occurrences must be a list")
            occurrence_seen = set()
            for raw in occurrences:
                key = (_integer(raw.get("layer_index"), "layer_index"), _text(raw.get("role"), "role"),
                       _integer(raw.get("decode_index"), "decode_index"))
                if key not in authority or key in occurrence_seen:
                    raise SharedConsumerError("wrong/duplicate natural occurrence")
                occurrence_seen.add(key)
                timing[(condition, *key)].append(_occurrence(raw, authority[key]))
            if occurrence_seen != NATURAL_MATRIX:
                raise SharedConsumerError("run does not contain exact 12-occurrence matrix")
            steps = run.get("decode_steps")
            if not isinstance(steps, list) or len(steps) != 4:
                raise SharedConsumerError("decode_steps must contain D0..D3")
            step_seen = set()
            for row in steps:
                d = _integer(row.get("decode_index"), "decode_index")
                if d not in range(4) or d in step_seen or _integer(row.get("generated_token_id"), "token") != tokens[d]:
                    raise SharedConsumerError("decode-step identity mismatch")
                step_seen.add(d)
                decode[(condition, d)].append(_finite(row.get("timing_ms"), "decode timing_ms", positive=True))
            run_regions = _regions(run) if isinstance(run.get("qweight_regions"), Mapping) else document_regions
            if run_regions is None:
                raise SharedConsumerError("run lacks process-local qweight region authority")
            policy = validate_policy_receipt(run.get("policy_receipt"), condition, run_regions)
            policies.append({"condition": condition, "rep": rep, "fresh_process_id": process, "validation": policy})
            for switch in policy["switches"]:
                overhead[condition].append(switch["api_duration_us"])
    if seen_conditions != set(CONDITIONS):
        raise SharedConsumerError("six-condition matrix mismatch")
    timing_rows = [{"condition": key[0], **authority[key[1:]], "statistics": _stats(values)}
                   for key, values in sorted(timing.items())]
    decode_rows = [{"condition": key[0], "decode_index": key[1], "generated_token_id": tokens[key[1]],
                    "statistics": _stats(values)} for key, values in sorted(decode.items())]
    overhead_rows = [{"condition": condition, "statistics": _stats(values, "us")}
                     for condition, values in sorted(overhead.items()) if values]
    return {"status": "PASS", "authority": "RAW_7_FRESH_PROCESS_RUNS_AND_ORDERED_POLICY_RECEIPTS_ONLY",
            "fixed_setaside_bytes": FIXED_SETASIDE_BYTES, "fresh_process_count": len(process_ids),
            "accepted_prefix_sha256": prefix, "generated_token_ids": list(tokens),
            "timing_points": timing_rows, "decode_step_timing": decode_rows,
            "policy_switch_overhead": overhead_rows, "policy_receipts": policies}


def consume_rotating_qualification(document: Mapping[str, Any]) -> dict[str, Any]:
    """Validate the isolated A/B/A rotating qualification and its matched API control."""
    if document.get("schema_version") != 1:
        raise SharedConsumerError("unsupported rotating schema")
    document_regions = (_regions(document, ("L0_UP", "L14_UP"))
                        if isinstance(document.get("qweight_regions"), Mapping) else None)
    blocks = document.get("conditions")
    if not isinstance(blocks, list):
        raise SharedConsumerError("rotating conditions must be a list")
    results, identities, processes = {}, {}, set()
    for block in blocks:
        condition = _text(block.get("condition"), "condition").upper()
        if condition not in {"ROTATING_PERSIST", "ROTATING_CONTROL"} or condition in results:
            raise SharedConsumerError("wrong/duplicate rotating condition")
        runs = block.get("runs")
        if not isinstance(runs, list) or len(runs) != ROTATING_REPS:
            raise SharedConsumerError("rotating condition requires exactly 9 reps")
        reps, samples, overheads, normalized = set(), [], [], []
        for run in runs:
            rep = _integer(run.get("rep"), "rep")
            if rep not in range(ROTATING_REPS) or rep in reps:
                raise SharedConsumerError("rotating missing/duplicate rep")
            reps.add(rep)
            process = _text(run.get("fresh_process_id"), "fresh_process_id")
            if process in processes:
                raise SharedConsumerError("rotating process identity reused")
            processes.add(process)
            pair = (_sha(run.get("input_sha256"), "input_sha256"), _sha(run.get("output_sha256"), "output_sha256"))
            identities.setdefault(condition, pair)
            if identities[condition] != pair:
                raise SharedConsumerError("rotating SHA drift")
            samples.append(_finite(run.get("target_timing_ms"), "target_timing_ms", positive=True))
            run_regions = (_regions(run, ("L0_UP", "L14_UP"))
                           if isinstance(run.get("qweight_regions"), Mapping) else document_regions)
            if run_regions is None:
                raise SharedConsumerError("rotating run lacks process-local A/B region authority")
            policy = validate_policy_receipt(run.get("policy_receipt"), condition, run_regions, rotating=True)
            normalized.append(policy)
            overheads.extend(s["api_duration_us"] for s in policy["switches"])
        results[condition] = {"timing": _stats(samples), "api_switch_overhead": _stats(overheads, "us"),
                              "input_sha256": identities[condition][0], "output_sha256": identities[condition][1],
                              "policy_receipts": normalized}
    if set(results) != {"ROTATING_PERSIST", "ROTATING_CONTROL"} or len(set(identities.values())) != 1:
        raise SharedConsumerError("rotating condition matrix or cross-condition SHA mismatch")
    control = results["ROTATING_CONTROL"]["timing"]["median_ms"]
    persist = results["ROTATING_PERSIST"]["timing"]["median_ms"]
    return {"status": "PASS", "authority": "RAW_9_REP_A_B_A_POLICY_SEQUENCE_ONLY",
            "conditions": results, "persist_vs_control_timing_benefit_fraction": (control - persist) / control}


def _session_options(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text, re.MULTILINE)


def _decimal(value: str, label: str) -> Decimal:
    try:
        result = Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise SharedConsumerError(f"invalid {label}") from exc
    if not result.is_finite() or result < 0:
        raise SharedConsumerError(f"invalid {label}")
    return result


def _read_ncu_base(path: Path, spec: Mapping[str, Any], metrics: Mapping[str, str]) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise SharedConsumerError("NCU BASE is incomplete")
    header, units = table[:2]
    if len(header) != len(set(header)) or len(header) != len(units):
        raise SharedConsumerError("NCU BASE ambiguous header")
    index = {name: i for i, name in enumerate(header)}
    required = {"ID", "Process ID", "Kernel Name", "profiler__replayer_passes", *metrics}
    if required - set(index):
        raise SharedConsumerError("NCU BASE missing required columns")
    ranges = [i for i, name in enumerate(header) if "Push/Pop_Range" in name]
    if len(ranges) != 1:
        raise SharedConsumerError("NCU BASE ambiguous range column")
    for metric, unit in metrics.items():
        if units[index[metric]].strip() != unit:
            raise SharedConsumerError(f"NCU unit mismatch: {metric}")
    pattern = re.compile(r"(?:^|:)" + re.escape(spec["range_name"]) + r"(?=:|/|$)")
    selected = [row for row in table[2:] if len(row) == len(header) and row[index["ID"]].strip()
                and len(pattern.findall(row[ranges[0]].strip())) == 1]
    names = [row[index["Kernel Name"]].strip() for row in selected]
    if not selected or sorted(names) != sorted(spec["expected_kernel_names"]):
        raise SharedConsumerError("NCU exact kernel inventory mismatch")
    ids = [row[index["ID"]].strip() for row in selected]
    if len(ids) != len(set(ids)) or len({row[index["Process ID"]].strip() for row in selected}) != 1:
        raise SharedConsumerError("NCU kernel/process identity ambiguity")
    per_kernel, sums = [], {metric: Decimal(0) for metric in metrics}
    for row in selected:
        if _decimal(row[index["profiler__replayer_passes"]], "replayer passes") != Decimal(spec["expected_pass_count"]):
            raise SharedConsumerError("NCU replay pass mismatch")
        values = {metric: str(_decimal(row[index[metric]], metric)) for metric in metrics}
        for metric, value in values.items():
            sums[metric] += Decimal(value)
        per_kernel.append({"id": row[index["ID"]].strip(), "kernel_name": row[index["Kernel Name"]].strip(),
                           "metrics": values})
    return {"sha256": _sha_file(path), "per_kernel": per_kernel,
            "additive_metric_sums": {metric: str(value) for metric, value in sums.items()}}


def _audit_session(path: Path, spec: Mapping[str, Any], metric_names: set[str]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if set(_session_options(text, "--replay-mode")) != {"application"}:
        raise SharedConsumerError("NCU replay mode mismatch")
    if set(_session_options(text, "--cache-control")) != {"none"}:
        raise SharedConsumerError("NCU cache-control mismatch")
    if {x.rstrip("/") for x in _session_options(text, "--nvtx-include")} != {spec["range_name"]}:
        raise SharedConsumerError("NCU range mismatch")
    raw = set(_session_options(text, "--metrics"))
    if len(raw) != 1 or set(next(iter(raw)).split(",")) != metric_names:
        raise SharedConsumerError("NCU metric set mismatch")
    return {"sha256": _sha_file(path), "replay_mode": "application", "cache_control": "none"}


def _audit_profile(path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    receipts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("status") == "PASS":
            receipts.append(row)
    if len(receipts) != spec["expected_pass_count"]:
        raise SharedConsumerError("PROFILE PASS receipt count does not match replay passes")
    expected = {key: spec[key] for key in ("condition", "target", "decode_index", "range_name",
                                                        "input_sha256", "output_sha256")}
    replay_identity = None
    for row in receipts:
        if isinstance(row.get("occurrences"), list):
            matches = [item for item in row["occurrences"]
                       if item.get("range") == spec["range_name"]]
            occurrence = matches[0] if len(matches) == 1 else {}
            observed = {"condition": row.get("condition"), "target": occurrence.get("target"),
                        "decode_index": occurrence.get("decode_index"), "range_name": occurrence.get("range"),
                        "input_sha256": occurrence.get("input_sha256"), "output_sha256": occurrence.get("output_sha256")}
            transitions = row.get("policy_transitions", [])
            policy_signature = (
                row.get("token_file_sha256"), tuple(row.get("generated_token_ids_D0_D3", [])),
                row.get("policy_transition_count"), row.get("no_reset_between_transitions"),
                tuple((item.get("phase"), item.get("target"), item.get("hit_ratio"),
                       item.get("hit_property"), item.get("miss_property"), item.get("persisting"))
                      for item in transitions),
            )
        else:
            observed = {"condition": row.get("condition"), "target": row.get("target"),
                        "decode_index": row.get("decode_index"), "range_name": row.get("range", row.get("range_name")),
                        "input_sha256": row.get("input_sha256"), "output_sha256": row.get("output_sha256")}
            policy_signature = tuple(sorted(observed.items()))
        if observed != expected:
            raise SharedConsumerError("PROFILE semantic identity mismatch")
        if replay_identity is None:
            replay_identity = policy_signature
        elif replay_identity != policy_signature:
            raise SharedConsumerError("PROFILE replay semantic/token/policy identity mismatch")
    return {"sha256": _sha_file(path), "pass_receipt_count": len(receipts), **expected}


def consume_shared_ncu(document: Mapping[str, Any], root: Path = Path(".")) -> dict[str, Any]:
    """Consume exact 14-point D3 NCU matrix from raw four-source evidence."""
    if document.get("schema_version") != 1:
        raise SharedConsumerError("unsupported shared NCU schema")
    document_regions = _regions(document) if isinstance(document.get("qweight_regions"), Mapping) else None
    metric_rows = document.get("metrics")
    if not isinstance(metric_rows, list) or not metric_rows:
        raise SharedConsumerError("metrics contract must be nonempty")
    metrics = {}
    session_metric_names = set()
    for row in metric_rows:
        name, unit = _text(row.get("name"), "metric.name"), _text(row.get("unit"), "metric.unit")
        if name in session_metric_names:
            raise SharedConsumerError("semantic NCU metric contract contains a duplicate")
        session_metric_names.add(name)
        if _boolean(row.get("additive"), "metric.additive"):
            metrics[name] = unit
    if not set(BASE_METRICS).issubset(metrics):
        raise SharedConsumerError("semantic NCU missing required base metrics")
    profiles = document.get("profiles")
    if not isinstance(profiles, list) or len(profiles) != len(NCU_MATRIX):
        raise SharedConsumerError("shared NCU must contain exactly 14 profiles")
    seen, output = set(), []
    for raw in profiles:
        condition = _text(raw.get("condition"), "condition").upper()
        target = _text(raw.get("target"), "target").upper()
        key = (condition, target)
        if key not in NCU_MATRIX or key in seen:
            raise SharedConsumerError("wrong/duplicate shared NCU point")
        seen.add(key)
        if _integer(raw.get("decode_index"), "decode_index") != 3:
            raise SharedConsumerError("shared NCU target is not D3")
        spec = {"condition": condition, "target": target, "decode_index": 3,
                "range_name": _text(raw.get("range_name"), "range_name"),
                "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
                "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
                "expected_kernel_names": raw.get("expected_kernel_names"),
                "expected_pass_count": _integer(raw.get("expected_pass_count"), "expected_pass_count", 1)}
        if not isinstance(spec["expected_kernel_names"], list) or not spec["expected_kernel_names"] or len(spec["expected_kernel_names"]) != len(set(spec["expected_kernel_names"])):
            raise SharedConsumerError("invalid expected kernel inventory")
        paths = {kind: root / _text(raw.get(f"{kind}_path"), f"{kind}_path")
                 for kind in ("base", "session", "profile", "policy_receipt")}
        if not all(path.is_file() for path in paths.values()):
            raise SharedConsumerError("missing raw NCU evidence")
        policy_raw = json.loads(paths["policy_receipt"].read_text(encoding="utf-8"))
        profile_regions = (_regions(raw) if isinstance(raw.get("qweight_regions"), Mapping)
                           else document_regions)
        if profile_regions is None:
            raise SharedConsumerError("NCU profile lacks process-local qweight region authority")
        policy = validate_policy_receipt(policy_raw, condition, profile_regions)
        output.append({"condition": condition, "target": target, "decode_index": 3,
                       "range_name": spec["range_name"], "input_sha256": spec["input_sha256"],
                       "output_sha256": spec["output_sha256"],
                       "session": _audit_session(paths["session"], spec, session_metric_names),
                       "profile": _audit_profile(paths["profile"], spec),
                       "base": _read_ncu_base(paths["base"], spec, metrics),
                       "policy": policy, "policy_receipt_sha256": _sha_file(paths["policy_receipt"])})
    if seen != NCU_MATRIX:
        raise SharedConsumerError("shared NCU matrix mismatch")
    return {"status": "PASS", "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_ORDERED_POLICY_RECEIPT_ONLY",
            "profile_count": len(output), "metrics": metric_rows,
            "nonadditive_metrics_delegated_to_critical_path_consumer": sorted(session_metric_names-set(metrics)),
            "profiles": output}


def analyze_shared_policy(native: Mapping[str, Any], ncu: Mapping[str, Any]) -> dict[str, Any]:
    """Independently compute local/decode/API and additive NCU effects."""
    timing = {(row["condition"], row["layer_index"], row["role"], row["decode_index"]): row["statistics"]
              for row in native.get("timing_points", [])}
    decode = {(row["condition"], row["decode_index"]): row["statistics"]
              for row in native.get("decode_step_timing", [])}
    if len(timing) != len(native.get("timing_points", [])) or len(decode) != len(native.get("decode_step_timing", [])):
        raise SharedConsumerError("duplicate native analysis point")
    local = []
    selected = {"SINGLE_L0_UP": ("L0_UP",), "SHARE2_UP": ("L0_UP", "L14_UP"),
                "SHARE2_L0": ("L0_UP", "L0_DOWN"), "SHARE3": TARGETS}
    material_by_condition = defaultdict(int)
    for condition, targets in selected.items():
        for target in targets:
            layer, role = TARGET_KEY[target]
            ref, got = timing[("ROTATE_CONTROL_3", layer, role, 3)], timing[(condition, layer, role, 3)]
            benefit = (ref["median_ms"] - got["median_ms"]) / ref["median_ms"]
            dispersion = math.hypot(ref["cv"], got["cv"])
            material = benefit >= 0.05 and benefit > dispersion
            material_by_condition[condition] += int(material)
            local.append({"condition": condition, "target": target, "decode_index": 3,
                          "timing_benefit_fraction": benefit, "combined_dispersion": dispersion,
                          "MATERIAL_LOCAL_TIMING_BENEFIT": material})
    decode_effects = []
    decode_material = {}
    for condition in selected:
        flags = []
        for d in (1, 2, 3):
            ref, got = decode[("ROTATE_CONTROL_3", d)], decode[(condition, d)]
            benefit = (ref["median_ms"] - got["median_ms"]) / ref["median_ms"]
            dispersion = math.hypot(ref["cv"], got["cv"])
            material = benefit >= 0.02 and benefit > dispersion
            flags.append(material)
            decode_effects.append({"condition": condition, "decode_index": d,
                                   "absolute_change_ms": got["median_ms"] - ref["median_ms"],
                                   "benefit_fraction": benefit, "combined_dispersion": dispersion,
                                   "MATERIAL_DECODE_BENEFIT": material})
        decode_material[condition] = all(flags)
    ncu_map = {(row["condition"], row["target"]): row for row in ncu.get("profiles", [])}
    ncu_effects = []
    for condition, targets in selected.items():
        for target in targets:
            ref, got = ncu_map[("ROTATE_CONTROL_3", target)], ncu_map[(condition, target)]
            effects = {}
            for metric in ref["base"]["additive_metric_sums"]:
                a = Decimal(ref["base"]["additive_metric_sums"][metric])
                b = Decimal(got["base"]["additive_metric_sums"][metric])
                effects[metric] = {"absolute_change": str(b - a),
                                   "benefit_fraction": None if a == 0 else float((a - b) / a)}
            ncu_effects.append({"condition": condition, "target": target, "effects_vs_rotate_control": effects})
    multi = {condition: count >= 2 for condition, count in material_by_condition.items()}
    any_multi = any(multi.values())
    any_decode = any(decode_material.values())
    if any_multi and any_decode:
        decision = "SHARED_RESIDENCY_END_TO_END_SUPPORTED"
    elif any_multi:
        decision = "SHARED_RESIDENCY_LOCAL_ONLY"
    elif any(material_by_condition.values()):
        decision = "SHARED_RESIDENCY_SINGLE_TARGET_ONLY"
    else:
        decision = "SHARED_RESIDENCY_NOT_SUPPORTED"
    return {"status": "PASS", "reference": "ROTATE_CONTROL_3", "local_effects": local,
            "decode_effects": decode_effects, "ncu_effects": ncu_effects,
            "MULTI_TARGET_RETAINED": multi, "MATERIAL_DECODE_BENEFIT": decode_material,
            "policy_switch_overhead": native.get("policy_switch_overhead", []),
            "stage_decision": decision}
