#!/usr/bin/env python3
"""Validate the pre-result SG1 canonical FAST12 promotion contract."""
import argparse
import csv
import hashlib
from pathlib import Path


VARIANTS = {"B16-N", "TC80-N"}
CORE = "6582b9d171330d88b17e8d5294c97704229e3823"
RUNTIME = "4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9"
BASE = "configs/dtc_l1/fast64/FAST64_BASE.config"
BASE_SHA = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
OVERLAYS = {
    "B16-N": ("docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_B16_N_OVERLAY.config", "658a13634cfc4a05e03437ed9b9a3922f9a91c2fce5d16c7b37784cfb38ccda8"),
    "TC80-N": ("docs/dtc_l1/iscas2027/granularity/sg1/config/SG1_TC80_N_OVERLAY.config", "423832831f7d45757fcca350886dcf7a26cdd0158604a3b7c883638d006bbabd"),
}


def rows(path):
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
    authority = {row["workload"]: row for row in rows(args.authority)}
    plan = rows(args.plan)
    expected = {(workload, variant) for workload in authority for variant in VARIANTS}
    actual = {(row["workload"], row["variant"]) for row in plan}
    assert len(plan) == len(expected) == 24
    assert actual == expected and len(actual) == len(plan)
    assert digest(repo / BASE) == BASE_SHA
    for row in plan:
        source = authority[row["workload"]]
        overlay, overlay_sha = OVERLAYS[row["variant"]]
        assert row["schema"] == "SG1_CANONICAL_FAST12_PLAN_V1"
        assert row["stage"] == "D2B_FAST12"
        assert row["canonical_core_source_head"] == CORE
        assert row["canonical_runtime_sha256"] == RUNTIME
        assert row["base_config"] == BASE and row["base_config_sha256"] == BASE_SHA
        assert row["overlay"] == overlay and row["overlay_sha256"] == overlay_sha
        assert digest(repo / overlay) == overlay_sha
        assert row["instructions"] == source["instructions"]
        assert row["trace_list_sha256"] == source["trace_list_sha256"]
        assert row["launch_gate"] == "D2B_G6_12_OF_12_STRICT_PASS+resource_slot"
    print("SG1 canonical FAST12 plan: PASS (24 unique authority-bound cells)")


if __name__ == "__main__":
    main()
