#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out
    gate = json.loads((out / "SIM_TRACE_PREP_GATE.json").read_text())
    assert gate["status"] == "SIM_PLATFORM_NOT_ADMITTED_STOP"
    assert not any(gate["authorization"].values())
    assert all(gate["mechanical_readiness"].values())
    platform = json.loads((out / "PLATFORM_BINDING.json").read_text())
    assert not platform["scope_compatible"]
    assert platform["baseline_config"]["blob"] == "3306caa589baa07c046e16fddd3066351ba10d2c"
    matrix = list(csv.DictReader((out / "L2_CONFIG_MATRIX.tsv").open(), delimiter="\t"))
    assert len(matrix) == 6
    assert {int(row["capacity_mib"]) for row in matrix} == {64, 128, 256}
    assert {row["arm"] for row in matrix} == {"A", "B"}
    assert all(row["authorized_to_run"] == "False" for row in matrix)
    estimate = json.loads((out / "TRACE_SIZE_ESTIMATE.json").read_text())
    assert estimate["pilot_policy"]["required"]
    assert estimate["model"]["loop_warp_iterations_both_arms"] == 1_572_864
    for arm in estimate["arms"].values():
        low, high = arm["estimated_dynamic_warp_instruction_records"]
        assert 0 < low < high
        assert arm["cta_loop_products"] == 786_432
    expected = {}
    for line in (out / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        expected[name] = digest
    actual = {}
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            actual[path.relative_to(out).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected
    print("PASS prep pack validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
