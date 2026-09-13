#!/usr/bin/env python3
"""Record only the transport/hash/schema closure of G's NVBit compatibility run.

This verifier intentionally does not open the compact diagnostic logs named in
the artifact index.  In particular, it never derives an NVBit, memory, timing,
or target outcome: it only proves that the immutable publication metadata is
closed and records whether a raw model trace was delivered to Lane P.
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


ROOT = "docs/vm_tlb/review_packs/C16_MULTIMODEL_NATIVE/lane_g_wave1_native/nvbit_compatibility_diagnostic"
MANIFEST = f"{ROOT}/PUBLISH_MANIFEST.json"
VALIDATION = f"{ROOT}/PUBLISH_VALIDATION_RECEIPT.json"
ENVIRONMENT = f"{ROOT}/NVBIT_COMPATIBILITY_ENVIRONMENT_RECEIPT.json"
TRANSFER = f"{ROOT}/NVBIT_COMPATIBILITY_TRANSFER_RECEIPT.json"


class AuxiliaryError(RuntimeError):
    """The compatibility publication cannot be consumed safely."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuxiliaryError(message)


def git(repo: Path, *args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise AuxiliaryError(result.stderr.decode(errors="replace").strip())
    return result.stdout if binary else result.stdout.decode("utf-8")


def object_json(repo: Path, commit: str, path: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = git(repo, "show", f"{commit}:{path}", binary=True)
    assert isinstance(payload, bytes)
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise AuxiliaryError(f"invalid JSON: {path}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value, {
        "path": path,
        "size_bytes": len(payload),
        "sha256": sha256_bytes(payload),
        "blob_id": str(git(repo, "rev-parse", f"{commit}:{path}")).strip(),
    }


def object_bytes(repo: Path, commit: str, path: str) -> bytes:
    payload = git(repo, "show", f"{commit}:{path}", binary=True)
    assert isinstance(payload, bytes)
    return payload


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
        handle.write(payload)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def validate(repo: Path, commit: str) -> dict[str, Any]:
    git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    manifest, manifest_ref = object_json(repo, commit, MANIFEST)
    validation, validation_ref = object_json(repo, commit, VALIDATION)
    environment, environment_ref = object_json(repo, commit, ENVIRONMENT)
    transfer, transfer_ref = object_json(repo, commit, TRANSFER)

    require(manifest.get("schema_version") == "C16_G_NVBIT_COMPATIBILITY_DIAGNOSTIC_PUBLISH_V1", "unexpected compatibility manifest schema")
    require(manifest.get("status") == "NVBIT_COMPATIBILITY_DIAGNOSTIC_COMPLETE", "compatibility publication is not complete")
    require(manifest.get("diagnostic_only") is True and manifest.get("scientific_eligible") is False, "compatibility package is not diagnostic-only")
    require(manifest.get("raw_payloads_committed") is False and manifest.get("remote_only_required_artifact_count") == 0, "unexpected raw/remote-only payload declaration")

    require(validation.get("schema_version") == "C16_G_NVBIT_COMPATIBILITY_PUBLISH_VALIDATION_V1", "unexpected validation schema")
    require(validation.get("status") == "PASS", "publication validation is not PASS")
    checks = validation.get("checks")
    require(isinstance(checks, dict), "validation lacks checks")
    require(checks.get("missing_path_count") == 0 and checks.get("size_or_sha256_failure_count") == 0, "publication payload closure failed")
    require(checks.get("external_artifacts_all_dual_endpoint_hash_closed") is True, "external artifact transfer is not closed")
    require(checks.get("raw_trace_file_count") == 0 and checks.get("remote_only_required_artifact_count") == 0, "compatibility package includes a raw trace or remote-only input")

    require(environment.get("schema_version") == "C16_G_NVBIT_COMPATIBILITY_ENVIRONMENT_V1", "unexpected environment schema")
    require(environment.get("diagnostic_status") == "NVBIT_COMPATIBILITY_DIAGNOSTIC_ONLY" and environment.get("scientific_eligible") is False, "environment receipt is not diagnostic-only")
    require(transfer.get("schema_version") == "C16_G_NVBIT_COMPATIBILITY_TRANSFER_V1", "unexpected transfer schema")
    require(transfer.get("status") == "PASS_DUAL_ENDPOINT_HASH_CLOSURE", "transfer receipt is not closed")
    require(transfer.get("diagnostic_only") is True and transfer.get("scientific_eligible") is False, "transfer receipt is not diagnostic-only")
    require(transfer.get("raw_trace_file_count") == 0 and transfer.get("remote_only_required_artifact_count") == 0, "transfer receipt includes a raw trace or remote-only input")
    remote, local = transfer.get("remote"), transfer.get("local")
    require(isinstance(remote, dict) and isinstance(local, dict), "transfer receipt lacks endpoints")
    require(remote.get("file_count") == local.get("file_count") and remote.get("total_bytes") == local.get("total_bytes") and remote.get("bundle_sha256") == local.get("bundle_sha256"), "remote/local transfer closure differs")

    files = manifest.get("files")
    require(isinstance(files, list) and len(files) == checks.get("payload_count"), "manifest payload count differs from validation")
    payloads: list[dict[str, Any]] = []
    for entry in files:
        require(isinstance(entry, dict), "invalid manifest file entry")
        name, expected_size, expected_sha = entry.get("path"), entry.get("size_bytes"), entry.get("sha256")
        require(isinstance(name, str) and isinstance(expected_size, int) and isinstance(expected_sha, str), "manifest entry lacks path/size/SHA")
        payload = object_bytes(repo, commit, f"{ROOT}/{name}")
        digest = sha256_bytes(payload)
        require(len(payload) == expected_size and digest == expected_sha, f"payload closure failed: {name}")
        payloads.append({"path": f"{ROOT}/{name}", "size_bytes": len(payload), "sha256": digest, "transport": "GIT_IMMUTABLE_HASH_CLOSED"})

    return {
        "schema_version": "C16_P_P3_NVBIT_COMPATIBILITY_AUXILIARY_RECEIPT_V1",
        "status": "C16_P_P3_NVBIT_COMPATIBILITY_AUXILIARY_NO_MODEL_TRACE",
        "created_at_utc": now(),
        "g_producer": {
            "commit": commit,
            "publish_manifest": manifest_ref,
            "publish_validation": validation_ref,
            "environment_receipt": environment_ref,
            "transfer_receipt": transfer_ref,
            "diagnostic_source_commit": manifest.get("producer_implementation", {}).get("diagnostic_source_commit") if isinstance(manifest.get("producer_implementation"), dict) else None,
        },
        "validated_payloads": payloads,
        "transport_hash_schema_validation": {
            "manifest_payload_count": len(payloads),
            "payload_size_sha256_failures": 0,
            "external_artifacts_all_dual_endpoint_hash_closed": True,
            "remote_only_required_artifact_count": 0,
            "remote_bundle_sha256": remote.get("bundle_sha256"),
            "local_bundle_sha256": local.get("bundle_sha256"),
            "raw_model_trace_transferred_to_p": False,
            "raw_model_trace_files": 0,
            "raw_model_trace_bytes": 0,
            "schema_status": "PASS",
        },
        "diagnostic_boundary": {
            "diagnostic_only": True,
            "scientific_eligible": False,
            "scientific_status_unchanged": manifest.get("formal_scientific_status_unchanged"),
            "c_fixed_target_authority": manifest.get("c_fixed_target_authority"),
            "no_model_target_result_inferred": True,
        },
        "lane_boundaries": {
            "p_read_compact_diagnostic_logs": False,
            "p_read_trace_payload": False,
            "p_memory_fingerprint": "NOT_PERFORMED_LANE_H_OWNED",
            "operator_layer_semantic_inference": "NOT_PERFORMED",
            "candidate_ncu_nvbit_outcomes_read": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--g-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = validate(args.repo.resolve(), args.g_commit)
        receipt["p_handler"] = {"path": "util/vm_tlb/c16/lane_p/nvbit_compatibility_auxiliary.py", "code_sha256": sha256_file(Path(__file__))}
        write_json(args.output.resolve(), receipt)
        print(json.dumps({"status": receipt["status"], "output": str(args.output.resolve()), "sha256": sha256_file(args.output.resolve())}, sort_keys=True))
        return 0
    except AuxiliaryError as exc:
        print(f"C16-P NVBit compatibility auxiliary validation blocked: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
