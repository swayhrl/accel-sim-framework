#!/usr/bin/env python3
"""R19 bounded real fast-weight semantic canary and local CUDA timing."""

import argparse
import hashlib
import json
import math
import os
import statistics
import sys
from pathlib import Path

import torch
from einops import rearrange, repeat
from opt_einsum import contract
from safetensors import safe_open
from transformers import AutoModelForCausalLM, AutoTokenizer


ARTIFACT_REVISION = "c4ec10a9e061c64c7db5fd6277b3fa545292a49f"
CONTEXT_TOKENS = 256
GROUPS = 3
WARMUPS = 2
FORMAL = 5


def tensor_sha256(tensor: torch.Tensor) -> str:
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def tensor_metrics(a: torch.Tensor, b: torch.Tensor) -> dict:
    af = a.detach().float()
    bf = b.detach().float()
    diff = (af - bf).abs()
    denom = bf.abs().clamp_min(1e-12)
    flat_a = af.reshape(-1)
    flat_b = bf.reshape(-1)
    cosine = torch.nn.functional.cosine_similarity(flat_a, flat_b, dim=0).item()
    return {
        "max_abs": diff.max().item(),
        "mean_abs": diff.mean().item(),
        "max_rel": (diff / denom).max().item(),
        "cosine": cosine,
        "allclose_rtol_1e-2_atol_1e-2": torch.allclose(af, bf, rtol=1e-2, atol=1e-2),
    }


def parameter_hashes(model, layers: list[int]) -> dict:
    out = {}
    for i in layers:
        mlp = model.model.layers[i].mlp
        for name in ("down_proj.weight", "ttt_proj.weight", "ttt_conv.weight"):
            obj = mlp
            for part in name.split("."):
                obj = getattr(obj, part)
            out[f"model.layers.{i}.mlp.{name}"] = tensor_sha256(obj)
    return out


def pad_chunks(module, x: torch.Tensor) -> torch.Tensor:
    return module.padding(x)


@torch.no_grad()
def prepared_update(module, x: torch.Tensor, target: torch.Tensor):
    z = module.act_fn(module.gate_proj(x)) * module.up_proj(x)
    t_chunks = pad_chunks(module, target)
    z_chunks = pad_chunks(module, z)
    bs, chunk_num, chunk_size, _ = t_chunks.shape
    t_conv = (
        module.ttt_conv(t_chunks.transpose(-1, -2).reshape(bs * chunk_num, -1, chunk_size))
        .transpose(-1, -2)
        .reshape(bs, chunk_num, chunk_size, -1)
    )
    if module.ttt_proj is not None:
        delta_excl = contract(
            "b t c h, b t c d, d e -> b t e h",
            z_chunks[:, :-1],
            t_conv[:, :-1],
            module.ttt_proj.weight,
        )
    else:
        delta_excl = contract(
            "b t c h, b t c d -> b t d h",
            z_chunks[:, :-1],
            t_conv[:, :-1],
        )
    updated = module.down_proj.weight.unsqueeze(0) + module.ttt_lr * delta_excl[:, 0]
    return z_chunks, t_conv, delta_excl, updated


@torch.no_grad()
def run_primary(captures, modules):
    outputs = []
    for i, module in modules.items():
        x, target = captures[i]
        outputs.append(module(x, t=target)[0])
    return outputs


@torch.no_grad()
def run_update_only(captures, modules):
    outputs = []
    for i, module in modules.items():
        _, _, delta, updated = prepared_update(module, *captures[i])
        outputs.extend((delta, updated))
    return outputs


@torch.no_grad()
def run_consumer(prepared, modules, updated: bool):
    outputs = []
    for i, module in modules.items():
        z_chunks, _, _, updated_w = prepared[i]
        weight = updated_w if updated else module.down_proj.weight.unsqueeze(0)
        outputs.append(contract("b d h, b c h -> b c d", weight, z_chunks[:, 1]))
    return outputs


@torch.no_grad()
def run_two_chunk_closed_form(captures, modules):
    """Same two-chunk math without materializing cat+cumsum weight history."""
    outputs = []
    for i, module in modules.items():
        z_chunks, _, _, updated_w = prepared_update(module, *captures[i])
        out0 = contract(
            "b d h, b c h -> b c d",
            module.down_proj.weight.unsqueeze(0),
            z_chunks[:, 0],
        )
        out1 = contract("b d h, b c h -> b c d", updated_w, z_chunks[:, 1])
        outputs.append(torch.cat((out0, out1), dim=1))
    return outputs


def time_call(fn) -> float:
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    torch.cuda.synchronize()
    start.record()
    value = fn()
    end.record()
    end.synchronize()
    # Keep outputs alive through the completion event.
    if not value:
        raise RuntimeError("timed function returned no outputs")
    return float(start.elapsed_time(end))


def summarize(samples: list[float]) -> dict:
    med = statistics.median(samples)
    return {
        "samples_ms": samples,
        "median_ms": med,
        "mad_ms": statistics.median(abs(x - med) for x in samples),
    }


def formal_timing(captures, modules, prepared, hashes_before) -> dict:
    arms = {
        "primary_released_all_adapted_layers": lambda: run_primary(captures, modules),
        "two_chunk_closed_form_all_adapted_layers": lambda: run_two_chunk_closed_form(captures, modules),
        "update_only_all_adapted_layers": lambda: run_update_only(captures, modules),
        "first_dependent_consumer_all_adapted_layers": lambda: run_consumer(prepared, modules, True),
        "no_write_consumer_diagnostic_all_adapted_layers": lambda: run_consumer(prepared, modules, False),
    }
    orders = [list(arms), list(reversed(arms)), list(arms)]
    groups = []
    for group_idx, order in enumerate(orders):
        row = {"group": group_idx, "order": order, "arms": {}}
        for name in order:
            for _ in range(WARMUPS):
                time_call(arms[name])
            samples = [time_call(arms[name]) for _ in range(FORMAL)]
            row["arms"][name] = summarize(samples)
        if parameter_hashes_holder[0] != hashes_before:
            raise RuntimeError("pre-update parameter hashes changed")
        groups.append(row)
    aggregate = {}
    for name in arms:
        all_samples = [x for g in groups for x in g["arms"][name]["samples_ms"]]
        aggregate[name] = summarize(all_samples)
    return {"groups": groups, "aggregate": aggregate}


# Set in main after loading; avoids hashing the entire model in timing helpers.
parameter_hashes_holder = [None]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available")
    device = torch.device("cuda:0")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.backends.cuda.matmul.allow_tf32 = False

    input_receipt = json.loads(args.input.read_text())
    tokenizer = AutoTokenizer.from_pretrained(args.checkpoint, local_files_only=True, trust_remote_code=True)
    tokens = tokenizer(input_receipt["prompt"], return_tensors="pt", add_special_tokens=True)
    if tokens.input_ids.shape[1] < CONTEXT_TOKENS:
        raise RuntimeError(f"real prompt has only {tokens.input_ids.shape[1]} tokens")
    input_ids = tokens.input_ids[:, :CONTEXT_TOKENS].contiguous()
    attention_mask = tokens.attention_mask[:, :CONTEXT_TOKENS].contiguous()
    prefix_text = tokenizer.decode(input_ids[0], skip_special_tokens=False)
    prefix_sha = hashlib.sha256(input_ids.numpy().tobytes()).hexdigest()

    model = AutoModelForCausalLM.from_pretrained(
        args.checkpoint,
        local_files_only=True,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        attn_implementation="sdpa",
    ).eval().to(device)
    model.config.use_cache = False
    layers = [int(x) for x in model.config.ttt_layers]
    modules = {i: model.model.layers[i].mlp for i in layers}

    with safe_open(args.checkpoint / "model.safetensors", framework="pt", device="cpu") as sf:
        keys = set(sf.keys())
        weight_key_check = {
            str(i): {
                "down_proj": f"model.layers.{i}.mlp.down_proj.weight" in keys,
                "ttt_proj": f"model.layers.{i}.mlp.ttt_proj.weight" in keys,
                "ttt_conv": f"model.layers.{i}.mlp.ttt_conv.weight" in keys,
            }
            for i in layers
        }

    input_ids_gpu = input_ids.to(device)
    attention_gpu = attention_mask.to(device)
    hashes_before = parameter_hashes(model, layers)
    parameter_hashes_holder[0] = hashes_before
    captures = {}
    handles = []

    def make_hook(idx):
        def hook(_module, args_in, kwargs_in):
            target = kwargs_in.get("t")
            if target is None:
                raise RuntimeError(f"TTT target missing at layer {idx}")
            captures[idx] = (args_in[0].detach().clone(), target.detach().clone())
        return hook

    for i, module in modules.items():
        handles.append(module.register_forward_pre_hook(make_hook(i), with_kwargs=True))

    torch.cuda.reset_peak_memory_stats(device)
    with torch.no_grad():
        first = model(
            input_ids=input_ids_gpu,
            attention_mask=attention_gpu,
            use_cache=False,
            logits_to_keep=1,
        ).logits.detach().clone()
    torch.cuda.synchronize()
    semantic_peak_allocated = torch.cuda.max_memory_allocated(device)
    semantic_peak_reserved = torch.cuda.max_memory_reserved(device)
    for h in handles:
        h.remove()

    if sorted(captures) != layers:
        raise RuntimeError(f"captured layers {sorted(captures)} != configured {layers}")
    hashes_after = parameter_hashes(model, layers)

    # Repeat from identical pre-state to prove reset/determinism.
    with torch.no_grad():
        second = model(
            input_ids=input_ids_gpu,
            attention_mask=attention_gpu,
            use_cache=False,
            logits_to_keep=1,
        ).logits.detach().clone()
    torch.cuda.synchronize()

    prepared = {i: prepared_update(module, *captures[i]) for i, module in modules.items()}
    semantic_layers = {}
    for i, module in modules.items():
        released = module(*captures[i])[0]
        z_chunks, t_conv, delta, updated_w = prepared[i]
        manual_consumer = contract("b d h, b c h -> b c d", updated_w, z_chunks[:, 1])
        base_consumer = contract(
            "b d h, b c h -> b c d",
            module.down_proj.weight.unsqueeze(0),
            z_chunks[:, 1],
        )
        released_dependent = released[:, module.ttt_chunk : 2 * module.ttt_chunk]
        closed_form = run_two_chunk_closed_form({i: captures[i]}, {i: module})[0]
        semantic_layers[str(i)] = {
            "x_shape": list(captures[i][0].shape),
            "target_shape": list(captures[i][1].shape),
            "z_chunks_shape": list(z_chunks.shape),
            "t_conv_shape": list(t_conv.shape),
            "delta_shape": list(delta.shape),
            "fast_state_bytes": updated_w.numel() * updated_w.element_size(),
            "delta_l2": delta.float().norm().item(),
            "delta_nonzero": int(torch.count_nonzero(delta).item()),
            "delta_sha256": tensor_sha256(delta),
            "consumer_vs_released": tensor_metrics(manual_consumer, released_dependent),
            "closed_form_vs_released": tensor_metrics(closed_form, released),
            "updated_vs_base_consumer": tensor_metrics(manual_consumer, base_consumer),
            "updated_differs_from_base": not torch.equal(manual_consumer, base_consumer),
        }

    torch.cuda.reset_peak_memory_stats(device)
    timing = formal_timing(captures, modules, prepared, hashes_before)
    torch.cuda.synchronize()
    timing_peak_allocated = torch.cuda.max_memory_allocated(device)
    timing_peak_reserved = torch.cuda.max_memory_reserved(device)

    # One bounded PyTorch-profiler pass to count actual CUDA kernel launches.
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU, torch.profiler.ProfilerActivity.CUDA]) as prof:
        run_primary(captures, modules)
        torch.cuda.synchronize()
    cuda_events = [e for e in prof.events() if e.device_type == torch.autograd.DeviceType.CUDA]
    launch_names = {}
    for e in cuda_events:
        launch_names[e.name] = launch_names.get(e.name, 0) + 1

    hashes_final = parameter_hashes(model, layers)
    if not (hashes_before == hashes_after == hashes_final):
        raise RuntimeError("adapted model parameters mutated")
    semantic_ok = all(
        x["delta_l2"] > 0
        and x["delta_nonzero"] > 0
        and x["updated_differs_from_base"]
        # The released path contracts both chunks in one batched GEMM while
        # the canary contracts only the dependent chunk. BF16 reduction order
        # therefore differs; require a tight cosine and mean-absolute bound.
        and x["consumer_vs_released"]["cosine"] >= 0.99999
        and x["consumer_vs_released"]["mean_abs"] <= 5e-3
        and x["closed_form_vs_released"]["cosine"] >= 0.99999
        and x["closed_form_vs_released"]["mean_abs"] <= 5e-3
        for x in semantic_layers.values()
    )
    repeat_bitwise = torch.equal(first, second)
    if not semantic_ok or not repeat_bitwise:
        (args.output_dir / "DEBUG_SEMANTIC.json").write_text(
            json.dumps(
                {
                    "semantic_ok": semantic_ok,
                    "repeat_bitwise": repeat_bitwise,
                    "semantic_layers": semantic_layers,
                },
                indent=2,
            )
            + "\n"
        )
        raise RuntimeError(f"semantic qualification failed semantic_ok={semantic_ok} repeat={repeat_bitwise}")

    result = {
        "stage": "AWMA_R19_FASTWEIGHT_109_V1",
        "artifact_class": "PUBLIC_REPRODUCTION_ARTIFACT",
        "artifact_revision": ARTIFACT_REVISION,
        "device": torch.cuda.get_device_name(device),
        "torch_version": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "context_tokens": CONTEXT_TOKENS,
        "full_prompt_tokens": int(tokens.input_ids.shape[1]),
        "prefix_token_ids_sha256": prefix_sha,
        "prefix_text_sha256": hashlib.sha256(prefix_text.encode("utf-8")).hexdigest(),
        "ttt_chunk": int(model.config.ttt_chunk),
        "adapted_layers": layers,
        "weight_key_check": weight_key_check,
        "parameter_hashes_before": hashes_before,
        "parameter_hashes_after": hashes_after,
        "repeat_logits_bitwise": repeat_bitwise,
        "semantic_layers": semantic_layers,
        "total_fast_state_bytes": sum(x["fast_state_bytes"] for x in semantic_layers.values()),
        "semantic_peak_allocated_bytes": semantic_peak_allocated,
        "semantic_peak_reserved_bytes": semantic_peak_reserved,
        "timing_peak_allocated_bytes": timing_peak_allocated,
        "timing_peak_reserved_bytes": timing_peak_reserved,
        "timing": timing,
        "primary_cuda_kernel_launches": len(cuda_events),
        "primary_cuda_kernel_names": launch_names,
        "nsys_captures": 0,
        "ncu_targets": 0,
    }
    (args.output_dir / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    (args.output_dir / "INPUT_PREFIX.txt").write_text(prefix_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
