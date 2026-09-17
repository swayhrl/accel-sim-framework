#!/usr/bin/env python3
"""Fail closed for the frozen SG3 G4 observer-on scheduling matrix.

This checks only the pre-result experiment contract: every authorized G4
workload/mode/resource point is present exactly once and agrees with the
frozen FAST12 authority.  It deliberately does not read or interpret any
simulation output.
"""
import argparse
import csv
import hashlib
from pathlib import Path


WORKLOADS = {"BICG", "GESUMMV", "Btree", "2DConvolution"}
MODES = {"IO", "OO"}
POINTS = {
    "capacity": {"half", "base", "double"},
    "mshr": {"half", "base", "double", "quad"},
    "cap": {"512", "1024", "2048", "4096", "8192"},
}
STAGES = {"capacity": "SG3.2", "mshr": "SG3.3", "cap": "SG3.4"}
CORE = "9b6bd33f3fb3236fd493db2dd7e11d356d1f272f"
RUNTIME = "ae9a51942e99c10ab2ffafd1c68bd5f8709911890a5f15283336dfc29b70680d"
OBSERVER_SHA = "916dd5cf98b57bb99a20ac11871a670b00db293ce7c336f0f88ee8b75469fad2"


def rows(path: Path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--authority", required=True, type=Path)
    args = parser.parse_args()
    authority = {row["workload"]: row for row in rows(args.authority)}
    plan = rows(args.plan)
    expected = {(dim, point, workload, mode)
                for dim, values in POINTS.items()
                for point in values for workload in WORKLOADS for mode in MODES}
    actual = {(row["dimension"], row["point"], row["workload"], row["mode"])
              for row in plan}
    assert len(plan) == len(expected) == 96, (len(plan), len(expected))
    assert actual == expected, (sorted(expected - actual), sorted(actual - expected))
    assert len(actual) == len(plan), "duplicate SG3 G4 cell"
    for row in plan:
        assert row["schema"] == "SG3_G4_OBSERVER_ON_PLAN_V1"
        assert row["stage"] == STAGES[row["dimension"]]
        assert row["observer"] == "1"
        assert row["core_source_head"] == CORE
        assert row["runtime_sha256"] == RUNTIME
        assert row["observer_overlay_sha256"] == OBSERVER_SHA
        source = authority[row["workload"]]
        assert row["instructions"] == source["instructions"]
        assert row["trace_list_sha256"] == source["trace_list_sha256"]
        if row["point"] == "base":
            assert row["dimension_overlay"] == "NONE"
            assert row["dimension_overlay_sha256"] == "NONE"
        else:
            assert row["dimension_overlay"].startswith("config/SG3_")
            assert len(row["dimension_overlay_sha256"]) == 64
            overlay = args.plan.parent / row["dimension_overlay"]
            assert overlay.is_file()
            assert sha256(overlay) == row["dimension_overlay_sha256"]
    print("SG3 G4 observer-on plan: PASS (96 unique authority-bound cells)")


if __name__ == "__main__":
    main()
