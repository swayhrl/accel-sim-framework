#!/usr/bin/env python3
"""Fail-closed semantic-range NCU CSV parser and module aggregator."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


class AggregationError(ValueError):
    pass


FIELDS = {
    "semantic_point",
    "range_name",
    "range_occurrence",
    "kernel_id",
    "kernel_name",
    "metric_name",
    "metric_unit",
    "metric_value",
    "input_elements",
    "output_elements",
    "dense_weight_bytes",
    "packed_weight_bytes",
}

DEFAULT_REQUIRED_DENOMINATORS = (
    "input_elements",
    "output_elements",
    "dense_weight_bytes",
)


def _clean_text(value, field):
    if value is None:
        raise AggregationError(f"missing field value: {field}")
    out = str(value).strip()
    if not out:
        raise AggregationError(f"empty field: {field}")
    return out


def _parse_occurrence(value):
    text = _clean_text(value, "range_occurrence")
    if not text.isdigit():
        raise AggregationError("range_occurrence must be a canonical non-negative integer")
    parsed = int(text)
    if str(parsed) != text:
        raise AggregationError("range_occurrence must use canonical decimal spelling")
    return parsed


def _parse_positive_int(value, field):
    text = _clean_text(value, field)
    if not text.isdigit():
        raise AggregationError(f"{field} must be a positive integer")
    parsed = int(text)
    if parsed <= 0:
        raise AggregationError(f"{field} must be > 0")
    return parsed


def _parse_metric_value(value):
    text = _clean_text(value, "metric_value")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise AggregationError(f"invalid metric value: {text}") from exc
    if not parsed.is_finite():
        raise AggregationError(f"non-finite metric value: {text}")
    return parsed


def _json_number(value):
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        as_float = float(value)
        if not math.isfinite(as_float):
            raise AggregationError("metric value cannot be represented as finite JSON number")
        return as_float
    return value


def validate_policy(policy):
    if not isinstance(policy, dict):
        raise AggregationError("policy must be an object")
    for key in ("additive_metrics", "non_additive_metrics"):
        if key not in policy or not isinstance(policy[key], dict):
            raise AggregationError(f"policy missing object: {key}")
    additive = policy["additive_metrics"]
    nonadd = policy["non_additive_metrics"]
    overlap = set(additive) & set(nonadd)
    if overlap:
        raise AggregationError("metric classified both additive and non-additive: " + ",".join(sorted(overlap)))
    if not additive and not nonadd:
        raise AggregationError("policy classifies no metrics")
    for group_name, group in (("additive_metrics", additive), ("non_additive_metrics", nonadd)):
        for metric, unit in group.items():
            if not isinstance(metric, str) or not metric.strip():
                raise AggregationError(f"empty metric name in {group_name}")
            if not isinstance(unit, str) or not unit.strip():
                raise AggregationError(f"empty unit for metric {metric}")
    required = policy.get("required_denominators", list(DEFAULT_REQUIRED_DENOMINATORS))
    if not isinstance(required, list) or any(x not in {"input_elements", "output_elements", "dense_weight_bytes", "packed_weight_bytes"} for x in required):
        raise AggregationError("invalid required_denominators")
    return {
        "additive_metrics": additive,
        "non_additive_metrics": nonadd,
        "required_denominators": tuple(required),
    }


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        if len(fieldnames) != len(set(fieldnames)):
            raise AggregationError("duplicate CSV header column")
        if any(name is None or not str(name).strip() for name in fieldnames):
            raise AggregationError("empty CSV header column")
        missing = FIELDS - set(fieldnames)
        if missing:
            raise AggregationError("missing columns: " + ",".join(sorted(missing)))
        return list(reader)


def _denominators(candidates, required):
    out = {}
    for name in ("input_elements", "output_elements", "dense_weight_bytes", "packed_weight_bytes"):
        raw = [("" if r.get(name) is None else str(r[name]).strip()) for r in candidates]
        nonempty = set(v for v in raw if v)
        if not nonempty:
            if name in required:
                raise AggregationError(f"missing required normalization denominator: {name}")
            out[name] = None
            continue
        if len(nonempty) != 1:
            raise AggregationError(f"inconsistent normalization denominator: {name}")
        if any(v == "" for v in raw):
            raise AggregationError(f"partially missing normalization denominator: {name}")
        out[name] = _parse_positive_int(next(iter(nonempty)), name)
    return out


def aggregate(rows, point, target_range, policy):
    resolved = validate_policy(policy)
    point = _clean_text(point, "point")
    target_range = _clean_text(target_range, "target_range")
    candidates = [
        r for r in rows
        if str(r.get("semantic_point", "")).strip() == point
        and str(r.get("range_name", "")).strip() == target_range
    ]
    if not candidates:
        raise AggregationError("missing target range")

    occurrences = {_parse_occurrence(r.get("range_occurrence")) for r in candidates}
    if len(occurrences) != 1:
        raise AggregationError("ambiguous target range occurrence")
    occurrence = next(iter(occurrences))

    allowed = set(resolved["additive_metrics"]) | set(resolved["non_additive_metrics"])
    kernels = defaultdict(lambda: {"kernel_name": None, "metrics": {}})
    kernel_names = {}
    units = {}

    for r in candidates:
        if _clean_text(r.get("semantic_point"), "semantic_point") != point:
            raise AggregationError("semantic_point changed inside candidate set")
        if _clean_text(r.get("range_name"), "range_name") != target_range:
            raise AggregationError("range_name changed inside candidate set")

        kid = _clean_text(r.get("kernel_id"), "kernel_id")
        name = _clean_text(r.get("kernel_name"), "kernel_name")
        if kid in kernel_names and kernel_names[kid] != name:
            raise AggregationError(f"kernel_id maps to multiple names: {kid}")
        kernel_names[kid] = name

        metric = _clean_text(r.get("metric_name"), "metric_name")
        unit = _clean_text(r.get("metric_unit"), "metric_unit")
        if metric not in allowed:
            raise AggregationError("unclassified metric " + metric)
        expected = resolved["additive_metrics"].get(metric, resolved["non_additive_metrics"].get(metric))
        if unit != expected:
            raise AggregationError(f"unit mismatch {metric}: {unit} != {expected}")
        if metric in units and units[metric] != unit:
            raise AggregationError("inconsistent unit " + metric)
        units[metric] = unit

        k = kernels[kid]
        k["kernel_name"] = name
        if metric in k["metrics"]:
            raise AggregationError(f"duplicate kernel metric row: kernel_id={kid} metric={metric}")
        value = _parse_metric_value(r.get("metric_value"))
        k["metrics"][metric] = {
            "value": _json_number(value),
            "value_exact": str(value),
            "unit": unit,
        }

    if not kernels:
        raise AggregationError("target range contains no kernels")

    denom = _denominators(candidates, resolved["required_denominators"])

    sums = {}
    for metric, unit in resolved["additive_metrics"].items():
        missing = [kid for kid, k in kernels.items() if metric not in k["metrics"]]
        if missing:
            raise AggregationError(
                "missing additive metric on kernels "
                + metric + ": " + ",".join(sorted(missing))
            )
        total = sum(
            Decimal(k["metrics"][metric]["value_exact"])
            for k in kernels.values()
        )
        total_json = _json_number(total)
        norm = {
            "per_input_element": float(total / denom["input_elements"]) if denom["input_elements"] else None,
            "per_output_element": float(total / denom["output_elements"]) if denom["output_elements"] else None,
            "per_dense_weight_byte": float(total / denom["dense_weight_bytes"]) if denom["dense_weight_bytes"] else None,
            "per_packed_weight_byte": float(total / denom["packed_weight_bytes"]) if denom["packed_weight_bytes"] else None,
        }
        sums[metric] = {
            "value": total_json,
            "value_exact": str(total),
            "unit": unit,
            "normalization": norm,
        }

    nonadd = {}
    nonadd_coverage = {}
    for metric in resolved["non_additive_metrics"]:
        values = []
        for kid, k in kernels.items():
            if metric in k["metrics"]:
                values.append({
                    "kernel_id": kid,
                    "kernel_name": k["kernel_name"],
                    "value": k["metrics"][metric]["value"],
                    "value_exact": k["metrics"][metric]["value_exact"],
                    "unit": k["metrics"][metric]["unit"],
                })
        nonadd[metric] = values
        nonadd_coverage[metric] = {
            "kernels_with_metric": len(values),
            "kernel_count": len(kernels),
            "complete": len(values) == len(kernels),
        }

    kernel_rows = [
        {
            "kernel_id": kid,
            "kernel_name": kernels[kid]["kernel_name"],
            "metrics": kernels[kid]["metrics"],
        }
        for kid in sorted(kernels)
    ]

    return {
        "status": "PASS",
        "semantic_point": point,
        "range_name": target_range,
        "range_occurrence": occurrence,
        "kernel_count": len(kernels),
        "kernels": kernel_rows,
        "SEMANTIC_MODULE_SUM": sums,
        "non_additive_per_kernel": nonadd,
        "non_additive_coverage": nonadd_coverage,
        "denominators": denom,
    }


def _metric_decimal(point, metric):
    try:
        item = point["SEMANTIC_MODULE_SUM"][metric]
    except KeyError as exc:
        raise AggregationError(f"missing comparison metric: {metric}") from exc
    try:
        value = Decimal(str(item.get("value_exact", item["value"])))
    except (InvalidOperation, KeyError) as exc:
        raise AggregationError(f"invalid comparison metric value: {metric}") from exc
    if not value.is_finite():
        raise AggregationError(f"non-finite comparison metric: {metric}")
    unit = _clean_text(item.get("unit"), "comparison metric unit")
    return value, unit


def _safe_ratio(num, den):
    if den == 0:
        return None
    return float(num / den)


def compare(points, metrics):
    required_points = ((1, "RAW"), (1, "AWQ"), (256, "RAW"), (256, "AWQ"))
    missing = [key for key in required_points if key not in points]
    if missing:
        raise AggregationError("missing comparison points: " + ",".join(map(str, missing)))

    out = []
    for metric in metrics:
        vals = {}
        units = set()
        for key in required_points:
            value, unit = _metric_decimal(points[key], metric)
            vals[key] = value
            units.add(unit)
        if len(units) != 1:
            raise AggregationError(f"cross-point unit mismatch for metric {metric}")

        ratios = {
            "M1_AWQ_over_RAW": _safe_ratio(vals[(1, "AWQ")], vals[(1, "RAW")]),
            "M256_AWQ_over_RAW": _safe_ratio(vals[(256, "AWQ")], vals[(256, "RAW")]),
            "RAW_M256_over_M1": _safe_ratio(vals[(256, "RAW")], vals[(1, "RAW")]),
            "AWQ_M256_over_M1": _safe_ratio(vals[(256, "AWQ")], vals[(1, "AWQ")]),
        }
        undefined = [name for name, value in ratios.items() if value is None]
        out.append({
            "metric_name": metric,
            "unit": next(iter(units)),
            **ratios,
            "ratio_status": "PASS" if not undefined else "UNDEFINED_ZERO_DENOMINATOR",
            "undefined_ratios": undefined,
        })
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--policy", type=Path, required=True)
    p.add_argument("--point", required=True)
    p.add_argument("--range", dest="target", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = aggregate(
        read_csv(a.csv),
        a.point,
        a.target,
        json.loads(a.policy.read_text()),
    )
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "kernels": result["kernel_count"]}))


if __name__ == "__main__":
    main()
