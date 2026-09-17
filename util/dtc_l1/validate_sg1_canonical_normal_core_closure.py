#!/usr/bin/env python3
"""Fail-closed audit of the frozen SG1 canonical-NORMAL Core closure."""

import argparse
import csv
import subprocess
from pathlib import Path


BASE = "95ccdb7a056f2d53f740d90869785cac6d4ee0f5"
CANONICAL = "6582b9d171330d88b17e8d5294c97704229e3823"
EXPECTED_PATHS = {"src/gpgpu-sim/gpu-cache.cc", "src/gpgpu-sim/gpu-cache.h"}
# The candidate cac1 series contains the same fixes plus two explicitly
# excluded diagnostic commits.  Stable patch IDs prove repair equivalence
# without treating the debug-only files as canonical science-path changes.
EQUIVALENT_PATCHES = (
    ("c0509ee04027f06053558abd90a24c6429643a9c", "6ea5b7824d8d53709777699864456084def81f2c"),
    ("fc643bf4c741ee750588005067825061873d0c02", "d772de2d31ccc1b0c7f9a7954034fda116ae64d1"),
    ("91d15a4f4f55f9458ae520677f05eb2ec8b7fa06", "b838fb6f58a90c6519b65bfaf4c680a3fbf83753"),
    (CANONICAL, "cac1ea8e7020ffcd739fc800f7d7107d216a8bb6"),
)


def git(repo, *args, input_text=None):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_text,
        text=True,
        check=True,
        capture_output=True,
    ).stdout


def patch_id(repo, commit):
    patch = git(repo, "show", "--format=", commit)
    return git(repo, "patch-id", "--stable", input_text=patch).split()[0]


def rows(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-repo", required=True, type=Path)
    parser.add_argument("--closure", required=True, type=Path)
    args = parser.parse_args()
    repo = args.core_repo.resolve()
    closure = rows(args.closure)

    assert any(row["commit"] == CANONICAL and row["classification"] == "CANONICAL_NORMAL_CORE_COMMIT" for row in closure)
    required = {"REQUIRED_CORRECTNESS_FIX", "REQUIRED_NORMAL_FIX", "REQUIRED_SCOPE_FIX"}
    assert required <= {row["classification"] for row in closure}
    for row in closure:
        if row["classification"].startswith("REQUIRED") or row["classification"] == "CANONICAL_NORMAL_CORE_COMMIT":
            assert row["affects_dtc_io"] == "NO"
            assert row["affects_dtc_oo"] == "NO"
            assert row["affects_l2"] == "NO"
            assert row["affects_config"] == "NO"

    assert git(repo, "merge-base", BASE, CANONICAL).strip() == BASE
    changed = set(filter(None, git(repo, "diff", "--name-only", f"{BASE}..{CANONICAL}").splitlines()))
    assert changed == EXPECTED_PATHS
    for left, right in EQUIVALENT_PATCHES:
        assert patch_id(repo, left) == patch_id(repo, right)

    print("SG1 canonical NORMAL Core closure: PASS (five repair patches, cache-only scope, candidate-equivalent)")


if __name__ == "__main__":
    main()
