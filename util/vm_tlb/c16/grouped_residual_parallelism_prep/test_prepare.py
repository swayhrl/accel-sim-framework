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
    assert gate["status"] == "READY_FOR_RESIDUAL_PARALLELISM_NATIVE_SCREEN"
    assert gate["source_isolation"]["same_compiled_target_kernel_all_cells"]
    assert gate["source_isolation"]["all_science_cells_mapping_mode"] == 1
    assert not gate["source_isolation"]["M_dependent_GEMM_body_branch"]
    assert gate["footprint"]["weight_side_bytes"] == 26_148_864
    assert gate["footprint"]["weight_side_over_64MiB"] == 0.3896484375
    assert gate["mapping"]["all_8_rows_pass"] and gate["mapping"]["all_address_sets_closed"]
    artifact = out / gate["bindings"]["patch_artifact"]
    assert digest(artifact) == gate["bindings"]["patch_artifact_sha256"]
    assert hashlib.sha256(gzip.decompress(artifact.read_bytes())).hexdigest() == gate["bindings"]["patch_sha256"]
    for key, name in (("mapping_proof_sha256", "MAPPING_BIJECTION.tsv"), ("address_set_audit_sha256", "ADDRESS_SET_AUDIT.json"), ("footprint_table_sha256", "FOOTPRINT_AND_MEMORY_BUDGET.tsv"), ("expected_launch_sha256", "EXPECTED_LAUNCH.tsv"), ("synthetic_contract_sha256", "SYNTHETIC_CONTRACT.json")):
        assert digest(out / name) == gate["bindings"][key]
    mappings = list(csv.DictReader((out / "MAPPING_BIJECTION.tsv").open(), delimiter="\t"))
    launches = list(csv.DictReader((out / "EXPECTED_LAUNCH.tsv").open(), delimiter="\t"))
    memory = list(csv.DictReader((out / "FOOTPRINT_AND_MEMORY_BUDGET.tsv").open(), delimiter="\t"))
    assert len(mappings) == len(launches) == len(memory) == 8
    assert all(row["bijection_and_coverage_pass"] == "True" for row in mappings)
    assert all(row["memory_pass"] == "True" for row in memory)
    expected_grids = {("1", "1"): "96", ("1", "8"): "768", ("16", "1"): "96", ("16", "8"): "768", ("32", "1"): "192", ("32", "8"): "1536", ("64", "1"): "384", ("64", "8"): "3072"}
    assert {(r["M"], r["split_k_iters"]): r["gemm_grid"] for r in launches} == expected_grids
    assert {(r["M"], r["reduction_grid"]) for r in launches if r["split_k_iters"] == "8"} == {("1", "24"), ("16", "384"), ("32", "768"), ("64", "1536")}
    synth = json.loads((out / "SYNTHETIC_CONTRACT.json").read_text())
    assert synth["status"] == "PASS_CPU_REFERENCE" and synth["weight_side_identical_for_all_M_and_split"]
    if args.full:
        required = {"AUTHORITY.json", "PATCH_SEMANTIC_DIFF.md", "RUNNER_CONTRACT.md", "SCIENTIFIC_BOUNDARY.md", "SHA256SUMS"}
        assert required <= {p.name for p in out.iterdir()}
        expected = {}
        for line in (out / "SHA256SUMS").read_text().splitlines():
            value, name = line.split("  ", 1)
            expected[name] = value
        actual = {p.relative_to(out).as_posix(): digest(p) for p in sorted(out.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"}
        assert actual == expected
    print("PASS residual parallelism prep validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
