#!/usr/bin/env python3
"""Materialize and validate hash-closed C16-G native-profile events for Lane P.

This is deliberately a publication/provenance tool.  It never invokes Nsight,
exports a report, or changes a scientific receipt.  Its input specification names
already-returned reports and receipts; its output contains only compact metadata
and hashes, never a raw profiler payload.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, sha256_file, valid_sha256


SCHEMA = "C16_G_NATIVE_EVENT_PUBLICATION_V1"
MANIFEST_NAME = "PUBLISH_MANIFEST.json"
VALIDATION_NAME = "PUBLISH_VALIDATION_RECEIPT.json"
METADATA_FILES = {MANIFEST_NAME, VALIDATION_NAME}
EVENT_COLUMNS = (
    "event_id", "event_type", "producer_branch", "producer_full_commit",
    "event_binding_manifest_path", "event_binding_manifest_sha256",
    "deployment_id", "model_id", "model_revision", "tokenizer_revision",
    "scenario_id", "input_hash", "profile_run_id", "package_id",
    "package_commit", "package_manifest_sha256", "runtime_source_commit",
    "remote_nsys_rep_logical_path", "remote_nsys_rep_size_bytes",
    "remote_nsys_rep_sha256", "remote_endpoint_state",
    "local_nsys_rep_path", "local_nsys_rep_size_bytes",
    "local_nsys_rep_sha256", "dual_endpoint_transfer_receipt_path",
    "dual_endpoint_transfer_receipt_sha256", "remote_nsys_version_receipt_path",
    "remote_nsys_version_receipt_sha256", "profile_command_config_sha256",
    "export_command_config_sha256", "terminal_status", "profile_receipt_path",
    "profile_receipt_sha256", "nsys_receipt_path", "nsys_receipt_sha256",
    "independent_export_validation_receipt_path",
    "independent_export_validation_receipt_sha256",
    "export_validation_binding_receipt_path",
    "export_validation_binding_receipt_sha256", "export_validation_status",
)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON root must be an object: {path}")
    return value


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def atomic_tsv(path: Path, columns: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def stable_sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def file_ref(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ContractError(f"required source payload is absent: {path}")
    return {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def output_ref(root: Path, path: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}


def ensure_sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or not valid_sha256(value):
        raise ContractError(f"{field} must be a SHA256")
    return value


def ensure_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{field} must be nonempty text")
    return value


def source_path(spec_path: Path, value: Any, field: str) -> Path:
    text = ensure_text(value, field)
    path = Path(text)
    return path if path.is_absolute() else (spec_path.parent / path)


def require_identity(profile: dict[str, Any], nsys: dict[str, Any], event_id: str) -> dict[str, Any]:
    identity = profile.get("identity")
    if not isinstance(identity, dict) or identity != nsys.get("identity"):
        raise ContractError(f"{event_id}: profile and nsys identities differ")
    for field in ("deployment_id", "model_id", "model_revision", "tokenizer_revision", "scenario_id", "input_hash", "run_id", "code_commit"):
        ensure_text(identity.get(field), f"{event_id}.identity.{field}")
    if profile.get("execution_mode") != "NATIVE_GPU" or nsys.get("execution_mode") != "NATIVE_GPU":
        raise ContractError(f"{event_id}: receipts are not native GPU operations")
    if profile.get("scientific_eligible") is not True or nsys.get("scientific_eligible") is not True:
        raise ContractError(f"{event_id}: receipts are not scientific eligible")
    return identity


def raw_spec(event: dict[str, Any], event_id: str) -> dict[str, Any]:
    raw = event.get("raw")
    if not isinstance(raw, dict):
        raise ContractError(f"{event_id}: missing raw specification")
    for field in ("remote_logical_path", "local_path", "remote_endpoint_state"):
        ensure_text(raw.get(field), f"{event_id}.raw.{field}")
    size = raw.get("size_bytes")
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise ContractError(f"{event_id}.raw.size_bytes must be positive")
    ensure_sha(raw.get("sha256"), f"{event_id}.raw.sha256")
    mode = ensure_text(raw.get("remote_recheck_mode"), f"{event_id}.raw.remote_recheck_mode")
    if mode not in {"LIVE_READ_ONLY_RECHECK", "HISTORICAL_CLOSURE_REMOTE_RECLAIMED"}:
        raise ContractError(f"{event_id}: unsupported remote-recheck mode")
    return raw


def validation_source(spec_path: Path, event: dict[str, Any], event_id: str) -> tuple[dict[str, Any] | None, Path | None, str]:
    raw = event.get("independent_export_validation_receipt")
    if raw is None:
        return None, None, "G1_EXPORT_VALIDATION_NOT_MATERIALIZED_BY_G"
    path = source_path(spec_path, raw, f"{event_id}.independent_export_validation_receipt")
    receipt = read_json(path)
    if receipt.get("status") != "G1_EXPORT_VALIDATED_PASS":
        raise ContractError(f"{event_id}: independent export-validation receipt is not PASS")
    return receipt, path, "G1_EXPORT_VALIDATED_PASS"


def source_events(spec_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spec = read_json(spec_path)
    if spec.get("schema_version") != "C16_G_NATIVE_EVENT_PUBLICATION_SOURCES_V1":
        raise ContractError("unsupported native-event source specification")
    producer_branch = ensure_text(spec.get("producer_branch"), "producer_branch")
    publication_source_anchor = ensure_text(spec.get("publication_source_anchor"), "publication_source_anchor")
    events = spec.get("events")
    if not isinstance(events, list) or not events:
        raise ContractError("source specification needs nonempty events")
    seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            raise ContractError("source event is not an object")
        event_id = ensure_text(event.get("event_id"), "event_id")
        if event_id in seen:
            raise ContractError(f"duplicate event_id: {event_id}")
        seen.add(event_id)
        profile_path = source_path(spec_path, event.get("profile_receipt"), f"{event_id}.profile_receipt")
        nsys_path = source_path(spec_path, event.get("nsys_receipt"), f"{event_id}.nsys_receipt")
        profile, nsys = read_json(profile_path), read_json(nsys_path)
        identity = require_identity(profile, nsys, event_id)
        raw = raw_spec(event, event_id)
        local_raw = source_path(spec_path, raw.get("local_path"), f"{event_id}.raw.local_path")
        actual = file_ref(local_raw)
        if actual["size_bytes"] != raw["size_bytes"] or actual["sha256"] != raw["sha256"]:
            raise ContractError(f"{event_id}: local raw does not match specified size/SHA256")
        profile_terminal = profile.get("artifacts", {}).get("terminal_status")
        nsys_terminal = nsys.get("artifacts", {}).get("terminal_status")
        if profile_terminal != "COMPLETE" or nsys_terminal != "COMPLETE":
            raise ContractError(f"{event_id}: profile terminal status is not COMPLETE")
        checks = profile.get("checks")
        if not isinstance(checks, dict):
            raise ContractError(f"{event_id}: profile receipt lacks checks")
        package = {
            "package_id": ensure_text(checks.get("package_id"), f"{event_id}.package_id"),
            "package_commit": ensure_text(checks.get("package_fixed_commit"), f"{event_id}.package_commit"),
            "package_manifest_sha256": ensure_sha(checks.get("package_manifest_sha256"), f"{event_id}.package_manifest_sha256"),
        }
        validation, validation_path, validation_status = validation_source(spec_path, event, event_id)
        if validation is not None and validation.get("identity") != identity:
            raise ContractError(f"{event_id}: independent export-validation identity differs")
        command = nsys.get("checks", {}).get("command")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
            raise ContractError(f"{event_id}: nsys receipt lacks literal profile command")
        checked.append({
            "source": event, "event_id": event_id, "profile_path": profile_path, "nsys_path": nsys_path,
            "profile": profile, "nsys": nsys, "identity": identity, "raw": raw, "local_raw": local_raw,
            "package": package, "validation": validation, "validation_path": validation_path,
            "validation_status": validation_status, "producer_branch": producer_branch,
            "publication_source_anchor": publication_source_anchor,
        })
    return spec, checked


def nsys_version_receipt(spec: dict[str, Any]) -> dict[str, Any]:
    remote = spec.get("remote_nsys_version")
    if not isinstance(remote, dict):
        raise ContractError("source specification lacks remote_nsys_version")
    return {
        "schema_version": "C16_G_REMOTE_NSYS_VERSION_RECEIPT_V1",
        "collection_scope": "PUBLICATION_PROVENANCE_ONLY_NO_GPU_RUN",
        "terminal_status": "COMPLETE",
        "remote_host_label": ensure_text(remote.get("remote_host_label"), "remote_nsys_version.remote_host_label"),
        "nsys_logical_path": ensure_text(remote.get("nsys_logical_path"), "remote_nsys_version.nsys_logical_path"),
        "command": ensure_text(remote.get("command"), "remote_nsys_version.command"),
        "stdout": ensure_text(remote.get("stdout"), "remote_nsys_version.stdout"),
        "version": ensure_text(remote.get("version"), "remote_nsys_version.version"),
        "measurement_active_observation": ensure_text(remote.get("measurement_active_observation"), "remote_nsys_version.measurement_active_observation"),
    }


def source_ref(path: Path) -> dict[str, Any]:
    return file_ref(path)


def profile_config(item: dict[str, Any]) -> dict[str, Any]:
    checks = item["nsys"].get("checks", {})
    return {
        "tool": item["nsys"].get("artifacts", {}).get("tool"),
        "literal_command": checks.get("command"),
        "capture_range": checks.get("nsys_capture_range"),
        "target_identity_fields": checks.get("target_identity_fields"),
        "profiler_mode": item["nsys"].get("runtime", {}).get("profiler_mode"),
    }


def export_config(item: dict[str, Any]) -> dict[str, Any]:
    if item["validation"] is None:
        return {
            "status": "NOT_MATERIALIZED_BY_G",
            "literal_export_command": "NOT_RECORDED_OR_RUN_BY_THIS_PUBLICATION_CLOSEOUT",
            "consumer_action": "P_LOCAL_EXPORT_REQUIRED_BEFORE_FORMAL_POSTPROCESS",
        }
    receipt = item["validation"]
    return {
        "status": "G1_EXPORT_VALIDATED_PASS",
        "literal_export_command": "NOT_RECORDED_IN_LEGACY_VALIDATION_RECEIPT",
        "validation_schema_version": receipt.get("schema_version"),
        "validation_stage_id": receipt.get("stage_id"),
        "validation_inputs": receipt.get("inputs"),
        "validation_evidence": receipt.get("evidence"),
    }


def transfer_receipt(item: dict[str, Any]) -> dict[str, Any]:
    raw = item["raw"]
    live = raw["remote_recheck_mode"] == "LIVE_READ_ONLY_RECHECK"
    if live:
        status = "DUAL_ENDPOINT_SHA_MATCHED_AT_PUBLICATION_CLOSEOUT"
        remote_note = "Remote path was re-read only for size/SHA; no profiler or export command was run."
    else:
        status = "HISTORICAL_DUAL_ENDPOINT_CLOSURE_RECORDED_REMOTE_RECLAIMED"
        remote_note = "Remote raw had already been reclaimed after prior local SHA closure; no regeneration or remote re-hash is possible or attempted."
    return {
        "schema_version": "C16_G_DUAL_ENDPOINT_TRANSFER_RECEIPT_V1",
        "event_id": item["event_id"],
        "status": status,
        "scope": "PUBLICATION_PROVENANCE_ONLY",
        "remote": {
            "logical_path": raw["remote_logical_path"], "size_bytes": raw["size_bytes"], "sha256": raw["sha256"],
            "endpoint_state": raw["remote_endpoint_state"], "recheck_mode": raw["remote_recheck_mode"],
            "recheck_evidence": raw.get("remote_recheck_evidence", remote_note),
        },
        "local": file_ref(item["local_raw"]),
        "sha256_match": True,
        "source_closure_evidence": raw.get("historical_closure_evidence", "CURRENT_CLOSEOUT_READ_ONLY_RECHECK"),
        "no_raw_regeneration": True,
    }


def validation_binding(item: dict[str, Any], transfer_rel: str, transfer_sha: str) -> dict[str, Any]:
    validation = item["validation"]
    independent = source_ref(item["validation_path"]) if item["validation_path"] is not None else None
    return {
        "schema_version": "C16_G_G1_EXPORT_VALIDATION_BINDING_V1",
        "event_id": item["event_id"],
        "terminal_status": item["validation_status"],
        "scientific_claim": "NO_NEW_TIMING_OR_EXPORT_CLAIM_IN_PUBLICATION_CLOSEOUT",
        "profile_runner_receipt": source_ref(item["profile_path"]),
        "nsys_capture_receipt": source_ref(item["nsys_path"]),
        "raw_profile": file_ref(item["local_raw"]),
        "dual_endpoint_transfer_receipt": {"path": transfer_rel, "sha256": transfer_sha},
        "independent_export_validation_receipt": independent,
        "export_config": export_config(item),
        "consumer_requirement": (
            "P_LOCAL_EXPORT_REQUIRED_BEFORE_FORMAL_POSTPROCESS" if validation is None
            else "INDEPENDENT_G_EXPORT_VALIDATION_ALREADY_BOUND"
        ),
    }


def event_document(item: dict[str, Any], *, binding_rel: str, binding_sha: str, version_rel: str, version_sha: str,
                   transfer_rel: str, transfer_sha: str, validation_rel: str, validation_sha: str) -> dict[str, Any]:
    identity, package, raw = item["identity"], item["package"], item["raw"]
    independent = source_ref(item["validation_path"]) if item["validation_path"] is not None else None
    return {
        "schema_version": "C16_G_P1_NATIVE_EVENT_V1",
        "event_type": "P1_CLEAN_NATIVE_NSYS_REPORT",
        "event_id": item["event_id"],
        "producer": {
            "branch": item["producer_branch"],
            "full_g_producer_commit": identity["code_commit"],
            "publication_materializer_source_anchor": item["publication_source_anchor"],
            "event_binding_manifest_path": binding_rel,
            "event_binding_manifest_sha256": binding_sha,
        },
        "identity": {
            **identity,
            **package,
            "runtime_source_commit": identity["code_commit"],
        },
        "raw_profile": {
            "remote_logical_path": raw["remote_logical_path"], "remote_size_bytes": raw["size_bytes"],
            "remote_sha256": raw["sha256"], "remote_endpoint_state": raw["remote_endpoint_state"],
            "local_destination_path": str(item["local_raw"]), "local_size_bytes": item["local_raw"].stat().st_size,
            "local_sha256": sha256_file(item["local_raw"]),
            "dual_endpoint_transfer_receipt": {"path": transfer_rel, "sha256": transfer_sha},
        },
        "remote_nsys_version_receipt": {"path": version_rel, "sha256": version_sha},
        "profile_config": profile_config(item),
        "profile_command_config_sha256": stable_sha(profile_config(item)),
        "export_config": export_config(item),
        "export_command_config_sha256": stable_sha(export_config(item)),
        "terminal_status": item["nsys"].get("artifacts", {}).get("terminal_status"),
        "receipts": {
            "profile_runner": source_ref(item["profile_path"]),
            "nsys_capture": source_ref(item["nsys_path"]),
            "independent_export_validation": independent,
            "export_validation_binding": {"path": validation_rel, "sha256": validation_sha},
        },
        "scientific_eligible_for_timing": True,
        "publication_scope": "PROVENANCE_ONLY_NO_RAW_REGENERATION_NO_NEW_GPU_RUN",
    }


def binding_manifest(spec_path: Path, spec: dict[str, Any], items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_NATIVE_EVENT_BINDING_MANIFEST_V1",
        "publication_scope": "PROVENANCE_ONLY",
        "source_spec": source_ref(spec_path),
        "producer_branch": ensure_text(spec.get("producer_branch"), "producer_branch"),
        "publication_source_anchor": ensure_text(spec.get("publication_source_anchor"), "publication_source_anchor"),
        "events": [{
            "event_id": item["event_id"], "identity": item["identity"], "package": item["package"],
            "profile_runner_receipt": source_ref(item["profile_path"]),
            "nsys_capture_receipt": source_ref(item["nsys_path"]),
            "local_raw_profile": file_ref(item["local_raw"]),
            "remote_logical_path": item["raw"]["remote_logical_path"],
            "remote_raw_size_bytes": item["raw"]["size_bytes"], "remote_raw_sha256": item["raw"]["sha256"],
            "independent_export_validation_receipt": (
                source_ref(item["validation_path"]) if item["validation_path"] is not None else None
            ),
            "export_validation_status": item["validation_status"],
        } for item in items],
    }


def payload_entries(root: Path) -> list[dict[str, Any]]:
    files = [path for path in sorted(root.rglob("*")) if path.is_file() and path.name not in METADATA_FILES]
    return [output_ref(root, path) for path in files]


def write_publication(spec_path: Path, root: Path) -> None:
    spec, items = source_events(spec_path)
    root.mkdir(parents=True, exist_ok=True)
    for stale in (root / MANIFEST_NAME, root / VALIDATION_NAME):
        if stale.exists():
            stale.unlink()
    atomic_bytes(root / "EVENT_SOURCES.json", spec_path.read_bytes())
    version_path = root / "REMOTE_NSYS_VERSION_RECEIPT.json"
    atomic_json(version_path, nsys_version_receipt(spec))
    binding_path = root / "EVENT_BINDING_MANIFEST.json"
    atomic_json(binding_path, binding_manifest(spec_path, spec, items))
    binding_sha, version_sha = sha256_file(binding_path), sha256_file(version_path)
    event_rows: list[dict[str, str]] = []
    for item in items:
        transfer_path = root / "transfer_receipts" / f"{item['event_id']}.json"
        atomic_json(transfer_path, transfer_receipt(item))
        transfer_sha = sha256_file(transfer_path)
        validation_path = root / "validation_bindings" / f"{item['event_id']}.json"
        atomic_json(validation_path, validation_binding(item, transfer_path.relative_to(root).as_posix(), transfer_sha))
        validation_sha = sha256_file(validation_path)
        event_path = root / "events" / f"{item['event_id']}.json"
        atomic_json(event_path, event_document(
            item, binding_rel=binding_path.relative_to(root).as_posix(), binding_sha=binding_sha,
            version_rel=version_path.relative_to(root).as_posix(), version_sha=version_sha,
            transfer_rel=transfer_path.relative_to(root).as_posix(), transfer_sha=transfer_sha,
            validation_rel=validation_path.relative_to(root).as_posix(), validation_sha=validation_sha,
        ))
        identity, package, raw = item["identity"], item["package"], item["raw"]
        independent = source_ref(item["validation_path"]) if item["validation_path"] is not None else None
        event_rows.append({
            "event_id": item["event_id"], "event_type": "P1_CLEAN_NATIVE_NSYS_REPORT",
            "producer_branch": ensure_text(spec.get("producer_branch"), "producer_branch"),
            "producer_full_commit": identity["code_commit"],
            "event_binding_manifest_path": binding_path.relative_to(root).as_posix(),
            "event_binding_manifest_sha256": binding_sha,
            "deployment_id": identity["deployment_id"], "model_id": identity["model_id"],
            "model_revision": identity["model_revision"], "tokenizer_revision": identity["tokenizer_revision"],
            "scenario_id": identity["scenario_id"], "input_hash": identity["input_hash"],
            "profile_run_id": identity["run_id"], "package_id": package["package_id"],
            "package_commit": package["package_commit"], "package_manifest_sha256": package["package_manifest_sha256"],
            "runtime_source_commit": identity["code_commit"], "remote_nsys_rep_logical_path": raw["remote_logical_path"],
            "remote_nsys_rep_size_bytes": str(raw["size_bytes"]), "remote_nsys_rep_sha256": raw["sha256"],
            "remote_endpoint_state": raw["remote_endpoint_state"], "local_nsys_rep_path": str(item["local_raw"]),
            "local_nsys_rep_size_bytes": str(item["local_raw"].stat().st_size),
            "local_nsys_rep_sha256": sha256_file(item["local_raw"]),
            "dual_endpoint_transfer_receipt_path": transfer_path.relative_to(root).as_posix(),
            "dual_endpoint_transfer_receipt_sha256": transfer_sha,
            "remote_nsys_version_receipt_path": version_path.relative_to(root).as_posix(),
            "remote_nsys_version_receipt_sha256": version_sha,
            "profile_command_config_sha256": stable_sha(profile_config(item)),
            "export_command_config_sha256": stable_sha(export_config(item)),
            "terminal_status": ensure_text(item["nsys"].get("artifacts", {}).get("terminal_status"), f"{item['event_id']}.terminal_status"),
            "profile_receipt_path": str(item["profile_path"]), "profile_receipt_sha256": sha256_file(item["profile_path"]),
            "nsys_receipt_path": str(item["nsys_path"]), "nsys_receipt_sha256": sha256_file(item["nsys_path"]),
            "independent_export_validation_receipt_path": "" if independent is None else independent["path"],
            "independent_export_validation_receipt_sha256": "" if independent is None else independent["sha256"],
            "export_validation_binding_receipt_path": validation_path.relative_to(root).as_posix(),
            "export_validation_binding_receipt_sha256": validation_sha,
            "export_validation_status": item["validation_status"],
        })
    atomic_tsv(root / "C16_G_NATIVE_EVENT_MANIFEST.tsv", EVENT_COLUMNS, event_rows)
    manifest_path = root / MANIFEST_NAME
    atomic_json(manifest_path, {
        "schema_version": SCHEMA,
        "status": "C16_G_NATIVE_EVENT_PUBLICATION_READY_FOR_P",
        "publication_scope": "PROVENANCE_ONLY_NO_GPU_RUN_NO_RAW_REGENERATION",
        "producer_branch": ensure_text(spec.get("producer_branch"), "producer_branch"),
        "publication_source_anchor": ensure_text(spec.get("publication_source_anchor"), "publication_source_anchor"),
        "raw_profiler_payloads_committed": False,
        "events": [item["event_id"] for item in items],
        "files": payload_entries(root),
    })
    entries = validate_publication(root, spec_path)
    validation_path = root / VALIDATION_NAME
    atomic_json(validation_path, {
        "schema_version": "C16_G_NATIVE_EVENT_PUBLICATION_VALIDATION_V1",
        "status": "PASS",
        "publication_manifest": output_ref(root, manifest_path),
        "payload_count": len(entries),
        "payload_scan": entries,
        "metadata_files_excluded_from_payload_set": sorted(METADATA_FILES),
        "validation_scope": "EXISTENCE_SIZE_SHA256_DUPLICATE_AND_MATERIALIZATION",
    })


def validate_publication(root: Path, spec_path: Path | None = None) -> list[dict[str, Any]]:
    manifest_path = root / MANIFEST_NAME
    manifest = read_json(manifest_path)
    if manifest.get("schema_version") != SCHEMA or manifest.get("raw_profiler_payloads_committed") is not False:
        raise ContractError("invalid native-event publication manifest header")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise ContractError("publication manifest has no payload files")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ContractError("publication manifest contains malformed file entry")
        rel, digest, size = entry.get("path"), entry.get("sha256"), entry.get("size_bytes")
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts or rel in seen:
            raise ContractError("publication manifest has unsafe or duplicate payload path")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0 or not valid_sha256(digest):
            raise ContractError("publication manifest has malformed payload metadata")
        seen.add(rel)
        path = root / rel
        if not path.is_file():
            raise ContractError(f"manifest references unmaterialized payload: {rel}")
        if path.stat().st_size != size or sha256_file(path) != digest:
            raise ContractError(f"manifest payload size/SHA mismatch: {rel}")
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file() and path.name not in METADATA_FILES}
    if actual != seen:
        raise ContractError(f"manifest payload set mismatch: unlisted={sorted(actual - seen)} stale={sorted(seen - actual)}")
    event_table = root / "C16_G_NATIVE_EVENT_MANIFEST.tsv"
    if not event_table.is_file():
        raise ContractError("event table is absent")
    with event_table.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if not rows or tuple(rows[0].keys()) != EVENT_COLUMNS:
        raise ContractError("event table has the wrong columns")
    ids = [row.get("event_id") for row in rows]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise ContractError("event table has duplicate or empty event IDs")
    for row in rows:
        for field in EVENT_COLUMNS:
            if field in {"independent_export_validation_receipt_path", "independent_export_validation_receipt_sha256"}:
                continue
            if not row.get(field):
                raise ContractError(f"event {row.get('event_id')} lacks required field {field}")
        for field in ("event_binding_manifest_sha256", "package_manifest_sha256", "remote_nsys_rep_sha256", "local_nsys_rep_sha256", "dual_endpoint_transfer_receipt_sha256", "remote_nsys_version_receipt_sha256", "profile_command_config_sha256", "export_command_config_sha256", "profile_receipt_sha256", "nsys_receipt_sha256", "export_validation_binding_receipt_sha256"):
            ensure_sha(row[field], f"event {row['event_id']}.{field}")
        for rel in (row["dual_endpoint_transfer_receipt_path"], row["remote_nsys_version_receipt_path"], row["export_validation_binding_receipt_path"]):
            if not (root / rel).is_file():
                raise ContractError(f"event {row['event_id']} references missing publication receipt {rel}")
        if row["independent_export_validation_receipt_path"]:
            ensure_sha(row["independent_export_validation_receipt_sha256"], f"event {row['event_id']}.independent_export_validation")
        event_document = root / "events" / f"{row['event_id']}.json"
        document = read_json(event_document)
        producer, identity, raw = document.get("producer"), document.get("identity"), document.get("raw_profile")
        if not isinstance(producer, dict) or not isinstance(identity, dict) or not isinstance(raw, dict):
            raise ContractError(f"event {row['event_id']} has malformed event document")
        if producer.get("branch") != row["producer_branch"] or producer.get("full_g_producer_commit") != row["producer_full_commit"]:
            raise ContractError(f"event {row['event_id']} producer document/table mismatch")
        if producer.get("event_binding_manifest_sha256") != row["event_binding_manifest_sha256"]:
            raise ContractError(f"event {row['event_id']} binding-manifest SHA mismatch")
        if identity.get("run_id") != row["profile_run_id"] or identity.get("package_manifest_sha256") != row["package_manifest_sha256"]:
            raise ContractError(f"event {row['event_id']} identity document/table mismatch")
        if raw.get("local_sha256") != row["local_nsys_rep_sha256"] or raw.get("remote_sha256") != row["remote_nsys_rep_sha256"]:
            raise ContractError(f"event {row['event_id']} raw SHA document/table mismatch")
    if spec_path is not None:
        source_events(spec_path)
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-spec", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_publication(args.source_spec, args.output_dir)
        print(f"PASS C16 native-event publication write: {args.output_dir}")
    else:
        entries = validate_publication(args.output_dir, args.source_spec)
        print(f"PASS C16 native-event publication validation: {len(entries)} payloads")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 native-event publication: {exc}", file=sys.stderr)
        raise SystemExit(2)
