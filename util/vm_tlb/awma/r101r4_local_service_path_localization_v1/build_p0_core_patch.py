#!/usr/bin/env python3
"""Build and reproduce the exact R101R4 P0 Core patch."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


OLD = Path("/root/awma_r101r3_bounded_service_handoff_174_v1_runtime/src/gpgpu-sim")
NEW = Path("/root/awma_r101r4_local_service_path_localization_174_v1_runtime/src/gpgpu-sim")
REPO = Path(
    "/root/workspace/accel-sim-framework-"
    "awma-r101r4-local-service-path-localization-174-v1"
)
OUTPUT = REPO / (
    "docs/vm_tlb/review_packs/"
    "AWMA_R101R4_LOCAL_SERVICE_PATH_LOCALIZATION_174_V1/P0_CORE.patch"
)
FILES = (
    "src/abstract_hardware_model.cc",
    "src/abstract_hardware_model.h",
    "src/gpgpu-sim/awma_transient_l2_policy.h",
    "src/gpgpu-sim/gpu-cache.cc",
    "src/gpgpu-sim/gpu-cache.h",
    "src/gpgpu-sim/shader.cc",
    "src/gpgpu-sim/shader.h",
)
NEW_FILES = ("src/gpgpu-sim/awma_r101r4_local_service.h",)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def render() -> bytes:
    sections: list[str] = []
    for relative in FILES:
        before = (OLD / relative).read_text()
        after = (NEW / relative).read_text()
        if before == after:
            raise RuntimeError(f"expected changed file is identical: {relative}")
        sections.append(f"diff --git a/{relative} b/{relative}\n")
        sections.extend(difflib.unified_diff(
            before.splitlines(True), after.splitlines(True),
            fromfile=f"a/{relative}", tofile=f"b/{relative}",
        ))
    for relative in NEW_FILES:
        after = (NEW / relative).read_text()
        sections.append(f"diff --git a/{relative} b/{relative}\n")
        sections.append("new file mode 100644\n")
        sections.extend(difflib.unified_diff(
            [], after.splitlines(True), fromfile="/dev/null",
            tofile=f"b/{relative}",
        ))
    return "".join(sections).encode()


def verify(blob: bytes) -> None:
    with tempfile.TemporaryDirectory(prefix="awma_r101r4_p0_patch_") as tmp:
        root = Path(tmp)
        for relative in FILES:
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(OLD / relative, destination)
        process = subprocess.run(
            ["patch", "-p1", "--batch", "--forward"],
            cwd=root, input=blob, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if process.returncode:
            raise RuntimeError(
                "patch reproduction failed: "
                + process.stdout.decode(errors="replace")
                + process.stderr.decode(errors="replace")
            )
        for relative in FILES + NEW_FILES:
            if (root / relative).read_bytes() != (NEW / relative).read_bytes():
                raise RuntimeError(f"reproduced source differs: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    blob = render()
    verify(blob)
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        temporary = OUTPUT.with_name(f".{OUTPUT.name}.tmp.{os.getpid()}")
        temporary.write_bytes(blob)
        os.replace(temporary, OUTPUT)
    print(
        f"path={OUTPUT} bytes={len(blob)} "
        f"sha256={hashlib.sha256(blob).hexdigest()} "
        f"write={int(args.write)} reproduce=PASS"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
