#!/usr/bin/env python3
"""Run capacity census, native intervention timing, dose timing, and CODE timing."""

import gc
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM
from transformers.cache_utils import DynamicCache
from transformers.models.qwen2.modeling_qwen2 import Qwen2RotaryEmbedding

from e1_residency_common import (
    AUTH,
    AWQ,
    L2_BYTES,
    PRESSURE_BYTES,
    PRESSURE_ELEMENTS,
    RAW,
    SPARSE_STRIDE_ELEMENTS,
    accepted_text_points,
    cuda_timed,
    dense_fp16_copy,
    file_sha,
    load_raw_layer_cpu,
    load_text_input,
    pressure_touch,
    raw_tensor_loader,
    role_module,
    state_bytes,
    tensor_sha,
    warm,
)


OUT = Path("/data/c16/e1_residency_intervention_v1")
TOKEN_PATH = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_CODE/payload/token_ids.json")
TOKEN_SHA = "7acdc48f59cf204c192c5663d62abfb72fb8d754e6b0e92bd28d991b64fdafb8"
CODE_INPUT_SHA = "8617167912ed3cc89d5821b8621cde092374638a099965b4e1fe2a9fec4e6077"
CODE_OUTPUTS = {
    "RAW_FP16": "bfe831b628e7941de2a50222f0d9d6ed3f3dbb5e38a5861dc28276c00f156512",
    "AWQ_FP16_INPUT": "8138405fa621da78b51b5d050493a2140a5a5725a85519a8d91c61c2b8d0978a",
}


def code_input(config, layer, load_tensor):
    if file_sha(TOKEN_PATH) != TOKEN_SHA:
        raise RuntimeError("CODE token authority mismatch")
    captured = {}
    hook = layer.mlp.down_proj.register_forward_pre_hook(lambda module, args: captured.update({"x": args[0].detach().clone()}))
    token_ids = json.loads(TOKEN_PATH.read_text())
    embedding = torch.nn.Embedding(config.vocab_size, config.hidden_size, dtype=torch.bfloat16)
    embedding.weight.data.copy_(load_tensor("model.embed_tokens.weight"))
    embedding = embedding.cuda()
    hidden = embedding(torch.tensor([token_ids], device="cuda"))
    positions = torch.arange(len(token_ids), device="cuda").unsqueeze(0)
    rotary = Qwen2RotaryEmbedding(config=config).cuda()
    position_embeddings = rotary(hidden, positions)
    with torch.inference_mode():
        layer(
            hidden,
            position_ids=positions,
            past_key_value=DynamicCache(),
            use_cache=True,
            cache_position=torch.arange(len(token_ids), device="cuda"),
            position_embeddings=position_embeddings,
        )
    hook.remove()
    result = captured["x"][:, :1, :].to(torch.float16).detach()
    if tensor_sha(result) != CODE_INPUT_SHA:
        raise RuntimeError("CODE M1 authority mismatch")
    del embedding, hidden, positions, rotary, position_embeddings, captured
    return result


def measure_state(module, tensor, pressure, state, expected_output_sha):
    warm(module, tensor)
    pressure_ms = pressure_touch(pressure, state)
    output, target_ms = cuda_timed(lambda: module(tensor))
    output_sha = tensor_sha(output)
    if output_sha != expected_output_sha:
        raise RuntimeError(f"output authority mismatch for {state}: {output_sha}")
    return target_ms, pressure_ms, output_sha


def main():
    if OUT.exists():
        raise SystemExit(f"refusing to overwrite {OUT}")
    OUT.mkdir(parents=True)

    # Contract: one 256 MiB FP32 allocation, initialized before target module preparation.
    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    pressure_contract = {
        "allocation_bytes": pressure.numel() * pressure.element_size(),
        "allocation_elements": pressure.numel(),
        "dtype": str(pressure.dtype),
        "device": str(pressure.device),
        "data_ptr": pressure.data_ptr(),
        "sparse_stride_elements": SPARSE_STRIDE_ELEMENTS,
        "sparse_stride_bytes": SPARSE_STRIDE_ELEMENTS * pressure.element_size(),
        "sparse_selected_elements": pressure[::SPARSE_STRIDE_ELEMENTS].numel(),
        "dense_selected_elements": pressure.numel(),
        "initialized_before_target_modules": True,
    }
    if pressure_contract["allocation_bytes"] != PRESSURE_BYTES:
        raise RuntimeError("pressure allocation size mismatch")

    config, raw_layer, load_tensor = load_raw_layer_cpu()
    raw_layer = raw_layer.cuda().eval()
    with torch.inference_mode():
        code_x = code_input(config, raw_layer, load_tensor)
    torch.save(code_x.cpu(), OUT / "CODE_DOWN_PROJ_M1_FP16_INPUT.pt")

    raw_modules = {}
    for role in ("q_proj", "down_proj", "up_proj"):
        raw_modules[role] = dense_fp16_copy(role_module(raw_layer, role))
    del raw_layer
    gc.collect()
    torch.cuda.empty_cache()

    awq_model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    awq_layer = awq_model.model.model.layers[0]
    awq_modules = {role: role_module(awq_layer, role) for role in ("q_proj", "down_proj", "up_proj")}

    census = []
    census_details = {}
    for role in ("q_proj", "down_proj", "up_proj"):
        for implementation, module in (("RAW_FP16", raw_modules[role]), ("AWQ_FP16_INPUT", awq_modules[role])):
            total, tensors = state_bytes(module)
            census.append(
                {
                    "role": role,
                    "implementation": implementation,
                    "state_bytes": total,
                    "device_l2_bytes": L2_BYTES,
                    "state_over_l2": total / L2_BYTES,
                    "relation_to_l2": "LT_L2" if total < L2_BYTES else "GT_L2" if total > L2_BYTES else "EQ_L2",
                }
            )
            census_details[f"{role}:{implementation}"] = tensors

    accepted = accepted_text_points()
    text_inputs = {}
    points = []
    for role, matrix_m in (("q_proj", 1), ("down_proj", 1), ("up_proj", 1), ("up_proj", 256)):
        tensor = load_text_input(role, matrix_m)
        text_inputs[(role, matrix_m)] = tensor
        for implementation in ("RAW_FP16", "AWQ_FP16_INPUT"):
            authority = accepted[(role, matrix_m, implementation)]
            if tensor_sha(tensor) != authority["input_sha"]:
                raise RuntimeError(f"TEXT input authority mismatch: {role} M{matrix_m} {implementation}")
            points.append((role, matrix_m, implementation))

    timing_rows = []
    for repetition in range(7):
        ordered = points[repetition % len(points):] + points[:repetition % len(points)]
        for role, matrix_m, implementation in ordered:
            module = raw_modules[role] if implementation == "RAW_FP16" else awq_modules[role]
            tensor = text_inputs[(role, matrix_m)]
            expected_output = accepted[(role, matrix_m, implementation)]["output_sha"]
            for state in ("WARM_A", "SPARSE_PAGE_PRESSURE", "DENSE_MEMORY_PRESSURE", "WARM_B"):
                with torch.inference_mode():
                    target_ms, pressure_ms, output_sha = measure_state(module, tensor, pressure, state, expected_output)
                timing_rows.append(
                    {
                        "input_kind": "TEXT",
                        "role": role,
                        "M": matrix_m,
                        "implementation": implementation,
                        "state": state,
                        "repetition": repetition,
                        "target_ms": target_ms,
                        "pressure_ms": pressure_ms,
                        "input_sha256": tensor_sha(tensor),
                        "output_sha256": output_sha,
                    }
                )

    dose_rows = []
    doses_mib = [0, 16, 32, 64, 128, 256]
    for repetition in range(7):
        ordered_doses = doses_mib[repetition % len(doses_mib):] + doses_mib[:repetition % len(doses_mib)]
        implementations = ("RAW_FP16", "AWQ_FP16_INPUT") if repetition % 2 == 0 else ("AWQ_FP16_INPUT", "RAW_FP16")
        for dose_mib in ordered_doses:
            for implementation in implementations:
                module = raw_modules["up_proj"] if implementation == "RAW_FP16" else awq_modules["up_proj"]
                tensor = text_inputs[("up_proj", 1)]
                expected_output = accepted[("up_proj", 1, implementation)]["output_sha"]
                with torch.inference_mode():
                    warm(module, tensor)
                    pressure_ms = pressure_touch(pressure, "DENSE_DOSE", dose_mib * 1024 * 1024)
                    output, target_ms = cuda_timed(lambda: module(tensor))
                output_sha = tensor_sha(output)
                if output_sha != expected_output:
                    raise RuntimeError("dose output authority mismatch")
                dose_rows.append(
                    {
                        "role": "up_proj",
                        "M": 1,
                        "implementation": implementation,
                        "dose_mib": dose_mib,
                        "repetition": repetition,
                        "target_ms": target_ms,
                        "pressure_ms": pressure_ms,
                        "input_sha256": tensor_sha(tensor),
                        "output_sha256": output_sha,
                    }
                )

    code_rows = []
    code_input_sha = tensor_sha(code_x)
    for repetition in range(7):
        implementations = ("RAW_FP16", "AWQ_FP16_INPUT") if repetition % 2 == 0 else ("AWQ_FP16_INPUT", "RAW_FP16")
        for implementation in implementations:
            module = raw_modules["down_proj"] if implementation == "RAW_FP16" else awq_modules["down_proj"]
            for state in ("WARM_A", "DENSE_MEMORY_PRESSURE", "WARM_B"):
                with torch.inference_mode():
                    target_ms, pressure_ms, output_sha = measure_state(module, code_x, pressure, state, CODE_OUTPUTS[implementation])
                code_rows.append(
                    {
                        "input_kind": "CODE",
                        "role": "down_proj",
                        "M": 1,
                        "implementation": implementation,
                        "state": state,
                        "repetition": repetition,
                        "target_ms": target_ms,
                        "pressure_ms": pressure_ms,
                        "input_sha256": code_input_sha,
                        "output_sha256": output_sha,
                    }
                )

    result = {
        "status": "PASS",
        "pressure_contract": pressure_contract,
        "capacity_census": census,
        "capacity_tensor_details": census_details,
        "native_text_rows": timing_rows,
        "dose_rows": dose_rows,
        "code": {
            "status": "PASS_COMMON_CODE_AUTHORITY_DIRECT_REUSE",
            "token_sha256": TOKEN_SHA,
            "input_sha256": code_input_sha,
            "rows": code_rows,
        },
    }
    (OUT / "NATIVE_RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "text_samples": len(timing_rows), "dose_samples": len(dose_rows), "code_samples": len(code_rows), "capacity_rows": len(census)}, sort_keys=True))


if __name__ == "__main__":
    main()
