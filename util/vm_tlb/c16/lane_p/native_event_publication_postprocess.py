#!/usr/bin/env python3
"""Consume a hash-closed C16-G native-event publication on Lane P.

The input is an immutable Git commit plus its compact publication bundle.  Raw
``.nsys-rep`` files remain outside Git.  This tool verifies every local raw and
receipt hash before it invokes the local Nsight CLI, then retains every CUDA
kernel row in a report-scoped catalog.  It never infers layer or operator
semantics from a kernel name and never joins report-local timestamps, streams,
or correlation IDs across reports.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from local_native_postprocess import (
    CATALOG_FIELDS,
    COVERAGE_FIELDS,
    PROFILE_REPORT_INDEX_FIELDS,
    RAW_INDEX_FIELDS,
    RUN_SUMMARY_FIELDS,
    derive_tables,
    deterministic_gzip,
    export_evidence,
    marker_intervals,
    sha256_file,
    write_json,
    write_tsv,
)


PUBLICATION_SCHEMA = "C16_G_NATIVE_EVENT_PUBLICATION_V1"
PUBLICATION_READY = "C16_G_NATIVE_EVENT_PUBLICATION_READY_FOR_P"
EVENT_SCHEMA = "C16_G_P1_NATIVE_EVENT_V1"
EVENT_TYPE = "P1_CLEAN_NATIVE_NSYS_REPORT"
REQUIRED_IDENTITY = (
    "deployment_id", "model_id", "model_revision", "tokenizer_revision",
    "scenario_id", "input_hash", "run_id", "code_commit", "dtype",
    "implementation_key", "quantization",
)
RUN_SCOPE = (
    "run_id", "device", "context", "stream", "correlation_id", "launch_ordinal",
)
SHAPE_RE = re.compile(r"^B(?P<batch>[0-9]+)_T(?P<prefill>[0-9]+)_D(?P<decode>[0-9]+)$")


class ContractError(RuntimeError):
    """A publication input is not suitable for P postprocess."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json_bytes(value: bytes, label: str) -> dict[str, Any]:
    try:
        result = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ContractError(f"{label} is not JSON") from exc
    if not isinstance(result, dict):
        raise ContractError(f"{label} JSON root is not an object")
    return result


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return read_json_bytes(path.read_bytes(), str(path))
    except OSError as exc:
        raise ContractError(f"cannot read {label}: {exc}") from exc


def require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be nonempty text")
    return value


def require_sha(value: Any, label: str) -> str:
    text = require_text(value, label)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise ContractError(f"{label} must be a lowercase SHA-256")
    return text


def require_commit(value: Any, label: str) -> str:
    text = require_text(value, label)
    if not re.fullmatch(r"[0-9a-f]{40}", text):
        raise ContractError(f"{label} must be a full Git commit")
    return text


def relative_path(value: Any, label: str) -> str:
    text = require_text(value, label)
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts:
        raise ContractError(f"{label} must be a safe publication-relative path")
    return path.as_posix()


def git_bytes(repo: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise ContractError(f"cannot read producer object {commit}:{path}: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def git_commit_exists(repo: Path, commit: str) -> None:
    result = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"], capture_output=True, check=False)
    if result.returncode:
        raise ContractError(f"declared producer commit is absent: {commit}")


def g_ref(repo: Path, commit: str, root: str, relative: str, expected_sha: str, label: str) -> tuple[bytes, dict[str, Any]]:
    relative = relative_path(relative, f"{label}.path")
    payload = git_bytes(repo, commit, f"{root}/{relative}")
    actual = sha256_bytes(payload)
    if actual != require_sha(expected_sha, f"{label}.sha256"):
        raise ContractError(f"{label} Git payload hash mismatch")
    return payload, {"path": relative, "size_bytes": len(payload), "sha256": actual}


def external_ref(value: Any, label: str, *, require_json: bool = True) -> tuple[Path, dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} reference is absent")
    path = Path(require_text(value.get("path"), f"{label}.path"))
    expected_size = value.get("size_bytes")
    if not isinstance(expected_size, int) or isinstance(expected_size, bool) or expected_size < 0:
        raise ContractError(f"{label}.size_bytes is invalid")
    expected_sha = require_sha(value.get("sha256"), f"{label}.sha256")
    if not path.is_file():
        raise ContractError(f"{label} is absent locally: {path}")
    actual_size, actual_sha = path.stat().st_size, sha256_file(path)
    if actual_size != expected_size or actual_sha != expected_sha:
        raise ContractError(f"{label} local size/SHA mismatch")
    return path, (read_json(path, label) if require_json else None), {"path": str(path), "size_bytes": actual_size, "sha256": actual_sha}


def event_identity(event: dict[str, Any], receipt: dict[str, Any], label: str) -> None:
    identity = event.get("identity")
    actual = receipt.get("identity")
    if not isinstance(identity, dict) or not isinstance(actual, dict):
        raise ContractError(f"{label} lacks an identity object")
    for field in REQUIRED_IDENTITY:
        if identity.get(field) != actual.get(field):
            raise ContractError(f"{label} identity differs at {field}")


def check_terminal(receipt: dict[str, Any], label: str) -> None:
    if receipt.get("execution_mode") != "NATIVE_GPU" or receipt.get("scientific_eligible") is not True:
        raise ContractError(f"{label} is not scientific native-GPU evidence")
    if receipt.get("artifacts", {}).get("terminal_status") != "COMPLETE":
        raise ContractError(f"{label} does not record COMPLETE terminal status")


def parse_shape(nsys: dict[str, Any], event_id: str) -> dict[str, str]:
    value = nsys.get("checks", {}).get("target_identity_fields", {}).get("shape_key")
    if not isinstance(value, str):
        raise ContractError(f"{event_id} nsys receipt lacks direct shape_key")
    match = SHAPE_RE.fullmatch(value)
    if match is None:
        raise ContractError(f"{event_id} nsys receipt has unsupported direct shape_key: {value}")
    return {"shape_key": value, **match.groupdict()}


def verify_event(repo: Path, publication_commit: str, root: str, event_path: str, expected_sha: str, binding_sha: str, nsys_version_sha: str) -> dict[str, Any]:
    payload, event_ref = g_ref(repo, publication_commit, root, event_path, expected_sha, "event")
    event = read_json_bytes(payload, event_path)
    event_id = require_text(event.get("event_id"), f"{event_path}.event_id")
    if event.get("schema_version") != EVENT_SCHEMA or event.get("event_type") != EVENT_TYPE:
        raise ContractError(f"{event_id} is not a P1 clean native event")
    if event.get("terminal_status") != "COMPLETE" or event.get("scientific_eligible_for_timing") is not True:
        raise ContractError(f"{event_id} is not terminal scientific P1 evidence")
    producer = event.get("producer")
    if not isinstance(producer, dict):
        raise ContractError(f"{event_id} lacks producer identity")
    if require_text(producer.get("branch"), f"{event_id}.producer.branch") != "hrl/vm-c16-g-autodl-wave1-v0":
        raise ContractError(f"{event_id} producer branch is unexpected")
    producer_commit = require_commit(producer.get("full_g_producer_commit"), f"{event_id}.producer.commit")
    git_commit_exists(repo, producer_commit)
    if producer.get("event_binding_manifest_path") != "EVENT_BINDING_MANIFEST.json" or producer.get("event_binding_manifest_sha256") != binding_sha:
        raise ContractError(f"{event_id} does not bind the frozen event-binding manifest")
    nsys_version = event.get("remote_nsys_version_receipt")
    if not isinstance(nsys_version, dict) or nsys_version.get("path") != "REMOTE_NSYS_VERSION_RECEIPT.json" or nsys_version.get("sha256") != nsys_version_sha:
        raise ContractError(f"{event_id} does not bind the frozen remote-nsys receipt")

    raw = event.get("raw_profile")
    if not isinstance(raw, dict):
        raise ContractError(f"{event_id} lacks raw profile declaration")
    raw_path = Path(require_text(raw.get("local_destination_path"), f"{event_id}.raw.local_path"))
    raw_size = raw.get("local_size_bytes")
    raw_sha = require_sha(raw.get("local_sha256"), f"{event_id}.raw.local_sha256")
    if not isinstance(raw_size, int) or raw_size <= 0 or raw.get("remote_size_bytes") != raw_size or raw.get("remote_sha256") != raw_sha:
        raise ContractError(f"{event_id} remote/local raw declaration differs")
    if not raw_path.is_file() or raw_path.stat().st_size != raw_size or sha256_file(raw_path) != raw_sha:
        raise ContractError(f"{event_id} local raw is not hash closed")

    receipts = event.get("receipts")
    if not isinstance(receipts, dict):
        raise ContractError(f"{event_id} lacks receipt references")
    profile_path, profile, profile_ref = external_ref(receipts.get("profile_runner"), f"{event_id}.profile_runner")
    nsys_path, nsys, nsys_ref = external_ref(receipts.get("nsys_capture"), f"{event_id}.nsys_capture")
    assert profile is not None and nsys is not None
    check_terminal(profile, f"{event_id}.profile_runner")
    check_terminal(nsys, f"{event_id}.nsys_capture")
    event_identity(event, profile, f"{event_id}.profile_runner")
    event_identity(event, nsys, f"{event_id}.nsys_capture")
    capture_artifacts = nsys.get("artifacts", {})
    capture_sha = capture_artifacts.get("output_sha256")
    capture_bytes = capture_artifacts.get("output_bytes")
    if capture_sha == raw_sha and capture_bytes == raw_size:
        capture_raw_binding = "DIRECT_NSYS_RECEIPT_SHA256"
    elif capture_sha == "NA" and capture_bytes == raw_size:
        # Several early Wave-1 captures predate recording output SHA in the
        # capture receipt.  Do not manufacture that binding: accept them only
        # because the signed P1 event and its validation binding name the raw
        # SHA, and the separately hash-closed dual-endpoint transfer proves
        # the local raw bytes below.
        capture_raw_binding = "LEGACY_NSYS_RECEIPT_SHA_NA__EVENT_AND_TRANSFER_HASH_CLOSED"
    else:
        raise ContractError(f"{event_id} nsys receipt raw artifact disagrees with event declaration")

    transfer_ref = raw.get("dual_endpoint_transfer_receipt")
    if not isinstance(transfer_ref, dict):
        raise ContractError(f"{event_id} lacks transfer receipt reference")
    transfer_payload, transfer_git_ref = g_ref(repo, publication_commit, root, transfer_ref.get("path"), transfer_ref.get("sha256"), f"{event_id}.transfer")
    transfer = read_json_bytes(transfer_payload, f"{event_id}.transfer")
    if transfer.get("event_id") != event_id or transfer.get("sha256_match") is not True or transfer.get("no_raw_regeneration") is not True:
        raise ContractError(f"{event_id} transfer closure is incomplete")
    for endpoint in ("local", "remote"):
        candidate = transfer.get(endpoint)
        if not isinstance(candidate, dict) or candidate.get("sha256") != raw_sha or candidate.get("size_bytes") != raw_size:
            raise ContractError(f"{event_id} transfer {endpoint} does not match raw")

    binding_ref = receipts.get("export_validation_binding")
    if not isinstance(binding_ref, dict):
        raise ContractError(f"{event_id} lacks export-validation binding")
    binding_payload, binding_git_ref = g_ref(repo, publication_commit, root, binding_ref.get("path"), binding_ref.get("sha256"), f"{event_id}.validation_binding")
    binding = read_json_bytes(binding_payload, f"{event_id}.validation_binding")
    if binding.get("event_id") != event_id or binding.get("raw_profile", {}).get("sha256") != raw_sha:
        raise ContractError(f"{event_id} validation binding does not bind its raw profile")
    if binding.get("profile_runner_receipt", {}).get("sha256") != profile_ref["sha256"] or binding.get("nsys_capture_receipt", {}).get("sha256") != nsys_ref["sha256"]:
        raise ContractError(f"{event_id} validation binding receipt hashes differ")
    if binding.get("dual_endpoint_transfer_receipt", {}).get("sha256") != transfer_git_ref["sha256"]:
        raise ContractError(f"{event_id} validation binding transfer hash differs")

    validation_info: dict[str, Any] = {"status": binding.get("terminal_status"), "local_file": None, "evidence": None}
    validation_ref = receipts.get("independent_export_validation")
    if validation_ref is not None:
        validation_path, validation, validation_file_ref = external_ref(validation_ref, f"{event_id}.independent_export_validation")
        assert validation is not None
        if validation.get("status") != "G1_EXPORT_VALIDATED_PASS":
            raise ContractError(f"{event_id} independent export validation is not PASS")
        event_identity(event, validation, f"{event_id}.independent_export_validation")
        inputs = validation.get("inputs", {})
        if not isinstance(inputs, dict) or inputs.get("raw_profile_sha256") != raw_sha or inputs.get("runner_receipt_sha256") != profile_ref["sha256"]:
            raise ContractError(f"{event_id} independent export validation input hashes differ")
        if inputs.get("profile_receipt_sha256") not in {profile_ref["sha256"], nsys_ref["sha256"]}:
            raise ContractError(f"{event_id} independent export validation profile receipt differs")
        validation_info = {"status": validation.get("status"), "local_file": validation_file_ref, "evidence": validation.get("evidence")}
    elif binding.get("consumer_requirement") != "P_LOCAL_EXPORT_REQUIRED_BEFORE_FORMAL_POSTPROCESS":
        raise ContractError(f"{event_id} lacks both independent validation and a local-export requirement")

    shape = parse_shape(nsys, event_id)
    return {
        "event_id": event_id,
        "event_git": event_ref,
        "event": event,
        "producer_commit": producer_commit,
        "raw_path": raw_path,
        "raw": {"path": str(raw_path), "size_bytes": raw_size, "sha256": raw_sha},
        "profile": profile,
        "profile_ref": profile_ref,
        "nsys": nsys,
        "nsys_ref": nsys_ref,
        "transfer_ref": transfer_git_ref,
        "binding_ref": binding_git_ref,
        "capture_raw_binding": capture_raw_binding,
        "validation": validation_info,
        "shape": shape,
    }


def validate_publication(repo: Path, commit: str, root: str, expected_manifest_sha: str) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    require_commit(commit, "producer commit")
    git_commit_exists(repo, commit)
    root = relative_path(root, "publication root")
    manifest_payload = git_bytes(repo, commit, f"{root}/PUBLISH_MANIFEST.json")
    manifest_sha = sha256_bytes(manifest_payload)
    if manifest_sha != require_sha(expected_manifest_sha, "expected publication manifest SHA"):
        raise ContractError("publication manifest SHA differs from caller-pinned SHA")
    manifest = read_json_bytes(manifest_payload, "PUBLISH_MANIFEST.json")
    if manifest.get("schema_version") != PUBLICATION_SCHEMA or manifest.get("status") != PUBLICATION_READY:
        raise ContractError("producer publication is not READY_FOR_P")
    refs = manifest.get("files")
    if not isinstance(refs, list) or not refs:
        raise ContractError("publication manifest has no file closure")
    by_path: dict[str, dict[str, Any]] = {}
    for ref in refs:
        if not isinstance(ref, dict):
            raise ContractError("publication file closure contains a non-object")
        path = relative_path(ref.get("path"), "publication file path")
        payload, checked = g_ref(repo, commit, root, path, ref.get("sha256"), f"publication file {path}")
        if checked["size_bytes"] != ref.get("size_bytes"):
            raise ContractError(f"publication file size mismatch: {path}")
        by_path[path] = {**checked, "payload": payload}
    binding_ref = by_path.get("EVENT_BINDING_MANIFEST.json")
    nsys_version_ref = by_path.get("REMOTE_NSYS_VERSION_RECEIPT.json")
    if binding_ref is None or nsys_version_ref is None:
        raise ContractError("publication is missing a required top-level receipt")
    # The validation receipt deliberately sits outside ``files``: adding it to
    # the payload set would make the manifest/validator closure circular.  It
    # is admissible only when its own report binds the exact frozen manifest.
    validation_payload = git_bytes(repo, commit, f"{root}/PUBLISH_VALIDATION_RECEIPT.json")
    validation = read_json_bytes(validation_payload, "PUBLISH_VALIDATION_RECEIPT.json")
    validation_manifest = validation.get("publication_manifest")
    if not isinstance(validation_manifest, dict):
        raise ContractError("publication validation receipt lacks manifest binding")
    if (validation.get("status") != "PASS"
            or validation_manifest.get("path") != "PUBLISH_MANIFEST.json"
            or validation_manifest.get("sha256") != manifest_sha
            or validation_manifest.get("size_bytes") != len(manifest_payload)):
        raise ContractError("producer publication validation did not PASS")
    validation_ref = {
        "path": "PUBLISH_VALIDATION_RECEIPT.json",
        "sha256": sha256_bytes(validation_payload),
        "size_bytes": len(validation_payload),
    }
    nsys_version = read_json_bytes(nsys_version_ref["payload"], "REMOTE_NSYS_VERSION_RECEIPT.json")
    if nsys_version.get("terminal_status") != "COMPLETE" or not isinstance(nsys_version.get("version"), str):
        raise ContractError("remote Nsight version receipt is incomplete")
    event_paths = sorted(path for path in by_path if path.startswith("events/") and path.endswith(".json"))
    if len(event_paths) != 8:
        raise ContractError(f"expected eight clean train events, found {len(event_paths)}")
    events = [verify_event(repo, commit, root, path, by_path[path]["sha256"], binding_ref["sha256"], nsys_version_ref["sha256"]) for path in event_paths]
    deployments = {item["event"]["identity"]["deployment_id"] for item in events}
    if deployments != {"c16_llama32_1b_frozen_compatible", "c16_qwen25_05b_native_reference"}:
        raise ContractError("publication train population is not exactly Llama plus Qwen0.5")
    return manifest, events, {
        "producer_commit": commit,
        "publication_root": root,
        "publication_manifest": {"path": "PUBLISH_MANIFEST.json", "sha256": manifest_sha, "size_bytes": len(manifest_payload)},
        "publication_validation": {key: validation_ref[key] for key in ("path", "sha256", "size_bytes")},
        "event_binding_manifest": {key: binding_ref[key] for key in ("path", "sha256", "size_bytes")},
        "remote_nsys_version": {key: nsys_version_ref[key] for key in ("path", "sha256", "size_bytes")},
        "remote_nsys_version_text": nsys_version.get("version"),
    }


def local_export(item: dict[str, Any], nsys: Path, output: Path) -> dict[str, Any]:
    sqlite = output / "sqlite" / f"{item['event_id']}.sqlite"
    receipt = output / "export_receipts" / f"{item['event_id']}.json"
    sqlite.parent.mkdir(parents=True, exist_ok=True)
    command = ["nice", "-n", "19", "ionice", "-c2", "-n7", str(nsys), "export", "--type", "sqlite", "--force-overwrite", "true", "--quiet", "true", "--output", str(sqlite), str(item["raw_path"])]
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode or not sqlite.is_file():
        raise ContractError(f"{item['event_id']} local nsys export failed: {result.stderr.strip()}")
    evidence = export_evidence(sqlite)
    expected = item["validation"].get("evidence")
    comparison: dict[str, Any] = {"mode": "P_LOCAL_EXPORT_ONLY", "status": "PASS_LOCAL_EXPORT_PARSED"}
    if isinstance(expected, dict):
        expected_counts = {
            "cuda_kernel_count": evidence["kernel_rows"],
            "named_kernel_count": evidence["named_kernel_rows"],
            "distinct_stream_count": evidence["distinct_stream_count"],
            "cuda_runtime_correlation_join_count": evidence["correlated_kernel_rows"],
            "nvtx_kernel_overlap_count": evidence["nvtx_kernel_overlap_rows"],
        }
        mismatches = {key: {"producer": expected.get(key), "local": actual} for key, actual in expected_counts.items() if expected.get(key) != actual}
        nvtx_expected = expected.get("required_nvtx_range_counts")
        if isinstance(nvtx_expected, dict):
            for name, actual in evidence["nvtx_range_counts"].items():
                if nvtx_expected.get(name) != actual:
                    mismatches[f"nvtx:{name}"] = {"producer": nvtx_expected.get(name), "local": actual}
        if mismatches:
            raise ContractError(f"{item['event_id']} local export differs from G validation evidence: {mismatches}")
        comparison = {"mode": "G_VALIDATION_EVIDENCE_VS_LOCAL_EXPORT", "status": "PASS_FIELD_EQUIVALENCE", "producer_evidence": expected}
    version = subprocess.run([str(nsys), "--version"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if version.returncode:
        raise ContractError(f"cannot obtain local nsys version: {version.stderr.strip()}")
    result_data = {
        "schema_version": "C16_P_P1_LOCAL_EXPORT_RECEIPT_V1",
        "status": comparison["status"],
        "event_id": item["event_id"],
        "identity": item["event"]["identity"],
        "raw_profile": item["raw"],
        "sqlite": {"path": str(sqlite), "size_bytes": sqlite.stat().st_size, "sha256": sha256_file(sqlite)},
        "local_nsys": {"path": str(nsys), "version": version.stdout.strip()},
        "command": command,
        "export_evidence": evidence,
        "comparison": comparison,
    }
    write_json(receipt, result_data)
    item["sqlite"] = sqlite
    item["sqlite_ref"] = result_data["sqlite"]
    item["export_receipt"] = receipt
    item["export"] = result_data
    return item


def catalog_rows(item: dict[str, Any]) -> Iterable[dict[str, Any]]:
    identity = item["event"]["identity"]
    connection = sqlite3.connect(item["sqlite"])
    emitted = 0
    try:
        full, phases, steps = marker_intervals(connection)
        expected = connection.execute("SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL").fetchone()[0]
        query = """
            SELECT k.rowid, k.start, k.end, k.deviceId, k.contextId, k.streamId, k.correlationId,
                   k.gridX, k.gridY, k.gridZ, k.blockX, k.blockY, k.blockZ, s.value
            FROM CUPTI_ACTIVITY_KIND_KERNEL k
            LEFT JOIN StringIds s ON s.id = k.demangledName
            ORDER BY k.start, k.rowid
        """
        for ordinal, row in enumerate(connection.execute(query), start=1):
            rowid, start, end, device, context, stream, correlation, gx, gy, gz, bx, by, bz, name = row
            midpoint = (int(start) + int(end)) // 2
            if not any(left <= midpoint <= right for left, right in full):
                raise ContractError(f"{item['event_id']} launch {ordinal} lies outside C16 full-forward NVTX")
            phase, decode_bin = "FULL_FORWARD_UNATTRIBUTED", "NOT_APPLICABLE"
            for left, right, step in steps:
                if left <= midpoint <= right:
                    phase, decode_bin = "DECODE", f"STEP_{step}"
                    break
            else:
                for left, right, candidate in phases:
                    if left <= midpoint <= right:
                        phase, decode_bin = candidate, "NOT_APPLICABLE" if candidate == "PREFILL" else "UNBINNED"
                        break
            emitted += 1
            yield {
                "run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "model_id": identity["model_id"],
                "model_revision": identity["model_revision"], "tokenizer_revision": identity["tokenizer_revision"],
                "scenario_id": identity["scenario_id"], "input_hash": identity["input_hash"], "phase": phase,
                "decode_step_bin": decode_bin, "device": f"cuda:{device}", "context": f"CUDA_CONTEXT_{context}",
                "stream": f"CUDA_STREAM_{stream}", "correlation_id": f"CUDA_CORRELATION_{correlation}", "launch_ordinal": ordinal,
                "kernel_name": name if isinstance(name, str) and name else "[UNRESOLVED_KERNEL_NAME]",
                "implementation_key": identity["implementation_key"], "grid": f"{gx}x{gy}x{gz}", "block": f"{bx}x{by}x{bz}",
                "start_ns": int(start), "end_ns": int(end), "duration_ns": int(end) - int(start),
                "operator_class": "UNKNOWN", "layer_id": "UNKNOWN", "shape_key": item["shape"]["shape_key"],
                "dtype_key": identity["dtype"], "semantic_evidence": "NSYS_NVTX_PHASE_ONLY_NO_DIRECT_OPERATOR_LAYER_EVIDENCE",
                "mapping_status": "UNKNOWN_OPERATOR_LAYER_NO_DIRECT_EVIDENCE", "evidence_tier": "NATIVE_PROFILED",
            }
    finally:
        connection.close()
    if emitted != expected:
        raise ContractError(f"{item['event_id']} catalog dropped launches ({emitted} != {expected})")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_indexes(items: list[dict[str, Any]], output: Path, catalog: Path, status: str) -> None:
    report_rows = []
    raw_rows = []
    for item in items:
        identity, evidence = item["event"]["identity"], item["export"]["export_evidence"]
        report_rows.append({
            "profile_report_id": item["raw"]["sha256"], "run_id": identity["run_id"], "deployment_id": identity["deployment_id"],
            "model_id": identity["model_id"], "model_revision": identity["model_revision"], "tokenizer_revision": identity["tokenizer_revision"],
            "scenario_id": identity["scenario_id"], "input_hash": identity["input_hash"], "raw_report_path": item["raw"]["path"],
            "raw_report_bytes": item["raw"]["size_bytes"], "raw_report_sha256": item["raw"]["sha256"], "sqlite_path": item["sqlite_ref"]["path"],
            "sqlite_bytes": item["sqlite_ref"]["size_bytes"], "sqlite_sha256": item["sqlite_ref"]["sha256"], "kernel_rows": evidence["kernel_rows"],
            "local_nsys_version": item["export"]["local_nsys"]["version"], "validation_receipt_sha256": item["binding_ref"]["sha256"], "status": status,
        })
        for role, ref, rows in (("RAW_NSYS_REP", item["raw"], "NA"), ("NSYS_SQLITE", item["sqlite_ref"], evidence["kernel_rows"])):
            raw_rows.append({"artifact_role": role, "run_id": identity["run_id"], "path": ref["path"], "size_bytes": ref["size_bytes"], "sha256": ref["sha256"], "logical_row_count": rows, "git_policy": "OUTSIDE_GIT", "hash_binding_or_receipt": str(item["export_receipt"]), "retention_status": "LOCAL_HASH_VERIFIED"})
    for path, role in ((catalog, "FULL_LAUNCH_CATALOG"), (output / "KERNEL_CATALOG.tsv.gz", "FULL_LAUNCH_CATALOG_DETERMINISTIC_GZIP")):
        raw_rows.append({"artifact_role": role, "run_id": "MULTI_RUN", "path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path), "logical_row_count": sum(item["export"]["export_evidence"]["kernel_rows"] for item in items), "git_policy": "OUTSIDE_GIT", "hash_binding_or_receipt": str(output / "POSTPROCESS_MANIFEST.json"), "retention_status": "LOCAL_GENERATED_RETAIN"})
    write_tsv(output / "PROFILE_REPORT_INDEX.tsv", PROFILE_REPORT_INDEX_FIELDS, report_rows)
    write_tsv(output / "RAW_ARTIFACT_INDEX.tsv", RAW_INDEX_FIELDS, raw_rows)
    write_tsv(output / "RAW_INDEX.tsv", RAW_INDEX_FIELDS, raw_rows)


def write_join_audit(items: list[dict[str, Any]], output: Path, catalog: Path) -> None:
    rows = read_tsv(catalog)
    required = tuple(CATALOG_FIELDS)
    missing = [field for field in required if field not in (rows[0] if rows else {})]
    empty = sum(any(not row.get(field, "") for field in required) for row in rows)
    keys = [tuple(row[field] for field in RUN_SCOPE) for row in rows]
    by_run: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_run[row["run_id"]].append(row)
    reports = []
    for item in items:
        run_id = item["event"]["identity"]["run_id"]
        members = by_run.get(run_id, [])
        expected = item["export"]["export_evidence"]["kernel_rows"]
        if len(members) != expected:
            raise ContractError(f"{item['event_id']} catalog population differs from local SQLite")
        reports.append({"run_id": run_id, "profile_report_id": item["raw"]["sha256"], "catalog_rows": len(members), "stream_ids": sorted({row["stream"] for row in members}), "correlation_ids": len({row["correlation_id"] for row in members}), "launch_ordinal_min": min(int(row["launch_ordinal"]) for row in members), "launch_ordinal_max": max(int(row["launch_ordinal"]) for row in members)})
    collisions = []
    ids = sorted(by_run)
    for index, left in enumerate(ids):
        for right in ids[index + 1:]:
            collisions.append({"left_run_id": left, "right_run_id": right, "shared_stream_ids": sorted({row["stream"] for row in by_run[left]} & {row["stream"] for row in by_run[right]}), "shared_correlation_id_count": len({row["correlation_id"] for row in by_run[left]} & {row["correlation_id"] for row in by_run[right]}), "conclusion": "REPORT_LOCAL_IDS_MUST_NOT_BE_JOINED_WITHOUT_RUN_OR_REPORT_SCOPE"})
    status = "PASS" if not missing and not empty and len(keys) == len(set(keys)) and set(by_run) == {item["event"]["identity"]["run_id"] for item in items} else "FAIL"
    audit = {"schema_version": "C16_P_P1_PUBLICATION_RUN_JOIN_AUDIT_V1", "status": status, "catalog_required_fields": required, "missing_required_fields": missing, "rows_with_empty_required_key_fields": empty, "physical_launch_scope": RUN_SCOPE, "catalog_rows": len(rows), "duplicate_physical_launch_keys": len(keys) - len(set(keys)), "run_report_index": reports, "cross_report_local_id_collisions": collisions, "cross_report_join_policy": {"absolute_timestamp": "FORBIDDEN", "bare_stream_or_correlation": "FORBIDDEN", "naked_launch_ordinal": "FORBIDDEN"}}
    write_json(output / "RUN_JOIN_AUDIT.json", audit)
    if status != "PASS":
        raise ContractError("run/join audit failed")


def run(args: argparse.Namespace) -> None:
    repo, output, nsys = args.repo.resolve(), args.output_dir.resolve(), args.nsys.resolve()
    if not nsys.is_file():
        raise ContractError(f"local nsys CLI is absent: {nsys}")
    join_contract = args.join_key_contract.resolve()
    if not join_contract.is_file():
        raise ContractError(f"JOIN_KEY_CONTRACT is absent: {join_contract}")
    try:
        join_contract_path = str(join_contract.relative_to(repo))
    except ValueError as exc:
        raise ContractError("JOIN_KEY_CONTRACT must reside in the P worktree") from exc
    manifest, items, closure = validate_publication(repo, args.producer_commit, args.publication_root, args.expected_manifest_sha256)
    output.mkdir(parents=True, exist_ok=True)
    closure["join_key_contract"] = {
        "path": join_contract_path,
        "sha256": sha256_file(join_contract),
        "size_bytes": join_contract.stat().st_size,
    }
    closure["events"] = [{"event_id": item["event_id"], "event_git": item["event_git"], "producer_commit": item["producer_commit"], "identity": item["event"]["identity"], "raw": item["raw"], "profile_runner": item["profile_ref"], "nsys_capture": item["nsys_ref"], "capture_raw_binding": item["capture_raw_binding"], "transfer": item["transfer_ref"], "validation_binding": item["binding_ref"], "independent_export_validation": item["validation"]} for item in items]
    closure["policy"] = {"qwen7_raw": "SKIPPED_RESOURCE / RESOURCE_UNAVAILABLE_ON_RTX3090; no native rows created", "qwen7_awq": "HOLDOUT_PENDING_FREEZE; excluded from this train catalog", "operator_or_layer_without_direct_evidence": "UNKNOWN", "kernel_name_semantic_heuristic": "FORBIDDEN", "cross_run_timestamp_or_bare_local_id_join": "FORBIDDEN"}
    write_json(output / "P1_CLOSURE_AUDIT.json", closure)
    exported = [local_export(item, nsys, output) for item in items]
    catalog = output / "KERNEL_CATALOG.tsv"
    write_tsv(catalog, CATALOG_FIELDS, (row for item in exported for row in catalog_rows(item)))
    deterministic_gzip(catalog, output / "KERNEL_CATALOG.tsv.gz")
    derived = derive_tables(catalog, output, publication_status="C16_G_HASH_CLOSED_P1 / CAPABILITY_LIMITED")
    write_indexes(exported, output, catalog, "C16_G_HASH_CLOSED_P1 / CAPABILITY_LIMITED")
    write_join_audit(exported, output, catalog)
    summaries = []
    for item in exported:
        identity, evidence = item["event"]["identity"], item["export"]["export_evidence"]
        summaries.append({"run_id": identity["run_id"], "deployment_id": identity["deployment_id"], "scenario_id": identity["scenario_id"], "raw_profile_sha256": item["raw"]["sha256"], "sqlite_sha256": item["sqlite_ref"]["sha256"], "kernel_rows": evidence["kernel_rows"], "catalog_rows": evidence["kernel_rows"], "distinct_streams": evidence["distinct_stream_count"], "correlated_kernel_rows": evidence["correlated_kernel_rows"], "nvtx_full_forward_ranges": evidence["nvtx_range_counts"]["C16_NATIVE_FULL_FORWARD"], "nvtx_prefill_ranges": evidence["nvtx_range_counts"]["C16_PHASE_PREFILL"], "nvtx_decode_ranges": evidence["nvtx_range_counts"]["C16_PHASE_DECODE"], "status": "C16_G_HASH_CLOSED_P1 / CAPABILITY_LIMITED"})
    write_tsv(output / "RUN_SUMMARY.tsv", RUN_SUMMARY_FIELDS, summaries)
    files = []
    for path in sorted(output.glob("*.tsv")) + sorted(output.glob("*.tsv.gz")) + sorted(output.glob("*.json")):
        if path.name != "POSTPROCESS_MANIFEST.json":
            files.append({"name": path.name, "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
    post = {"schema_version": "C16_P_P1_PUBLICATION_POSTPROCESS_V1", "status": "C16_P_NATIVE_CATALOG_READY_FOR_C_CONSUMPTION_CAPABILITY_LIMITED", "producer": closure, "population_policy": "Every CUPTI kernel row from every closed P1 report is retained; full catalog and deterministic gzip are outside Git.", "semantic_policy": "operator_class and layer_id are UNKNOWN unless a separate direct-evidence merge proves one unique report-scoped match; kernel-name inference and cross-run local-ID joins are forbidden.", "derived": derived, "files": files}
    write_json(output / "POSTPROCESS_MANIFEST.json", post)
    print(f"PASS C16 P P1 publication postprocess: {sum(item['export']['export_evidence']['kernel_rows'] for item in exported)} launch rows")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--producer-commit", required=True)
    parser.add_argument("--publication-root", required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--nsys", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--join-key-contract", type=Path, required=True)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 P publication postprocess: {exc}", file=sys.stderr)
        raise SystemExit(2)
