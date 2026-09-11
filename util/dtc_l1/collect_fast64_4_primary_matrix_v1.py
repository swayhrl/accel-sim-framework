#!/usr/bin/env python3
"""Fail-closed collector for a complete FAST64.4 primary-matrix registry.

The input registry names already strict-parsed compact JSON summaries.  This
tool has no simulator authority and publishes only a fresh, atomically-created
candidate output directory.  Its outputs remain candidates pending the stage
handoff/checklist; it never writes a PASS marker.
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
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
          "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = {"BASE": "PAPER_BASE", "IO": "PAPER_IO", "OO": "PAPER_OO"}
CONFIG = {
    "BASE": ("FAST64_BASE_A1", "1a016e3cac65376330a92dd3fcf037d5fdcab5e7d295920be568e04600dd1cde"),
    "IO": ("FAST64_IO_A1", "d4a2d9d0088946b950370b922a8d8e34422bbca9bac26f109b3977fe02a7f621"),
    "OO": ("FAST64_OO_A1", "546c68f96d47f4650703ccfbc925bd789f923501d5607a77e79ca4845f234caa"),
}
REGISTRY_FIELDS = ("workload", "mode", "summary", "origin", "cap_disposition", "retry_resolution")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def require(mapping: dict, keys: tuple[str, ...], label: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        fail(f"{label}: MISSING=" + ",".join(missing))


def equal(mapping: dict, keys: tuple[str, ...], label: str) -> None:
    require(mapping, keys, label)
    if len({mapping[key] for key in keys}) != 1:
        fail(f"{label}: CONSERVATION=" + ",".join(keys))


def zero(mapping: dict, keys: tuple[str, ...], label: str) -> None:
    require(mapping, keys, label)
    bad = [key for key in keys if mapping[key] != 0]
    if bad:
        fail(f"{label}: TERMINAL_NONZERO=" + ",".join(bad))


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or any(tuple(row) != REGISTRY_FIELDS for row in rows):
        fail("INVALID_FAST64_4_PRIMARY_REGISTRY_SCHEMA")
    expected = {(workload, mode) for workload in ROSTER for mode in MODES}
    actual = {(row["workload"], row["mode"]) for row in rows}
    if len(rows) != 36 or actual != expected:
        fail("FAST64_4_REGISTRY_MUST_CONTAIN_EXACTLY_36_CELLS")
    if len(actual) != len(rows):
        fail("FAST64_4_REGISTRY_DUPLICATE_CELL")
    return rows


def read_summary(registry: dict[str, str]) -> dict:
    path = Path(registry["summary"])
    if not path.is_absolute():
        path = ROOT / path
    if not path.is_file():
        fail(f"{registry['workload']}/{registry['mode']}: SUMMARY_MISSING={path}")
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"{registry['workload']}/{registry['mode']}: SUMMARY_JSON_INVALID={error}")
    registry["_path"] = str(path)
    registry["_sha256"] = sha256(path)
    return record


def validate_row(registry: dict[str, str], record: dict) -> None:
    workload, mode = registry["workload"], registry["mode"]
    label = f"{workload}/{mode}"
    provenance, metrics = record.get("provenance", {}), record.get("metrics", {})
    if record.get("schema") != "dtc_l1_summary_v1":
        fail(f"{label}: SUMMARY_SCHEMA")
    config_id, config_sha = CONFIG[mode]
    expected = {"config_id": config_id, "config_sha256": config_sha}
    if provenance.get("workload_id", "").casefold() != workload.casefold() or any(provenance.get(k) != v for k, v in expected.items()):
        fail(f"{label}: PROVENANCE_MISMATCH")
    require(provenance, ("workload_sha256", "core_sha", "runtime_binary_sha256", "observer_overlay_sha256", "framework_sha"), label)
    if metrics.get("DTC_L1_mode") != MODES[mode]:
        fail(f"{label}: MODE_MISMATCH")
    require(metrics, ("gpu_tot_sim_cycle", "gpu_tot_sim_insn", "DTC_L1_lower_outstanding", "DTC_L1_lower_cap_full_events"), label)
    if metrics["gpu_tot_sim_cycle"] <= 0 or metrics["gpu_tot_sim_insn"] <= 0:
        fail(f"{label}: NO_PROGRESS")
    attempt = record.get("immutable_attempt", {})
    require(attempt, ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256"), label)
    trace = record.get("external_artifacts", {}).get("trace_list_sha256")
    if not trace:
        fail(f"{label}: TRACE_IDENTITY_MISSING")
    if mode == "BASE":
        equal(metrics, ("DTC_L1_pib_admits", "DTC_L1_pib_retires"), label)
        equal(metrics, ("DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released"), label)
        zero(metrics, ("DTC_L1_pib_occupancy", "DTC_L1_lower_outstanding"), label)
    elif mode == "IO":
        equal(metrics, ("DTC_L1_io_lower_created", "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses"), label)
        equal(metrics, ("DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed"), label)
        equal(metrics, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"), label)
        zero(metrics, ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"), label)
    else:
        equal(metrics, ("DTC_L1_oo_lower_created", "DTC_L1_oo_lower_issued", "DTC_L1_oo_lower_responses"), label)
        equal(metrics, ("DTC_L1_oo_completion_dependency_count", "DTC_L1_oo_completion_dependency_closed"), label)
        equal(metrics, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"), label)
        zero(metrics, ("DTC_L1_oo_inflight_current", "DTC_L1_oo_pib_occupancy", "DTC_L1_oo_active_refs", "DTC_L1_lower_outstanding"), label)
    cap = metrics["DTC_L1_lower_cap_full_events"]
    disposition = registry["cap_disposition"]
    if cap == 0 and disposition != "ZERO":
        fail(f"{label}: ZERO_CAP_REQUIRES_ZERO_DISPOSITION")
    if cap != 0 and not disposition.startswith("SOURCE_RESOLVED:"):
        fail(f"{label}: NONZERO_CAP_REQUIRES_SOURCE_RESOLVED_DISPOSITION")


def write_tsv(path: Path, headings: tuple[str, ...], rows: list[tuple[object, ...]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(headings)
        writer.writerows(rows)
    os.chmod(path, 0o444)


def collect(rows: list[dict[str, str]], records: dict[tuple[str, str], dict], out: Path, registry_sha: str) -> None:
    triplets: list[tuple[object, ...]] = []
    speedups: list[tuple[object, ...]] = []
    matrix: list[tuple[object, ...]] = []
    accounting: list[tuple[object, ...]] = []
    identity: list[tuple[object, ...]] = []
    raw: list[tuple[object, ...]] = []
    by_cell = {(row["workload"], row["mode"]): row for row in rows}
    for workload in ROSTER:
        selected = [(mode, by_cell[(workload, mode)], records[(workload, mode)]) for mode in MODES]
        p = [record["provenance"] for _, _, record in selected]
        common = ("workload_sha256", "core_sha", "runtime_binary_sha256", "observer_overlay_sha256", "framework_sha")
        if any(len({item[key] for item in p}) != 1 for key in common):
            fail(f"{workload}: TRIPLET_IDENTITY_MISMATCH")
        traces = {record["external_artifacts"]["trace_list_sha256"] for _, _, record in selected}
        insns = {record["metrics"]["gpu_tot_sim_insn"] for _, _, record in selected}
        if len(traces) != 1 or len(insns) != 1:
            fail(f"{workload}: TRIPLET_TRACE_OR_INSTRUCTION_MISMATCH")
        cycles = {mode: record["metrics"]["gpu_tot_sim_cycle"] for mode, _, record in selected}
        triplets.append((workload, *(p[0][key] for key in common), traces.pop(), *(cycles[mode] for mode in MODES), insns.pop(), "PASS"))
        speedups.append((workload, cycles["BASE"], cycles["IO"], cycles["OO"], f"{cycles['BASE']/cycles['IO']:.6f}", f"{cycles['BASE']/cycles['OO']:.6f}", "CANDIDATE_PENDING_STAGE4_HANDOFF"))
        for mode, row, record in selected:
            m, provenance = record["metrics"], record["provenance"]
            matrix.append((workload, mode, provenance.get("source_log", "NA"), row["origin"], "CANDIDATE_PENDING_STAGE4_HANDOFF", m["gpu_tot_sim_cycle"], m["gpu_tot_sim_insn"], provenance["config_sha256"], provenance["workload_sha256"], provenance["core_sha"], provenance["runtime_binary_sha256"], provenance["observer_overlay_sha256"], provenance["framework_sha"], row["summary"], row["_sha256"], record.get("external_artifacts", {}).get("run_dir", "NA")))
            if mode == "BASE":
                counts = (m["DTC_L1_lower_requests_acquired"], m["DTC_L1_lower_requests_released"], m["DTC_L1_lower_requests_released"], m["DTC_L1_pib_admits"], m["DTC_L1_pib_retires"], m["DTC_L1_pib_occupancy"], 0, m["DTC_L1_lower_outstanding"], 0)
            elif mode == "IO":
                counts = (m["DTC_L1_lower_credit_acquired"], m["DTC_L1_io_lower_issued"], m["DTC_L1_io_lower_responses"], m["DTC_L1_io_completion_dependency_count"], m["DTC_L1_io_completion_dependency_closed"], m["DTC_L1_io_pib_occupancy"], m["DTC_L1_io_inflight_current"], m["DTC_L1_lower_outstanding"], 0)
            else:
                counts = (m["DTC_L1_lower_credit_acquired"], m["DTC_L1_oo_lower_issued"], m["DTC_L1_oo_lower_responses"], m["DTC_L1_oo_completion_dependency_count"], m["DTC_L1_oo_completion_dependency_closed"], m["DTC_L1_oo_pib_occupancy"], m["DTC_L1_oo_inflight_current"], m["DTC_L1_lower_outstanding"], m["DTC_L1_oo_active_refs"])
            accounting.append((workload, mode, *counts, m["DTC_L1_lower_cap_full_events"], row["cap_disposition"], "PASS"))
            identity.append((workload, mode, row["summary"], row["_sha256"], provenance["config_sha256"], provenance["workload_sha256"], provenance["core_sha"], provenance["runtime_binary_sha256"], provenance["observer_overlay_sha256"], provenance["framework_sha"], record["external_artifacts"]["trace_list_sha256"]))
            raw.append((workload, mode, record.get("external_artifacts", {}).get("run_dir", "NA"), provenance.get("source_log", "NA"), record.get("external_artifacts", {}).get("simulator_stdout_sha256", "NA"), record.get("external_artifacts", {}).get("simulator_stderr_sha256", "NA")))
    gm_io = math.prod(float(row[4]) for row in speedups) ** (1 / len(ROSTER))
    gm_oo = math.prod(float(row[5]) for row in speedups) ** (1 / len(ROSTER))
    speedups.append(("GM-FAST12", "n/a", "n/a", "n/a", f"{gm_io:.6f}", f"{gm_oo:.6f}", "CANDIDATE_PENDING_STAGE4_HANDOFF"))
    write_tsv(out / "fast64_4_primary_matrix.tsv", ("workload", "mode", "accepted_namespace", "origin", "status", "cycles", "instructions", "config_sha256", "payload_sha256", "core_sha", "runtime_sha256", "observer_sha256", "scientific_framework_sha", "evidence_path", "evidence_sha256", "raw_run_ref"), matrix)
    write_tsv(out / "fast64_4_triplets.tsv", ("workload", "payload_sha256", "core_sha", "runtime_sha256", "observer_sha256", "scientific_framework_sha", "trace_list_sha256", "base_cycles", "io_cycles", "oo_cycles", "instructions", "status"), triplets)
    write_tsv(out / "fast64_4_speedup.tsv", ("workload", "base_cycles", "io_cycles", "oo_cycles", "speedup_io", "speedup_oo", "status"), speedups)
    write_tsv(out / "fast64_4_accounting.tsv", ("workload", "mode", "lower_created_or_acquired", "issued", "response_or_released", "dependency_create", "dependency_complete", "final_pib", "final_inflight", "final_lower", "final_oo_active_refs", "lower_cap_full_events", "cap_disposition", "accepted"), accounting)
    write_tsv(out / "fast64_4_identity_manifest.tsv", ("workload", "mode", "evidence_path", "evidence_sha256", "config_sha256", "payload_sha256", "core_sha", "runtime_sha256", "observer_sha256", "scientific_framework_sha", "trace_list_sha256"), identity)
    write_tsv(out / "fast64_4_raw_log_index.tsv", ("workload", "mode", "raw_run_ref", "source_log", "stdout_sha256", "stderr_sha256"), raw)
    write_tsv(out / "fast64_4_collector_status.tsv", ("item", "value"), [("status", "CANDIDATE_PENDING_STAGE4_HANDOFF"), ("accepted_cells", 36), ("membership", "FAST12_EXACT"), ("registry_sha256", registry_sha)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    rows = read_registry(args.registry)
    records: dict[tuple[str, str], dict] = {}
    for row in rows:
        record = read_summary(row)
        validate_row(row, record)
        records[(row["workload"], row["mode"])] = record
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        collect(rows, records, temporary, sha256(args.registry))
        os.chmod(temporary, 0o555)
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_4_PRIMARY_MATRIX_V1_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
