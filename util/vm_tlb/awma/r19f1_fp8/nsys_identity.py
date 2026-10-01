#!/usr/bin/env python3
"""Single bounded NSYS witness for the R19F1 same-consumer FP8 pair."""

import hashlib
import json
import os
from pathlib import Path

import torch


ROOT = Path("/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001")
PARENT = Path("/data/c16/awma/r19_fp8_readiness_20261001")


def sha_tensor(tensor):
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def main():
    assert os.environ.get("R19F1_GPU_LOCK_HELD") == "1"
    import transformer_engine.pytorch as te
    from transformer_engine.common import recipe

    receipt = json.loads((ROOT / "raw/REPRESENTATION_RECEIPT.json").read_text())
    assert receipt["rep_matched_numeric_gate_pass"]
    assert receipt["D0_preliminary_exact_safe_qualified"]
    payload = ROOT / "raw/QWEN25_LAYER0_UP_PROJ_REAL_INPUT_WEIGHT.pt"
    expected_payload = receipt["payload_sha256"]
    assert hashlib.sha256(payload.read_bytes()).hexdigest() == expected_payload
    obj = torch.load(payload, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    w = obj["weight"].to("cuda:0")
    fp8_recipe = recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    layer = te.Linear(896, 4864, bias=False, params_dtype=torch.bfloat16, device="cuda:0").eval()
    with torch.no_grad():
        layer.weight.copy_(w)
    layer.requires_grad_(False)
    with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
        layer(x, is_first_microbatch=True)
        layer(x, is_first_microbatch=False)
    torch.cuda.synchronize()
    cached = layer._fp8_workspaces["weight"]
    assert sha_tensor(cached._data) == receipt["cached_weight_representation"]["data"]["sha256"]
    assert sha_tensor(cached._scale_inv) == receipt["cached_weight_representation"]["scale_inv"]["sha256"]
    cache_ptr = cached._data.data_ptr()

    q = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )(x)
    assert sha_tensor(q._data) == receipt["online_input_representation"]["data"]["sha256"]
    assert sha_tensor(q._scale_inv) == receipt["online_input_representation"]["scale_inv"]["sha256"]
    summary = {"pairs": [], "input_q_data_sha256": sha_tensor(q._data), "weight_q_data_sha256": sha_tensor(cached._data)}
    for i in range(3):
        torch.cuda.nvtx.range_push("R19F1_A1_ONLINE")
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            a = layer(x, is_first_microbatch=False)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()

        torch.cuda.nvtx.range_push("R19F1_D0_READY")
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            d = layer(q, is_first_microbatch=False)
        torch.cuda.synchronize()
        torch.cuda.nvtx.range_pop()
        assert torch.equal(a, d)
        assert cached._data.data_ptr() == cache_ptr
        summary["pairs"].append({"index": i, "online_output_sha256": sha_tensor(a), "ready_output_sha256": sha_tensor(d)})
    (ROOT / "raw/NSYS_WITNESS_RECEIPT.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
