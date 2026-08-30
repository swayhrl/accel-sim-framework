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
import gzip
import json
import math
import re
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
    contract_path: Path | None = None


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
                  field: str, threshold: float, interval: int, cadence_slop: int = 0) -> int | str:
    """Return the longest exactly-adjacent high-average-window run per stream."""
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
            if value is not None and value >= threshold and (previous is None or interval <= now - previous <= interval + cadence_slop):
                run += 1
                longest = max(longest, run)
            else:
                run = 0
            previous = now
    return longest


def channel_imbalance(records: list[dict[str, str]], configured_channels: int,
                      traffic_fraction_threshold: float = .01) -> dict[str, float | str]:
    """Channel imbalance, with near-idle windows separated from traffic evidence."""
    required = ("window_start_cycle", "channel", "bandwidth_util_numerator_bytes",
                "bandwidth_util_denominator_bytes")
    if not records or any(any(row.get(key) in (None, "", NA, "NA") for key in required) for row in records):
        return {key: NA for key in ("all_window_max_to_mean_max", "all_window_max_to_mean_p95", "all_window_cv_max", "all_window_cv_p95", "active_channels_p50", "active_channels_p95", "active_channels_max", "traffic_conditioned_window_fraction", "traffic_conditioned_max_to_mean_p95", "traffic_conditioned_cv_p95", "traffic_weighted_max_to_mean", "traffic_weighted_cv")}
    groups: dict[str, list[tuple[int, float, float]]] = defaultdict(list)
    for row in records:
        value, denominator = number(row, "bandwidth_util_numerator_bytes"), number(row, "bandwidth_util_denominator_bytes")
        channel = integer(row, "channel")
        # The required-field check above makes this a defensive assertion, not
        # a silent record drop which could bias an imbalance calculation.
        if value is None or denominator is None or channel is None:
            return {key: NA for key in ("all_window_max_to_mean_max", "all_window_max_to_mean_p95", "all_window_cv_max", "all_window_cv_p95", "active_channels_p50", "active_channels_p95", "active_channels_max", "traffic_conditioned_window_fraction", "traffic_conditioned_max_to_mean_p95", "traffic_conditioned_cv_p95", "traffic_weighted_max_to_mean", "traffic_weighted_cv")}
        groups[row["window_start_cycle"]].append((channel, value, denominator))
    ratios, cvs, active_counts, conditioned = [], [], [], []
    for pairs in groups.values():
        if len(pairs) != configured_channels or {channel for channel, _, _ in pairs} != set(range(configured_channels)):
            return {key: NA for key in ("all_window_max_to_mean_max", "all_window_max_to_mean_p95", "all_window_cv_max", "all_window_cv_p95", "active_channels_p50", "active_channels_p95", "active_channels_max", "traffic_conditioned_window_fraction", "traffic_conditioned_max_to_mean_p95", "traffic_conditioned_cv_p95", "traffic_weighted_max_to_mean", "traffic_weighted_cv")}
        values = [value for _, value, _ in pairs]
        mean = sum(values) / len(values)
        total, capacity = sum(values), sum(denominator for _, _, denominator in pairs)
        active_counts.append(sum(value > 0 for value in values))
        if mean == 0:
            ratio = cv = 0.0
        else:
            ratio = max(values) / mean
            cv = math.sqrt(sum((value - mean) ** 2 for value in values) / len(values)) / mean
        ratios.append(ratio); cvs.append(cv)
        if total >= traffic_fraction_threshold * capacity:
            conditioned.append((ratio, cv, total))
    weighted_denominator = sum(total for _, _, total in conditioned)
    return {"all_window_max_to_mean_max": max(ratios, default=0.0), "all_window_max_to_mean_p95": percentile(ratios, .95),
            "all_window_cv_max": max(cvs, default=0.0), "all_window_cv_p95": percentile(cvs, .95),
            "active_channels_p50": percentile(active_counts, .50), "active_channels_p95": percentile(active_counts, .95), "active_channels_max": max(active_counts, default=0),
            "traffic_conditioned_window_fraction": len(conditioned) / len(groups) if groups else NA,
            "traffic_conditioned_max_to_mean_p95": percentile((ratio for ratio, _, _ in conditioned), .95),
            "traffic_conditioned_cv_p95": percentile((cv for _, cv, _ in conditioned), .95),
            "traffic_weighted_max_to_mean": (sum(ratio * total for ratio, _, total in conditioned) / weighted_denominator) if weighted_denominator else NA,
            "traffic_weighted_cv": (sum(cv * total for _, cv, total in conditioned) / weighted_denominator) if weighted_denominator else NA}


def one(records: list[dict[str, str]], field: str) -> str:
    values = {row.get(field, "") for row in records if row.get(field, "")}
    if len(values) != 1:
        raise ValueError(f"expected one {field}, observed {sorted(values)}")
    return values.pop()


def validate_window_stream(records: list[dict[str, str]], id_field: str, time_field: str,
                           configured_streams: int, interval: int, completed_windows: int,
                           cadence_slop: int = 0) -> str:
    """Reject duplicate, missing, unexpected-id, and gapped stream/time keys."""
    try:
        keys = [(int(row[id_field]), int(row[time_field])) for row in records]
    except (KeyError, ValueError):
        return "FAIL_INVALID_STREAM_KEY"
    if len(keys) != len(set(keys)):
        return "FAIL_DUPLICATE_STREAM_WINDOW_KEY"
    if {stream for stream, _ in keys} != set(range(configured_streams)):
        return "FAIL_STREAM_ID_SET_MISMATCH"
    for stream in range(configured_streams):
        times = sorted(time for stream_id, time in keys if stream_id == stream)
        if len(times) != completed_windows or any(not interval <= later - earlier <= interval + cadence_slop for earlier, later in zip(times, times[1:])):
            return "FAIL_MISSING_OR_GAPPED_STREAM_WINDOW"
    return "PASS_FULL_WINDOWS_ONLY"


def validate_time_groups(records: list[dict[str, str]], id_field: str, time_field: str,
                         configured_streams: int) -> str:
    """Require every exact time group to contain one record for every stream."""
    groups: dict[int, list[int]] = defaultdict(list)
    try:
        for row in records:
            groups[int(row[time_field])].append(int(row[id_field]))
    except (KeyError, ValueError):
        return "FAIL_INVALID_TIME_GROUP_KEY"
    expected = set(range(configured_streams))
    for stream_ids in groups.values():
        if len(stream_ids) != configured_streams or set(stream_ids) != expected:
            return "FAIL_TIME_GROUP_STREAM_ALIGNMENT"
    return "PASS_EXACT_TIME_GROUP_ALIGNMENT"


def ratio_distribution(records: list[dict[str, str]], numerator: str, denominator: str) -> dict[str, float | str]:
    values: list[float] = []
    for row in records:
        top, bottom = number(row, numerator), number(row, denominator)
        if top is None or bottom is None:
            return {key: NA for key in ("cycle_fraction", "window_fraction_p50", "window_fraction_p95", "window_fraction_max")}
        values.append(top / bottom if bottom else 0.0)
    top_total, bottom_total = field_total(records, numerator), field_total(records, denominator)
    return {"cycle_fraction": top_total / bottom_total if isinstance(top_total, int) and isinstance(bottom_total, int) and bottom_total else NA,
            "window_fraction_p50": percentile(values, .50), "window_fraction_p95": percentile(values, .95), "window_fraction_max": max(values, default=0.0)}


def native_dram_data_bus_util_from_lines(lines: Iterable[str], configured_channels: int) -> dict[str, float | int | str]:
    """Aggregate the final complete native ``DRAM[id]`` snapshot.

    ``dram_t::print`` is emitted one block per channel.  A repeated channel id
    starts a new snapshot; incomplete snapshots are deliberately discarded.
    This never mixes channels from separate prints or promotes a last-channel
    value to an application-level result.
    """
    snapshots: list[dict[int, tuple[int, float]]] = []
    current: dict[int, tuple[int, float]] = {}
    active_channel: int | None = None
    active_commands: int | None = None
    active_inline_util: float | None = None
    active_detail_util: float | None = None

    def finish_active() -> None:
        nonlocal active_commands, active_inline_util, active_detail_util
        if active_channel is not None and active_commands is not None:
            # The detailed ``bwutil =`` print retains more precision than the
            # compact summary; use it when present within the same DRAM block.
            utility = active_detail_util if active_detail_util is not None else active_inline_util
            if utility is not None:
                current[active_channel] = (active_commands, utility)

    for line in lines:
        header = re.search(r"\bDRAM\[(\d+)\]:", line)
        if header:
            finish_active()
            channel = int(header.group(1))
            if channel in current:
                snapshots.append(current)
                current = {}
            active_channel = channel
            active_commands = active_inline_util = active_detail_util = None
            continue
        if active_channel is None:
            continue
        command = re.search(r"\bn_cmd=(\d+)\b", line)
        inline_util = re.search(r"\bbw_util\s*=\s*([0-9.+-eE]+)", line)
        detail_util = re.search(r"^\s*bwutil\s*=\s*([0-9.+-eE]+)", line)
        if command:
            active_commands = int(command.group(1))
        if inline_util:
            active_inline_util = float(inline_util.group(1))
        if detail_util:
            active_detail_util = float(detail_util.group(1))
    finish_active()
    if current:
        snapshots.append(current)
    expected = set(range(configured_channels))
    complete = [snapshot for snapshot in snapshots
                if len(snapshot) == configured_channels and set(snapshot) == expected]
    if not complete:
        return {"native_dram_snapshot_status": "FAIL_NO_COMPLETE_CHANNEL_SNAPSHOT",
                "native_dram_channels_observed": NA,
                "native_dram_data_bus_util_weighted_mean": NA,
                "native_dram_data_bus_util_p50": NA,
                "native_dram_data_bus_util_p95": NA,
                "native_dram_data_bus_util_max": NA,
                "native_dram_n_cmd_sum": NA}
    selected = complete[-1]
    commands = [command for command, _ in selected.values()]
    utils = [util for _, util in selected.values()]
    total_commands = sum(commands)
    return {"native_dram_snapshot_status": "PASS_FINAL_COMPLETE_CHANNEL_SNAPSHOT",
            "native_dram_channels_observed": len(selected),
            "native_dram_data_bus_util_weighted_mean":
                sum(command * util for command, util in selected.values()) / total_commands if total_commands else NA,
            "native_dram_data_bus_util_p50": percentile(utils, .50),
            "native_dram_data_bus_util_p95": percentile(utils, .95),
            "native_dram_data_bus_util_max": max(utils),
            "native_dram_n_cmd_sum": total_commands}


def native_dram_data_bus_util(directory: Path, configured_channels: int) -> dict[str, float | int | str]:
    """Read retained raw logs and aggregate their final complete DRAM snapshot."""
    raw_gz, raw = directory / "raw.log.gz", directory / "raw.log"
    if raw_gz.exists():
        source = gzip.open(raw_gz, "rt", errors="replace")
    elif raw.exists():
        source = raw.open(errors="replace")
    else:
        return {"native_dram_snapshot_status": "NOT_RETAINED_RAW_LOG",
                "native_dram_channels_observed": NA,
                "native_dram_data_bus_util_weighted_mean": NA,
                "native_dram_data_bus_util_p50": NA,
                "native_dram_data_bus_util_p95": NA,
                "native_dram_data_bus_util_max": NA,
                "native_dram_n_cmd_sum": NA}
    with source:
        return native_dram_data_bus_util_from_lines(source, configured_channels)


def load_contract(cell: Cell) -> dict[str, Any]:
    if cell.contract_path is None:
        raise ValueError(f"{cell.name}: machine-readable cell contract is required")
    contract = json.loads(cell.contract_path.read_text())
    if contract.get("schema") != "EP_L2_CALIBRATION_CONTRACT_V2" or contract.get("cell") != cell.name:
        raise ValueError(f"{cell.name}: invalid cell contract {cell.contract_path}")
    if (not isinstance(contract.get("effective_config"), dict) or
            not isinstance(contract.get("allowed_config_fields"), list) or
            not isinstance(contract.get("runtime_config_composite_sha256"), str)):
        raise ValueError(f"{cell.name}: incomplete effective-config contract")
    return contract


def contract_binding_status(contract: dict[str, Any], actual_config_hash: str) -> str:
    """Bind a contract's declared effective config to the actual run digest."""
    gate = contract.get("config_delta_gate", {})
    if (not contract.get("runtime_config_composite_sha256") or
            gate.get("status") != "PASS" or not gate.get("evidence_path")):
        return "REJECTED_INCOMPLETE_CONFIG_DELTA_GATE"
    if actual_config_hash != contract["runtime_config_composite_sha256"]:
        return "REJECTED_RUNTIME_CONFIG_HASH_MISMATCH"
    return "PASS_RUNTIME_CONFIG_BOUND"


def runtime_config_hash(status: dict[str, Any], manifest: dict[str, Any], campaign: dict[str, Any]) -> str:
    """Return the authoritative runtime-config digest from retained run audit.

    Current promoted calibration runners place the per-run audit in
    ``run_status.json``; older formal artifacts retain it in the manifest or
    campaign manifest.  These are ordered evidence sources, never a default.
    """
    for source in (status.get("audit", {}), manifest.get("audit", {}), campaign):
        value = source.get("runtime_config_composite_sha256", NA)
        if value not in (None, "", NA):
            return value
    return NA


def expected_allowed_config_fields(descriptor_capacity: int, l1_class: str) -> set[str]:
    allowed = set()
    if descriptor_capacity != 256:
        allowed.add("descriptor_pool_size")
    if l1_class == "META_HR":
        allowed.update(("l1_mshr_entries", "l1_merge_cap", "l1_missq_entries"))
    elif l1_class == "BANK_HR":
        allowed.add("l1_bank_count")
    elif l1_class != "BASE":
        raise ValueError(f"unknown L1 class {l1_class}")
    return allowed


def artifact_run(cell: Cell, directory: Path) -> dict[str, Any]:
    status = json.loads((directory / "run_status.json").read_text())
    if status.get("status") != "COMPLETE_VALID":
        raise ValueError(f"{directory}: status is {status.get('status')!r}, not COMPLETE_VALID")
    manifest = json.loads((directory / "manifest.json").read_text())
    contract = load_contract(cell)
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
    l2_stream_status = validate_window_stream(l2_windows, "slice", "start_cycle", configured_l2, l2_interval, full_l2)
    # DRAM sampling happens on the 850-MHz DRAM cadence while timestamps are
    # global cycles; source therefore emits adjacent starts 5000 or 5001 apart.
    dram_stream_status = validate_window_stream(dram_windows, "channel", "window_start_cycle", configured_dram, dram_interval, full_dram, 1)
    l2_group_status = validate_time_groups(l2_windows, "slice", "start_cycle", configured_l2)
    dram_group_status = validate_time_groups(dram_windows, "channel", "window_start_cycle", configured_dram)
    cardinality = {
        "configured_l2_slices": configured_l2, "configured_dram_channels": configured_dram,
        "unique_l2_slice_ids": len(slice_ids), "unique_dram_channel_ids": len(channel_ids),
        "l2_window_interval_cycles": l2_interval, "dram_window_interval_cycles": dram_interval,
        "completion_cycles": completion, "expected_l2_window_rows": full_l2 * configured_l2,
        "actual_l2_window_rows": len(l2_windows), "expected_dram_window_rows": full_dram * configured_dram,
        "actual_dram_window_rows": len(dram_windows),
        "l2_stream_key_status": l2_stream_status, "dram_stream_key_status": dram_stream_status,
        "l2_time_group_alignment_status": l2_group_status,
        "dram_time_group_alignment_status": dram_group_status,
        "cardinality_status": "PASS_FULL_WINDOWS_ONLY" if (len(l2_windows) == full_l2 * configured_l2 and
            len(dram_windows) == full_dram * configured_dram and len(slice_ids) == configured_l2 and
            len(channel_ids) == configured_dram and l2_stream_status == "PASS_FULL_WINDOWS_ONLY" and
            dram_stream_status == "PASS_FULL_WINDOWS_ONLY" and l2_group_status == "PASS_EXACT_TIME_GROUP_ALIGNMENT" and
            dram_group_status == "PASS_EXACT_TIME_GROUP_ALIGNMENT") else "FAIL_TOPOLOGY_OR_STREAM_MISMATCH",
        "aggregation_reason": "Producer emits completed 5K intervals only; no partial terminal interval. L2 is per slice; DRAM is per channel. DRAM global-cycle starts are adjacent at 5000/5001 because sampling follows the 850-MHz DRAM cadence.",
    }
    desc = distribution(l2_windows, "descriptor_avg", cell.descriptor_capacity, "samples")
    mshr = distribution(l2_windows, "line_mshr_avg", 128, "samples")
    lower = distribution(l2_windows, "lowerq_avg", 128, "samples")
    sched = distribution(dram_windows, "scheduler_occ_avg", 128, "dram_cycles")
    returnq = distribution(dram_windows, "returnq_occ_avg", 192, "dram_cycles")
    admission = distribution(dram_windows, "bandwidth_util")
    scheduler_full = ratio_distribution(dram_windows, "scheduler_full_cycles", "dram_cycles")
    returnq_full = ratio_distribution(dram_windows, "returnq_full_cycles", "dram_cycles")
    temporal = {
        **{f"descriptor_{key}": value for key, value in desc.items()},
        **{f"line_mshr_{key}": value for key, value in mshr.items()},
        **{f"l2_to_dram_occ_{key}": value for key, value in lower.items()},
        **{f"scheduler_occ_{key}": value for key, value in sched.items()},
        **{f"returnq_occ_{key}": value for key, value in returnq.items()},
        **{f"lower_admission_byte_rate_norm_{key}": value for key, value in admission.items()},
        "scheduler_full_active_fraction": sum((integer(row, "scheduler_full_cycles") or 0) > 0 for row in dram_windows) / len(dram_windows),
        "returnq_full_active_fraction": sum((integer(row, "returnq_full_cycles") or 0) > 0 for row in dram_windows) / len(dram_windows),
        **{f"scheduler_full_{key}": value for key, value in scheduler_full.items()},
        **{f"returnq_full_{key}": value for key, value in returnq_full.items()},
        "native_dram_data_bus_util_window": NA,
        "native_dram_data_bus_window_status": "NOT_RETAINED_PER_5K_WINDOW",
        "read_bytes_windows": field_total(dram_windows, "successful_read_bytes"),
        "write_bytes_windows": field_total(dram_windows, "successful_write_bytes"),
        "descriptor_longest_high_average_window_run": longest_burst(l2_windows, "slice", "start_cycle", "descriptor_avg", .9 * cell.descriptor_capacity, l2_interval),
        "scheduler_longest_high_average_window_run": longest_burst(dram_windows, "channel", "window_start_cycle", "scheduler_occ_avg", .9 * 128, dram_interval, 1),
        **{f"channel_{key}": value for key, value in channel_imbalance(dram_windows, configured_dram).items()},
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
        "dram_write_bytes": dram_total("successful_write_bytes"), "lower_admission_byte_rate_norm": field_weighted(app_dram, "bandwidth_util", "dram_cycles"),
        "terminal_clean": summary0.get("invariants_terminal_clean", NA),
    }
    config_hash = runtime_config_hash(status, manifest, campaign)
    if config_hash == NA:
        raise ValueError(f"{directory}: no runtime config hash in run or campaign manifest")
    binding = contract_binding_status(contract, config_hash)
    if binding != "PASS_RUNTIME_CONFIG_BOUND":
        raise ValueError(f"{directory}: {binding}")
    return {"cell": cell.name, "workload": status["workload"], "variant": status["variant"],
            "core_sha": manifest.get("core_commit", audit.get("core_authoritative_source", NA)),
            "framework_sha": manifest.get("framework_commit", audit.get("framework_authoritative_source", NA)),
            "config_hash": config_hash, "trace_identity": status.get("trace", NA),
            "frequency_mhz": status.get("frequency_mhz", NA), "descriptor_capacity": cell.descriptor_capacity,
            "l1_config_class": cell.l1_class, "source_dir": str(directory), "_contract": contract,
            "config_contract_binding_status": binding,
            **native_dram_data_bus_util(directory, configured_dram), **cardinality, **temporal, **metrics}


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
    for key in ("workload", "variant", "frequency_mhz", "trace_identity"):
        if base[key] != candidate[key]:
            return f"REJECTED_{key.upper()}_MISMATCH"
    base_contract, candidate_contract = base.get("_contract"), candidate.get("_contract")
    if not base_contract or not candidate_contract:
        return "REJECTED_MISSING_CELL_CONTRACT"
    if base_contract.get("semantic_base_id") != candidate_contract.get("semantic_base_id"):
        return "REJECTED_SEMANTIC_BASE_ID_MISMATCH"
    if candidate_contract.get("base_core_sha") != base["core_sha"] or candidate_contract.get("base_framework_sha") != base["framework_sha"]:
        return "REJECTED_BASE_LINEAGE_MISMATCH"
    if candidate_contract.get("candidate_core_sha") != candidate["core_sha"] or candidate_contract.get("candidate_framework_sha") != candidate["framework_sha"]:
        return "REJECTED_CANDIDATE_LINEAGE_MISMATCH"
    source_changed = (base["core_sha"], base["framework_sha"]) != (candidate["core_sha"], candidate["framework_sha"])
    gate = candidate_contract.get("equivalence_gate", {})
    if source_changed and (gate.get("status") != "PASS" or not gate.get("id") or not gate.get("evidence_path") or candidate_contract.get("allowed_source_delta_class") in (None, "NONE")):
        return "REJECTED_CHANGED_SHA_WITHOUT_PASS_EQUIVALENCE"
    expected = expected_allowed_config_fields(candidate["descriptor_capacity"], candidate["l1_config_class"])
    declared = set(candidate_contract.get("allowed_config_fields", []))
    if declared != expected:
        return "REJECTED_DECLARED_ALLOWED_FIELDS_MISMATCH"
    base_config, candidate_config = base_contract["effective_config"], candidate_contract["effective_config"]
    if set(base_config) != set(candidate_config):
        return "REJECTED_EFFECTIVE_CONFIG_KEYSET_MISMATCH"
    changed = {field for field in base_config if base_config[field] != candidate_config[field]}
    if changed != expected:
        return "REJECTED_UNAUTHORIZED_EFFECTIVE_CONFIG_DIFF"
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
                       "dram_read_bytes", "dram_write_bytes", "lower_admission_byte_rate_norm", "native_dram_data_bus_util_weighted_mean",
                       "descriptor_longest_high_average_window_run", "scheduler_longest_high_average_window_run", "channel_traffic_conditioned_cv_p95"):
            left, right = base.get(metric, NA), row.get(metric, NA)
            result[f"delta_{metric}"] = right - left if isinstance(left, (int, float)) and isinstance(right, (int, float)) else NA
        output.append(result)
    return output


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    records = [{field: value for field, value in record.items() if not field.startswith("_")} for record in records]
    fields = list(dict.fromkeys(field for record in records for field in record))
    with path.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=fields, lineterminator="\n"); writer.writeheader(); writer.writerows(records)


def parse_cell(text: str) -> Cell:
    # NAME:ROOT:DESCRIPTOR:L1_CLASS:CONTRACT; ROOT may not contain a colon on Linux.
    try:
        name, root, descriptor, l1_class, contract = text.rsplit(":", 4)
        return Cell(name, Path(root), int(descriptor), l1_class, Path(contract))
    except ValueError as error:
        raise argparse.ArgumentTypeError("cell must be NAME:ROOT:DESCRIPTOR:L1_CLASS:CONTRACT") from error


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
                   "expected_dram_window_rows", "actual_dram_window_rows", "l2_stream_key_status", "dram_stream_key_status",
                   "l2_time_group_alignment_status", "dram_time_group_alignment_status", "cardinality_status", "aggregation_reason")}
                   for row in records]
    temporal_keys = [
        "descriptor_avg", "descriptor_p50", "descriptor_p95", "descriptor_max", "descriptor_near_full_fraction", "descriptor_full_fraction",
        "line_mshr_avg", "line_mshr_p50", "line_mshr_p95", "line_mshr_max", "line_mshr_near_full_fraction", "line_mshr_full_fraction",
        "l2_to_dram_occ_avg", "l2_to_dram_occ_p50", "l2_to_dram_occ_p95", "l2_to_dram_occ_max", "l2_to_dram_occ_near_full_fraction", "l2_to_dram_occ_full_fraction",
        "scheduler_occ_avg", "scheduler_occ_p50", "scheduler_occ_p95", "scheduler_occ_max", "scheduler_occ_near_full_fraction", "scheduler_occ_full_fraction",
        "returnq_occ_avg", "returnq_occ_p50", "returnq_occ_p95", "returnq_occ_max", "returnq_occ_near_full_fraction", "returnq_occ_full_fraction",
        "lower_admission_byte_rate_norm_avg", "lower_admission_byte_rate_norm_p50", "lower_admission_byte_rate_norm_p95", "lower_admission_byte_rate_norm_max", "scheduler_full_active_fraction", "returnq_full_active_fraction",
        "scheduler_full_cycle_fraction", "scheduler_full_window_fraction_p50", "scheduler_full_window_fraction_p95", "scheduler_full_window_fraction_max",
        "returnq_full_cycle_fraction", "returnq_full_window_fraction_p50", "returnq_full_window_fraction_p95", "returnq_full_window_fraction_max",
        "native_dram_data_bus_util_window", "native_dram_data_bus_window_status", "read_bytes_windows", "write_bytes_windows",
        "descriptor_longest_high_average_window_run", "scheduler_longest_high_average_window_run",
        "channel_all_window_max_to_mean_max", "channel_all_window_max_to_mean_p95", "channel_all_window_cv_max", "channel_all_window_cv_p95",
        "channel_active_channels_p50", "channel_active_channels_p95", "channel_active_channels_max", "channel_traffic_conditioned_window_fraction",
        "channel_traffic_conditioned_max_to_mean_p95", "channel_traffic_conditioned_cv_p95", "channel_traffic_weighted_max_to_mean", "channel_traffic_weighted_cv",
    ]
    temporal = [{key: row[key] for key in ("cell", "workload", "variant", "descriptor_capacity", "l1_config_class", *temporal_keys)} for row in records]
    write_csv(args.out / "TEMPORAL_CARDINALITY_AUDIT.csv", cardinality)
    write_csv(args.out / "TEMPORAL_DISTRIBUTIONS.csv", temporal)
    channel_keys = ["cell", "workload", "variant", *[key for key in temporal_keys if key.startswith("channel_")]]
    write_csv(args.out / "CHANNEL_IMBALANCE.csv", [{key: row[key] for key in channel_keys} for row in records])
    native_keys = ("cell", "workload", "variant", "native_dram_snapshot_status", "native_dram_channels_observed",
                   "native_dram_data_bus_util_weighted_mean", "native_dram_data_bus_util_p50",
                   "native_dram_data_bus_util_p95", "native_dram_data_bus_util_max", "native_dram_n_cmd_sum", "source_dir")
    write_csv(args.out / "NATIVE_DRAM_BANDWIDTH.csv", [{key: row[key] for key in native_keys} for row in records])
    write_csv(args.out / "CALIBRATION_MATRIX.csv", records)
    write_csv(args.out / "CALIBRATION_DELTAS.csv", make_deltas(records))
    (args.out / "ANALYSIS_MANIFEST.json").write_text(json.dumps({"schema": "EP_L2_LANE_D_V3", "cells": [{"name": cell.name, "root": str(cell.root), "descriptor_capacity": cell.descriptor_capacity, "l1_class": cell.l1_class, "contract": str(cell.contract_path)} for cell in args.cell], "records": len(records), "workloads": sorted(workloads) if workloads else "all"}, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
