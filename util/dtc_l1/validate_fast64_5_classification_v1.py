#!/usr/bin/env python3
"""Fail-closed completeness validator; it never infers causal classes."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree", "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
HEADINGS = ("workload", "primary_class", "secondary_classes", "evidence_paths", "evidence_backed_rationale", "validator_status")
CLASSES = {"CONVENTIONAL_STRUCTURE_LIMITED", "LOW_STRUCTURAL_PRESSURE", "DOWNSTREAM_PLATFORM_LIMITED", "COMPUTE_REUSE_DOMINATED", "TRAFFIC_SENSITIVE", "IO_HOL_SENSITIVE", "OO_RECLAIM_SENSITIVE", "GENUINE_MECHANISM_NON_BENEFICIARY", "IMPLEMENTATION_MODELING_ISSUE"}


def validate(path: Path, evidence_root: Path | None = None) -> list[dict[str, str]]:
    """Validate supplied causal evidence without inferring any classification."""
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if len(rows) != len(ROSTER) or any(tuple(row) != HEADINGS for row in rows) or {row["workload"] for row in rows} != set(ROSTER):
        raise RuntimeError("FAST64_5_CLASSIFICATION_EXACT_FAST12_REQUIRED")
    for row in rows:
        primary = row["primary_class"]
        secondary = {item for item in row["secondary_classes"].split(",") if item}
        if primary not in CLASSES or not secondary.issubset(CLASSES) or primary in secondary:
            raise RuntimeError("FAST64_5_CLASSIFICATION_ENUM_INVALID=" + row["workload"])
        if primary == "IMPLEMENTATION_MODELING_ISSUE" or "IMPLEMENTATION_MODELING_ISSUE" in secondary:
            raise RuntimeError("FAST64_5_IMPLEMENTATION_ISSUE_BLOCKS_PASS=" + row["workload"])
        for key in ("evidence_paths", "evidence_backed_rationale"):
            if not row[key].strip():
                raise RuntimeError("FAST64_5_CLASSIFICATION_EVIDENCE_MISSING=" + row["workload"])
        if evidence_root is not None:
            for raw in row["evidence_paths"].split(";"):
                candidate = Path(raw.strip())
                if not candidate.is_absolute():
                    candidate = evidence_root / candidate
                if not candidate.is_file():
                    raise RuntimeError("FAST64_5_CLASSIFICATION_EVIDENCE_PATH_MISSING=" + row["workload"])
    return rows

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classification", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path)
    args = parser.parse_args()
    rows = validate(args.classification, args.evidence_root)
    print("FAST64_5_CLASSIFICATION_V1_PASS rows=12")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
