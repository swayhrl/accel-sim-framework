#!/usr/bin/env python3
"""Fail-closed collector for the frozen 78-cell FAST64.6 sensitivity matrix.

The input registry is deliberately separate from live dispatch state.  It may
reference a strict terminal sensitivity record or an exact matching accepted
FAST64.4 primary record, but every matrix cell must be supplied exactly once.
This tool publishes a candidate data package only; it never writes a PASS
marker or changes any scheduler/controller state.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROSTER = ("BICG", "GESUMMV", "Btree")
MODES = ("IO", "OO")
DIMENSIONS = ("logical", "physical", "pib")
CLASS = "PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE"
REGISTRY_FIELDS = ("workload", "dimension", "point", "mode", "summary", "origin")


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric(value: object, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        fail(f"{label}: POSITIVE_NUMBER_REQUIRED")
    return float(value)


def require(mapping: dict, keys: tuple[str, ...], label: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        fail(f"{label}: MISSING=" + ",".join(missing))


def equal(metrics: dict, keys: tuple[str, ...], label: str) -> None:
    require(metrics, keys, label)
    if len({metrics[key] for key in keys}) != 1:
        fail(f"{label}: CONSERVATION=" + ",".join(keys))


def zero(metrics: dict, keys: tuple[str, ...], label: str) -> None:
    require(metrics, keys, label)
    bad = [key for key in keys if metrics[key] != 0]
    if bad:
        fail(f"{label}: TERMINAL_NONZERO=" + ",".join(bad))


def read_tsv_with_preamble(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = next((i for i, line in enumerate(lines) if line.startswith("workload\t")), None)
    if header is None:
        fail("FAST64_6_MATRIX_SCHEMA_INVALID")
    metadata: dict[str, str] = {}
    for line in lines[:header]:
        fields = line.split("\t")
        if len(fields) == 2:
            metadata[fields[0]] = fields[1]
    rows = list(csv.DictReader(lines[header:], delimiter="\t"))
    return metadata, rows


def read_matrix(path: Path) -> tuple[dict[str, str], dict[tuple[str, str, str, str], dict[str, str]]]:
    metadata, rows = read_tsv_with_preamble(path)
    if metadata.get("schema") != "FAST64_6_SENSITIVITY_MATRIX_V1":
        fail("FAST64_6_MATRIX_SCHEMA_INVALID")
    need = {"scientific_framework_sha", "formal_core_sha", "formal_runtime_sha256", "observer_sha256"}
    if not need.issubset(metadata):
        fail("FAST64_6_MATRIX_IDENTITY_METADATA_MISSING")
    expected = {(w, d, p, m) for w in ROSTER for d, points in {
        "logical": ("16", "32", "64"),
        "physical": ("16.5", "24", "32", "40", "48"),
        "pib": ("32", "64", "128", "192", "256"),
    }.items() for p in points for m in MODES}
    index = {(row.get("workload"), row.get("dimension"), row.get("point"), row.get("mode")): row for row in rows}
    if len(rows) != 78 or len(index) != 78 or set(index) != expected:
        fail("FAST64_6_MATRIX_MUST_CONTAIN_EXACTLY_78_FROZEN_CELLS")
    for key, row in index.items():
        if row.get("classification") != CLASS or row.get("dimension") not in DIMENSIONS:
            fail(f"{key}: MATRIX_CLASSIFICATION_OR_DIMENSION_INVALID")
    return metadata, index


def read_registry(path: Path, expected: set[tuple[str, str, str, str]]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or any(tuple(row) != REGISTRY_FIELDS for row in rows):
        fail("FAST64_6_REGISTRY_SCHEMA_INVALID")
    cells = {(r["workload"], r["dimension"], r["point"], r["mode"]) for r in rows}
    if len(rows) != 78 or len(cells) != 78 or cells != expected:
        fail("FAST64_6_REGISTRY_MUST_CONTAIN_EXACTLY_78_CELLS")
    return rows


def load_summary(row: dict[str, str]) -> dict:
    path = Path(row["summary"])
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        fail(f"{row['workload']}/{row['dimension']}/{row['point']}/{row['mode']}: SUMMARY_MISSING")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"SUMMARY_JSON_INVALID={error}")
    row["_path"], row["_sha256"] = str(path), sha256(path)
    return record


def expected_config_id(row: dict[str, str]) -> str:
    stem = {"logical": f"LOGICAL_{row['point']}KB", "physical": f"PHYSICAL_{'16p5' if row['point'] == '16.5' else row['point']}KB", "pib": f"PIB_{row['point']}ENTRIES"}[row["dimension"]]
    return f"FAST64_SENS_{stem}_{row['mode']}"


def validate_row(row: dict[str, str], matrix: dict[str, str], meta: dict[str, str], record: dict) -> None:
    label = "/".join((row["workload"], row["dimension"], row["point"], row["mode"]))
    if row["origin"] not in {"STRICT_TERMINAL_SENSITIVITY", "EXACT_FAST64_4_PRIMARY_REUSE"}:
        fail(f"{label}: ORIGIN_INVALID")
    if record.get("schema") != "dtc_l1_summary_v1":
        fail(f"{label}: SUMMARY_SCHEMA_INVALID")
    p, m = record.get("provenance", {}), record.get("metrics", {})
    require(p, ("workload_id", "config_sha256", "core_sha", "runtime_binary_sha256", "observer_overlay_sha256", "framework_sha", "result_classification"), label)
    require(m, ("DTC_L1_mode", "gpu_tot_sim_cycle", "gpu_tot_sim_insn", "DTC_L1_lower_outstanding", "DTC_L1_lower_cap_full_events"), label)
    if p["workload_id"].casefold() != row["workload"].casefold() or p["config_sha256"] != matrix["config_sha256"]:
        fail(f"{label}: PAYLOAD_OR_CONFIG_MISMATCH")
    if p["config_id"] != expected_config_id(row) and row["origin"] != "EXACT_FAST64_4_PRIMARY_REUSE":
        fail(f"{label}: CONFIG_ID_MISMATCH")
    for field, meta_field in (("core_sha", "formal_core_sha"), ("runtime_binary_sha256", "formal_runtime_sha256"), ("observer_overlay_sha256", "observer_sha256"), ("framework_sha", "scientific_framework_sha")):
        if p[field] != meta[meta_field]:
            fail(f"{label}: IDENTITY_MISMATCH={field}")
    trace = record.get("external_artifacts", {}).get("trace_list_sha256")
    if trace != matrix["payload_sha256"]:
        fail(f"{label}: TRACE_PAYLOAD_MISMATCH")
    if p["result_classification"] != CLASS:
        fail(f"{label}: CLASSIFICATION_MISMATCH")
    if m["DTC_L1_mode"] != f"PAPER_{row['mode']}":
        fail(f"{label}: MODE_MISMATCH")
    numeric(m["gpu_tot_sim_cycle"], label + "/cycles")
    numeric(m["gpu_tot_sim_insn"], label + "/instructions")
    attempt = record.get("immutable_attempt", {})
    require(attempt, ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256"), label)
    if row["mode"] == "IO":
        equal(m, ("DTC_L1_io_lower_created", "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses"), label)
        equal(m, ("DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed"), label)
        equal(m, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"), label)
        zero(m, ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"), label)
    else:
        equal(m, ("DTC_L1_oo_lower_created", "DTC_L1_oo_lower_issued", "DTC_L1_oo_lower_responses"), label)
        equal(m, ("DTC_L1_oo_completion_dependency_count", "DTC_L1_oo_completion_dependency_closed"), label)
        equal(m, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"), label)
        zero(m, ("DTC_L1_oo_inflight_current", "DTC_L1_oo_pib_occupancy", "DTC_L1_oo_active_refs", "DTC_L1_lower_outstanding"), label)


def write_tsv(path: Path, header: tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(header); writer.writerows(rows)
    os.chmod(path, 0o444)


def reference_cell(matrix: dict[str, str], workload: str, current_mode: str) -> tuple[str, str, str, str]:
    ref = matrix["reference_point"].split("_")
    if len(ref) == 4 and ref[2:] == ["same", "mode"]:
        return workload, ref[0], ref[1], current_mode
    if len(ref) != 3:
        fail(f"{workload}: REFERENCE_POINT_INVALID")
    return workload, ref[0], ref[1], ref[2]


def collect(registry: list[dict[str, str]], matrix: dict[tuple[str, str, str, str], dict[str, str]], records: dict[tuple[str, str, str, str], dict], output: Path, matrix_sha: str, registry_sha: str) -> None:
    cells, raw = [], []
    for row in registry:
        key = (row["workload"], row["dimension"], row["point"], row["mode"])
        record, spec = records[key], matrix[key]
        p, m = record["provenance"], record["metrics"]
        cells.append((*key, spec["modeled_value"], spec["config_path"], p["config_sha256"], m["gpu_tot_sim_cycle"], m["gpu_tot_sim_insn"], m["DTC_L1_lower_cap_full_events"], row["origin"], row["summary"], row["_sha256"], "CANDIDATE_PENDING_STAGE6_HANDOFF"))
        a, x = record["immutable_attempt"], record.get("external_artifacts", {})
        raw.append((*key, row["summary"], row["_sha256"], a["attempt_uuid"], a["runner_sha256"], a["start_receipt_sha256"], a["terminal_receipt_sha256"], x.get("run_dir", "NA"), x.get("simulator_stdout_sha256", "NA"), x.get("simulator_stderr_sha256", "NA")))
    by_key = {key: record for key, record in records.items()}
    families: dict[str, list[tuple[object, ...]]] = {d: [] for d in DIMENSIONS}
    for key, record in sorted(by_key.items()):
        workload, dimension, point, mode = key; spec = matrix[key]
        ref_key = reference_cell(spec, workload, mode)
        if ref_key not in by_key:
            fail(f"{workload}/{dimension}/{point}/{mode}: REFERENCE_CELL_MISSING")
        cycles, ref_cycles = numeric(record["metrics"]["gpu_tot_sim_cycle"], "cycles"), numeric(by_key[ref_key]["metrics"]["gpu_tot_sim_cycle"], "reference_cycles")
        families[dimension].append((workload, point, mode, spec["modeled_value"], spec["reference_point"], spec["reference_mode"], int(cycles), int(ref_cycles), f"{cycles/ref_cycles:.9f}", f"{ref_cycles/cycles:.9f}", "CANDIDATE_PENDING_STAGE6_HANDOFF"))
    write_tsv(output / "fast64_6_cells.tsv", ("workload", "dimension", "point", "mode", "modeled_value", "config_path", "config_sha256", "cycles", "instructions", "lower_cap_full_events", "origin", "evidence_path", "evidence_sha256", "status"), cells)
    header = ("workload", "point", "mode", "modeled_value", "reference_point", "reference_mode", "cycles", "reference_cycles", "cycles_over_reference", "speedup_vs_reference", "status")
    for dimension, rows in families.items():
        write_tsv(output / f"fast64_6_{dimension}_plot.tsv", header, rows)
    write_tsv(output / "fast64_6_raw_manifest.tsv", ("workload", "dimension", "point", "mode", "evidence_path", "evidence_sha256", "attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256", "raw_run_ref", "stdout_sha256", "stderr_sha256"), raw)
    write_tsv(output / "fast64_6_collector_status.tsv", ("item", "value"), [("status", "CANDIDATE_PENDING_STAGE6_HANDOFF"), ("accepted_cells", 78), ("matrix_sha256", matrix_sha), ("registry_sha256", registry_sha), ("promotion", "NONE")])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    meta, matrix = read_matrix(args.matrix)
    rows = read_registry(args.registry, set(matrix))
    records = {}
    for row in rows:
        key = (row["workload"], row["dimension"], row["point"], row["mode"])
        record = load_summary(row); validate_row(row, matrix[key], meta, record); records[key] = record
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        collect(rows, matrix, records, temporary, sha256(args.matrix), sha256(args.registry))
        os.chmod(temporary, 0o555); os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True); raise
    print(f"FAST64_6_SENSITIVITY_V1_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
