#!/usr/bin/env python3
"""Future-only Stage6 collector with accepted Stage4 raw-evidence reuse.

The live v1 collector remains frozen.  v2 uses v1's terminal and identity
checks unchanged, adding the authority required to consume an exact primary
record whose raw classification predates Stage6 precomputation.
"""
from __future__ import annotations

import argparse
import copy
import csv
import os
import shutil
import tempfile
from pathlib import Path

import collect_fast64_6_sensitivity_v1 as v1

FAST12 = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
          "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = ("BASE", "IO", "OO")
REUSE_RAW_CLASSES = {"PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE", v1.CLASS}


def read_tsv(path: Path, prefix: str) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    index = next((i for i, line in enumerate(lines) if line.startswith(prefix)), None)
    if index is None:
        v1.fail(f"TSV_SCHEMA_INVALID={path}")
    return list(csv.DictReader(lines[index:], delimiter="\t"))


def require_prior_pass(ledger: Path) -> None:
    states = {r.get("stage"): r.get("current_state", r.get("status"))
              for r in read_tsv(ledger, "stage\t")}
    missing = [stage for stage in ("FAST64.4", "FAST64.5") if states.get(stage) != "PASS"]
    if missing:
        v1.fail("FAST64_6_PRIOR_PASS_REQUIRED=" + ",".join(missing))


def primary_acceptance(path: Path) -> set[tuple[str, str, str]]:
    rows = read_tsv(path, "workload\t")
    need = {"workload", "mode", "evidence_path", "acceptance_status"}
    if not rows or not need.issubset(rows[0]):
        v1.fail("FAST64_4_PRIMARY_MATRIX_SCHEMA_INVALID")
    expected = {(workload, mode) for workload in FAST12 for mode in MODES}
    if len(rows) != 36 or {(r.get("workload"), r.get("mode")) for r in rows} != expected:
        v1.fail("FAST64_4_PRIMARY_MATRIX_EXACT_36_REQUIRED")
    accepted = set()
    for row in rows:
        if row["acceptance_status"] != "STRICT_TERMINAL_ACCEPTED":
            continue
        evidence = Path(row["evidence_path"])
        if not evidence.is_absolute():
            evidence = v1.ROOT / "docs/dtc_l1/fast64/generated" / evidence
        accepted.add((row["workload"].casefold(), row["mode"], str(evidence.resolve())))
    return accepted


def validate(row: dict[str, str], matrix: dict[str, str], meta: dict[str, str], record: dict,
             accepted: set[tuple[str, str, str]]) -> None:
    if row["origin"] != "EXACT_FAST64_4_PRIMARY_REUSE":
        v1.validate_row(row, matrix, meta, record)
        return
    label = "/".join((row["workload"], row["dimension"], row["point"], row["mode"]))
    provenance = record.get("provenance", {})
    key = (row["workload"].casefold(), row["mode"], str(Path(row["_path"]).resolve()))
    if key not in accepted:
        v1.fail(f"{label}: PRIMARY_REUSE_ACCEPTANCE_MISSING")
    if provenance.get("result_classification") not in REUSE_RAW_CLASSES:
        v1.fail(f"{label}: PRIMARY_REUSE_RAW_CLASS_INVALID")
    # Reuse v1 verbatim after replacing only the historical class in memory;
    # neither the immutable compact JSON nor its provenance is rewritten.
    checked = copy.deepcopy(record)
    checked.setdefault("provenance", {})["result_classification"] = v1.CLASS
    v1.validate_row(row, matrix, meta, checked)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-ledger", type=Path, required=True)
    parser.add_argument("--stage4-primary-matrix", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        v1.fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    require_prior_pass(args.stage_ledger)
    accepted = primary_acceptance(args.stage4_primary_matrix)
    meta, matrix = v1.read_matrix(args.matrix)
    rows = v1.read_registry(args.registry, set(matrix))
    records = {}
    for row in rows:
        key = (row["workload"], row["dimension"], row["point"], row["mode"])
        record = v1.load_summary(row)
        validate(row, matrix[key], meta, record, accepted)
        records[key] = record
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        v1.collect(rows, matrix, records, temporary, v1.sha256(args.matrix), v1.sha256(args.registry))
        os.chmod(temporary, 0o555)
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_6_SENSITIVITY_V2_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
