#!/usr/bin/env python3
"""Provenance-safe temporal and calibration analysis for EP-L2 Lane D.

Inputs are immutable result roots.  A cell declaration explicitly identifies
the only intended experimental dimensions; all other provenance must match
before a delta is emitted.  Missing telemetry is emitted as ``NOT_EMITTED``;
it is never silently converted to zero.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

NA = "NOT_EMITTED"
SCHEMA = "EPL2B0V1"


@dataclass(frozen=True)
class Cell:
    name: str
    root: Path
    descriptor_capacity: int
    l1_class: str


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as source:
        return list(csv.DictReader(source))


def number(row: dict[str, str], field: str) -> float | None:
    value = row.get(field)
    if value in (None, "", "NA", NA):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def integer(row: dict[str, str], field: str) -> int | None:
    value = number(row, field)
    return int(value) if value is not None else None


def field_total(records: list[dict[str, str]], field: str) -> int | str:
    values = [integer(row, field) for row in records]
    if not values or any(value is None for value in values):
        return NA
    return sum(value for value in values if value is not None)


def field_weighted(records: list[dict[str, str]], field: str, weight: str) -> float | str:
    pairs = [(number(row, field), number(row, weight)) for row in records]
    if not pairs or any(value is None or factor is None for value, factor in pairs):
        return NA
    denominator = sum(factor for _, factor in pairs if factor is not None)
    return (sum(value * factor for value, factor in pairs if value is not None and factor is not None) /
            denominator) if denominator else 0.0


def percentile(values: Iterable[float], p: float) -> float | str:
    """Nearest-rank percentile, deterministic and documented for small N."""
    ordered = sorted(values)
    if not ordered:
        return NA
    if not 0.0 <= p <= 1.0:
        raise ValueError("percentile must be within [0, 1]")
    return ordered[max(0, math.ceil(p * len(ordered)) - 1)]


def distribution(records: list[dict[str, str]], field: str, capacity: float | None = None,
                 weight: str | None = None) -> dict[str, float | int | str]:
    values = [number(row, field) for row in records]
    if not values or any(value is None for value in values):
        return {key: NA for key in ("avg", "p50", "p95", "max", "near_full_fraction", "full_fraction")}
    actual = [value for value in values if value is not None]
    average: float | str
    if weight:
        average = field_weighted(records, field, weight)
    else:
        average = sum(actual) / len(actual)
    near = full = NA
    if capacity is not None:
        near = sum(value >= 0.9 * capacity for value in actual) / len(actual)
        full = sum(value >= capacity for value in actual) / len(actual)
    return {"avg": average, "p50": percentile(actual, .50), "p95": percentile(actual, .95),
            "max": max(actual), "near_full_fraction": near, "full_fraction": full}


def interval_cycles(records: list[dict[str, str]], interval_field: str = "interval") -> int | None:
    if not records:
        return None
    text = records[0].get(interval_field, "")
    if text.endswith("_cycle"):
        try:
            return int(text[:-6])
        except ValueError:
            return None
    return None


def longest_burst(records: list[dict[str, str]], id_field: str, time_field: str,
                  field: str, threshold: float) -> int | str:
    """Return the longest consecutive high-pressure run within one stream."""
    required = (id_field, time_field, field)
    if not records or any(any(row.get(key) in (None, "", NA, "NA") for key in required) for row in records):
        return NA
    longest = 0
    by_stream: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in records:
        by_stream[row[id_field]].append(row)
    for stream in by_stream.values():
        run = 0
        previous: int | None = None
        for row in sorted(stream, key=lambda item: int(item[time_field])):
            now, value = int(row[time_field]), number(row, field)
            if value is not None and value >= threshold and (previous is None or now > previous):
                run += 1
                longest = max(longest, run)
            else:
                run = 0
            previous = now
    return longest


def channel_imbalance(records: list[dict[str, str]]) -> dict[str, float | str]:
    """Per-time-window channel traffic imbalance; zeros are meaningful samples."""
    required = ("window_start_cycle", "channel", "bandwidth_util_numerator_bytes")
    if not records or any(any(row.get(key) in (None, "", NA, "NA") for key in required) for row in records):
        return {"max_to_mean_max": NA, "max_to_mean_p95": NA, "cv_max": NA, "cv_p95": NA}
    groups: dict[str, list[float]] = defaultdict(list)
    for row in records:
        value = number(row, "bandwidth_util_numerator_bytes")
        if value is not None:
            groups[row["window_start_cycle"]].append(value)
    ratios, cvs = [], []
    for values in groups.values():
        mean = sum(values) / len(values)
        if mean == 0:
            ratios.append(0.0); cvs.append(0.0)
        else:
            ratios.append(max(values) / mean)
            cvs.append(math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)) / mean)
    return {"max_to_mean_max": max(ratios, default=0.0), "max_to_mean_p95": percentile(ratios, .95),
            "cv_max": max(cvs, default=0.0), "cv_p95": percentile(cvs, .95)}


def one(records: list[dict[str, str]], field: str) -> str:
    values = {row.get(field, "") for row in records if row.get(field, "")}
    if len(values) != 1:
        raise ValueError(f"expected one {field}, observed {sorted(values)}")
    return values.pop()


def artifact_run(cell: Cell, directory: Path) -> dict[str, Any]:
    status = json.loads((directory / "run_status.json").read_text())
    if status.get("status") != "COMPLETE_VALID":
        raise ValueError(f"{directory}: status is {status.get('status')!r}, not COMPLETE_VALID")
    manifest = json.loads((directory / "manifest.json").read_text())
    campaign_path = cell.root / "campaign_manifest.json"
    campaign = json.loads(campaign_path.read_text()) if campaign_path.exists() else {}
    slices = rows(directory / "target_slice.csv")
    summary = rows(directory / "target_summary.csv")
    l1 = [row for row in rows(directory / "target_l1.csv") if row.get("scope") == "application"]
    dram = rows(directory / "target_dram.csv")
    l2_windows = [row for row in rows(directory / "target_window.csv") if row.get("scope") == "window"]
    dram_windows = [row for row in dram if row.get("scope") == "window"]
    app_dram = [row for row in dram if row.get("scope") == "application"]
    if not slices or not summary or not l2_windows or not dram_windows:
        raise ValueError(f"{directory}: required telemetry file is empty")
    schemas = {one(slices, "schema_version"), one(l2_windows, "schema_version")}
    schemas.update(row.get("schema_version", "") for row in dram_windows)
    if schemas != {SCHEMA, "EPL2DRAMV1"}:
        raise ValueError(f"{directory}: incompatible telemetry schemas {sorted(schemas)}")
    audit = manifest.get("audit", {})
    completion = int(status["terminal_gpu_tot_sim_cycle"])
    l2_interval, dram_interval = interval_cycles(l2_windows), interval_cycles(dram_windows)
    configured_l2 = integer(summary[0], "slice_count")
    configured_dram = len(app_dram)
    slice_ids, channel_ids = {row["slice"] for row in l2_windows}, {row["channel"] for row in dram_windows}
    if configured_l2 is None or configured_dram == 0 or l2_interval is None or dram_interval is None:
        raise ValueError(f"{directory}: insufficient cardinality metadata")
    full_l2, full_dram = completion // l2_interval, completion // dram_interval
    cardinality = {
        "configured_l2_slices": configured_l2, "configured_dram_channels": configured_dram,
        "unique_l2_slice_ids": len(slice_ids), "unique_dram_channel_ids": len(channel_ids),
        "l2_window_interval_cycles": l2_interval, "dram_window_interval_cycles": dram_interval,
        "completion_cycles": completion, "expected_l2_window_rows": full_l2 * configured_l2,
        "actual_l2_window_rows": len(l2_windows), "expected_dram_window_rows": full_dram * configured_dram,
        "actual_dram_window_rows": len(dram_windows),
        "cardinality_status": "PASS_FULL_WINDOWS_ONLY" if (len(l2_windows) == full_l2 * configured_l2 and
            len(dram_windows) == full_dram * configured_dram and len(slice_ids) == configured_l2 and
            len(channel_ids) == configured_dram) else "FAIL_TOPOLOGY_OR_STREAM_MISMATCH",
        "aggregation_reason": "Producer emits completed 5K intervals only; no partial terminal interval. L2 is per slice; DRAM is per channel.",
    }
    desc = distribution(l2_windows, "descriptor_avg", cell.descriptor_capacity, "samples")
    mshr = distribution(l2_windows, "line_mshr_avg", 128, "samples")
    lower = distribution(l2_windows, "lowerq_avg", 128, "samples")
    sched = distribution(dram_windows, "scheduler_occ_avg", 128, "dram_cycles")
    returnq = distribution(dram_windows, "returnq_occ_avg", 192, "dram_cycles")
    bw = distribution(dram_windows, "bandwidth_util")
    temporal = {
        **{f"descriptor_{key}": value for key, value in desc.items()},
        **{f"line_mshr_{key}": value for key, value in mshr.items()},
        **{f"l2_to_dram_occ_{key}": value for key, value in lower.items()},
        **{f"scheduler_occ_{key}": value for key, value in sched.items()},
        **{f"returnq_occ_{key}": value for key, value in returnq.items()},
        **{f"bandwidth_util_{key}": value for key, value in bw.items()},
        "scheduler_full_active_fraction": sum((integer(row, "scheduler_full_cycles") or 0) > 0 for row in dram_windows) / len(dram_windows),
        "returnq_full_active_fraction": sum((integer(row, "returnq_full_cycles") or 0) > 0 for row in dram_windows) / len(dram_windows),
        "read_bytes_windows": field_total(dram_windows, "successful_read_bytes"),
        "write_bytes_windows": field_total(dram_windows, "successful_write_bytes"),
        "descriptor_high_burst_windows": longest_burst(l2_windows, "slice", "start_cycle", "descriptor_avg", .9 * cell.descriptor_capacity),
        "scheduler_high_burst_windows": longest_burst(dram_windows, "channel", "window_start_cycle", "scheduler_occ_avg", .9 * 128),
        **{f"channel_{key}": value for key, value in channel_imbalance(dram_windows).items()},
    }
    # Application records contain exact totals/occupancy; window records describe temporal shape.
    app_slice = [row for row in slices if row.get("scope") == "application"]
    def app_total(field: str) -> int | str: return field_total(app_slice, field)
    def app_weighted(field: str) -> float | str: return field_weighted(app_slice, field, "samples")
    def dram_total(field: str) -> int | str: return field_total(app_dram, field)
    def l1_total(field: str) -> int | str: return field_total(l1, field)
    summary0 = summary[0]
    metrics = {
        "cycles": completion, "descriptor_need": app_total("c7e_descriptor_need"),
        "descriptor_block": app_total("c7d_descriptor_pool_full_block"), "descriptor_occ_avg": app_weighted("descriptor_avg"),
        "descriptor_occ_max": max((integer(row, "descriptor_max") or 0 for row in app_slice), default=0),
        "line_mshr_need": app_total("c7e_line_mshr_need"), "line_mshr_block": app_total("c7d_line_mshr_full_block"),
        "line_mshr_occ_avg": app_weighted("line_mshr_avg"), "line_mshr_occ_max": max((integer(row, "line_mshr_max") or 0 for row in app_slice), default=0),
        "l1_mshr_entry_fail": l1_total("mshr_entry_fail"), "l1_missq_full": l1_total("miss_queue_full"),
        "l1_bank_latency_conflict": l1_total("bank_latency_queue_conflict"), "wad_full": app_total("c7d_wad_full_events"),
        "wad_hazard": app_total("c7d_wad_hazard_events"), "payload_capacity_denial": app_total("c7d_payload_capacity_allocation_denial"),
        "payload_service_denial": app_total("c7d_payload_service_port_denial"), "bank_conflict_ops": app_total("bank_true_conflict_ops"),
        "bank_wait_cycles": app_total("bank_wait_cycles"), "l2_to_dram_full": app_total("c7d_l2_to_dram_full_block"),
        "scheduler_causal_block": app_total("c7e_dram_scheduler_causal_block"), "dram_read_bytes": dram_total("successful_read_bytes"),
        "dram_write_bytes": dram_total("successful_write_bytes"), "dram_bandwidth_util": field_weighted(app_dram, "bandwidth_util", "dram_cycles"),
        "terminal_clean": summary0.get("invariants_terminal_clean", NA),
    }
    config_hash = audit.get("runtime_config_composite_sha256", campaign.get("runtime_config_composite_sha256", NA))
    if config_hash == NA:
        raise ValueError(f"{directory}: no runtime config hash in run or campaign manifest")
    return {"cell": cell.name, "workload": status["workload"], "variant": status["variant"],
            "core_sha": manifest.get("core_commit", audit.get("core_authoritative_source", NA)),
            "framework_sha": manifest.get("framework_commit", audit.get("framework_authoritative_source", NA)),
            "config_hash": config_hash, "trace_identity": status.get("trace", NA),
            "frequency_mhz": status.get("frequency_mhz", NA), "descriptor_capacity": cell.descriptor_capacity,
            "l1_config_class": cell.l1_class, "source_dir": str(directory), **cardinality, **temporal, **metrics}


def discover(cell: Cell, workloads: set[str] | None) -> list[dict[str, Any]]:
    records = []
    for status_path in sorted(cell.root.glob("B0-*/*/run_status.json")):
        workload = status_path.parent.name
        if workloads and workload not in workloads:
            continue
        records.append(artifact_run(cell, status_path.parent))
    if not records:
        raise ValueError(f"{cell.name}: no complete runs under {cell.root}")
    keys = [(record["workload"], record["variant"], record["cell"]) for record in records]
    if len(keys) != len(set(keys)):
        raise ValueError(f"{cell.name}: duplicate workload/variant/cell record")
    return records


def pair_status(base: dict[str, Any], candidate: dict[str, Any]) -> str:
    for key in ("workload", "variant", "core_sha", "framework_sha", "frequency_mhz", "trace_identity"):
        if base[key] != candidate[key]:
            return f"REJECTED_{key.upper()}_MISMATCH"
    if (base["descriptor_capacity"], base["l1_config_class"]) == (candidate["descriptor_capacity"], candidate["l1_config_class"]) and base["config_hash"] != candidate["config_hash"]:
        return "REJECTED_UNDECLARED_CONFIG_MISMATCH"
    return "COMPATIBLE_DECLARED_CELL_DELTA"


def make_deltas(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bases = {(row["workload"], row["variant"]): row for row in records
             if row["descriptor_capacity"] == 256 and row["l1_config_class"] == "BASE"}
    output = []
    for row in records:
        if row["descriptor_capacity"] == 256 and row["l1_config_class"] == "BASE":
            continue
        base = bases.get((row["workload"], row["variant"]))
        if base is None:
            output.append({"cell": row["cell"], "workload": row["workload"], "variant": row["variant"],
                           "comparison_status": "MISSING_D256_BASELINE"})
            continue
        result = {"cell": row["cell"], "workload": row["workload"], "variant": row["variant"],
                  "comparison_status": pair_status(base, row), "baseline_config_hash": base["config_hash"],
                  "candidate_config_hash": row["config_hash"]}
        if result["comparison_status"] != "COMPATIBLE_DECLARED_CELL_DELTA":
            output.append(result); continue
        result["cycle_speedup"] = base["cycles"] / row["cycles"]
        for metric in ("descriptor_need", "descriptor_block", "descriptor_occ_avg", "line_mshr_need", "line_mshr_block",
                       "line_mshr_occ_avg", "l1_mshr_entry_fail", "l1_missq_full", "l1_bank_latency_conflict", "wad_full",
                       "wad_hazard", "bank_conflict_ops", "bank_wait_cycles", "l2_to_dram_full", "scheduler_causal_block",
                       "dram_read_bytes", "dram_write_bytes", "dram_bandwidth_util", "descriptor_high_burst_windows",
                       "scheduler_high_burst_windows", "channel_cv_p95"):
            left, right = base.get(metric, NA), row.get(metric, NA)
            result[f"delta_{metric}"] = right - left if isinstance(left, (int, float)) and isinstance(right, (int, float)) else NA
        output.append(result)
    return output


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(field for record in records for field in record))
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields); writer.writeheader(); writer.writerows(records)


def parse_cell(text: str) -> Cell:
    # NAME:ROOT:DESCRIPTOR:L1_CLASS; ROOT may not contain a colon on Linux.
    try:
        name, root, descriptor, l1_class = text.rsplit(":", 3)
        return Cell(name, Path(root), int(descriptor), l1_class)
    except ValueError as error:
        raise argparse.ArgumentTypeError("cell must be NAME:ROOT:DESCRIPTOR:L1_CLASS") from error


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cell", type=parse_cell, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workload", action="append", help="restrict to known completed workload(s)")
    args = parser.parse_args()
    if len({cell.name for cell in args.cell}) != len(args.cell):
        raise SystemExit("duplicate cell name")
    workloads = set(args.workload) if args.workload else None
    args.out.mkdir(parents=True, exist_ok=True)
    records = [record for cell in args.cell for record in discover(cell, workloads)]
    cardinality = [{key: row[key] for key in ("cell", "workload", "variant", "source_dir", "configured_l2_slices",
                   "configured_dram_channels", "unique_l2_slice_ids", "unique_dram_channel_ids", "l2_window_interval_cycles",
                   "dram_window_interval_cycles", "completion_cycles", "expected_l2_window_rows", "actual_l2_window_rows",
                   "expected_dram_window_rows", "actual_dram_window_rows", "cardinality_status", "aggregation_reason")}
                   for row in records]
    temporal_keys = [
        "descriptor_avg", "descriptor_p50", "descriptor_p95", "descriptor_max", "descriptor_near_full_fraction", "descriptor_full_fraction",
        "line_mshr_avg", "line_mshr_p50", "line_mshr_p95", "line_mshr_max", "line_mshr_near_full_fraction", "line_mshr_full_fraction",
        "l2_to_dram_occ_avg", "l2_to_dram_occ_p50", "l2_to_dram_occ_p95", "l2_to_dram_occ_max", "l2_to_dram_occ_near_full_fraction", "l2_to_dram_occ_full_fraction",
        "scheduler_occ_avg", "scheduler_occ_p50", "scheduler_occ_p95", "scheduler_occ_max", "scheduler_occ_near_full_fraction", "scheduler_occ_full_fraction",
        "returnq_occ_avg", "returnq_occ_p50", "returnq_occ_p95", "returnq_occ_max", "returnq_occ_near_full_fraction", "returnq_occ_full_fraction",
        "bandwidth_util_avg", "bandwidth_util_p50", "bandwidth_util_p95", "bandwidth_util_max", "scheduler_full_active_fraction", "returnq_full_active_fraction",
        "read_bytes_windows", "write_bytes_windows", "descriptor_high_burst_windows", "scheduler_high_burst_windows",
        "channel_max_to_mean_max", "channel_max_to_mean_p95", "channel_cv_max", "channel_cv_p95",
    ]
    temporal = [{key: row[key] for key in ("cell", "workload", "variant", "descriptor_capacity", "l1_config_class", *temporal_keys)} for row in records]
    write_csv(args.out / "TEMPORAL_CARDINALITY_AUDIT.csv", cardinality)
    write_csv(args.out / "TEMPORAL_DISTRIBUTIONS.csv", temporal)
    write_csv(args.out / "CHANNEL_IMBALANCE.csv", [{key: row[key] for key in ("cell", "workload", "variant", "channel_max_to_mean_max", "channel_max_to_mean_p95", "channel_cv_max", "channel_cv_p95")} for row in records])
    write_csv(args.out / "CALIBRATION_MATRIX.csv", records)
    write_csv(args.out / "CALIBRATION_DELTAS.csv", make_deltas(records))
    (args.out / "ANALYSIS_MANIFEST.json").write_text(json.dumps({"schema": "EP_L2_LANE_D_V1", "cells": [cell.__dict__ | {"root": str(cell.root)} for cell in args.cell], "records": len(records), "workloads": sorted(workloads) if workloads else "all"}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
