#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    out = args.out
    gate = json.loads((out / "EARLY_GATE.json").read_text())
    assert gate["status"] == "READY_FOR_GROUPED_CTA_NATIVE_BASELINE"
    assert gate["source_isolation"]["same_patched_kernel_all_cells"]
    assert gate["source_isolation"]["mapping_select_branch_free"]
    assert gate["source_isolation"]["only_intentional_device_semantic_change"] == "logical CTA to (Mtile,Ntile) mapping"
    assert gate["bijection"]["all_rows_pass"] and gate["address_set"]["all_cases_pass"]
    artifact = out / gate["bindings"]["patch_artifact"]
    assert digest(artifact) == gate["bindings"]["patch_artifact_sha256"]
    assert hashlib.sha256(gzip.decompress(artifact.read_bytes())).hexdigest() == gate["bindings"]["patch_sha256"]
    assert digest(out / "MAPPING_BIJECTION.tsv") == gate["bindings"]["mapping_bijection_sha256"]
    assert digest(out / "ADDRESS_SET_INVARIANCE.json") == gate["bindings"]["address_set_invariance_sha256"]
    assert digest(out / "EXPECTED_LAUNCH.tsv") == gate["bindings"]["expected_launch_sha256"]
    rows = list(csv.DictReader((out / "MAPPING_BIJECTION.tsv").open(), delimiter="\t"))
    assert len(rows) == 4 and all(row["bijection_pass"] == "True" for row in rows)
    assert {row["same_N_adjacent_M_linear_distance"] for row in rows if row["mapping"] == "ROW"} == {"384"}
    assert {row["same_N_adjacent_M_linear_distance"] for row in rows if row["mapping"] == "GROUP_M16"} == {"1"}
    address = json.loads((out / "ADDRESS_SET_INVARIANCE.json").read_text())
    assert address["all_cases_pass"] and len(address["cases"]) == 4
    assert all(all(case["object_unions_equal"].values()) for case in address["cases"])
    launches = list(csv.DictReader((out / "EXPECTED_LAUNCH.tsv").open(), delimiter="\t"))
    assert len(launches) == 8
    if args.full:
        required = {"AUTHORITY.json", "PATCH_SEMANTIC_DIFF.md", "MEMORY_BUDGET.tsv", "ROW_CALIBRATION.tsv", "RUNNER_CONTRACT.md", "SCIENTIFIC_BOUNDARY.md", "SHA256SUMS"}
        assert required <= {p.name for p in out.iterdir()}
        expected = {}
        for line in (out / "SHA256SUMS").read_text().splitlines():
            value, name = line.split("  ", 1)
            expected[name] = value
        actual = {p.relative_to(out).as_posix(): digest(p) for p in sorted(out.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"}
        assert actual == expected
    print("PASS grouped CTA prep validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
