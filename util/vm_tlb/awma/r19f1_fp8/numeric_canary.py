#!/usr/bin/env python3
"""R19F1 real-payload representation-matched numeric and D0 admission canary.

All CUDA activity requires the shared campaign flock held by the launcher.
The temporary quantize_impl wrapper is audit-only: it returns TE's unmodified
object and is removed before F0/D0 calls. No timed result uses this wrapper.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import time
from pathlib import Path

import torch
import torch.nn.functional as F


PARENT = Path("/data/c16/awma/r19_fp8_readiness_20261001")
ROOT = Path("/data/c16/awma/r19f1_fp8_numeric_decomposition_20261001")
PAYLOAD = ROOT / "raw/QWEN25_LAYER0_UP_PROJ_REAL_INPUT_WEIGHT.pt"
TE_SOURCE = PARENT / "source/TransformerEngine_v2_19"
EXPECTED_PAYLOAD_SHA = "5ac9e6eb35ec2676926481d563628b80d528dac3dbdbe87bece26d21f4c54b48"
EXPECTED_SOURCE_HEAD = "5e52befd5262c06289106338c308079d6adb391f"
ATOL = 0.0675
RTOL = 0.125


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def tensor_identity(tensor: torch.Tensor) -> dict:
    return {
        "shape": list(tensor.shape),
        "dtype": str(tensor.dtype),
        "bytes": tensor.numel() * tensor.element_size(),
        "sha256": tensor_sha(tensor),
    }


def q_identity(quantized) -> dict:
    data = quantized._data
    scale_inv = quantized._scale_inv
    if data is None or scale_inv is None:
        raise RuntimeError("Required FP8 data or scale_inv is missing")
    return {
        "type": type(quantized).__name__,
        "nominal_dtype": str(getattr(quantized, "dtype", quantized._dtype)),
        "fp8_dtype": str(quantized._fp8_dtype),
        "data": tensor_identity(data),
        "scale_inv": tensor_identity(scale_inv),
        "scale_inv_values": scale_inv.detach().float().cpu().reshape(-1).tolist(),
        "rowwise_usage": bool(quantized._quantizer.rowwise_usage),
        "columnwise_usage": bool(quantized._quantizer.columnwise_usage),
    }


def metrics(lhs: torch.Tensor, rhs: torch.Tensor) -> dict:
    lhs = lhs.detach().float().reshape(-1)
    rhs = rhs.detach().float().reshape(-1)
    assert lhs.numel() == rhs.numel()
    error = (lhs - rhs).abs()
    cpu = error.cpu()
    return {
        "n": lhs.numel(),
        "all_finite": bool(torch.isfinite(lhs).all() and torch.isfinite(rhs).all()),
        "max_abs": float(error.max().item()),
        "mean_abs": float(error.mean().item()),
        "rmse": float(torch.sqrt(torch.mean((lhs - rhs) ** 2)).item()),
        "max_rel_eps1e6": float((error / (rhs.abs() + 1e-6)).max().item()),
        "cosine": float(F.cosine_similarity(lhs, rhs, dim=0).item()),
        "abs_p50": float(torch.quantile(cpu, 0.5).item()),
        "abs_p90": float(torch.quantile(cpu, 0.9).item()),
        "abs_p99": float(torch.quantile(cpu, 0.99).item()),
        "abs_p999": float(torch.quantile(cpu, 0.999).item()),
        "allclose_atol_0p0675_rtol_0p125": bool(torch.allclose(lhs, rhs, atol=ATOL, rtol=RTOL)),
        "bitwise_equal": bool(torch.equal(lhs, rhs)),
    }


def write_tsv(path: Path, comparison: str, row: dict) -> None:
    keys = ["comparison", *row.keys()]
    with path.open("w", encoding="utf-8") as stream:
        stream.write("\t".join(keys) + "\n")
        stream.write("\t".join(str(comparison if key == "comparison" else row[key]) for key in keys) + "\n")


def main() -> None:
    assert os.environ.get("R19F1_GPU_LOCK_HELD") == "1"
    assert file_sha(PAYLOAD) == EXPECTED_PAYLOAD_SHA
    source_head = subprocess.check_output(
        ["git", "-C", str(TE_SOURCE), "rev-parse", "HEAD"], text=True
    ).strip()
    assert source_head == EXPECTED_SOURCE_HEAD
    assert torch.cuda.get_device_capability(0) == (8, 9)
    torch.backends.cuda.matmul.allow_tf32 = False

    import transformer_engine
    import transformer_engine.pytorch as te
    import transformer_engine_torch as tex
    from transformer_engine.common import recipe

    available, reason = te.is_fp8_available(return_reason=True)
    assert available, reason
    obj = torch.load(PAYLOAD, map_location="cpu", weights_only=True)
    x = obj["input"].to("cuda:0")
    w = obj["weight"].to("cuda:0")
    assert tuple(x.shape) == (1, 256, 896)
    assert tuple(w.shape) == (4864, 896)
    assert x.dtype == w.dtype == torch.bfloat16
    fp8_recipe = recipe.Float8CurrentScaling(fp8_format=recipe.Format.E4M3)
    layer = te.Linear(896, 4864, bias=False, params_dtype=torch.bfloat16, device="cuda:0").eval()
    with torch.no_grad():
        layer.weight.copy_(w)
    layer.requires_grad_(False)

    torch.cuda.synchronize()
    first_begin = time.perf_counter()
    with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
        layer(x, is_first_microbatch=True)
    torch.cuda.synchronize()
    first_ms_not_primary = (time.perf_counter() - first_begin) * 1000
    for _ in range(2):
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            layer(x, is_first_microbatch=False)

    qweight = layer._fp8_workspaces.get("weight")
    if qweight is None:
        raise RuntimeError("TE frozen-weight FP8 workspace is missing")
    weight_before = q_identity(qweight)
    weight_ptr_before = qweight._data.data_ptr()

    quantizer_cls = te.Float8CurrentScalingQuantizer
    original_quantize_impl = quantizer_cls.quantize_impl
    captured = []

    def capture_quantize_impl(self, tensor):
        result = original_quantize_impl(self, tensor)
        if tensor.data_ptr() == x.data_ptr() and tensor.numel() == x.numel():
            captured.append(result)
        return result

    quantizer_cls.quantize_impl = capture_quantize_impl
    try:
        with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
            y_online = layer(x, is_first_microbatch=False)
    finally:
        quantizer_cls.quantize_impl = original_quantize_impl
    if len(captured) != 1:
        raise RuntimeError(f"Expected one captured online input representation, got {len(captured)}")
    q_online = captured[0]
    online_id = q_identity(q_online)

    # This is the documented public TE quantizer, with the exact arguments used
    # by current-scaling recipe state and no-gradient module input preparation.
    public_quantizer = te.Float8CurrentScalingQuantizer(
        fp8_dtype=te.DType.kFloat8E4M3,
        device=x.device,
        rowwise=True,
        columnwise=False,
        force_pow_2_scales=False,
    )
    q_ready = public_quantizer(x)
    ready_id = q_identity(q_ready)
    exact_ready_representation = (
        online_id["data"]["sha256"] == ready_id["data"]["sha256"]
        and online_id["scale_inv"]["sha256"] == ready_id["scale_inv"]["sha256"]
        and online_id["fp8_dtype"] == ready_id["fp8_dtype"]
    )

    with torch.no_grad():
        y_b0 = F.linear(x, w)
        x_rep = q_online.dequantize(dtype=torch.float32)
        w_rep = qweight.dequantize(dtype=torch.float32)
        y_r0 = F.linear(x_rep.reshape(-1, 896), w_rep)
    if not exact_ready_representation:
        raise RuntimeError("Public quantizer did not reproduce online FP8 bits and scale")
    # TE's internal Float8TensorStorage is intentionally not a public module
    # input. The public Float8Tensor has bit/scale-identical representation.
    with torch.no_grad(), te.autocast(enabled=True, recipe=fp8_recipe):
        y_f0 = layer(q_ready, is_first_microbatch=False)
        y_d0 = layer(q_ready, is_first_microbatch=False)
    torch.cuda.synchronize()

    weight_after = q_identity(qweight)
    weight_ptr_after = qweight._data.data_ptr()
    weight_stable = weight_before == weight_after and weight_ptr_before == weight_ptr_after
    numerics = metrics(y_f0, y_r0)
    distortion = metrics(y_r0, y_b0)
    old_v1_diagnostic = metrics(y_f0, y_b0)
    online_f0_equal = bool(torch.equal(y_online.float().reshape(-1), y_f0.float().reshape(-1)))
    ready_f0_equal = bool(torch.equal(y_d0.float().reshape(-1), y_f0.float().reshape(-1)))
    all_finite = all(
        bool(torch.isfinite(t).all()) for t in (x, w, x_rep, w_rep, y_b0, y_r0, y_f0, y_online, y_d0)
    )
    numeric_pass = all_finite and numerics["allclose_atol_0p0675_rtol_0p125"]
    d0_qualified = (
        numeric_pass and exact_ready_representation and weight_stable
        and online_f0_equal and ready_f0_equal
    )

    objects_path = ROOT / "raw/NUMERICAL_OBJECTS.pt"
    torch.save(
        {
            "B0_ORIGINAL": y_b0.cpu(),
            "R0_REP_MATCHED": y_r0.cpu(),
            "F0_TE_FP8": y_f0.cpu(),
            "A1_ONLINE_CANARY": y_online.cpu(),
            "D0_READY_CANARY": y_d0.cpu(),
            "input_fp8_data": q_online._data.cpu(),
            "input_scale_inv": q_online._scale_inv.cpu(),
            "weight_fp8_data": qweight._data.cpu(),
            "weight_scale_inv": qweight._scale_inv.cpu(),
            "input_dequantized_fp32": x_rep.cpu(),
            "weight_dequantized_fp32": w_rep.cpu(),
        },
        objects_path,
    )

    receipt = {
        "stage": "AWMA_R19F1_FP8_NUMERIC_DECOMPOSITION_109_V1",
        "source_commit": source_head,
        "scientific_parent": "63de02aa82587680baca665d09101dc8c67222a2",
        "payload_sha256": file_sha(PAYLOAD),
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "TE_version": transformer_engine.__version__,
        "SM": list(torch.cuda.get_device_capability(0)),
        "cublasLt_version": int(tex.get_cublasLt_version()),
        "fp8_available": available,
        "recipe": "Float8CurrentScaling(E4M3, use_power_2_scales=False)",
        "reference": "FP32 torch.nn.functional.linear(dequantized exact TE input and cached weight), allow_tf32=False",
        "numeric_contract": {"atol": ATOL, "rtol": RTOL, "source": "TE v2.19 tests/pytorch/utils.py quantization_tols(fp8_current_scaling)"},
        "first_call_ms_not_primary": first_ms_not_primary,
        "online_input_representation": online_id,
        "public_ready_input_representation": ready_id,
        "cached_weight_representation": weight_before,
        "weight_cache_data_ptr_unchanged": weight_ptr_before == weight_ptr_after,
        "cached_weight_bits_and_metadata_unchanged": weight_stable,
        "public_ready_input_bit_and_scale_match": exact_ready_representation,
        "online_and_F0_bitwise_equal": online_f0_equal,
        "D0_and_F0_bitwise_equal": ready_f0_equal,
        "B0_ORIGINAL": tensor_identity(y_b0),
        "R0_REP_MATCHED": tensor_identity(y_r0),
        "F0_TE_FP8": tensor_identity(y_f0),
        "input_dequantized_fp32": tensor_identity(x_rep),
        "weight_dequantized_fp32": tensor_identity(w_rep),
        "representation_matched_numerics": numerics,
        "representation_distortion": distortion,
        "historical_B0_vs_F0_diagnostic_not_regating_V1": old_v1_diagnostic,
        "all_finite": all_finite,
        "rep_matched_numeric_gate_pass": numeric_pass,
        "D0_preliminary_exact_safe_qualified": d0_qualified,
        "numerical_objects_path": str(objects_path),
        "numerical_objects_sha256": file_sha(objects_path),
    }
    path = ROOT / "raw/REPRESENTATION_RECEIPT.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    write_tsv(ROOT / "raw/REP_MATCHED_NUMERICS.tsv", "F0_TE_FP8_vs_R0_REP_MATCHED", numerics)
    write_tsv(ROOT / "raw/REPRESENTATION_DISTORTION.tsv", "R0_REP_MATCHED_vs_B0_ORIGINAL", distortion)
    print(json.dumps({
        "rep_matched_numeric_gate_pass": numeric_pass,
        "D0_preliminary_exact_safe_qualified": d0_qualified,
        "consumer_max_abs": numerics["max_abs"],
        "consumer_mean_abs": numerics["mean_abs"],
        "distortion_max_abs": distortion["max_abs"],
        "distortion_mean_abs": distortion["mean_abs"],
        "public_ready_input_bit_and_scale_match": exact_ready_representation,
        "weight_cache_stable": weight_stable,
    }, sort_keys=True))
    if not numeric_pass:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
