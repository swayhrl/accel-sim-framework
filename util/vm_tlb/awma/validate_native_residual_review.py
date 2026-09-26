#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


REPO = Path(
    "/root/workspace/accel-sim-framework-awma-ai-translation-native-residual-174new-v1"
)
PACK = REPO / "docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_NATIVE_RESIDUAL_174NEW_V1"
REQUIRED = (
    "README.md", "NATIVE_INTERPRETATION_FREEZE.md",
    "B1_NATIVE_DIAGNOSTIC_PREREGISTRATION.md", "NEW_TRACE_QUALIFICATION.tsv",
    "L1_M1_SCALE_COMPARISON.tsv", "NEW_AI_RESIDUAL_MATRIX.tsv",
    "DIAGNOSTIC_DECISION_LOG.tsv", "L2_GRAMMAR_AUDIT.md",
    "L2_DERIVED_INPUT_AUTHORITY.tsv", "CLOSEST_WORK_SCREEN.md",
    "PROTOTYPE_DECISION.md", "REPORT.md", "EXECUTION_SUMMARY.md",
    "RAW_DATA_INDEX.tsv", "SHA256SUMS",
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

    qualification = read_tsv(PACK / "NEW_TRACE_QUALIFICATION.tsv")
    if len(qualification) != 4 or any(row["correctness"] != "True" for row in qualification):
        errors.append("QUALIFICATION")
    if {row["target"] for row in qualification} != {"L1", "M1", "M2", "L2"}:
        errors.append("TARGET_SET")
    scale = {row["target"]: row for row in read_tsv(PACK / "L1_M1_SCALE_COMPARISON.tsv")}
    if set(scale) != {"L1", "M1"}:
        errors.append("SCALE_ROWS")
    else:
        for field in (
            "sim_instructions_per_cta", "memory_instructions_per_cta",
            "active_lane_refs_per_cta", "logical_requests_per_cta",
        ):
            if scale["L1"][field] != scale["M1"][field]:
                errors.append(f"SCALE_MISMATCH:{field}")
        if scale["L1"]["cta_scale_vs_M1"] != "8":
            errors.append("SCALE_RATIO")
    residual = {row["target"]: row for row in read_tsv(PACK / "NEW_AI_RESIDUAL_MATRIX.tsv")}
    expected = {
        "L1": "ACCESS_PATH_MODEL_SENSITIVE_ONLY",
        "M1": "ACCESS_PATH_MODEL_SENSITIVE_ONLY",
        "M2": "NO_MATERIAL_TRANSLATION_RESIDUAL",
        "L2": "NO_MATERIAL_TRANSLATION_RESIDUAL",
    }
    if set(residual) != set(expected):
        errors.append("RESIDUAL_TARGETS")
    else:
        for target, classification in expected.items():
            if residual[target]["classification"] != classification:
                errors.append(f"CLASSIFICATION:{target}")
            if residual[target]["correctness"] != "True":
                errors.append(f"RESIDUAL_CORRECTNESS:{target}")
            if residual[target]["b0_mshr_full"] != "0" or residual[target]["b0_pwq_full"] != "0":
                errors.append(f"UNEXPECTED_FULL:{target}")

    authority = json.loads((Path(
        "/root/share/mnt164/huangrulin/awma_ai_translation_native_residual_174new_v1/"
        "L2_GRAMMAR_REPAIRED_DETERMINISTIC/AUTHORITY.json"
    )).read_text())
    if not authority["byte_identical"] or authority["modified_instruction_records"] != 0:
        errors.append("L2_DERIVED_AUTHORITY")
    if authority["source_sha256"] != authority["derived_sha256"]:
        errors.append("L2_DERIVED_HASH")
    if authority["l2_validator"]["status"] != "TRACEG_GRAMMAR_PASS":
        errors.append("L2_VALIDATOR")

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

    if any(PACK.glob("PROBLEM_CARD_*.md")):
        errors.append("UNAUTHORIZED_PROBLEM_CARD")
    if "NO_NEW_AI_TRANSLATION_PROBLEM_IDENTIFIED_V1" not in (PACK / "REPORT.md").read_text():
        errors.append("FINAL_STATUS")

    manifest = []
    for line in (PACK / "SHA256SUMS").read_text().splitlines():
        expected_hash, name = line.split("  ", 1)
        manifest.append(name)
        if digest(PACK / name) != expected_hash:
            errors.append(f"PACK_HASH:{name}")
    expected_manifest = sorted(
        path.name for path in PACK.iterdir()
        if path.is_file() and path.name != "SHA256SUMS"
    )
    if sorted(manifest) != expected_manifest:
        errors.append("MANIFEST_COVERAGE")

    print(
        f"required={len(REQUIRED)} raw_checked={raw_checked} "
        f"qualified={len(qualification)} residual={len(residual)} errors={len(errors)}"
    )
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
