#!/usr/bin/env python3
"""Validate the frozen SG4A missing-point FAST12 matrix without running it."""
import argparse
import csv
import hashlib
from pathlib import Path


MODES = {"IO", "OO"}
POINTS = {32, 64, 80}
CORE = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
RUNTIME = "462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9"
MAP = {
    (32, "IO"): (64, "configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_32/FAST64_SENS_LOGICAL_32KB_IO.config", None),
    (32, "OO"): (64, "configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_32/FAST64_SENS_LOGICAL_32KB_OO.config", None),
    (64, "IO"): (128, "configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_64/FAST64_SENS_LOGICAL_64KB_IO.config", None),
    (64, "OO"): (128, "configs/dtc_l1/fast64/sensitivity_frozen_v2/logical_64/FAST64_SENS_LOGICAL_64KB_OO.config", None),
    (80, "IO"): (160, "configs/dtc_l1/fast64/FAST64_IO.config", "docs/dtc_l1/iscas2027/granularity/sg4a/config/SG4A_LOGICAL80_IO_OVERLAY.config"),
    (80, "OO"): (160, "configs/dtc_l1/fast64/FAST64_OO.config", "docs/dtc_l1/iscas2027/granularity/sg4a/config/SG4A_LOGICAL80_OO_OVERLAY.config"),
}


def table(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--authority", required=True, type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    authority = {r["workload"]: r for r in table(args.authority)}
    plan = table(args.plan)
    expected = {(w, m, k) for w in authority for m in MODES for k in POINTS}
    actual = {(r["workload"], r["mode"], int(r["logical_kib"])) for r in plan}
    assert len(plan) == len(expected) == 72
    assert actual == expected
    assert len(actual) == len(plan), "duplicate FAST12 logical-point cell"
    for row in plan:
        key = (int(row["logical_kib"]), row["mode"])
        sets, config, overlay = MAP[key]
        source = authority[row["workload"]]
        assert row["schema"] == "SG4A_FAST12_MISSING_POINT_PLAN_V1"
        assert row["stage"] == "SG4A.2" and row["core_source_head"] == CORE
        assert row["runtime_sha256"] == RUNTIME
        assert row["logical_sets"] == str(sets)
        assert row["physical_pool_lines"] == "640" and row["physical_pool_bytes"] == "81920"
        assert row["instructions"] == source["instructions"]
        assert row["trace_list_sha256"] == source["trace_list_sha256"]
        assert row["base_config"] == config and digest(repo / config) == row["base_config_sha256"]
        if overlay is None:
            assert row["overlay"] == "NONE" and row["overlay_sha256"] == "NONE"
        else:
            assert row["overlay"] == overlay and digest(repo / overlay) == row["overlay_sha256"]
    print("SG4A FAST12 missing-point plan: PASS (72 unique frozen cells)")


if __name__ == "__main__":
    main()
