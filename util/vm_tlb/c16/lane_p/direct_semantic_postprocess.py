#!/usr/bin/env python3
"""Locally qualify and merge a hash-closed C16 direct-semantic event.

This is deliberately conservative.  It derives semantics only from direct
runtime-module NVTX containment inside the diagnostic report.  A clean report
is never joined by timestamp, CUDA correlation, stream, duration, or launch
ordinal.  It may receive a diagnostic label only when its report-scoped
structural tuple has exactly one diagnostic candidate.
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


TAG_PREFIX = "C16_DIRECT_SEMANTIC_V1"
DIRECT = "DIRECT_DIAGNOSTIC_STRUCTURAL_UNAMBIGUOUS"
UNKNOWN_ZERO = "UNKNOWN_NO_DIAGNOSTIC_STRUCTURAL_CANDIDATE"
UNKNOWN_MULTI = "UNKNOWN_AMBIGUOUS_DIAGNOSTIC_STRUCTURAL_CANDIDATES"
UNKNOWN_NONDIRECT = "UNKNOWN_UNIQUE_DIAGNOSTIC_CANDIDATE_WITHOUT_DIRECT_EVIDENCE"

DIAGNOSTIC_FIELDS = (
    "diagnostic_profile_report_id", "deployment_id", "scenario_id", "run_id", "kernel_rowid", "kernel_name",
    "device", "context", "stream", "correlation_id", "grid", "block", "start_ns", "end_ns", "duration_ns",
    "phase", "layer_id", "operator", "operator_detail", "module_path", "module_class", "evidence_type",
    "nvtx_evidence_type", "module_identity_evidence_type", "evidence_source", "mapping_status",
    "source_semantic_receipt_sha256", "source_raw_profile_sha256", "source_package_manifest_sha256",
)
CLEAN_MAP_FIELDS = (
    "clean_profile_report_id", "clean_run_id", "deployment_id", "model_id", "model_revision",
    "tokenizer_revision", "scenario_id", "input_hash", "implementation_key", "dtype_key", "phase",
    "decode_step_bin", "device", "context", "stream", "correlation_id", "launch_ordinal", "kernel_name",
    "grid", "block", "duration_ns", "structural_key_sha256", "diagnostic_profile_report_id",
    "diagnostic_run_id", "diagnostic_kernel_rowid", "diagnostic_structural_candidate_count", "layer_id",
    "operator", "operator_detail", "module_path", "module_class", "evidence_type", "evidence_source",
    "mapping_status",
)
COVERAGE_FIELDS = (
    "clean_profile_report_id", "clean_run_id", "deployment_id", "scenario_id", "phase", "total_launch_rows",
    "direct_mapped_launch_rows", "direct_mapped_launch_fraction", "total_gpu_duration_ns",
    "direct_mapped_gpu_duration_ns", "direct_mapped_gpu_time_fraction", "ambiguous_launch_rows",
    "ambiguous_gpu_duration_ns", "unknown_launch_rows", "unknown_gpu_duration_ns", "status",
)
RAW_INDEX_FIELDS = (
    "artifact_role", "path", "size_bytes", "sha256", "logical_row_count", "git_policy", "retention_status",
)

class ContractError(RuntimeError):
    """The event is incomplete or violates the P join contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be an object: {path}")
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


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ContractError(f"producer object is not available at {commit}:{path}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def identity_subset_matches(observed: Any, expected: dict[str, Any], *, label: str) -> None:
    if not isinstance(observed, dict) or not observed:
        raise ContractError(f"{label} lacks identity")
    mismatches = [key for key, value in observed.items() if expected.get(key) != value]
    if mismatches:
        raise ContractError(f"{label} identity differs from frozen event at: {','.join(sorted(mismatches))}")


def require_file_hash(entry: dict[str, Any], *, label: str) -> Path:
    path = Path(str(entry.get("path", "")))
    expected = entry.get("sha256")
    expected_size = entry.get("size_bytes")
    if not path.is_file() or not isinstance(expected, str) or not expected or not isinstance(expected_size, int):
        raise ContractError(f"{label} lacks an existing path, SHA-256, or byte size")
    if path.stat().st_size != expected_size or sha256_file(path) != expected:
        raise ContractError(f"{label} local file does not match its hash-closed declaration")
    return path


def direct_payload_roles(payloads: dict[str, Path]) -> dict[str, Path]:
    """Resolve direct-semantic payload roles without encoding a model name.

    The producer artifact id is part of the producer's hash-closed manifest.
    P accepts exactly one raw report, remote SQLite export, and full direct map
    with the standard role suffixes.  A gzip companion does not satisfy the
    full-map role.
    """
    suffixes = {
        "raw": "_DIRECT_SEMANTIC_RAW",
        "remote_sqlite": "_DIRECT_SEMANTIC_SQLITE",
        "producer_map": "_DIRECT_SEMANTIC_MAP",
    }
    result: dict[str, Path] = {}
    for role, suffix in suffixes.items():
        matches = [path for artifact_id, path in payloads.items() if artifact_id.endswith(suffix)]
        if len(matches) != 1:
            raise ContractError(f"producer manifest must contain exactly one {role} direct-semantic payload")
        result[role] = matches[0]
    return result


def producer_event(event: dict[str, Any], repo: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Path]]:
    producer = event.get("producer")
    identity = event.get("identity")
    if not isinstance(producer, dict) or not isinstance(identity, dict):
        raise ContractError("event lacks producer or identity")
    commit, manifest_path, manifest_sha = producer.get("commit"), producer.get("manifest_path"), producer.get("manifest_sha256")
    if not all(isinstance(value, str) and value for value in (commit, manifest_path, manifest_sha)):
        raise ContractError("event producer commit/manifest closure is incomplete")
    exists = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if exists.returncode:
        raise ContractError(f"producer commit is not locally available: {commit}")
    manifest_bytes = git_bytes(repo, commit, manifest_path)
    if sha256_bytes(manifest_bytes) != manifest_sha:
        raise ContractError("producer manifest content does not match the frozen event SHA-256")
    try:
        manifest = json.loads(manifest_bytes)
    except json.JSONDecodeError as exc:
        raise ContractError("producer manifest is not JSON") from exc
    if not isinstance(manifest, dict) or manifest.get("status") != "DIRECT_SEMANTIC_QUALIFICATION_PASS":
        raise ContractError("producer manifest is not a passing direct-semantic event")
    identity_subset_matches(manifest.get("identity"), identity, label="producer manifest")
    if manifest.get("classification") != "SEMANTIC_DIAGNOSTIC_ONLY":
        raise ContractError("producer manifest is not explicitly diagnostic-only")
    base = manifest_path.rsplit("/", 1)[0]
    for item in manifest.get("git_payloads", []):
        if not isinstance(item, dict):
            raise ContractError("producer manifest has an invalid Git payload")
        payload_path = item.get("path")
        if not isinstance(payload_path, str) or not isinstance(item.get("sha256"), str) or not isinstance(item.get("size_bytes"), int):
            raise ContractError("producer Git payload lacks path/hash/size")
        payload = git_bytes(repo, commit, f"{base}/{payload_path}")
        if len(payload) != item["size_bytes"] or sha256_bytes(payload) != item["sha256"]:
            raise ContractError(f"producer Git payload is not hash-closed: {payload_path}")
    local_by_artifact_id: dict[str, Path] = {}
    for item in manifest.get("external_hash_closed_payloads", []):
        if not isinstance(item, dict) or not isinstance(item.get("artifact_id"), str):
            raise ContractError("producer manifest has an invalid external payload")
        local_by_artifact_id[item["artifact_id"]] = require_file_hash(item, label=item["artifact_id"])
    return producer, manifest, direct_payload_roles(local_by_artifact_id)


def receipt_provenance(event: dict[str, Any], manifest: dict[str, Any], local: dict[str, Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    receipts = event.get("receipts")
    if not isinstance(receipts, dict):
        raise ContractError("event lacks diagnostic receipt declarations")
    semantic_path = require_file_hash(receipts.get("semantic", {}), label="semantic receipt")
    nsys_path = require_file_hash(receipts.get("nsys", {}), label="nsys receipt")
    semantic, nsys = read_json(semantic_path), read_json(nsys_path)
    identity = event["identity"]
    identity_subset_matches(semantic.get("identity"), identity, label="semantic receipt")
    identity_subset_matches(nsys.get("identity"), identity, label="nsys receipt")
    semantic_checks = semantic.get("checks", {})
    nsys_checks = nsys.get("checks", {})
    required_semantic = (
        semantic.get("status") == "SEMANTIC_DIAGNOSTIC_ONLY_COMPLETE",
        semantic.get("scientific_eligible") is False,
        semantic.get("scientific_eligible_for_timing") is False,
        semantic_checks.get("direct_module_identity_only") is True,
        semantic_checks.get("kernel_name_heuristic_forbidden") is True,
        semantic_checks.get("duration_semantic_guessing_forbidden") is True,
        semantic_checks.get("historical_operator_backfill_forbidden") is True,
        isinstance(semantic_checks.get("direct_module_hook_count"), int) and semantic_checks["direct_module_hook_count"] > 0,
    )
    required_nsys = (
        nsys.get("execution_mode") == "NATIVE_GPU",
        nsys.get("scientific_eligible") is False,
        nsys_checks.get("semantic_diagnostic_only") is True,
        nsys_checks.get("naked_launch_ordinal_join_forbidden") is True,
    )
    if not all(required_semantic) or not all(required_nsys):
        raise ContractError("diagnostic receipts do not prove direct, non-timing semantic provenance")
    if not local["raw"].is_file():
        raise ContractError("diagnostic raw report disappeared after producer-manifest closure")
    return semantic, nsys


def schema(connection: sqlite3.Connection) -> dict[str, list[tuple[Any, ...]]]:
    result: dict[str, list[tuple[Any, ...]]] = {}
    for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name"):
        table_name = str(name)
        escaped_name = table_name.replace("'", "''")
        result[table_name] = [tuple(row) for row in connection.execute(f"PRAGMA table_info('{escaped_name}')")]
    return result


def scalar(connection: sqlite3.Connection, query: str) -> int:
    row = connection.execute(query).fetchone()
    if row is None or not isinstance(row[0], int):
        raise ContractError(f"SQLite scalar query failed: {query}")
    return row[0]


def sqlite_evidence(path: Path) -> dict[str, Any]:
    connection = sqlite3.connect(path)
    try:
        return {
            "schema": schema(connection),
            "kernel_rows": scalar(connection, "SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL"),
            "correlated_kernel_rows": scalar(connection, "SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k JOIN CUPTI_ACTIVITY_KIND_RUNTIME r ON r.correlationId = k.correlationId"),
            "stream_ids": [row[0] for row in connection.execute("SELECT DISTINCT streamId FROM CUPTI_ACTIVITY_KIND_KERNEL ORDER BY streamId")],
            "phase_ranges": {marker: scalar(connection, "SELECT COUNT(*) FROM NVTX_EVENTS WHERE text = " + repr(marker)) for marker in ("C16_PHASE_PREFILL", "C16_PHASE_DECODE")},
            "direct_runtime_ranges": scalar(connection, "SELECT COUNT(*) FROM NVTX_EVENTS WHERE text LIKE 'C16_DIRECT_SEMANTIC_V1|%'") ,
        }
    finally:
        connection.close()


def local_export_qualification(remote: Path, local: Path, output: Path, *, nsys_version: str, identity: dict[str, Any]) -> dict[str, Any]:
    remote_evidence, local_evidence = sqlite_evidence(remote), sqlite_evidence(local)
    required = ("CUPTI_ACTIVITY_KIND_KERNEL", "CUPTI_ACTIVITY_KIND_RUNTIME", "NVTX_EVENTS", "StringIds")
    essential_schema_match = all(remote_evidence["schema"].get(table) == local_evidence["schema"].get(table) for table in required)
    comparable = ("kernel_rows", "correlated_kernel_rows", "stream_ids", "phase_ranges", "direct_runtime_ranges")
    mismatches = {field: {"remote": remote_evidence[field], "local": local_evidence[field]} for field in comparable if remote_evidence[field] != local_evidence[field]}
    result = {
        "schema_version": "C16_P_P2_LOCAL_EXPORT_QUALIFICATION_V1",
        "status": "PASS" if essential_schema_match and not mismatches else "FAIL",
        "identity": identity,
        "remote_sqlite": {"path": str(remote), "sha256": sha256_file(remote), "evidence": remote_evidence},
        "local_sqlite": {"path": str(local), "sha256": sha256_file(local), "evidence": local_evidence},
        "essential_consumed_schema_match": essential_schema_match,
        "schema_exact_match": remote_evidence["schema"] == local_evidence["schema"],
        "local_only_tables": sorted(set(local_evidence["schema"]) - set(remote_evidence["schema"])),
        "remote_only_tables": sorted(set(remote_evidence["schema"]) - set(local_evidence["schema"])),
        "field_mismatches": mismatches,
        "local_nsys_version": nsys_version,
        "sqlite_byte_identity_required": False,
    }
    write_json(output, result)
    if result["status"] != "PASS":
        raise ContractError("local diagnostic export failed consumed-schema/population qualification")
    return result


def parse_tag(text: str, identity: dict[str, Any]) -> dict[str, str] | None:
    if not text.startswith(TAG_PREFIX + "|"):
        return None
    fields: dict[str, str] = {}
    for part in text.split("|")[1:]:
        if "=" not in part:
            return None
        key, value = part.split("=", 1)
        if not key or not value or key in fields:
            return None
        fields[key] = value
    needed = {"run_id", "deployment_id", "scenario_id", "layer_id", "operator", "operator_detail", "module_path", "module_class"}
    if set(fields) != needed or any(fields[key] != identity[key] for key in ("run_id", "deployment_id", "scenario_id")):
        return None
    if fields["operator"] not in {"ATTENTION", "FFN", "NORM", "EMBEDDING_OUTPUT"}:
        return None
    return fields


def choose_range(midpoint: int, ranges: list[tuple[int, int, dict[str, str]]]) -> tuple[dict[str, str] | None, bool]:
    candidates = [(end - start, fields) for start, end, fields in ranges if start <= midpoint <= end]
    if not candidates:
        return None, False
    candidates.sort(key=lambda item: item[0])
    narrowest = candidates[0][0]
    tied = [fields for width, fields in candidates if width == narrowest]
    labels = {(item["layer_id"], item["operator"], item["operator_detail"], item["module_path"]) for item in tied}
    return (tied[0], False) if len(labels) == 1 else (None, True)


def phase_at(midpoint: int, ranges: list[tuple[int, int, str]]) -> str:
    matches = [phase for start, end, phase in ranges if start <= midpoint <= end]
    return matches[0] if len(matches) == 1 else "UNKNOWN"


def diagnostic_rows(sqlite_path: Path, *, identity: dict[str, Any], profile_sha: str, semantic_sha: str, package_sha: str) -> tuple[list[dict[str, Any]], int, int]:
    connection = sqlite3.connect(sqlite_path)
    try:
        direct_ranges: list[tuple[int, int, dict[str, str]]] = []
        phases: list[tuple[int, int, str]] = []
        for start, end, text in connection.execute("SELECT start, end, text FROM NVTX_EVENTS WHERE end IS NOT NULL ORDER BY start, rowid"):
            if not isinstance(text, str) or int(end) <= int(start):
                continue
            if text in {"C16_PHASE_PREFILL", "C16_PHASE_DECODE"}:
                phases.append((int(start), int(end), text.removeprefix("C16_PHASE_")))
            parsed = parse_tag(text, identity)
            if parsed is not None:
                direct_ranges.append((int(start), int(end), parsed))
        if not direct_ranges:
            raise ContractError("local diagnostic export has no parseable direct module NVTX ranges")
        query = """
            SELECT k.rowid, k.start, k.end, k.deviceId, k.contextId, k.streamId, k.correlationId,
                   k.gridX, k.gridY, k.gridZ, k.blockX, k.blockY, k.blockZ, s.value
            FROM CUPTI_ACTIVITY_KIND_KERNEL k LEFT JOIN StringIds s ON s.id = k.demangledName
            ORDER BY k.start, k.rowid
        """
        rows: list[dict[str, Any]] = []
        ambiguous = 0
        for rowid, start, end, device, context, stream, correlation, gx, gy, gz, bx, by, bz, name in connection.execute(query):
            start_i, end_i = int(start), int(end)
            semantic, collision = choose_range((start_i + end_i) // 2, direct_ranges)
            if collision:
                ambiguous += 1
            row: dict[str, Any] = {
                "diagnostic_profile_report_id": profile_sha, "deployment_id": identity["deployment_id"],
                "scenario_id": identity["scenario_id"], "run_id": identity["run_id"], "kernel_rowid": rowid,
                "kernel_name": name if isinstance(name, str) and name else "[UNRESOLVED_KERNEL_NAME]",
                "device": f"cuda:{device}", "context": f"CUDA_CONTEXT_{context}", "stream": f"CUDA_STREAM_{stream}",
                "correlation_id": f"CUDA_CORRELATION_{correlation}", "grid": f"{gx}x{gy}x{gz}", "block": f"{bx}x{by}x{bz}",
                "start_ns": start_i, "end_ns": end_i, "duration_ns": end_i - start_i,
                "phase": phase_at((start_i + end_i) // 2, phases), "source_semantic_receipt_sha256": semantic_sha,
                "source_raw_profile_sha256": profile_sha, "source_package_manifest_sha256": package_sha,
            }
            if semantic is None:
                row.update({"layer_id": "UNKNOWN", "operator": "UNKNOWN", "operator_detail": "UNKNOWN", "module_path": "UNKNOWN", "module_class": "UNKNOWN", "evidence_type": "UNKNOWN", "nvtx_evidence_type": "UNKNOWN", "module_identity_evidence_type": "UNKNOWN", "evidence_source": "NO_UNAMBIGUOUS_DIRECT_RUNTIME_NVTX_CONTAINMENT", "mapping_status": "UNKNOWN_AMBIGUOUS_DIRECT_RANGE" if collision else "UNKNOWN_CONSERVATIVE"})
            else:
                row.update({"layer_id": semantic["layer_id"], "operator": semantic["operator"], "operator_detail": semantic["operator_detail"], "module_path": semantic["module_path"], "module_class": semantic["module_class"], "evidence_type": "DIRECT_MODULE_ID", "nvtx_evidence_type": "DIRECT_RUNTIME_NVTX", "module_identity_evidence_type": "DIRECT_MODULE_ID", "evidence_source": "DIRECT_RUNTIME_NVTX_TEMPORAL_CONTAINMENT", "mapping_status": "DIRECT_UNAMBIGUOUS"})

            rows.append(row)
    finally:
        connection.close()
    return rows, len(direct_ranges), ambiguous


def diagnostic_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row[field]) for field in ("run_id", "kernel_rowid", "correlation_id", "stream", "start_ns", "end_ns"))


def reproduce_producer_map(rows: list[dict[str, Any]], producer_map: Path) -> dict[str, Any]:
    with producer_map.open("r", encoding="utf-8", newline="") as handle:
        published = list(csv.DictReader(handle, delimiter="\t"))
    published_by_key = {tuple(row[field] for field in ("run_id", "kernel_rowid", "correlation_id", "stream", "start_ns", "end_ns")): row for row in published}
    local_by_key = {diagnostic_key(row): row for row in rows}
    if len(published_by_key) != len(published) or len(local_by_key) != len(rows):
        raise ContractError("diagnostic map does not retain unique report-local stable keys")
    fields = ("kernel_name", "device", "context", "grid", "block", "duration_ns", "phase", "layer_id", "operator", "operator_detail", "module_path", "module_class", "evidence_type", "nvtx_evidence_type", "module_identity_evidence_type", "evidence_source", "mapping_status")
    mismatches = 0
    for key, local in local_by_key.items():
        remote = published_by_key.get(key)
        if remote is None or any(str(local[field]) != remote[field] for field in fields):
            mismatches += 1
    result = {"published_rows": len(published), "local_rows": len(rows), "published_unique_keys": len(published_by_key), "local_unique_keys": len(local_by_key), "field_mismatch_rows": mismatches, "status": "PASS" if not mismatches and len(published) == len(rows) else "FAIL"}
    if result["status"] != "PASS":
        raise ContractError("local direct-semantic reconstruction does not reproduce the producer's published semantic map")
    return result


def structural_values(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row[field]) for field in ("deployment_id", "scenario_id", "input_hash", "implementation_key", "dtype_key", "phase", "device", "context", "kernel_name", "grid", "block"))


def structural_hash(values: tuple[str, ...]) -> str:
    return hashlib.sha256("\x1f".join(values).encode("utf-8")).hexdigest()


def clean_profile(event: dict[str, Any]) -> tuple[dict[str, str], dict[str, Any]]:
    clean = event.get("clean_catalog")
    if not isinstance(clean, dict):
        raise ContractError("event lacks clean catalog closure")
    catalog = require_file_hash(clean.get("catalog", {}), label="clean KERNEL_CATALOG")
    index = require_file_hash(clean.get("profile_index", {}), label="clean PROFILE_REPORT_INDEX")
    with index.open("r", encoding="utf-8", newline="") as handle:
        matches = [row for row in csv.DictReader(handle, delimiter="\t") if row.get("run_id") == clean.get("run_id")]
    if len(matches) != 1:
        raise ContractError("clean profile report index does not have one frozen S2 report")
    profile = matches[0]
    if profile.get("profile_report_id") != clean.get("profile_report_sha256") or profile.get("raw_report_sha256") != clean.get("profile_report_sha256"):
        raise ContractError("clean report SHA does not match its frozen profile index")
    raw_path = Path(profile.get("raw_report_path", ""))
    if not raw_path.is_file() or sha256_file(raw_path) != clean["profile_report_sha256"]:
        raise ContractError("clean raw report is absent or no longer hash-closed")
    if int(profile.get("kernel_rows", "-1")) != clean.get("expected_kernel_rows"):
        raise ContractError("clean profile index has an unexpected kernel population")
    return profile, {**clean, "catalog_path": catalog}


def merge_clean_catalog(event: dict[str, Any], diagnostic: list[dict[str, Any]], output: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    profile, clean = clean_profile(event)
    identity = event["identity"]
    diagnostic_index: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in diagnostic:
        structural = (
            str(row["deployment_id"]), str(row["scenario_id"]), str(identity["input_hash"]),
            str(identity["implementation_key"]), str(identity["dtype"]), str(row["phase"]), str(row["device"]),
            str(row["context"]), str(row["kernel_name"]), str(row["grid"]), str(row["block"]),
        )
        diagnostic_index[structural].append(row)
    catalog_path = clean["catalog_path"]
    map_path = output / "DIRECT_SEMANTIC_MAP.tsv"
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rows_written = 0
    with catalog_path.open("r", encoding="utf-8", newline="") as input_handle, tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=output, prefix=".DIRECT_SEMANTIC_MAP.", suffix=".tmp", delete=False) as output_handle:
        reader = csv.DictReader(input_handle, delimiter="\t")
        writer = csv.DictWriter(output_handle, fieldnames=CLEAN_MAP_FIELDS, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in reader:
            if row.get("run_id") != clean["run_id"]:
                continue
            expected = {"deployment_id": identity["deployment_id"], "model_id": identity["model_id"], "model_revision": identity["model_revision"], "tokenizer_revision": identity["tokenizer_revision"], "scenario_id": identity["scenario_id"], "input_hash": identity["input_hash"], "implementation_key": identity["implementation_key"], "dtype_key": identity["dtype"]}
            if any(row.get(field) != value for field, value in expected.items()):
                raise ContractError("clean catalog row identity does not match direct-semantic event")
            values = structural_values(row)
            candidates = diagnostic_index.get(values, [])
            phase = row["phase"]
            duration = int(row["duration_ns"])
            counts[phase]["total_rows"] += 1
            counts[phase]["total_duration"] += duration
            base: dict[str, Any] = {
                "clean_profile_report_id": profile["profile_report_id"], "clean_run_id": row["run_id"],
                **{field: row[field] for field in ("deployment_id", "model_id", "model_revision", "tokenizer_revision", "scenario_id", "input_hash", "implementation_key", "dtype_key", "phase", "decode_step_bin", "device", "context", "stream", "correlation_id", "launch_ordinal", "kernel_name", "grid", "block", "duration_ns")},
                "structural_key_sha256": structural_hash(values), "diagnostic_profile_report_id": "UNKNOWN",
                "diagnostic_run_id": "UNKNOWN", "diagnostic_kernel_rowid": "UNKNOWN",
                "diagnostic_structural_candidate_count": len(candidates), "layer_id": "UNKNOWN", "operator": "UNKNOWN",
                "operator_detail": "UNKNOWN", "module_path": "UNKNOWN", "module_class": "UNKNOWN",
                "evidence_type": "UNKNOWN", "evidence_source": "NO_UNIQUE_REPORT_SCOPED_STRUCTURAL_DIAGNOSTIC_MATCH",
            }
            if len(candidates) == 1 and candidates[0]["mapping_status"] == "DIRECT_UNAMBIGUOUS":
                candidate = candidates[0]
                base.update({"diagnostic_profile_report_id": candidate["diagnostic_profile_report_id"], "diagnostic_run_id": candidate["run_id"], "diagnostic_kernel_rowid": candidate["kernel_rowid"], "layer_id": candidate["layer_id"], "operator": candidate["operator"], "operator_detail": candidate["operator_detail"], "module_path": candidate["module_path"], "module_class": candidate["module_class"], "evidence_type": "DIRECT_MODULE_ID", "evidence_source": "DIRECT_RUNTIME_NVTX_TEMPORAL_CONTAINMENT_IN_DIAGNOSTIC__UNIQUE_REPORT_SCOPED_STRUCTURAL_MATCH", "mapping_status": DIRECT})
                counts[phase]["mapped_rows"] += 1
                counts[phase]["mapped_duration"] += duration
            elif len(candidates) == 0:
                base["mapping_status"] = UNKNOWN_ZERO
                counts[phase]["unknown_rows"] += 1
                counts[phase]["unknown_duration"] += duration
            elif len(candidates) > 1:
                base["mapping_status"] = UNKNOWN_MULTI
                counts[phase]["ambiguous_rows"] += 1
                counts[phase]["ambiguous_duration"] += duration
                counts[phase]["unknown_rows"] += 1
                counts[phase]["unknown_duration"] += duration
            else:
                base["mapping_status"] = UNKNOWN_NONDIRECT
                counts[phase]["unknown_rows"] += 1
                counts[phase]["unknown_duration"] += duration
            writer.writerow(base)
            rows_written += 1
        temporary = Path(output_handle.name)
    os.replace(temporary, map_path)
    if rows_written != clean["expected_kernel_rows"]:
        raise ContractError(f"clean semantic merge lost launches: wrote {rows_written}, expected {clean['expected_kernel_rows']}")
    coverage = []
    for phase, values in sorted(counts.items()):
        total_duration = values["total_duration"]
        coverage.append({
            "clean_profile_report_id": profile["profile_report_id"], "clean_run_id": clean["run_id"],
            "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"], "phase": phase,
            "total_launch_rows": values["total_rows"], "direct_mapped_launch_rows": values["mapped_rows"],
            "direct_mapped_launch_fraction": values["mapped_rows"] / values["total_rows"] if values["total_rows"] else 0.0,
            "total_gpu_duration_ns": total_duration, "direct_mapped_gpu_duration_ns": values["mapped_duration"],
            "direct_mapped_gpu_time_fraction": values["mapped_duration"] / total_duration if total_duration else 0.0,
            "ambiguous_launch_rows": values["ambiguous_rows"], "ambiguous_gpu_duration_ns": values["ambiguous_duration"],
            "unknown_launch_rows": values["unknown_rows"], "unknown_gpu_duration_ns": values["unknown_duration"],
            "status": "COVERAGE_LIMITED" if values["mapped_duration"] / total_duration < 0.95 else "DIRECT_SEMANTIC_COVERAGE_QUALIFIED",
        })
    write_tsv(output / "SEMANTIC_COVERAGE.tsv", COVERAGE_FIELDS, coverage)
    deterministic_gzip(map_path, output / "DIRECT_SEMANTIC_MAP.tsv.gz")
    return {"clean_profile": profile, "clean_rows": rows_written, "coverage": coverage, "diagnostic_structural_key_fields": ["deployment_id", "scenario_id", "input_hash", "implementation_key", "dtype_key", "phase", "device", "context", "kernel_name", "grid", "block"], "prohibited_cross_report_join_fields": ["start_ns", "end_ns", "duration_ns", "correlation_id", "stream", "launch_ordinal"]}, coverage


def diagnostic_coverage(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["phase"])].append(row)
    result = []
    for phase, values in sorted(grouped.items()):
        total = sum(int(row["duration_ns"]) for row in values)
        mapped = [row for row in values if row["mapping_status"] == "DIRECT_UNAMBIGUOUS"]
        result.append({"phase": phase, "total_kernel_rows": len(values), "total_gpu_duration_ns": total, "direct_mapped_kernel_rows": len(mapped), "direct_mapped_gpu_duration_ns": sum(int(row["duration_ns"]) for row in mapped), "unknown_kernel_rows": len(values) - len(mapped), "ambiguous_kernel_rows": sum(row["mapping_status"] == "UNKNOWN_AMBIGUOUS_DIRECT_RANGE" for row in values), "status": "SEMANTIC_DIAGNOSTIC_ONLY"})
    return result


def write_raw_index(output: Path, sources: list[tuple[str, Path, int | str]]) -> None:
    rows = []
    for role, path, population in sources:
        rows.append({"artifact_role": role, "path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path), "logical_row_count": population, "git_policy": "OUTSIDE_GIT" if path.is_relative_to(output) or path.suffix in {".sqlite", ".rep"} else "GIT_DECLARATION_ONLY", "retention_status": "HASH_CLOSED_RETAIN"})
    write_tsv(output / "RAW_ARTIFACT_INDEX.tsv", RAW_INDEX_FIELDS, rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--event", type=Path, required=True)
    parser.add_argument("--local-sqlite", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--local-nsys-version", required=True)
    args = parser.parse_args()
    event = read_json(args.event)
    if event.get("schema_version") != "C16_P_P2_EVENT_V1" or event.get("event_type") != "P2_DIRECT_SEMANTIC":
        raise ContractError("input is not a C16 P hash-closed P2 event")
    join_contract = require_file_hash(event.get("join_key_contract", {}), label="frozen P JOIN_KEY_CONTRACT")
    producer, manifest, local = producer_event(event, args.repo)
    semantic, nsys = receipt_provenance(event, manifest, local)
    if not args.local_sqlite.is_file():
        raise ContractError("local diagnostic SQLite export is absent")
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    qualification = local_export_qualification(local["remote_sqlite"], args.local_sqlite, output / "LOCAL_DIAGNOSTIC_EXPORT_QUALIFICATION.json", nsys_version=args.local_nsys_version, identity=event["identity"])
    rows, range_count, direct_ambiguity = diagnostic_rows(args.local_sqlite, identity=event["identity"], profile_sha=sha256_file(local["raw"]), semantic_sha=sha256_file(Path(event["receipts"]["semantic"]["path"])), package_sha=str(semantic["checks"]["package_manifest_sha256"]))
    write_tsv(output / "DIAGNOSTIC_DIRECT_SEMANTIC_MAP.tsv", DIAGNOSTIC_FIELDS, rows)
    deterministic_gzip(output / "DIAGNOSTIC_DIRECT_SEMANTIC_MAP.tsv", output / "DIAGNOSTIC_DIRECT_SEMANTIC_MAP.tsv.gz")
    reproduction = reproduce_producer_map(rows, local["producer_map"])
    write_tsv(output / "DIAGNOSTIC_SEMANTIC_COVERAGE.tsv", tuple(diagnostic_coverage(rows)[0].keys()), diagnostic_coverage(rows))
    merge, coverage = merge_clean_catalog(event, rows, output)
    write_raw_index(output, [
        ("DIAGNOSTIC_RAW_NSYS_REP", local["raw"], "NA"),
        ("DIAGNOSTIC_REMOTE_SQLITE", local["remote_sqlite"], len(rows)),
        ("DIAGNOSTIC_LOCAL_SQLITE", args.local_sqlite, len(rows)),
        ("DIAGNOSTIC_DIRECT_MAP", output / "DIAGNOSTIC_DIRECT_SEMANTIC_MAP.tsv", len(rows)),
        ("CLEAN_DIRECT_SEMANTIC_MAP", output / "DIRECT_SEMANTIC_MAP.tsv", merge["clean_rows"]),
        ("CLEAN_DIRECT_SEMANTIC_MAP_GZIP", output / "DIRECT_SEMANTIC_MAP.tsv.gz", merge["clean_rows"]),
    ])
    audit = {
        "schema_version": "C16_P_SEMANTIC_MERGE_AUDIT_V1", "status": "PASS_COVERAGE_LIMITED",
        "classification": "REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL", "scientific_eligible": False,
        "producer": producer, "identity": event["identity"],
        "sources": {"producer_manifest_sha256": producer["manifest_sha256"], "diagnostic_raw_profile_sha256": sha256_file(local["raw"]), "diagnostic_semantic_receipt_sha256": sha256_file(Path(event["receipts"]["semantic"]["path"])), "diagnostic_nsys_receipt_sha256": sha256_file(Path(event["receipts"]["nsys"]["path"])), "clean_catalog_sha256": event["clean_catalog"]["catalog"]["sha256"], "clean_profile_index_sha256": event["clean_catalog"]["profile_index"]["sha256"], "join_key_contract_path": str(join_contract), "join_key_contract_sha256": event["join_key_contract"]["sha256"]},
        "local_export_qualification": {"path": "LOCAL_DIAGNOSTIC_EXPORT_QUALIFICATION.json", "sha256": sha256_file(output / "LOCAL_DIAGNOSTIC_EXPORT_QUALIFICATION.json"), "status": qualification["status"]},
        "diagnostic_direct_evidence": {"kernel_rows": len(rows), "direct_runtime_range_count": range_count, "direct_unambiguous_rows": sum(row["mapping_status"] == "DIRECT_UNAMBIGUOUS" for row in rows), "unknown_rows": sum(row["mapping_status"] != "DIRECT_UNAMBIGUOUS" for row in rows), "ambiguous_direct_range_rows": direct_ambiguity, "producer_map_reproduction": reproduction},
        "clean_merge": {**merge, "coverage_limited": any(row["status"] == "COVERAGE_LIMITED" for row in coverage)},
        "join_policy": {"diagnostic_internal_temporal_containment": "ALLOWED_ONLY_FOR_DIRECT_RUNTIME_NVTX", "cross_report_absolute_timestamp_join": "FORBIDDEN", "cross_report_bare_correlation_or_stream_join": "FORBIDDEN", "cross_report_naked_launch_ordinal_join": "FORBIDDEN", "zero_or_multiple_structural_candidates": "UNKNOWN", "kernel_name_semantic_heuristic": "FORBIDDEN"},
    }
    write_json(output / "SEMANTIC_MERGE_AUDIT.json", audit)
    files = []
    for path in sorted(output.iterdir()):
        if path.is_file() and path.name != "SEMANTIC_POSTPROCESS_MANIFEST.json":
            files.append({"name": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    write_json(output / "SEMANTIC_POSTPROCESS_MANIFEST.json", {"schema_version": "C16_P_SEMANTIC_POSTPROCESS_V1", "status": "REAL_NATIVE_SCHEMA_SANITY / PROVISIONAL / COVERAGE_LIMITED", "event_sha256": sha256_file(args.event), "audit_sha256": sha256_file(output / "SEMANTIC_MERGE_AUDIT.json"), "files": files})
    print("PASS C16 P local direct-semantic event: COVERAGE_LIMITED")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 P direct semantic event: {exc}", file=sys.stderr)
        raise SystemExit(2)
