#!/usr/bin/env python3
"""Shared helpers for the bounded CCE dC zero-init counterfactual."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

import torch
from cut_cross_entropy import linear_cross_entropy
from cut_cross_entropy import tl_autotune
from safetensors import safe_open


ATOL = 1e-2
RTOL = 1e-2
PARENT_ROOT = Path("/data/c16/awma/exact_loss_cce_liger_109_v1_20260930")
MODEL_ROOT = Path(
    "/data/c16/models/.incoming/qwen2p5_0p5b_instruct/"
    "7ae557604adf67be50417f59c2c2f167def9a775"
)
REAL_SHAPE = (255, 896, 151936)
ACCEPTED_ZERO_FILL_MS = 0.751779


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    cpu = tensor.detach().contiguous().cpu()
    array = cpu.view(torch.uint8).numpy()
    digest = hashlib.sha256()
    digest.update(memoryview(array))
    return digest.hexdigest()


def tensor_bytes(tensor: torch.Tensor) -> int:
    return tensor.numel() * tensor.element_size()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def fixed_meta() -> dict[str, object]:
    config = tl_autotune._cce_best_config()
    values = dict(config.all_kwargs())
    expected = {
        "BLOCK_B": 128,
        "BLOCK_V": 128,
        "BLOCK_D": 32,
        "num_warps": 4,
        "num_stages": 4,
    }
    observed_relevant = {key: values[key] for key in expected}
    if observed_relevant != expected:
        raise RuntimeError(f"fixed CCE meta mismatch: {observed_relevant} != {expected}")
    if tl_autotune._AUTOTUNE:
        raise RuntimeError("CCE autotuning is enabled")
    if os.environ.get("CCE_AUTOTUNE", "0") != "0":
        raise RuntimeError("CCE_AUTOTUNE environment is not frozen off")
    return {
        **values,
        "MM_BACK_BLOCK_D": 64,
        "CCE_AUTOTUNE": 0,
        "source": "tl_autotune._cce_best_config with BF16 E",
    }


def set_arm(arm: str) -> None:
    if arm == "C0":
        os.environ["CCE_DC_FIRST_STORE"] = "0"
    elif arm == "C1":
        os.environ["CCE_DC_FIRST_STORE"] = "1"
    else:
        raise ValueError(arm)


def make_leaves(hidden: torch.Tensor, weight: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    return (
        hidden.detach().clone().requires_grad_(True),
        weight.detach().clone().requires_grad_(True),
    )


def backward_on_leaves(
    arm: str,
    hidden: torch.Tensor,
    weight: torch.Tensor,
    labels: torch.Tensor,
    reduction: str = "mean",
) -> torch.Tensor:
    loss = linear_cross_entropy(
        hidden,
        weight,
        labels,
        ignore_index=-100,
        softcap=None,
        reduction=reduction,
        shift=0,
        filter_eps=None,
        accum_e_fp32=True,
        accum_c_fp32=True,
        filter_e_grad=False,
        filter_c_grad=False,
        impl="cce_exact",
    )
    loss.backward()
    if hidden.grad is None or weight.grad is None:
        raise RuntimeError(f"{arm} failed the full-gradient contract")
    return loss


def forward_backward(
    arm: str,
    base_hidden: torch.Tensor,
    base_weight: torch.Tensor,
    labels: torch.Tensor,
    reduction: str = "mean",
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    set_arm(arm)
    hidden, weight = make_leaves(base_hidden, base_weight)
    loss = backward_on_leaves(arm, hidden, weight, labels, reduction)
    return loss, hidden.grad, weight.grad


def scalar_metrics(got: torch.Tensor, ref: torch.Tensor) -> dict[str, object]:
    gv = float(got.detach().float().cpu())
    rv = float(ref.detach().float().cpu())
    if math.isnan(gv) and math.isnan(rv):
        return {
            "observed": gv,
            "reference": rv,
            "both_nan": True,
            "finite": False,
            "max_abs": 0.0,
            "mean_abs": 0.0,
            "max_rel": 0.0,
            "cosine_similarity": 1.0,
            "allclose": True,
        }
    absolute = abs(gv - rv)
    relative = absolute / max(abs(rv), 1e-30)
    return {
        "observed": gv,
        "reference": rv,
        "both_nan": False,
        "finite": math.isfinite(gv),
        "max_abs": absolute,
        "mean_abs": absolute,
        "max_rel": relative,
        "cosine_similarity": 1.0 if gv == rv else float(math.copysign(1.0, gv * rv)),
        "allclose": absolute <= ATOL + RTOL * abs(rv),
    }


def tensor_metrics(got: torch.Tensor, ref: torch.Tensor, chunk: int = 1 << 20) -> dict[str, object]:
    if got.shape != ref.shape or got.dtype != ref.dtype:
        return {
            "shape_match": got.shape == ref.shape,
            "dtype_match": got.dtype == ref.dtype,
            "allclose": False,
            "finite": False,
        }
    lhs_flat = got.detach().reshape(-1)
    rhs_flat = ref.detach().reshape(-1)
    max_abs = 0.0
    max_rel = 0.0
    sum_abs = 0.0
    dot = 0.0
    lhs_norm = 0.0
    rhs_norm = 0.0
    allclose = True
    finite = True
    for start in range(0, lhs_flat.numel(), chunk):
        stop = min(start + chunk, lhs_flat.numel())
        lhs = lhs_flat[start:stop].float()
        rhs = rhs_flat[start:stop].float()
        diff = (lhs - rhs).abs()
        max_abs = max(max_abs, float(diff.max().cpu()))
        max_rel = max(max_rel, float((diff / rhs.abs().clamp_min(1e-30)).max().cpu()))
        sum_abs += float(diff.sum(dtype=torch.float64).cpu())
        lhs64 = lhs.double()
        rhs64 = rhs.double()
        dot += float((lhs64 * rhs64).sum().cpu())
        lhs_norm += float((lhs64 * lhs64).sum().cpu())
        rhs_norm += float((rhs64 * rhs64).sum().cpu())
        allclose = allclose and bool((diff <= ATOL + RTOL * rhs.abs()).all().cpu())
        finite = finite and bool(torch.isfinite(lhs).all().cpu())
    cosine = dot / math.sqrt(lhs_norm * rhs_norm) if lhs_norm and rhs_norm else 1.0
    return {
        "shape": list(got.shape),
        "dtype": str(got.dtype),
        "numel": got.numel(),
        "max_abs": max_abs,
        "mean_abs": sum_abs / lhs_flat.numel(),
        "max_rel": max_rel,
        "cosine_similarity": cosine,
        "allclose": allclose,
        "finite": finite,
        "shape_match": True,
        "dtype_match": True,
    }


def compare_outputs(
    candidate: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    reference: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
) -> dict[str, dict[str, object]]:
    loss, grad_hidden, grad_weight = candidate
    ref_loss, ref_hidden, ref_weight = reference
    return {
        "loss": scalar_metrics(loss, ref_loss),
        "grad_hidden": tensor_metrics(grad_hidden, ref_hidden),
        "grad_weight": tensor_metrics(grad_weight, ref_weight),
    }


def qualified(metrics: dict[str, dict[str, object]]) -> bool:
    return all(bool(metrics[name].get("allclose", False)) for name in metrics)


def load_real_inputs() -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[str, object]]:
    runtime = json.loads((PARENT_ROOT / "raw" / "RUNTIME_INPUT_RECEIPT.json").read_text())
    snapshot_path = PARENT_ROOT / "raw" / "REAL_FINAL_HIDDEN_AND_LABELS.pt"
    if sha_file(snapshot_path) != runtime["snapshot_sha256"]:
        raise RuntimeError("accepted hidden snapshot file hash mismatch")
    snapshot = torch.load(snapshot_path, map_location="cpu", weights_only=True)
    hidden = snapshot["hidden"]
    labels = snapshot["labels"]
    if tensor_sha(hidden) != runtime["hidden_sha256"]:
        raise RuntimeError("accepted hidden tensor hash mismatch")
    if tensor_sha(labels) != runtime["labels_sha256"]:
        raise RuntimeError("accepted labels tensor hash mismatch")
    with safe_open(MODEL_ROOT / "model.safetensors", framework="pt", device="cpu") as source:
        weight = source.get_tensor(runtime["checkpoint_tensor_key"])
    if tensor_sha(weight) != runtime["lm_head_sha256"]:
        raise RuntimeError("accepted lm_head tensor hash mismatch")
    hidden = hidden.to("cuda:0")
    labels = labels.to("cuda:0")
    weight = weight.to("cuda:0")
    if tuple(hidden.shape) != REAL_SHAPE[:2] or tuple(weight.shape) != (REAL_SHAPE[2], REAL_SHAPE[1]):
        raise RuntimeError(f"real shape mismatch hidden={hidden.shape} weight={weight.shape}")
    receipt = {
        "parent_runtime_receipt": str(PARENT_ROOT / "raw" / "RUNTIME_INPUT_RECEIPT.json"),
        "snapshot_sha256": runtime["snapshot_sha256"],
        "hidden_sha256": runtime["hidden_sha256"],
        "labels_sha256": runtime["labels_sha256"],
        "lm_head_sha256": runtime["lm_head_sha256"],
        "hidden_shape": list(hidden.shape),
        "weight_shape": list(weight.shape),
        "labels_shape": list(labels.shape),
        "storage_dtype": str(hidden.dtype),
    }
    return hidden, weight, labels, receipt


def init_state_accounting(vocab: int, hidden: int) -> dict[str, int]:
    lock_rows = math.ceil(vocab / 128)
    lock_cols = math.ceil(hidden / 64)
    elements = lock_rows * lock_cols
    return {
        "lock_rows": lock_rows,
        "lock_cols": lock_cols,
        "elements": elements,
        "bytes": elements * 4,
        "additional_bytes_vs_c0": 0,
        "full_dc_fp32_bytes": vocab * hidden * 4,
    }
