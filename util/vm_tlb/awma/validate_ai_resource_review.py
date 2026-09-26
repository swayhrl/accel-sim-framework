#!/usr/bin/env python3
"""Validate the AI resource characterization review pack and raw closure."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


PACK = Path("/root/workspace/accel-sim-framework-awma-ai-gpu-resource-bottleneck-characterization-v1/docs/vm_tlb/review_packs/AWMA_AI_GPU_RESOURCE_BOTTLENECK_CHARACTERIZATION_V1")
REQUIRED = {
    "README.md", "REPORT.md", "TARGET_SUITE_PREREG.tsv",
    "RESOURCE_DIAGNOSTIC_REGISTRY.tsv", "RESOURCE_KNOB_SOURCE_AUDIT.md",
    "RESOURCE_KNOB_AUDIT_CORRECTION.tsv", "BASELINE_BOTTLENECK_MATRIX.tsv",
    "TARGET_DOMAIN_PREREG.tsv", "UPPER_BOUND_SELECTION.tsv",
    "RESOURCE_2X_MATRIX.tsv", "RESOURCE_UPPER_BOUND_MATRIX.tsv",
    "RESOURCE_SATURATION_MAP.tsv", "AI_FAMILY_RESOURCE_MAP.md",
    "CROSS_SCALE_ANALYSIS.md", "CLOSEST_WORK_SCREEN.md",
    "PROTOTYPE_DECISION.md", "ENGINEERING_DEVIATIONS.md",
    "RAW_DATA_INDEX.tsv", "SHA256SUMS",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (PACK / name).open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> int:
    errors: list[str] = []
    missing = sorted(REQUIRED - {path.name for path in PACK.iterdir() if path.is_file()})
    if missing:
        errors.append(f"missing files: {missing}")
    if any(PACK.glob("ARCH_PROBLEM_CARD_*.md")):
        errors.append("problem card exists despite failed gate")
    report = (PACK / "REPORT.md").read_text()
    if "AI_RESOURCE_MAP_COMPLETE_NO_ACTIONABLE_PROBLEM" not in report:
        errors.append("final status missing")

    targets = rows("TARGET_SUITE_PREREG.tsv")
    if len(targets) != 8 or sum(row["exact_role"] == "LOW_DEMAND_CONTROL" for row in targets) != 1:
        errors.append("target suite shape mismatch")
    domains = rows("TARGET_DOMAIN_PREREG.tsv")
    if len(domains) != 8:
        errors.append("domain prereg shape mismatch")
    if next(row for row in domains if row["target"] == "M2")["arm_1"] != "NONE":
        errors.append("M2 received a diagnostic")

    two = rows("RESOURCE_2X_MATRIX.tsv")
    if len(two) != 14:
        errors.append("2x row count mismatch")
    statuses = {status: sum(row["status"] == status for row in two)
                for status in {row["status"] for row in two}}
    if statuses != {"PASS": 11, "INVALID_SOURCE_COUPLING": 1, "SKIPPED_SOURCE_COUPLING": 2}:
        errors.append(f"2x status counts mismatch: {statuses}")
    for row in two:
        if row["status"] == "PASS" and (row["work_conserved"] != "True" or row["correctness"] != "True"):
            errors.append(f"2x correctness failed: {row['target']} {row['arm']}")
    if any(row["target"] == "M2" for row in two):
        errors.append("M2 present in 2x table")

    upper = rows("RESOURCE_UPPER_BOUND_MATRIX.tsv")
    if len(upper) != 7 or {row["target"] for row in upper} != {"T0", "T1", "T2", "SPLITKV", "L2", "L1", "M1"}:
        errors.append("upper matrix shape mismatch")
    for row in upper:
        if row["status"] != "PASS" or row["work_conserved"] != "True" or row["correctness"] != "True":
            errors.append(f"upper correctness failed: {row['target']}")
    saturation = rows("RESOURCE_SATURATION_MAP.tsv")
    if len(saturation) != 7:
        errors.append("saturation map row count mismatch")

    raw = rows("RAW_DATA_INDEX.tsv")
    for row in raw:
        path = Path(row["path"])
        if not path.is_file() or path.stat().st_size != int(row["bytes"]) or sha(path) != row["sha256"]:
            errors.append(f"raw mismatch: {path}")
    manifest_entries = []
    for line in (PACK / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split("  ", 1)
        manifest_entries.append(name)
        path = PACK / name
        if not path.is_file() or sha(path) != digest:
            errors.append(f"manifest mismatch: {name}")
    expected_manifest = sorted(path.name for path in PACK.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    if sorted(manifest_entries) != expected_manifest:
        errors.append("manifest coverage mismatch")

    print(f"required={len(REQUIRED)} targets={len(targets)} two_x={len(two)} upper={len(upper)} raw={len(raw)} errors={len(errors)}")
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
