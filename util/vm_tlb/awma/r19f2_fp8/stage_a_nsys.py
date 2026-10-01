#!/usr/bin/env python3
"""Single NSYS witness for exact B0/S1/D0 sibling FP8 consumers."""

import hashlib
import json
import os
from pathlib import Path

import torch


ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001/raw")


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def main():
    assert os.environ.get("R19F2_GPU_LOCK_HELD") == "1"
    import transformer_engine.pytorch as te
    from transformer_engine.common import recipe

    authority = json.loads((ROOT / "REAL_MLP_INPUT_WEIGHT_RECEIPT.json").read_text())
    identity = json.loads((ROOT / "SHARED_REP_IDENTITY.json").read_text())
    payload = ROOT / "QWEN25_LAYER0_MLP_REAL_X_GATE_UP_DOWN.pt"
    assert hashlib.sha256(payload.read_bytes()).hexdigest() == authority["payload_sha256"]
    assert identity["mlp_output_bitwise_identical_all_arms"]
    obj = torch.load(payload, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    weights = {role: obj[f"{role}_weight"].to("cuda:0") for role in ("gate", "up")}
    fp8_recipe = recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    layers = {}
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
    cache_pointers = {}
    for role in ("gate", "up"):
        weight_cache = layers[role]._fp8_workspaces["weight"]
        assert tensor_sha(weight_cache._data) == identity["cached_weight_before"][role]["data"]["sha256"]
        assert tensor_sha(weight_cache._scale_inv) == identity["cached_weight_before"][role]["scale_inv"]["sha256"]
        cache_pointers[role] = weight_cache._data.data_ptr()
    shared_quantizer = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )
    q_ready = shared_quantizer(x)
    torch.cuda.synchronize()
    assert tensor_sha(q_ready._data) == identity["shared_input"]["data"]["sha256"]
    assert tensor_sha(q_ready._scale_inv) == identity["shared_input"]["scale_inv"]["sha256"]
    expected_gate = identity["output_ids"]["B0_DUPLICATE"]["gate"]["sha256"]
    expected_up = identity["output_ids"]["B0_DUPLICATE"]["up"]["sha256"]
    status = []
    for repeat in range(3):
        for arm in ("B0_DUPLICATE", "S1_SHARED", "D0_READY_PAIR"):
            torch.cuda.nvtx.range_push(f"R19F2_{arm}_P")
            with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
                if arm == "B0_DUPLICATE":
                    gate = layers["gate"](x, is_first_microbatch=False)
                    up = layers["up"](x, is_first_microbatch=False)
                else:
                    q = q_ready if arm == "D0_READY_PAIR" else shared_quantizer(x)
                    gate = layers["gate"](q, is_first_microbatch=False)
                    up = layers["up"](q, is_first_microbatch=False)
            torch.cuda.synchronize()
            torch.cuda.nvtx.range_pop()
            assert tensor_sha(gate) == expected_gate
            assert tensor_sha(up) == expected_up
            for role in ("gate", "up"):
                assert layers[role]._fp8_workspaces["weight"]._data.data_ptr() == cache_pointers[role]
            status.append({"repeat": repeat, "arm": arm, "gate_sha256": expected_gate, "up_sha256": expected_up})
    (ROOT / "NSYS_WITNESS_RECEIPT.json").write_text(json.dumps({"ranges": status, "same_outputs": True}, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"range_count": len(status), "same_outputs": True}, sort_keys=True))


if __name__ == "__main__":
    main()
