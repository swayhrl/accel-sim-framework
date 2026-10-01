#!/usr/bin/env python3
"""Un-timed Stage A exact gate/up shared-representation admission canary."""

import csv
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import torch
import torch.nn.functional as F


ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/raw")
PAYLOAD = ROOT / "QWEN25_LAYER0_MLP_REAL_X_GATE_UP_DOWN.pt"
TE_SOURCE = Path("/data/c16/awma/r19_fp8_readiness_20261001/source/TransformerEngine_v2_19")
TE_HEAD = "5e52befd5262c06289106338c308079d6adb391f"
PARENT_Q_INPUT = "79c754c1ec58ac3e5338e3bab28887a56803d0139394fe5a93c35df74e33ee15"
PARENT_Q_SCALE = "e40242473eecf057b7426f890b25b6645e7c8d6f570596591ec2b150598c8734"
PARENT_Q_UP_WEIGHT = "bac0aac613572052c949f3ec9719ce95520185233c0c2253a82af0181a8457dd"


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def tensor_id(tensor):
    return {"shape": list(tensor.shape), "dtype": str(tensor.dtype), "bytes": tensor.numel() * tensor.element_size(), "sha256": tensor_sha(tensor)}


def fp8_id(tensor):
    return {
        "type": type(tensor).__name__,
        "fp8_dtype": str(tensor._fp8_dtype),
        "nominal_dtype": str(getattr(tensor, "dtype", tensor._dtype)),
        "data": tensor_id(tensor._data),
        "scale_inv": tensor_id(tensor._scale_inv),
        "scale_inv_values": tensor._scale_inv.detach().float().cpu().reshape(-1).tolist(),
        "device_data_ptr": int(tensor._data.data_ptr()),
    }


def same_rep(a, b):
    return (
        a["fp8_dtype"] == b["fp8_dtype"]
        and a["data"]["sha256"] == b["data"]["sha256"]
        and a["scale_inv"]["sha256"] == b["scale_inv"]["sha256"]
    )


def main():
    assert os.environ.get("R19F2_GPU_LOCK_HELD") == "1"
    source_head = subprocess.check_output(["git", "-C", str(TE_SOURCE), "rev-parse", "HEAD"], text=True).strip()
    assert source_head == TE_HEAD
    authority = json.loads((ROOT / "REAL_MLP_INPUT_WEIGHT_RECEIPT.json").read_text())
    assert file_sha(PAYLOAD) == authority["payload_sha256"]
    import transformer_engine
    import transformer_engine.pytorch as te
    import transformer_engine_torch as tex
    from transformer_engine.common import recipe

    assert torch.cuda.get_device_capability(0) == (8, 9)
    available, reason = te.is_fp8_available(return_reason=True)
    assert available, reason
    obj = torch.load(PAYLOAD, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    weights = {role: obj[f"{role}_weight"].to("cuda:0") for role in ("gate", "up", "down")}
    for role in ("gate", "up"):
        assert tuple(weights[role].shape) == (4864, 896)
    assert tuple(weights["down"].shape) == (896, 4864)
    assert tensor_sha(x) == authority["input"]["sha256"]
    for role in weights:
        assert tensor_sha(weights[role]) == authority[f"{role}_weight"]["sha256"]

    fp8_recipe = recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    layers = {}
    start = time.perf_counter()
    for role in ("gate", "up"):
        layer = te.Linear(896, 4864, bias=False, params_dtype=torch.bfloat16, device="cuda:0").eval()
        with torch.no_grad():
            layer.weight.copy_(weights[role])
        layer.requires_grad_(False)
        layers[role] = layer
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            layer(x, is_first_microbatch=True)
            layer(x, is_first_microbatch=False)
    torch.cuda.synchronize()
    first_call_and_cache_ms_not_primary = (time.perf_counter() - start) * 1000
    cached_before = {role: fp8_id(layers[role]._fp8_workspaces["weight"]) for role in layers}
    assert cached_before["up"]["data"]["sha256"] == PARENT_Q_UP_WEIGHT

    cls = te.Float8CurrentScalingQuantizer
    original = cls.quantize_impl
    captured = []

    def audit_quantize(self, tensor):
        result = original(self, tensor)
        if tensor.data_ptr() == x.data_ptr() and tensor.numel() == x.numel():
            captured.append(result)
        return result

    online_output = {}
    online_input = {}
    cls.quantize_impl = audit_quantize
    try:
        for role in ("gate", "up"):
            captured.clear()
            with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
                online_output[role] = layers[role](x, is_first_microbatch=False)
            if len(captured) != 1:
                raise RuntimeError(f"Expected exactly one {role} online input quantization, got {len(captured)}")
            online_input[role] = fp8_id(captured[0])
    finally:
        cls.quantize_impl = original
    if not same_rep(online_input["gate"], online_input["up"]):
        raise RuntimeError("Gate and up normal online input FP8 representations differ")
    if online_input["up"]["data"]["sha256"] != PARENT_Q_INPUT or online_input["up"]["scale_inv"]["sha256"] != PARENT_Q_SCALE:
        raise RuntimeError("R19F2 online representation differs from frozen R19F1")

    q_shared = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )(x)
    shared_id = fp8_id(q_shared)
    if not all(same_rep(shared_id, online_input[role]) for role in ("gate", "up")):
        raise RuntimeError("Public shared input FP8 representation differs from normal gate/up")
    shared_output = {}
    ready_output = {}
    for role in ("gate", "up"):
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            shared_output[role] = layers[role](q_shared, is_first_microbatch=False)
            ready_output[role] = layers[role](q_shared, is_first_microbatch=False)
    torch.cuda.synchronize()

    def mlp_output(outputs):
        hidden = F.silu(outputs["gate"]) * outputs["up"]
        return F.linear(hidden, weights["down"])

    mlp = {"B0_DUPLICATE": mlp_output(online_output), "S1_SHARED": mlp_output(shared_output), "D0_READY_PAIR": mlp_output(ready_output)}
    torch.cuda.synchronize()
    all_finite = all(bool(torch.isfinite(t).all()) for group in (online_output, shared_output, ready_output) for t in group.values()) and all(bool(torch.isfinite(t).all()) for t in mlp.values())
    gate_equal = torch.equal(online_output["gate"], shared_output["gate"]) and torch.equal(shared_output["gate"], ready_output["gate"])
    up_equal = torch.equal(online_output["up"], shared_output["up"]) and torch.equal(shared_output["up"], ready_output["up"])
    mlp_equal = torch.equal(mlp["B0_DUPLICATE"], mlp["S1_SHARED"]) and torch.equal(mlp["S1_SHARED"], mlp["D0_READY_PAIR"])
    cached_after = {role: fp8_id(layers[role]._fp8_workspaces["weight"]) for role in layers}
    cached_stable = {role: cached_before[role] == cached_after[role] for role in layers}
    assert all_finite and gate_equal and up_equal and mlp_equal and all(cached_stable.values())

    output_ids = {
        arm: {
            "gate": tensor_id(outputs["gate"]),
            "up": tensor_id(outputs["up"]),
            "mlp": tensor_id(mlp[arm]),
        }
        for arm, outputs in (
            ("B0_DUPLICATE", online_output),
            ("S1_SHARED", shared_output),
            ("D0_READY_PAIR", ready_output),
        )
    }
    frozen_objects = ROOT / "STAGE_A_NUMERICAL_OBJECTS.pt"
    torch.save(
        {
            "shared_fp8_input_data": q_shared._data.cpu(),
            "shared_fp8_input_scale_inv": q_shared._scale_inv.cpu(),
            "gate_fp8_weight_data": layers["gate"]._fp8_workspaces["weight"]._data.cpu(),
            "gate_fp8_weight_scale_inv": layers["gate"]._fp8_workspaces["weight"]._scale_inv.cpu(),
            "up_fp8_weight_data": layers["up"]._fp8_workspaces["weight"]._data.cpu(),
            "up_fp8_weight_scale_inv": layers["up"]._fp8_workspaces["weight"]._scale_inv.cpu(),
            "gate_output": online_output["gate"].cpu(),
            "up_output": online_output["up"].cpu(),
            "mlp_output": mlp["B0_DUPLICATE"].cpu(),
        },
        frozen_objects,
    )
    receipt = {
        "stage": "AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1",
        "source_commit": source_head,
        "TE_version": transformer_engine.__version__,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "device_capability": list(torch.cuda.get_device_capability(0)),
        "cublasLt_version": int(tex.get_cublasLt_version()),
        "recipe": "Float8CurrentScaling(E4M3,use_power_2_scales=False)",
        "mlp_payload_sha256": file_sha(PAYLOAD),
        "first_call_and_weight_cache_ms_not_primary": first_call_and_cache_ms_not_primary,
        "online_input": online_input,
        "shared_input": shared_id,
        "gate_and_up_online_input_representation_identical": True,
        "shared_representation_identical_to_both_online": True,
        "cached_weight_before": cached_before,
        "cached_weight_after": cached_after,
        "cached_weight_bits_scale_pointer_stable": cached_stable,
        "output_ids": output_ids,
        "gate_output_bitwise_identical_all_arms": gate_equal,
        "up_output_bitwise_identical_all_arms": up_equal,
        "mlp_output_bitwise_identical_all_arms": mlp_equal,
        "all_finite": all_finite,
        "downstream_formula": "F.linear(F.silu(gate)*up,real_BF16_down_weight)",
        "logical_input_quantizer_invocations_per_arm": {"B0_DUPLICATE": 2, "S1_SHARED": 1, "D0_READY_PAIR": 0},
        "frozen_numerical_objects_sha256": file_sha(frozen_objects),
    }
    (ROOT / "SHARED_REP_IDENTITY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    with (ROOT / "NUMERICAL_IDENTITY.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("arm", "gate_sha256", "up_sha256", "mlp_sha256", "finite"))
        for arm in ("B0_DUPLICATE", "S1_SHARED", "D0_READY_PAIR"):
            ids = output_ids[arm]
            writer.writerow((arm, ids["gate"]["sha256"], ids["up"]["sha256"], ids["mlp"]["sha256"], all_finite))
    print(json.dumps({
        "shared_input_q_sha": shared_id["data"]["sha256"],
        "gate_cached_weight_q_sha": cached_before["gate"]["data"]["sha256"],
        "up_cached_weight_q_sha": cached_before["up"]["data"]["sha256"],
        "gate_output_sha": output_ids["B0_DUPLICATE"]["gate"]["sha256"],
        "up_output_sha": output_ids["B0_DUPLICATE"]["up"]["sha256"],
        "mlp_output_sha": output_ids["B0_DUPLICATE"]["mlp"]["sha256"],
        "all_exact_identity_gates_pass": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
