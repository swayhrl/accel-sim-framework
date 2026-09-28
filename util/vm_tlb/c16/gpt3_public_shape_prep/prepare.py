#!/usr/bin/env python3
"""CPU-only node109 bootstrap. This module deliberately never imports torch/CUDA."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path: Path, value) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path("/data/c16/gpt3_public_shape_scale_transfer_v1"))
    args = parser.parse_args()
    if "torch" in sys.modules:
        raise RuntimeError("CPU bootstrap must not import torch")
    pack = args.repo / "docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_PREP_174NEW_V1"
    ready = json.loads((pack / "PRE_GPU_READY.json").read_text())
    if ready["status"] != "PRE_GPU_READY" or ready["resource_attestation"]["gpu_used"]:
        raise RuntimeError("PRE_GPU_READY gate missing or invalid")
    current = subprocess.check_output(["git", "-C", str(args.repo), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.run(["git", "-C", str(args.repo), "merge-base", "--is-ancestor", ready["validated_prep_head"], current]).returncode:
        raise RuntimeError("current producer worktree does not contain validated prep head")
    for item in ready["source_files"]:
        path = args.repo / item["path"]
        if sha(path) != item["sha256"]:
            raise RuntimeError(f"prep source hash mismatch: {path}")
    for arm in ("A", "B"):
        item = ready["accepted_binaries"][arm]
        path = Path(item["path"])
        if not path.is_file() or sha(path) != item["sha256"]:
            raise RuntimeError(f"accepted binary mismatch: {arm}")
    run_id = "C16R_gpt3-public-shape-scale-transfer-v1_" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = args.root / run_id
    raw = run / "raw"
    raw.mkdir(parents=True, exist_ok=False)
    (args.root / "ACTIVE_RUN_ID").write_text(run_id + "\n", encoding="utf-8")
    manifest = {
        "status": "CPU_BOOTSTRAP_PASS_GPU_NOT_STARTED",
        "run_id": run_id,
        "prep_branch": ready["prep_branch"],
        "validated_prep_head": ready["validated_prep_head"],
        "validated_prep_tree": ready["validated_prep_tree"],
        "ready_file_sha256": sha(pack / "PRE_GPU_READY.json"),
        "binary_hashes_verified": True,
        "torch_or_cuda_imported": False,
        "gpu_lock_requested": False,
        "gpu_started": False,
    }
    atomic_json(raw / "CPU_BOOTSTRAP_MANIFEST.json", manifest)
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
