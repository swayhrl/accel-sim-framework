#!/usr/bin/env python3
"""Verify a hash-closed G3 NVBit terminal package without reading trace data.

This is deliberately a Lane-P transport/hash/schema auxiliary only.  It
verifies the immutable G publication objects and records whether a model trace
was actually delivered.  It never opens a raw NVBit trace, decodes an address,
or derives a memory fingerprint; those tasks belong solely to Lane H.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_wave1_native/fixed_target_execution/g3_nvbit"
MANIFEST = f"{ROOT}/PUBLISH_MANIFEST.json"
CAPABILITY = f"{ROOT}/G3_NVBIT_CAPABILITY_LIMITED_RECEIPT.json"
VALIDATION = f"{ROOT}/PUBLISH_VALIDATION_RECEIPT.json"
EXPECTED_MANIFEST_SCHEMA = "C16_G3_NVBIT_CAPABILITY_LIMITED_PUBLISH_V1"
EXPECTED_CAPABILITY_SCHEMA = "C16_G3_NVBIT_CAPABILITY_LIMITED_V1"
EXPECTED_VALIDATION_SCHEMA = "C16_G3_NVBIT_PUBLISH_VALIDATION_V1"


class AuxiliaryError(RuntimeError):
    """The G3 terminal package is incomplete or is not P-safe."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise AuxiliaryError(result.stderr.decode(errors="replace").strip())
    return result.stdout if binary else result.stdout.decode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuxiliaryError(message)


def require_commit(repo: Path, commit: str) -> None:
    git(repo, "cat-file", "-e", f"{commit}^{{commit}}")


def git_object(repo: Path, commit: str, path: str) -> tuple[bytes, str]:
    payload = git(repo, "show", f"{commit}:{path}", binary=True)  # type: ignore[assignment]
    return payload, sha256_bytes(payload)


def git_json(repo: Path, commit: str, path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload, digest = git_object(repo, commit, path)
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise AuxiliaryError(f"invalid JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    blob = str(git(repo, "rev-parse", f"{commit}:{path}")).strip()
    return value, {"path": path, "size_bytes": len(payload), "sha256": digest, "blob_id": blob}


def validate(repo: Path, commit: str) -> dict[str, Any]:
    require_commit(repo, commit)
    manifest, manifest_ref = git_json(repo, commit, MANIFEST)
    capability, capability_ref = git_json(repo, commit, CAPABILITY)
    validation, validation_ref = git_json(repo, commit, VALIDATION)
    require(manifest.get("schema_version") == EXPECTED_MANIFEST_SCHEMA, "unexpected G3 publish-manifest schema")
    require(manifest.get("status") == "G3_CAPABILITY_LIMITED", "G3 publish manifest is not terminal capability-limited")
    require(manifest.get("raw_payloads_committed") is False, "G3 package unexpectedly declares raw trace payloads")
    external = manifest.get("external_raw_index")
    require(isinstance(external, dict) and external.get("remote_only_required_artifact_count") == 0, "G3 package has unresolved remote-only raw artifact")
    require(capability.get("schema_version") == EXPECTED_CAPABILITY_SCHEMA, "unexpected G3 capability receipt schema")
    require(capability.get("status") == "G3_CAPABILITY_LIMITED", "G3 capability receipt is not terminal")
    require(capability.get("scientific_eligible_for_timing") is False, "G3 terminal package claims timing eligibility")
    require(capability.get("scientific_nvbit_target_result_emitted") is False, "G3 package claims an NVBit target result")
    first = capability.get("first_c_target_only")
    require(isinstance(first, dict), "G3 terminal package lacks the attempted-target identity")
    require(first.get("model_raw_trace_files") == 0 and first.get("model_raw_trace_bytes") == 0, "G3 package has a model raw trace; route it through the future trace contract")
    require(first.get("target_identity_status") == "TARGET_IDENTITY_NOT_REPRODUCIBLE", "G3 terminal disposition is not explicit")
    rows = capability.get("row_disposition")
    require(isinstance(rows, dict) and rows.get("no_target_rows_modified") is True and rows.get("no_target_metric_or_capture_substitution") is True, "G3 terminal receipt permits an unauthorized target substitution")
    lane_h = capability.get("lane_h_notification")
    require(isinstance(lane_h, dict) and lane_h.get("real_model_trace_canary_available") is False, "G3 package incorrectly exposes a Lane-H memory input")
    require(validation.get("schema_version") == EXPECTED_VALIDATION_SCHEMA and validation.get("status") == "PASS", "G3 publish validation did not pass")
    checks = validation.get("checks")
    require(isinstance(checks, dict), "G3 validation lacks checks")
    require(checks.get("missing_path_count") == 0 and checks.get("size_or_sha256_failure_count") == 0 and checks.get("external_artifacts_all_dual_endpoint_hash_closed") is True, "G3 publication closure failed")
    files = manifest.get("files")
    require(isinstance(files, list) and len(files) == checks.get("payload_count"), "G3 manifest file count differs from validation")
    file_refs: list[dict[str, Any]] = []
    for entry in files:
        require(isinstance(entry, dict), "invalid G3 manifest file entry")
        relative, expected_size, expected_sha = entry.get("path"), entry.get("size_bytes"), entry.get("sha256")
        require(isinstance(relative, str) and isinstance(expected_size, int) and isinstance(expected_sha, str), "G3 manifest entry lacks path/size/SHA")
        payload, digest = git_object(repo, commit, f"{ROOT}/{relative}")
        require(len(payload) == expected_size and digest == expected_sha, f"G3 manifest payload closure failed: {relative}")
        file_refs.append({"path": f"{ROOT}/{relative}", "size_bytes": len(payload), "sha256": digest, "transport": "GIT_IMMUTABLE_HASH_CLOSED"})
    authority = manifest.get("planning_authority")
    require(isinstance(authority, dict), "G3 manifest lacks frozen planning authority")
    return {
        "schema_version": "C16_P_P3_NVBIT_AUXILIARY_RECEIPT_V1",
        "status": "C16_P_P3_NVBIT_AUXILIARY_CAPABILITY_LIMITED_NO_MODEL_TRACE",
        "created_at_utc": now(),
        "g_producer": {"commit": commit, "publish_manifest": manifest_ref, "capability_receipt": capability_ref, "publish_validation": validation_ref},
        "validated_payloads": file_refs,
        "frozen_target_authority": {
            "c_fixed_commit": authority.get("c_fixed_commit"),
            "selector_freeze_sha256": authority.get("selector_freeze_sha256"),
            "g_target_policy_sha256": authority.get("g_target_policy_sha256"),
            "nvbit_target_plan_sha256": authority.get("nvbit_target_plan_sha256"),
        },
        "transport_hash_schema_validation": {
            "manifest_payload_count": len(file_refs),
            "payload_size_sha256_failures": 0,
            "external_artifacts_all_dual_endpoint_hash_closed": True,
            "remote_only_required_artifact_count": 0,
            "raw_model_trace_transferred_to_p": False,
            "raw_model_trace_files": 0,
            "raw_model_trace_bytes": 0,
            "schema_status": "PASS",
        },
        "terminal_disposition": {
            "terminal_scope": capability.get("terminal_scope"),
            "first_target_status": first.get("terminal_status"),
            "first_target_identity_status": first.get("target_identity_status"),
            "remaining_rows": rows.get("remaining_287_rows"),
            "target_substitution": "FORBIDDEN_AND_NOT_PERFORMED",
        },
        "lane_boundaries": {
            "p_read_trace_payload": False,
            "p_memory_fingerprint": "NOT_PERFORMED_LANE_H_OWNED",
            "lane_h_real_model_trace_canary_available": False,
            "operator_layer_semantic_inference": "NOT_PERFORMED",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--g-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.repo.resolve(), args.g_commit)
        result["p_handler"] = {"path": "util/vm_tlb/c16/lane_p/nvbit_canary_auxiliary.py", "code_sha256": sha256_file(Path(__file__))}
        write_json(args.output.resolve(), result)
        print(json.dumps({"status": result["status"], "output": str(args.output.resolve()), "sha256": sha256_file(args.output.resolve())}, sort_keys=True))
        return 0
    except AuxiliaryError as exc:
        print(f"C16-P NVBit auxiliary validation blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
