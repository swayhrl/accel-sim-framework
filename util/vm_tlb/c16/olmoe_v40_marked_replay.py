#!/usr/bin/env python3
"""Exact expert58 replay with durable host-phase markers for NVBit V40."""
import hashlib
import json
import os
from pathlib import Path

MARKERS = Path(os.environ["C16_V40_MARKER_FILE"])

def mark(name: str) -> None:
    with MARKERS.open("a", encoding="utf-8") as handle:
        handle.write(name + "\n")
        handle.flush()
        os.fsync(handle.fileno())


mark("M0_PROCESS_START")
mark("M0A_IMPORTS_BEGIN")
import torch
from transformers import AutoModelForCausalLM
mark("M0B_IMPORTS_DONE")

ROOT = "/data/c16/models/olmoe-1b-7b-0125-instruct/b89a7c4bc24fb9e55ce2543c9458ce0ca5c4650e"
INPUT = "/data/c16/olmoe_v39r2/expert58_d32_input.pt"
mark("M0C_CUDA_INIT_BEGIN")
model = AutoModelForCausalLM.from_pretrained(
    ROOT, local_files_only=True, torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
).to("cuda").eval()
mark("M0D_CUDA_INIT_DONE")
mark("M0E_REPLAY_STATE_LOAD_BEGIN")
value = torch.load(INPUT, weights_only=True).to("cuda")
mark("M0F_REPLAY_STATE_LOAD_DONE")
mark("M0G_TARGET_READY")
mark("M1_BEFORE_EXPERT58_CALL")
with torch.inference_mode():
    output = model.model.layers[1].mlp.experts[58].down_proj(value)
weight = model.model.layers[1].mlp.experts[58].down_proj.weight
def descriptor(tensor, role):
    return {"semantic_role": role, "ptr": hex(tensor.data_ptr()), "bytes": tensor.numel() * tensor.element_size(), "dtype": str(tensor.dtype), "shape": list(tensor.shape)}
with (MARKERS.parent / "ADDRESS_CONTEXT.json").open("w", encoding="utf-8") as handle:
    json.dump({"ranges": [descriptor(value, "EXPERT_DOWN_INPUT"), descriptor(weight, "EXPERT_DOWN_WEIGHT"), descriptor(output, "EXPERT_DOWN_OUTPUT")]}, handle, indent=2)
mark("M2_AFTER_EXPERT58_CALL_RETURN")
mark("M3_BEFORE_TORCH_CUDA_SYNCHRONIZE")
torch.cuda.synchronize()
mark("M4_AFTER_TORCH_CUDA_SYNCHRONIZE")
# BF16 NumPy conversion is not portable; hash the exact tensor storage bits.
digest = hashlib.sha256(output.detach().cpu().contiguous().view(torch.uint16).numpy().tobytes()).hexdigest()
with (MARKERS.parent / "output.sha256").open("w", encoding="ascii") as handle:
    handle.write(digest + "\n")
mark("M5_OUTPUT_HASH_CLOSED")
mark("M6_BEFORE_NORMAL_PROCESS_EXIT")
