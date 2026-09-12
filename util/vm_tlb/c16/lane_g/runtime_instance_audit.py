#!/usr/bin/env python3
"""Capture a complete, truthful C16-1.1 AutoDL resource receipt.

This runtime helper supplements the immutable offline Lane-G package.  It is
not a model runner, profiler, or scientific measurement.  In particular, an
observed OS boot time is recorded as such; it is never relabelled as a
provider-reported rental-start time merely to initialize the budget ledger.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file
from execution_budget import initialize_ledger


START_SOURCES = {
    "CONTAINER_PID1_STARTTIME_OBSERVED_UNIX_EPOCH",
    "OS_BOOT_TIME_OBSERVED_UNIX_EPOCH",
    "PROVIDER_OR_AUTODL_RECORDED_UNIX_EPOCH",
    "USER_CONFIRMED_AUTODL_START_UNIX_EPOCH",
}
GPU_IDENTITY_FIELDS = "name,uuid,driver_version,memory.total"
GPU_STATE_FIELDS = (
    "uuid,temperature.gpu,pstate,power.draw,power.limit,clocks.current.graphics,"
    "clocks.current.memory,clocks.max.graphics,clocks.max.memory,"
    "clocks_throttle_reasons.active"
)


def query(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"required resource query failed: {' '.join(command)}") from exc


def optional_query(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"


def discover_tool(name: str, candidates: tuple[Path, ...]) -> dict[str, str]:
    """Resolve an installed tool even when the image did not export PATH."""
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return {"path": str(candidate), "version": optional_query([str(candidate), "--version"])}
    return {"path": "UNAVAILABLE", "version": "UNAVAILABLE"}


def memory_bytes() -> int:
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    except (ValueError, OSError, AttributeError):
        return 0


def os_release() -> dict[str, str]:
    path = Path("/etc/os-release")
    if not path.is_file():
        return {"status": "UNAVAILABLE"}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            result[key] = value.strip().strip('"')
    return result or {"status": "UNAVAILABLE"}


def cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name") and ":" in line:
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return "UNAVAILABLE"


def require_single_gpu(rows: list[str]) -> None:
    if len(rows) != 1:
        raise ContractError(f"C16 Wave-1 binding requires exactly one visible GPU; observed {len(rows)}")


def dry_receipt(work_root: Path) -> dict[str, Any]:
    return {
        "schema_version": "C16_G_RUNTIME_INSTANCE_AUDIT_V1",
        "stage_id": "C16-1.1",
        "execution_mode": "DRY_RUN",
        "scientific_eligible": False,
        "work_root": str(work_root),
        "checks": {"no_ssh": True, "no_nvidia_smi": True, "no_gpu_operation": True},
        "status": "DRY_RUN_NONSCIENTIFIC",
    }


def real_receipt(args: argparse.Namespace) -> dict[str, Any]:
    if args.exclusive_confirmation != "PROVIDER_CONFIRMED_EXCLUSIVE":
        raise ContractError("requires explicit --exclusive-confirmation PROVIDER_CONFIRMED_EXCLUSIVE; exclusivity is never inferred from nvidia-smi")
    if args.instance_start_source not in START_SOURCES:
        raise ContractError("instance-start source is not a truthful supported C16 source")
    if args.instance_start_unix <= 0 or args.instance_start_unix > time.time():
        raise ContractError("instance-start timestamp must be observed, positive, and non-future")
    identity_rows = [row for row in query(["nvidia-smi", f"--query-gpu={GPU_IDENTITY_FIELDS}", "--format=csv,noheader,nounits"]).splitlines() if row]
    require_single_gpu(identity_rows)
    state_rows = [row for row in query(["nvidia-smi", f"--query-gpu={GPU_STATE_FIELDS}", "--format=csv,noheader,nounits"]).splitlines() if row]
    require_single_gpu(state_rows)
    disk = shutil.disk_usage(args.work_root)
    if disk.free < args.min_disk_gib * 1024 ** 3:
        raise ContractError(f"work disk free space below planned minimum {args.min_disk_gib} GiB")
    observed_at = time.time()
    return {
        "schema_version": "C16_G_RUNTIME_INSTANCE_AUDIT_V1",
        "stage_id": "C16-1.1",
        "execution_mode": "AUTODL_RESOURCE_AUDIT",
        "scientific_eligible": False,
        "runtime_audit_code": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "work_root": str(args.work_root),
        "observed_at_unix": observed_at,
        "observed_at_utc": dt.datetime.fromtimestamp(observed_at, tz=dt.timezone.utc).isoformat(),
        "instance_start": {
            "unix": args.instance_start_unix,
            "utc": dt.datetime.fromtimestamp(args.instance_start_unix, tz=dt.timezone.utc).isoformat(),
            "source": args.instance_start_source,
            "source_note": args.instance_start_note,
        },
        "execution_budget_ledger": str(args.budget_ledger),
        "gpu_identity_rows": identity_rows,
        "gpu_state_rows": state_rows,
        "gpu_compute_apps_at_audit": [row for row in query(["nvidia-smi", "--query-compute-apps=pid,process_name,gpu_uuid", "--format=csv,noheader"]).splitlines() if row],
        "gpu_listing": query(["nvidia-smi", "-L"]),
        "provider_exclusive_confirmation": args.exclusive_confirmation,
        "exclusive_confirmation_evidence": args.exclusive_evidence,
        "host": {
            "hostname": query(["hostname"]),
            "kernel": query(["uname", "-srmo"]),
            "os_release": os_release(),
            "container_cgroup": optional_query(["cat", "/proc/1/cgroup"]),
            "cpu_model": cpu_model(),
            "cpu_logical_cores": os.cpu_count(),
            "ram_bytes": memory_bytes(),
            "disk_total_bytes": disk.total,
            "disk_free_bytes": disk.free,
        },
        "toolchain": {
            "nvidia_smi_version": query(["nvidia-smi"]),
            "nvcc": discover_tool("nvcc", (Path("/usr/local/cuda-12.4/bin/nvcc"),)),
            "nsys": discover_tool("nsys", (Path("/opt/nvidia/nsight-compute/2024.1.1/host/target-linux-x64/nsys"),)),
            "ncu": discover_tool("ncu", (Path("/opt/nvidia/nsight-compute/2024.1.1/ncu"), Path("/usr/local/cuda-12.4/bin/ncu"))),
            "audit_python": str(Path(sys.executable).resolve()),
            "audit_python_version": sys.version,
            "conda_version": optional_query(["conda", "--version"]),
        },
        "checks": {
            "gpu_visible": True,
            "single_gpu_binding_observed": True,
            "temperature_clock_power_captured": True,
            "exclusive_not_inferred": True,
            "disk_minimum_gib": args.min_disk_gib,
        },
        "status": "RESOURCE_RECEIPT_COMPLETE_NOT_A_SCIENTIFIC_MEASUREMENT",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    parser.add_argument("--budget-ledger", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--execute", action="store_true")
    parser.add_argument("--exclusive-confirmation", default="")
    parser.add_argument("--exclusive-evidence", default="")
    parser.add_argument("--min-disk-gib", type=int, default=120)
    parser.add_argument("--instance-start-unix", type=float)
    parser.add_argument("--instance-start-source", default="")
    parser.add_argument("--instance-start-note", default="")
    args = parser.parse_args()
    if args.min_disk_gib < 1:
        parser.error("--min-disk-gib must be positive")
    if args.execute and (args.budget_ledger is None or args.instance_start_unix is None):
        parser.error("--execute requires a ledger and an observed instance-start timestamp")
    if args.execute and not args.work_root.is_dir():
        raise ContractError("work root must exist before the C16-1.1 audit")
    receipt = dry_receipt(args.work_root) if args.dry_run else real_receipt(args)
    atomic_json(args.receipt, receipt)
    if args.execute:
        initialize_ledger(
            args.budget_ledger,
            instance_start_unix=args.instance_start_unix,
            start_source=args.instance_start_source,
            instance_receipt_path=args.receipt,
        )
    print(f"PASS C16 runtime instance audit: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 runtime instance audit: {exc}", file=sys.stderr)
        raise SystemExit(2)
