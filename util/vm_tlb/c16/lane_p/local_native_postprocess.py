#!/usr/bin/env python3
"""Qualify and locally postprocess C16 hash-closed Nsight Systems exports.

This program deliberately stops at phase-level attribution.  It never derives
an operator or layer from a kernel name; no direct mapping evidence means
``UNKNOWN``.  The large launch catalog stays in caller-selected scratch space
and is represented in review material by logical row counts and SHA-256.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


CATALOG_FIELDS = (
    "run_id", "deployment_id", "model_id", "model_revision", "tokenizer_revision",
    "scenario_id", "input_hash", "phase", "decode_step_bin", "device", "context",
    "stream", "correlation_id", "launch_ordinal", "kernel_name", "implementation_key",
    "grid", "block", "start_ns", "end_ns", "duration_ns", "operator_class", "layer_id",
    "shape_key", "dtype_key", "semantic_evidence", "mapping_status", "evidence_tier",
)
SEMANTIC_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "kernel_name", "implementation_key",
    "operator_class", "layer_id", "shape_key", "dtype_key", "semantic_evidence",
    "mapping_status",
)
COVERAGE_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "phase", "total_gpu_duration_ns",
    "mapped_gpu_duration_ns", "mapped_gpu_time_fraction", "status",
)
HEAVY_TAIL_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "phase", "kernel_identity", "duration_ns",
    "phase_gpu_time_fraction", "certainty_reason", "status",
)
RUN_SUMMARY_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "raw_profile_sha256", "sqlite_sha256",
    "kernel_rows", "catalog_rows", "distinct_streams", "correlated_kernel_rows",
    "nvtx_full_forward_ranges", "nvtx_prefill_ranges", "nvtx_decode_ranges", "status",
)
PHASE_SUMMARY_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "phase", "launch_rows", "gpu_duration_ns",
    "distinct_kernel_names", "distinct_streams", "status",
)
BASELINE_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "input_hash", "measurement_kind", "measurement_index",
    "profiler_mode", "output_checksum", "duration_ms", "peak_allocated_bytes", "peak_reserved_bytes",
    "evidence_tier", "status",
)
IMPLEMENTATION_FIELDS = (
    "run_id", "deployment_id", "scenario_id", "attention_backend", "runtime_kv_representation",
    "quantization_runtime", "compile_state", "logits_policy", "evidence", "status",
)
RAW_INDEX_FIELDS = (
    "artifact_role", "run_id", "path", "size_bytes", "sha256", "logical_row_count",
    "git_policy", "hash_binding_or_receipt", "retention_status",
)
REQUIRED_NVTX = ("C16_NATIVE_FULL_FORWARD", "C16_PHASE_PREFILL", "C16_PHASE_DECODE")


class ContractError(RuntimeError):
    """A missing evidence link or unsupported SQLite shape."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root is not an object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def write_tsv(path: Path, fields: tuple[str, ...], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def deterministic_gzip(source: Path, destination: Path) -> None:
    with source.open("rb") as input_handle, destination.open("wb") as output_handle:
        with gzip.GzipFile(filename="", mode="wb", fileobj=output_handle, mtime=0) as gzip_handle:
            for block in iter(lambda: input_handle.read(1024 * 1024), b""):
                gzip_handle.write(block)


def scalar(connection: sqlite3.Connection, sql: str) -> int:
    row = connection.execute(sql).fetchone()
    if row is None or not isinstance(row[0], int):
        raise ContractError(f"SQLite count query failed: {sql}")
    return row[0]


def table_schema(connection: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").fetchall()
    schema: dict[str, list[dict[str, Any]]] = {}
    for (name,) in rows:
        table_name = str(name)
        escaped_name = table_name.replace("'", "''")
        schema[table_name] = [
            {"cid": row[0], "name": row[1], "type": row[2], "notnull": row[3], "default": row[4], "pk": row[5]}
            for row in connection.execute(f"PRAGMA table_info('{escaped_name}')")
        ]
    return schema


def marker_counts(connection: sqlite3.Connection) -> dict[str, int]:
    return {name: scalar(connection, "SELECT COUNT(*) FROM NVTX_EVENTS WHERE text = " + repr(name)) for name in REQUIRED_NVTX}


def export_evidence(sqlite_path: Path) -> dict[str, Any]:
    try:
        connection = sqlite3.connect(sqlite_path)
        evidence = {
            "schema": table_schema(connection),
            "kernel_rows": scalar(connection, "SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL"),
            "named_kernel_rows": scalar(connection, """
                SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k
                JOIN StringIds s ON s.id = k.demangledName
                WHERE s.value IS NOT NULL AND s.value != ''
            """),
            "stream_ids": [row[0] for row in connection.execute("SELECT DISTINCT streamId FROM CUPTI_ACTIVITY_KIND_KERNEL ORDER BY streamId")],
            "correlated_kernel_rows": scalar(connection, """
                SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k
                JOIN CUPTI_ACTIVITY_KIND_RUNTIME r ON r.correlationId = k.correlationId
                WHERE k.correlationId IS NOT NULL
            """),
            "nvtx_range_counts": marker_counts(connection),
            "nvtx_kernel_overlap_rows": scalar(connection, """
                SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k
                JOIN NVTX_EVENTS n ON ((k.start + k.end) / 2) BETWEEN n.start AND n.end
                WHERE n.text IN ('C16_NATIVE_FULL_FORWARD', 'C16_PHASE_PREFILL', 'C16_PHASE_DECODE')
            """),
        }
    except sqlite3.Error as exc:
        raise ContractError(f"cannot inspect SQLite export {sqlite_path}: {exc}") from exc
    finally:
        try:
            connection.close()
        except UnboundLocalError:
            pass
    evidence["distinct_stream_count"] = len(evidence["stream_ids"])
    return evidence


def verify_source(source: dict[str, Any]) -> dict[str, Any]:
    required = ("label", "raw_profile", "sqlite", "profile_receipt", "runner_receipt", "binding_receipt", "validation_receipt", "baseline_receipt")
    if any(not isinstance(source.get(key), str) or not source[key] for key in required):
        raise ContractError("source manifest has incomplete hash-closed inputs")
    paths = {key: Path(source[key]) for key in required if key != "label"}
    if any(not path.is_file() for path in paths.values()):
        absent = [key for key, path in paths.items() if not path.is_file()]
        raise ContractError(f"source {source['label']} has absent inputs: {absent}")
    profile, runner, binding, validation, baseline = (
        read_json(paths["profile_receipt"]), read_json(paths["runner_receipt"]),
        read_json(paths["binding_receipt"]), read_json(paths["validation_receipt"]), read_json(paths["baseline_receipt"]),
    )
    inputs = validation.get("inputs", {})
    expected = {
        "raw_profile": inputs.get("raw_profile_sha256"),
        "profile_receipt": inputs.get("profile_receipt_sha256"), "runner_receipt": inputs.get("runner_receipt_sha256"),
        "binding_receipt": inputs.get("binding_receipt_sha256"),
    }
    actual = {key: sha256_file(paths[key]) for key in expected}
    if any(not isinstance(digest, str) or actual[key] != digest for key, digest in expected.items()):
        raise ContractError(f"source {source['label']} does not match its validation receipt hash bindings")
    actual["sqlite"] = sha256_file(paths["sqlite"])
    actual["baseline_receipt"] = sha256_file(paths["baseline_receipt"])
    remote_sqlite_sha256 = inputs.get("sqlite_sha256")
    if not isinstance(remote_sqlite_sha256, str) or not remote_sqlite_sha256:
        raise ContractError(f"source {source['label']} validation receipt lacks remote SQLite SHA-256")
    if actual["sqlite"] != remote_sqlite_sha256:
        qualification_path = source.get("local_export_qualification")
        if not isinstance(qualification_path, str) or not qualification_path:
            raise ContractError(f"source {source['label']} local SQLite differs from remote export without a passing local-export qualification")
        qualification = read_json(Path(qualification_path))
        if qualification.get("status") != "PASS":
            raise ContractError(f"source {source['label']} local-export qualification did not pass")
        if qualification.get("remote_sqlite", {}).get("sha256") == remote_sqlite_sha256 and qualification.get("local_sqlite", {}).get("sha256") == actual["sqlite"]:
            if qualification.get("identity") != profile.get("identity"):
                raise ContractError(f"source {source['label']} qualification identity differs from profile identity")
        else:
            tool_version = source.get("local_export_tool_version")
            if not isinstance(tool_version, str) or not tool_version or tool_version != qualification.get("local_nsys_version"):
                raise ContractError(f"source {source['label']} local SQLite is not bound to the qualified local nsys tool version")
            if qualification.get("essential_schema_match") is not True or qualification.get("field_mismatches"):
                raise ContractError(f"source {source['label']} relies on a qualification that lacks consumed-field equivalence")
    identity = profile.get("identity")
    if not isinstance(identity, dict) or identity != runner.get("identity") or identity != validation.get("identity"):
        raise ContractError(f"source {source['label']} profile/runner/validation identities differ")
    if profile.get("execution_mode") != "NATIVE_GPU" or validation.get("status") != "G1_EXPORT_VALIDATED_PASS":
        raise ContractError(f"source {source['label']} is not a validated native G1 export")
    baseline_identity = baseline.get("identity")
    if baseline.get("execution_mode") != "NATIVE_GPU" or baseline.get("scientific_eligible") is not True or not isinstance(baseline_identity, dict):
        raise ContractError(f"source {source['label']} baseline receipt is not scientific native evidence")
    for key in ("deployment_id", "scenario_id", "input_hash"):
        if baseline_identity.get(key) != identity.get(key):
            raise ContractError(f"source {source['label']} baseline identity differs at {key}")
    checks = runner.get("checks", {})
    if binding.get("package_id") != checks.get("package_id") or binding.get("package_fixed_commit") != checks.get("package_fixed_commit"):
        raise ContractError(f"source {source['label']} package identity differs from binding")
    return {"source": source, "paths": paths, "profile": profile, "runner": runner, "binding": binding, "validation": validation, "baseline": baseline, "hashes": actual, "remote_sqlite_sha256": remote_sqlite_sha256}


def marker_intervals(connection: sqlite3.Connection) -> tuple[list[tuple[int, int]], list[tuple[int, int, str]], list[tuple[int, int, int]]]:
    rows = connection.execute("SELECT start, end, text FROM NVTX_EVENTS WHERE end IS NOT NULL AND text LIKE 'C16_%' ORDER BY start, rowid").fetchall()
    full: list[tuple[int, int]] = []
    phases: list[tuple[int, int, str]] = []
    steps: list[tuple[int, int, int]] = []
    for start, end, text in rows:
        if not isinstance(start, int) or not isinstance(end, int) or end < start or not isinstance(text, str):
            continue
        if text == "C16_NATIVE_FULL_FORWARD":
            full.append((start, end))
        elif text == "C16_PHASE_PREFILL":
            phases.append((start, end, "PREFILL"))
        elif text == "C16_PHASE_DECODE":
            phases.append((start, end, "DECODE"))
        elif text.startswith("C16_DECODE_STEP_"):
            try:
                steps.append((start, end, int(text.rsplit("_", 1)[1])))
            except ValueError:
                pass
    if not full or not any(phase == "PREFILL" for _, _, phase in phases) or not any(phase == "DECODE" for _, _, phase in phases):
        raise ContractError("SQLite export lacks required C16 NVTX full/prefill/decode intervals")
    return full, phases, steps


def contains(intervals: list[tuple[int, int]], point: int) -> bool:
    return any(start <= point <= end for start, end in intervals)


def classify(midpoint: int, phases: list[tuple[int, int, str]], steps: list[tuple[int, int, int]]) -> tuple[str, str]:
    for start, end, step in steps:
        if start <= midpoint <= end:
            return "DECODE", f"STEP_{step}"
    for start, end, phase in phases:
        if start <= midpoint <= end:
            return phase, "NOT_APPLICABLE" if phase == "PREFILL" else "UNBINNED"
    return "FULL_FORWARD_UNATTRIBUTED", "NOT_APPLICABLE"


def source_catalog_rows(verified: dict[str, Any]) -> Iterable[dict[str, Any]]:
    identity = verified["profile"]["identity"]
    scenario = verified["binding"].get("scenario", {})
    shape_key = f"B{scenario.get('batch_size')}_T{scenario.get('prefill_tokens')}_D{scenario.get('decode_tokens')}"
    connection = sqlite3.connect(verified["paths"]["sqlite"])
    emitted = 0
    expected = scalar(connection, "SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL")
    try:
        full, phases, steps = marker_intervals(connection)
        query = """
            SELECT k.rowid, k.start, k.end, k.deviceId, k.contextId, k.streamId, k.correlationId,
                   k.gridX, k.gridY, k.gridZ, k.blockX, k.blockY, k.blockZ, s.value
            FROM CUPTI_ACTIVITY_KIND_KERNEL k
            LEFT JOIN StringIds s ON s.id = k.demangledName
            ORDER BY k.start, k.rowid
        """
        for ordinal, (rowid, start, end, device, context, stream, correlation, gx, gy, gz, bx, by, bz, name) in enumerate(connection.execute(query), start=1):
            midpoint = (int(start) + int(end)) // 2
            if not contains(full, midpoint):
                raise ContractError(f"{verified['source']['label']} kernel ordinal {ordinal} lies outside all full-forward NVTX intervals; refusing to drop it")
            phase, decode_step = classify(midpoint, phases, steps)
            emitted += 1
            yield {
                "run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "model_id": identity["model_id"],
                "model_revision": identity["model_revision"], "tokenizer_revision": identity["tokenizer_revision"],
                "scenario_id": identity["scenario_id"], "input_hash": identity["input_hash"], "phase": phase,
                "decode_step_bin": decode_step, "device": f"cuda:{device}", "context": f"CUDA_CONTEXT_{context}",
                "stream": f"CUDA_STREAM_{stream}", "correlation_id": f"CUDA_CORRELATION_{correlation}",
                "launch_ordinal": ordinal, "kernel_name": name if isinstance(name, str) and name else "[UNRESOLVED_KERNEL_NAME]",
                "implementation_key": identity["implementation_key"], "grid": f"{gx}x{gy}x{gz}", "block": f"{bx}x{by}x{bz}",
                "start_ns": int(start), "end_ns": int(end), "duration_ns": int(end) - int(start),
                "operator_class": "UNKNOWN", "layer_id": "UNKNOWN", "shape_key": shape_key,
                "dtype_key": identity["dtype"], "semantic_evidence": "NSYS_KERNEL_NAME_PLUS_NVTX_PHASE",
                "mapping_status": "UNKNOWN_OPERATOR_LAYER_NO_DIRECT_EVIDENCE", "evidence_tier": "NATIVE_PROFILED",
            }
    finally:
        connection.close()
    if emitted != expected:
        raise ContractError(f"{verified['source']['label']} catalog lost launches: emitted {emitted}, source has {expected}")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def derive_tables(catalog: Path, output_dir: Path) -> dict[str, int]:
    rows = read_rows(catalog)
    semantic_seen: set[tuple[str, str, str, str]] = set()
    semantic: list[dict[str, str]] = []
    coverage: dict[tuple[str, str, str, str], int] = defaultdict(int)
    phase_rows: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["run_id"], row["scenario_id"], row["kernel_name"], row["phase"])
        if key not in semantic_seen:
            semantic_seen.add(key)
            semantic.append({field: row[field] for field in SEMANTIC_FIELDS})
        run_phase = (row["run_id"], row["deployment_id"], row["scenario_id"], row["phase"])
        coverage[run_phase] += int(row["duration_ns"])
        phase_rows[run_phase].append(row)
    write_tsv(output_dir / "KERNEL_SEMANTIC_MAP.tsv", SEMANTIC_FIELDS, semantic)
    coverage_rows = [{
        "run_id": run_id, "deployment_id": deployment_id, "scenario_id": scenario_id, "phase": phase,
        "total_gpu_duration_ns": duration, "mapped_gpu_duration_ns": 0, "mapped_gpu_time_fraction": "0.0",
        "status": "UNKNOWN_OPERATOR_LAYER_NO_DIRECT_EVIDENCE",
    } for (run_id, deployment_id, scenario_id, phase), duration in sorted(coverage.items())]
    write_tsv(output_dir / "SEMANTIC_COVERAGE.tsv", COVERAGE_FIELDS, coverage_rows)
    heavy: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for (run_id, deployment_id, scenario_id, phase), members in sorted(phase_rows.items()):
        total = coverage[(run_id, deployment_id, scenario_id, phase)]
        summaries.append({
            "run_id": run_id, "deployment_id": deployment_id, "scenario_id": scenario_id, "phase": phase,
            "launch_rows": len(members), "gpu_duration_ns": total,
            "distinct_kernel_names": len({row["kernel_name"] for row in members}),
            "distinct_streams": len({row["stream"] for row in members}),
            "status": "REAL_NATIVE_SCHEMA_SANITY_PROVISIONAL",
        })
        for row in members:
            duration = int(row["duration_ns"])
            if total and duration / total >= 0.01:
                heavy.append({
                    "run_id": run_id, "deployment_id": deployment_id, "scenario_id": scenario_id, "phase": phase,
                    "kernel_identity": "|".join((row["kernel_name"], row["grid"], row["block"], row["dtype_key"])),
                    "duration_ns": duration, "phase_gpu_time_fraction": format(duration / total, ".12g"),
                    "certainty_reason": "SINGLE_LAUNCH_AT_LEAST_ONE_PERCENT_PHASE_GPU_TIME",
                    "status": "PROVISIONAL_NOT_SELECTOR_FREEZE",
                })
    write_tsv(output_dir / "HEAVY_TAIL_KERNELS.tsv", HEAVY_TAIL_FIELDS, heavy)
    write_tsv(output_dir / "PHASE_SUMMARY.tsv", PHASE_SUMMARY_FIELDS, summaries)
    return {"kernel_catalog_rows": len(rows), "semantic_rows": len(semantic), "heavy_tail_rows": len(heavy), "phase_summary_rows": len(summaries)}


def write_baselines_and_audits(verified: list[dict[str, Any]], output: Path) -> dict[str, int]:
    baseline_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    for item in verified:
        receipt = item["baseline"]
        identity, artifacts, checks = receipt["identity"], receipt.get("artifacts", {}), receipt.get("checks", {})
        durations = artifacts.get("duration_ms")
        if not isinstance(durations, list) or not durations:
            raise ContractError(f"baseline receipt for {item['source']['label']} lacks retained measure durations")
        for index, duration in enumerate(durations):
            baseline_rows.append({
                "run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"],
                "input_hash": identity["input_hash"], "measurement_kind": "MEASURE", "measurement_index": index,
                "profiler_mode": "UNPROFILED", "output_checksum": checks.get("output_checksum", "UNKNOWN"),
                "duration_ms": duration, "peak_allocated_bytes": artifacts.get("peak_allocated_bytes", "UNKNOWN"),
                "peak_reserved_bytes": artifacts.get("peak_reserved_bytes", "UNKNOWN"), "evidence_tier": "NATIVE_BASELINE",
                "status": "COMPLETE",
            })
        runtime = item["profile"].get("runtime", {})
        profiled_identity = item["profile"]["identity"]
        audit_rows.append({
            "run_id": profiled_identity["run_id"], "deployment_id": profiled_identity["deployment_id"], "scenario_id": profiled_identity["scenario_id"],
            "attention_backend": runtime.get("attention_backend", "UNKNOWN_NO_DIRECT_RECEIPT_FIELD"),
            "runtime_kv_representation": "UNKNOWN_NO_DIRECT_RUNTIME_LAYOUT_EVIDENCE",
            "quantization_runtime": profiled_identity.get("quantization", "UNKNOWN_NO_DIRECT_RECEIPT_FIELD"),
            "compile_state": runtime.get("compile_state", "UNKNOWN_NO_DIRECT_RECEIPT_FIELD"),
            "logits_policy": "UNKNOWN_NO_DIRECT_RECEIPT_FIELD",
            "evidence": "profile receipt runtime identity only; no operator/layer or runtime-layout inference",
            "status": "PARTIAL_DIRECT_RUNTIME_EVIDENCE",
        })
    write_tsv(output / "NATIVE_BASELINE.tsv", BASELINE_FIELDS, baseline_rows)
    write_tsv(output / "RUNTIME_IMPLEMENTATION_AUDIT.tsv", IMPLEMENTATION_FIELDS, audit_rows)
    return {"native_baseline_rows": len(baseline_rows), "runtime_implementation_audit_rows": len(audit_rows)}


def write_raw_index(verified: list[dict[str, Any]], output: Path, catalog_rows: int) -> None:
    rows: list[dict[str, Any]] = []
    for item in verified:
        run_id = item["profile"]["identity"]["run_id"]
        rows.append({
            "artifact_role": "RAW_NSYS_REP", "run_id": run_id, "path": item["paths"]["raw_profile"],
            "size_bytes": item["paths"]["raw_profile"].stat().st_size, "sha256": item["hashes"]["raw_profile"],
            "logical_row_count": "NA", "git_policy": "OUTSIDE_GIT", "hash_binding_or_receipt": item["paths"]["validation_receipt"],
            "retention_status": "LOCAL_HASH_VERIFIED",
        })
        rows.append({
            "artifact_role": "NSYS_SQLITE", "run_id": run_id, "path": item["paths"]["sqlite"],
            "size_bytes": item["paths"]["sqlite"].stat().st_size, "sha256": item["hashes"]["sqlite"],
            "logical_row_count": export_evidence(item["paths"]["sqlite"])["kernel_rows"], "git_policy": "OUTSIDE_GIT",
            "hash_binding_or_receipt": item["paths"]["validation_receipt"], "retention_status": "LOCAL_HASH_VERIFIED",
        })
    for name, role, count in (
        ("KERNEL_CATALOG.tsv", "FULL_LAUNCH_CATALOG", catalog_rows),
        ("KERNEL_CATALOG.tsv.gz", "FULL_LAUNCH_CATALOG_DETERMINISTIC_GZIP", catalog_rows),
    ):
        path = output / name
        rows.append({
            "artifact_role": role, "run_id": "MULTI_RUN", "path": path, "size_bytes": path.stat().st_size,
            "sha256": sha256_file(path), "logical_row_count": count, "git_policy": "OUTSIDE_GIT",
            "hash_binding_or_receipt": str(output / "POSTPROCESS_MANIFEST.json"), "retention_status": "LOCAL_GENERATED_RETAIN",
        })
    write_tsv(output / "RAW_INDEX.tsv", RAW_INDEX_FIELDS, rows)


def qualify(args: argparse.Namespace) -> None:
    remote, local = Path(args.remote_sqlite), Path(args.local_sqlite)
    if not remote.is_file() or not local.is_file():
        raise ContractError("qualification requires both remote and local SQLite exports")
    remote_evidence, local_evidence = export_evidence(remote), export_evidence(local)
    profile = read_json(Path(args.profile_receipt))
    binding = read_json(Path(args.binding_receipt))
    identity = profile.get("identity")
    if not isinstance(identity, dict):
        raise ContractError("qualification profile receipt lacks identity")
    binding_identity = {
        "deployment_id": binding.get("deployment_id"), "model_id": binding.get("model_id"),
        "model_revision": binding.get("model_revision"), "tokenizer_revision": binding.get("tokenizer_revision"),
        "scenario_id": binding.get("scenario", {}).get("scenario_id"),
        "input_hash": binding.get("input", {}).get("raw_input_sha256"),
    }
    if any(identity.get(key) != value for key, value in binding_identity.items()):
        raise ContractError("qualification profile/binding identity does not agree")
    comparable = ("kernel_rows", "named_kernel_rows", "stream_ids", "correlated_kernel_rows", "nvtx_range_counts", "nvtx_kernel_overlap_rows")
    mismatches = {key: {"remote": remote_evidence[key], "local": local_evidence[key]} for key in comparable if remote_evidence[key] != local_evidence[key]}
    essential_tables = ("CUPTI_ACTIVITY_KIND_KERNEL", "CUPTI_ACTIVITY_KIND_RUNTIME", "NVTX_EVENTS", "StringIds")
    essential_schema_match = all(remote_evidence["schema"].get(name) == local_evidence["schema"].get(name) for name in essential_tables)
    result = {
        "schema_version": "C16_P_LOCAL_NSYS_EXPORT_QUALIFICATION_V1",
        "status": "PASS" if not mismatches and essential_schema_match else "FAIL",
        "qualification_scope": "remote_vs_local_export_of_same_frozen_nsys_rep",
        "remote_sqlite": {"path": str(remote), "sha256": sha256_file(remote), "evidence": remote_evidence},
        "local_sqlite": {"path": str(local), "sha256": sha256_file(local), "evidence": local_evidence},
        "schema_exact_match": remote_evidence["schema"] == local_evidence["schema"],
        "essential_schema_match": essential_schema_match,
        "field_mismatches": mismatches,
        "local_nsys_version": args.local_nsys_version,
        "identity": identity,
        "binding": {key: binding.get(key) for key in ("package_id", "package_fixed_commit", "package_manifest_sha256")},
        "note": "SQLite byte identity is intentionally not required; consumed schema and row relationships are compared.",
    }
    write_json(Path(args.output), result)
    if result["status"] != "PASS":
        raise ContractError(f"local export qualification failed; see {args.output}")


def local_export(args: argparse.Namespace) -> None:
    raw, output, receipt = Path(args.raw_profile), Path(args.output), Path(args.receipt)
    nsys = Path(args.nsys)
    if not raw.is_file() or not nsys.is_file():
        raise ContractError("local export requires an existing raw report and nsys executable")
    actual_raw_sha = sha256_file(raw)
    if actual_raw_sha != args.raw_sha256:
        raise ContractError("raw report SHA-256 does not equal the caller's hash-closed expected value")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "nice", "-n", "19", "ionice", "-c2", "-n7", str(nsys), "export", "--type", "sqlite",
        "--force-overwrite", "true", "--quiet", "true", "--output", str(output), str(raw),
    ]
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0 or not output.is_file():
        raise ContractError(f"local nsys export failed ({completed.returncode}): {completed.stderr.strip()}")
    version = subprocess.run([str(nsys), "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if version.returncode != 0:
        raise ContractError(f"cannot record local nsys version: {version.stderr.strip()}")
    write_json(receipt, {
        "schema_version": "C16_P_LOCAL_NSYS_EXPORT_RECEIPT_V1",
        "status": "LOCAL_EXPORT_COMPLETE",
        "raw_profile": {"path": str(raw), "size_bytes": raw.stat().st_size, "sha256": actual_raw_sha},
        "sqlite": {"path": str(output), "size_bytes": output.stat().st_size, "sha256": sha256_file(output)},
        "local_nsys": {"path": str(nsys), "version": version.stdout.strip()},
        "command": command,
        "stdout": completed.stdout.strip(),
    })


def postprocess(args: argparse.Namespace) -> None:
    manifest = read_json(Path(args.source_manifest))
    source_specs = manifest.get("sources")
    if not isinstance(source_specs, list) or not source_specs:
        raise ContractError("source manifest must have at least one source")
    verified = [verify_source(source) for source in source_specs]
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    catalog = output / "KERNEL_CATALOG.tsv"
    write_tsv(catalog, CATALOG_FIELDS, (row for source in verified for row in source_catalog_rows(source)))
    stats = derive_tables(catalog, output)
    stats.update(write_baselines_and_audits(verified, output))
    deterministic_gzip(catalog, output / "KERNEL_CATALOG.tsv.gz")
    write_raw_index(verified, output, stats["kernel_catalog_rows"])
    run_summaries: list[dict[str, Any]] = []
    for item in verified:
        evidence = export_evidence(item["paths"]["sqlite"])
        identity = item["profile"]["identity"]
        run_summaries.append({
            "run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"],
            "raw_profile_sha256": item["hashes"]["raw_profile"], "sqlite_sha256": item["hashes"]["sqlite"],
            "kernel_rows": evidence["kernel_rows"], "catalog_rows": sum(1 for row in read_rows(catalog) if row["run_id"] == identity["run_id"]),
            "distinct_streams": evidence["distinct_stream_count"], "correlated_kernel_rows": evidence["correlated_kernel_rows"],
            "nvtx_full_forward_ranges": evidence["nvtx_range_counts"]["C16_NATIVE_FULL_FORWARD"],
            "nvtx_prefill_ranges": evidence["nvtx_range_counts"]["C16_PHASE_PREFILL"],
            "nvtx_decode_ranges": evidence["nvtx_range_counts"]["C16_PHASE_DECODE"],
            "status": "REAL_NATIVE_SCHEMA_SANITY_PROVISIONAL",
        })
    write_tsv(output / "RUN_SUMMARY.tsv", RUN_SUMMARY_FIELDS, run_summaries)
    files = []
    for path in sorted(output.glob("*.tsv")) + sorted(output.glob("*.tsv.gz")):
        files.append({"path": str(path), "name": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    output_manifest = {
        "schema_version": "C16_P_LOCAL_NATIVE_POSTPROCESS_V1",
        "status": "REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL",
        "scientific_eligible": False,
        "provisional_reason": "G formal native producer checkpoint has not yet been committed; not consumable as a cross-lane scientific conclusion.",
        "semantic_policy": "operator_class and layer_id are UNKNOWN unless direct mapping evidence is supplied; no kernel-name inference was performed.",
        "population_policy": "all source CUPTI kernel rows are retained; full TSV and deterministic gzip remain raw-outside-Git.",
        "sources": [{
            "label": item["source"]["label"], "identity": item["profile"]["identity"], "input_hashes": item["hashes"],
            "remote_sqlite_sha256": item["remote_sqlite_sha256"],
            "validation_receipt": str(item["paths"]["validation_receipt"]),
        } for item in verified],
        "derived": stats,
        "files": files,
    }
    write_json(output / "POSTPROCESS_MANIFEST.json", output_manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    qualification = subparsers.add_parser("qualify", help="compare remote and local SQLite exports")
    qualification.add_argument("--remote-sqlite", required=True)
    qualification.add_argument("--local-sqlite", required=True)
    qualification.add_argument("--profile-receipt", required=True)
    qualification.add_argument("--binding-receipt", required=True)
    qualification.add_argument("--local-nsys-version", required=True)
    qualification.add_argument("--output", required=True)
    qualification.set_defaults(func=qualify)
    export = subparsers.add_parser("export", help="low-priority local nsys export for a hash-closed report")
    export.add_argument("--nsys", required=True)
    export.add_argument("--raw-profile", required=True)
    export.add_argument("--raw-sha256", required=True)
    export.add_argument("--output", required=True)
    export.add_argument("--receipt", required=True)
    export.set_defaults(func=local_export)
    census = subparsers.add_parser("postprocess", help="build a complete local raw-outside-Git census")
    census.add_argument("--source-manifest", required=True)
    census.add_argument("--output-dir", required=True)
    census.set_defaults(func=postprocess)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 P local postprocess: {exc}", file=sys.stderr)
        raise SystemExit(2)
