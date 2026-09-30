#!/usr/bin/env python3
"""Locked GPU campaign for the Round16 CCE/Liger exact-loss side lane."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import json
import math
import os
import statistics
import time
import traceback
from contextlib import nullcontext
from pathlib import Path

import torch
import torch.nn.functional as F
import transformers
import triton
from cut_cross_entropy import linear_cross_entropy
from liger_kernel.backends import available_impls, get_impl
from liger_kernel.transformers import LigerFusedLinearCrossEntropyLoss
from safetensors import safe_open
from transformers import AutoModelForCausalLM


ATOL = 1e-2
RTOL = 1e-2
ARMS = ("B0", "B1", "B2")
ARM_NAMES = {
    "B0": "PYTORCH_MATERIALIZED_LOGITS",
    "B1": "CCE_EXACT_NO_FILTER",
    "B2": "LIGER_FUSED_LINEAR_CE_TRITON_ADA",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


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


def make_leaves(hidden: torch.Tensor, weight: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    return (
        hidden.detach().clone().requires_grad_(True),
        weight.detach().clone().requires_grad_(True),
    )


def make_liger() -> LigerFusedLinearCrossEntropyLoss:
    return LigerFusedLinearCrossEntropyLoss(
        ignore_index=-100,
        lse_square_scale=0.0,
        label_smoothing=0.0,
        reduction="mean",
        softcap=None,
        return_z_loss=False,
        accum_dtype=torch.float32,
    )


def arm_forward(
    arm: str,
    hidden: torch.Tensor,
    weight: torch.Tensor,
    labels: torch.Tensor,
    liger_loss: LigerFusedLinearCrossEntropyLoss,
) -> torch.Tensor:
    if arm == "B0":
        logits = hidden @ weight.T
        return F.cross_entropy(logits.float(), labels, ignore_index=-100, reduction="mean")
    if arm == "B1":
        return linear_cross_entropy(
            hidden,
            weight,
            labels,
            ignore_index=-100,
            softcap=None,
            reduction="mean",
            shift=0,
            filter_eps=None,
            accum_e_fp32=True,
            accum_c_fp32=True,
            filter_e_grad=False,
            filter_c_grad=False,
            impl="cce_exact",
        )
    if arm == "B2":
        return liger_loss(weight, hidden, labels)
    raise ValueError(arm)


def execute(
    arm: str,
    base_hidden: torch.Tensor,
    base_weight: torch.Tensor,
    labels: torch.Tensor,
    liger_loss: LigerFusedLinearCrossEntropyLoss,
    saved_records: list[dict[str, object]] | None = None,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    hidden, weight = make_leaves(base_hidden, base_weight)

    def pack(tensor: torch.Tensor) -> torch.Tensor:
        shape = list(tensor.shape)
        if shape == list(hidden.shape):
            identity = "hidden_or_grad_hidden_shape"
        elif shape == list(weight.shape):
            identity = "lm_head_or_grad_weight_shape"
        elif shape == [hidden.shape[0], weight.shape[0]]:
            identity = "full_TxV_logits_state"
        elif shape == list(labels.shape):
            identity = "labels_or_token_state"
        else:
            identity = "other"
        saved_records.append(
            {
                "shape": shape,
                "dtype": str(tensor.dtype),
                "logical_bytes": tensor_bytes(tensor),
                "identity": identity,
                "requires_grad": bool(tensor.requires_grad),
                "storage_ptr": int(tensor.untyped_storage().data_ptr()),
            }
        )
        return tensor

    hooks = (
        torch.autograd.graph.saved_tensors_hooks(pack, lambda tensor: tensor)
        if saved_records is not None
        else nullcontext()
    )
    with hooks:
        loss = arm_forward(arm, hidden, weight, labels, liger_loss)
        loss.backward()
    if hidden.grad is None or weight.grad is None:
        raise RuntimeError(f"{arm} failed full-gradient contract")
    return loss, hidden, weight, hidden.grad, weight.grad


def scalar_metrics(got: torch.Tensor, ref: torch.Tensor) -> dict[str, object]:
    got_value = float(got.detach().float().cpu())
    ref_value = float(ref.detach().float().cpu())
    absolute = abs(got_value - ref_value)
    relative = absolute / max(abs(ref_value), 1e-30)
    return {
        "reference": ref_value,
        "observed": got_value,
        "max_abs": absolute,
        "mean_abs": absolute,
        "max_rel": relative,
        "cosine_similarity": 1.0 if got_value == ref_value else float(math.copysign(1.0, got_value * ref_value)),
        "allclose": absolute <= ATOL + RTOL * abs(ref_value),
        "finite": math.isfinite(got_value),
    }


def tensor_metrics(got: torch.Tensor, ref: torch.Tensor, chunk: int = 1 << 20) -> dict[str, object]:
    if got.shape != ref.shape or got.dtype != ref.dtype:
        return {
            "shape_match": got.shape == ref.shape,
            "dtype_match": got.dtype == ref.dtype,
            "allclose": False,
        }
    got_flat = got.detach().reshape(-1)
    ref_flat = ref.detach().reshape(-1)
    max_abs = 0.0
    max_rel = 0.0
    sum_abs = 0.0
    dot = 0.0
    norm_got = 0.0
    norm_ref = 0.0
    allclose = True
    finite = True
    for start in range(0, got_flat.numel(), chunk):
        stop = min(start + chunk, got_flat.numel())
        lhs = got_flat[start:stop].float()
        rhs = ref_flat[start:stop].float()
        diff = (lhs - rhs).abs()
        max_abs = max(max_abs, float(diff.max().cpu()))
        max_rel = max(max_rel, float((diff / rhs.abs().clamp_min(1e-30)).max().cpu()))
        sum_abs += float(diff.sum(dtype=torch.float64).cpu())
        dot += float((lhs.double() * rhs.double()).sum().cpu())
        norm_got += float((lhs.double() * lhs.double()).sum().cpu())
        norm_ref += float((rhs.double() * rhs.double()).sum().cpu())
        allclose = allclose and bool((diff <= ATOL + RTOL * rhs.abs()).all().cpu())
        finite = finite and bool(torch.isfinite(lhs).all().cpu())
        del lhs, rhs, diff
    cosine = dot / math.sqrt(norm_got * norm_ref) if norm_got and norm_ref else float("nan")
    return {
        "shape": list(got.shape),
        "dtype": str(got.dtype),
        "numel": got.numel(),
        "max_abs": max_abs,
        "mean_abs": sum_abs / got_flat.numel(),
        "max_rel": max_rel,
        "cosine_similarity": cosine,
        "allclose": allclose,
        "finite": finite,
        "shape_match": True,
        "dtype_match": True,
    }


def capture_real_inputs(
    model_root: Path, tokens: list[int], raw: Path
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, dict[str, object]]:
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    model = AutoModelForCausalLM.from_pretrained(
        model_root,
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
    ).eval().to("cuda:0")
    tied = (
        hasattr(model, "model")
        and hasattr(model.model, "embed_tokens")
        and model.lm_head.weight.data_ptr() == model.model.embed_tokens.weight.data_ptr()
    )
    input_ids = torch.tensor(tokens[:-1], dtype=torch.long, device="cuda:0").unsqueeze(0)
    labels = torch.tensor(tokens[1:], dtype=torch.long, device="cuda:0")
    with torch.no_grad():
        outputs = model.model(input_ids=input_ids, use_cache=False, return_dict=True)
        hidden = outputs.last_hidden_state.squeeze(0).detach().clone().contiguous()
        weight = model.lm_head.weight.detach().clone().contiguous()
    if hidden.shape != (255, 896) or weight.shape != (151936, 896):
        raise ValueError(f"unexpected real shape hidden={hidden.shape} weight={weight.shape}")
    if hidden.dtype != torch.bfloat16 or weight.dtype != torch.bfloat16:
        raise ValueError(f"unexpected dtype hidden={hidden.dtype} weight={weight.dtype}")
    hidden_sha = tensor_sha(hidden)
    weight_sha = tensor_sha(weight)

    checkpoint_key = None
    checkpoint_sha = None
    with safe_open(model_root / "model.safetensors", framework="pt", device="cpu") as source:
        for key in ("lm_head.weight", "model.embed_tokens.weight"):
            if key in source.keys():
                candidate = source.get_tensor(key)
                candidate_sha = tensor_sha(candidate)
                if candidate_sha == weight_sha:
                    checkpoint_key = key
                    checkpoint_sha = candidate_sha
                    break
    if checkpoint_sha != weight_sha:
        raise ValueError("runtime lm_head does not match an exact checkpoint tensor")

    snapshot = raw / "REAL_FINAL_HIDDEN_AND_LABELS.pt"
    torch.save({"hidden": hidden.cpu(), "labels": labels.cpu()}, snapshot)
    receipt = {
        "model_forward": "AutoModelForCausalLM.model(...).last_hidden_state",
        "model_eval": True,
        "use_cache": False,
        "input_shape": list(input_ids.shape),
        "hidden_shape": list(hidden.shape),
        "hidden_dtype": str(hidden.dtype),
        "hidden_sha256": hidden_sha,
        "lm_head_shape": list(weight.shape),
        "lm_head_dtype": str(weight.dtype),
        "lm_head_sha256": weight_sha,
        "checkpoint_tensor_key": checkpoint_key,
        "checkpoint_tensor_sha256": checkpoint_sha,
        "lm_head_tied_to_input_embedding": tied,
        "labels_shape": list(labels.shape),
        "labels_sha256": tensor_sha(labels),
        "ignore_positions": int((labels == -100).sum().cpu()),
        "snapshot_path": str(snapshot),
        "snapshot_sha256": sha_file(snapshot),
        "snapshot_size_bytes": snapshot.stat().st_size,
    }
    del outputs, model, input_ids
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    return hidden, weight, labels, receipt


def cpu_fp32_sanity(hidden: torch.Tensor, weight: torch.Tensor, labels: torch.Tensor) -> dict[str, object]:
    started = time.perf_counter()
    h = hidden[:1].float().cpu()
    w = weight.float().cpu()
    target = labels[:1].cpu()
    with torch.no_grad():
        logits = h @ w.T
        loss = F.cross_entropy(logits, target, reduction="mean")
    result = {
        "scope": "first real token, full real vocabulary, FP32 CPU semantic sanity only",
        "hidden_shape": list(h.shape),
        "weight_shape": list(w.shape),
        "label": int(target.item()),
        "loss": float(loss),
        "finite": bool(torch.isfinite(loss)),
        "wall_ms": (time.perf_counter() - started) * 1000,
        "not_performance_evidence": True,
    }
    del h, w, target, logits, loss
    gc.collect()
    return result


def numerical_qualification(
    base_hidden: torch.Tensor,
    base_weight: torch.Tensor,
    labels: torch.Tensor,
    liger_loss: LigerFusedLinearCrossEntropyLoss,
    total_memory: int,
) -> tuple[dict[str, object], dict[str, bool]]:
    results: dict[str, object] = {}
    qualified: dict[str, bool] = {}

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    ref_loss, ref_h, ref_w, ref_grad_h, ref_grad_w = execute(
        "B0", base_hidden, base_weight, labels, liger_loss
    )
    torch.cuda.synchronize()
    b0_wall_ms = (time.perf_counter() - started) * 1000
    b0_peak = torch.cuda.max_memory_allocated()
    if b0_peak > int(total_memory * 0.90):
        raise RuntimeError(
            f"full accepted window B0 peak {b0_peak} violates required 10% device margin"
        )
    ref_grad_h = ref_grad_h.detach().clone()
    ref_grad_w = ref_grad_w.detach().clone()
    ref_loss_value = ref_loss.detach().clone()
    results["B0"] = {
        "arm_name": ARM_NAMES["B0"],
        "loss": scalar_metrics(ref_loss_value, ref_loss_value),
        "grad_hidden": tensor_metrics(ref_grad_h, ref_grad_h),
        "grad_weight": {"self_reference": True, "allclose": True, "finite": True},
        "qualification_wall_ms": b0_wall_ms,
        "peak_allocated_bytes": b0_peak,
        "device_margin_fraction": (total_memory - b0_peak) / total_memory,
        "qualified": True,
    }
    qualified["B0"] = True
    del ref_loss, ref_h, ref_w
    gc.collect()

    for arm in ("B1", "B2"):
        torch.cuda.empty_cache()
        started = time.perf_counter()
        loss, h, w, grad_h, grad_w = execute(arm, base_hidden, base_weight, labels, liger_loss)
        torch.cuda.synchronize()
        metrics = {
            "arm_name": ARM_NAMES[arm],
            "loss": scalar_metrics(loss, ref_loss_value),
            "grad_hidden": tensor_metrics(grad_h, ref_grad_h),
            "grad_weight": tensor_metrics(grad_w, ref_grad_w),
            "qualification_wall_ms": (time.perf_counter() - started) * 1000,
        }
        ok = all(
            bool(metrics[name].get("allclose", False)) and bool(metrics[name].get("finite", False))
            for name in ("loss", "grad_hidden", "grad_weight")
        )
        metrics["qualified"] = ok
        results[arm] = metrics
        qualified[arm] = ok
        del loss, h, w, grad_h, grad_w
        gc.collect()
        torch.cuda.empty_cache()

    del ref_grad_h, ref_grad_w, ref_loss_value
    gc.collect()
    torch.cuda.empty_cache()
    return results, qualified


def memory_diagnostics(
    base_hidden: torch.Tensor,
    base_weight: torch.Tensor,
    labels: torch.Tensor,
    liger_loss: LigerFusedLinearCrossEntropyLoss,
    qualified: dict[str, bool],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for arm in ARMS:
        if not qualified.get(arm):
            result[arm] = {"qualified": False, "status": "NOT_RUN"}
            continue
        records: list[dict[str, object]] = []
        hidden, weight = make_leaves(base_hidden, base_weight)
        del hidden, weight
        gc.collect()
        torch.cuda.empty_cache()
        active_h, active_w = make_leaves(base_hidden, base_weight)
        torch.cuda.synchronize()
        baseline_allocated = torch.cuda.memory_allocated()
        baseline_reserved = torch.cuda.memory_reserved()
        torch.cuda.reset_peak_memory_stats()

        def pack(tensor: torch.Tensor) -> torch.Tensor:
            shape = list(tensor.shape)
            if shape == list(active_h.shape):
                identity = "hidden_or_grad_hidden_shape"
            elif shape == list(active_w.shape):
                identity = "lm_head_or_grad_weight_shape"
            elif shape == [active_h.shape[0], active_w.shape[0]]:
                identity = "full_TxV_logits_state"
            elif shape == list(labels.shape):
                identity = "labels_or_token_state"
            else:
                identity = "other"
            records.append(
                {
                    "shape": shape,
                    "dtype": str(tensor.dtype),
                    "logical_bytes": tensor_bytes(tensor),
                    "identity": identity,
                    "requires_grad": bool(tensor.requires_grad),
                    "storage_ptr": int(tensor.untyped_storage().data_ptr()),
                }
            )
            return tensor

        with torch.autograd.graph.saved_tensors_hooks(pack, lambda tensor: tensor):
            loss = arm_forward(arm, active_h, active_w, labels, liger_loss)
            loss.backward()
        torch.cuda.synchronize()
        peak_allocated = torch.cuda.max_memory_allocated()
        peak_reserved = torch.cuda.max_memory_reserved()
        unique_storage = {}
        for record in records:
            unique_storage.setdefault(record["storage_ptr"], record["logical_bytes"])
        mandatory_output_bytes = (
            tensor_bytes(active_h.grad) + tensor_bytes(active_w.grad) + tensor_bytes(loss)
        )
        result[arm] = {
            "qualified": True,
            "baseline_allocated_bytes": baseline_allocated,
            "baseline_reserved_bytes": baseline_reserved,
            "peak_allocated_bytes": peak_allocated,
            "peak_reserved_bytes": peak_reserved,
            "peak_allocated_delta_bytes": peak_allocated - baseline_allocated,
            "peak_reserved_delta_bytes": peak_reserved - baseline_reserved,
            "mandatory_output_bytes": mandatory_output_bytes,
            "saved_tensor_pack_events": len(records),
            "saved_tensor_logical_bytes_sum": sum(int(r["logical_bytes"]) for r in records),
            "saved_tensor_unique_storage_bytes": sum(int(v) for v in unique_storage.values()),
            "saved_tensors": records,
            "full_TxV_logits_saved": any(r["identity"] == "full_TxV_logits_state" for r in records),
            "full_TxV_logits_exists": arm == "B0",
            "allocator_bytes_are_not_dram_traffic": True,
        }
        del loss, active_h, active_w
        gc.collect()
        torch.cuda.empty_cache()
    return result


def time_one(
    arm: str,
    base_hidden: torch.Tensor,
    base_weight: torch.Tensor,
    labels: torch.Tensor,
    liger_loss: LigerFusedLinearCrossEntropyLoss,
) -> tuple[float, float, float]:
    hidden, weight = make_leaves(base_hidden, base_weight)
    torch.cuda.synchronize()
    begin = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    begin.record()
    host_begin = time.perf_counter_ns()
    loss = arm_forward(arm, hidden, weight, labels, liger_loss)
    loss.backward()
    end.record()
    torch.cuda.synchronize()
    host_ms = (time.perf_counter_ns() - host_begin) / 1e6
    gpu_ms = begin.elapsed_time(end)
    loss_value = float(loss.detach().cpu())
    del loss, hidden, weight, begin, end
    gc.collect()
    return gpu_ms, host_ms, loss_value


def formal_timing(
    base_hidden: torch.Tensor,
    base_weight: torch.Tensor,
    labels: torch.Tensor,
    liger_loss: LigerFusedLinearCrossEntropyLoss,
    qualified: dict[str, bool],
    raw: Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    active = [arm for arm in ARMS if qualified.get(arm)]
    samples: list[dict[str, object]] = []
    group_orders = [
        ["B0", "B1", "B2"],
        ["B1", "B2", "B0"],
        ["B2", "B0", "B1"],
    ]
    for group, order in enumerate(group_orders):
        order = [arm for arm in order if arm in active]
        for warmup in range(2):
            for arm in order:
                gpu_ms, host_ms, loss_value = time_one(
                    arm, base_hidden, base_weight, labels, liger_loss
                )
                samples.append(
                    {
                        "group": group,
                        "phase": "warmup",
                        "repeat": warmup,
                        "order": order.index(arm),
                        "arm": arm,
                        "arm_name": ARM_NAMES[arm],
                        "gpu_ms": gpu_ms,
                        "host_ms": host_ms,
                        "loss": loss_value,
                    }
                )
        for repeat in range(5):
            for arm in order:
                gpu_ms, host_ms, loss_value = time_one(
                    arm, base_hidden, base_weight, labels, liger_loss
                )
                samples.append(
                    {
                        "group": group,
                        "phase": "formal",
                        "repeat": repeat,
                        "order": order.index(arm),
                        "arm": arm,
                        "arm_name": ARM_NAMES[arm],
                        "gpu_ms": gpu_ms,
                        "host_ms": host_ms,
                        "loss": loss_value,
                    }
                )

    fields = [
        "group",
        "phase",
        "repeat",
        "order",
        "arm",
        "arm_name",
        "gpu_ms",
        "host_ms",
        "loss",
    ]
    with (raw / "TIMING_SAMPLES.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(samples)

    summary: dict[str, object] = {}
    for arm in active:
        formal = [row for row in samples if row["arm"] == arm and row["phase"] == "formal"]
        gpu_values = [float(row["gpu_ms"]) for row in formal]
        host_values = [float(row["host_ms"]) for row in formal]
        group_medians = {
            str(group): statistics.median(
                float(row["gpu_ms"])
                for row in formal
                if int(row["group"]) == group
            )
            for group in range(3)
        }
        gpu_median = statistics.median(gpu_values)
        gpu_mad = statistics.median(abs(value - gpu_median) for value in gpu_values)
        host_median = statistics.median(host_values)
        host_mad = statistics.median(abs(value - host_median) for value in host_values)
        summary[arm] = {
            "arm_name": ARM_NAMES[arm],
            "formal_samples": len(formal),
            "gpu_ms_median": gpu_median,
            "gpu_ms_mad": gpu_mad,
            "host_ms_median": host_median,
            "host_ms_mad": host_mad,
            "group_gpu_ms_medians": group_medians,
            "group_median_range_fraction": (
                max(group_medians.values()) - min(group_medians.values())
            )
            / gpu_median,
        }
    if "B0" in summary:
        for arm in ("B1", "B2"):
            if arm in summary:
                summary[arm]["speedup_vs_B0_gpu"] = (
                    summary["B0"]["gpu_ms_median"] / summary[arm]["gpu_ms_median"]
                )
    if "B1" in summary and "B2" in summary:
        faster = min(("B1", "B2"), key=lambda arm: summary[arm]["gpu_ms_median"])
        slower = "B1" if faster == "B2" else "B2"
        summary["strong_software_comparison"] = {
            "faster_arm": faster,
            "slower_arm": slower,
            "faster_ms": summary[faster]["gpu_ms_median"],
            "slower_ms": summary[slower]["gpu_ms_median"],
            "slower_over_faster_fraction": (
                summary[slower]["gpu_ms_median"] / summary[faster]["gpu_ms_median"] - 1.0
            ),
        }
    return samples, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--r101-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root
    raw = root / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    failure_path = raw / "CAMPAIGN_FAILURE.json"
    campaign: dict[str, object] = {
        "stage": "AWMA_EXACT_LOSS_CCE_LIGER_109_V1",
        "status": "RUNNING",
        "started_unix_ns": time.time_ns(),
        "lock_contract": "/data/c16/locks/c16_gpu_campaign.lock",
    }
    try:
        if os.environ.get("AWMA_GPU_LOCK_HELD") != "1":
            raise RuntimeError("GPU campaign wrapper did not attest the shared lock")
        source_identity = json.loads((root / "receipts" / "SOURCE_IDENTITY.json").read_text())
        if source_identity["cce"]["commit"] != "3de376c106a1916bc5e1b619f9c77c87a461ee1c":
            raise RuntimeError("CCE source freeze mismatch")
        if source_identity["liger"]["commit"] != "6ad077c36379eb9c7950f5572cc713f4d38e21a7":
            raise RuntimeError("Liger source freeze mismatch")
        tokens = json.loads((args.r101_root / "raw" / "TRAIN_DISCOVERY_256.json").read_text())
        device = torch.device("cuda:0")
        props = torch.cuda.get_device_properties(device)
        if props.major != 8 or props.minor != 9:
            raise RuntimeError(f"expected SM89, observed sm_{props.major}{props.minor}")
        environment = {
            "python": os.sys.version.replace("\n", " "),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "transformers": transformers.__version__,
            "triton": triton.__version__,
            "gpu_name": props.name,
            "compute_capability": f"{props.major}.{props.minor}",
            "total_memory_bytes": props.total_memory,
            "liger_kernel_impl_env": os.environ.get("LIGER_KERNEL_IMPL"),
            "liger_get_impl": get_impl(),
            "liger_available_impls": sorted(available_impls("fused_linear_cross_entropy", device)),
            "formal_source_freeze_before_timing": True,
        }
        write_json(raw / "GPU_ENVIRONMENT.json", environment)
        usable = environment["liger_available_impls"]
        if not usable or usable[0] != "nvidia-triton":
            raise RuntimeError(f"Ada inner dispatch did not resolve Triton first: {usable}")
        if any(name in usable for name in ("nvidia-cutile", "nvidia-cutedsl")):
            raise RuntimeError(f"SM90-only Liger backend unexpectedly available: {usable}")

        base_hidden, base_weight, labels, runtime_input = capture_real_inputs(
            args.model_root, tokens, raw
        )
        write_json(raw / "RUNTIME_INPUT_RECEIPT.json", runtime_input)
        sanity = cpu_fp32_sanity(base_hidden, base_weight, labels)
        if not sanity["finite"]:
            raise RuntimeError("CPU FP32 real-input sanity failed")
        write_json(raw / "CPU_FP32_SANITY.json", sanity)

        liger_loss = make_liger()
        numerical, qualified = numerical_qualification(
            base_hidden, base_weight, labels, liger_loss, props.total_memory
        )
        write_json(raw / "NUMERICAL_QUALIFICATION.json", numerical)
        if not all(qualified.values()):
            campaign["status"] = "IMPLEMENTATION_CONTRACT_NOT_QUALIFIED"
            campaign["qualified_arms"] = qualified
            write_json(raw / "CAMPAIGN_RESULT.json", campaign)
            return

        memory = memory_diagnostics(base_hidden, base_weight, labels, liger_loss, qualified)
        write_json(raw / "MEMORY_ACCOUNTING.json", memory)
        samples, timing = formal_timing(
            base_hidden, base_weight, labels, liger_loss, qualified, raw
        )
        write_json(raw / "TIMING_SUMMARY.json", timing)
        campaign.update(
            {
                "status": "COMPLETE",
                "qualified_arms": qualified,
                "formal_sample_counts": {
                    arm: sum(
                        row["phase"] == "formal" and row["arm"] == arm for row in samples
                    )
                    for arm in ARMS
                },
                "profiling_triggered": False,
                "profiler_reason": "deferred to post-timing decision; no profiler invoked by campaign",
                "finished_unix_ns": time.time_ns(),
            }
        )
        write_json(raw / "CAMPAIGN_RESULT.json", campaign)
        print(json.dumps({"status": campaign["status"], "timing": timing}, sort_keys=True))
    except Exception as exc:
        campaign.update(
            {
                "status": "FAILED",
                "error": repr(exc),
                "traceback": traceback.format_exc(),
                "finished_unix_ns": time.time_ns(),
            }
        )
        write_json(failure_path, campaign)
        raise
    finally:
        if torch.cuda.is_initialized():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
