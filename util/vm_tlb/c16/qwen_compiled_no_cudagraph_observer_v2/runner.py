#!/usr/bin/env python3
"""Future Mode-B-only observer qualification runner; never science timing."""

import argparse
import csv
import hashlib
import json
import os
import statistics
import time
import traceback
from collections import Counter
from pathlib import Path

os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

import torch
from torch.profiler import ProfilerActivity, profile
from vllm import LLM, SamplingParams
from vllm.compilation.decorators import TorchCompileWithNoGuardsWrapper
from vllm.config.compilation import CUDAGraphMode, CompilationConfig, CompilationMode
from vllm.forward_context import get_forward_context, is_forward_context_available

from observer_v2 import HookSession, select_semantic_modules, sha_json


ROOT = Path(__file__).resolve().parents[4]
ASSET_PACK = ROOT / "docs/vm_tlb/review_packs/C16_MEASUREMENT_CAMPAIGN_STAGEA_ASSET_INPUT_CLOSURE_174NEW_V1"


def expected_rows(path, point):
    with path.open(newline="", encoding="utf-8") as stream:
        return [row for row in csv.DictReader(stream, delimiter="\t") if row["point_id"] == point]


def check_semantic(actual, expected):
    if len(actual) != len(expected) or len(actual) != 4608:
        raise RuntimeError(f"semantic coverage count {len(actual)} != frozen 4608")
    for row, target in zip(actual, expected):
        if row["ordinal"] != int(target["ordinal"]) or row["module"] != target["module_name"]:
            raise RuntimeError(f"semantic order mismatch at expected ordinal {target['ordinal']}")
        for actual_key, expected_key in (("input_shape", "expected_input_shape"), ("output_shape", "expected_output_shape")):
            if row[actual_key] != json.loads(target[expected_key]):
                raise RuntimeError(f"semantic shape mismatch at {target['ordinal']} {actual_key}")


def extract_rows(outputs, source_ids):
    if len(outputs) != len(source_ids):
        raise RuntimeError("batch row count changed")
    rows = []
    for batch_row, (response, source_id) in enumerate(zip(outputs, source_ids)):
        if len(response.outputs) != 1:
            raise RuntimeError("unexpected completion count")
        completion = response.outputs[0]
        tokens = list(completion.token_ids)
        if len(tokens) != 32 or completion.logprobs is None or len(completion.logprobs) != 32:
            raise RuntimeError("D0-D31 output length changed")
        sampled = []
        for step, token in enumerate(tokens):
            if token not in completion.logprobs[step]:
                raise RuntimeError(f"sampled token lacks logprob at D{step}")
            sampled.append(float(completion.logprobs[step][token].logprob))
        rows.append({"batch_row": batch_row, "source_id": source_id,
                     "prompt_token_count": len(response.prompt_token_ids),
                     "tokens": tokens, "sampled_logprobs": sampled})
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--point", choices=("MP02", "MP03"), required=True)
    parser.add_argument("--arm", choices=("NATIVE", "STRUCTURAL"), required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--expected-sequence", type=Path, required=True)
    parser.add_argument("--qualification-receipt", type=Path)
    parser.add_argument("--remaining-point-seconds", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    point_reservation = 75 if args.point == "MP02" else 105
    if not (0 < args.remaining_point_seconds <= point_reservation):
        raise SystemExit("invalid externally verified remaining point budget")
    point_cap = args.remaining_point_seconds
    started = time.monotonic()
    result = {"point": args.point, "arm": args.arm, "status": "RUNNING",
              "point_reservation_seconds": point_reservation,
              "verified_remaining_seconds_at_entry": point_cap}
    model_class = None
    original_model_call = None
    try:
        if args.model.name != "aa8e72537993ba99e69dfaafa59ed015b17504d1":
            raise RuntimeError("Qwen BF16 model revision path changed")
        model_config = args.model / "config.json"
        if hashlib.sha256(model_config.read_bytes()).hexdigest() != "eed00b17e22553979d090fa492e587e92885e328914c8e0b0b78f0a0d3576b3b":
            raise RuntimeError("Qwen BF16 model config SHA changed")
        if args.arm == "STRUCTURAL":
            if args.qualification_receipt is None:
                raise RuntimeError("structural NSYS requires accepted native neutrality receipt")
            qualification = json.loads(args.qualification_receipt.read_text())
            if qualification.get("point") != args.point or qualification.get("status") != "NATIVE_NEUTRALITY_PASS":
                raise RuntimeError("structural NSYS is not authorized before native PASS")
        elif args.qualification_receipt is not None:
            raise RuntimeError("qualification receipt is structural-only")

        source_ids = [f"TRAIN_A_DISCOVERY_{i:02d}" for i in range(1 if args.point == "MP02" else 4)]
        with (ASSET_PACK / "TOKENIZATION_RECEIPTS.tsv").open(newline="", encoding="utf-8") as stream:
            token_receipts = {(row["model_key"], row["source_text_id"]): row
                              for row in csv.DictReader(stream, delimiter="\t")}
        prompts = []
        for source_id in source_ids:
            token_path = ASSET_PACK / "token_ids/QWEN_BF16" / f"{source_id}.json"
            tokens = json.loads(token_path.read_text())
            if len(tokens) != 512 or not all(type(value) is int for value in tokens):
                raise RuntimeError(f"frozen token identity malformed: {source_id}")
            receipt = token_receipts[("QWEN_BF16", source_id)]
            if hashlib.sha256(token_path.read_bytes()).hexdigest() != receipt["token_id_file_sha256"] or sha_json(tokens) != receipt["token_ids_sha256"]:
                raise RuntimeError(f"frozen token SHA changed: {source_id}")
            prompts.append({"prompt_token_ids": tokens})
        expected = expected_rows(args.expected_sequence, args.point)
        if len(expected) != 4608 or [int(row["ordinal"]) for row in expected] != list(range(4608)):
            raise RuntimeError("expected semantic sequence not closed")

        llm = LLM(
            model=str(args.model), tokenizer=str(args.model), skip_tokenizer_init=True,
            dtype="bfloat16", quantization=None, model_impl="vllm", enforce_eager=False,
            compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.NONE),
            tensor_parallel_size=1, max_model_len=544, max_num_seqs=len(prompts),
            max_num_batched_tokens=len(prompts) * 544, gpu_memory_utilization=0.92,
            cpu_offload_gb=0, enable_prefix_caching=False, seed=0, disable_log_stats=True,
        )
        engine = llm.llm_engine
        runner = engine.model_executor.driver_worker.model_runner
        config = runner.vllm_config
        cc = config.compilation_config
        model = runner.get_model() if hasattr(runner, "get_model") else runner.model
        if config.model_config.enforce_eager or cc.mode != CompilationMode.VLLM_COMPILE or cc.backend != "inductor" or cc.cudagraph_mode != CUDAGraphMode.NONE:
            raise RuntimeError("MODE_B effective config identity invalid")
        if os.environ.get("TORCH_COMPILE_DISABLE") == "1":
            raise RuntimeError("torch.compile disabled by environment")
        graph_manager = runner.cudagraph_manager
        if graph_manager.needs_capture() or graph_manager.graphs:
            raise RuntimeError("MODE_B has CUDA Graph capture/replay state")

        modules = select_semantic_modules(model)
        frozen_names = {row["module_name"] for row in expected}
        if len(modules) != 144 or {name for name, _ in modules} != frozen_names:
            raise RuntimeError("semantic module source census changed")
        model_modules = list(model.named_modules())
        attention = sorted({type(module.impl).__name__ for _, module in model_modules if getattr(module, "impl", None) is not None and type(module.impl).__name__.endswith("AttentionImpl")})
        linear = sorted({type(module.quant_method).__name__ for _, module in model_modules if getattr(module, "quant_method", None) is not None and type(module.quant_method).__name__.endswith("LinearMethod")})
        if "FlashAttentionImpl" not in attention or "UnquantizedLinearMethod" not in linear:
            raise RuntimeError("MODE_B attention/linear backend substitution")

        model_calls = {"count": 0, "skip_compiled_seen": False, "compiled_at_call": False}
        model_class = type(model)
        original_model_call = model_class.__call__

        def tracked_model_call(self, *pos, **kw):
            model_calls["count"] += 1
            if is_forward_context_available():
                model_calls["skip_compiled_seen"] |= bool(get_forward_context().skip_compiled)
            compiled = any(
                not bool(getattr(module, "do_not_compile", True))
                and (bool(getattr(module, "compiled", False)) or getattr(module, "aot_compiled_fn", None) is not None)
                for module in self.modules() if isinstance(module, TorchCompileWithNoGuardsWrapper)
            )
            model_calls["compiled_at_call"] |= compiled
            return original_model_call(self, *pos, **kw)

        model_class.__call__ = tracked_model_call
        sampling = SamplingParams(temperature=0.0, top_p=1.0, max_tokens=32,
                                  ignore_eos=True, detokenize=False, logprobs=20)

        def request(install_observer):
            hooks = HookSession(modules).install() if install_observer else None
            arm_label = "ON" if install_observer else "OFF"
            torch.cuda.nvtx.range_push(f"C16_MODE_B_{args.point}_{arm_label}")
            try:
                torch.cuda.synchronize()
                start = torch.cuda.Event(enable_timing=True)
                stop = torch.cuda.Event(enable_timing=True)
                start.record()
                host_start = time.perf_counter_ns()
                outputs = llm.generate(prompts, sampling, use_tqdm=False)
                stop.record()
                torch.cuda.synchronize()
                host_end = time.perf_counter_ns()
            finally:
                torch.cuda.nvtx.range_pop()
                if hooks is not None:
                    hooks.remove()
            receipt = hooks.receipt() if hooks is not None else None
            if receipt is not None:
                try:
                    check_semantic(receipt["semantic_order"], expected)
                except Exception:
                    result.setdefault("semantic_failure_receipts", []).append(receipt)
                    result["gate_status"] = "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
                    raise
            return {"request_cuda_event_ms": float(start.elapsed_time(stop)),
                    "host_wall_ms": (host_end - host_start) / 1e6,
                    "rows": extract_rows(outputs, source_ids), "semantic": receipt}

        if args.arm == "STRUCTURAL":
            warmups = {"ON": request(True)}
            if time.monotonic() - started >= point_cap:
                raise RuntimeError("point GPU-active cap reached during structural warmup")
            measured = [{"arm": "ON", **request(True)}]
            kernel_inventory = None
            result.update({"warmups": warmups, "measured": measured})
        else:
            warmups = {"OFF": request(False), "ON": request(True)}
            measured = []
            for native_arm in ("OFF", "ON", "ON", "OFF", "OFF", "ON"):
                if time.monotonic() - started >= point_cap:
                    raise RuntimeError("point GPU-active cap would be exceeded")
                measured.append({"arm": native_arm, **request(native_arm == "ON")})
            result.update({"warmups": warmups, "measured": measured})
            reference = next(row["rows"] for row in measured if row["arm"] == "OFF")
            for sample in measured:
                if len(sample["rows"]) != len(reference):
                    raise RuntimeError("OFF/ON batch shape changed")
                for left, right in zip(reference, sample["rows"]):
                    if left["batch_row"] != right["batch_row"] or left["source_id"] != right["source_id"] or left["prompt_token_count"] != right["prompt_token_count"] or left["tokens"] != right["tokens"]:
                        raise RuntimeError("OFF/ON exact token, source or row correctness failed")
                    if len(left["sampled_logprobs"]) != 32 or len(right["sampled_logprobs"]) != 32:
                        raise RuntimeError("sampled-token logprob length changed")
                    for off_value, on_value in zip(left["sampled_logprobs"], right["sampled_logprobs"]):
                        if abs(off_value - on_value) > 0.05 + 0.01 * abs(off_value):
                            raise RuntimeError("original sampled-token logprob tolerance failed")
            off = [row for row in measured if row["arm"] == "OFF"]
            on = [row for row in measured if row["arm"] == "ON"]
            cuda_off = statistics.median(row["request_cuda_event_ms"] for row in off)
            cuda_on = statistics.median(row["request_cuda_event_ms"] for row in on)
            host_off = statistics.median(row["host_wall_ms"] for row in off)
            host_on = statistics.median(row["host_wall_ms"] for row in on)
            neutrality = {"cuda_off_median_ms": cuda_off, "cuda_on_median_ms": cuda_on,
                          "cuda_limit_ms": max(5.0, 0.10 * cuda_off),
                          "host_off_median_ms": host_off, "host_on_median_ms": host_on,
                          "host_crosscheck_limit_ms": max(5.0, 0.10 * host_off)}
            if abs(cuda_on - cuda_off) > neutrality["cuda_limit_ms"]:
                result["gate_status"] = "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_NEUTRALITY_FAIL"
                result["neutrality"] = neutrality
                raise RuntimeError("original CUDA-event neutrality gate failed")
            if abs(host_on - host_off) > neutrality["host_crosscheck_limit_ms"]:
                result["gate_status"] = "CANARY_ENGINEERING_STOP"
                result["neutrality"] = neutrality
                raise RuntimeError("host-wall cross-check discrepant")
            kernel_inventory = {}
            for native_arm in ("OFF", "ON"):
                if time.monotonic() - started >= point_cap:
                    raise RuntimeError("point GPU-active cap prevents identity inventory")
                with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
                             record_shapes=False, profile_memory=False, with_stack=False) as profiler:
                    identity_request = request(native_arm == "ON")
                names = [event.name for event in profiler.events()
                         if getattr(event, "device_type", None) == torch.autograd.DeviceType.CUDA]
                inventory = dict(sorted(Counter(names).items()))
                kernel_inventory[native_arm] = {"kernel_count": len(names),
                                                "kernel_inventory": inventory,
                                                "kernel_inventory_sha256": sha_json(inventory),
                                                "identity_request_semantic_sha256": identity_request["semantic"]["semantic_order_sha256"] if native_arm == "ON" else None}
            if kernel_inventory["OFF"]["kernel_count"] != kernel_inventory["ON"]["kernel_count"] or kernel_inventory["OFF"]["kernel_inventory_sha256"] != kernel_inventory["ON"]["kernel_inventory_sha256"]:
                result["gate_status"] = "COMPILED_NO_CUDAGRAPH_OBSERVER_V2_IDENTITY_FAIL"
                raise RuntimeError("OFF/ON compiled kernel inventory changed")

        compiled_modules = [{"name": name, "class": type(module).__name__,
                             "do_not_compile": bool(getattr(module, "do_not_compile", True)),
                             "compiled": bool(getattr(module, "compiled", False)),
                             "aot_compiled_fn": getattr(module, "aot_compiled_fn", None) is not None}
                            for name, module in model_modules if isinstance(module, TorchCompileWithNoGuardsWrapper)]
        active_qwen = [row for row in compiled_modules if row["class"] == "Qwen2Model"
                       and not row["do_not_compile"] and (row["compiled"] or row["aot_compiled_fn"])]
        if not active_qwen or not model_calls["compiled_at_call"] or model_calls["skip_compiled_seen"]:
            raise RuntimeError("observer invalidated compiled Qwen2Model identity")
        if graph_manager.needs_capture() or graph_manager.graphs:
            raise RuntimeError("MODE_B unexpectedly captured CUDA Graph")
        if time.monotonic() - started > point_cap:
            raise RuntimeError("point GPU-active cap exceeded")
        result.update({"status": "PASS", "warmups": warmups, "measured": measured,
                       "kernel_inventory": kernel_inventory,
                       "neutrality": neutrality if args.arm == "NATIVE" else None,
                       "config": {"enforce_eager": config.model_config.enforce_eager,
                                  "compilation_mode": cc.mode.name, "backend": cc.backend,
                                  "cudagraph_mode": cc.cudagraph_mode.name},
                       "runtime_identity": {"compiled_qwen2model": True,
                                            "skip_compiled_seen": model_calls["skip_compiled_seen"],
                                            "model_call_count": model_calls["count"],
                                            "capture_count": len(graph_manager.graphs),
                                            "attention_impl": attention, "linear_method": linear,
                                            "compiled_modules": compiled_modules},
                       "duration_role": "QUALIFICATION_DIAGNOSTIC_ONLY",
                       "gpu_active_seconds": time.monotonic() - started})
    except BaseException as error:
        result.update({"status": "ERROR", "error_type": type(error).__name__,
                       "error": str(error), "traceback": traceback.format_exc(),
                       "gpu_active_seconds": time.monotonic() - started})
    finally:
        if model_class is not None and original_model_call is not None:
            model_class.__call__ = original_model_call
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print(json.dumps({key: result.get(key) for key in ("point", "arm", "status", "error_type")}))
    if result["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
