#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


BASE = Path("/root/awma_r101_transient_l2_arch_174_v1_runtime/src/gpgpu-sim")
CANDIDATE = Path(
    "/root/awma_r101r2_context2_memory_service_174_v1_runtime/src/gpgpu-sim"
)
REPO = Path(
    "/root/workspace/accel-sim-framework-awma-r101r2-context2-memory-service-174-v1"
)
OUTPUT = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1/O2_CORE.patch"
)

FILES = (
    "src/abstract_hardware_model.cc",
    "src/abstract_hardware_model.h",
    "src/gpgpu-sim/awma_r101r2_o2_service.h",
    "src/gpgpu-sim/awma_transient_l2_policy.h",
    "src/gpgpu-sim/gpu-cache.cc",
    "src/gpgpu-sim/gpu-cache.h",
    "src/gpgpu-sim/shader.cc",
    "src/gpgpu-sim/shader.h",
)


def diff_one(relative: str) -> bytes:
    old = BASE / relative
    new = CANDIDATE / relative
    if not new.is_file():
        raise RuntimeError(f"candidate source missing: {new}")
    command = [
        "diff", "-U0", "--label", f"a/{relative}",
        str(old if old.is_file() else Path("/dev/null")),
        "--label", f"b/{relative}", str(new),
    ]
    result = subprocess.run(command, check=False, capture_output=True)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr.decode(errors="replace"))
    return result.stdout


def main() -> None:
    payload = b"".join(diff_one(relative) for relative in FILES)
    if not payload:
        raise RuntimeError("O2 core patch is unexpectedly empty")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(payload)
    print(
        f"path={OUTPUT} bytes={len(payload)} "
        f"sha256={hashlib.sha256(payload).hexdigest()}"
    )


if __name__ == "__main__":
    main()
