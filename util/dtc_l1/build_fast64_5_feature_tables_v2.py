#!/usr/bin/env python3
"""Fail-closed measured-feature builder for the accepted FAST64.4 matrix.

This is deliberately a future-only production path.  Unlike the v1 fixture
builder, it refuses a merely well-shaped matrix: every primary compact record
must be explicitly accepted, identity-consistent within its triplet, and have
the terminal lifecycle closure required by its mode.  It emits measured tables
only; causal classes remain a separately reviewed input.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
          "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = ("BASE", "IO", "OO")
IDENTITY = ("core_sha", "runtime_binary_sha256", "observer_overlay_sha256",
            "framework_sha", "payload_sha256")
REQUIRED = ("workload", "mode", "evidence_path", "acceptance_status", *IDENTITY)


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        lines = stream.readlines()
    header = next((index for index, line in enumerate(lines)
                   if line.startswith("stage\t") or line.startswith("workload\t")), None)
    if header is None:
        fail(f"TSV_HEADER_MISSING={path}")
    return list(csv.DictReader(lines[header:], delimiter="\t"))


def require_stage4_pass(ledger: Path) -> None:
    states = {row.get("stage"): row.get("current_state", row.get("status"))
              for row in rows(ledger)}
    if states.get("FAST64.4") != "PASS":
        fail("FAST64_4_PASS_REQUIRED")


def summary(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"SUMMARY_INVALID={path}:{error}")
    if data.get("schema") != "dtc_l1_summary_v1":
        fail(f"SUMMARY_SCHEMA_INVALID={path}")
    return data


def require_equal(metrics: dict, keys: tuple[str, ...], label: str) -> None:
    if any(key not in metrics for key in keys):
        fail(f"{label}: TERMINAL_METRIC_MISSING")
    if len({metrics[key] for key in keys}) != 1:
        fail(f"{label}: LIFECYCLE_CONSERVATION_FAILED")


def validate_mode(metrics: dict, mode: str, label: str) -> None:
    if metrics.get("DTC_L1_mode") != f"PAPER_{mode}":
        fail(f"{label}: MODE_MISMATCH")
    if metrics.get("gpu_tot_sim_cycle", 0) <= 0 or metrics.get("gpu_tot_sim_insn", 0) <= 0:
        fail(f"{label}: PERFORMANCE_COUNTER_INVALID")
    if metrics.get("DTC_L1_lower_outstanding") != 0:
        fail(f"{label}: TERMINAL_LOWER_NOT_DRAINED")
    if mode == "BASE":
        require_equal(metrics, ("DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released"), label)
    elif mode == "IO":
        require_equal(metrics, ("DTC_L1_io_lower_created", "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses"), label)
        require_equal(metrics, ("DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed"), label)
        if metrics.get("DTC_L1_io_inflight_current") != 0 or metrics.get("DTC_L1_io_pib_occupancy") != 0:
            fail(f"{label}: TERMINAL_IO_NOT_DRAINED")
    else:
        require_equal(metrics, ("DTC_L1_oo_lower_created", "DTC_L1_oo_lower_issued", "DTC_L1_oo_lower_responses"), label)
        require_equal(metrics, ("DTC_L1_oo_completion_dependency_count", "DTC_L1_oo_completion_dependency_closed"), label)
        if any(metrics.get(key) != 0 for key in ("DTC_L1_oo_inflight_current", "DTC_L1_oo_pib_occupancy", "DTC_L1_oo_active_refs")):
            fail(f"{label}: TERMINAL_OO_NOT_DRAINED")


def validate_primary(matrix: Path) -> list[dict[str, str]]:
    primary = rows(matrix)
    if not primary or not set(REQUIRED).issubset(primary[0]):
        fail("FAST64_4_MATRIX_PRODUCTION_SCHEMA_INVALID")
    expected = {(workload, mode) for workload in ROSTER for mode in MODES}
    pairs = {(row.get("workload"), row.get("mode")) for row in primary}
    if len(primary) != 36 or pairs != expected:
        fail("FAST64_4_EXACT_PRIMARY_MATRIX_REQUIRED")
    by_workload: dict[str, list[dict[str, str]]] = {workload: [] for workload in ROSTER}
    for row in primary:
        label = f"{row['workload']}/{row['mode']}"
        if row.get("acceptance_status") != "STRICT_TERMINAL_ACCEPTED":
            fail(f"{label}: PRIMARY_ACCEPTANCE_REQUIRED")
        evidence = Path(row["evidence_path"])
        if not evidence.is_absolute():
            evidence = ROOT / "docs/dtc_l1/fast64/generated" / evidence
        data = summary(evidence)
        provenance, metrics = data.get("provenance", {}), data.get("metrics", {})
        for key in IDENTITY[:-1]:
            if provenance.get(key) != row[key]:
                fail(f"{label}: COMPACT_IDENTITY_MISMATCH={key}")
        if data.get("external_artifacts", {}).get("trace_list_sha256") != row["payload_sha256"]:
            fail(f"{label}: COMPACT_PAYLOAD_MISMATCH")
        if provenance.get("workload_id", "").casefold() != row["workload"].casefold():
            fail(f"{label}: COMPACT_WORKLOAD_MISMATCH")
        validate_mode(metrics, row["mode"], label)
        row["evidence_path"] = str(evidence)
        row["evidence_sha256"] = sha256(evidence)
        by_workload[row["workload"]].append(row)
    for workload, triplet in by_workload.items():
        if len(triplet) != 3 or any(len({row[key] for row in triplet}) != 1 for key in IDENTITY):
            fail(f"{workload}: TRIPLET_IDENTITY_MISMATCH")
    return primary


def validate_structural(path: Path) -> None:
    structural = rows(path)
    if len(structural) != 12 or {row.get("workload") for row in structural} != set(ROSTER):
        fail("FAST64_3_EXACT_STRUCTURAL_REQUIRED")


def write_tsv(path: Path, fields: tuple[str, ...], items: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(fields)
        writer.writerows(items)


def emitted_provenance(path: Path) -> None:
    # Table/column-level provenance covers every emitted feature column.  A
    # column whose structural name is carried from Stage3 is intentionally
    # source-keyed by that exact name rather than converted to a proxy.
    entries = []
    mappings = {
        "fast12_summary.csv": {"workload": ("FAST64.4 matrix", "workload", "identity", "member"),
            "base_cycles": ("FAST64.4 Base compact JSON", "gpu_tot_sim_cycle", "identity", "cycles"),
            "io_cycles": ("FAST64.4 IO compact JSON", "gpu_tot_sim_cycle", "identity", "cycles"),
            "oo_cycles": ("FAST64.4 OO compact JSON", "gpu_tot_sim_cycle", "identity", "cycles"),
            "speedup_io": ("FAST64.4 compact triplet", "Base/IO gpu_tot_sim_cycle", "Base/IO", "ratio"),
            "speedup_oo": ("FAST64.4 compact triplet", "Base/OO gpu_tot_sim_cycle", "Base/OO", "ratio"),
            "instructions": ("FAST64.4 Base compact JSON", "gpu_tot_sim_insn", "identity", "instructions")},
        "fast12_live_misses.csv": {"workload": ("FAST64.4 matrix", "workload", "identity", "member"), "mode": ("FAST64.4 matrix", "mode", "identity", "mode"),
            "create_or_acquire": ("FAST64.4 compact JSON", "mode-specific lower acquire", "identity", "requests"),
            "complete_or_release": ("FAST64.4 compact JSON", "mode-specific lower release", "identity", "requests"),
            "peak": ("FAST64.4 compact JSON", "DTC_L1_lower_outstanding_peak", "identity", "global requests"),
            "average_per_sm": ("Core telemetry audit", "NO_LOWER_OUTSTANDING_OCCUPANCY_INTEGRAL", "NOT_DERIVED", "MISSING_SOURCE_DEFINED_AVERAGE"),
            "terminal_lower": ("FAST64.4 compact JSON", "DTC_L1_lower_outstanding", "identity", "global requests")},
        "fast12_traffic.csv": {"workload": ("FAST64.4 matrix", "workload", "identity", "member"), "mode": ("FAST64.4 matrix", "mode", "identity", "mode")},
        "fast12_io_oo.csv": {"workload": ("FAST64.4 matrix", "workload", "identity", "member"), "mode": ("FAST64.4 matrix", "mode", "identity", "mode")},
    }
    columns = {
        "fast12_traffic.csv": ("l1_accesses", "l1_misses", "l2_accesses", "l2_misses", "l2_reservation_fails", "global_reads", "global_writes"),
        "fast12_io_oo.csv": ("head_not_ready", "head_ready", "hol_cycles", "hol_count", "retire", "ooo_retire", "immediate_reclaim", "deferred_reclaim", "final_ref_reclaim", "active_refs", "wakeups"),
    }
    for table, mapping in mappings.items():
        for column, (artifact, keys, formula, units) in mapping.items():
            entries.append((table, column, artifact, keys, formula, units, "SOURCE_DEFINED_OR_EXPLICIT_MISSING"))
    for table, names in columns.items():
        for column in names:
            entries.append((table, column, "FAST64.4 compact JSON", column, "identity", "source counter", "UNSUPPORTED_IF_ABSENT"))
    entries.append(("fast12_stalls.csv", "workload", "FAST64.3 structural companion", "workload", "identity", "member", "FAIL_CLOSED"))
    entries.append(("fast12_stalls.csv", "*", "FAST64.3 structural companion", "same-named structural column", "identity", "events/source units", "UNSUPPORTED_IF_ABSENT"))
    write_tsv(path, ("output_file", "output_column", "source_artifact", "source_metric_keys", "formula", "units_or_normalization", "missing_disposition"), entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage-ledger", type=Path, required=True)
    parser.add_argument("--stage4-matrix", type=Path, required=True)
    parser.add_argument("--stage3-structural", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_ALREADY_EXISTS")
    require_stage4_pass(args.stage_ledger)
    primary = validate_primary(args.stage4_matrix)
    validate_structural(args.stage3_structural)
    args.output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        feature_dir = temporary / "features"
        command = [sys.executable, str(ROOT / "util/dtc_l1/build_fast64_5_feature_tables_v1.py"),
                   "--stage-ledger", str(args.stage_ledger), "--stage4-dir", str(args.stage4_matrix.parent),
                   "--stage3-dir", str(args.stage3_structural.parent), "--output-dir", str(feature_dir)]
        result = subprocess.run(command, text=True, capture_output=True)
        if result.returncode:
            fail("FEATURE_BUILDER_V1_REJECTED=" + result.stderr.strip())
        for child in feature_dir.iterdir():
            shutil.move(str(child), temporary / child.name)
        feature_dir.rmdir()
        write_tsv(temporary / "fast64_5_input_manifest.tsv",
                  ("workload", "mode", "evidence_path", "evidence_sha256", *IDENTITY),
                  [tuple(row[key] for key in ("workload", "mode", "evidence_path", "evidence_sha256", *IDENTITY)) for row in primary])
        emitted_provenance(temporary / "fast64_5_emitted_column_provenance.tsv")
        write_tsv(temporary / "fast64_5_feature_build_status.tsv", ("item", "value"),
                  [("status", "MEASURED_FEATURES_PENDING_RESEARCHER_CAUSAL_CLASSIFICATION"),
                   ("stage4_matrix_sha256", sha256(args.stage4_matrix)),
                   ("stage3_structural_sha256", sha256(args.stage3_structural)),
                   ("stage_ledger_sha256", sha256(args.stage_ledger)),
                   ("promotion", "NONE")])
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_5_FEATURE_TABLES_V2_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
