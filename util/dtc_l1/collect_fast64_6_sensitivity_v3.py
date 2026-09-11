#!/usr/bin/env python3
"""Final FAST64.6 candidate collector with explicit nonnumeric deadlocks.

V1/V2 remain frozen for their live acquisition dependencies.  V3 is invoked
only after the numeric registry is complete and keeps expected physical-boundary
deadlocks out of numeric cycles and speedup plots.
"""
from __future__ import annotations

import argparse
import csv
import os
import shutil
import tempfile
from pathlib import Path

import collect_fast64_6_sensitivity_v1 as v1
import collect_fast64_6_sensitivity_v2 as v2
import validate_fast64_6_expected_deadlock_registry_v1 as deadlocks

ROOT = Path(__file__).resolve().parents[2]
DEADLOCK_KEYS = {(w, "physical", "16.5", m) for w in ("BICG", "GESUMMV") for m in v1.MODES}
NUMERIC_FIELDS = ("workload", "dimension", "point", "mode", "summary", "origin")


def fail(message: str) -> None:
    raise RuntimeError(message)


def numeric_registry(path: Path, expected: set[tuple[str, str, str, str]]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    keys = {(r.get("workload"), r.get("dimension"), r.get("point"), r.get("mode")) for r in rows}
    if not rows or tuple(rows[0]) != NUMERIC_FIELDS or len(rows) != 74 or keys != expected:
        fail("FAST64_6_NUMERIC_REGISTRY_EXACT_74_REQUIRED")
    return rows


def write_deadlocks(output: Path, rows: list[dict[str, str]]) -> None:
    with (output / "fast64_6_expected_deadlocks.tsv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("workload", "dimension", "point", "mode", "modeled_value", "disposition", "formal_run_dir", "attempt_uuid", "terminal_receipt_sha256", "diagnostic_evidence", "classification_authority"))
        for row in rows:
            writer.writerow(tuple(row[key] for key in ("workload", "dimension", "point", "mode", "modeled_value", "disposition", "formal_run_dir", "attempt_uuid", "terminal_receipt_sha256", "diagnostic_evidence", "classification_authority")))
    os.chmod(output / "fast64_6_expected_deadlocks.tsv", 0o444)


def write_status(output: Path, matrix: Path, numeric: Path, deadlock: Path) -> None:
    v1.write_tsv(output / "fast64_6_collector_status.tsv", ("item", "value"), [
        ("status", "CANDIDATE_PENDING_STAGE6_HANDOFF"),
        ("numeric_strict_cells", 74), ("expected_resource_deadlocks", 4),
        ("numeric_registry_sha256", v1.sha256(numeric)),
        ("deadlock_registry_sha256", v1.sha256(deadlock)),
        ("matrix_sha256", v1.sha256(matrix)),
        ("promotion", "NONE"),
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-ledger", type=Path, required=True)
    parser.add_argument("--stage4-primary-matrix", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--numeric-registry", type=Path, required=True)
    parser.add_argument("--deadlock-registry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    v2.require_prior_pass(args.stage_ledger)
    meta, matrix = v1.read_matrix(args.matrix)
    expected = set(matrix) - DEADLOCK_KEYS
    rows = numeric_registry(args.numeric_registry, expected)
    accepted = v2.primary_acceptance(args.stage4_primary_matrix)
    records = {}
    for row in rows:
        key = (row["workload"], row["dimension"], row["point"], row["mode"])
        record = v1.load_summary(row)
        v2.validate(row, matrix[key], meta, record, accepted)
        records[key] = record
    dead_rows = deadlocks.table(args.deadlock_registry)
    for row in dead_rows:
        deadlocks.validate(row, matrix, meta)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        v1.collect(rows, matrix, records, temporary, v1.sha256(args.matrix), v1.sha256(args.numeric_registry))
        write_deadlocks(temporary, dead_rows)
        write_status(temporary, args.matrix, args.numeric_registry, args.deadlock_registry)
        os.chmod(temporary, 0o555)
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_6_SENSITIVITY_V3_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
