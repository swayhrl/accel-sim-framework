#!/usr/bin/env python3
"""Fail-closed static validator for the fixed canonical SG5 C2 matrix."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


WORKLOADS = {"ATAX", "BICG", "GESUMMV", "Btree", "2DConvolution", "Gaussian"}
VARIANTS = {"B16-S", "TC80-S", "B16-N", "TC80-N", "IO", "OO"}
CORE = "1406840bc2000c9f5292f6db64fa84e115568b0c"
RUNTIME = "7d3e80859e482d3a7029e4300a87a61c71c09485d6cfd2c7c0dd97aa02fd89a7"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    args = parser.parse_args()
    plan, authority = read(args.plan), {r["workload"]: r for r in read(args.authority)}
    expected = {(workload, variant) for workload in WORKLOADS for variant in VARIANTS}
    observed = {(r["workload"], r["variant"]) for r in plan}
    assert len(plan) == len(expected) == 36 and observed == expected
    for row in plan:
        assert row["schema"] == "SG5_CANONICAL_G6_PLAN_V1"
        assert row["stage"] == "SG5.C2" and row["observer"] == "1"
        assert row["canonical_core_source_head"] == CORE
        assert row["canonical_runtime_sha256"] == RUNTIME
        assert row["workload"] in authority
        assert row["instructions"] == authority[row["workload"]]["instructions"]
        assert row["trace_list_sha256"] == authority[row["workload"]]["trace_list_sha256"]
        assert row["launch_gate"] == "SG5_C1_PASS+actual_live_workers_below_target"
        assert row["evidence_boundary"] == "Diagnostic observer row only; never primary performance evidence."
    print("SG5 canonical C2 plan: PASS (36 unique authority-bound observer-only cells)")


if __name__ == "__main__":
    main()
