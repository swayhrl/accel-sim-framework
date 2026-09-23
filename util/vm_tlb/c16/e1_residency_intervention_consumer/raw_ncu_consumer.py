#!/usr/bin/env python3
"""Fail-closed consumer for residency-intervention raw NCU BASE/SESSION/PROFILE evidence.

The producer's semantic summary is deliberately not an input. Each profile is
bound by a consumer-owned point specification to one raw wide NCU CSV, its raw
session transcript, and the raw profiler log that carries the replay identity
receipt. Intervention state is part of the semantic identity.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "e1_semantic_ncu_consumer"))
from aggregator import AggregationError, aggregate  # noqa: E402


class RawNcuError(ValueError):
    """Raw evidence is absent, ambiguous, or violates the frozen contract."""


METRICS = (
    "l1tex__t_bytes.sum",
    "lts__t_bytes.sum",
    "dram__bytes.sum",
)
METRIC_UNIT = "byte"
STATES = (
    "WARM",
    "SPARSE_PAGE_PRESSURE",
    "DENSE_MEMORY_PRESSURE",
)
ROLES = ("q_proj", "down_proj", "up_proj")
IMPLEMENTATIONS = ("RAW_FP16", "AWQ_FP16_INPUT")
POLICY = {
    "additive_metrics": {metric: METRIC_UNIT for metric in METRICS},
    "non_additive_metrics": {},
    "required_denominators": [
        "input_elements",
        "output_elements",
        "dense_weight_bytes",
    ],
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RawNcuError(f"missing or empty point-spec field: {field}")
    return value.strip()


def _positive_int(value: object, field: str) -> int:
    if isinstance(value, bool):
        raise RawNcuError(f"{field} must be a positive integer")
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RawNcuError(f"{field} must be a positive integer") from exc
    if parsed <= 0 or str(parsed) != str(value).strip():
        raise RawNcuError(f"{field} must be a canonical positive integer")
    return parsed


def _hash(value: object, field: str) -> str:
    parsed = _text(value, field).lower()
    if not HEX64.fullmatch(parsed):
        raise RawNcuError(f"{field} must be a lowercase SHA256")
    return parsed


def _string_list(value: object, field: str, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise RawNcuError(f"{field} must be a list")
    parsed = [_text(item, field) for item in value]
    if not allow_empty and not parsed:
        raise RawNcuError(f"{field} must not be empty")
    if len(parsed) != len(set(parsed)):
        raise RawNcuError(f"{field} contains duplicates")
    return parsed


def _decimal(value: str, field: str) -> Decimal:
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        raise RawNcuError(f"missing metric value: {field}")
    try:
        parsed = Decimal(cleaned)
    except InvalidOperation as exc:
        raise RawNcuError(f"invalid metric value: {field}={value!r}") from exc
    if not parsed.is_finite():
        raise RawNcuError(f"non-finite metric value: {field}")
    return parsed


def _canonical_decimal(value: Decimal) -> str:
    return str(value.to_integral_value()) if value == value.to_integral_value() else str(value)


def _session_hashes(text: str, key: str) -> set[str]:
    # Accept raw JSON/log spellings such as "input_sha256": "..." and
    # input_sha256=..., while requiring one unambiguous exact digest.
    pattern = re.compile(
        rf"(?i)(?:[\"']?{re.escape(key)}[\"']?)\s*[:=]\s*[\"']?([0-9a-f]{{64}})"
    )
    return {match.group(1).lower() for match in pattern.finditer(text)}


def _session_option(text: str, option: str) -> list[str]:
    pattern = re.compile(rf"(?:^|\s){re.escape(option)}(?:=|\s+)([^\s\"']+)", re.MULTILINE)
    return pattern.findall(text)


def _audit_session(path: Path, spec: dict) -> dict:
    text = path.read_text(encoding="utf-8", errors="strict")
    if not text.strip():
        raise RawNcuError("empty SESSION evidence")

    replay = set(_session_option(text, "--replay-mode"))
    cache = set(_session_option(text, "--cache-control"))
    ranges = {value.rstrip("/") for value in _session_option(text, "--nvtx-include")}
    metric_lists = _session_option(text, "--metrics")
    if replay != {"application"}:
        raise RawNcuError(f"SESSION replay mode is not uniquely application: {sorted(replay)}")
    if cache != {"none"}:
        raise RawNcuError(f"SESSION cache control is not uniquely none: {sorted(cache)}")
    if ranges != {spec["range_name"]}:
        raise RawNcuError(f"SESSION exact target range mismatch: {sorted(ranges)}")
    if len(set(metric_lists)) != 1:
        raise RawNcuError("SESSION has missing or ambiguous --metrics evidence")
    requested = metric_lists[0].split(",")
    if len(requested) != len(set(requested)) or set(requested) != set(METRICS):
        raise RawNcuError(f"SESSION metric set mismatch: {requested}")

    return {
        "sha256": _sha256(path),
        "replay_mode": "application",
        "cache_control": "none",
        "nvtx_range": spec["range_name"],
        "metrics": list(METRICS),
    }


def _audit_profile_log(path: Path, spec: dict) -> dict:
    text = path.read_text(encoding="utf-8", errors="strict")
    if not text.strip():
        raise RawNcuError("empty PROFILE evidence")
    receipts = []
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if value.get("status") == "PASS":
            receipts.append(value)
    if len(receipts) != 1:
        raise RawNcuError(f"PROFILE must contain exactly one PASS replay receipt, got {len(receipts)}")
    receipt = receipts[0]
    expected = {
        "role": spec["role"],
        "M": spec["M"],
        "implementation": spec["implementation"],
        "state": spec["state"],
        "range": spec["range_name"],
        "input_sha256": spec["input_sha256"],
        "output_sha256": spec["output_sha256"],
    }
    mismatches = {
        key: {"expected": exp, "observed": receipt.get(key)}
        for key, exp in expected.items()
        if receipt.get(key) != exp
    }
    if mismatches:
        raise RawNcuError("PROFILE replay identity mismatch: " + json.dumps(mismatches, sort_keys=True))
    return {
        "sha256": _sha256(path),
        "status": "PASS",
        **expected,
    }


def _parse_spec(raw: dict, root: Path) -> dict:
    if not isinstance(raw, dict):
        raise RawNcuError("each profile point-spec must be an object")
    point = _text(raw.get("point"), "point")
    role = _text(raw.get("role"), "role")
    if role not in ROLES:
        raise RawNcuError(f"unsupported role: {role}")
    m_value = _positive_int(raw.get("M"), "M")
    if m_value not in (1, 256):
        raise RawNcuError(f"unsupported M: {m_value}")
    implementation = _text(raw.get("implementation"), "implementation")
    if implementation not in IMPLEMENTATIONS:
        raise RawNcuError(f"unsupported implementation: {implementation}")
    state = _text(raw.get("state"), "state")
    if state not in STATES:
        raise RawNcuError(f"unsupported intervention state: {state}")

    expected_names = _string_list(raw.get("expected_kernel_names"), "expected_kernel_names")
    pressure_names = _string_list(
        raw.get("pressure_kernel_names", []), "pressure_kernel_names", allow_empty=True
    )
    if state != "WARM" and not pressure_names:
        raise RawNcuError("pressure states require pressure_kernel_names authority")
    if set(expected_names) & set(pressure_names):
        raise RawNcuError("target and pressure kernel inventories overlap in point-spec")

    base_path = root / _text(raw.get("base_path"), "base_path")
    session_path = root / _text(raw.get("session_path"), "session_path")
    profile_path = root / _text(raw.get("profile_path"), "profile_path")
    if not base_path.is_file():
        raise RawNcuError(f"missing raw BASE evidence: {base_path}")
    if not session_path.is_file():
        raise RawNcuError(f"missing raw SESSION evidence: {session_path}")
    if not profile_path.is_file():
        raise RawNcuError(f"missing raw PROFILE evidence: {profile_path}")

    parsed = {
        "point": point,
        "role": role,
        "M": m_value,
        "implementation": implementation,
        "state": state,
        "range_name": _text(raw.get("range_name"), "range_name"),
        "input_sha256": _hash(raw.get("input_sha256"), "input_sha256"),
        "output_sha256": _hash(raw.get("output_sha256"), "output_sha256"),
        "expected_pass_count": _positive_int(
            raw.get("expected_pass_count"), "expected_pass_count"
        ),
        "expected_kernel_names": expected_names,
        "pressure_kernel_names": pressure_names,
        "input_elements": _positive_int(raw.get("input_elements"), "input_elements"),
        "output_elements": _positive_int(raw.get("output_elements"), "output_elements"),
        "dense_weight_bytes": _positive_int(
            raw.get("dense_weight_bytes"), "dense_weight_bytes"
        ),
        "packed_weight_bytes": raw.get("packed_weight_bytes"),
        "base_path": base_path,
        "session_path": session_path,
        "profile_path": profile_path,
    }
    if parsed["implementation"] == "AWQ_FP16_INPUT":
        parsed["packed_weight_bytes"] = _positive_int(
            parsed["packed_weight_bytes"], "packed_weight_bytes"
        )
    elif parsed["packed_weight_bytes"] not in (None, ""):
        raise RawNcuError("RAW_FP16 point must not claim packed_weight_bytes")
    else:
        parsed["packed_weight_bytes"] = None
    return parsed


def _nvtx_exact(cell: str, target: str) -> bool:
    # NCU emits a single push/pop range for this qualified selector.  A trailing
    # slash is accepted because that is the selector spelling in SESSION.
    return cell.strip().rstrip("/") == target


def _read_base(spec: dict) -> tuple[list[dict], dict]:
    path = spec["base_path"]
    with path.open(newline="", encoding="utf-8-sig") as stream:
        table = list(csv.reader(stream))
    if len(table) < 3:
        raise RawNcuError("raw BASE CSV is missing header/unit/data rows")
    header, units = table[0], table[1]
    if not header or len(header) != len(set(header)):
        raise RawNcuError("raw BASE CSV has empty or duplicate header names")
    if len(units) != len(header):
        raise RawNcuError("raw BASE unit row width mismatch")
    index = {name: position for position, name in enumerate(header)}
    range_columns = [i for i, name in enumerate(header) if "Push/Pop_Range" in name]
    required = {
        "ID",
        "Process ID",
        "Kernel Name",
        "Block Size",
        "Grid Size",
        "profiler__replayer_passes",
        *METRICS,
    }
    missing = required - set(index)
    if missing:
        raise RawNcuError("raw BASE missing required columns: " + ",".join(sorted(missing)))
    if len(range_columns) != 1:
        raise RawNcuError("raw BASE has missing or ambiguous NVTX Push/Pop_Range column")
    for metric in METRICS:
        if units[index[metric]].strip() != METRIC_UNIT:
            raise RawNcuError(
                f"raw BASE unit mismatch for {metric}: {units[index[metric]]!r}"
            )

    range_column = range_columns[0]
    candidates = []
    for row_number, row in enumerate(table[2:], start=3):
        if len(row) != len(header):
            if any(cell.strip() for cell in row):
                raise RawNcuError(f"raw BASE malformed row width at row {row_number}")
            continue
        if not row[index["ID"]].strip():
            continue
        if _nvtx_exact(row[range_column], spec["range_name"]):
            candidates.append((row_number, row))
    if not candidates:
        raise RawNcuError("raw BASE contains no exact target semantic range")

    processes = {row[index["Process ID"]].strip() for _, row in candidates}
    if "" in processes or len(processes) != 1:
        raise RawNcuError("raw BASE target range has ambiguous process identity")
    names_by_id: dict[str, str] = {}
    normalized = []
    semantic_point = "|".join(
        (
            spec["point"],
            spec["role"],
            f"M{spec['M']}",
            spec["implementation"],
            spec["state"],
        )
    )
    for row_number, row in candidates:
        kernel_id = row[index["ID"]].strip()
        kernel_name = row[index["Kernel Name"]].strip()
        if not kernel_id or not kernel_name:
            raise RawNcuError("raw BASE has empty kernel identity")
        if kernel_id in names_by_id and names_by_id[kernel_id] != kernel_name:
            raise RawNcuError(f"kernel ID maps to multiple names: {kernel_id}")
        if kernel_id in names_by_id:
            raise RawNcuError(f"duplicate raw target kernel ID: {kernel_id}")
        names_by_id[kernel_id] = kernel_name
        passes = _decimal(
            row[index["profiler__replayer_passes"]], "profiler__replayer_passes"
        )
        if passes != Decimal(spec["expected_pass_count"]):
            raise RawNcuError(
                f"replay pass mismatch for kernel {kernel_id}: {passes} != "
                f"{spec['expected_pass_count']}"
            )
        for metric in METRICS:
            value = _decimal(row[index[metric]], metric)
            normalized.append(
                {
                    "semantic_point": semantic_point,
                    "range_name": spec["range_name"],
                    "range_occurrence": "0",
                    "kernel_id": kernel_id,
                    "kernel_name": kernel_name,
                    "metric_name": metric,
                    "metric_unit": METRIC_UNIT,
                    "metric_value": _canonical_decimal(value),
                    "input_elements": str(spec["input_elements"]),
                    "output_elements": str(spec["output_elements"]),
                    "dense_weight_bytes": str(spec["dense_weight_bytes"]),
                    "packed_weight_bytes": (
                        str(spec["packed_weight_bytes"])
                        if spec["packed_weight_bytes"] is not None
                        else ""
                    ),
                    "source_raw_filename": path.name,
                    "source_row_identity": str(row_number),
                    "raw_source_sha256": _sha256(path),
                    "intervention_state": spec["state"],
                    "role": spec["role"],
                    "M": str(spec["M"]),
                    "implementation": spec["implementation"],
                }
            )

    observed_names = set(names_by_id.values())
    expected_names = set(spec["expected_kernel_names"])
    pressure_inside = observed_names & set(spec["pressure_kernel_names"])
    if pressure_inside:
        raise RawNcuError(
            "pressure kernel entered target semantic range: " + ",".join(sorted(pressure_inside))
        )
    if observed_names != expected_names or len(names_by_id) != len(spec["expected_kernel_names"]):
        raise RawNcuError(
            "target kernel inventory mismatch: expected="
            + repr(sorted(expected_names))
            + " observed="
            + repr(sorted(observed_names))
        )

    try:
        aggregated = aggregate(
            normalized, semantic_point, spec["range_name"], POLICY
        )
    except AggregationError as exc:
        raise RawNcuError(f"hardened semantic aggregation failed: {exc}") from exc
    provenance = {
        "base_sha256": _sha256(path),
        "selected_process_id": next(iter(processes)),
        "selected_kernel_count": len(names_by_id),
        "kernel_names": [names_by_id[key] for key in sorted(names_by_id)],
        "metric_units": {metric: METRIC_UNIT for metric in METRICS},
        "expected_pass_count": spec["expected_pass_count"],
    }
    return normalized, {"aggregation": aggregated, "provenance": provenance}


def consume(spec_document: dict, spec_root: Path = Path(".")) -> dict:
    if not isinstance(spec_document, dict):
        raise RawNcuError("point-spec document must be an object")
    if spec_document.get("schema_version") != 1:
        raise RawNcuError("unsupported point-spec schema_version")
    raw_profiles = spec_document.get("profiles")
    if not isinstance(raw_profiles, list) or not raw_profiles:
        raise RawNcuError("point-spec requires a non-empty profiles list")
    specs = [_parse_spec(raw, spec_root) for raw in raw_profiles]

    identities = []
    for spec in specs:
        identity = (
            spec["point"],
            spec["role"],
            spec["M"],
            spec["implementation"],
            spec["state"],
        )
        if identity in identities:
            raise RawNcuError(f"duplicate semantic intervention state: {identity}")
        identities.append(identity)

    profiles = []
    normalized_rows = []
    for spec in specs:
        session = _audit_session(spec["session_path"], spec)
        profile_log = _audit_profile_log(spec["profile_path"], spec)
        rows, base = _read_base(spec)
        normalized_rows.extend(rows)
        profiles.append(
            {
                "semantic_identity": {
                    "point": spec["point"],
                    "role": spec["role"],
                    "M": spec["M"],
                    "implementation": spec["implementation"],
                    "state": spec["state"],
                },
                "range_name": spec["range_name"],
                "input_sha256": spec["input_sha256"],
                "output_sha256": spec["output_sha256"],
                "session": session,
                "profile_log": profile_log,
                **base,
            }
        )

    grouped: dict[tuple, dict[str, dict]] = defaultdict(dict)
    for profile in profiles:
        identity = profile["semantic_identity"]
        key = (
            identity["point"],
            identity["role"],
            identity["M"],
            identity["implementation"],
        )
        grouped[key][identity["state"]] = profile

    ratios = []
    for key, states in sorted(grouped.items()):
        if "WARM" not in states:
            raise RawNcuError(f"state-ratio group is missing WARM authority: {key}")
        for state in ("SPARSE_PAGE_PRESSURE", "DENSE_MEMORY_PRESSURE"):
            if state not in states:
                continue
            for metric in METRICS:
                warm = Decimal(
                    states["WARM"]["aggregation"]["SEMANTIC_MODULE_SUM"][metric][
                        "value_exact"
                    ]
                )
                pressure = Decimal(
                    states[state]["aggregation"]["SEMANTIC_MODULE_SUM"][metric][
                        "value_exact"
                    ]
                )
                ratio = None if warm == 0 else float(pressure / warm)
                ratios.append(
                    {
                        "point": key[0],
                        "role": key[1],
                        "M": key[2],
                        "implementation": key[3],
                        "state": state,
                        "metric_name": metric,
                        "unit": METRIC_UNIT,
                        "pressure_over_warm": ratio,
                        "ratio_status": (
                            "PASS" if ratio is not None else "UNDEFINED_ZERO_DENOMINATOR"
                        ),
                    }
                )

    return {
        "status": "PASS",
        "authority": "DIRECT_RAW_BASE_SESSION_PROFILE_ONLY",
        "semantic_identity_fields": [
            "point",
            "role",
            "M",
            "implementation",
            "state",
        ],
        "profiles": profiles,
        "state_ratios": ratios,
        "normalized_rows": normalized_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--point-spec", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    document = json.loads(args.point_spec.read_text(encoding="utf-8"))
    result = consume(document, args.point_spec.parent)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "profiles": len(result["profiles"])}))


if __name__ == "__main__":
    main()
