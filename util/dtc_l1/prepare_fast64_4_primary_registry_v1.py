#!/usr/bin/env python3
"""Prepare the future-only 36-cell FAST64.4 collector registry fail closed.

The tool has no simulator or controller authority.  It consumes only a
completed FAST64.3 Base source registry and the 24-cell IO/OO coverage table,
requires every referenced compact JSON to be present and lower-cap-clean, then
atomically writes a fresh collector input registry.  It never rewrites either
source table or publishes a stage PASS marker.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "docs/dtc_l1/fast64/generated"
BASE_REGISTRY = GENERATED / "FAST64_3_BASE_SOURCE_REGISTRY_V3_CORE41.tsv"
COVERAGE = GENERATED / "FAST64_4_IO_OO_COVERAGE_V1.tsv"
OUTPUT = GENERATED / "FAST64_4_PRIMARY_COLLECTOR_REGISTRY_V1.tsv"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
          "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
BASE_HEADINGS = ("workload", "source_class", "summary", "structural", "core_sha", "runtime_sha256")
COVERAGE_HEADINGS = ("workload", "mode", "coverage_status", "identity_disposition", "compact_or_run_reference", "note")
OUTPUT_HEADINGS = ("workload", "mode", "summary", "origin", "cap_disposition", "retry_resolution")


def read_tsv(path: Path, headings: tuple[str, ...], label: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise RuntimeError(f"{label}_MISSING={path}")
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or any(tuple(row) != headings for row in rows):
        raise RuntimeError(f"{label}_SCHEMA_INVALID")
    return rows


def resolve_json(generated: Path, reference: str, label: str) -> Path:
    candidate = Path(reference)
    if candidate.is_absolute() or ".." in candidate.parts or candidate.suffix != ".json":
        raise RuntimeError(f"{label}_SUMMARY_REFERENCE_INVALID={reference}")
    path = generated / candidate
    if not path.is_file():
        raise RuntimeError(f"{label}_SUMMARY_MISSING={path}")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"{label}_SUMMARY_JSON_INVALID={error}") from error
    if record.get("schema") != "dtc_l1_summary_v1":
        raise RuntimeError(f"{label}_SUMMARY_SCHEMA_INVALID")
    metrics = record.get("metrics", {})
    if metrics.get("DTC_L1_lower_cap_full_events") != 0:
        raise RuntimeError(f"{label}_CAP_RESOLUTION_REQUIRED")
    return path


def validate_base(rows: list[dict[str, str]], generated: Path) -> dict[str, dict[str, str]]:
    if len(rows) != len(ROSTER) or {row["workload"] for row in rows} != set(ROSTER):
        raise RuntimeError("BASE_REGISTRY_MUST_HAVE_EXACT_FAST12")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        workload = row["workload"]
        if workload in result or row["source_class"].startswith("INVALID_"):
            raise RuntimeError(f"BASE_ROW_NOT_PROMOTABLE={workload}")
        resolve_json(generated, row["summary"], f"{workload}/BASE")
        result[workload] = row
    return result


def validate_coverage(rows: list[dict[str, str]], generated: Path) -> dict[tuple[str, str], dict[str, str]]:
    expected = {(workload, mode) for workload in ROSTER for mode in ("IO", "OO")}
    actual = {(row["workload"], row["mode"]) for row in rows}
    if len(rows) != len(expected) or actual != expected:
        raise RuntimeError("IO_OO_COVERAGE_MUST_HAVE_EXACT_24_CELLS")
    result: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["workload"], row["mode"])
        if key in result or row["coverage_status"] != "STRICT_TERMINAL_REUSE_CANDIDATE":
            raise RuntimeError(f"IO_OO_CELL_NOT_STRICT_TERMINAL={key[0]}/{key[1]}")
        resolve_json(generated, row["compact_or_run_reference"], f"{key[0]}/{key[1]}")
        result[key] = row
    return result


def rows_for_collector(base: dict[str, dict[str, str]], coverage: dict[tuple[str, str], dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for workload in ROSTER:
        base_row = base[workload]
        rows.append({
            "workload": workload,
            "mode": "BASE",
            "summary": base_row["summary"],
            "origin": "BASE_SOURCE=" + base_row["source_class"],
            "cap_disposition": "ZERO",
            "retry_resolution": "BASE_REGISTRY_V3_SOURCE",
        })
        for mode in ("IO", "OO"):
            row = coverage[(workload, mode)]
            rows.append({
                "workload": workload,
                "mode": mode,
                "summary": row["compact_or_run_reference"],
                "origin": "IO_OO_COVERAGE=" + row["identity_disposition"],
                "cap_disposition": "ZERO",
                "retry_resolution": "COVERAGE_V1_STRICT_TERMINAL",
            })
    return rows


def write_once(path: Path, rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise RuntimeError(f"OUTPUT_ALREADY_EXISTS={path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent, text=True)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=OUTPUT_HEADINGS, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        os.chmod(temporary, 0o444)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-root", type=Path, default=GENERATED)
    parser.add_argument("--base-registry", type=Path)
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    generated = args.generated_root
    base_path = args.base_registry or generated / BASE_REGISTRY.name
    coverage_path = args.coverage or generated / COVERAGE.name
    output = args.output or generated / OUTPUT.name
    base = validate_base(read_tsv(base_path, BASE_HEADINGS, "BASE_REGISTRY"), generated)
    coverage = validate_coverage(read_tsv(coverage_path, COVERAGE_HEADINGS, "IO_OO_COVERAGE"), generated)
    rows = rows_for_collector(base, coverage)
    if args.dry_run:
        print("FAST64_4_PRIMARY_REGISTRY_V1_DRY_RUN_PASS rows=" + str(len(rows)))
    else:
        write_once(output, rows)
        print("FAST64_4_PRIMARY_REGISTRY_V1_PREPARED output=" + str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
