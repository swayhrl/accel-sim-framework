#!/usr/bin/env python3
"""Publish a future-only Stage4 coverage V2 after strict Core658 2D results.

The original coverage is retained unchanged.  This tool accepts only the two
strictly collected Core658 2D JSON records and atomically publishes a new
24-cell coverage table for the existing fail-closed registry preparer.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path


HEADINGS = ("workload", "mode", "coverage_status", "identity_disposition", "compact_or_run_reference", "note")
CORE = "6587238c60214d99491f4048e28ce8a3458c1509"
RUNTIME = "29a3dd9f57a5accb89822ca3fcf06b11c437bfe864ee43d2ff5f26c8c056f3c1"
FRAMEWORK = "037f008b330eb230353b60edf126d6be9f45afdc"
OBSERVER = "2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e"
CONFIG = {
    "IO": ("FAST64_IO_A1", "d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621"),
    "OO": ("FAST64_OO_A1", "546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if len(rows) != 24 or any(tuple(row) != HEADINGS for row in rows):
        raise RuntimeError("COVERAGE_V1_SCHEMA_OR_CARDINALITY_INVALID")
    if {(row["workload"], row["mode"]) for row in rows}.__len__() != 24:
        raise RuntimeError("COVERAGE_V1_DUPLICATE_CELL")
    return rows


def validate_summary(path: Path, mode: str) -> None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"{mode}_SUMMARY_UNREADABLE") from error
    p, m, attempt = record.get("provenance", {}), record.get("metrics", {}), record.get("immutable_attempt", {})
    config_id, config_sha = CONFIG[mode]
    expected = {
        "workload_id": "2DConvolution", "config_id": config_id,
        "config_sha256": config_sha, "core_sha": CORE,
        "runtime_binary_sha256": RUNTIME, "framework_sha": FRAMEWORK,
        "observer_overlay_sha256": OBSERVER,
        "result_classification": "PRECOMPUTED_PENDING_FAST64_3_ACCEPTANCE",
    }
    if record.get("schema") != "dtc_l1_summary_v1" or any(p.get(k) != v for k, v in expected.items()):
        raise RuntimeError(f"{mode}_SUMMARY_IDENTITY_MISMATCH")
    if any(not attempt.get(key) for key in ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256")):
        raise RuntimeError(f"{mode}_IMMUTABLE_RECEIPT_MISSING")
    if m.get("gpu_tot_sim_cycle", 0) <= 0 or m.get("gpu_tot_sim_insn", 0) <= 0 or m.get("DTC_L1_lower_cap_full_events") != 0:
        raise RuntimeError(f"{mode}_PROGRESS_OR_CAP_INVALID")
    if m.get("DTC_L1_lower_credit_acquired") != m.get("DTC_L1_lower_credit_released") or m.get("DTC_L1_lower_outstanding") != 0:
        raise RuntimeError(f"{mode}_LOWER_LIFECYCLE_INVALID")
    prefix = mode.lower()
    needed = (f"DTC_L1_{prefix}_lower_created", f"DTC_L1_{prefix}_lower_issued", f"DTC_L1_{prefix}_lower_responses", f"DTC_L1_{prefix}_completion_dependency_count", f"DTC_L1_{prefix}_completion_dependency_closed", f"DTC_L1_{prefix}_inflight_current", f"DTC_L1_{prefix}_pib_occupancy")
    if any(key not in m for key in needed):
        raise RuntimeError(f"{mode}_MODE_METRIC_MISSING")
    if not (m[needed[0]] == m[needed[1]] == m[needed[2]] and m[needed[3]] == m[needed[4]] and m[needed[5]] == 0 and m[needed[6]] == 0):
        raise RuntimeError(f"{mode}_MODE_LIFECYCLE_INVALID")
    if mode == "OO" and m.get("DTC_L1_oo_active_refs") != 0:
        raise RuntimeError("OO_ACTIVE_REFS_NOT_DRAINED")


def write_once(path: Path, rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise RuntimeError("OUTPUT_ALREADY_EXISTS")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.tmp.", dir=path.parent, text=True)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=HEADINGS, delimiter="\t", lineterminator="\n")
            writer.writeheader(); writer.writerows(rows)
        os.chmod(temporary, 0o444)
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage-v1", type=Path, required=True)
    parser.add_argument("--io-summary", type=Path, required=True)
    parser.add_argument("--oo-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = read_tsv(args.coverage_v1)
    replacements = {
        "IO": "fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_io_core6587238c_a1_v1.json",
        "OO": "fast64_4_2d_tag_identity_v2/fast64_4_primary_2DConvolution_oo_core6587238c_a1_v1.json",
    }
    for mode, path in (("IO", args.io_summary), ("OO", args.oo_summary)):
        validate_summary(path, mode)
        matches = [row for row in rows if row["workload"] == "2DConvolution" and row["mode"] == mode]
        if len(matches) != 1 or matches[0]["coverage_status"] != "BLOCKED_ON_FINAL_CORE_IDENTITY":
            raise RuntimeError(f"{mode}_V1_REPLACEMENT_ANCHOR_INVALID")
        matches[0].update({
            "coverage_status": "STRICT_TERMINAL_REUSE_CANDIDATE",
            "identity_disposition": "CORE658_COMMON_TRIPLET",
            "compact_or_run_reference": replacements[mode],
            "note": "Core658 strict terminal; common identity with accepted Core658 Base",
        })
    if args.dry_run:
        print("FAST64_4_CORE658_COVERAGE_V2_DRY_RUN_PASS rows=24")
    else:
        write_once(args.output, rows)
        print(f"FAST64_4_CORE658_COVERAGE_V2_PUBLISHED output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
