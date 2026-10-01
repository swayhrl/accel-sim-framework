#!/usr/bin/env python3
"""CPU-only freeze of the accepted Qwen layer-0 natural MLP sibling weights."""

import hashlib
import json
from pathlib import Path

import torch
from safetensors import safe_open


PARENT = Path("/data/c16/awma/r19_fp8_readiness_20261001/raw")
MODEL = Path("/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors")
ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/raw")
PARENT_SHA = "5ac9e6eb35ec2676926481d563628b80d528dac3dbdbe87bece26d21f4c54b48"
MODEL_SHA = "fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe"
X_SHA = "9a3511216c1598669c99273d233f1efaeb3b8ed2881911fd871ea7e0c22ad960"
UP_SHA = "c66e277c3f509f8b2e3b40155a954f98ac5753870d344c9f67005f7108991862"


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()


def describe(tensor):
    return {
        "shape": list(tensor.shape),
        "dtype": str(tensor.dtype),
        "bytes": tensor.numel() * tensor.element_size(),
        "sha256": tensor_sha(tensor),
    }


def main():
    assert file_sha(MODEL) == MODEL_SHA
    parent_path = PARENT / "QWEN25_LAYER0_UP_PROJ_REAL_INPUT_WEIGHT.pt"
    assert file_sha(parent_path) == PARENT_SHA
    parent = torch.load(parent_path, map_location="cpu", weights_only=True)
    x = parent["input"].contiguous()
    up_parent = parent["weight"].contiguous()
    assert tensor_sha(x) == X_SHA
    assert tensor_sha(up_parent) == UP_SHA
    assert tuple(x.shape) == (1, 256, 896)
    names = {
        "gate": "model.layers.0.mlp.gate_proj.weight",
        "up": "model.layers.0.mlp.up_proj.weight",
        "down": "model.layers.0.mlp.down_proj.weight",
    }
    with safe_open(MODEL, framework="pt", device="cpu") as reader:
        weights = {role: reader.get_tensor(name).contiguous() for role, name in names.items()}
    assert torch.equal(weights["up"], up_parent)
    assert tensor_sha(weights["up"]) == UP_SHA
    assert all(weights[role].dtype == torch.bfloat16 for role in names)
    assert tuple(weights["gate"].shape) == (4864, 896)
    assert tuple(weights["up"].shape) == (4864, 896)
    assert tuple(weights["down"].shape) == (896, 4864)
    payload = ROOT / "QWEN25_LAYER0_MLP_REAL_X_GATE_UP_DOWN.pt"
    torch.save({"input": x, "gate_weight": weights["gate"], "up_weight": weights["up"], "down_weight": weights["down"]}, payload)
    receipt = {
        "stage": "AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1",
        "scientific_parent": "7375abd8e86c1523c1873913e8fffccf0b4e3a96",
        "model": "Qwen/Qwen2.5-0.5B-Instruct",
        "model_revision": "7ae557604adf67be50417f59c2c2f167def9a775",
        "model_safetensors_sha256": MODEL_SHA,
        "parent_x_up_payload_sha256": PARENT_SHA,
        "parent_up_weight_bitwise_equal": True,
        "weight_source_names": names,
        "input": describe(x),
        "gate_weight": describe(weights["gate"]),
        "up_weight": describe(weights["up"]),
        "down_weight": describe(weights["down"]),
        "payload_path": str(payload),
        "payload_bytes": payload.stat().st_size,
        "payload_sha256": file_sha(payload),
        "environment": "/data/c16/awma/r19_fp8_readiness_20261001/env",
        "torch": torch.__version__,
        "cpu_only": True,
    }
    (ROOT / "REAL_MLP_INPUT_WEIGHT_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
