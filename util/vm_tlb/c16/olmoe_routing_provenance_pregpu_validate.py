#!/usr/bin/env python3
"""Fail-closed CPU-only authority seal immediately before the locked campaign."""
from __future__ import annotations

import hashlib
import json
import os
import platform
from pathlib import Path

import torch
import transformers
from transformers.models.olmoe import modeling_olmoe

ROOT = Path("/data/c16/olmoe_routing_provenance_multiround_v1")
REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-routing-provenance-multiround-109-v1")
MODEL = Path("/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e")
ENV = Path("/data/c16/env/c16-olmoe-v34-runtime-v1")
EXPECTED_MODELING = "413888fc3be7e037727586f25900b629cc5dbc06b227a4f0d42c67cacb597bc7"
EXPECTED_ASSET_RECEIPT = "01319b411b07ccd7b53c4f653bd5986a51604d9c2c16be7412257e994ff49d13"
EXPECTED_INPUTS = {
    "P_TEXT": "bba8ad1051b3e96039933d65ad8d77af3877f5603ae743b5e123d82c64de88e5",
    "P_CODE": "107ef30b6f1bab3052bdd909b734ac538fa5aa4944c5094ac3b66c25fc3247f2",
    "P_STRUCTURED": "ec5cd4d780ee8b16829eb9c71c002996a114bf84b5209511cf75d0c8469fdad4",
    "P_PROSE": "e798d58332299434f0b945238c047340e6070cf881bd677fdfc62c369e24f2e4",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def main() -> None:
    run_id = (ROOT / "ACTIVE_RUN_ID").read_text().strip()
    run = ROOT / "raw" / run_id
    freeze = json.loads((run / "INPUT_FREEZE_MANIFEST.json").read_text())
    if freeze["status"] != "PASS_CPU_INPUT_FREEZE" or freeze["run_id"] != run_id:
        raise RuntimeError("INPUT_FREEZE_RECEIPT_INVALID")
    for prompt_id, expected in EXPECTED_INPUTS.items():
        path = run / "inputs" / f"{prompt_id}.token_ids.json"
        if sha(path) != expected or len(json.loads(path.read_text())) != 2048:
            raise RuntimeError(f"INPUT_AUTHORITY_FAIL {prompt_id}")
    if torch.__version__ != "2.7.1+cu126" or torch.version.cuda != "12.6":
        raise RuntimeError("TORCH_RUNTIME_AUTHORITY_FAIL")
    if transformers.__version__ != "4.55.0" or platform.python_version() != "3.12.3":
        raise RuntimeError("PYTHON_TRANSFORMERS_AUTHORITY_FAIL")
    modeling_path = Path(modeling_olmoe.__file__)
    if sha(modeling_path) != EXPECTED_MODELING:
        raise RuntimeError("MODELING_OLMOE_SOURCE_AUTHORITY_FAIL")
    asset_receipt = MODEL / "MODEL_ASSET_RECEIPT.json"
    if sha(asset_receipt) != EXPECTED_ASSET_RECEIPT:
        raise RuntimeError("MODEL_ASSET_RECEIPT_FAIL")
    runner = REPO / "util/vm_tlb/c16/olmoe_routing_provenance_runner.py"
    prepare = REPO / "util/vm_tlb/c16/olmoe_routing_provenance_prepare.py"
    wrapper = ROOT / "run_olmoe_routing_locked.sh"
    receipt = {
        "status": "PASS_PRE_GPU_AUTHORITY_SEAL",
        "run_id": run_id,
        "coordination_head": "378df585cba4c21ac5864c374976e271ae44e9a3",
        "producer_base": "0e88faa28c9066b48e394dce657d7a16e6332a32",
        "model_id": "allenai/OLMoE-1B-7B-0125-Instruct",
        "model_revision": "b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e",
        "model_asset_receipt_path": str(asset_receipt),
        "model_asset_receipt_sha256": sha(asset_receipt),
        "runtime_env": str(ENV),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "transformers": transformers.__version__,
        "modeling_olmoe_path": str(modeling_path),
        "modeling_olmoe_sha256": sha(modeling_path),
        "input_freeze_manifest_sha256": sha(run / "INPUT_FREEZE_MANIFEST.json"),
        "pip_freeze_sha256": sha(run / "RUNTIME_PIP_FREEZE.txt"),
        "runner_path": str(runner),
        "runner_sha256": sha(runner),
        "prepare_sha256": sha(prepare),
        "locked_wrapper_path": str(wrapper),
        "locked_wrapper_sha256": sha(wrapper),
        "session_count": 6,
        "prompt_count": 4,
        "gpu_used_during_seal": False,
    }
    atomic_json(run / "PRE_GPU_AUTHORITY_RECEIPT.json", receipt)
    manifest_path = run / "CAMPAIGN_MANIFEST.pre_gpu.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["pre_gpu_authority_receipt_sha256"] = sha(run / "PRE_GPU_AUTHORITY_RECEIPT.json")
    manifest["runner_sha256"] = receipt["runner_sha256"]
    manifest["runtime"] = {"python": receipt["python"], "torch": receipt["torch"], "torch_cuda": receipt["torch_cuda"], "transformers": receipt["transformers"], "modeling_olmoe_sha256": receipt["modeling_olmoe_sha256"]}
    atomic_json(manifest_path, manifest)
    print(json.dumps({"status": receipt["status"], "run_id": run_id, "runner_sha256": receipt["runner_sha256"]}))


if __name__ == "__main__":
    main()
