#!/usr/bin/env python3
"""Single-target, single-graph-mode Stage A runtime qualification canary."""

import argparse
import hashlib
import json
import os
import subprocess
import time
import traceback
from collections import Counter
from pathlib import Path

os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("VLLM_LOGGING_LEVEL", "INFO")

import torch
from torch.profiler import ProfilerActivity, profile
from vllm import LLM, SamplingParams


TARGETS = {
    "QWEN_BF16": {"dtype": "bfloat16", "quantization": None, "decode": 4, "max_model_len": 516},
    "QWEN_AWQ": {"dtype": "float16", "quantization": "awq", "decode": 4, "max_model_len": 516},
    "OLMOE": {"dtype": "bfloat16", "quantization": None, "decode": 32, "max_model_len": 544},
}


def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def gpu_memory_used_mib():
    text = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], text=True)
    return int(text.strip().splitlines()[0])


def completion_receipt(request_output):
    completion = request_output.outputs[0]
    tokens = [int(x) for x in completion.token_ids]
    logprobs = []
    for index, row in enumerate(completion.logprobs or []):
        entries = []
        for token_id, value in sorted(row.items(), key=lambda pair: int(pair[0])):
            entries.append({"token_id": int(token_id), "logprob": float(value.logprob),
                            "rank": int(value.rank) if value.rank is not None else None})
        logprobs.append(entries)
    routed = getattr(completion, "routed_experts", None)
    if routed is not None:
        routed = routed.tolist() if hasattr(routed, "tolist") else routed
    return {"tokens": tokens, "token_count": len(tokens), "logprobs": logprobs,
            "logprobs_sha256": sha_json(logprobs), "routed_experts": routed,
            "routing_sha256": sha_json(routed) if routed is not None else None,
            "finish_reason": completion.finish_reason}


def module_receipt(model):
    rows = []
    for name, module in model.named_modules():
        cls = type(module).__name__
        interesting = any(term in cls for term in ("Attention", "MergedColumnParallelLinear", "FusedMoE", "SparseMoe"))
        if not interesting and not any(name.endswith(suffix) for suffix in ("gate_up_proj", ".experts", ".gate")):
            continue
        quant = getattr(module, "quant_method", None)
        kernel = getattr(quant, "kernel", None) if quant is not None else None
        rows.append({"name": name, "module_class": cls,
                     "quant_method_class": type(quant).__name__ if quant is not None else None,
                     "kernel_backend_class": type(kernel).__name__ if kernel is not None else None,
                     "parameter_shapes": {n: {"shape": list(p.shape), "dtype": str(p.dtype),
                                               "bytes": p.numel() * p.element_size()}
                                          for n, p in module.named_parameters(recurse=False)}})
    return rows


def attention_receipt(model_runner, model):
    values = []
    for name, module in model.named_modules():
        cls = type(module).__name__
        if "Attention" in cls:
            impl = getattr(module, "impl", None)
            values.append({"name": name, "module_class": cls,
                           "impl_class": type(impl).__name__ if impl is not None else None})
    groups = []
    for outer in getattr(model_runner, "attn_groups", []) or []:
        for group in outer if isinstance(outer, (list, tuple)) else [outer]:
            backend = getattr(group, "backend", None)
            groups.append({"group_class": type(group).__name__,
                           "backend_class": type(backend).__name__ if backend is not None else None})
    return {"modules": values, "runner_groups": groups}


def select_semantic_modules(model, target):
    selected = []
    for name, module in model.named_modules():
        if name.endswith(".self_attn"):
            selected.append((name, module))
        elif target.startswith("QWEN") and name.endswith((".mlp.gate_up_proj", ".mlp.act_fn", ".mlp.down_proj")):
            selected.append((name, module))
        elif target == "OLMOE" and name.endswith((".mlp.gate", ".mlp.experts")):
            selected.append((name, module))
    return selected


class HookSession:
    def __init__(self, modules, collect):
        self.modules = modules
        self.collect = collect
        self.handles = []
        self.pending = {}
        self.events = []
        self.order = []
        self.ordinal = 0

    def install(self):
        for name, module in self.modules:
            self.handles.append(module.register_forward_pre_hook(self.make_pre(name)))
            self.handles.append(module.register_forward_hook(self.make_post(name)))
        return self

    def make_pre(self, name):
        def hook(module, args):
            ordinal = self.ordinal; self.ordinal += 1
            label = f"C16_STAGEA_{ordinal}_{name}"
            torch.cuda.nvtx.range_push(label)
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            start.record()
            self.pending[id(module)] = (ordinal, name, start, stop,
                                        list(args[0].shape) if args and isinstance(args[0], torch.Tensor) else None)
        return hook

    def make_post(self, name):
        def hook(module, args, output):
            ordinal, module_name, start, stop, input_shape = self.pending.pop(id(module))
            stop.record(); torch.cuda.nvtx.range_pop()
            value = output[0] if isinstance(output, (tuple, list)) and output and isinstance(output[0], torch.Tensor) else output
            output_shape = list(value.shape) if isinstance(value, torch.Tensor) else None
            if self.collect:
                self.events.append((ordinal, module_name, start, stop, input_shape, output_shape))
                self.order.append({"ordinal": ordinal, "module": module_name,
                                   "input_shape": input_shape, "output_shape": output_shape})
        return hook

    def remove(self):
        for handle in self.handles:
            handle.remove()
        if self.pending:
            raise RuntimeError(f"unclosed semantic hooks: {len(self.pending)}")

    def receipt(self):
        return {"semantic_order": self.order,
                "semantic_order_sha256": sha_json(self.order),
                "event_timings_ms": [{"ordinal": o, "module": n, "elapsed_ms": float(s.elapsed_time(e)),
                                      "input_shape": i, "output_shape": out}
                                     for o, n, s, e, i, out in self.events]}


def profiler_inventory(call):
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=False,
                 profile_memory=False, with_stack=False) as prof:
        receipt = call()
        torch.cuda.synchronize()
    names = []
    for event in prof.events():
        device = str(getattr(event, "device_type", "")).lower()
        if "cuda" in device:
            names.append(event.name)
    counts = Counter(names)
    return receipt, {"kernel_count": len(names), "kernel_inventory": dict(sorted(counts.items())),
                     "kernel_sequence_sha256": sha_json(names), "kernel_inventory_sha256": sha_json(dict(sorted(counts.items())))}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--target", choices=TARGETS, required=True)
    p.add_argument("--graph-mode", choices=("off", "on"), required=True)
    p.add_argument("--model", type=Path, required=True)
    p.add_argument("--input-json", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    spec = TARGETS[args.target]
    result = {"target": args.target, "graph_mode": args.graph_mode, "status": "RUNNING",
              "model_path": str(args.model), "model_revision": args.model.name}
    try:
        token_ids = json.loads(args.input_json.read_text())
        if len(token_ids) != 512:
            raise RuntimeError(f"input token count {len(token_ids)} != 512")
        before_mib = gpu_memory_used_mib()
        torch.cuda.reset_peak_memory_stats()
        llm = LLM(model=str(args.model), tokenizer=str(args.model), skip_tokenizer_init=True,
                  dtype=spec["dtype"], quantization=spec["quantization"], model_impl="vllm",
                  enforce_eager=args.graph_mode == "off", tensor_parallel_size=1,
                  max_model_len=spec["max_model_len"], max_num_seqs=1, max_num_batched_tokens=1024,
                  gpu_memory_utilization=0.92, cpu_offload_gb=0, enable_prefix_caching=False,
                  enable_return_routed_experts=args.target == "OLMOE", seed=0, disable_log_stats=True)
        torch.cuda.synchronize()
        after_load_mib = gpu_memory_used_mib()
        engine = llm.llm_engine
        model_runner = engine.model_executor.driver_worker.model_runner
        model = model_runner.model
        modules = module_receipt(model)
        attention = attention_receipt(model_runner, model)
        semantic_modules = select_semantic_modules(model, args.target)
        if not semantic_modules:
            raise RuntimeError("semantic module census empty")
        sampling = SamplingParams(temperature=0.0, top_p=1.0, max_tokens=spec["decode"],
                                  ignore_eos=True, detokenize=False, logprobs=20)

        def generate(instrument=False, collect=False):
            hooks = HookSession(semantic_modules, collect).install() if instrument else None
            if instrument:
                torch.cuda.nvtx.range_push(f"C16_STAGEA_{args.target}_{args.graph_mode}_INSTRUMENT_ON")
            torch.cuda.synchronize()
            start = torch.cuda.Event(enable_timing=True); stop = torch.cuda.Event(enable_timing=True)
            start.record(); host_start = time.perf_counter_ns()
            output = llm.generate({"prompt_token_ids": token_ids}, sampling, use_tqdm=False)[0]
            stop.record(); torch.cuda.synchronize(); host_end = time.perf_counter_ns()
            if instrument:
                torch.cuda.nvtx.range_pop()
            hook_receipt = None
            if hooks:
                hooks.remove(); hook_receipt = hooks.receipt()
            return {"output": completion_receipt(output), "host_wall_ms": (host_end-host_start)/1e6,
                    "cuda_event_ms": float(start.elapsed_time(stop)), "instrumentation": hook_receipt}

        warmup = generate(False, False)
        native_runs = []
        if args.graph_mode == "off":
            order = [(False, False), (True, True), (True, False), (False, False), (False, False), (True, False)]
            for instrument, collect in order:
                native_runs.append({"arm": "ON" if instrument else "OFF", **generate(instrument, collect)})
            prof_off_output, prof_off = profiler_inventory(lambda: generate(False, False))
            prof_on_output, prof_on = profiler_inventory(lambda: generate(True, False))
            profiler_data = {"OFF": {**prof_off, "output": prof_off_output["output"]},
                             "ON": {**prof_on, "output": prof_on_output["output"]}}
        else:
            native_runs.append({"arm": "GRAPH_ON", **generate(False, False)})
            prof_output, prof_data = profiler_inventory(lambda: generate(False, False))
            profiler_data = {"GRAPH_ON": {**prof_data, "output": prof_output["output"]}}
        torch.cuda.synchronize()
        steady_mib = gpu_memory_used_mib()
        result.update({
            "status": "PASS", "prompt_token_count": len(token_ids), "decode_tokens": spec["decode"],
            "warmup": warmup, "native_runs": native_runs, "profiler": profiler_data,
            "module_census": modules, "attention_backend": attention,
            "semantic_module_names": [name for name, _ in semantic_modules],
            "vllm_config": {"enforce_eager": args.graph_mode == "off", "max_model_len": spec["max_model_len"],
                            "max_num_seqs": 1, "max_num_batched_tokens": 1024, "gpu_memory_utilization": 0.92,
                            "cpu_offload_gb": 0, "dtype": spec["dtype"], "quantization": spec["quantization"],
                            "model_impl": "vllm"},
            "vram": {"before_process_mib": before_mib, "after_load_mib": after_load_mib,
                     "steady_after_canary_mib": steady_mib,
                     "torch_memory_allocated_bytes": torch.cuda.memory_allocated(),
                     "torch_memory_reserved_bytes": torch.cuda.memory_reserved(),
                     "torch_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                     "torch_peak_reserved_bytes": torch.cuda.max_memory_reserved()},
        })
    except BaseException as exc:
        result.update({"status": "RUNTIME_ERROR", "error_type": type(exc).__name__,
                       "error": str(exc), "traceback": traceback.format_exc(),
                       "oom": isinstance(exc, torch.cuda.OutOfMemoryError) or "out of memory" in str(exc).lower()})
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result.get(k) for k in ("target", "graph_mode", "status", "error_type", "oom")}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
