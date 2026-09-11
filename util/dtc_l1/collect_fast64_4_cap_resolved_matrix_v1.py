#!/usr/bin/env python3
"""Future-only FAST64.4 collector with explicit cap-resolution provenance.

The frozen V1 collector cannot represent a common final cap together with a
source-proven cap-inert 8192 reuse.  This tool imports only V1's output writer
after pinning its source bytes, and independently rejects every undeclared cap
identity mix.  It has no simulator/controller authority and never emits PASS.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FROZEN = ROOT / "util/dtc_l1/collect_fast64_4_primary_matrix_v1.py"
FROZEN_SHA256 = "72668f8057bb4d0f8ea6d487246724a879c1adec516ce0a1667a4369e6603104"
ROSTER = ("ATAX", "BICG", "GESUMMV", "GEMM", "2DConvolution", "Btree",
          "DWT2D", "Gaussian", "Hotspot1", "LUD", "NN", "MRI-Q")
MODES = {"BASE": "PAPER_BASE", "IO": "PAPER_IO", "OO": "PAPER_OO"}
REGISTRY_FIELDS = ("workload", "mode", "summary", "origin", "cap_disposition", "retry_resolution")
CAP_FIELDS = ("workload", "mode", "formal_cap", "source_cap", "cap_identity_class", "expected_config_id", "expected_config_sha256", "resolution_authority", "resolution_authority_sha256")
REACQUIRED = "REACQUIRED_AT_FINAL_CAP"
INERT_REUSE = "SOURCE_PROVEN_CAP_INERT_REUSE_8192_TO_FINAL"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def load_frozen() -> object:
    if sha256(FROZEN) != FROZEN_SHA256:
        fail("FROZEN_V1_COLLECTOR_SHA_MISMATCH")
    spec = importlib.util.spec_from_file_location("fast64_4_collector_v1_frozen", FROZEN)
    if spec is None or spec.loader is None:
        fail("FROZEN_V1_COLLECTOR_LOAD_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_tsv(path: Path, fields: tuple[str, ...], label: str) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    if not rows or any(tuple(row) != fields for row in rows):
        fail(f"{label}_SCHEMA_INVALID")
    return rows


def cap_map(path: Path) -> tuple[dict[tuple[str, str], dict[str, str]], int]:
    rows = read_tsv(path, CAP_FIELDS, "CAP_RESOLUTION")
    expected = {(workload, mode) for workload in ROSTER for mode in MODES}
    mapped = {(row["workload"], row["mode"]): row for row in rows}
    if len(rows) != 36 or set(mapped) != expected or len(mapped) != len(rows):
        fail("CAP_RESOLUTION_MUST_HAVE_EXACT_36_CELLS")
    formal_caps = {row["formal_cap"] for row in rows}
    if len(formal_caps) != 1:
        fail("CAP_RESOLUTION_NOT_COMMON_PLATFORM_CAP")
    try:
        formal_cap = int(formal_caps.pop())
    except ValueError as error:
        raise RuntimeError("CAP_RESOLUTION_FORMAL_CAP_INVALID") from error
    if formal_cap <= 8192:
        fail("CAP_RESOLUTION_FORMAL_CAP_NOT_ABOVE_BOUND_CANDIDATE")
    for key, row in mapped.items():
        label = f"{key[0]}/{key[1]}"
        try:
            source_cap = int(row["source_cap"])
        except ValueError as error:
            raise RuntimeError(f"{label}: SOURCE_CAP_INVALID") from error
        if source_cap > formal_cap or source_cap <= 0:
            fail(f"{label}: SOURCE_CAP_RANGE_INVALID")
        authority = ROOT / row["resolution_authority"]
        if not authority.is_file() or sha256(authority) != row["resolution_authority_sha256"]:
            fail(f"{label}: CAP_RESOLUTION_AUTHORITY_MISMATCH")
        if source_cap == formal_cap:
            if row["cap_identity_class"] != REACQUIRED:
                fail(f"{label}: FINAL_CAP_REACQUISITION_CLASS_REQUIRED")
        elif not (source_cap == 8192 and row["cap_identity_class"] == INERT_REUSE):
            fail(f"{label}: UNDECLARED_CAP_IDENTITY_MIX")
    return mapped, formal_cap


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
    if any(mapping[key] != 0 for key in keys):
        fail(f"{label}: TERMINAL_NONZERO=" + ",".join(key for key in keys if mapping[key] != 0))


def validate_row(v1: object, row: dict[str, str], cap: dict[str, str]) -> dict:
    label = f"{row['workload']}/{row['mode']}"
    record = v1.read_summary(row)
    provenance, metrics = record.get("provenance", {}), record.get("metrics", {})
    if record.get("schema") != "dtc_l1_summary_v1":
        fail(f"{label}: SUMMARY_SCHEMA")
    if provenance.get("workload_id", "").casefold() != row["workload"].casefold():
        fail(f"{label}: WORKLOAD_PROVENANCE_MISMATCH")
    if provenance.get("config_id") != cap["expected_config_id"] or provenance.get("config_sha256") != cap["expected_config_sha256"]:
        fail(f"{label}: CONFIG_CAP_IDENTITY_MISMATCH")
    require(provenance, ("workload_sha256", "core_sha", "runtime_binary_sha256", "observer_overlay_sha256", "framework_sha"), label)
    if metrics.get("DTC_L1_mode") != MODES[row["mode"]]:
        fail(f"{label}: MODE_MISMATCH")
    require(metrics, ("gpu_tot_sim_cycle", "gpu_tot_sim_insn", "DTC_L1_lower_outstanding", "DTC_L1_lower_cap_full_events"), label)
    if metrics["gpu_tot_sim_cycle"] <= 0 or metrics["gpu_tot_sim_insn"] <= 0 or metrics["DTC_L1_lower_cap_full_events"] != 0:
        fail(f"{label}: CAP_OR_PROGRESS_INVALID")
    attempt = record.get("immutable_attempt", {})
    require(attempt, ("attempt_uuid", "runner_sha256", "start_receipt_sha256", "terminal_receipt_sha256"), label)
    if not record.get("external_artifacts", {}).get("trace_list_sha256"):
        fail(f"{label}: TRACE_IDENTITY_MISSING")
    if row["mode"] == "BASE":
        equal(metrics, ("DTC_L1_pib_admits", "DTC_L1_pib_retires"), label)
        equal(metrics, ("DTC_L1_lower_requests_acquired", "DTC_L1_lower_requests_released"), label)
        zero(metrics, ("DTC_L1_pib_occupancy", "DTC_L1_lower_outstanding"), label)
    elif row["mode"] == "IO":
        equal(metrics, ("DTC_L1_io_lower_created", "DTC_L1_io_lower_issued", "DTC_L1_io_lower_responses"), label)
        equal(metrics, ("DTC_L1_io_completion_dependency_count", "DTC_L1_io_completion_dependency_closed"), label)
        equal(metrics, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"), label)
        zero(metrics, ("DTC_L1_io_inflight_current", "DTC_L1_io_pib_occupancy", "DTC_L1_lower_outstanding"), label)
    else:
        equal(metrics, ("DTC_L1_oo_lower_created", "DTC_L1_oo_lower_issued", "DTC_L1_oo_lower_responses"), label)
        equal(metrics, ("DTC_L1_oo_completion_dependency_count", "DTC_L1_oo_completion_dependency_closed"), label)
        equal(metrics, ("DTC_L1_lower_credit_acquired", "DTC_L1_lower_credit_released"), label)
        zero(metrics, ("DTC_L1_oo_inflight_current", "DTC_L1_oo_pib_occupancy", "DTC_L1_oo_active_refs", "DTC_L1_lower_outstanding"), label)
    return record


def write_cap_identity(path: Path, rows: list[dict[str, str]], mapping: dict[tuple[str, str], dict[str, str]], formal_cap: int, registry: Path, cap_path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("workload", "mode", "formal_cap", "source_cap", "cap_identity_class", "expected_config_id", "expected_config_sha256", "registry_cap_disposition", "resolution_authority", "resolution_authority_sha256"))
        for row in rows:
            cap = mapping[(row["workload"], row["mode"])]
            writer.writerow((row["workload"], row["mode"], formal_cap, cap["source_cap"], cap["cap_identity_class"], cap["expected_config_id"], cap["expected_config_sha256"], row["cap_disposition"], cap["resolution_authority"], cap["resolution_authority_sha256"]))
    os.chmod(path, 0o444)
    with (path.parent / "fast64_4_collector_status.tsv").open("a", encoding="utf-8") as stream:
        stream.write(f"formal_common_cap\t{formal_cap}\nregistry_sha256\t{sha256(registry)}\ncap_resolution_sha256\t{sha256(cap_path)}\nfrozen_v1_collector_sha256\t{FROZEN_SHA256}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--cap-resolution", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output_dir.exists():
        fail("OUTPUT_DIRECTORY_ALREADY_EXISTS")
    v1 = load_frozen()
    rows = v1.read_registry(args.registry)
    mapping, formal_cap = cap_map(args.cap_resolution)
    records = {(row["workload"], row["mode"]): validate_row(v1, row, mapping[(row["workload"], row["mode"])]) for row in rows}
    temporary = Path(tempfile.mkdtemp(prefix=f".{args.output_dir.name}.tmp.", dir=args.output_dir.parent))
    try:
        v1.collect(rows, records, temporary, sha256(args.registry))
        write_cap_identity(temporary / "fast64_4_cap_identity_manifest.tsv", rows, mapping, formal_cap, args.registry, args.cap_resolution)
        os.chmod(temporary, 0o555)
        os.replace(temporary, args.output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    print(f"FAST64_4_CAP_RESOLVED_MATRIX_V1_CANDIDATE_PASS output={args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
