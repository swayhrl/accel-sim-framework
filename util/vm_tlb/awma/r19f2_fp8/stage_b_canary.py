#!/usr/bin/env python3
"""Bounded exact one-launch fused current-scaling admission on frozen real X."""

import csv
import hashlib
import json
import os
from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.cpp_extension import load


ROOT = Path("/data/c16/awma/r19f2_fp8_software_counterfactual_20261001")
RAW = ROOT / "raw"
SOURCE = Path("/home/huangrulin/workspace/worktrees/accel-sim-awma-r19f2-fp8-software-counterfactual-109-v1/util/vm_tlb/awma/r19f2_fp8")
BUILD = ROOT / "build/fused_cs_v1"


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(tensor):
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def main():
    assert os.environ.get("R19F2_GPU_LOCK_HELD") == "1"
    import transformer_engine.pytorch as te
    from transformer_engine.common import recipe

    source_cpp = SOURCE / "fused_current_scale.cpp"
    source_cu = SOURCE / "fused_current_scale.cu"
    assert source_cpp.is_file() and source_cu.is_file()
    BUILD.mkdir(parents=True, exist_ok=True)
    extension = load(
        name="r19f2_fused_cs_v1",
        sources=[str(source_cpp), str(source_cu)],
        build_directory=str(BUILD),
        extra_cflags=["-O3"],
        extra_cuda_cflags=["-O3", "--expt-relaxed-constexpr", "-arch=sm_89"],
        verbose=True,
    )
    shared = json.loads((RAW / "SHARED_REP_IDENTITY.json").read_text())
    authority = json.loads((RAW / "REAL_MLP_INPUT_WEIGHT_RECEIPT.json").read_text())
    payload = RAW / "QWEN25_LAYER0_MLP_REAL_X_GATE_UP_DOWN.pt"
    assert file_sha(payload) == authority["payload_sha256"]
    obj = torch.load(payload, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    weights = {role: obj[f"{role}_weight"].to("cuda:0") for role in ("gate", "up", "down")}
    assert torch.cuda.get_device_capability(0) == (8, 9)
    props = torch.cuda.get_device_properties(0)
    blocks = props.multi_processor_count
    assert blocks > 0
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
        assert tensor_sha(layer._fp8_workspaces["weight"]._data) == shared["cached_weight_before"][role]["data"]["sha256"]
        assert tensor_sha(layer._fp8_workspaces["weight"]._scale_inv) == shared["cached_weight_before"][role]["scale_inv"]["sha256"]
    torch.cuda.synchronize()
    cache_ptrs = {role: layers[role]._fp8_workspaces["weight"]._data.data_ptr() for role in layers}

    quantizer = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )
    q_ref = quantizer(x)
    q_data = torch.empty(x.shape, dtype=torch.uint8, device=x.device)
    q_fused = quantizer.create_tensor_from_data(q_data, fake_dtype=torch.bfloat16, internal=False)
    amax = torch.empty((1,), dtype=torch.float32, device=x.device)
    assert type(q_fused).__name__ == "Float8Tensor"
    assert tensor_sha(q_ref._data) == shared["shared_input"]["data"]["sha256"]
    assert tensor_sha(q_ref._scale_inv) == shared["shared_input"]["scale_inv"]["sha256"]

    extension.fused_current_scale_(x, q_fused._data, q_fused._scale_inv, amax, blocks)
    torch.cuda.synchronize()
    data_sha = tensor_sha(q_fused._data)
    scale_sha = tensor_sha(q_fused._scale_inv)
    exact_data = data_sha == shared["shared_input"]["data"]["sha256"]
    exact_scale = scale_sha == shared["shared_input"]["scale_inv"]["sha256"]
    if not (exact_data and exact_scale):
        failure = {
            "stage": "AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1",
            "status": "EXACT_FUSED_REPRESENTATION_FAILED",
            "fused_fp8_data_sha256": data_sha,
            "te_fp8_data_sha256": shared["shared_input"]["data"]["sha256"],
            "fused_inverse_scale_sha256": scale_sha,
            "te_inverse_scale_sha256": shared["shared_input"]["scale_inv"]["sha256"],
            "fused_inverse_scale_value": q_fused._scale_inv.detach().float().cpu().tolist(),
            "te_inverse_scale_value": q_ref._scale_inv.detach().float().cpu().tolist(),
            "amax_value": amax.detach().float().cpu().tolist(),
            "extension_path": str(Path(extension.__file__).resolve()),
        }
        (RAW / "FUSED_REP_IDENTITY.json").write_text(json.dumps(failure, indent=2, sort_keys=True) + "\n")
        print(json.dumps(failure, sort_keys=True))
        raise SystemExit(2)

    outputs = {}
    for arm, q in (("S1_SHARED", q_ref), ("S2_FUSED_SHARED", q_fused)):
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            gate = layers["gate"](q, is_first_microbatch=False)
            up = layers["up"](q, is_first_microbatch=False)
        mlp = F.linear(F.silu(gate) * up, weights["down"])
        torch.cuda.synchronize()
        outputs[arm] = {"gate": tensor_sha(gate), "up": tensor_sha(up), "mlp": tensor_sha(mlp)}
        assert torch.isfinite(gate).all() and torch.isfinite(up).all() and torch.isfinite(mlp).all()
    expected = {key: shared["output_ids"]["B0_DUPLICATE"][key]["sha256"] for key in ("gate", "up", "mlp")}
    exact_outputs = outputs["S1_SHARED"] == outputs["S2_FUSED_SHARED"] == expected
    stable_weights = all(
        layers[role]._fp8_workspaces["weight"]._data.data_ptr() == cache_ptrs[role]
        and tensor_sha(layers[role]._fp8_workspaces["weight"]._data) == shared["cached_weight_before"][role]["data"]["sha256"]
        and tensor_sha(layers[role]._fp8_workspaces["weight"]._scale_inv) == shared["cached_weight_before"][role]["scale_inv"]["sha256"]
        for role in layers
    )
    assert exact_outputs and stable_weights
    so_path = Path(extension.__file__).resolve()
    receipt = {
        "stage": "AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1",
        "status": "EXACT_ONE_LAUNCH_FUSED_REP_QUALIFIED",
        "input_payload_sha256": authority["payload_sha256"],
        "source_cpp_sha256": file_sha(source_cpp),
        "source_cu_sha256": file_sha(source_cu),
        "extension_so_path": str(so_path),
        "extension_so_sha256": file_sha(so_path),
        "cooperative_blocks": blocks,
        "threads_per_block": 256,
        "amax_value": amax.detach().float().cpu().tolist(),
        "fp8_data_sha256": data_sha,
        "inverse_scale_sha256": scale_sha,
        "inverse_scale_value": q_fused._scale_inv.detach().float().cpu().tolist(),
        "te_fp8_data_sha256": shared["shared_input"]["data"]["sha256"],
        "te_inverse_scale_sha256": shared["shared_input"]["scale_inv"]["sha256"],
        "fp8_bits_and_inverse_scale_exact": exact_data and exact_scale,
        "outputs": outputs,
        "gate_up_mlp_outputs_bitwise_equal": exact_outputs,
        "cached_weight_bits_scales_pointer_stable": stable_weights,
        "consumer": "unchanged TE v2.19 te.Linear with accepted cached FP8 gate/up weights",
        "one_launch_source_identity": "fused_current_scale_ calls exactly one cudaLaunchCooperativeKernel",
    }
    (RAW / "FUSED_REP_IDENTITY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    with (RAW / "STAGE_B_NUMERICAL_IDENTITY.tsv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, delimiter="\t", lineterminator="\n")
        writer.writerow(("arm", "fp8_data_sha256", "inverse_scale_sha256", "gate_output_sha256", "up_output_sha256", "mlp_output_sha256"))
        for arm in ("S1_SHARED", "S2_FUSED_SHARED"):
            writer.writerow((arm, data_sha, scale_sha, outputs[arm]["gate"], outputs[arm]["up"], outputs[arm]["mlp"]))
    print(json.dumps({"status": receipt["status"], "fp8_bits_and_inverse_scale_exact": True, "outputs_bitwise_equal": True, "extension_so_sha256": receipt["extension_so_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
