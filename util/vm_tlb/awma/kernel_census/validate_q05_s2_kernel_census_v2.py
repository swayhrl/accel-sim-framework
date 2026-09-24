#!/usr/bin/env python3
"""Validate the immutable V2 census artifacts emitted from accepted authority."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sqlite", type=Path, required=True)
    parser.add_argument("--v1-inventory", type=Path, required=True)
    args = parser.parse_args()
    assert sha256(args.sqlite) == "17d9551472a4b8d090a6aa9437ff9a74d90f336ae1ab15189ed108da1041734d"
    assert sha256(args.v1_inventory) == "7825697aa23647daee6a38ac4436029c5746fe29a468d303520d3884f2b4abef"
    inventory = args.out / "ALL_KERNEL_LAUNCHES_V2.tsv"
    assert sha256(inventory) == "222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a"
    with inventory.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 34677
    assert sum(1 for row in rows if row["phase_class"] == "UNKNOWN") == 0
    assert sum(1 for row in rows if row["v1_phase"] == "UNKNOWN" and row["phase_class"] != "UNKNOWN") == 605
    assert sum(1 for row in rows if row["v1_phase"] != "UNKNOWN" and (row["v1_phase"], row["v1_decode_step"]) != (row["phase"], row["decode_step"])) == 0
    assert {key: sum(1 for row in rows if row["phase_class"] == key) for key in ("PREFILL", "DECODE", "AUXILIARY")} == {"PREFILL": 980, "DECODE": 33664, "AUXILIARY": 33}
    assert sum(int(row["duration_ns"]) for row in rows) == 154876910
    assert all(row["assignment_method"] in {"CUPTI_CORRELATED_RUNTIME_START_IN_SAME_THREAD_NVTX", "AUXILIARY_RUNTIME_START_OUTSIDE_ALL_C16_PHASE_RANGES"} for row in rows)
    print("V2_CENSUS_VALIDATION_PASS")


if __name__ == "__main__":
    main()
