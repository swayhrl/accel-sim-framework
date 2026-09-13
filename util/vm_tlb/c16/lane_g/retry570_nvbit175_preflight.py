#!/usr/bin/env python3
"""Fail-closed, non-mutating Retry570 NVBit 1.7.5 runtime preflight."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file, valid_sha256
from retry570_long_watch import nvdisasm_environment_contract


SCHEMA = "C16_G_RETRY570_NVBIT175_PREFLIGHT_V1"


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON object: {path}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON object required: {path}")
    return value


def text(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ContractError(f"command failed: {' '.join(command)}") from exc


def passed_receipt(path: Path | None, expected: str) -> str:
    if path is None or not path.is_file():
        return "NOT_MATERIALIZED"
    value = load(path)
    return "PASS" if value.get("status") == expected else "FAIL"


def active_gpu_process_count() -> int:
    output = text(["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader"])
    return len([line for line in output.splitlines() if line.strip()])


def runtime_identity(python: Path) -> dict[str, str]:
    program = """import json,torch
from pathlib import Path
p=Path(torch.__file__).resolve().parent/'lib'/'libtorch_cuda.so'
print(json.dumps({'torch':torch.__version__,'torch_cuda':torch.version.cuda,'libtorch':str(p),'cuda_available':torch.cuda.is_available(),'device':torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NA','capability':'.'.join(map(str,torch.cuda.get_device_capability(0))) if torch.cuda.is_available() else 'NA'}))"""
    try:
        return json.loads(text([str(python), "-c", program]))
    except json.JSONDecodeError as exc:
        raise ContractError("cannot decode Python/PyTorch identity") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--nvbit-release-root", type=Path, required=True)
    parser.add_argument("--lane-tool", type=Path, required=True)
    parser.add_argument("--nvdisasm", type=Path, required=True)
    parser.add_argument("--nsys", type=Path, required=True)
    parser.add_argument("--budget-ledger", type=Path, required=True)
    parser.add_argument("--official-receipt", type=Path)
    parser.add_argument("--empty-receipt", type=Path)
    parser.add_argument("--lane-first-kernel-receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = load(args.profile)
    if profile.get("profile_status") != "KNOWN_GOOD_FOR_MINIMAL_LANE_G_FIRST_KERNEL":
        raise ContractError("profile is not a known-good Lane G first-kernel profile")
    expected = profile["gpu"], profile["cuda"], profile["pytorch"], profile["nvbit"], profile["lane_g_tracer"]
    gpu, cuda, torch_profile, nvbit, tracer = expected
    smi = text(["nvidia-smi", "--query-gpu=name,uuid,driver_version,compute_cap", "--format=csv,noheader,nounits"])
    parts = [item.strip() for item in smi.split(",")]
    identity = runtime_identity(args.python)
    nvcc = text([str(args.nvdisasm.parent / "nvcc"), "--version"])
    nvdisasm_version = text([str(args.nvdisasm), "--version"])
    nsys_version = text([str(args.nsys), "--version"])
    child = nvdisasm_environment_contract(args.nvdisasm, os.environ.get("PATH", ""))
    measurement = args.budget_ledger.parent.parent / "control" / "MEASUREMENT_ACTIVE"
    profile_match = (
        len(parts) == 4 and parts[0] == gpu["name"] and parts[2] == profile["driver_version"] and parts[3] == gpu["compute_capability"] and
        identity["torch"] == torch_profile["version"] and str(identity["torch_cuda"]) == torch_profile["cuda"] and identity["device"] == gpu["name"] and
        sha256_file(Path(identity["libtorch"])) == torch_profile["libtorch_cuda_sha256"] and
        sha256_file(args.nvbit_release_root / "core" / "libnvbit.a") == nvbit["core_libnvbit_sha256"] and sha256_file(args.lane_tool) == tracer["binary_sha256"]
    )
    official = passed_receipt(args.official_receipt, "NVBIT_OFFICIAL_VECTORADD_SMOKE_PASS")
    empty = passed_receipt(args.empty_receipt, "MODULE_FIRST_USE_2X2_COMPLETE")
    lane = passed_receipt(args.lane_first_kernel_receipt, "COMPLETE")
    no_stale_gpu = active_gpu_process_count() == 0
    output = {
        "schema_version": SCHEMA, "scientific_eligible": False, "diagnostic_only": True,
        "GPU_IDENTITY": "PASS" if len(parts) == 4 and parts[0] == gpu["name"] and parts[3] == gpu["compute_capability"] else "FAIL",
        "PROFILE_MATCH": "KNOWN_GOOD" if profile_match else "UNVALIDATED_MATRIX",
        "CUDA_VERSION": cuda["toolkit"], "DRIVER": parts[2] if len(parts) == 4 else "UNAVAILABLE",
        "PYTORCH": identity["torch"], "NVBIT_VERSION": nvbit["version"],
        "NVDISASM_PATH": "PASS" if args.nvdisasm.is_file() and cuda["nvdisasm_absolute_path"] == str(args.nvdisasm) and cuda["nvdisasm"] in nvdisasm_version else "FAIL",
        "NSYS_PATH": "PASS" if args.nsys.is_file() and os.access(args.nsys, os.X_OK) and "NVIDIA Nsight Systems version" in nsys_version else "FAIL",
        "CHILD_PATH": "PASS" if str(args.nvdisasm.parent) in child["PATH"].split(":") and child["NVDISASM"] == "nvdisasm" else "FAIL",
        "CUDA_MODULE_LOADING": os.environ.get("CUDA_MODULE_LOADING", "UNSET"),
        "OFFICIAL_NVBIT_SMOKE": official, "EXACT_EMPTY_SMOKE": empty, "LANE_G_FIRST_KERNEL_SMOKE": lane,
        "STALE_GPU_PROCESS": "ABSENT" if no_stale_gpu else "PRESENT", "MEASUREMENT_ACTIVE": "PRESENT" if measurement.exists() else "ABSENT",
        "child_environment": child, "observed": {"nvidia_smi": smi, "nvcc": nvcc, "nvdisasm": nvdisasm_version, "nsys": nsys_version, "torch": identity},
    }
    required = (profile_match, output["NVDISASM_PATH"] == "PASS", output["NSYS_PATH"] == "PASS", output["CHILD_PATH"] == "PASS", os.environ.get("CUDA_MODULE_LOADING") == "EAGER",
                official == "PASS", empty == "PASS", lane == "PASS", no_stale_gpu, not measurement.exists())
    output["CAPTURE_ALLOWED"] = "YES" if all(required) else "NO"
    atomic_json(args.output, output)
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        raise SystemExit(f"FAIL Retry570 NVBit 1.7.5 preflight: {exc}")
