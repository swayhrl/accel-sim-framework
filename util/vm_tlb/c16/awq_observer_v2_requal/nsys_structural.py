#!/usr/bin/env python3
"""One-request NSYS structural wrapper using the exact qualified V2 HookSession."""

import argparse
import hashlib
import importlib.util
import json
import os
import time
from pathlib import Path


EXPECTED_RUNNER_SHA = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sha(args.runner) != EXPECTED_RUNNER_SHA:
        raise SystemExit("qualified V2 runner SHA mismatch")

    os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("VLLM_LOGGING_LEVEL", "INFO")
    spec = importlib.util.spec_from_file_location("c16_exact_observer_v2_runner", args.runner)
    exact = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exact)

    tokens = json.loads(args.input_json.read_text())
    if len(tokens) != 512:
        raise RuntimeError("input token count is not 512")
    target = exact.TARGETS["QWEN_AWQ"]
    llm = exact.LLM(model=str(args.model), tokenizer=str(args.model), skip_tokenizer_init=True,
                    dtype=target["dtype"], quantization=target["quantization"], model_impl="vllm",
                    enforce_eager=True, tensor_parallel_size=1, max_model_len=target["max_model_len"],
                    max_num_seqs=1, max_num_batched_tokens=1024, gpu_memory_utilization=0.92,
                    cpu_offload_gb=0, enable_prefix_caching=False,
                    enable_return_routed_experts=False, seed=0, disable_log_stats=True)
    exact.torch.cuda.synchronize()
    engine = llm.llm_engine
    model_runner = engine.model_executor.driver_worker.model_runner
    model = model_runner.model
    modules = exact.select_semantic_modules(model, "QWEN_AWQ")
    sampling = exact.SamplingParams(temperature=0.0, top_p=1.0, max_tokens=target["decode"],
                                    ignore_eos=True, detokenize=False, logprobs=20)

    llm.generate({"prompt_token_ids": tokens}, sampling, use_tqdm=False)
    exact.torch.cuda.synchronize()

    hooks = exact.HookSession(modules, collect=True).install()
    exact.torch.cuda.nvtx.range_push("C16_STAGEA_QWEN_AWQ_off_INSTRUMENT_ON")
    exact.torch.cuda.synchronize()
    start = exact.torch.cuda.Event(enable_timing=True)
    stop = exact.torch.cuda.Event(enable_timing=True)
    start.record()
    host_start = time.perf_counter_ns()
    output = llm.generate({"prompt_token_ids": tokens}, sampling, use_tqdm=False)[0]
    stop.record()
    exact.torch.cuda.synchronize()
    host_end = time.perf_counter_ns()
    exact.torch.cuda.nvtx.range_pop()
    hooks.remove()

    result = {
        "status": "PASS",
        "purpose": "NSYS_STRUCTURAL_ONLY_EXCLUDED_FROM_NATIVE_TIMING",
        "target": "QWEN_AWQ",
        "graph_mode": "off",
        "model_revision": args.model.name,
        "qualified_v2_runner_sha256": EXPECTED_RUNNER_SHA,
        "observer_source": "HookSession imported from exact qualified V2 runner",
        "per_occurrence_cuda_events": 0,
        "request_level_cuda_events": 2,
        "host_wall_ms_non_authoritative": (host_end - host_start) / 1e6,
        "cuda_event_ms_non_authoritative": float(start.elapsed_time(stop)),
        "output": exact.completion_receipt(output),
        "instrumentation": hooks.receipt(),
        "module_census": exact.module_receipt(model),
        "attention_backend": exact.attention_receipt(model_runner, model),
        "semantic_module_names": [name for name, _ in modules],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "semantic_occurrences": len(result["instrumentation"]["semantic_order"])}, sort_keys=True))


if __name__ == "__main__":
    main()
