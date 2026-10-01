#!/usr/bin/env python3
"""CPU-only installed package/source/GPU telemetry receipt; no CUDA import."""

import hashlib
import importlib.metadata as md
import json
import subprocess
from pathlib import Path


ROOT = Path("/data/c16/awma/r20_active_world_native_v1")
SOURCE = ROOT / "source/mujoco_warp"
MENAGERIE = ROOT / "source/mujoco_menagerie"
RAW = ROOT / "raw"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path):
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def main():
    packages = {}
    for name in ("mujoco", "warp-lang", "numpy", "absl-py", "etils", "glfw", "pyopengl"):
        dist = md.distribution(name)
        record = next((dist.locate_file(file) for file in dist.files if str(file).endswith(".dist-info/RECORD")), None)
        h = hashlib.sha256()
        present = 0
        for rel in sorted(dist.files or [], key=str):
            path = Path(dist.locate_file(rel))
            if not path.is_file():
                continue
            present += 1
            h.update(str(rel).encode())
            h.update(bytes.fromhex(sha(path)))
        packages[name] = {
            "version": dist.version,
            "dist_info_record_path": str(record) if record else None,
            "dist_info_record_sha256": sha(Path(record)) if record else None,
            "installed_files_present": present,
            "installed_tree_sha256": h.hexdigest(),
        }
    gpu = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=name,uuid,memory.total,driver_version,compute_cap", "--format=csv,noheader"],
        text=True,
    ).strip()
    receipt = {
        "stage": "AWMA_R20_ACTIVE_WORLD_NATIVE_109_V1",
        "source_commit": git_head(SOURCE),
        "menagerie_commit": git_head(MENAGERIE),
        "source_pyproject_blob": subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD:pyproject.toml"], text=True).strip(),
        "source_solver_blob": subprocess.check_output(["git", "-C", str(SOURCE), "rev-parse", "HEAD:mujoco_warp/_src/solver.py"], text=True).strip(),
        "uv_lock_sha256": sha(SOURCE / "uv.lock"),
        "uv_tool_version": subprocess.check_output([str(ROOT / "toolenv/bin/uv"), "--version"], text=True).strip(),
        "isolated_environment": str(ROOT / "env"),
        "installed_packages": packages,
        "gpu_telemetry": gpu,
        "warp_runtime_canary_receipt": "B16_GRAPH_CANARY.json",
        "warp_reported_cuda_toolkit": "12.9",
        "warp_reported_driver_cuda_api": "13.0",
    }
    (RAW / "RUNTIME_SOURCE_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"source_commit": receipt["source_commit"], "menagerie_commit": receipt["menagerie_commit"], "uv_lock_sha256": receipt["uv_lock_sha256"], "packages": {k: v["version"] for k, v in packages.items()}, "gpu_telemetry": gpu}, sort_keys=True))


if __name__ == "__main__":
    main()
