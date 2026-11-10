#!/usr/bin/env python3
"""Offline, CPU-only installation receipt; never loads checkpoint tensors."""

import hashlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path

assert os.environ.get("CUDA_VISIBLE_DEVICES") == "-1"
assert os.environ.get("VLLM_TARGET_DEVICE") == "cpu"
assert os.environ.get("HF_HUB_OFFLINE") == "1"

import torch
import vllm

root = Path(metadata.distribution("vllm").locate_file("vllm"))
registry = root / "model_executor/models/registry.py"
qwen = root / "model_executor/models/qwen3_5.py"
multimodal = root / "config/multimodal.py"
source_text = {p.name: p.read_text(encoding="utf-8") for p in (registry, qwen, multimodal)}

checks = {
    "vllm_import": bool(vllm),
    "qwen_conditional_registry": "Qwen3_5ForConditionalGeneration" in source_text["registry.py"],
    "qwen_causal_registry": "Qwen3_5ForCausalLM" in source_text["registry.py"],
    "multimodal_pruning": "supports_multimodal_pruning = True" in source_text["qwen3_5.py"],
    "language_model_only_config": "language_model_only: bool = False" in source_text["multimodal.py"],
    "cuda_uninitialized": not torch.cuda.is_initialized(),
}
assert all(checks.values()), checks

result = {
    "scope": "static_import_and_cli_cpu_only_no_checkpoint_load",
    "versions": {name: metadata.version(name) for name in ("vllm", "torch", "transformers", "triton", "uv")},
    "checks": checks,
    "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (registry, qwen, multimodal)},
    "torch_cuda_initialized": torch.cuda.is_initialized(),
}
print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
