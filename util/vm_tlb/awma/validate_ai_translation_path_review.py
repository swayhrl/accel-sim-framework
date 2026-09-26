#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


REPO = Path(
    "/root/workspace/accel-sim-framework-awma-ai-translation-path-and-residual-174new-v1"
)
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_PATH_AND_RESIDUAL_174NEW_V1"
REQUIRED = (
    "ACCESS_PATH_SOURCE_AUDIT.md", "PATH_MODEL_CONTRACT.md",
    "DIRECTED_PATH_CORRECTNESS.tsv", "EXISTING_TRACE_PATH_MATRIX.tsv",
    "EXISTING_TRACE_INTERPRETATION.md", "NEW_TRACE_QUALIFICATION.tsv",
    "NEW_AI_RESIDUAL_MATRIX.tsv", "DIAGNOSTIC_DECISION_LOG.tsv",
    "CLOSEST_WORK_SCREEN.md", "PROTOTYPE_DECISION.md", "REPORT.md",
    "NATIVE_HANDOFF_STATUS.json", "EXECUTION_SUMMARY.md",
    "RAW_DATA_INDEX.tsv", "README.md", "SHA256SUMS",
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
    for path in PACK.glob("*.json"):
        try:
            json.loads(path.read_text())
        except Exception as error:
            errors.append(f"JSON:{path.name}:{error}")
    for path in PACK.glob("*.tsv"):
        rows = [row for row in csv.reader(path.open(), delimiter="\t") if row]
        if not rows or any(len(row) != len(rows[0]) for row in rows):
            errors.append(f"TSV:{path.name}")

    matrix = read_tsv(PACK / "EXISTING_TRACE_PATH_MATRIX.tsv")
    if len(matrix) != 4 or any(row["correctness"] != "True" for row in matrix):
        errors.append("PATH_MATRIX")
    if any(
        row["b2_status"] != "NOT_IMPLEMENTED_SOURCE_SEMANTICS_INSUFFICIENT"
        for row in matrix
    ):
        errors.append("B2_STATUS")
    directed = read_tsv(PACK / "DIRECTED_PATH_CORRECTNESS.tsv")
    if len(directed) != 10:
        errors.append("DIRECTED_COUNT")

    raw_checked = 0
    for row in read_tsv(PACK / "RAW_DATA_INDEX.tsv"):
        if row["kind"] == "AUTHORITY":
            continue
        path = Path(row["path_or_type"])
        if not path.is_file():
            errors.append(f"RAW_MISSING:{row['identity']}")
            continue
        raw_checked += 1
        if digest(path) != row["sha256_or_commit"]:
            errors.append(f"RAW_HASH:{row['identity']}")

    manifest = []
    for line in (PACK / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        manifest.append(name)
        if digest(PACK / name) != expected:
            errors.append(f"PACK_HASH:{name}")
    expected_manifest = sorted(
        path.name for path in PACK.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    if sorted(manifest) != expected_manifest:
        errors.append("MANIFEST_COVERAGE")

    print(
        f"required={len(REQUIRED)} raw_checked={raw_checked} "
        f"path_targets={len(matrix)} directed={len(directed)} errors={len(errors)}"
    )
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
