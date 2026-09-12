#!/usr/bin/env python3
"""Install and import-check the C16 CPython 3.10 wheelhouse without a GPU."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from c16_native_common import ContractError, atomic_json, sha256_file
from wheelhouse_manifest import canonical_package, requirement_roots
from wheelhouse_verify import validate


def run(command: list[str]) -> str:
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if completed.returncode != 0:
        raise ContractError(f"offline wheelhouse command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr}")
    return completed.stdout


def python_version(python: Path) -> str:
    return run([str(python), "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"]).strip()


def imports(python: Path) -> dict[str, Any]:
    program = """import importlib,json\nmodules=['torch','transformers','accelerate','safetensors','huggingface_hub','pynvml','awq']\nloaded={}\nfor name in modules:\n module=importlib.import_module(name)\n loaded[name]=getattr(module,'__version__','VERSION_NOT_EXPOSED')\nimport torch\nloaded['torch_cuda_build']=torch.version.cuda\nprint(json.dumps(loaded,sort_keys=True))\n"""
    return json.loads(run([str(python), "-c", program]).strip())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--venv", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    version = python_version(args.python)
    if not version.startswith("3.10."):
        raise ContractError(f"offline wheelhouse verification requires CPython 3.10, got {version}")
    wheel_count = validate(args.wheelhouse, args.manifest, args.requirements)
    if args.venv.exists():
        raise ContractError(f"clean verification venv already exists: {args.venv}")
    roots = requirement_roots(args.requirements)
    pip_version = roots.get(canonical_package("pip"))
    if pip_version is None:
        raise ContractError("requirements lock must pin pip for offline resolver dry-run support")
    run([str(args.python), "-m", "venv", str(args.venv)])
    venv_python = args.venv / "bin/python"
    common = [str(venv_python), "-m", "pip", "install", "--no-index", "--find-links", str(args.wheelhouse), "--only-binary=:all:"]
    run([*common, f"pip=={pip_version}"])
    run([*common, "--dry-run", "-r", str(args.requirements)])
    run([*common, "-r", str(args.requirements)])
    run([str(venv_python), "-m", "pip", "check"])
    import_receipt = imports(venv_python)
    receipt = {
        "schema_version": "C16_G_OFFLINE_WHEELHOUSE_RECEIPT_V1",
        "stage_id": "C16-0.3",
        "execution_mode": "OFFLINE_CPU_IMPORT_ONLY",
        "scientific_eligible": False,
        "target": "Linux_x86_64_CP310_CUDA12.4_runtime_plan",
        "wheelhouse": str(args.wheelhouse),
        "manifest": str(args.manifest),
        "manifest_sha256": sha256_file(args.manifest),
        "requirements": str(args.requirements),
        "requirements_sha256": sha256_file(args.requirements),
        "wheel_count": wheel_count,
        "python_version": version,
        "offline_pip_upgrade": f"PASS_NO_INDEX_FIND_LINKS_pip=={pip_version}",
        "resolution_dry_run": "PASS_NO_INDEX_FIND_LINKS",
        "install": "PASS_NO_INDEX_FIND_LINKS",
        "pip_check": "PASS",
        "imports": import_receipt,
        "cuda_device_query_executed": False,
        "cuda_kernel_executed": False,
        "gpu_runtime_status": "GPU_RUNTIME_VERIFY_REQUIRED",
        "status": "LOCAL_WHEELHOUSE_HASH_CLOSED_CPU_IMPORT_VERIFIED",
    }
    atomic_json(args.receipt, receipt)
    print(f"PASS C16 offline wheelhouse install/import verification: {args.receipt}")


if __name__ == "__main__":
    try:
        main()
    except ContractError as exc:
        print(f"FAIL C16 offline wheelhouse verification: {exc}", file=sys.stderr)
        raise SystemExit(2)
