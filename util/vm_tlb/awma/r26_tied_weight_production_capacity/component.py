#!/usr/bin/env python3
"""Integrated tied-weight-only training component for AWMA R26.

The component intentionally supports only the frozen R26 contract: one tied
input-embedding/lm-head weight is trainable, the backbone is frozen but remains
in the gradient path, and the only policies are C1 (default) and explicit S2.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import torch


R25_DIR = Path(__file__).resolve().parents[1] / "r25_tied_weight_broader_validation"
sys.path.insert(0, str(R25_DIR))
import accepted_r24_base as base  # noqa: E402
from run_r25_campaign import OPTIMIZER, R25CompactEmbedding, fixed_meta  # noqa: E402


STAGE = "AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1"
MODEL_ID = "meta-llama/Llama-3.2-1B"
REVISION = "4e20de362430cd3b72f300e6b0f18e50e7166e08"
V, H, T = 128256, 2048, 127
ATOL = RTOL = 1e-2
BLOCK_V = 128
ROWS_PER_TILE = 4096
TILE_COUNT = 32
TILE_BUDGET = 32 * 1024 * 1024
POLICIES = ("c1", "s2")
IDENTITY = {
    "stage": STAGE,
    "model_id": MODEL_ID,
    "revision": REVISION,
    "weight_shape": [V, H],
    "weight_dtype": "torch.bfloat16",
    "optimizer": OPTIMIZER,
    "input_authority": "ADOPTED_LLAMA_S0_T128_V1",
    "shifted_positions": T,
}


def sha_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tensor_sha(tensor: torch.Tensor) -> str:
    value = tensor.detach().contiguous().cpu().view(torch.uint8).numpy()
    return hashlib.sha256(memoryview(value)).hexdigest()


def nbytes(tensor: torch.Tensor) -> int:
    return tensor.numel() * tensor.element_size()


def canonical_sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


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
        "shape": [],
        "dtype": "scalar",
    }


def tensor_metrics(got: torch.Tensor, ref: torch.Tensor, max_chunk_bytes: int = 64 * 1024 * 1024):
    if got.shape != ref.shape or got.dtype != ref.dtype:
        return {
            "shape": list(got.shape), "dtype": str(got.dtype),
            "shape_match": got.shape == ref.shape,
            "dtype_match": got.dtype == ref.dtype,
            "finite": False, "allclose": False,
        }
    lhs, rhs = got.detach().reshape(-1), ref.detach().reshape(-1)
    chunk = max(1, max_chunk_bytes // max(lhs.element_size(), rhs.element_size()))
    max_abs = max_rel = sum_abs = dot = lhs_norm = rhs_norm = 0.0
    finite = allclose = True
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
        finite &= bool(torch.isfinite(a).all())
        allclose &= bool((d <= ATOL + RTOL * b.abs()).all())
    cosine = dot / math.sqrt(lhs_norm * rhs_norm) if lhs_norm and rhs_norm else 1.0
    return {
        "shape": list(got.shape), "dtype": str(got.dtype), "numel": got.numel(),
        "max_abs": max_abs, "mean_abs": sum_abs / max(lhs.numel(), 1),
        "max_rel": max_rel, "cosine_similarity": cosine,
        "finite": finite, "allclose": allclose,
        "shape_match": True, "dtype_match": True,
    }


def state_metrics(got: dict, ref: dict):
    result = {}
    for name in ("weight", "m", "v"):
        result[name] = tensor_metrics(got[name], ref[name])
    result["step"] = {
        "observed": got["step"], "reference": ref["step"],
        "max_abs": abs(got["step"] - ref["step"]), "mean_abs": abs(got["step"] - ref["step"]),
        "max_rel": 0.0, "cosine_similarity": 1.0,
        "finite": True, "allclose": got["step"] == ref["step"],
        "shape": [], "dtype": "int",
    }
    return result


def compare_observables(got: dict, ref: dict, names):
    out = {}
    for name in names:
        if name in ("loss", "next_loss"):
            out[name] = scalar_metrics(float(got[name]), float(ref[name]))
        elif name == "step":
            out[name] = state_metrics({"weight": torch.empty(0), "m": torch.empty(0), "v": torch.empty(0), "step": got[name]}, {"weight": torch.empty(0), "m": torch.empty(0), "v": torch.empty(0), "step": ref[name]})["step"]
        else:
            out[name] = tensor_metrics(got[name], ref[name])
    return out


@dataclass
class BatchBinding:
    batch: int
    input_ids_cpu: torch.Tensor
    labels_cpu: torch.Tensor
    input_ids_sha256: str
    labels_sha256: str


def make_batch(tokens_path: str | Path, batch: int) -> BatchBinding:
    tokens = json.loads(Path(tokens_path).read_text())
    if not isinstance(tokens, list) or len(tokens) != 128:
        raise RuntimeError("frozen token authority mismatch")
    base_input = torch.tensor(tokens[:-1], dtype=torch.int64).view(1, T)
    base_labels = torch.tensor(tokens[1:], dtype=torch.int64).view(1, T)
    input_ids = base_input.repeat(batch, 1).contiguous()
    labels = base_labels.repeat(batch, 1).contiguous()
    return BatchBinding(batch, input_ids, labels, tensor_sha(input_ids), tensor_sha(labels))


class TiedWeightTrainer:
    """One model instance and one W/m/v state with C1 default and S2 opt-in."""

    def __init__(self, model_path: str, tokens_path: str, batch: int, checkpoint: str | None = None):
        if os.environ.get("R26_GPU_LOCK_HELD") != "1":
            raise RuntimeError("R26_GPU_LOCK_HELD=1 required")
        if batch < 1 or batch > 512:
            raise RuntimeError("physical batch outside frozen range")
        self.model_path = Path(model_path)
        self.tokens_path = Path(tokens_path)
        self.binding = make_batch(tokens_path, batch)
        self.batch = batch
        self.meta = fixed_meta()
        expected_meta = {
            "BLOCK_B": 128, "BLOCK_V": 128, "BLOCK_D": 32,
            "num_warps": 4, "num_stages": 4,
            "MM_BACK_BLOCK_D": 64, "CCE_AUTOTUNE": 0,
        }
        if self.meta != expected_meta or base.tl_autotune._AUTOTUNE:
            raise RuntimeError(f"CCE meta mismatch: {self.meta}")
        from transformers import AutoModelForCausalLM
        self.model = AutoModelForCausalLM.from_pretrained(
            str(self.model_path), local_files_only=True, torch_dtype=torch.bfloat16,
            attn_implementation="sdpa",
        ).train().to("cuda:0")
        for p in self.model.parameters():
            p.requires_grad_(False)
        self.backbone = self.model.model
        self.weight = self.model.get_input_embeddings().weight
        self.weight.requires_grad_(True)
        output_weight = self.model.get_output_embeddings().weight
        self._assert_tied(output_weight)
        if tuple(self.weight.shape) != (V, H) or self.weight.dtype != torch.bfloat16:
            raise RuntimeError("tied W identity mismatch")
        if [n for n, p in self.model.named_parameters() if p.requires_grad] != ["model.embed_tokens.weight"]:
            raise RuntimeError("trainable parameter set mismatch")
        self.m = torch.zeros_like(self.weight, dtype=torch.float32)
        self.v = torch.zeros_like(self.weight, dtype=torch.float32)
        self.step = 0
        self.phase = "INITIALIZED"
        self.collector = base.CompactCollector()
        self.input_ids = self.binding.input_ids_cpu.to("cuda:0")
        self.labels = self.binding.labels_cpu.to("cuda:0").reshape(-1)
        self.attention = torch.ones_like(self.input_ids)
        if checkpoint:
            self.load_checkpoint(checkpoint)

    def _assert_tied(self, output_weight=None):
        output_weight = output_weight if output_weight is not None else self.model.get_output_embeddings().weight
        if self.weight.data_ptr() != output_weight.data_ptr():
            raise RuntimeError("tied data pointer mismatch")
        if self.weight.untyped_storage().data_ptr() != output_weight.untyped_storage().data_ptr():
            raise RuntimeError("tied storage mismatch")

    def authority(self):
        return {
            "identity": IDENTITY,
            "model_path": str(self.model_path),
            "model_safetensors_sha256": sha_file(self.model_path / "model.safetensors"),
            "config_sha256": sha_file(self.model_path / "config.json"),
            "tokens_path": str(self.tokens_path), "tokens_sha256": sha_file(self.tokens_path),
            "batch": self.batch, "input_shape": list(self.input_ids.shape),
            "labels_shape": list(self.labels.shape),
            "input_ids_sha256": self.binding.input_ids_sha256,
            "labels_sha256": self.binding.labels_sha256,
            "tied_pointer_exact": True, "tied_storage_exact": True,
            "trainable_parameters": [n for n, p in self.model.named_parameters() if p.requires_grad],
            "fixed_cce_meta": self.meta,
            "default_policy": "c1", "capacity_policy_requires_explicit_opt_in": "s2",
        }

    def _checkpoint_identity(self):
        return {
            "model_id": MODEL_ID, "revision": REVISION,
            "weight_shape": [V, H], "weight_dtype": "torch.bfloat16",
            "optimizer_sha256": canonical_sha(OPTIMIZER),
            "tokens_sha256": sha_file(self.tokens_path),
        }

    def snapshot_cpu(self, policy: str):
        torch.cuda.synchronize()
        return {
            "schema": "R26_TIED_WEIGHT_CHECKPOINT_V1",
            "identity": self._checkpoint_identity(),
            "policy_metadata": policy,
            "weight": self.weight.detach().cpu().clone(),
            "m": self.m.detach().cpu().clone(),
            "v": self.v.detach().cpu().clone(),
            "step": int(self.step),
            "cpu_rng": torch.get_rng_state().clone(),
            "cuda_rng": torch.cuda.get_rng_state("cuda:0").cpu().clone(),
            "contains_gpu_tensor": False,
        }

    def save_checkpoint(self, path: str | Path, policy: str):
        state = self.snapshot_cpu(policy)
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(state, path)
        receipt = {
            "path": str(path), "bytes": path.stat().st_size, "sha256": sha_file(path),
            "step": state["step"], "policy_metadata": policy,
            "weight_sha256": tensor_sha(state["weight"]),
            "m_sha256": tensor_sha(state["m"]), "v_sha256": tensor_sha(state["v"]),
            "cpu_rng_sha256": tensor_sha(state["cpu_rng"]),
            "cuda_rng_sha256": tensor_sha(state["cuda_rng"]),
            "contains_gpu_tensor": False,
        }
        return state, receipt

    def load_checkpoint(self, path: str | Path):
        state = torch.load(path, map_location="cpu", weights_only=False)
        if state.get("schema") != "R26_TIED_WEIGHT_CHECKPOINT_V1":
            raise RuntimeError("unsupported checkpoint schema")
        if state.get("identity") != self._checkpoint_identity():
            raise RuntimeError("checkpoint identity mismatch")
        for name in ("weight", "m", "v", "cpu_rng", "cuda_rng"):
            if not isinstance(state.get(name), torch.Tensor) or state[name].device.type != "cpu":
                raise RuntimeError(f"checkpoint {name} is not CPU tensor")
        if tuple(state["weight"].shape) != (V, H) or state["weight"].dtype != torch.bfloat16:
            raise RuntimeError("checkpoint W mismatch")
        if tuple(state["m"].shape) != (V, H) or state["m"].dtype != torch.float32:
            raise RuntimeError("checkpoint m mismatch")
        if tuple(state["v"].shape) != (V, H) or state["v"].dtype != torch.float32:
            raise RuntimeError("checkpoint v mismatch")
        with torch.no_grad():
            self.weight.copy_(state["weight"], non_blocking=False)
            self.m.copy_(state["m"], non_blocking=False)
            self.v.copy_(state["v"], non_blocking=False)
        self.step = int(state["step"])
        self.weight.grad = None
        self.collector.reset()
        torch.set_rng_state(state["cpu_rng"])
        torch.cuda.set_rng_state(state["cuda_rng"], device="cuda:0")
        torch.cuda.synchronize()
        self._assert_tied()
        return state

    def _model_forward(self, policy: str):
        if policy in POLICIES:
            embeds = R25CompactEmbedding.apply(self.weight, self.input_ids, self.collector)
            out = self.backbone(inputs_embeds=embeds, attention_mask=self.attention, use_cache=False, return_dict=True)
        elif policy == "b0":
            out = self.backbone(input_ids=self.input_ids, attention_mask=self.attention, use_cache=False, return_dict=True)
        else:
            raise ValueError(policy)
        hidden_3d = out.last_hidden_state
        return hidden_3d, hidden_3d.reshape(self.batch * T, H)

    @torch.no_grad()
    def next_loss(self):
        out = self.backbone(input_ids=self.input_ids, attention_mask=self.attention, use_cache=False, return_dict=True)
        loss, _ = base.cce_forward(out.last_hidden_state.reshape(self.batch * T, H), self.weight, self.labels)
        torch.cuda.synchronize()
        return float(loss)

    def _update_full(self, grad, step):
        for start in range(0, V, ROWS_PER_TILE):
            stop = min(start + ROWS_PER_TILE, V)
            base.adamw_update_tile(self.weight[start:stop], self.m[start:stop], self.v[start:stop], grad[start:stop], step, OPTIMIZER)

    def run_step(self, policy: str = "c1", *, diagnostic: bool = False, timed: bool = False):
        if policy not in ("b0", "c1", "s2"):
            raise ValueError(policy)
        if policy == "s2" and os.environ.get("R26_ALLOW_S2", "0") != "1":
            raise RuntimeError("S2 requires explicit R26_ALLOW_S2=1 opt-in")
        self.weight.grad = None
        self.collector.reset()
        next_step = self.step + 1
        torch.cuda.synchronize()
        pre_alloc = torch.cuda.memory_allocated()
        pre_reserved = torch.cuda.memory_reserved()
        torch.cuda.reset_peak_memory_stats()
        complete_host_start = time.perf_counter_ns()
        self.phase = "FORWARD_BACKBONE"
        hidden_3d, hidden = self._model_forward(policy)
        forward_peak_alloc = torch.cuda.max_memory_allocated()
        forward_peak_reserved = torch.cuda.max_memory_reserved()
        self.phase = "CCE_FORWARD"
        loss, lse = base.cce_forward(hidden, self.weight, self.labels)
        torch.cuda.synchronize()
        pre_target_alloc = torch.cuda.memory_allocated()
        pre_target_reserved = torch.cuda.memory_reserved()
        torch.cuda.reset_peak_memory_stats()
        target_start = torch.cuda.Event(enable_timing=True) if timed else None
        target_end = torch.cuda.Event(enable_timing=True) if timed else None
        full_first = torch.cuda.Event(enable_timing=True) if timed and policy in ("b0", "c1") else None
        full_release = torch.cuda.Event(enable_timing=True) if timed and policy in ("b0", "c1") else None
        if target_start is not None:
            target_start.record()
        target_host_start = time.perf_counter_ns()
        dH_cpu = grad_cpu = None
        compact_rows = compact_bytes = inverse_bytes = 0

        # dH generation and complete old-W backbone/lookup consumption precede updates.
        if policy == "b0":
            self.phase = "B0_CLASSIFIER_DH_DW"
            de, dc = base.cce_backward(hidden, self.weight, self.labels, lse, True, True)
            if de is None or dc is None:
                raise RuntimeError("B0 CCE output missing")
            if diagnostic:
                dH_cpu = de.detach().cpu().clone()
            if full_first is not None:
                full_first.record()
            self.phase = "B0_BACKBONE_LOOKUP_BACKWARD"
            hidden_3d.backward(de.view_as(hidden_3d))
            if self.weight.grad is None:
                raise RuntimeError("B0 dense lookup gradient missing")
            self.weight.grad.add_(dc)
            del dc, de
            if diagnostic:
                grad_cpu = self.weight.grad.detach().cpu().clone()
            self.phase = "B0_ADAMW_UPDATE"
            self._update_full(self.weight.grad, next_step)
            self.weight.grad = None
            if full_release is not None:
                full_release.record()
            dense_lookup, full_gradient, peak_full = True, True, 2
        else:
            self.phase = "CLASSIFIER_DH"
            de, _ = base.cce_backward(hidden, self.weight, self.labels, lse, True, False)
            if de is None:
                raise RuntimeError("classifier dH missing")
            if diagnostic:
                dH_cpu = de.detach().cpu().clone()
            self.phase = "BACKBONE_COMPACT_LOOKUP_BACKWARD"
            hidden_3d.backward(de.view_as(hidden_3d))
            del de
            if self.weight.grad is not None:
                raise RuntimeError(f"{policy} materialized dense lookup W.grad")
            if self.collector.ids is None or self.collector.grad is None:
                raise RuntimeError("compact lookup gradient missing")
            compact_rows = self.collector.ids.numel()
            compact_bytes = nbytes(self.collector.ids) + nbytes(self.collector.grad)
            inverse_bytes = self.collector.inverse_bytes
            if policy == "c1":
                self.phase = "C1_FULL_CLASSIFIER_GRADIENT"
                _, dc = base.cce_backward(hidden, self.weight, self.labels, lse, False, True)
                if dc is None:
                    raise RuntimeError("C1 full classifier gradient missing")
                if full_first is not None:
                    full_first.record()
                dc.index_add_(0, self.collector.ids, self.collector.grad)
                if diagnostic:
                    grad_cpu = dc.detach().cpu().clone()
                self.phase = "C1_ADAMW_UPDATE"
                self._update_full(dc, next_step)
                del dc
                if full_release is not None:
                    full_release.record()
                dense_lookup, full_gradient, peak_full = False, True, 1
            else:
                grad_cpu = torch.empty((V, H), dtype=torch.bfloat16) if diagnostic else None
                for start in range(0, V, ROWS_PER_TILE):
                    self.phase = f"S2_TILE_CLASSIFIER_UPDATE_{start // ROWS_PER_TILE}"
                    stop = min(start + ROWS_PER_TILE, V)
                    tile_labels = base.local_targets(self.labels, start, stop)
                    _, dc = base.cce_backward(hidden, self.weight[start:stop], tile_labels, lse, False, True)
                    if dc is None:
                        raise RuntimeError("S2 tile gradient missing")
                    selected = (self.collector.ids >= start) & (self.collector.ids < stop)
                    if bool(selected.any()):
                        local = self.collector.ids[selected] - start
                        dc.index_add_(0, local, self.collector.grad[selected])
                    if grad_cpu is not None:
                        grad_cpu[start:stop].copy_(dc)
                    base.adamw_update_tile(self.weight[start:stop], self.m[start:stop], self.v[start:stop], dc, next_step, OPTIMIZER)
                    del dc
                dense_lookup, full_gradient, peak_full = False, False, 0

        if target_end is not None:
            target_end.record()
            target_end.synchronize()
            target_gpu_ms = target_start.elapsed_time(target_end)
        else:
            torch.cuda.synchronize()
            target_gpu_ms = None
        target_host_ms = (time.perf_counter_ns() - target_host_start) / 1e6
        target_peak_alloc = torch.cuda.max_memory_allocated()
        target_peak_reserved = torch.cuda.max_memory_reserved()
        full_lifetime = None
        if full_first is not None and full_release is not None:
            full_lifetime = full_first.elapsed_time(full_release)
        complete_ms = (time.perf_counter_ns() - complete_host_start) / 1e6
        whole_peak_alloc = max(forward_peak_alloc, target_peak_alloc)
        whole_peak_reserved = max(forward_peak_reserved, target_peak_reserved)
        self.step = next_step
        self.phase = "STEP_COMPLETE"
        result = {
            "policy": policy, "batch": self.batch, "loss": float(loss), "step": self.step,
            "target_gpu_ms": target_gpu_ms, "target_host_ms": target_host_ms,
            "complete_train_step_ms": complete_ms,
            "pre_step_allocated_bytes": pre_alloc, "pre_step_reserved_bytes": pre_reserved,
            "pre_target_allocated_bytes": pre_target_alloc, "pre_target_reserved_bytes": pre_target_reserved,
            "forward_peak_allocated_bytes": forward_peak_alloc, "forward_peak_reserved_bytes": forward_peak_reserved,
            "target_peak_allocated_bytes": target_peak_alloc, "target_peak_reserved_bytes": target_peak_reserved,
            "whole_step_peak_allocated_bytes": whole_peak_alloc, "whole_step_peak_reserved_bytes": whole_peak_reserved,
            "post_step_allocated_bytes": None, "post_step_reserved_bytes": None,
            "dense_lookup_gradient_materialized": dense_lookup,
            "full_classifier_or_total_gradient_materialized": full_gradient,
            "peak_full_gradient_buffers": peak_full,
            "full_bf16_gradient_bytes": V * H * 2 if full_gradient else 0,
            "full_gradient_lifetime_gpu_ms": full_lifetime,
            "compact_rows": compact_rows, "compact_bytes": compact_bytes,
            "inverse_index_bytes": inverse_bytes,
            "s2_rows_per_tile": ROWS_PER_TILE if policy == "s2" else 0,
            "s2_tile_count": TILE_COUNT if policy == "s2" else 0,
            "s2_fp32_tile_budget_bytes": TILE_BUDGET if policy == "s2" else 0,
            "diagnostic": diagnostic,
        }
        if diagnostic:
            result["diagnostic_tensors"] = {"dH": dH_cpu, "gradient": grad_cpu}
        del hidden_3d, hidden, loss, lse
        self.collector.reset()
        torch.cuda.synchronize()
        result["post_step_allocated_bytes"] = torch.cuda.memory_allocated()
        result["post_step_reserved_bytes"] = torch.cuda.memory_reserved()
        return result

    @torch.no_grad()
    def finite_state(self, rows: int = 4096):
        for name, tensor in (("weight", self.weight), ("m", self.m), ("v", self.v)):
            for start in range(0, V, rows):
                if not bool(torch.isfinite(tensor[start : start + rows]).all()):
                    return False, name, start
        return True, None, None

    def close(self):
        self.weight.grad = None
        self.collector.reset()
        torch.cuda.synchronize()
