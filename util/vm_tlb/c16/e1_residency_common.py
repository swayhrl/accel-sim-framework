#!/usr/bin/env python3
"""Shared frozen authorities and helpers for the C16 E1 residency intervention."""

import csv
import hashlib
import json
import statistics
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM
from safetensors import safe_open
from transformers import Qwen2Config
from transformers.models.qwen2.modeling_qwen2 import Qwen2DecoderLayer


RAW = Path("/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28")
AWQ = "/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641"
AUTH = Path("/data/c16/e1_clean_baseline_v1/capture_a")
REPO = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-residency-intervention-109-v1")
CLEAN_PACK = REPO / "docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_109_V1"
PRESSURE_BYTES = 256 * 1024 * 1024
PRESSURE_ELEMENTS = PRESSURE_BYTES // 4
SPARSE_STRIDE_ELEMENTS = 1024
L2_BYTES = 67_108_864


def tensor_sha(tensor: torch.Tensor) -> str:
    raw = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats(values):
    return {
        "samples_ms": values,
        "min_ms": min(values),
        "median_ms": statistics.median(values),
        "max_ms": max(values),
        "cv": statistics.pstdev(values) / statistics.mean(values),
    }


def raw_tensor_loader():
    index = json.loads((RAW / "model.safetensors.index.json").read_text())["weight_map"]

    def load(key):
        with safe_open(RAW / index[key], framework="pt", device="cpu") as handle:
            return handle.get_tensor(key)

    return load


def load_raw_layer_cpu():
    config = Qwen2Config.from_pretrained(RAW)
    load = raw_tensor_loader()
    layer = Qwen2DecoderLayer(config, 0).to(dtype=torch.bfloat16)
    layer.load_state_dict({name: load("model.layers.0." + name) for name in layer.state_dict()}, strict=True)
    return config, layer, load


def role_module(layer, role):
    if role == "q_proj":
        return layer.self_attn.q_proj
    if role == "down_proj":
        return layer.mlp.down_proj
    if role == "up_proj":
        return layer.mlp.up_proj
    raise ValueError(role)


def dense_fp16_copy(module):
    result = torch.nn.Linear(
        module.in_features,
        module.out_features,
        bias=module.bias is not None,
        dtype=torch.float16,
    )
    result.weight.data.copy_(module.weight.detach().cpu().to(torch.float16))
    if module.bias is not None:
        result.bias.data.copy_(module.bias.detach().cpu().to(torch.float16))
    return result.cuda().eval()


def load_single_module(role, implementation):
    if implementation == "RAW_FP16":
        _, layer, _ = load_raw_layer_cpu()
        module = dense_fp16_copy(role_module(layer, role))
        del layer
        return module, None
    model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    layer = model.model.model.layers[0]
    return role_module(layer, role), model


def accepted_text_points():
    result = {}
    path = CLEAN_PACK / "CORE_18_POINT_PATHS.tsv"
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["implementation"] in ("RAW_FP16", "AWQ_FP16_INPUT"):
                result[(row["role"], int(row["M"]), row["implementation"])] = row
    return result


def load_text_input(role, matrix_m):
    return torch.load(AUTH / f"{role}_M{matrix_m}_input.pt", map_location="cpu", weights_only=True).to(torch.float16).cuda()


def state_bytes(module):
    tensors = []
    total = 0
    for name, tensor in sorted(module.state_dict().items()):
        byte_count = tensor.numel() * tensor.element_size()
        total += byte_count
        tensors.append(
            {
                "name": name,
                "shape": list(tensor.shape),
                "dtype": str(tensor.dtype),
                "element_count": tensor.numel(),
                "element_size_bytes": tensor.element_size(),
                "bytes": byte_count,
            }
        )
    return total, tensors


def cuda_timed(call):
    start = torch.cuda.Event(enable_timing=True)
    stop = torch.cuda.Event(enable_timing=True)
    start.record()
    output = call()
    stop.record()
    stop.synchronize()
    return output, float(start.elapsed_time(stop))


def warm(module, tensor):
    module(tensor)
    module(tensor)
    torch.cuda.synchronize()


def pressure_touch(buffer, state, dose_bytes=PRESSURE_BYTES):
    if state in ("WARM", "WARM_A", "WARM_B", "WARM_RECOVERY") or dose_bytes == 0:
        return 0.0
    if state == "SPARSE_PAGE_PRESSURE":
        call = lambda: buffer[::SPARSE_STRIDE_ELEMENTS].sum()
    elif state in ("DENSE_MEMORY_PRESSURE", "DENSE_DOSE"):
        elements = dose_bytes // buffer.element_size()
        call = lambda: buffer[:elements].sum()
    else:
        raise ValueError(state)
    _, elapsed = cuda_timed(call)
    torch.cuda.synchronize()
    return elapsed
