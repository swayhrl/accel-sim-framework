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
    assert gate["status"] == "READY_FOR_NATIVE_CAUSAL_SCREEN"
    assert gate["source_isolation"]["same_patched_kernel_for_all_cells"]
    assert gate["source_isolation"]["only_state_dependent_memory_semantic"] == "qweight/qzeros/scales replica base address"
    assert not gate["source_isolation"]["replica_address_arithmetic_has_branch"]
    assert gate["memory"]["all_cells_pass"]
    assert gate["launch"]["matrix_rows"] == 8
    artifact = out / gate["bindings"]["patch_artifact"]
    assert digest(artifact) == gate["bindings"]["patch_artifact_sha256"]
    assert hashlib.sha256(gzip.decompress(artifact.read_bytes())).hexdigest() == gate["bindings"]["patch_sha256"]
    assert digest(out / "MEMORY_BUDGET.tsv") == gate["bindings"]["memory_budget_sha256"]
    assert digest(out / "EXPECTED_LAUNCH.tsv") == gate["bindings"]["expected_launch_sha256"]
    memory = list(csv.DictReader((out / "MEMORY_BUDGET.tsv").open(), delimiter="\t"))
    launches = list(csv.DictReader((out / "EXPECTED_LAUNCH.tsv").open(), delimiter="\t"))
    assert len(memory) == len(launches) == 8
    assert all(row["pass"] == "True" for row in memory)
    assert {row["state"] for row in launches} == {"SHARED", "PER_MTILE"}
    for k in ("2560", "3072"):
        for split, grid, scratch in (("8", "49152", "201326592"), ("1", "6144", "25165824")):
            rows = [r for r in launches if r["K"] == k and r["split_k_iters"] == split]
            assert len(rows) == 2
            assert {r["gemm_grid"] for r in rows} == {grid}
            assert {r["scratch_bytes"] for r in rows} == {scratch}
    if args.full:
        required = {"AUTHORITY.json", "PATCH_SEMANTIC_DIFF.md", "REPLICA_CONTRACT.json", "RUNNER_CONTRACT.md", "SCIENTIFIC_BOUNDARY.md", "SHA256SUMS"}
        assert required <= {p.name for p in out.iterdir()}
        expected = {}
        for line in (out / "SHA256SUMS").read_text().splitlines():
            value, name = line.split("  ", 1)
            expected[name] = value
        actual = {p.relative_to(out).as_posix(): digest(p) for p in sorted(out.rglob("*")) if p.is_file() and p.name != "SHA256SUMS"}
        assert actual == expected
    print("PASS cross-M prep validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
