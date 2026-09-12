#!/usr/bin/env python3
"""Record C16-1.1 resources without guessing GPU exclusivity or capability."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json


def query(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"required resource query failed: {' '.join(command)}") from exc


def memory_bytes() -> int:
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError, AttributeError):
        return 0


def dry_receipt(work_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_AUTODL_INSTANCE_RECEIPT_V1",
        "stage_id": "C16-1.1",
        "execution_mode": "DRY_RUN",
        "scientific_eligible": False,
        "work_root": str(work_root),
        "checks": {"no_nvidia_smi": True, "no_ssh": True, "no_gpu_operation": True},
        "status": "DRY_RUN_NONSCIENTIFIC",
    }


def real_receipt(work_root: Path, exclusive_confirmation: str, min_disk_gib: int) -> dict[str, Any]:
    if exclusive_confirmation != "PROVIDER_CONFIRMED_EXCLUSIVE":
        raise ContractError("C16-1.1 requires --exclusive-confirmation PROVIDER_CONFIRMED_EXCLUSIVE; do not infer exclusivity")
    gpu_rows = [line for line in query(["nvidia-smi", "--query-gpu=name,uuid,driver_version,memory.total", "--format=csv,noheader,nounits"]).splitlines() if line]
    if not gpu_rows:
        raise ContractError("nvidia-smi reports no GPU")
    applications = query(["nvidia-smi", "--query-compute-apps=pid,process_name,gpu_uuid", "--format=csv,noheader"]) if gpu_rows else ""
    disk = shutil.disk_usage(work_root)
    if disk.free < min_disk_gib * 1024 ** 3:
        raise ContractError(f"work disk free space below {min_disk_gib} GiB")
    return {
        "schema_version": "C16_G_AUTODL_INSTANCE_RECEIPT_V1",
        "stage_id": "C16-1.1",
        "execution_mode": "AUTODL_RESOURCE_AUDIT",
        "scientific_eligible": False,
        "work_root": str(work_root),
        "gpu_rows": gpu_rows,
        "compute_apps_at_audit": applications.splitlines() if applications else [],
        "provider_exclusive_confirmation": exclusive_confirmation,
        "cpu_logical_cores": os.cpu_count(),
        "ram_bytes": memory_bytes(),
        "disk_total_bytes": disk.total,
        "disk_free_bytes": disk.free,
        "nvcc_version": query(["nvcc", "--version"]),
        "checks": {"gpu_visible": True, "disk_minimum_gib": min_disk_gib, "exclusive_not_inferred": True},
        "status": "RESOURCE_RECEIPT_COMPLETE_NOT_A_SCIENTIFIC_MEASUREMENT",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--execute", action="store_true")
    parser.add_argument("--exclusive-confirmation", default="")
    parser.add_argument("--min-disk-gib", type=int, default=300)
    args = parser.parse_args()
    if args.min_disk_gib < 1:
        parser.error("--min-disk-gib must be positive")
    receipt = dry_receipt(args.work_root) if args.dry_run else real_receipt(args.work_root, args.exclusive_confirmation, args.min_disk_gib)
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 AutoDL instance receipt: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 AutoDL instance receipt: {exc}", file=sys.stderr)
        raise SystemExit(2)
