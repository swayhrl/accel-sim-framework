#!/usr/bin/env python3
"""Fail closed on source-defined, nonnumeric FAST64.6 capacity deadlocks.

This validator deliberately validates *only* the four M5.4-authorized
physical-16.5-KiB observations.  They are not numeric sensitivity results and
must never enter a strict-terminal performance collector as such.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import collect_fast64_6_sensitivity_v1 as sensitivity

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {("BICG", "IO"), ("BICG", "OO"), ("GESUMMV", "IO"), ("GESUMMV", "OO")}
FIELDS = ("workload", "dimension", "point", "mode", "modeled_value", "formal_run_dir",
          "attempt_uuid", "manifest_sha256", "start_receipt_sha256", "terminal_receipt_sha256",
          "stdout_sha256", "diagnostic_evidence", "diagnostic_sha256", "classification_authority",
          "classification_authority_sha256", "disposition")


def fail(message: str) -> None:
    raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 6 or lines[0] != "schema\tFAST64_6_EXPECTED_RESOURCE_DEADLOCK_REGISTRY_V1":
        fail("EXPECTED_DEADLOCK_REGISTRY_SCHEMA_INVALID")
    if lines[1] != "classification\tEXPECTED_RESOURCE_DEADLOCK_NONNUMERIC":
        fail("EXPECTED_DEADLOCK_REGISTRY_CLASSIFICATION_INVALID")
    rows = list(csv.DictReader(lines[4:], delimiter="\t"))
    if not rows or tuple(rows[0]) != FIELDS or len(rows) != 4:
        fail("EXPECTED_DEADLOCK_REGISTRY_COLUMNS_OR_COUNT_INVALID")
    if {(row["workload"], row["mode"]) for row in rows} != EXPECTED:
        fail("EXPECTED_DEADLOCK_REGISTRY_ROSTER_INVALID")
    return rows


def receipt(path: Path, label: str) -> dict[str, str]:
    with path.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    data = {row.get("key", ""): row.get("value", "") for row in rows}
    if not data:
        fail(f"{label}: RECEIPT_EMPTY")
    return data


def manifest(path: Path, label: str) -> dict[str, str]:
    data = receipt(path, label)
    required = ("attempt_uuid", "simulator_sha256", "config_sha256", "trace_list_sha256",
                "framework_scientific_config_source_sha", "core_source_head", "observer_overlay_sha256")
    if any(not data.get(key) for key in required):
        fail(f"{label}: MANIFEST_FIELDS_MISSING")
    return data


def validate_diagnostic(row: dict[str, str], stdout: Path) -> None:
    evidence = row["diagnostic_evidence"]
    if evidence.startswith("simulator.stdout:"):
        text = stdout.read_text(encoding="utf-8", errors="replace")
        if "DTC_L1_IO_RESOURCE_DEADLOCK diagnostic state:" not in text:
            fail(f"{row['workload']}/{row['mode']}: IO_MARKER_MISSING")
        required = ("free_phys=0", "allocated_phys=132", "partial_entries=1",
                    "lower_create=0", "lower_issue=0", "inflight=0")
        if any(token not in text for token in required):
            fail(f"{row['workload']}/{row['mode']}: IO_RESOURCE_STATE_INCOMPLETE")
        if row["diagnostic_sha256"] != "NA":
            fail(f"{row['workload']}/{row['mode']}: IO_DIAGNOSTIC_SHA_MUST_BE_NA")
        return
    path = ROOT / "docs/dtc_l1/fast64" / evidence
    if not path.is_file() or digest(path) != row["diagnostic_sha256"]:
        fail(f"{row['workload']}/{row['mode']}: DIAGNOSTIC_HASH_MISMATCH")
    record = json.loads(path.read_text(encoding="utf-8"))
    states = record.get("resource_state", [])
    if record.get("classification") != "NONFORMAL_DIAGNOSTIC_NOT_RESULT" or record.get("mode") != row["mode"] or not states:
        fail(f"{row['workload']}/{row['mode']}: DIAGNOSTIC_SCHEMA_OR_MODE_INVALID")
    for state in states:
        if state.get("allocated_phys") != 132 or any(state.get(key) != 0 for key in ("lower_create", "lower_issue", "inflight")):
            fail(f"{row['workload']}/{row['mode']}: DIAGNOSTIC_RESOURCE_STATE_INVALID")
        if row["mode"] == "IO" and (state.get("free_phys") != 0 or state.get("partial_entries") != 1):
            fail(f"{row['workload']}/{row['mode']}: IO_DIAGNOSTIC_RESOURCE_STATE_INVALID")
        if row["mode"] == "OO" and not isinstance(state.get("active_refs"), int):
            fail(f"{row['workload']}/{row['mode']}: OO_DIAGNOSTIC_RESOURCE_STATE_INVALID")


def validate(row: dict[str, str], matrix: dict[tuple[str, str, str, str], dict[str, str]], meta: dict[str, str]) -> None:
    label = f"{row['workload']}/{row['dimension']}/{row['point']}/{row['mode']}"
    key = (row["workload"], row["dimension"], row["point"], row["mode"])
    spec = matrix.get(key)
    if not spec or row["dimension"] != "physical" or row["point"] != "16.5" or row["modeled_value"] != "132_lines_16896B":
        fail(f"{label}: MATRIX_CELL_INVALID")
    run = Path(row["formal_run_dir"])
    manifest_path, start_path, terminal_path, stdout = (run / name for name in ("RUN_MANIFEST.tsv", "RUN_START.tsv", "RUN_TERMINAL.tsv", "simulator.stdout"))
    if any(not path.is_file() for path in (manifest_path, start_path, terminal_path, stdout)):
        fail(f"{label}: FORMAL_EVIDENCE_MISSING")
    for path, expected in ((manifest_path, row["manifest_sha256"]), (start_path, row["start_receipt_sha256"]),
                           (terminal_path, row["terminal_receipt_sha256"]), (stdout, row["stdout_sha256"])):
        if digest(path) != expected:
            fail(f"{label}: HASH_MISMATCH={path.name}")
    data, start, terminal = manifest(manifest_path, label), receipt(start_path, label), receipt(terminal_path, label)
    if any(item.get("attempt_uuid") != row["attempt_uuid"] for item in (data, start, terminal)) or terminal.get("simulator_exit_status") != "1":
        fail(f"{label}: RECEIPT_OR_EXIT_INVALID")
    if data["config_sha256"] != spec["config_sha256"] or data["trace_list_sha256"] != spec["payload_sha256"]:
        fail(f"{label}: CONFIG_OR_PAYLOAD_MISMATCH")
    for field, expected in (("core_source_head", meta["formal_core_sha"]), ("simulator_sha256", meta["formal_runtime_sha256"]),
                            ("observer_overlay_sha256", meta["observer_sha256"]), ("framework_scientific_config_source_sha", meta["scientific_framework_sha"])):
        if data[field] != expected:
            fail(f"{label}: IDENTITY_MISMATCH={field}")
    authority = ROOT / "docs/dtc_l1/fast64" / row["classification_authority"]
    if not authority.is_file() or digest(authority) != row["classification_authority_sha256"]:
        fail(f"{label}: CLASSIFICATION_AUTHORITY_MISMATCH")
    if row["disposition"] != "EXPECTED_RESOURCE_DEADLOCK_NO_NUMERIC_PERFORMANCE":
        fail(f"{label}: DISPOSITION_INVALID")
    validate_diagnostic(row, stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, required=True)
    args = parser.parse_args()
    meta, matrix = sensitivity.read_matrix(args.matrix)
    rows = table(args.registry)
    for row in rows:
        validate(row, matrix, meta)
    print("FAST64_6_EXPECTED_DEADLOCK_REGISTRY_V1_PASS rows=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
