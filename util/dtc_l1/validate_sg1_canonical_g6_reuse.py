#!/usr/bin/env python3
"""Fail-closed audit for reusing D2B canonical smoke rows as SG1 G6 cells."""
import argparse
import csv
import json
from pathlib import Path

CORE = "6582b9d171330d88b17e8d5294c97704229e3823"
RUNTIME = "4fcac62cd7bdccc5a49cc77950ffc45c60d5fce7c4ee44bba877e1fef2d07ef9"
BASE = "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"
TRACE_CONFIG = "19dd14b3a4b6c1a1cb2833bd091f0dbd485ad79336ef7d4b0c9db1f7c46f504e"
OVERLAY = {
    "B16-N": ("658a13634cfc4a05e03437ed9b9a3922f9a91c2fce5d16c7b37784cfb38ccda8", "32x4x128=128_lines=16384_bytes"),
    "TC80-N": ("423832831f7d45757fcca350886dcf7a26cdd0158604a3b7c883638d006bbabd", "32x20x128=640_lines=81920_bytes"),
}


def rows(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def kv(path):
    return {k: v for k, v in (line.split("\t", 1) for line in Path(path).read_text().splitlines() if "\t" in line)}


def require(actual, expected, label):
    if actual != expected:
        raise SystemExit(f"SG1 canonical G6 reuse FAIL: {label}: {actual!r} != {expected!r}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True)
    parser.add_argument("--authority", required=True)
    parser.add_argument("--smoke", required=True)
    args = parser.parse_args()
    authority = {r["workload"]: r for r in rows(args.authority)}
    plan = {(r["workload"], r["variant"]): r for r in rows(args.plan)}
    smoke = [r for r in rows(args.smoke) if r["workload"] in {"BICG", "Btree"}]
    require(len(smoke), 4, "four reusable smoke rows")
    for row in smoke:
        key = (row["workload"], row["variant"])
        planned = plan.get(key)
        if planned is None or planned["planned_provenance"] != "REUSE_D2B_SMOKE_ONLY_IF_EXACT_IDENTITY_AND_STRICT_PASS":
            raise SystemExit(f"SG1 canonical G6 reuse FAIL: not reusable plan cell {key}")
        require(row["status"], "STRICT_PASS", f"{key} smoke status")
        manifest = kv(Path(row["run_dir"]) / "RUN_MANIFEST.tsv")
        terminal = kv(Path(row["run_dir"]) / "RUN_TERMINAL.tsv")
        receipt = json.loads((Path(row["run_dir"]) / "VALIDATION.json").read_text())
        for field, expected in {
            "workload": row["workload"], "variant": row["variant"], "core_source_head": CORE,
            "simulator_sha256": RUNTIME, "base_config_sha256": BASE,
            "trace_config_sha256": TRACE_CONFIG, "trace_list_sha256": authority[row["workload"]]["trace_list_sha256"],
            "expected_instructions": authority[row["workload"]]["instructions"], "effective_pib": "8", "effective_mshr": "32",
            "overlay_config_sha256": OVERLAY[row["variant"]][0], "normal_cache_geometry": OVERLAY[row["variant"]][1],
        }.items():
            require(manifest.get(field), expected, f"{key} {field}")
        require(terminal.get("simulator_exit_status"), "0", f"{key} natural exit")
        require(receipt.get("status"), "PASS", f"{key} strict receipt")
        require(all(receipt.get("checks", {}).values()), True, f"{key} all strict checks")
    print("SG1 canonical G6 reuse: PASS (4 exact-identity D2B smoke rows)")


if __name__ == "__main__":
    main()
