#!/usr/bin/env python3
"""Single-point/arm Stage A dense-first Tier0 runner.

The process loads one frozen model, performs one excluded warmup, then either
three instrumentation-OFF native requests or one Graph-OFF observed request.
"""

import argparse
import hashlib
import importlib.util
import json
import os
import time
import traceback
from pathlib import Path


os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("VLLM_LOGGING_LEVEL", "INFO")

import torch
from vllm import LLM, SamplingParams


OBSERVER_SHA = {
    "V1": "1f68c1117623cbc46f98f51f17ba798d8bf5ffb103f427b9d7b916ced0a35020",
    "V2": "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22",
}


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load_observer(path, identity):
    actual = file_sha(path)
    if actual != OBSERVER_SHA[identity]:
        raise RuntimeError(f"{identity} observer source SHA mismatch: {actual}")
    spec = importlib.util.spec_from_file_location(f"c16_observer_{identity.lower()}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, actual


def batch_output_receipt(outputs, source_rows, observer_module):
    rows = []
    for index, (output, source) in enumerate(zip(outputs, source_rows)):
        rows.append({
            "batch_row": index,
            "source_id": source["source_id"],
            "input_file": source["path"],
            "input_file_sha256": source["file_sha256"],
            "input_token_ids_sha256": source["token_ids_sha256"],
            "request_id": str(output.request_id),
            "completion": observer_module.completion_receipt(output),
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--point", choices=("MP01", "MP02", "MP03", "MP05"), required=True)
    parser.add_argument("--graph-mode", choices=("on", "off"), required=True)
    parser.add_argument("--arm", choices=("native", "observed"), required=True)
    parser.add_argument("--observer", choices=("V1", "V2"), required=True)
    parser.add_argument("--observer-source", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--model-kind", choices=("QWEN_BF16", "QWEN_AWQ"), required=True)
    parser.add_argument("--input-json", type=Path, action="append", required=True)
    parser.add_argument("--decode-tokens", type=int, required=True)
    parser.add_argument("--timing-endpoint", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "point": args.point,
        "graph_mode": args.graph_mode,
        "arm": args.arm,
        "observer_identity": args.observer,
        "status": "RUNNING",
        "timing_endpoint": args.timing_endpoint,
    }
    try:
        if args.arm == "observed" and args.graph_mode != "off":
            raise RuntimeError("observed arm is Graph OFF only")
        if args.arm == "native" and args.observer not in ("V1", "V2"):
            raise RuntimeError("observer identity still must be frozen for native provenance")
        observer, observer_sha = load_observer(args.observer_source, args.observer)
        sources = []
        prompts = []
        for path in args.input_json:
            tokens = json.loads(path.read_text())
            if len(tokens) != 512 or not all(isinstance(value, int) for value in tokens):
                raise RuntimeError(f"invalid frozen input: {path}")
            sources.append({
                "source_id": path.stem,
                "path": str(path),
                "file_sha256": file_sha(path),
                "token_ids_sha256": sha_json(tokens),
                "token_count": len(tokens),
            })
            prompts.append({"prompt_token_ids": tokens})
        batch = len(prompts)
        expected_batch = 4 if args.point == "MP03" else 1
        if batch != expected_batch:
            raise RuntimeError(f"{args.point} requires batch {expected_batch}, got {batch}")
        expected_kind = "QWEN_AWQ" if args.point == "MP05" else "QWEN_BF16"
        if args.model_kind != expected_kind:
            raise RuntimeError(f"{args.point} model kind mismatch")
        expected_decode = 1 if args.point == "MP01" else 32
        if args.decode_tokens != expected_decode:
            raise RuntimeError(f"{args.point} decode token count mismatch")

        dtype = "float16" if args.model_kind == "QWEN_AWQ" else "bfloat16"
        quantization = "awq" if args.model_kind == "QWEN_AWQ" else None
        max_model_len = 512 + args.decode_tokens
        llm = LLM(
            model=str(args.model), tokenizer=str(args.model), skip_tokenizer_init=True,
            dtype=dtype, quantization=quantization, model_impl="vllm",
            enforce_eager=args.graph_mode == "off", tensor_parallel_size=1,
            max_model_len=max_model_len, max_num_seqs=batch,
            max_num_batched_tokens=batch * max_model_len,
            gpu_memory_utilization=0.92, cpu_offload_gb=0,
            enable_prefix_caching=False, seed=0, disable_log_stats=True,
        )
        torch.cuda.synchronize()
        engine = llm.llm_engine
        model_runner = engine.model_executor.driver_worker.model_runner
        model = model_runner.model
        module_census = observer.module_receipt(model)
        attention_backend = observer.attention_receipt(model_runner, model)
        selected_methods = {row.get("quant_method_class") for row in module_census if row.get("quant_method_class")}
        selected_kernels = {row.get("kernel_backend_class") for row in module_census if row.get("kernel_backend_class")}
        selected_attention = {row.get("impl_class") for row in attention_backend["modules"] if row.get("impl_class")}
        if "FlashAttentionImpl" not in selected_attention:
            raise RuntimeError(f"unexpected attention backend: {sorted(selected_attention)}")
        if args.model_kind == "QWEN_AWQ":
            if "AutoAWQMarlinLinearMethod" not in selected_methods or "MarlinLinearKernel" not in selected_kernels:
                raise RuntimeError(f"unexpected AWQ backend: methods={sorted(selected_methods)} kernels={sorted(selected_kernels)}")
        elif "UnquantizedLinearMethod" not in selected_methods:
            raise RuntimeError(f"unexpected BF16 projection method: {sorted(selected_methods)}")
        semantic_modules = observer.select_semantic_modules(model, args.model_kind)
        if not semantic_modules:
            raise RuntimeError("semantic module census empty")
        sampling = SamplingParams(
            temperature=0.0, top_p=1.0, max_tokens=args.decode_tokens,
            ignore_eos=True, detokenize=False, logprobs=20,
        )

        def invoke(instrument, collect):
            hooks = observer.HookSession(semantic_modules, collect).install() if instrument else None
            if instrument:
                torch.cuda.nvtx.range_push(f"C16_TIER0_{args.point}_GRAPH_OFF_OBSERVED")
            torch.cuda.synchronize()
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            start.record()
            host_start = time.perf_counter_ns()
            outputs = llm.generate(prompts, sampling, use_tqdm=False)
            stop.record()
            torch.cuda.synchronize()
            host_end = time.perf_counter_ns()
            if instrument:
                torch.cuda.nvtx.range_pop()
            instrumentation = None
            if hooks:
                hooks.remove()
                instrumentation = hooks.receipt()
            return {
                "host_wall_ms": (host_end - host_start) / 1e6,
                "cuda_event_ms": float(start.elapsed_time(stop)),
                "rows": batch_output_receipt(outputs, sources, observer),
                "instrumentation": instrumentation,
            }

        warmup = invoke(False, False)
        if args.arm == "native":
            samples = [invoke(False, False) for _ in range(3)]
        else:
            samples = [invoke(True, True)]
        result.update({
            "status": "PASS",
            "process_id": os.getpid(),
            "model_kind": args.model_kind,
            "model_path": str(args.model),
            "model_revision": args.model.name,
            "observer_source": str(args.observer_source),
            "observer_source_sha256": observer_sha,
            "batch_size": batch,
            "real_single_batch_call": True,
            "decode_tokens": args.decode_tokens,
            "input_sources": sources,
            "warmup_excluded": warmup,
            "samples": samples,
            "semantic_module_names": [name for name, _ in semantic_modules],
            "module_census": module_census,
            "attention_backend": attention_backend,
            "vllm_config": {
                "enforce_eager": args.graph_mode == "off",
                "max_model_len": max_model_len,
                "max_num_seqs": batch,
                "max_num_batched_tokens": batch * max_model_len,
                "gpu_memory_utilization": 0.92,
                "cpu_offload_gb": 0,
                "dtype": dtype,
                "quantization": quantization,
                "model_impl": "vllm",
            },
            "cuda_device": {
                "name": torch.cuda.get_device_name(0),
                "uuid": str(getattr(torch.cuda.get_device_properties(0), "uuid", None)),
                "capability": list(torch.cuda.get_device_capability(0)),
            },
        })
    except BaseException as exc:
        result.update({
            "status": "RUNTIME_ERROR",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "traceback": traceback.format_exc(),
            "oom": isinstance(exc, torch.cuda.OutOfMemoryError) or "out of memory" in str(exc).lower(),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: result.get(key) for key in ("point", "graph_mode", "arm", "status", "error_type", "oom")}, sort_keys=True))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
