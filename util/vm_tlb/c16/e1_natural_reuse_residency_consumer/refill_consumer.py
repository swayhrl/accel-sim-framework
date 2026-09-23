#!/usr/bin/env python3
"""Independent, fail-closed consumer for E1 refill timing and raw NCU evidence.

The consumer never reads a producer summary.  Timing is recomputed from raw
per-repetition rows.  NCU values are accepted only after the BASE CSV, SESSION
command transcript, and PROFILE replay receipt agree on one semantic identity.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


class RefillConsumerError(ValueError):
    """Raw refill evidence is missing, ambiguous, or violates the contract."""


DOMAIN = "TEXT"
M_VALUE = 1
ROLES = ("q_proj", "down_proj", "up_proj")
IMPLEMENTATIONS = ("RAW_FP16", "AWQ_FP16_INPUT")
CALL_INDICES = (1, 2, 3, 4, 5, 6)
NCU_CALL_INDICES = (1, 2, 4)
EXPECTED_REPS = 9
METRICS = ("l1tex__t_bytes.sum", "lts__t_bytes.sum", "dram__bytes.sum")
METRIC_UNIT = "byte"
HEX64 = re.compile(r"^[0-9a-f]{64}$")

TIMING_POINTS = frozenset(
    (DOMAIN, role, M_VALUE, implementation)
    for role in ROLES
    for implementation in IMPLEMENTATIONS
)
NCU_POINTS = frozenset(
    (DOMAIN, role, M_VALUE, implementation, call_index)
    for role in ROLES
    for implementation in IMPLEMENTATIONS
    for call_index in NCU_CALL_INDICES
)


def _first(row: Mapping[str, Any], names: Sequence[str], field: str) -> Any:
    present = [name for name in names if name in row and str(row[name]).strip()]
    if not present:
        raise RefillConsumerError(f"missing field: {field}")
    values = {str(row[name]).strip() for name in present}
    if len(values) != 1:
        raise RefillConsumerError(f"ambiguous aliases for {field}: {present}")
    return row[present[0]]


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RefillConsumerError(f"missing or empty field: {field}")
    return value.strip()


def _canonical_int(value: Any, field: str, *, positive: bool = False) -> int:
    if isinstance(value, bool):
        raise RefillConsumerError(f"{field} must be an integer")
    raw = str(value).strip()
    try:
        parsed = int(raw)
    except (TypeError, ValueError) as exc:
        raise RefillConsumerError(f"{field} must be an integer") from exc
    if raw != str(parsed) or (positive and parsed <= 0):
        raise RefillConsumerError(f"{field} must be a canonical integer")
    return parsed


def _call_index(value: Any) -> int:
    raw = str(value).strip().upper()
    if raw.startswith("K"):
        raw = raw[1:]
    parsed = _canonical_int(raw, "refill_call_index", positive=True)
    if parsed not in CALL_INDICES:
        raise RefillConsumerError(f"unsupported refill_call_index: K{parsed}")
    return parsed


def _sha(value: Any, field: str) -> str:
    parsed = _text(str(value), field).lower()
    if not HEX64.fullmatch(parsed):
        raise RefillConsumerError(f"{field} must be a lowercase SHA256")
    return parsed


def _positive_finite(value: Any, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RefillConsumerError(f"{field} must be numeric") from exc
    if not math.isfinite(parsed) or parsed <= 0:
        raise RefillConsumerError(f"{field} must be positive and finite")
    return parsed


def _point_from_row(row: Mapping[str, Any]) -> tuple[str, str, int, str]:
    domain = str(_first(row, ("domain", "workload"), "domain")).strip().upper()
    role = str(_first(row, ("role", "operator_role"), "role")).strip()
    matrix_m = _canonical_int(_first(row, ("M", "m"), "M"), "M", positive=True)
    implementation = str(
        _first(row, ("implementation", "impl"), "implementation")
    ).strip()
    return domain, role, matrix_m, implementation


def _stats(samples: Sequence[tuple[int, float]]) -> dict[str, Any]:
    values = [value for _, value in sorted(samples)]
    mean = statistics.fmean(values)
    return {
        "sample_count": len(values),
        "samples_ms": values,
        "min_ms": min(values),
        "median_ms": statistics.median(values),
        "max_ms": max(values),
        "mean_ms": mean,
        "cv": statistics.pstdev(values) / mean,
    }


def analyze_timing_rows(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_reps: int = EXPECTED_REPS,
    expected_points: frozenset[tuple[str, str, int, str]] = TIMING_POINTS,
) -> dict[str, Any]:
    """Validate and summarize the complete raw K1..K6 timing matrix."""
    if expected_reps <= 0:
        raise RefillConsumerError("expected_reps must be positive")
    grouped: dict[tuple[str, str, int, str], dict[int, list[tuple[int, float]]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    point_shas: dict[tuple[str, str, int, str], tuple[str, str]] = {}
    semantic_input_shas: dict[tuple[str, str, int], str] = {}
    seen: set[tuple[str, str, int, str, int, int]] = set()
    row_count = 0

    for row in rows:
        row_count += 1
        point = _point_from_row(row)
        call_index = _call_index(
            _first(row, ("refill_call_index", "call_index", "K"), "refill_call_index")
        )
        rep = _canonical_int(_first(row, ("rep", "repetition"), "rep"), "rep")
        if rep < 0:
            raise RefillConsumerError("rep must be nonnegative")
        identity = (*point, call_index, rep)
        if identity in seen:
            raise RefillConsumerError(f"duplicate point/K/rep: {identity!r}")
        seen.add(identity)
        timing_ms = _positive_finite(
            _first(row, ("timing_ms", "target_ms", "elapsed_ms"), "timing_ms"),
            "timing_ms",
        )
        input_sha = _sha(
            _first(row, ("input_sha256", "target_input_sha256"), "input_sha256"),
            "input_sha256",
        )
        output_sha = _sha(
            _first(row, ("output_sha256", "target_output_sha256"), "output_sha256"),
            "output_sha256",
        )
        pair = (input_sha, output_sha)
        if point in point_shas and point_shas[point] != pair:
            raise RefillConsumerError(f"input/output SHA drift within point: {point!r}")
        point_shas[point] = pair
        semantic_point = point[:3]
        if semantic_point in semantic_input_shas and semantic_input_shas[semantic_point] != input_sha:
            raise RefillConsumerError(
                f"input SHA drift across implementations: {semantic_point!r}"
            )
        semantic_input_shas[semantic_point] = input_sha
        grouped[point][call_index].append((rep, timing_ms))

    if row_count == 0:
        raise RefillConsumerError("empty timing evidence")
    if set(grouped) != set(expected_points):
        missing = sorted(set(expected_points) - set(grouped))
        extra = sorted(set(grouped) - set(expected_points))
        raise RefillConsumerError(f"timing point matrix mismatch: missing={missing}, extra={extra}")

    analyses = []
    allowed_rep_sets = {frozenset(range(expected_reps)), frozenset(range(1, expected_reps + 1))}
    for point in sorted(grouped):
        by_call = grouped[point]
        if set(by_call) != set(CALL_INDICES):
            missing = sorted(set(CALL_INDICES) - set(by_call))
            extra = sorted(set(by_call) - set(CALL_INDICES))
            raise RefillConsumerError(
                f"K matrix mismatch for {point!r}: missing={missing}, extra={extra}"
            )
        rep_sets = []
        call_stats: dict[int, dict[str, Any]] = {}
        for call_index in CALL_INDICES:
            samples = by_call[call_index]
            rep_set = frozenset(rep for rep, _ in samples)
            if len(samples) != expected_reps or rep_set not in allowed_rep_sets:
                raise RefillConsumerError(
                    f"rep matrix mismatch for {point!r}/K{call_index}: {sorted(rep_set)}"
                )
            rep_sets.append(rep_set)
            call_stats[call_index] = _stats(samples)
        if len(set(rep_sets)) != 1:
            raise RefillConsumerError(f"rep indexing drift across K calls: {point!r}")

        k1 = call_stats[1]["median_ms"]
        ratios = {f"K{k}": call_stats[k]["median_ms"] / k1 for k in CALL_INDICES}
        medians = [call_stats[k]["median_ms"] for k in CALL_INDICES]
        violations = [
            {"from": f"K{k}", "to": f"K{k + 1}", "delta_ms": medians[k] - medians[k - 1]}
            for k in range(1, len(medians))
            if medians[k] > medians[k - 1]
        ]
        analyses.append(
            {
                "semantic_identity": {
                    "domain": point[0],
                    "role": point[1],
                    "M": point[2],
                    "implementation": point[3],
                },
                "input_sha256": point_shas[point][0],
                "output_sha256": point_shas[point][1],
                "call_statistics": {f"K{k}": call_stats[k] for k in CALL_INDICES},
                "timing_ratios_over_K1": ratios,
                "K1_to_K6_fractional_recovery": (k1 - call_stats[6]["median_ms"]) / k1,
                "monotonicity_diagnostic": {
                    "is_nonincreasing": not violations,
                    "nonincreasing_transition_count": 5 - len(violations),
                    "violation_count": len(violations),
                    "violations": violations,
                    "is_pass_gate": False,
                },
            }
        )

    return {
        "status": "PASS",
        "authority": "RAW_PER_REPETITION_TIMING_ROWS_ONLY",
        "expected_repetitions": expected_reps,
        "expected_calls": [f"K{k}" for k in CALL_INDICES],
        "points": analyses,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decimal(value: str, field: str) -> Decimal:
    try:
        parsed = Decimal(value.replace(",", "").strip())
    except (InvalidOperation, AttributeError) as exc:
        raise RefillConsumerError(f"invalid metric value: {field}={value!r}") from exc
    if not parsed.is_finite() or parsed < 0:
        raise RefillConsumerError(f"nonfinite/negative metric value: {field}")
    return parsed


def _canon_decimal(value: Decimal) -> str:
    return str(value.to_integral_value()) if value == value.to_integral_value() else str(value)


def _list(value: Any, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise RefillConsumerError(f"{field} must be a list")
    result = [_text(item, field) for item in value]
    if not allow_empty and not result:
        raise RefillConsumerError(f"{field} must not be empty")
    if len(result) != len(set(result)):
        raise RefillConsumerError(f"{field} contains duplicates")
    return result


def _parse_ncu_spec(raw: Mapping[str, Any], root: Path) -> dict[str, Any]:
    point = _text(raw.get("point"), "point")
    domain = _text(raw.get("domain"), "domain").upper()
    role = _text(raw.get("role"), "role")
    matrix_m = _canonical_int(raw.get("M"), "M", positive=True)
    implementation = _text(raw.get("implementation"), "implementation")
    call_index = _call_index(raw.get("refill_call_index"))
    identity = (domain, role, matrix_m, implementation, call_index)
    expected_names = _list(raw.get("expected_kernel_names"), "expected_kernel_names")
    pressure_names = _list(
        raw.get("pressure_kernel_names", []), "pressure_kernel_names", allow_empty=True
    )
    if set(expected_names) & set(pressure_names):
        raise RefillConsumerError("target and pressure kernel inventories overlap")
    paths = {}
    for kind in ("base", "session", "profile"):
        path = root / _text(raw.get(f"{kind}_path"), f"{kind}_path")
        if not path.is_file():
            raise RefillConsumerError(f"missing raw {kind.upper()} evidence: {path}")
        paths[kind] = path
    parsed = {
        "point": point,
        "domain": domain,
        "role": role,
        "M": matrix_m,
        "implementation": implementation,
        "refill_call_index": call_index,
        "range_name": _text(raw.get("range_name"), "range_name"),
        "input_sha256": _sha(raw.get("input_sha256"), "input_sha256"),
        "output_sha256": _sha(raw.get("output_sha256"), "output_sha256"),
        "expected_pass_count": _canonical_int(
            raw.get("expected_pass_count"), "expected_pass_count", positive=True
        ),
        "expected_kernel_names": expected_names,
        "pressure_kernel_names": pressure_names,
        **{f"{kind}_path": path for kind, path in paths.items()},
    }
    if identity not in NCU_POINTS:
        raise RefillConsumerError(f"unsupported refill NCU point: {identity!r}")
    return parsed


def _session_option(text: str, option: str) -> list[str]:
    return re.findall(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", text, re.MULTILINE)


def _audit_session(path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="strict")
    if not text.strip():
        raise RefillConsumerError("empty SESSION evidence")
    replay = set(_session_option(text, "--replay-mode"))
    cache = set(_session_option(text, "--cache-control"))
    ranges = {item.rstrip("/") for item in _session_option(text, "--nvtx-include")}
    metric_lists = set(_session_option(text, "--metrics"))
    if replay != {"application"}:
        raise RefillConsumerError(f"SESSION replay mode mismatch: {sorted(replay)}")
    if cache != {"none"}:
        raise RefillConsumerError(f"SESSION cache control mismatch: {sorted(cache)}")
    if ranges != {spec["range_name"]}:
        raise RefillConsumerError(f"SESSION exact target range mismatch: {sorted(ranges)}")
    if len(metric_lists) != 1:
        raise RefillConsumerError("SESSION has missing or ambiguous --metrics")
    requested = next(iter(metric_lists)).split(",")
    if len(requested) != len(set(requested)) or set(requested) != set(METRICS):
        raise RefillConsumerError(f"SESSION metric set mismatch: {requested}")
    return {
        "sha256": _sha256(path),
        "replay_mode": "application",
        "cache_control": "none",
        "nvtx_range": spec["range_name"],
        "metrics": list(METRICS),
    }


def _audit_profile(path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="strict")
    receipts = []
    for line in text.splitlines():
        try:
            value = json.loads(line.strip())
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(value, dict) and value.get("status") == "PASS":
            receipts.append(value)
    if len(receipts) != 1:
        raise RefillConsumerError(
            f"PROFILE must contain exactly one PASS replay receipt, got {len(receipts)}"
        )
    receipt = receipts[0]
    expected = {
        "role": spec["role"],
        "M": spec["M"],
        "implementation": spec["implementation"],
        "range": spec["range_name"],
        "input_sha256": spec["input_sha256"],
        "output_sha256": spec["output_sha256"],
    }
    mismatches = {
        key: {"expected": expected_value, "observed": receipt.get(key)}
        for key, expected_value in expected.items()
        if receipt.get(key) != expected_value
    }
    raw_call = receipt.get("refill_call_index", receipt.get("selected_k"))
    if receipt.get("refill_call_index") is not None and receipt.get("selected_k") is not None and receipt.get("refill_call_index") != receipt.get("selected_k"):
        mismatches["refill_call_aliases"] = {
            "refill_call_index": receipt.get("refill_call_index"),
            "selected_k": receipt.get("selected_k"),
        }
    try:
        observed_call = _call_index(raw_call)
    except RefillConsumerError:
        observed_call = None
    if observed_call != spec["refill_call_index"]:
        mismatches["refill_call_index"] = {
            "expected": spec["refill_call_index"],
            "observed": raw_call,
        }
    if mismatches:
        raise RefillConsumerError(
            "PROFILE replay identity mismatch: " + json.dumps(mismatches, sort_keys=True)
        )
    return {"sha256": _sha256(path), "status": "PASS", **expected, "refill_call_index": observed_call}


def _nvtx_exact(cell: str, target: str) -> bool:
    pattern = re.compile(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)")
    return len(pattern.findall(cell.strip())) == 1


def _read_base(path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise RefillConsumerError("raw BASE CSV is missing header/unit/data rows")
    header, units = table[0], table[1]
    if not header or len(header) != len(set(header)):
        raise RefillConsumerError("raw BASE has empty or duplicate header names")
    if len(units) != len(header):
        raise RefillConsumerError("raw BASE unit row width mismatch")
    index = {name: i for i, name in enumerate(header)}
    required = {
        "ID", "Process ID", "Kernel Name", "profiler__replayer_passes", *METRICS
    }
    missing = required - set(index)
    if missing:
        raise RefillConsumerError("raw BASE missing required columns: " + ",".join(sorted(missing)))
    range_columns = [i for i, name in enumerate(header) if "Push/Pop_Range" in name]
    if len(range_columns) != 1:
        raise RefillConsumerError("raw BASE has missing or ambiguous NVTX Push/Pop_Range column")
    for metric in METRICS:
        if units[index[metric]].strip() != METRIC_UNIT:
            raise RefillConsumerError(f"raw BASE unit mismatch for {metric}: {units[index[metric]]!r}")

    candidates: list[tuple[int, list[str]]] = []
    for row_number, row in enumerate(table[2:], start=3):
        if len(row) != len(header):
            if any(cell.strip() for cell in row):
                raise RefillConsumerError(f"raw BASE malformed row width at row {row_number}")
            continue
        if row[index["ID"]].strip() and _nvtx_exact(row[range_columns[0]], spec["range_name"]):
            candidates.append((row_number, row))
    if not candidates:
        raise RefillConsumerError("raw BASE contains no exact target semantic range")
    processes = {row[index["Process ID"]].strip() for _, row in candidates}
    if "" in processes or len(processes) != 1:
        raise RefillConsumerError("raw BASE target range has ambiguous process identity")
    names_by_id: dict[str, str] = {}
    totals = {metric: Decimal(0) for metric in METRICS}
    source_rows = []
    for row_number, row in candidates:
        kernel_id = row[index["ID"]].strip()
        kernel_name = row[index["Kernel Name"]].strip()
        if not kernel_id or not kernel_name or kernel_id in names_by_id:
            raise RefillConsumerError(f"empty or duplicate raw target kernel ID: {kernel_id!r}")
        names_by_id[kernel_id] = kernel_name
        passes = _decimal(row[index["profiler__replayer_passes"]], "profiler__replayer_passes")
        if passes != Decimal(spec["expected_pass_count"]):
            raise RefillConsumerError(f"replay pass mismatch for kernel {kernel_id}")
        values = {}
        for metric in METRICS:
            value = _decimal(row[index[metric]], metric)
            totals[metric] += value
            values[metric] = _canon_decimal(value)
        source_rows.append({"row": row_number, "kernel_id": kernel_id, "kernel_name": kernel_name, "metrics": values})
    observed_names = set(names_by_id.values())
    pressure_inside = observed_names & set(spec["pressure_kernel_names"])
    if pressure_inside:
        raise RefillConsumerError(
            "pressure kernel entered target semantic range: " + ",".join(sorted(pressure_inside))
        )
    expected_names = set(spec["expected_kernel_names"])
    if observed_names != expected_names or len(names_by_id) != len(spec["expected_kernel_names"]):
        raise RefillConsumerError(
            f"target kernel inventory mismatch: expected={sorted(expected_names)!r} observed={sorted(observed_names)!r}"
        )
    return {
        "base_sha256": _sha256(path),
        "selected_process_id": next(iter(processes)),
        "kernel_names": [names_by_id[key] for key in sorted(names_by_id)],
        "metric_sums": {metric: _canon_decimal(value) for metric, value in totals.items()},
        "metric_unit": METRIC_UNIT,
        "source_rows": source_rows,
    }


def consume_ncu(
    document: Mapping[str, Any],
    root: Path = Path("."),
    *,
    expected_points: frozenset[tuple[str, str, int, str, int]] = NCU_POINTS,
) -> dict[str, Any]:
    """Consume the exact K1/K2/K4 BASE+SESSION+PROFILE matrix."""
    if document.get("schema_version") != 1:
        raise RefillConsumerError("unsupported NCU point-spec schema_version")
    raw_profiles = document.get("profiles")
    if not isinstance(raw_profiles, list) or not raw_profiles:
        raise RefillConsumerError("NCU point-spec requires a non-empty profiles list")
    specs = [_parse_ncu_spec(raw, root) for raw in raw_profiles]
    identities = [
        (spec["domain"], spec["role"], spec["M"], spec["implementation"], spec["refill_call_index"])
        for spec in specs
    ]
    if len(identities) != len(set(identities)):
        raise RefillConsumerError("duplicate semantic refill_call_index identity")
    if set(identities) != set(expected_points):
        missing = sorted(set(expected_points) - set(identities))
        extra = sorted(set(identities) - set(expected_points))
        raise RefillConsumerError(f"NCU point matrix mismatch: missing={missing}, extra={extra}")

    profiles = []
    point_shas: dict[tuple[str, str, int, str], tuple[str, str]] = {}
    for spec in specs:
        point = (spec["domain"], spec["role"], spec["M"], spec["implementation"])
        pair = (spec["input_sha256"], spec["output_sha256"])
        if point in point_shas and point_shas[point] != pair:
            raise RefillConsumerError(f"NCU input/output SHA drift across calls: {point!r}")
        point_shas[point] = pair
        session = _audit_session(spec["session_path"], spec)
        profile = _audit_profile(spec["profile_path"], spec)
        base = _read_base(spec["base_path"], spec)
        profiles.append(
            {
                "semantic_identity": {
                    "point": spec["point"],
                    "domain": spec["domain"],
                    "role": spec["role"],
                    "M": spec["M"],
                    "implementation": spec["implementation"],
                    "refill_call_index": spec["refill_call_index"],
                },
                "range_name": spec["range_name"],
                "input_sha256": spec["input_sha256"],
                "output_sha256": spec["output_sha256"],
                "session": session,
                "profile_log": profile,
                **base,
            }
        )

    by_point: dict[tuple[str, str, int, str], dict[int, dict[str, Any]]] = defaultdict(dict)
    for profile in profiles:
        identity = profile["semantic_identity"]
        key = (identity["domain"], identity["role"], identity["M"], identity["implementation"])
        by_point[key][identity["refill_call_index"]] = profile
    call_ratios = []
    for key, calls in sorted(by_point.items()):
        if not set(NCU_CALL_INDICES).issubset(calls):
            continue
        for call_index in (2, 4):
            for metric in METRICS:
                baseline = Decimal(calls[1]["metric_sums"][metric])
                value = Decimal(calls[call_index]["metric_sums"][metric])
                ratio = None if baseline == 0 else float(value / baseline)
                call_ratios.append(
                    {
                        "domain": key[0], "role": key[1], "M": key[2],
                        "implementation": key[3], "refill_call_index": call_index,
                        "metric_name": metric, "Ki_over_K1": ratio,
                        "ratio_status": "PASS" if ratio is not None else "UNDEFINED_ZERO_DENOMINATOR",
                    }
                )

    by_role_call: dict[tuple[str, str, int, int], dict[str, dict[str, Any]]] = defaultdict(dict)
    for profile in profiles:
        identity = profile["semantic_identity"]
        key = (identity["domain"], identity["role"], identity["M"], identity["refill_call_index"])
        by_role_call[key][identity["implementation"]] = profile
    implementation_ratios = []
    for key, implementations in sorted(by_role_call.items()):
        if not set(IMPLEMENTATIONS).issubset(implementations):
            continue
        for metric in METRICS:
            raw = Decimal(implementations["RAW_FP16"]["metric_sums"][metric])
            awq = Decimal(implementations["AWQ_FP16_INPUT"]["metric_sums"][metric])
            ratio = None if raw == 0 else float(awq / raw)
            implementation_ratios.append(
                {
                    "domain": key[0], "role": key[1], "M": key[2],
                    "refill_call_index": key[3], "metric_name": metric,
                    "AWQ_over_RAW": ratio,
                    "ratio_status": "PASS" if ratio is not None else "UNDEFINED_ZERO_DENOMINATOR",
                }
            )
    return {
        "status": "PASS",
        "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY",
        "semantic_identity_fields": [
            "point", "domain", "role", "M", "implementation", "refill_call_index"
        ],
        "profiles": profiles,
        "call_ratios": call_ratios,
        "implementation_ratios": implementation_ratios,
    }


def _read_dict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise RefillConsumerError("timing CSV has missing or duplicate headers")
        return list(reader)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timing-csv", type=Path)
    parser.add_argument("--ncu-spec", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if (args.timing_csv is None) == (args.ncu_spec is None):
        parser.error("exactly one of --timing-csv or --ncu-spec is required")
    if args.timing_csv:
        result = analyze_timing_rows(_read_dict_rows(args.timing_csv))
    else:
        document = json.loads(args.ncu_spec.read_text(encoding="utf-8"))
        result = consume_ncu(document, args.ncu_spec.parent)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS"}, sort_keys=True))


if __name__ == "__main__":
    main()
