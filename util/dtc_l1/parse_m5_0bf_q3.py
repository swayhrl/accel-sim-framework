#!/usr/bin/env python3
"""Extract Base-only M5.0BF lower-cap fidelity metrics.

This is intentionally separate from the formal M5 result parser: Q3 is a
platform-fidelity diagnostic and must retain the native downstream-pressure
evidence that is emitted in Accel-Sim's perf-counter CSV rather than in the
terminal simulator log.
"""

import argparse
import csv
import gzip
import hashlib
import json
import re
from pathlib import Path


KEY_VALUE = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(.*?)\s*$")
NUMBER = re.compile(r"^-?\d+$")


def parse_terminal_log(path):
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = KEY_VALUE.match(line)
        if match:
            value = match.group(2)
            values[match.group(1)] = int(value) if NUMBER.fullmatch(value) else value
    return values


def last_complete_counter_row(path):
    with gzip.open(path, "rt", encoding="utf-8", errors="replace", newline="") as fh:
        rows = csv.reader(fh)
        header = next(rows, None)
        if not header:
            raise ValueError("perf counter has no header")
        last = None
        for row in rows:
            if len(row) == len(header):
                last = row
        if last is None:
            raise ValueError("perf counter has no complete data row")
    return dict(zip(header, last))


def number(value, name):
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("non-integral counter %s=%r" % (name, value)) from exc


def pressure(counter, prefix):
    values = [number(value, key) for key, value in counter.items()
              if key.startswith(prefix)]
    if not values:
        raise ValueError("missing perf-counter family " + prefix)
    return {
        "subpartitions": len(values),
        "sum": sum(values),
        "max": max(values),
        "nonzero_subpartitions": sum(value != 0 for value in values),
    }


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required(values, key):
    if key not in values:
        raise ValueError("missing terminal metric " + key)
    return number(values[key], key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--perf-counter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--core-sha", required=True)
    parser.add_argument("--framework-sha", required=True)
    parser.add_argument("--config-file", type=Path, required=True)
    parser.add_argument("--workload-file", type=Path, required=True)
    args = parser.parse_args()

    try:
        terminal = parse_terminal_log(args.log)
        counter = last_complete_counter_row(args.perf_counter)
        cycles = required(terminal, "gpu_tot_sim_cycle")
        instructions = required(terminal, "gpu_tot_sim_insn")
        if cycles <= 0:
            raise ValueError("gpu_tot_sim_cycle must be positive")
        lower_occupancy_cycle_sum = required(
            terminal, "DTC_L1_lower_outstanding_cycle_sum")
        lower_occupancy_sample_cycles = required(
            terminal, "DTC_L1_lower_outstanding_sample_cycles")
        if lower_occupancy_sample_cycles <= 0:
            raise ValueError("DTC_L1_lower_outstanding_sample_cycles must be positive")
        metrics = {
            "base_cycles": cycles,
            "base_instructions": instructions,
            "base_ipc": instructions / cycles,
            "lower_outstanding_cap": required(terminal, "DTC_L1_lower_outstanding_cap"),
            "lower_outstanding_average": lower_occupancy_cycle_sum /
                                         lower_occupancy_sample_cycles,
            "lower_outstanding_peak": required(terminal, "DTC_L1_lower_outstanding_peak"),
            "lower_outstanding_cycle_sum": lower_occupancy_cycle_sum,
            "lower_outstanding_sample_cycles": lower_occupancy_sample_cycles,
            "lower_cap_full_events": required(terminal, "DTC_L1_lower_cap_full_events"),
            "lower_cap_full_cycles": required(
                terminal, "DTC_L1_nonexclusive_lower_cap_full_cycles"),
            "pib_full_events": required(terminal, "DTC_L1_pib_full_events"),
            "pib_full_cycles": required(terminal, "DTC_L1_nonexclusive_pib_full_cycles"),
            "mshr_entry_full_cycles": required(terminal, "DTC_L1_nonexclusive_mshr_entry_full_cycles"),
            "mshr_merge_full_cycles": required(terminal, "DTC_L1_nonexclusive_mshr_merge_full_cycles"),
            "true_tag_cacheline_allocation_fail_events": required(
                terminal, "DTC_L1_baseline_l1d_line_allocation_fail_events"),
            "tag_bank_conflict_cycles": required(terminal, "DTC_L1_nonexclusive_tag_bank_conflict_cycles"),
            "native_gpu_stall_dramfull": required(terminal, "gpu_stall_dramfull"),
            "native_chiplet_queue_full": pressure(counter, "chiplet_queue_full_"),
            "native_l2_dram_queue_full": pressure(counter, "L2_dram_queue_full_"),
        }
    except ValueError as exc:
        parser.error(str(exc))

    result = {
        "schema": "dtc_l1_m5_0bf_q3_v2",
        "provenance": {
            "candidate": args.candidate,
            "core_sha": args.core_sha,
            "framework_sha": args.framework_sha,
            "config_file": str(args.config_file),
            "config_sha256": sha256(args.config_file),
            "workload_file": str(args.workload_file),
            "workload_sha256": sha256(args.workload_file),
            "source_log": str(args.log),
            "perf_counter": str(args.perf_counter),
            "perf_counter_sha256": sha256(args.perf_counter),
        },
        "metrics": metrics,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
