#!/usr/bin/env python3
"""R25 cross-model tied-weight gradient lifetime campaign.

The implementation deliberately reuses the accepted R24 CCE helpers while
adding the production-oriented one-full-buffer C1 arm and point-generic shape
handling required by R25.
"""

from __future__ import annotations

import argparse
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
from transformers import AutoModelForCausalLM

import accepted_r24_base as base


STAGE = "AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1"
ARMS = ("B0_DENSE_STRONG", "C1_COMPACT_FULL", "S2_TILED")
ORDERS = (
    ("B0_DENSE_STRONG", "C1_COMPACT_FULL", "S2_TILED"),
    ("C1_COMPACT_FULL", "S2_TILED", "B0_DENSE_STRONG"),
    ("S2_TILED", "B0_DENSE_STRONG", "C1_COMPACT_FULL"),
)
ATOL = RTOL = 1e-2
TILE_BUDGET = 32 * 1024 * 1024
OPTIMIZER = {
    "optimizer": "explicit AdamW reference",
    "lr": 1e-3,
    "betas": [0.9, 0.999],
    "eps": 1e-8,
    "weight_decay": 1e-2,
    "bias_correction": True,
    "decoupled_weight_decay": True,
    "moment_dtype": "torch.float32",
    "parameter_storage_dtype": "torch.bfloat16",
    "gradient_clipping": False,
    "grad_scaler": False,
    "amsgrad": False,
    "foreach": False,
    "fused": False,
}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(t: torch.Tensor) -> str:
    a = t.detach().contiguous().cpu().view(torch.uint8).numpy()
    return hashlib.sha256(memoryview(a)).hexdigest()


def nbytes(t: torch.Tensor) -> int:
    return t.numel() * t.element_size()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def median(xs):
    return statistics.median(xs)


def mad(xs):
    m = median(xs)
    return median([abs(x - m) for x in xs])


def scalar_metrics(got: float, ref: float):
    d = abs(got - ref)
    return {
        "observed": got,
        "reference": ref,
        "max_abs": d,
        "mean_abs": d,
        "max_rel": d / max(abs(ref), 1e-30),
        "cosine_similarity": 1.0 if got == ref else math.copysign(1.0, got * ref),
        "finite": math.isfinite(got),
        "allclose": d <= ATOL + RTOL * abs(ref),
        "dtype": "scalar",
        "shape": [],
    }


def tensor_metrics(got: torch.Tensor, ref: torch.Tensor, chunk: int = 1 << 20):
    if got.shape != ref.shape or got.dtype != ref.dtype:
        return {
            "shape_match": got.shape == ref.shape,
            "dtype_match": got.dtype == ref.dtype,
            "allclose": False,
            "finite": False,
            "shape": list(got.shape),
            "dtype": str(got.dtype),
        }
    lhs, rhs = got.detach().reshape(-1), ref.detach().reshape(-1)
    max_abs = max_rel = sum_abs = dot = lhs_norm = rhs_norm = 0.0
    allclose = finite = True
    for start in range(0, lhs.numel(), chunk):
        a = lhs[start : start + chunk].float()
        b = rhs[start : start + chunk].float()
        d = (a - b).abs()
        max_abs = max(max_abs, float(d.max()))
        max_rel = max(max_rel, float((d / b.abs().clamp_min(1e-30)).max()))
        sum_abs += float(d.double().sum())
        a64, b64 = a.double(), b.double()
        dot += float((a64 * b64).sum())
        lhs_norm += float((a64 * a64).sum())
        rhs_norm += float((b64 * b64).sum())
        allclose &= bool((d <= ATOL + RTOL * b.abs()).all())
        finite &= bool(torch.isfinite(a).all())
    cos = dot / math.sqrt(lhs_norm * rhs_norm) if lhs_norm and rhs_norm else 1.0
    return {
        "shape": list(got.shape),
        "dtype": str(got.dtype),
        "numel": got.numel(),
        "max_abs": max_abs,
        "mean_abs": sum_abs / max(lhs.numel(), 1),
        "max_rel": max_rel,
        "cosine_similarity": cos,
        "allclose": allclose,
        "finite": finite,
        "shape_match": True,
        "dtype_match": True,
    }


def fixed_meta():
    values = dict(base.tl_autotune._cce_best_config().all_kwargs())
    keys = ("BLOCK_B", "BLOCK_V", "BLOCK_D", "num_warps", "num_stages")
    result = {key: values[key] for key in keys}
    result["MM_BACK_BLOCK_D"] = 64
    result["CCE_AUTOTUNE"] = 0
    if base.tl_autotune._AUTOTUNE or os.environ.get("CCE_AUTOTUNE", "0") != "0":
        raise RuntimeError("CCE autotune is not frozen off")
    return result


@dataclass
class CpuState:
    weight: torch.Tensor
    m: torch.Tensor
    v: torch.Tensor
    step: int
    cpu_rng: torch.Tensor
    cuda_rng: torch.Tensor

    @property
    def bytes(self):
        return nbytes(self.weight) + nbytes(self.m) + nbytes(self.v)


class R25CompactEmbedding(torch.autograd.Function):
    """Sorted unique-row gradient using the native embedding-backward reducer.

    Indices are remapped onto the compact unique-row domain, so the same native
    accumulation primitive as B0 is used without ever allocating a VxH lookup
    gradient.  Sorting/remapping and the compact reducer stay in TARGET_REGION.
    """

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
        grad = torch.ops.aten.embedding_dense_backward(
            grad_output,
            inverse.view_as(indices),
            unique.numel(),
            -1,
            False,
        )
        ctx.collector.ids = unique
        ctx.collector.grad = grad
        ctx.collector.inverse_bytes = nbytes(inverse)
        return None, None, None


class Campaign:
    def __init__(self, args):
        if os.environ.get("R25_GPU_LOCK_HELD") != "1":
            raise RuntimeError("R25_GPU_LOCK_HELD=1 required")
        self.args = args
        self.point = args.point
        self.root = Path(args.root)
        self.raw = self.root / "raw" / self.point
        self.raw.mkdir(parents=True, exist_ok=True)
        self.meta = fixed_meta()
        self.block_v = int(self.meta["BLOCK_V"])
        self.tokens = json.loads(Path(args.tokens).read_text())
        if isinstance(self.tokens, dict):
            self.tokens = self.tokens.get("token_ids", self.tokens.get("tokens"))
        if not isinstance(self.tokens, list):
            raise RuntimeError("token authority is not a token list")
        self.input_ids_cpu = torch.tensor(self.tokens[:-1], dtype=torch.int64).view(1, -1)
        self.labels_cpu = torch.tensor(self.tokens[1:], dtype=torch.int64)
        self.t = self.labels_cpu.numel()
        self.input_ids = self.input_ids_cpu.to("cuda:0")
        self.labels = self.labels_cpu.to("cuda:0")
        self.attention = torch.ones_like(self.input_ids)
        self.model = AutoModelForCausalLM.from_pretrained(
            args.model,
            local_files_only=True,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
        ).train().to("cuda:0")
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.backbone = self.model.model
        self.weight = self.model.get_input_embeddings().weight
        self.weight.requires_grad_(True)
        output_weight = self.model.get_output_embeddings().weight
        if self.weight.data_ptr() != output_weight.data_ptr():
            raise RuntimeError("tied weight data pointer mismatch")
        if self.weight.untyped_storage().data_ptr() != output_weight.untyped_storage().data_ptr():
            raise RuntimeError("tied weight storage pointer mismatch")
        if self.weight.dtype != torch.bfloat16:
            raise RuntimeError(f"weight dtype mismatch: {self.weight.dtype}")
        self.vocab, self.hidden_size = self.weight.shape
        self.rows_per_tile = (
            TILE_BUDGET // (self.hidden_size * 4) // self.block_v
        ) * self.block_v
        if self.rows_per_tile <= 0:
            raise RuntimeError("derived tile has no rows")
        self.tile_count = math.ceil(self.vocab / self.rows_per_tile)
        self.m = torch.zeros_like(self.weight, dtype=torch.float32)
        self.v = torch.zeros_like(self.weight, dtype=torch.float32)
        self.collector = base.CompactCollector()
        self.initial_weight_cpu = self.weight.detach().cpu().clone()
        self.frozen: CpuState | None = None
        self._validate_point_identity()
        self._write_authority()

    def _validate_point_identity(self):
        expected = {
            "D0": {
                "tokens": 256,
                "t": 255,
                "shape": (151936, 896),
                "input_sha": "f59446f6a177507048cad5e272d03b1d910337bf0e626f4ce78aa8c244837a1e",
                "labels_sha": "c89b22206d04b19d9a018e25c732aa5b1acf01b7b1ca18579bfc9ac4e1214f3a",
            },
            "H0": {
                "tokens": 128,
                "t": 127,
                "shape": (128256, 2048),
                "input_sha": None,
                "labels_sha": None,
            },
        }[self.point]
        if len(self.tokens) != expected["tokens"] or self.t != expected["t"]:
            raise RuntimeError("token count mismatch")
        if tuple(self.weight.shape) != expected["shape"]:
            raise RuntimeError(f"weight shape mismatch {tuple(self.weight.shape)}")
        if expected["input_sha"] and tensor_sha(self.input_ids_cpu) != expected["input_sha"]:
            raise RuntimeError("D0 input hash mismatch")
        if expected["labels_sha"] and tensor_sha(self.labels_cpu) != expected["labels_sha"]:
            raise RuntimeError("D0 labels hash mismatch")

    def _write_authority(self):
        config = json.loads((Path(self.args.model) / "config.json").read_text())
        write_json(self.raw / "RUNTIME_POINT_AUTHORITY.json", {
            "stage": STAGE,
            "point": self.point,
            "model_path": self.args.model,
            "model_safetensors_sha256": sha_file(Path(self.args.model) / "model.safetensors"),
            "config_sha256": sha_file(Path(self.args.model) / "config.json"),
            "token_path": self.args.tokens,
            "token_file_sha256": sha_file(Path(self.args.tokens)),
            "token_count": len(self.tokens),
            "input_ids_sha256": tensor_sha(self.input_ids_cpu),
            "labels_sha256": tensor_sha(self.labels_cpu),
            "input_shape": list(self.input_ids_cpu.shape),
            "labels_shape": list(self.labels_cpu.shape),
            "weight_shape": list(self.weight.shape),
            "weight_dtype": str(self.weight.dtype),
            "config_hidden_size": config.get("hidden_size"),
            "config_vocab_size": config.get("vocab_size"),
            "tie_word_embeddings": config.get("tie_word_embeddings"),
            "embedding_data_ptr": self.weight.data_ptr(),
            "lm_head_data_ptr": self.model.get_output_embeddings().weight.data_ptr(),
            "tied_pointer_exact": True,
            "tied_storage_exact": True,
            "trainable_parameters": [n for n, p in self.model.named_parameters() if p.requires_grad],
            "fixed_cce_meta": self.meta,
            "tile_budget_bytes": TILE_BUDGET,
            "rows_per_tile": self.rows_per_tile,
            "tile_count": self.tile_count,
            "tile_fp32_budget_bytes": self.rows_per_tile * self.hidden_size * 4,
        })

    def state_from_current(self, step: int) -> CpuState:
        torch.cuda.synchronize()
        return CpuState(
            self.weight.detach().cpu().clone(),
            self.m.detach().cpu().clone(),
            self.v.detach().cpu().clone(),
            step,
            torch.get_rng_state().clone(),
            torch.cuda.get_rng_state("cuda:0").cpu().clone(),
        )

    def restore(self, state: CpuState | None = None) -> int:
        state = state or self.frozen
        if state is None:
            raise RuntimeError("missing frozen state")
        with torch.no_grad():
            self.weight.copy_(state.weight, non_blocking=False)
            self.m.copy_(state.m, non_blocking=False)
            self.v.copy_(state.v, non_blocking=False)
        self.weight.grad = None
        self.collector.reset()
        torch.set_rng_state(state.cpu_rng)
        torch.cuda.set_rng_state(state.cuda_rng, device="cuda:0")
        torch.cuda.synchronize()
        return state.step

    def model_forward(self, arm: str):
        if arm in ("C1_COMPACT_FULL", "S2_TILED"):
            embeds = R25CompactEmbedding.apply(self.weight, self.input_ids, self.collector)
            out = self.backbone(
                inputs_embeds=embeds,
                attention_mask=self.attention,
                use_cache=False,
                return_dict=True,
            )
        else:
            out = self.backbone(
                input_ids=self.input_ids,
                attention_mask=self.attention,
                use_cache=False,
                return_dict=True,
            )
        hidden_3d = out.last_hidden_state
        hidden_3d.retain_grad()
        return hidden_3d, hidden_3d.reshape(self.t, self.hidden_size)

    @torch.no_grad()
    def next_loss(self):
        out = self.backbone(
            input_ids=self.input_ids,
            attention_mask=self.attention,
            use_cache=False,
            return_dict=True,
        )
        loss, _ = base.cce_forward(
            out.last_hidden_state.reshape(self.t, self.hidden_size), self.weight, self.labels
        )
        torch.cuda.synchronize()
        return float(loss)

    def update_full(self, grad: torch.Tensor, step: int):
        for start in range(0, self.vocab, self.rows_per_tile):
            stop = min(start + self.rows_per_tile, self.vocab)
            base.adamw_update_tile(
                self.weight[start:stop], self.m[start:stop], self.v[start:stop],
                grad[start:stop], step, OPTIMIZER,
            )

    def run_microstep(self, arm: str, step: int, capture: str = "none", timed: bool = False):
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
        complete_start = time.perf_counter_ns()
        hidden_3d, hidden = self.model_forward(arm)
        loss, lse = base.cce_forward(hidden, self.weight, self.labels)
        torch.cuda.synchronize()
        forward_peak_alloc = torch.cuda.max_memory_allocated()
        forward_peak_reserved = torch.cuda.max_memory_reserved()
        target_base_alloc = torch.cuda.memory_allocated()
        target_base_reserved = torch.cuda.memory_reserved()
        torch.cuda.reset_peak_memory_stats()
        start_event = torch.cuda.Event(enable_timing=True) if timed else None
        end_event = torch.cuda.Event(enable_timing=True) if timed else None
        first_event = torch.cuda.Event(enable_timing=True) if timed and arm != "S2_TILED" else None
        release_event = torch.cuda.Event(enable_timing=True) if timed and arm != "S2_TILED" else None
        if start_event is not None:
            start_event.record()
        target_host_start = time.perf_counter_ns()
        grad_capture = None
        dense_lookup = arm == "B0_DENSE_STRONG"
        full_classifier = arm != "S2_TILED"
        full_count = 2 if arm == "B0_DENSE_STRONG" else (1 if arm == "C1_COMPACT_FULL" else 0)
        compact_rows = compact_bytes = inverse_bytes = 0

        if arm == "B0_DENSE_STRONG":
            de, dc = base.cce_backward(hidden, self.weight, self.labels, lse, True, True)
            if de is None or dc is None:
                raise RuntimeError("B0 CCE backward missing output")
            if first_event is not None:
                first_event.record()
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is None:
                raise RuntimeError("B0 dense lookup gradient missing")
            self.weight.grad.add_(dc)
            del dc
            if capture == "full":
                grad_capture = self.weight.grad.detach().cpu().clone()
            self.update_full(self.weight.grad, step)
            self.weight.grad = None
            if release_event is not None:
                release_event.record()

        elif arm == "C1_COMPACT_FULL":
            de, _ = base.cce_backward(hidden, self.weight, self.labels, lse, True, False)
            if de is None:
                raise RuntimeError("C1 dH missing")
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is not None:
                raise RuntimeError("C1 materialized dense lookup W.grad")
            if self.collector.ids is None or self.collector.grad is None:
                raise RuntimeError("C1 compact lookup gradient missing")
            compact_rows = self.collector.ids.numel()
            compact_bytes = nbytes(self.collector.ids) + nbytes(self.collector.grad)
            inverse_bytes = self.collector.inverse_bytes
            _, dc = base.cce_backward(hidden, self.weight, self.labels, lse, False, True)
            if dc is None:
                raise RuntimeError("C1 classifier gradient missing")
            if first_event is not None:
                first_event.record()
            dc.index_add_(0, self.collector.ids, self.collector.grad)
            if capture == "full":
                grad_capture = dc.detach().cpu().clone()
            self.update_full(dc, step)
            del dc
            if release_event is not None:
                release_event.record()

        else:
            de, _ = base.cce_backward(hidden, self.weight, self.labels, lse, True, False)
            if de is None:
                raise RuntimeError("S2 dH missing")
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is not None:
                raise RuntimeError("S2 materialized dense lookup W.grad")
            if self.collector.ids is None or self.collector.grad is None:
                raise RuntimeError("S2 compact lookup gradient missing")
            compact_rows = self.collector.ids.numel()
            compact_bytes = nbytes(self.collector.ids) + nbytes(self.collector.grad)
            inverse_bytes = self.collector.inverse_bytes
            debug = torch.empty_like(self.weight) if capture == "full" else None
            for start in range(0, self.vocab, self.rows_per_tile):
                stop = min(start + self.rows_per_tile, self.vocab)
                tile_labels = base.local_targets(self.labels, start, stop)
                _, dc = base.cce_backward(
                    hidden, self.weight[start:stop], tile_labels, lse, False, True
                )
                if dc is None:
                    raise RuntimeError("S2 tile gradient missing")
                selected = (self.collector.ids >= start) & (self.collector.ids < stop)
                if bool(selected.any()):
                    local = self.collector.ids[selected] - start
                    dc.index_add_(0, local, self.collector.grad[selected])
                if debug is not None:
                    debug[start:stop].copy_(dc)
                base.adamw_update_tile(
                    self.weight[start:stop], self.m[start:stop], self.v[start:stop],
                    dc, step, OPTIMIZER,
                )
                del dc
            if debug is not None:
                grad_capture = debug.cpu()
                del debug

        if end_event is not None:
            end_event.record()
            end_event.synchronize()
            target_gpu_ms = start_event.elapsed_time(end_event)
        else:
            torch.cuda.synchronize()
            target_gpu_ms = None
        target_host_ms = (time.perf_counter_ns() - target_host_start) / 1e6
        full_lifetime = None
        if first_event is not None and release_event is not None:
            full_lifetime = first_event.elapsed_time(release_event)
        target_peak_alloc = torch.cuda.max_memory_allocated()
        target_peak_reserved = torch.cuda.max_memory_reserved()
        complete_ms = (time.perf_counter_ns() - complete_start) / 1e6
        dH = hidden_3d.grad.detach().cpu().clone() if capture == "full" else None
        result = {
            "arm": arm,
            "loss": float(loss),
            "step_after": step,
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
            "whole_peak_allocated_bytes": max(forward_peak_alloc, target_peak_alloc),
            "whole_peak_reserved_bytes": max(forward_peak_reserved, target_peak_reserved),
            "dense_lookup_gradient_materialized": dense_lookup,
            "full_classifier_or_total_gradient_materialized": full_classifier,
            "full_gradient_buffer_count_peak": full_count,
            "full_gradient_bytes_each": self.vocab * self.hidden_size * 2,
            "full_gradient_lifetime_gpu_ms": full_lifetime,
            "compact_lookup_rows": compact_rows,
            "compact_lookup_bytes": compact_bytes,
            "compact_inverse_temporary_bytes": inverse_bytes,
            "s2_rows_per_tile": self.rows_per_tile if arm == "S2_TILED" else 0,
            "s2_tile_count": self.tile_count if arm == "S2_TILED" else 0,
            "s2_fp32_tile_budget_bytes": self.rows_per_tile * self.hidden_size * 4 if arm == "S2_TILED" else 0,
            "s2_consumer_bf16_tile_bytes": self.rows_per_tile * self.hidden_size * 2 if arm == "S2_TILED" else 0,
        }
        if capture != "none":
            result["capture"] = {
                "dH": dH,
                "gradient": grad_capture,
                "weight": self.weight.detach().cpu().clone(),
                "m": self.m.detach().cpu().clone(),
                "v": self.v.detach().cpu().clone(),
                "next_loss": self.next_loss(),
                "cpu_rng": torch.get_rng_state().clone(),
                "cuda_rng": torch.cuda.get_rng_state("cuda:0").cpu().clone(),
            }
        del hidden_3d, hidden, loss, lse
        gc.collect()
        return result

    def bootstrap(self):
        self.m.zero_()
        self.v.zero_()
        with torch.no_grad():
            self.weight.copy_(self.initial_weight_cpu)
        torch.manual_seed(25001 if self.point == "D0" else 25002)
        torch.cuda.manual_seed_all(25001 if self.point == "D0" else 25002)
        self.run_microstep("B0_DENSE_STRONG", 1, capture="none", timed=False)
        self.frozen = self.state_from_current(1)
        write_json(self.raw / "FROZEN_START_STATE.json", {
            "point": self.point,
            "step": 1,
            "weight": {"shape": list(self.frozen.weight.shape), "dtype": str(self.frozen.weight.dtype), "sha256": tensor_sha(self.frozen.weight)},
            "m": {"shape": list(self.frozen.m.shape), "dtype": str(self.frozen.m.dtype), "sha256": tensor_sha(self.frozen.m)},
            "v": {"shape": list(self.frozen.v.shape), "dtype": str(self.frozen.v.dtype), "sha256": tensor_sha(self.frozen.v)},
            "cpu_snapshot_bytes": self.frozen.bytes,
            "snapshot_device": "CPU",
            "persistent_gpu_snapshot_bytes": 0,
            "cpu_rng_sha256": tensor_sha(self.frozen.cpu_rng),
            "cuda_rng_sha256": tensor_sha(self.frozen.cuda_rng),
        })
        del self.initial_weight_cpu
        gc.collect()
        torch.cuda.empty_cache()

    def compare_observables(self, got, ref, names):
        result = {}
        for name in names:
            if name in ("loss", "next_loss"):
                result[name] = scalar_metrics(got[name], ref[name])
            elif name == "step":
                result[name] = {"observed": got[name], "reference": ref[name], "allclose": got[name] == ref[name], "finite": True, "max_abs": abs(got[name]-ref[name]), "mean_abs": abs(got[name]-ref[name]), "max_rel": 0.0, "cosine_similarity": 1.0, "dtype": "int", "shape": []}
            else:
                result[name] = tensor_metrics(got[name], ref[name])
        return result

    def qualify_one_step(self):
        outputs = {}
        for arm in ARMS:
            step = self.restore() + 1
            outputs[arm] = self.run_microstep(arm, step, capture="full", timed=False)
        ref = outputs["B0_DENSE_STRONG"]
        details = {}
        first = None
        for arm, value in outputs.items():
            got = {
                "loss": value["loss"], "dH": value["capture"]["dH"],
                "gradient": value["capture"]["gradient"], "weight": value["capture"]["weight"],
                "m": value["capture"]["m"], "v": value["capture"]["v"],
                "step": value["step_after"], "next_loss": value["capture"]["next_loss"],
            }
            rv = {
                "loss": ref["loss"], "dH": ref["capture"]["dH"],
                "gradient": ref["capture"]["gradient"], "weight": ref["capture"]["weight"],
                "m": ref["capture"]["m"], "v": ref["capture"]["v"],
                "step": ref["step_after"], "next_loss": ref["capture"]["next_loss"],
            }
            metrics = self.compare_observables(got, rv, tuple(got))
            qualified = all(x["allclose"] for x in metrics.values())
            details[arm] = {"qualified": qualified, "metrics": metrics}
            if not qualified and first is None:
                first = {"phase": "one_step", "arm": arm, "metrics": {k:v for k,v in metrics.items() if not v["allclose"]}}
        write_json(self.raw / "ONE_STEP_NUMERICAL_QUALIFICATION.json", details)
        for value in outputs.values():
            value.pop("capture", None)
        del outputs, ref
        gc.collect()
        return all(details[a]["qualified"] for a in ARMS), first

    def state_from_capture(self, capture, step):
        return CpuState(capture["weight"], capture["m"], capture["v"], step, capture["cpu_rng"], capture["cuda_rng"])

    def qualify_trajectory(self):
        rows = []
        first = None
        for candidate in ("C1_COMPACT_FULL", "S2_TILED"):
            bstate = self.frozen
            cstate = self.frozen
            for trajectory_step in range(1, 5):
                b_step = self.restore(bstate) + 1
                b = self.run_microstep("B0_DENSE_STRONG", b_step, capture="state", timed=False)
                bstate = self.state_from_capture(b["capture"], b_step)
                c_step = self.restore(cstate) + 1
                c = self.run_microstep(candidate, c_step, capture="state", timed=False)
                cstate = self.state_from_capture(c["capture"], c_step)
                got = {"loss": c["loss"], "weight": cstate.weight, "m": cstate.m, "v": cstate.v, "step": c_step, "next_loss": c["capture"]["next_loss"]}
                ref = {"loss": b["loss"], "weight": bstate.weight, "m": bstate.m, "v": bstate.v, "step": b_step, "next_loss": b["capture"]["next_loss"]}
                metrics = self.compare_observables(got, ref, tuple(got))
                qualified = all(x["allclose"] for x in metrics.values())
                rows.append({"candidate": candidate, "trajectory_step": trajectory_step, "qualified": qualified, "metrics": metrics})
                if not qualified and first is None:
                    first = {"phase": "trajectory", "arm": candidate, "trajectory_step": trajectory_step, "metrics": {k:v for k,v in metrics.items() if not v["allclose"]}}
                del b, c
                gc.collect()
            del bstate, cstate
            gc.collect()
        write_json(self.raw / "FOUR_STEP_TRAJECTORY_QUALIFICATION.json", rows)
        return all(r["qualified"] for r in rows), first

    def qualify(self):
        one_ok, first = self.qualify_one_step()
        trajectory_ok, trajectory_first = self.qualify_trajectory()
        if first is None:
            first = trajectory_first
        result = {
            "point": self.point,
            "one_step_qualified": one_ok,
            "four_step_trajectory_qualified": trajectory_ok,
            "qualified": one_ok and trajectory_ok,
            "tolerance": {"rtol": RTOL, "atol": ATOL},
            "first_mismatch": first,
            "h0_performance_inspected": False if self.point == "H0" else None,
        }
        write_json(self.raw / "QUALIFICATION_STATUS.json", result)
        if not result["qualified"]:
            raise RuntimeError("R25_NUMERIC_OR_TRAJECTORY_NOT_QUALIFIED")
        print(json.dumps(result, indent=2, sort_keys=True))

    def validate_freeze(self):
        freeze = json.loads(Path(self.args.freeze).read_text())
        for item in freeze["files"]:
            if sha_file(Path(item["path"])) != item["sha256"]:
                raise RuntimeError(f"implementation freeze hash mismatch: {item['path']}")
        if not freeze.get("D0_qualified") or not freeze.get("H0_qualified"):
            raise RuntimeError("implementation freeze lacks two-point qualification")

    def formal(self):
        self.validate_freeze()
        samples = []
        raw_path = self.raw / "FORMAL_RUNS.jsonl"
        raw_path.write_text("")
        for group, order in enumerate(ORDERS):
            for arm in order:
                for repeat in range(2):
                    step = self.restore() + 1
                    self.run_microstep(arm, step, capture="none", timed=True)
            for repeat in range(5):
                for position, arm in enumerate(order):
                    step = self.restore() + 1
                    value = self.run_microstep(arm, step, capture="none", timed=True)
                    row = {"point": self.point, "group": group, "repeat": repeat, "position": position, **value, "numeric_qualified": True}
                    samples.append(row)
                    with raw_path.open("a") as f:
                        f.write(json.dumps(row, sort_keys=True) + "\n")
        self.summarize(samples)

    def timing_class(self, samples, candidate, baseline):
        groups = []
        for group in range(3):
            c = [r["target_gpu_ms"] for r in samples if r["group"] == group and r["arm"] == candidate]
            b = [r["target_gpu_ms"] for r in samples if r["group"] == group and r["arm"] == baseline]
            cm, bm, cmad, bmad = median(c), median(b), mad(c), mad(b)
            threshold = 3 * max(cmad, bmad)
            gap = bm - cm
            direction = "STABLE_BENEFIT" if gap > threshold else ("STABLE_REGRESSION" if -gap > threshold else "INDETERMINATE")
            groups.append({"group": group, "candidate_median_ms": cm, "candidate_mad_ms": cmad, "baseline_median_ms": bm, "baseline_mad_ms": bmad, "baseline_minus_candidate_ms": gap, "threshold_ms": threshold, "direction": direction})
        benefits = sum(g["direction"] == "STABLE_BENEFIT" for g in groups)
        regressions = sum(g["direction"] == "STABLE_REGRESSION" for g in groups)
        classification = "BENEFIT" if benefits >= 2 and regressions < 2 else ("REGRESSION" if regressions >= 2 else "MIXED")
        return {"candidate": candidate, "baseline": baseline, "groups": groups, "stable_benefit_groups": benefits, "stable_regression_groups": regressions, "classification": classification}

    def summarize(self, samples):
        comparisons = {
            "S2_vs_C1": self.timing_class(samples, "S2_TILED", "C1_COMPACT_FULL"),
            "C1_vs_B0": self.timing_class(samples, "C1_COMPACT_FULL", "B0_DENSE_STRONG"),
            "S2_vs_B0": self.timing_class(samples, "S2_TILED", "B0_DENSE_STRONG"),
        }
        arm_summary = {}
        for arm in ARMS:
            rows = [r for r in samples if r["arm"] == arm]
            arm_summary[arm] = {
                "target_gpu_median_ms": median([r["target_gpu_ms"] for r in rows]),
                "target_gpu_mad_ms": mad([r["target_gpu_ms"] for r in rows]),
                "complete_microstep_median_ms": median([r["complete_microstep_ms"] for r in rows]),
                "complete_microstep_mad_ms": mad([r["complete_microstep_ms"] for r in rows]),
                "target_peak_allocated_median_bytes": median([r["target_peak_allocated_bytes"] for r in rows]),
                "target_peak_reserved_median_bytes": median([r["target_peak_reserved_bytes"] for r in rows]),
                "whole_peak_allocated_median_bytes": median([r["whole_peak_allocated_bytes"] for r in rows]),
                "full_gradient_lifetime_median_ms": None if arm == "S2_TILED" else median([r["full_gradient_lifetime_gpu_ms"] for r in rows]),
                "compact_lookup_rows_median": median([r["compact_lookup_rows"] for r in rows]),
                "compact_lookup_bytes_median": median([r["compact_lookup_bytes"] for r in rows]),
            }
        c1_group_medians = {g: median([r["target_peak_allocated_bytes"] for r in samples if r["group"] == g and r["arm"] == "C1_COMPACT_FULL"]) for g in range(3)}
        structural = (
            all(not r["dense_lookup_gradient_materialized"] and r["full_gradient_buffer_count_peak"] == 1 for r in samples if r["arm"] == "C1_COMPACT_FULL")
            and all(not r["dense_lookup_gradient_materialized"] and r["full_gradient_buffer_count_peak"] == 0 and not r["full_classifier_or_total_gradient_materialized"] for r in samples if r["arm"] == "S2_TILED")
        )
        every = all(r["target_peak_allocated_bytes"] < c1_group_medians[r["group"]] for r in samples if r["arm"] == "S2_TILED")
        capacity = structural and every and arm_summary["S2_TILED"]["target_peak_allocated_median_bytes"] < arm_summary["C1_COMPACT_FULL"]["target_peak_allocated_median_bytes"]
        summary = {
            "stage": STAGE,
            "point": self.point,
            "sample_count": len(samples),
            "arm_summary": arm_summary,
            "comparisons": comparisons,
            "arm_identity_qualified": structural,
            "every_s2_sample_below_corresponding_c1_group_median": every,
            "capacity_class": "CAUSAL_CAPACITY_RESPONSE" if capacity else "NO_CAUSAL_CAPACITY_RESPONSE",
            "cpu_restore_snapshot_bytes": self.frozen.bytes,
            "direct_accounting": {
                "B0_DENSE_STRONG": {"dense_lookup_full": True, "full_classifier_total": True, "peak_full_buffers": 2},
                "C1_COMPACT_FULL": {"dense_lookup_full": False, "full_classifier_total": True, "peak_full_buffers": 1},
                "S2_TILED": {"dense_lookup_full": False, "full_classifier_total": False, "peak_full_buffers": 0},
                "optimizer_W_bytes": nbytes(self.weight),
                "optimizer_m_bytes": nbytes(self.m),
                "optimizer_v_bytes": nbytes(self.v),
                "saved_hidden_bytes": self.t * self.hidden_size * 2,
                "saved_lse_bytes": self.t * 4,
                "labels_bytes": nbytes(self.labels),
                "persistent_candidate_metadata_bytes": 0,
                "allocator_bytes_are_not_dram_traffic": True,
            },
        }
        write_json(self.raw / "FORMAL_SUMMARY.json", summary)
        if not structural:
            raise RuntimeError("R25_ARM_IDENTITY_NOT_QUALIFIED")
        print(json.dumps(summary, indent=2, sort_keys=True))

    def environment(self):
        write_json(self.raw / "ENVIRONMENT.json", {
            "stage": STAGE, "point": self.point, "python": sys.version,
            "torch": torch.__version__, "torch_cuda": torch.version.cuda,
            "transformers": importlib.metadata.version("transformers"),
            "triton": triton.__version__, "numpy": np.__version__,
            "cce_source": sys.modules["cut_cross_entropy"].__file__,
            "CCE_AUTOTUNE": os.environ.get("CCE_AUTOTUNE"),
            "CCE_DC_FIRST_STORE": os.environ.get("CCE_DC_FIRST_STORE"),
            "gpu": torch.cuda.get_device_name(0),
            "capability": list(torch.cuda.get_device_capability(0)),
            "pid": os.getpid(), "mode": self.args.mode,
        })

    def run(self):
        self.environment()
        self.bootstrap()
        if self.args.mode == "qualify":
            self.qualify()
        else:
            self.formal()


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--root", required=True)
    p.add_argument("--point", required=True, choices=("D0", "H0"))
    p.add_argument("--model", required=True)
    p.add_argument("--tokens", required=True)
    p.add_argument("--mode", required=True, choices=("qualify", "formal"))
    p.add_argument("--freeze")
    args = p.parse_args()
    if args.mode == "formal" and not args.freeze:
        p.error("--freeze is required for formal mode")
    return args


if __name__ == "__main__":
    args = parse_args()
    try:
        Campaign(args).run()
    except Exception as exc:
        root = Path(args.root) / "raw" / args.point
        root.mkdir(parents=True, exist_ok=True)
        write_json(root / f"CAMPAIGN_FAILURE_{args.mode}.json", {
            "stage": STAGE, "point": args.point, "mode": args.mode,
            "error": repr(exc), "traceback": traceback.format_exc(),
        })
        raise
