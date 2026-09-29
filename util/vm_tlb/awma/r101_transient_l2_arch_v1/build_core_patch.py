#!/usr/bin/env python3
from __future__ import annotations

import difflib
import hashlib
from pathlib import Path


BASE = Path("/root/awma_rtx4080_v1_baseline_promotion_v1_runtime/src/gpgpu-sim")
CANDIDATE = Path("/root/awma_r101_transient_l2_arch_174_v1_runtime/src/gpgpu-sim")
OUTPUT = Path("/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1/docs/vm_tlb/review_packs/AWMA_R101_TRANSIENT_L2_ARCH_EXPLORATION_174_V1/TRANSIENT_L2_CORE.patch")
EXPECTED = {
    "src/gpgpu-sim/gpu-cache.cc": "8b8fcc3f9356da6005d0898c50298553270484ba58bcab1765ef5615e75d7cbb",
    "src/gpgpu-sim/shader.cc": "b8caf666a367ecd41e09a34bf2caf1c5484fd199948094b877d7366b185fb978",
    "src/gpgpu-sim/l2cache.cc": "881d5708a0a0f0b021d528cd64600e42c4de28aa89daed1f2f3542a3ba9d9073",
    "src/gpgpu-sim/gpu-sim.h": "a046fabc77b2ef4a4fdf981232c48693bff48bbc958a74cccc3f1939a43faeb9",
    "src/gpgpu-sim/gpu-cache.h": "5ef6f6d26ffa4b162a41b6f6d55d5a4506075875fde31597710055f66a0a5bcf",
    "src/gpgpu-sim/gpu-sim.cc": "61509c07c4cb416c52f7bd83ed9bcca5da0fbba6baef37fd6157677915c8e9c2",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lines(path: Path) -> list[str]:
    return path.read_text().splitlines(keepends=True)


def main() -> int:
    chunks: list[str] = []
    for relative, expected in EXPECTED.items():
        source = BASE / relative; target = CANDIDATE / relative
        if sha(source) != expected:
            raise RuntimeError(f"baseline source mismatch: {relative}")
        chunks.extend(difflib.unified_diff(
            lines(source), lines(target), fromfile=f"a/{relative}",
            tofile=f"b/{relative}", n=3,
        ))
    new_relative = "src/gpgpu-sim/awma_transient_l2_policy.h"
    chunks.extend(difflib.unified_diff(
        [], lines(CANDIDATE / new_relative), fromfile="/dev/null",
        tofile=f"b/{new_relative}", n=3,
    ))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    patch = "".join(chunks)
    patch = "".join("\n" if line == " \n" else line
                    for line in patch.splitlines(keepends=True))
    OUTPUT.write_text(patch)
    print(f"patch_bytes={OUTPUT.stat().st_size} patch_sha256={sha(OUTPUT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
