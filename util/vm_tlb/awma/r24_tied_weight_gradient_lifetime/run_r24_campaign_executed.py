#!/usr/bin/env python3
"""R24 tied-weight gradient lifetime native campaign."""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import importlib.metadata
import json
import math
import os
import statistics
import sys
import time
import traceback
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import triton
from cut_cross_entropy import linear_cross_entropy
from cut_cross_entropy import tl_autotune
from cut_cross_entropy.cce_backward import cce_backward_kernel
from cut_cross_entropy.utils import TensorInfo
from transformers import AutoModelForCausalLM


ARMS = ("B0_STRONG", "S1_LATE_FULL", "S2_LATE_TILED")
V, H, T = 151936, 896, 255
ATOL = RTOL = 1e-2
BLOCK_V = 128
TILE_BUDGET = 32 * 1024 * 1024
ROWS_PER_TILE = (TILE_BUDGET // (H * 4) // BLOCK_V) * BLOCK_V
TILE_COUNT = math.ceil(V / ROWS_PER_TILE)


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    value = tensor.detach().contiguous().cpu().view(torch.uint8).numpy()
    return hashlib.sha256(memoryview(value)).hexdigest()


def nbytes(tensor: torch.Tensor) -> int:
    return tensor.numel() * tensor.element_size()


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_tsv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def median(values):
    return statistics.median(values)


def mad(values):
    med = median(values)
    return median([abs(value - med) for value in values])


def tensor_metrics(got: torch.Tensor, ref: torch.Tensor, chunk: int = 1 << 20):
    if got.shape != ref.shape or got.dtype != ref.dtype:
        return {
            "shape_match": got.shape == ref.shape,
            "dtype_match": got.dtype == ref.dtype,
            "allclose": False,
            "finite": False,
        }
    lhs = got.detach().reshape(-1)
    rhs = ref.detach().reshape(-1)
    max_abs = max_rel = sum_abs = dot = lhs_norm = rhs_norm = 0.0
    allclose = finite = True
    for start in range(0, lhs.numel(), chunk):
        stop = min(start + chunk, lhs.numel())
        a = lhs[start:stop].float()
        b = rhs[start:stop].float()
        diff = (a - b).abs()
        max_abs = max(max_abs, float(diff.max()))
        max_rel = max(max_rel, float((diff / b.abs().clamp_min(1e-30)).max()))
        sum_abs += float(diff.double().sum())
        a64, b64 = a.double(), b.double()
        dot += float((a64 * b64).sum())
        lhs_norm += float((a64 * a64).sum())
        rhs_norm += float((b64 * b64).sum())
        allclose &= bool((diff <= ATOL + RTOL * b.abs()).all())
        finite &= bool(torch.isfinite(a).all())
    cosine = dot / math.sqrt(lhs_norm * rhs_norm) if lhs_norm and rhs_norm else 1.0
    return {
        "shape": list(got.shape),
        "dtype": str(got.dtype),
        "numel": got.numel(),
        "max_abs": max_abs,
        "mean_abs": sum_abs / lhs.numel(),
        "max_rel": max_rel,
        "cosine_similarity": cosine,
        "allclose": allclose,
        "finite": finite,
        "shape_match": True,
        "dtype_match": True,
    }


def scalar_metrics(got: float, ref: float):
    diff = abs(got - ref)
    return {
        "observed": got,
        "reference": ref,
        "max_abs": diff,
        "mean_abs": diff,
        "max_rel": diff / max(abs(ref), 1e-30),
        "cosine_similarity": 1.0 if got == ref else math.copysign(1.0, got * ref),
        "finite": math.isfinite(got),
        "allclose": diff <= ATOL + RTOL * abs(ref),
    }


class CompactCollector:
    ids: torch.Tensor | None = None
    grad: torch.Tensor | None = None
    inverse_bytes: int = 0

    def reset(self):
        self.ids = None
        self.grad = None
        self.inverse_bytes = 0


class CompactEmbedding(torch.autograd.Function):
    @staticmethod
    def forward(ctx, weight, indices, collector):
        ctx.save_for_backward(indices)
        ctx.collector = collector
        return F.embedding(indices, weight)

    @staticmethod
    def backward(ctx, grad_output):
        (indices,) = ctx.saved_tensors
        flat_ids = indices.reshape(-1)
        unique, inverse = torch.unique(flat_ids, sorted=True, return_inverse=True)
        grad = torch.zeros(
            (unique.numel(), grad_output.shape[-1]),
            dtype=grad_output.dtype,
            device=grad_output.device,
        )
        grad.index_add_(0, inverse, grad_output.reshape(-1, grad_output.shape[-1]))
        ctx.collector.ids = unique
        ctx.collector.grad = grad
        ctx.collector.inverse_bytes = nbytes(inverse)
        return None, None, None


def fixed_meta():
    values = dict(tl_autotune._cce_best_config().all_kwargs())
    expected = {
        "BLOCK_B": 128,
        "BLOCK_V": 128,
        "BLOCK_D": 32,
        "num_warps": 4,
        "num_stages": 4,
    }
    if {key: values[key] for key in expected} != expected:
        raise RuntimeError(f"CCE meta mismatch {values}")
    if tl_autotune._AUTOTUNE or os.environ.get("CCE_AUTOTUNE", "0") != "0":
        raise RuntimeError("CCE autotune not frozen off")
    return {**values, "MM_BACK_BLOCK_D": 64, "CCE_AUTOTUNE": 0}


def cce_forward(hidden, weight, labels):
    loss, lse = linear_cross_entropy(
        hidden.detach(),
        weight.detach(),
        labels,
        ignore_index=-100,
        softcap=None,
        reduction="mean",
        shift=0,
        return_lse=True,
        filter_eps=None,
        accum_e_fp32=True,
        accum_c_fp32=True,
        filter_e_grad=False,
        filter_c_grad=False,
        impl="cce_exact",
    )
    return loss, lse


def cce_backward(hidden, weight, labels, lse, compute_de, compute_dc):
    do = lse.new_ones(())
    de, dc, _ = cce_backward_kernel(
        do=do,
        dlse=None,
        e=hidden.detach(),
        e_info=TensorInfo(hidden.dtype, compute_de),
        c=weight.detach(),
        c_info=TensorInfo(weight.dtype, compute_dc),
        bias=None,
        bias_info=None,
        lse=lse.detach(),
        valids=None,
        softcap=None,
        filter_eps=None,
        targets=labels,
        shift=0,
        vocab_ordering=None,
        grad_scale=1.0 / lse.numel(),
        accum_e_fp32=True,
        accum_c_fp32=True,
        filter_e_grad=False,
        filter_c_grad=False,
        reduce_e_grad=False,
        pg=None,
    )
    return de, dc


def local_targets(labels: torch.Tensor, start: int, stop: int) -> torch.Tensor:
    local = labels - start
    padding = stop - start + 1
    return torch.where(
        (labels >= start) & (labels < stop),
        local,
        labels.new_full((), padding),
    )


@torch.no_grad()
def adamw_update_tile(weight, m, v, grad, step, contract):
    beta1, beta2 = contract["betas"]
    lr = contract["lr"]
    eps = contract["eps"]
    wd = contract["weight_decay"]
    g = grad.float()
    m.mul_(beta1).add_(g, alpha=1 - beta1)
    v.mul_(beta2).addcmul_(g, g, value=1 - beta2)
    denom = v.sqrt().div_(math.sqrt(1 - beta2**step)).add_(eps)
    p = weight.float()
    p.mul_(1 - lr * wd)
    p.addcdiv_(m, denom, value=-lr / (1 - beta1**step))
    weight.copy_(p)


@dataclass
class FrozenState:
    weight: torch.Tensor
    m: torch.Tensor
    v: torch.Tensor
    step: int
    cpu_rng: torch.Tensor
    cuda_rng: torch.Tensor


class Campaign:
    def __init__(self, args):
        if os.environ.get("R24_GPU_LOCK_HELD") != "1":
            raise RuntimeError("R24_GPU_LOCK_HELD=1 required")
        self.args = args
        self.root = Path(args.root)
        self.raw = self.root / "raw"
        self.raw.mkdir(parents=True, exist_ok=True)
        self.pack = Path(args.pack)
        self.contract = json.loads((self.pack / "OPTIMIZER_CONTRACT.json").read_text())
        if ROWS_PER_TILE != 9344 or TILE_COUNT != 17:
            raise RuntimeError("frozen tile derivation mismatch")
        if self.contract["optimizer_rows_per_tile"] != ROWS_PER_TILE:
            raise RuntimeError("optimizer contract tile mismatch")
        self.meta = fixed_meta()
        self.tokens = json.loads(Path(args.tokens).read_text())
        if len(self.tokens) != 256:
            raise RuntimeError("token count mismatch")
        self.input_ids_cpu = torch.tensor(self.tokens[:-1], dtype=torch.int64).view(1, T)
        self.labels_cpu = torch.tensor(self.tokens[1:], dtype=torch.int64)
        if tensor_sha(self.input_ids_cpu) != "f59446f6a177507048cad5e272d03b1d910337bf0e626f4ce78aa8c244837a1e":
            raise RuntimeError("input_ids hash mismatch")
        if tensor_sha(self.labels_cpu) != "c89b22206d04b19d9a018e25c732aa5b1acf01b7b1ca18579bfc9ac4e1214f3a":
            raise RuntimeError("labels hash mismatch")
        self.input_ids = self.input_ids_cpu.to("cuda:0")
        self.labels = self.labels_cpu.to("cuda:0")
        self.attention = torch.ones_like(self.input_ids)
        self.model = AutoModelForCausalLM.from_pretrained(
            args.model,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
        ).train().to("cuda:0")
        for param in self.model.parameters():
            param.requires_grad_(False)
        self.weight = self.model.model.embed_tokens.weight
        self.weight.requires_grad_(True)
        output_weight = self.model.get_output_embeddings().weight
        if self.weight.data_ptr() != output_weight.data_ptr():
            raise RuntimeError("tied storage pointer mismatch")
        if self.weight.untyped_storage().data_ptr() != output_weight.untyped_storage().data_ptr():
            raise RuntimeError("tied untyped storage mismatch")
        if tuple(self.weight.shape) != (V, H) or self.weight.dtype != torch.bfloat16:
            raise RuntimeError("tied W identity mismatch")
        self.m = torch.zeros_like(self.weight, dtype=torch.float32)
        self.v = torch.zeros_like(self.weight, dtype=torch.float32)
        self.collector = CompactCollector()
        self.frozen: FrozenState | None = None
        self.initial_weight = self.weight.detach().clone()
        self.base_model_parameter_bytes = sum(nbytes(p) for p in self.model.parameters())
        self._write_authority()

    def _write_authority(self):
        receipt = {
            "stage": "AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1",
            "model": self.args.model,
            "model_safetensors_sha256": sha_file(Path(self.args.model) / "model.safetensors"),
            "token_file": self.args.tokens,
            "token_file_sha256": sha_file(Path(self.args.tokens)),
            "input_ids_sha256": tensor_sha(self.input_ids_cpu),
            "labels_sha256": tensor_sha(self.labels_cpu),
            "input_shape": list(self.input_ids.shape),
            "labels_shape": list(self.labels.shape),
            "weight_shape": list(self.weight.shape),
            "weight_dtype": str(self.weight.dtype),
            "embedding_data_ptr": self.weight.data_ptr(),
            "lm_head_data_ptr": self.model.get_output_embeddings().weight.data_ptr(),
            "untyped_storage_data_ptr": self.weight.untyped_storage().data_ptr(),
            "tied_pointer_exact": True,
            "tied_storage_exact": True,
            "only_tied_W_trainable": [name for name, p in self.model.named_parameters() if p.requires_grad],
            "fixed_cce_meta": self.meta,
            "rows_per_tile": ROWS_PER_TILE,
            "tile_count": TILE_COUNT,
            "tile_fp32_bytes": ROWS_PER_TILE * H * 4,
        }
        write_json(self.raw / "TIED_INPUT_SOURCE_AUTHORITY.json", receipt)

    def restore(self):
        if self.frozen is None:
            raise RuntimeError("frozen state missing")
        with torch.no_grad():
            self.weight.copy_(self.frozen.weight)
            self.m.copy_(self.frozen.m)
            self.v.copy_(self.frozen.v)
        self.weight.grad = None
        self.collector.reset()
        torch.set_rng_state(self.frozen.cpu_rng)
        torch.cuda.set_rng_state(self.frozen.cuda_rng, device="cuda:0")
        return self.frozen.step

    def model_forward(self, arm):
        if arm == "S2_LATE_TILED":
            embeds = CompactEmbedding.apply(self.weight, self.input_ids, self.collector)
            out = self.model.model(
                inputs_embeds=embeds,
                attention_mask=self.attention,
                use_cache=False,
                return_dict=True,
            )
        else:
            out = self.model.model(
                input_ids=self.input_ids,
                attention_mask=self.attention,
                use_cache=False,
                return_dict=True,
            )
        hidden = out.last_hidden_state
        hidden.retain_grad()
        return hidden, hidden.reshape(T, H)

    @torch.no_grad()
    def next_loss(self):
        out = self.model.model(
            input_ids=self.input_ids,
            attention_mask=self.attention,
            use_cache=False,
            return_dict=True,
        )
        loss, _ = cce_forward(out.last_hidden_state.reshape(T, H), self.weight, self.labels)
        torch.cuda.synchronize()
        return float(loss)

    def update_full(self, grad, step):
        for start in range(0, V, ROWS_PER_TILE):
            stop = min(start + ROWS_PER_TILE, V)
            adamw_update_tile(
                self.weight[start:stop],
                self.m[start:stop],
                self.v[start:stop],
                grad[start:stop],
                step,
                self.contract,
            )

    def run_microstep(self, arm, step, capture=False, measure=False, purpose=""):
        if arm not in ARMS:
            raise ValueError(arm)
        self.model.zero_grad(set_to_none=True)
        self.weight.grad = None
        self.collector.reset()
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        pre_alloc = torch.cuda.memory_allocated()
        pre_reserved = torch.cuda.memory_reserved()
        torch.cuda.reset_peak_memory_stats()
        complete_start_ns = time.perf_counter_ns()
        hidden_3d, hidden = self.model_forward(arm)
        loss, lse = cce_forward(hidden, self.weight, self.labels)
        torch.cuda.synchronize()
        forward_peak_alloc = torch.cuda.max_memory_allocated()
        forward_peak_reserved = torch.cuda.max_memory_reserved()
        target_base_alloc = torch.cuda.memory_allocated()
        target_base_reserved = torch.cuda.memory_reserved()
        torch.cuda.reset_peak_memory_stats()
        target_start = torch.cuda.Event(enable_timing=True)
        target_end = torch.cuda.Event(enable_timing=True)
        full_first = torch.cuda.Event(enable_timing=True) if arm != "S2_LATE_TILED" else None
        full_release = torch.cuda.Event(enable_timing=True) if arm != "S2_LATE_TILED" else None
        target_start.record()
        target_host_start = time.perf_counter_ns()
        grad_capture = None
        full_buffer_count_peak = 0
        compact_rows = compact_bytes = compact_inverse_bytes = 0
        if arm == "B0_STRONG":
            de, dc = cce_backward(hidden, self.weight, self.labels, lse, True, True)
            assert de is not None and dc is not None
            full_first.record()
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is None:
                raise RuntimeError("B0 lookup gradient missing")
            self.weight.grad.add_(dc)
            full_buffer_count_peak = 2
            del dc
            if capture:
                grad_capture = self.weight.grad.detach().cpu()
            self.update_full(self.weight.grad, step)
            self.weight.grad = None
            full_release.record()
        elif arm == "S1_LATE_FULL":
            de, _ = cce_backward(hidden, self.weight, self.labels, lse, True, False)
            assert de is not None
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is None:
                raise RuntimeError("S1 lookup gradient missing")
            full_first.record()
            _, dc = cce_backward(hidden, self.weight, self.labels, lse, False, True)
            assert dc is not None
            self.weight.grad.add_(dc)
            full_buffer_count_peak = 2
            del dc
            if capture:
                grad_capture = self.weight.grad.detach().cpu()
            self.update_full(self.weight.grad, step)
            self.weight.grad = None
            full_release.record()
        else:
            de, _ = cce_backward(hidden, self.weight, self.labels, lse, True, False)
            assert de is not None
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is not None:
                raise RuntimeError("S2 formal path materialized dense W.grad")
            if self.collector.ids is None or self.collector.grad is None:
                raise RuntimeError("S2 compact lookup gradient missing")
            compact_rows = self.collector.ids.numel()
            compact_bytes = nbytes(self.collector.ids) + nbytes(self.collector.grad)
            compact_inverse_bytes = self.collector.inverse_bytes
            debug = torch.empty_like(self.weight) if capture else None
            for start in range(0, V, ROWS_PER_TILE):
                stop = min(start + ROWS_PER_TILE, V)
                tile_labels = local_targets(self.labels, start, stop)
                _, dc = cce_backward(
                    hidden,
                    self.weight[start:stop],
                    tile_labels,
                    lse,
                    False,
                    True,
                )
                assert dc is not None
                selected = (self.collector.ids >= start) & (self.collector.ids < stop)
                if bool(selected.any()):
                    local = self.collector.ids[selected] - start
                    dc.index_add_(0, local, self.collector.grad[selected])
                if debug is not None:
                    debug[start:stop].copy_(dc)
                adamw_update_tile(
                    self.weight[start:stop],
                    self.m[start:stop],
                    self.v[start:stop],
                    dc,
                    step,
                    self.contract,
                )
                del dc
            if debug is not None:
                grad_capture = debug.cpu()
                del debug
        target_end.record()
        target_end.synchronize()
        target_host_ms = (time.perf_counter_ns() - target_host_start) / 1e6
        target_gpu_ms = target_start.elapsed_time(target_end)
        lifetime_ms = None
        if full_first is not None and full_release is not None:
            lifetime_ms = full_first.elapsed_time(full_release)
        target_peak_alloc = torch.cuda.max_memory_allocated()
        target_peak_reserved = torch.cuda.max_memory_reserved()
        complete_ms = (time.perf_counter_ns() - complete_start_ns) / 1e6
        complete_peak_alloc = max(forward_peak_alloc, target_peak_alloc)
        complete_peak_reserved = max(forward_peak_reserved, target_peak_reserved)
        dH_capture = hidden_3d.grad.detach().cpu() if capture else None
        result = {
            "purpose": purpose,
            "arm": arm,
            "loss": float(loss),
            "target_gpu_ms": target_gpu_ms,
            "target_host_ms": target_host_ms,
            "complete_microstep_ms": complete_ms,
            "pre_forward_allocated_bytes": pre_alloc,
            "pre_forward_reserved_bytes": pre_reserved,
            "target_baseline_allocated_bytes": target_base_alloc,
            "target_baseline_reserved_bytes": target_base_reserved,
            "target_peak_allocated_bytes": target_peak_alloc,
            "target_peak_reserved_bytes": target_peak_reserved,
            "target_peak_allocated_delta_bytes": target_peak_alloc - target_base_alloc,
            "target_peak_reserved_delta_bytes": target_peak_reserved - target_base_reserved,
            "whole_peak_allocated_bytes": complete_peak_alloc,
            "whole_peak_reserved_bytes": complete_peak_reserved,
            "full_dense_gradient_materialized": arm != "S2_LATE_TILED",
            "full_gradient_buffer_count_peak": full_buffer_count_peak,
            "full_gradient_lifetime_gpu_ms": lifetime_ms,
            "compact_lookup_rows": compact_rows,
            "compact_lookup_bytes": compact_bytes,
            "compact_inverse_temporary_bytes": compact_inverse_bytes,
            "s2_rows_per_tile": ROWS_PER_TILE if arm == "S2_LATE_TILED" else 0,
            "s2_tile_count": TILE_COUNT if arm == "S2_LATE_TILED" else 0,
            "step_after": step,
        }
        if capture:
            next_loss = self.next_loss()
            result["capture"] = {
                "dH": dH_capture,
                "gradient": grad_capture,
                "weight": self.weight.detach().cpu(),
                "m": self.m.detach().cpu(),
                "v": self.v.detach().cpu(),
                "next_loss": next_loss,
            }
        del hidden_3d, hidden, loss, lse
        gc.collect()
        return result

    def bootstrap(self):
        self.m.zero_()
        self.v.zero_()
        with torch.no_grad():
            self.weight.copy_(self.initial_weight)
        torch.manual_seed(24001)
        torch.cuda.manual_seed_all(24001)
        result = self.run_microstep("B0_STRONG", 1, capture=False, measure=False, purpose="BOOTSTRAP")
        torch.cuda.synchronize()
        self.frozen = FrozenState(
            weight=self.weight.detach().clone(),
            m=self.m.detach().clone(),
            v=self.v.detach().clone(),
            step=1,
            cpu_rng=torch.get_rng_state().clone(),
            cuda_rng=torch.cuda.get_rng_state("cuda:0").clone(),
        )
        receipt = {
            "bootstrap_arm": "B0_STRONG",
            "bootstrap_target_gpu_ms_diagnostic": result["target_gpu_ms"],
            "weight": {"shape": list(self.frozen.weight.shape), "dtype": str(self.frozen.weight.dtype), "sha256": tensor_sha(self.frozen.weight)},
            "first_moment": {"shape": list(self.frozen.m.shape), "dtype": str(self.frozen.m.dtype), "sha256": tensor_sha(self.frozen.m)},
            "second_moment": {"shape": list(self.frozen.v.shape), "dtype": str(self.frozen.v.dtype), "sha256": tensor_sha(self.frozen.v)},
            "step": self.frozen.step,
            "cpu_rng_sha256": tensor_sha(self.frozen.cpu_rng),
            "cuda_rng_sha256": tensor_sha(self.frozen.cuda_rng),
            "frozen_snapshot_gpu_bytes": nbytes(self.frozen.weight) + nbytes(self.frozen.m) + nbytes(self.frozen.v),
        }
        write_json(self.raw / "FROZEN_START_STATE.json", receipt)
        del self.initial_weight
        gc.collect()
        torch.cuda.empty_cache()

    def qualify(self):
        outputs = {}
        for arm in ARMS:
            step = self.restore() + 1
            outputs[arm] = self.run_microstep(arm, step, capture=True, purpose=f"QUALIFY_{arm}")
            torch.cuda.synchronize()
        ref = outputs["B0_STRONG"]
        rows = []
        details = {}
        first_mismatch = None
        for arm in ARMS:
            value = outputs[arm]
            if arm == "B0_STRONG":
                metrics = {
                    "loss": scalar_metrics(value["loss"], ref["loss"]),
                    "dH": tensor_metrics(value["capture"]["dH"], ref["capture"]["dH"]),
                    "gradient": tensor_metrics(value["capture"]["gradient"], ref["capture"]["gradient"]),
                    "weight": tensor_metrics(value["capture"]["weight"], ref["capture"]["weight"]),
                    "m": tensor_metrics(value["capture"]["m"], ref["capture"]["m"]),
                    "v": tensor_metrics(value["capture"]["v"], ref["capture"]["v"]),
                    "next_loss": scalar_metrics(value["capture"]["next_loss"], ref["capture"]["next_loss"]),
                }
            else:
                metrics = {
                    "loss": scalar_metrics(value["loss"], ref["loss"]),
                    "dH": tensor_metrics(value["capture"]["dH"], ref["capture"]["dH"]),
                    "gradient": tensor_metrics(value["capture"]["gradient"], ref["capture"]["gradient"]),
                    "weight": tensor_metrics(value["capture"]["weight"], ref["capture"]["weight"]),
                    "m": tensor_metrics(value["capture"]["m"], ref["capture"]["m"]),
                    "v": tensor_metrics(value["capture"]["v"], ref["capture"]["v"]),
                    "next_loss": scalar_metrics(value["capture"]["next_loss"], ref["capture"]["next_loss"]),
                }
            qualified = all(metric.get("allclose", False) for metric in metrics.values()) and value["step_after"] == ref["step_after"]
            details[arm] = {"qualified": qualified, "metrics": metrics, "step_exact": value["step_after"] == ref["step_after"]}
            for name, metric in metrics.items():
                rows.append({
                    "arm": arm,
                    "observable": name,
                    "qualified": metric.get("allclose", False),
                    "finite": metric.get("finite", False),
                    "shape": json.dumps(metric.get("shape", []), separators=(",", ":")),
                    "dtype": metric.get("dtype", "scalar"),
                    "max_abs": metric.get("max_abs", 0.0),
                    "mean_abs": metric.get("mean_abs", 0.0),
                    "max_rel": metric.get("max_rel", 0.0),
                    "cosine_similarity": metric.get("cosine_similarity", 1.0),
                })
                if not metric.get("allclose", False) and first_mismatch is None:
                    first_mismatch = {"arm": arm, "observable": name, "metrics": metric}
        write_tsv(self.raw / "NUMERICAL_QUALIFICATION.tsv", rows)
        write_json(self.raw / "NUMERICAL_QUALIFICATION.json", details)
        write_json(self.raw / "FIRST_MISMATCH.json", {"status": "NONE" if first_mismatch is None else "MISMATCH", "first_mismatch": first_mismatch})
        for value in outputs.values():
            value.pop("capture", None)
        del ref, outputs
        gc.collect()
        if not all(details[arm]["qualified"] for arm in ARMS):
            raise RuntimeError("R24_NUMERIC_CONTRACT_NOT_QUALIFIED")

    def formal(self):
        orders = (
            ("B0_STRONG", "S1_LATE_FULL", "S2_LATE_TILED"),
            ("S1_LATE_FULL", "S2_LATE_TILED", "B0_STRONG"),
            ("S2_LATE_TILED", "B0_STRONG", "S1_LATE_FULL"),
        )
        samples = []
        raw_jsonl = self.raw / "FORMAL_RUNS.jsonl"
        raw_jsonl.write_text("")
        for group, order in enumerate(orders):
            for arm in order:
                for repeat in range(2):
                    step = self.restore() + 1
                    self.run_microstep(arm, step, capture=False, purpose=f"WARMUP_G{group}_{arm}_{repeat}")
            for repeat in range(5):
                for position, arm in enumerate(order):
                    step = self.restore() + 1
                    result = self.run_microstep(arm, step, capture=False, purpose=f"FORMAL_G{group}_R{repeat}_{arm}")
                    row = {
                        "group": group,
                        "repeat": repeat,
                        "position": position,
                        **result,
                        "numeric_qualified": True,
                    }
                    samples.append(row)
                    with raw_jsonl.open("a") as f:
                        f.write(json.dumps(row, sort_keys=True) + "\n")
        target_rows = [{
            "group": r["group"], "repeat": r["repeat"], "position": r["position"], "arm": r["arm"],
            "target_gpu_ms": f"{r['target_gpu_ms']:.9f}", "target_host_ms": f"{r['target_host_ms']:.9f}",
            "full_dense_gradient_materialized": r["full_dense_gradient_materialized"],
            "full_gradient_lifetime_gpu_ms": "" if r["full_gradient_lifetime_gpu_ms"] is None else f"{r['full_gradient_lifetime_gpu_ms']:.9f}",
            "target_peak_allocated_bytes": r["target_peak_allocated_bytes"], "target_peak_reserved_bytes": r["target_peak_reserved_bytes"],
            "target_peak_allocated_delta_bytes": r["target_peak_allocated_delta_bytes"], "target_peak_reserved_delta_bytes": r["target_peak_reserved_delta_bytes"],
            "compact_lookup_rows": r["compact_lookup_rows"], "compact_lookup_bytes": r["compact_lookup_bytes"],
            "s2_rows_per_tile": r["s2_rows_per_tile"], "s2_tile_count": r["s2_tile_count"], "numeric_qualified": True,
        } for r in samples]
        micro_rows = [{
            "group": r["group"], "repeat": r["repeat"], "position": r["position"], "arm": r["arm"],
            "complete_microstep_ms": f"{r['complete_microstep_ms']:.9f}",
            "whole_peak_allocated_bytes": r["whole_peak_allocated_bytes"], "whole_peak_reserved_bytes": r["whole_peak_reserved_bytes"],
            "pre_forward_allocated_bytes": r["pre_forward_allocated_bytes"], "pre_forward_reserved_bytes": r["pre_forward_reserved_bytes"],
            "numeric_qualified": True,
        } for r in samples]
        write_tsv(self.raw / "FORMAL_TARGET_TIMING.tsv", target_rows)
        write_tsv(self.raw / "FORMAL_MICROSTEP_TIMING.tsv", micro_rows)
        return samples

    def summarize(self, samples):
        group_rows = []
        for group in range(3):
            arm_values = {}
            for arm in ARMS:
                rows = [r for r in samples if r["group"] == group and r["arm"] == arm]
                gpu = [r["target_gpu_ms"] for r in rows]
                host = [r["target_host_ms"] for r in rows]
                complete = [r["complete_microstep_ms"] for r in rows]
                arm_values[arm] = {"gpu": gpu, "host": host, "complete": complete}
                group_rows.append({
                    "group": group, "arm": arm,
                    "target_gpu_median_ms": median(gpu), "target_gpu_mad_ms": mad(gpu),
                    "target_host_median_ms": median(host), "target_host_mad_ms": mad(host),
                    "complete_median_ms": median(complete), "complete_mad_ms": mad(complete),
                    "target_peak_allocated_bytes": median([r["target_peak_allocated_bytes"] for r in rows]),
                    "target_peak_allocated_delta_bytes": median([r["target_peak_allocated_delta_bytes"] for r in rows]),
                    "full_gradient_lifetime_median_ms": "" if arm == "S2_LATE_TILED" else median([r["full_gradient_lifetime_gpu_ms"] for r in rows]),
                })
        write_tsv(self.raw / "GROUP_RESPONSE_SUMMARY.tsv", group_rows)

        def stable_regression(candidate, baseline):
            count = 0
            for group in range(3):
                c = [r["target_gpu_ms"] for r in samples if r["group"] == group and r["arm"] == candidate]
                b = [r["target_gpu_ms"] for r in samples if r["group"] == group and r["arm"] == baseline]
                gap = median(c) - median(b)
                if gap > 3 * max(mad(c), mad(b)):
                    count += 1
            return count

        s2_vs_b0_reg = stable_regression("S2_LATE_TILED", "B0_STRONG")
        s2_vs_s1_reg = stable_regression("S2_LATE_TILED", "S1_LATE_FULL")
        formal_s2_no_full = all(not r["full_dense_gradient_materialized"] for r in samples if r["arm"] == "S2_LATE_TILED")
        peak = {arm: median([r["target_peak_allocated_bytes"] for r in samples if r["arm"] == arm]) for arm in ARMS}
        memory_reduction = formal_s2_no_full and peak["S2_LATE_TILED"] < min(peak["B0_STRONG"], peak["S1_LATE_FULL"])
        if memory_reduction and (s2_vs_b0_reg >= 2 or s2_vs_s1_reg >= 2):
            decision = "R24_CAPACITY_TIME_TRADEOFF"
        elif memory_reduction and s2_vs_b0_reg == 0 and s2_vs_s1_reg == 0:
            decision = "R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT"
        elif not memory_reduction:
            decision = "R24_TIED_WEIGHT_GRADIENT_PATH_NOT_BENEFICIAL"
        else:
            decision = "R24_CAPACITY_TIME_TRADEOFF"
        memory_rows = []
        for arm in ARMS:
            rows = [r for r in samples if r["arm"] == arm]
            memory_rows.append({
                "arm": arm,
                "formal_full_dense_gradient_materialized": any(r["full_dense_gradient_materialized"] for r in rows),
                "full_size_gradient_buffers_peak": max(r["full_gradient_buffer_count_peak"] for r in rows),
                "median_target_peak_allocated_bytes": median([r["target_peak_allocated_bytes"] for r in rows]),
                "median_target_peak_reserved_bytes": median([r["target_peak_reserved_bytes"] for r in rows]),
                "median_target_peak_allocated_delta_bytes": median([r["target_peak_allocated_delta_bytes"] for r in rows]),
                "median_whole_peak_allocated_bytes": median([r["whole_peak_allocated_bytes"] for r in rows]),
                "full_gradient_lifetime_median_ms": "" if arm == "S2_LATE_TILED" else median([r["full_gradient_lifetime_gpu_ms"] for r in rows]),
                "s2_tile_fp32_bytes": ROWS_PER_TILE * H * 4 if arm == "S2_LATE_TILED" else 0,
                "s2_tile_bf16_bytes": ROWS_PER_TILE * H * 2 if arm == "S2_LATE_TILED" else 0,
                "compact_lookup_rows": median([r["compact_lookup_rows"] for r in rows]),
                "compact_lookup_bytes": median([r["compact_lookup_bytes"] for r in rows]),
                "optimizer_state_bytes": nbytes(self.m) + nbytes(self.v),
                "frozen_start_snapshot_bytes": nbytes(self.frozen.weight) + nbytes(self.frozen.m) + nbytes(self.frozen.v),
                "saved_final_hidden_bytes": T * H * 2,
                "saved_lse_bytes": T * 4,
                "labels_bytes": nbytes(self.labels),
                "allocator_bytes_are_not_dram_traffic": True,
            })
        write_tsv(self.raw / "MEMORY_ACCOUNTING.tsv", memory_rows)
        lifetime_rows = [{
            "group": r["group"], "repeat": r["repeat"], "arm": r["arm"],
            "full_dense_gradient_materialized": r["full_dense_gradient_materialized"],
            "full_gradient_first_point": "classifier_dW_before_backbone" if r["arm"] == "B0_STRONG" else ("lookup_dense_dW_after_backbone" if r["arm"] == "S1_LATE_FULL" else "NEVER"),
            "full_gradient_last_point": "released_after_AdamW" if r["arm"] != "S2_LATE_TILED" else "NEVER",
            "full_gradient_lifetime_gpu_ms": "" if r["full_gradient_lifetime_gpu_ms"] is None else f"{r['full_gradient_lifetime_gpu_ms']:.9f}",
        } for r in samples]
        write_tsv(self.raw / "LIFETIME_TRACE.tsv", lifetime_rows)
        summary = {
            "decision": decision,
            "s2_no_full_gradient_all_formal": formal_s2_no_full,
            "s2_memory_reduction": memory_reduction,
            "s2_stable_regression_groups_vs_b0": s2_vs_b0_reg,
            "s2_stable_regression_groups_vs_s1": s2_vs_s1_reg,
            "median_target_peak_allocated_bytes": peak,
        }
        write_json(self.raw / "DECISION.json", summary)
        return summary

    def environment(self):
        write_json(self.raw / "ENVIRONMENT.json", {
            "python": sys.version,
            "torch": torch.__version__, "torch_cuda": torch.version.cuda,
            "transformers": importlib.metadata.version("transformers"),
            "triton": triton.__version__, "numpy": np.__version__,
            "cce_source": sys.modules["cut_cross_entropy"].__file__,
            "CCE_AUTOTUNE": os.environ.get("CCE_AUTOTUNE"),
            "CCE_DC_FIRST_STORE": os.environ.get("CCE_DC_FIRST_STORE"),
            "gpu": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)),
            "pid": os.getpid(),
        })

    def run(self):
        self.environment()
        self.bootstrap()
        self.qualify()
        samples = self.formal()
        summary = self.summarize(samples)
        print(json.dumps(summary, indent=2, sort_keys=True))


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--pack", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--tokens", required=True)
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    campaign = {"stage": "AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1", "status": "RUNNING"}
    try:
        Campaign(args).run()
    except Exception as exc:
        campaign.update({"status": "FAILED", "error": repr(exc), "traceback": traceback.format_exc()})
        root = Path(args.root) / "raw"
        root.mkdir(parents=True, exist_ok=True)
        write_json(root / "CAMPAIGN_FAILURE.json", campaign)
        raise
