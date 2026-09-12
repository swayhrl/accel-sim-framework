#!/usr/bin/env python3
"""Validate the minimum evidence needed to release a real C16 G1 nsys pass."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON receipt {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON receipt is not an object: {path}")
    return value


def scalar(connection: sqlite3.Connection, query: str) -> int:
    value = connection.execute(query).fetchone()
    if value is None or not isinstance(value[0], int):
        raise ContractError("Nsight SQLite query did not return an integer count")
    return value[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sqlite", type=Path, required=True)
    parser.add_argument("--raw-profile", type=Path, required=True)
    parser.add_argument("--profile-receipt", type=Path, required=True)
    parser.add_argument("--runner-receipt", type=Path, required=True)
    parser.add_argument("--binding-receipt", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    profile = read_json(args.profile_receipt)
    runner = read_json(args.runner_receipt)
    binding = read_json(args.binding_receipt)
    if profile.get("execution_mode") != "NATIVE_GPU" or profile.get("scientific_eligible") is not True:
        raise ContractError("G1 profile receipt is not a native scientific operation")
    if profile.get("artifacts", {}).get("terminal_status") not in {"COMPLETE", "BOUNDED_PARTIAL"}:
        raise ContractError("G1 profile receipt lacks an accepted terminal state")
    if runner.get("execution_mode") != "NATIVE_GPU" or runner.get("scientific_eligible") is not True:
        raise ContractError("G1 child runner did not record native execution")
    if profile.get("identity") != runner.get("identity"):
        raise ContractError("G1 profile and child runner identities differ")
    checks = runner.get("checks", {})
    if checks.get("execution_budget_ownership") != "PROFILER_WRAPPER":
        raise ContractError("G1 child did not attest profiler-wrapper budget ownership")
    parent_path = checks.get("parent_lease_receipt")
    if not isinstance(parent_path, str) or not parent_path or parent_path == "NA":
        raise ContractError("G1 child lacks the immutable parent lease receipt reference")
    if binding.get("package_id") != checks.get("package_id") or binding.get("package_fixed_commit") != checks.get("package_fixed_commit"):
        raise ContractError("G1 runner/package binding identity differs")
    if binding.get("package_manifest_sha256") != checks.get("package_manifest_sha256"):
        raise ContractError("G1 package manifest hash differs from frozen binding")
    if not args.sqlite.is_file() or not args.raw_profile.is_file():
        raise ContractError("G1 export or raw profile is absent")

    try:
        connection = sqlite3.connect(args.sqlite)
        kernel_count = scalar(connection, "SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL")
        stream_count = scalar(connection, "SELECT COUNT(DISTINCT streamId) FROM CUPTI_ACTIVITY_KIND_KERNEL")
        named_kernel_count = scalar(connection, """
            SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k
            JOIN StringIds s ON s.id = k.demangledName
            WHERE s.value IS NOT NULL AND s.value != ''
        """)
        correlated_kernel_count = scalar(connection, """
            SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k
            JOIN CUPTI_ACTIVITY_KIND_RUNTIME r ON r.correlationId = k.correlationId
            WHERE k.correlationId IS NOT NULL
        """)
        nvtx_overlap_count = scalar(connection, """
            SELECT COUNT(*) FROM CUPTI_ACTIVITY_KIND_KERNEL k
            JOIN NVTX_EVENTS n ON ((k.start + k.end) / 2) BETWEEN n.start AND n.end
            WHERE n.text IN ('C16_NATIVE_FULL_FORWARD', 'C16_PHASE_PREFILL', 'C16_PHASE_DECODE')
        """)
        required_nvtx = {
            name: scalar(connection, "SELECT COUNT(*) FROM NVTX_EVENTS WHERE text = " + repr(name))
            for name in ("C16_NATIVE_FULL_FORWARD", "C16_PHASE_PREFILL", "C16_PHASE_DECODE")
        }
    except sqlite3.Error as exc:
        raise ContractError(f"cannot validate Nsight SQLite export: {exc}") from exc
    finally:
        try:
            connection.close()
        except UnboundLocalError:
            pass
    if kernel_count <= 0 or stream_count <= 0 or named_kernel_count <= 0 or correlated_kernel_count <= 0 or nvtx_overlap_count <= 0:
        raise ContractError("G1 export lacks kernel/stream/name/correlation/NVTX linkage")
    if any(value <= 0 for value in required_nvtx.values()):
        raise ContractError("G1 export lacks one or more required C16 NVTX phase ranges")
    receipt = {
        "schema_version": "C16_G_G1_EXPORT_VALIDATION_V1",
        "stage_id": "C16-1.4",
        "status": "G1_EXPORT_VALIDATED_PASS",
        "scientific_eligible": True,
        "identity": profile["identity"],
        "runtime": profile["runtime"],
        "inputs": {
            "raw_profile_path": str(args.raw_profile),
            "raw_profile_sha256": sha256_file(args.raw_profile),
            "sqlite_path": str(args.sqlite),
            "sqlite_sha256": sha256_file(args.sqlite),
            "profile_receipt_sha256": sha256_file(args.profile_receipt),
            "runner_receipt_sha256": sha256_file(args.runner_receipt),
            "binding_receipt_sha256": sha256_file(args.binding_receipt),
        },
        "evidence": {
            "cuda_kernel_count": kernel_count,
            "distinct_stream_count": stream_count,
            "named_kernel_count": named_kernel_count,
            "cuda_runtime_correlation_join_count": correlated_kernel_count,
            "nvtx_kernel_overlap_count": nvtx_overlap_count,
            "required_nvtx_range_counts": required_nvtx,
            "run_package_identity_consistent": True,
            "parent_lease_receipt": parent_path,
        },
    }
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 formal G1 independent export validation: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 formal G1 independent export validation: {exc}", file=sys.stderr)
        raise SystemExit(2)
