#!/usr/bin/env python3
"""Category-aware, fail-closed consumer for critical-path NCU BASE evidence.

Exact NCU metric names are deliberately supplied by a producer-side runtime
query.  This consumer owns the semantic category and aggregation rules; it
does not guess metric names or derive unavailable categories from substitutes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


class CriticalPathError(ValueError):
    """Critical-path evidence is absent, ambiguous, or violates the contract."""


ADDITIVE_CATEGORY_UNITS = {
    "KERNEL_ELAPSED_CYCLES": {"cycle", "cycles"},
    "L2_READ_HIT_SECTORS": {"sector", "sectors"},
    "L2_READ_MISS_SECTORS": {"sector", "sectors"},
    "DRAM_READ_SECTORS": {"sector", "sectors"},
    "DRAM_READ_BYTES": {"byte", "bytes"},
}

PER_KERNEL_CATEGORY_UNITS = {
    "L2_READ_HIT_RATE": {"%", "percent"},
    "LONG_SCOREBOARD_STALL": {"%", "percent"},
    "MEMORY_DEPENDENCY_STALL": {"%", "percent"},
    "MEMORY_PIPE_UTILIZATION": {"%", "percent"},
    "LSU_UTILIZATION": {"%", "percent"},
    "ACHIEVED_ACTIVE_WARPS": {"warp", "warps"},
    "ACHIEVED_OCCUPANCY": {"%", "percent"},
}

CATEGORY_POLICY = {
    **{category: "SEMANTIC_SUM" for category in ADDITIVE_CATEGORY_UNITS},
    **{category: "PER_KERNEL_ONLY" for category in PER_KERNEL_CATEGORY_UNITS},
}
KNOWN_CATEGORIES = frozenset(CATEGORY_POLICY)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
RANGE_COLUMN = "NVTX Push/Pop_Range"
IDENTITY_COLUMNS = ("ID", "Kernel Name", RANGE_COLUMN)


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CriticalPathError(f"missing or empty field: {field}")
    return value.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_number(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _decimal(value: object, field: str) -> Decimal:
    raw = str(value).replace(",", "").strip()
    if not raw:
        raise CriticalPathError(f"missing metric value: {field}")
    try:
        parsed = Decimal(raw)
    except InvalidOperation as exc:
        raise CriticalPathError(f"invalid metric value: {field}={value!r}") from exc
    if not parsed.is_finite():
        raise CriticalPathError(f"non-finite metric value: {field}")
    return parsed


def _nvtx_exact(cell: str, target: str) -> bool:
    # NCU commonly prefixes ranges with a process/domain and suffixes with '/'.
    pattern = re.compile(r"(?:^|:)" + re.escape(target) + r"(?=:|/|$)")
    return len(pattern.findall(cell.strip())) == 1


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise CriticalPathError(f"{field} must be a non-empty list")
    parsed = [_text(item, field) for item in value]
    if len(parsed) != len(set(parsed)):
        raise CriticalPathError(f"{field} contains duplicates")
    return parsed


def _parse_query_receipt(raw: object, root: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CriticalPathError("query_receipt must be an object")
    if raw.get("status") != "PASS":
        raise CriticalPathError("metric query receipt status must be PASS")
    command = _text(raw.get("command"), "query_receipt.command")
    if "query" not in command.lower() or "metric" not in command.lower():
        raise CriticalPathError("query receipt command does not establish metric discovery")

    result: dict[str, Any] = {"status": "PASS", "command": command}
    if "path" in raw:
        path = root / _text(raw.get("path"), "query_receipt.path")
        if not path.is_file() or path.stat().st_size == 0:
            raise CriticalPathError(f"missing or empty metric query receipt: {path}")
        actual = _sha256(path)
        claimed = _text(raw.get("sha256"), "query_receipt.sha256").lower()
        if not HEX64.fullmatch(claimed) or claimed != actual:
            raise CriticalPathError("metric query receipt SHA256 mismatch")
        result.update({"path": str(path), "sha256": actual})
    else:
        output_sha = _text(raw.get("output_sha256"), "query_receipt.output_sha256").lower()
        if not HEX64.fullmatch(output_sha):
            raise CriticalPathError("query_receipt.output_sha256 must be a lowercase SHA256")
        result["output_sha256"] = output_sha
    return result


def _parse_metric_catalog(raw: object) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not isinstance(raw, list) or not raw:
        raise CriticalPathError("metric_availability must be a non-empty list")

    available: list[dict[str, Any]] = []
    unavailable: list[dict[str, Any]] = []
    seen_categories: set[str] = set()
    seen_names: set[str] = set()
    for index, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise CriticalPathError(f"metric_availability[{index}] must be an object")
        category = _text(entry.get("category"), f"metric_availability[{index}].category")
        if category not in KNOWN_CATEGORIES:
            raise CriticalPathError(f"unknown metric category: {category}")
        if category in seen_categories:
            raise CriticalPathError(f"duplicate metric category: {category}")
        seen_categories.add(category)
        if not isinstance(entry.get("available"), bool):
            raise CriticalPathError(f"availability for {category} must be boolean")

        if not entry["available"]:
            if entry.get("metric_name") not in (None, "") or entry.get("unit") not in (None, ""):
                raise CriticalPathError(
                    f"unavailable category {category} must not claim metric_name/unit"
                )
            unavailable.append(
                {
                    "category": category,
                    "available": False,
                    "reason": _text(entry.get("reason"), f"{category}.reason"),
                    "aggregation": CATEGORY_POLICY[category],
                }
            )
            continue

        metric_name = _text(entry.get("metric_name"), f"{category}.metric_name")
        unit = _text(entry.get("unit"), f"{category}.unit")
        if metric_name in seen_names:
            raise CriticalPathError(f"duplicate exact metric name: {metric_name}")
        seen_names.add(metric_name)
        allowed_units = (
            ADDITIVE_CATEGORY_UNITS.get(category)
            or PER_KERNEL_CATEGORY_UNITS.get(category)
            or set()
        )
        if unit not in allowed_units:
            raise CriticalPathError(
                f"unit mismatch for category {category}: {unit!r}; expected one of {sorted(allowed_units)}"
            )

        policy = CATEGORY_POLICY[category]
        claimed_policy = entry.get("aggregation", policy)
        if claimed_policy != policy:
            raise CriticalPathError(
                f"aggregation mismatch for {category}: expected {policy}, got {claimed_policy!r}"
            )
        aggregation_authority = entry.get("aggregation_authority")
        if policy == "PER_KERNEL_ONLY" and aggregation_authority not in (None, ""):
            # A future consumer may implement a specifically documented formula.
            # This version refuses to silently turn that receipt into an average/sum.
            raise CriticalPathError(
                f"explicit non-additive aggregation is not implemented for {category}; preserve per-kernel"
            )
        available.append(
            {
                "category": category,
                "available": True,
                "metric_name": metric_name,
                "unit": unit,
                "aggregation": policy,
            }
        )
    return available, unavailable


def _parse_profile(raw: object, root: Path) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise CriticalPathError("each profile must be an object")
    path = root / _text(raw.get("base_path"), "profile.base_path")
    if not path.is_file() or path.stat().st_size == 0:
        raise CriticalPathError(f"missing or empty BASE evidence: {path}")
    return {
        "condition": _text(raw.get("condition"), "profile.condition"),
        "target": _text(raw.get("target"), "profile.target"),
        "range_name": _text(raw.get("range_name"), "profile.range_name"),
        "expected_kernel_names": _string_list(
            raw.get("expected_kernel_names"), "profile.expected_kernel_names"
        ),
        "base_path": path,
    }


def _read_base(
    profile: dict[str, Any], available: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path: Path = profile["base_path"]
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.reader(stream))
    if len(rows) < 3:
        raise CriticalPathError(f"BASE evidence lacks header/unit/data rows: {path}")
    header, units, *data = rows
    if len(header) != len(set(header)):
        raise CriticalPathError(f"duplicate BASE column/metric row identity: {path}")
    if len(units) != len(header) or any(len(row) != len(header) for row in data):
        raise CriticalPathError(f"ragged BASE evidence: {path}")

    required = [*IDENTITY_COLUMNS, *[metric["metric_name"] for metric in available]]
    missing = sorted(set(required) - set(header))
    if missing:
        raise CriticalPathError(
            "producer claimed metric available but BASE is missing required columns: "
            + ", ".join(missing)
        )
    index = {name: header.index(name) for name in required}
    for metric in available:
        observed_unit = units[index[metric["metric_name"]]].strip()
        if observed_unit != metric["unit"]:
            raise CriticalPathError(
                f"unit mismatch for {metric['metric_name']} in {profile['condition']}: "
                f"catalog={metric['unit']!r}, BASE={observed_unit!r}"
            )

    selected = [
        row for row in data if _nvtx_exact(row[index[RANGE_COLUMN]], profile["range_name"])
    ]
    if not selected:
        raise CriticalPathError(
            f"no rows for exact semantic range {profile['range_name']} in {path}"
        )

    observed_names = [row[index["Kernel Name"]].strip() for row in selected]
    if any(not name for name in observed_names):
        raise CriticalPathError("empty kernel name inside target semantic range")
    if len(observed_names) != len(set(observed_names)):
        raise CriticalPathError("duplicate metric row/kernel occurrence inside semantic range")
    if set(observed_names) != set(profile["expected_kernel_names"]):
        raise CriticalPathError(
            "kernel inventory mismatch: expected "
            f"{sorted(profile['expected_kernel_names'])}, observed {sorted(observed_names)}"
        )

    normalized: list[dict[str, Any]] = []
    seen_metric_rows: set[tuple[str, str]] = set()
    for row in selected:
        kernel_id = row[index["ID"]].strip()
        kernel_name = row[index["Kernel Name"]].strip()
        if not kernel_id:
            raise CriticalPathError("empty kernel ID inside target semantic range")
        for metric in available:
            metric_name = metric["metric_name"]
            identity = (kernel_id, metric_name)
            if identity in seen_metric_rows:
                raise CriticalPathError(f"duplicate metric row: {identity}")
            seen_metric_rows.add(identity)
            value = _decimal(row[index[metric_name]], f"{kernel_name}/{metric_name}")
            normalized.append(
                {
                    "condition": profile["condition"],
                    "target": profile["target"],
                    "range_name": profile["range_name"],
                    "kernel_id": kernel_id,
                    "kernel_name": kernel_name,
                    "category": metric["category"],
                    "metric_name": metric_name,
                    "unit": metric["unit"],
                    "aggregation": metric["aggregation"],
                    "value": _canonical_number(value),
                }
            )
    return normalized, {
        "path": str(path),
        "sha256": _sha256(path),
        "kernel_inventory": sorted(observed_names),
        "semantic_range": profile["range_name"],
    }


def consume(document: dict[str, Any], root: Path | str = Path(".")) -> dict[str, Any]:
    """Validate and normalize a critical-path metric bundle.

    ``document`` is consumer-owned configuration plus runtime discovery receipt;
    producer summary tables are intentionally not accepted.
    """
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise CriticalPathError("schema_version must equal 1")
    root = Path(root)
    query_receipt = _parse_query_receipt(document.get("query_receipt"), root)
    available, unavailable = _parse_metric_catalog(document.get("metric_availability"))
    raw_profiles = document.get("profiles")
    if not isinstance(raw_profiles, list) or not raw_profiles:
        raise CriticalPathError("profiles must be a non-empty list")

    profiles = [_parse_profile(raw, root) for raw in raw_profiles]
    identities = [(profile["condition"], profile["target"]) for profile in profiles]
    if len(identities) != len(set(identities)):
        raise CriticalPathError("duplicate condition/target profile")

    normalized: list[dict[str, Any]] = []
    provenance: list[dict[str, Any]] = []
    for profile in profiles:
        rows, receipt = _read_base(profile, available)
        normalized.extend(rows)
        provenance.append(
            {
                "condition": profile["condition"],
                "target": profile["target"],
                **receipt,
            }
        )

    semantic_sums: list[dict[str, Any]] = []
    for profile in profiles:
        for metric in available:
            if metric["aggregation"] != "SEMANTIC_SUM":
                continue
            matching = [
                row
                for row in normalized
                if row["condition"] == profile["condition"]
                and row["target"] == profile["target"]
                and row["category"] == metric["category"]
            ]
            total = sum((Decimal(str(row["value"])) for row in matching), Decimal(0))
            semantic_sums.append(
                {
                    "condition": profile["condition"],
                    "target": profile["target"],
                    "category": metric["category"],
                    "metric_name": metric["metric_name"],
                    "unit": metric["unit"],
                    "value": _canonical_number(total),
                    "kernel_count": len(matching),
                }
            )

    return {
        "schema_version": 1,
        "status": "PASS",
        "authority": "DIRECT_RUNTIME_QUERY_AND_RAW_BASE_ONLY",
        "query_receipt": query_receipt,
        "metric_availability": [*available, *unavailable],
        "kernel_metrics": normalized,
        "semantic_sums": semantic_sums,
        "non_additive_policy": "PER_KERNEL_ONLY_WITHOUT_EXPLICIT_AGGREGATION_AUTHORITY",
        "profile_provenance": provenance,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    document = json.loads(args.contract.read_text(encoding="utf-8"))
    result = consume(document, args.root)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
