#!/usr/bin/env python3
"""Validate mechanical coverage of the SG3.0 L2 source/config field map."""

import argparse
import csv
from pathlib import Path


REQUIRED_SUBJECTS = {
    "source_basis",
    "FAST64_IO/OO dl2", "cache_type", "sets", "line_size_bytes", "ways",
    "replacement_policy", "write_policy", "allocation_policy",
    "write_allocate_policy", "set_index_function", "atom_or_sector_bytes",
    "MSHR_type", "MSHR_entries", "MSHR_merge_limit", "cache_miss_queue",
    "result_fifo_entries", "data_port_width_bytes_per_cache_cycle",
    "L2_bank_count", "aggregate_L2_data_capacity", "rop_delay_cycles",
    "L2_terminal_stats", "dtc_lower_outstanding_cap", "scope_guard",
}
DL2 = "S:128:128:16,L:B:m:L:L,A:192:4,32:0,32"


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def effective_value(config, key):
    values = [line.split(maxsplit=1)[1].strip() for line in config.read_text(encoding="utf-8").splitlines()
              if line.startswith(key + " ")]
    assert values, f"missing {key} in {config}"
    return values[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--field-map", required=True, type=Path)
    parser.add_argument("--io-config", required=True, type=Path)
    parser.add_argument("--oo-config", required=True, type=Path)
    args = parser.parse_args()
    table = rows(args.field_map)
    subjects = [row["subject"] for row in table]
    assert set(subjects) == REQUIRED_SUBJECTS, sorted(REQUIRED_SUBJECTS - set(subjects))
    assert len(subjects) == len(set(subjects)), "duplicate field-map subject"
    for row in table:
        assert row["parser_or_source_meaning"].strip()
        assert row["scope"].strip()
        assert row["resource_or_semantic_effect"].strip()
        assert row["available_terminal_counter_or_evidence"].strip()
        assert row["config_only_change"].strip()
        assert row["latency_relation"].strip()
        assert row["evidence"].strip()
    by_subject = {row["subject"]: row for row in table}
    assert by_subject["FAST64_IO/OO dl2"]["configured_value"] == DL2
    assert by_subject["dtc_lower_outstanding_cap"]["configured_value"] == "8192"
    assert by_subject["dtc_lower_outstanding_cap"]["scope"].startswith("one GPU-wide")
    assert "per L2 bank" in by_subject["MSHR_entries"]["scope"]
    assert "per L2 bank" in by_subject["cache_miss_queue"]["scope"]
    assert effective_value(args.io_config, "-gpgpu_cache:dl2") == DL2
    assert effective_value(args.oo_config, "-gpgpu_cache:dl2") == DL2
    assert effective_value(args.io_config, "-gpgpu_dtc_l1_lower_outstanding_cap") == "8192"
    assert effective_value(args.oo_config, "-gpgpu_dtc_l1_lower_outstanding_cap") == "8192"
    print("SG3 L2 config field map: PASS (24 mapped fields, IO/OO effective settings agree)")


if __name__ == "__main__":
    main()
