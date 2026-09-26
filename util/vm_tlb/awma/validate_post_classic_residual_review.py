#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
from pathlib import Path


REPO = Path(
    "/root/workspace/accel-sim-framework-awma-post-classic-baseline-residual-discovery-v1"
)
PACK = (
    REPO
    / "docs/vm_tlb/review_packs"
    / "AWMA_POST_CLASSIC_BASELINE_RESIDUAL_DISCOVERY_V1"
)
REQUIRED = (
    "README.md", "REPORT.md", "STRONG_BASELINE_RESIDUAL_MATRIX.tsv",
    "MULTIPAGE_AND_HEAD_EXPOSURE.tsv", "HEAD_PRELAUNCH_COLLISION.tsv",
    "RESIDUAL_LOCALIZATION.md", "RESIDUAL_HEADROOM.tsv",
    "OBSERVATORY_LOCALIZATION.tsv", "CLOSEST_WORK_AFTER_BASELINE.md",
    "HYPOTHESIS_DISPOSITION.tsv", "PROTOTYPE_DECISION.md",
    "PREREGISTRATION.md", "OBSERVATORY_PREREGISTRATION.md",
    "SOURCE_ANCHORS.tsv", "VALIDATION.md", "RAW_INDEX.tsv", "SHA256SUMS",
    "EXECUTION_SUMMARY.md",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main() -> int:
    errors: list[str] = []
    for name in REQUIRED:
        if not (PACK / name).is_file():
            errors.append(f"MISSING:{name}")
    for path in PACK.glob("*.tsv"):
        rows = [row for row in csv.reader(path.open(), delimiter="\t") if row]
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            errors.append(f"TSV:{path.name}")

    raw_checked = 0
    for row in read_tsv(PACK / "RAW_INDEX.tsv"):
        if row["kind"] == "authority":
            continue
        path = Path(row["path_or_type"])
        if not path.is_file():
            errors.append(f"RAW_MISSING:{row['identity']}:{path}")
            continue
        raw_checked += 1
        if digest(path) != row["sha256_or_commit"]:
            errors.append(f"RAW_HASH:{row['identity']}")

    baseline = read_tsv(PACK / "STRONG_BASELINE_RESIDUAL_MATRIX.tsv")
    if len(baseline) != 7 or any(row["correctness"] != "True" for row in baseline):
        errors.append("BASELINE_MATRIX")
    headroom = read_tsv(PACK / "RESIDUAL_HEADROOM.tsv")
    if len(headroom) != 4 or any(row["correctness"] != "True" for row in headroom):
        errors.append("HEADROOM_MATRIX")
    observatory = read_tsv(PACK / "OBSERVATORY_LOCALIZATION.tsv")
    if len(observatory) != 4 or any(row["neutral_exact"] != "True" for row in observatory):
        errors.append("OBSERVATORY_NEUTRALITY")
    collisions = read_tsv(PACK / "HEAD_PRELAUNCH_COLLISION.tsv")
    if any(row["head_demand_loses_to_nonhead_prelaunch_cycles"] != "0" for row in collisions):
        errors.append("H2_COLLISION")
    report = (PACK / "REPORT.md").read_text()
    if "NO_NOVEL_RESIDUAL_MECHANISM_IDENTIFIED_V1" not in report:
        errors.append("FINAL_STATUS")

    manifest_rows = []
    for line in (PACK / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        manifest_rows.append(name)
        if digest(PACK / name) != expected:
            errors.append(f"PACK_HASH:{name}")
    expected_manifest = sorted(
        path.name for path in PACK.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    if sorted(manifest_rows) != expected_manifest:
        errors.append("MANIFEST_COVERAGE")

    print(
        f"required={len(REQUIRED)} raw_checked={raw_checked} "
        f"baseline_targets={len(baseline)} phase_c_targets={len(headroom)} "
        f"errors={len(errors)}"
    )
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
