#!/usr/bin/env python3
"""Bounded no-offload RAW BF16 full-model fit probe for the optional control."""

import json
import struct
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM


RAW = Path("/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28")
TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
OUT = Path("/data/c16/e1_natural_reuse_residency_v1/RAW_OPTIONAL_PROBE.json")


def checkpoint_tensor_bytes():
    total = 0
    for path in RAW.glob("*.safetensors"):
        with path.open("rb") as handle:
            header_bytes = struct.unpack("<Q", handle.read(8))[0]
            header = json.loads(handle.read(header_bytes))
        total += sum(value["data_offsets"][1] - value["data_offsets"][0] for key, value in header.items() if key != "__metadata__")
    return total


def main():
    config = json.loads((RAW / "config.json").read_text())
    free_bytes, total_bytes = torch.cuda.mem_get_info()
    weight_bytes = checkpoint_tensor_bytes()
    head_dim = config["hidden_size"] // config["num_attention_heads"]
    kv_bytes = config["num_hidden_layers"] * 2 * config["num_key_value_heads"] * 2048 * head_dim * 2
    logits_bytes = 2048 * config["vocab_size"] * 2
    result = {
        "status": None,
        "attempt_contract": {
            "dtype": "torch.bfloat16",
            "offload": False,
            "device_map": None,
            "backend_change": False,
            "package_change": False,
            "oom_workaround": False,
        },
        "gpu_total_bytes": total_bytes,
        "gpu_free_before_bytes": free_bytes,
        "checkpoint_tensor_bytes": weight_bytes,
        "prefill_kv_bytes": kv_bytes,
        "prefill_logits_bytes": logits_bytes,
        "minimum_live_bytes_before_other_activations": weight_bytes + kv_bytes + logits_bytes,
    }
    try:
        model = AutoModelForCausalLM.from_pretrained(RAW, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True).cuda().eval()
        ids = torch.tensor([json.loads(TOKENS.read_text())], dtype=torch.long, device="cuda")
        with torch.inference_mode():
            output = model(input_ids=ids, use_cache=True)
            current = torch.argmax(output.logits[:, -1, :], dim=-1, keepdim=True)
            past = output.past_key_values
            for _ in range(4):
                output = model(input_ids=current, past_key_values=past, use_cache=True)
                past = output.past_key_values
                current = torch.argmax(output.logits[:, -1, :], dim=-1, keepdim=True)
        torch.cuda.synchronize()
        result["status"] = "RAW_FULL_MODEL_NATURAL_CONTROL_FIT"
    except torch.cuda.OutOfMemoryError as error:
        result["status"] = "RAW_FULL_MODEL_NATURAL_CONTROL_NOT_RUN_RESOURCE_BOUND"
        result["failure_type"] = type(error).__name__
        result["failure_message"] = str(error)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
