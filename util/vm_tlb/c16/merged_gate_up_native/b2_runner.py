#!/usr/bin/env python3
"""Pinned vLLM merged gate/up natural D0-D3 runner for C16 Lane 7."""

import argparse
import hashlib
import json
import os
import re
import types
from pathlib import Path

os.environ.setdefault("VLLM_ENABLE_V1_MULTIPROCESSING", "0")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("VLLM_LOGGING_LEVEL", "WARNING")

import torch
from vllm import LLM, SamplingParams
from vllm.model_executor.models.qwen2 import Qwen2MLP


MODEL = Path("/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641")
TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_FILE_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"
EXPECTED_TOKENS = [23578, 11, 323, 3950]


def file_sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tensor_sha(tensor):
    data = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def first_tensor(output):
    if isinstance(output, torch.Tensor):
        return output
    if isinstance(output, (tuple, list)) and output and isinstance(output[0], torch.Tensor):
        return output[0]
    raise TypeError(f"cannot extract tensor from {type(output)}")


def tensor_meta(tensor):
    return {"shape": list(tensor.shape), "dtype": str(tensor.dtype),
            "device": str(tensor.device), "numel": tensor.numel(),
            "bytes": tensor.numel() * tensor.element_size()}


def object_tensor_meta(obj):
    result = {}
    if obj is None:
        return result
    for name, value in vars(obj).items():
        if isinstance(value, torch.Tensor):
            result[name] = tensor_meta(value)
        elif isinstance(value, (str, int, float, bool, type(None))):
            result[name] = value
        elif isinstance(value, (list, tuple)) and all(isinstance(x, (str, int, float, bool, type(None))) for x in value):
            result[name] = list(value)
    return result


def extract_tokens(outputs, request_id):
    for output in outputs:
        if output.request_id == request_id and output.outputs:
            return list(output.outputs[0].token_ids)
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tensor-dump", type=Path)
    parser.add_argument("--timeline-nvtx", choices=("off", "on"), default="off")
    args = parser.parse_args()
    if file_sha(TOKENS) != TOKEN_FILE_SHA:
        raise RuntimeError("token authority mismatch")
    prefix = json.loads(TOKENS.read_text())
    if len(prefix) != 2048:
        raise RuntimeError(f"prompt length drift: {len(prefix)}")

    llm = LLM(
        model=str(MODEL), tokenizer=str(MODEL), skip_tokenizer_init=True,
        dtype="float16", quantization="awq", enforce_eager=True,
        tensor_parallel_size=1, max_model_len=4096, max_num_batched_tokens=4096,
        max_num_seqs=1, gpu_memory_utilization=0.90, enable_prefix_caching=False,
        seed=0, disable_log_stats=True,
    )
    engine = llm.llm_engine
    model_runner = engine.model_executor.driver_worker.model_runner
    model = model_runner.model
    mlps = []
    for name, module in model.named_modules():
        if isinstance(module, Qwen2MLP):
            match = re.search(r"layers\.(\d+)\.mlp$", name)
            if not match:
                raise RuntimeError(f"cannot bind Qwen2MLP layer index: {name}")
            mlps.append((int(match.group(1)), name, module))
    mlps.sort()
    if [row[0] for row in mlps] != list(range(28)):
        raise RuntimeError(f"Qwen2 MLP census mismatch: {[x[0] for x in mlps]}")

    state = {"active": False, "decode_index": 0, "current": None,
             "wall_start": torch.cuda.Event(enable_timing=True),
             "wall_stop": torch.cuda.Event(enable_timing=True),
             "step_events": [], "timeline_open": False,
             "inactive_execute_token_counts": []}
    pending = {}
    captures = {}
    ffn_pending = {}
    ffn_captures = {}
    handles = []

    def make_pre(layer, role):
        def hook(module, module_args):
            decode = state["current"]
            if not state["active"] or decode is None:
                return
            key = (layer, role, decode)
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            captured_input = module_args[0].detach().clone() if args.tensor_dump else None
            label = f"C16_MERGED_BASELINE_B2_L{layer}_D{decode}_{role.upper()}"
            if args.timeline_nvtx == "on":
                torch.cuda.nvtx.range_push(label)
            start.record()
            pending[key] = {"start": start, "stop": stop, "range": label,
                            "input": captured_input}
        return hook

    def make_post(layer, role):
        def hook(module, module_args, output):
            decode = state["current"]
            if not state["active"] or decode is None:
                return
            key = (layer, role, decode)
            record = pending.pop(key)
            record["stop"].record()
            if args.timeline_nvtx == "on":
                torch.cuda.nvtx.range_pop()
            value = first_tensor(output)
            record["output"] = value.detach().clone() if args.tensor_dump else None
            record["input_shape"] = list(module_args[0].shape)
            record["output_shape"] = list(value.shape)
            captures[key] = record
        return hook

    def make_ffn_pre(layer):
        def hook(module, module_args):
            decode = state["current"]
            if not state["active"] or decode is None:
                return
            key = (layer, decode)
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            captured_input = module_args[0].detach().clone() if args.tensor_dump else None
            label = f"C16_MERGED_BASELINE_B2_L{layer}_D{decode}_FFN"
            if args.timeline_nvtx == "on":
                torch.cuda.nvtx.range_push(label)
            start.record()
            ffn_pending[key] = {"start": start, "stop": stop, "range": label,
                                "input": captured_input}
        return hook

    def make_ffn_post(layer):
        def hook(module, module_args, output):
            decode = state["current"]
            if not state["active"] or decode is None:
                return
            key = (layer, decode)
            record = ffn_pending.pop(key)
            record["stop"].record()
            if args.timeline_nvtx == "on":
                torch.cuda.nvtx.range_pop()
            value = first_tensor(output)
            record["output"] = value.detach().clone() if args.tensor_dump else None
            record["input_shape"] = list(module_args[0].shape)
            record["output_shape"] = list(value.shape)
            ffn_captures[key] = record
        return hook

    for layer, _, mlp in mlps:
        handles.extend([
            mlp.register_forward_pre_hook(make_ffn_pre(layer)),
            mlp.register_forward_hook(make_ffn_post(layer)),
            mlp.gate_up_proj.register_forward_pre_hook(make_pre(layer, "gate_up")),
            mlp.gate_up_proj.register_forward_hook(make_post(layer, "gate_up")),
            mlp.act_fn.register_forward_pre_hook(make_pre(layer, "silu_and_mul")),
            mlp.act_fn.register_forward_hook(make_post(layer, "silu_and_mul")),
            mlp.down_proj.register_forward_pre_hook(make_pre(layer, "down")),
            mlp.down_proj.register_forward_hook(make_post(layer, "down")),
        ])

    original_execute = model_runner.execute_model
    original_sample = model_runner.sample_tokens

    def execute_wrapper(self, scheduler_output, intermediate_tensors=None):
        if not state["active"]:
            state["inactive_execute_token_counts"].append(scheduler_output.total_num_scheduled_tokens)
        else:
            decode = state["decode_index"]
            if decode >= 4 or scheduler_output.total_num_scheduled_tokens != 1:
                raise RuntimeError(f"decode schedule drift D{decode} tokens={scheduler_output.total_num_scheduled_tokens}")
            state["current"] = decode
            if decode == 0:
                if args.timeline_nvtx == "on":
                    torch.cuda.nvtx.range_push("C16_MERGED_BASELINE_B2_DECODE_D0_D3")
                    state["timeline_open"] = True
                state["wall_start"].record()
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            start.record()
            state["step_events"].append((start, stop))
        return original_execute(scheduler_output, intermediate_tensors)

    def sample_wrapper(self, grammar_output):
        result = original_sample(grammar_output)
        if state["active"]:
            decode = state["current"]
            if decode is None:
                raise RuntimeError("sample without active decode")
            state["step_events"][-1][1].record()
            if decode == 3:
                state["wall_stop"].record()
                if state["timeline_open"]:
                    torch.cuda.nvtx.range_pop()
                    state["timeline_open"] = False
            state["decode_index"] += 1
            state["current"] = None
        return result

    model_runner.execute_model = types.MethodType(execute_wrapper, model_runner)
    model_runner.sample_tokens = types.MethodType(sample_wrapper, model_runner)

    params = SamplingParams(temperature=0.0, max_tokens=5, ignore_eos=True, detokenize=False)
    request_id = f"C16_MERGED_B2_{args.run_index}"
    engine.add_request(request_id, {"prompt_token_ids": prefix}, params)
    outputs = engine.step()
    prefill_frontend_steps = 1
    if extract_tokens(outputs, request_id) or state["inactive_execute_token_counts"] != [2048]:
        raise RuntimeError(f"prefill queue boundary drift outputs={outputs} executes={state['inactive_execute_token_counts']}")
    state["active"] = True
    final_tokens = []
    decode_frontend_steps = 0
    while state["decode_index"] < 4 or len(final_tokens) < 4:
        outputs = engine.step()
        decode_frontend_steps += 1
        step_tokens = extract_tokens(outputs, request_id)
        if step_tokens:
            final_tokens = step_tokens
        if decode_frontend_steps > 12:
            raise RuntimeError("decode output not delivered within twelve frontend steps")
    torch.cuda.synchronize()
    generated = final_tokens[:4]
    if state["decode_index"] != 4 or len(state["step_events"]) != 4:
        raise RuntimeError(f"decode closure failure: {state['decode_index']}")
    if pending or ffn_pending or len(captures) != 336 or len(ffn_captures) != 112:
        raise RuntimeError(f"capture closure pending={len(pending)}/{len(ffn_pending)} captures={len(captures)}/{len(ffn_captures)}")

    occurrences = []
    for layer in range(28):
        for role in ("gate_up", "silu_and_mul", "down"):
            for decode in range(4):
                record = captures[(layer, role, decode)]
                occurrences.append({"layer": layer, "role": role, "decode_index": decode,
                                    "range": record["range"], "input_shape": record["input_shape"],
                                    "output_shape": record["output_shape"],
                                    "target_ms": float(record["start"].elapsed_time(record["stop"]))})
    ffn_occurrences = []
    for layer in range(28):
        for decode in range(4):
            record = ffn_captures[(layer, decode)]
            ffn_occurrences.append({"layer": layer, "decode_index": decode,
                                    "range": record["range"], "input_shape": record["input_shape"],
                                    "output_shape": record["output_shape"],
                                    "target_ms": float(record["start"].elapsed_time(record["stop"]))})

    module_census = []
    for layer, name, mlp in mlps:
        quant = mlp.gate_up_proj.quant_method
        kernel = getattr(quant, "kernel", None)
        parameters = {param_name: tensor_meta(param) for param_name, param in mlp.gate_up_proj.named_parameters(recurse=False)}
        module_census.append({
            "layer": layer, "path": name, "mlp_class": type(mlp).__name__,
            "gate_up_class": type(mlp.gate_up_proj).__name__,
            "activation_class": type(mlp.act_fn).__name__, "down_class": type(mlp.down_proj).__name__,
            "quant_method_class": type(quant).__name__,
            "kernel_backend_class": type(kernel).__name__ if kernel is not None else None,
            "kernel_backend_module": type(kernel).__module__ if kernel is not None else None,
            "gate_up_parameters": parameters, "quant_method_state": object_tensor_meta(quant),
            "kernel_state": object_tensor_meta(kernel),
        })

    tensor_dump_status = None
    if args.tensor_dump:
        payload = {"arm": "B2", "generated_token_ids_D0_D3": generated, "tensors": {}}
        finite = True
        for (layer, role, decode), record in sorted(captures.items()):
            inp = record["input"].cpu()
            out = record["output"].cpu()
            finite = finite and bool(torch.isfinite(inp).all()) and bool(torch.isfinite(out).all())
            if role == "gate_up":
                logical = out.reshape(1, 1, -1)
                if list(logical.shape) != [1, 1, 37888]:
                    raise RuntimeError(f"gate_up shape drift L{layer} D{decode}: {list(logical.shape)}")
                payload["tensors"][f"L{layer}.D{decode}.gate_proj.output"] = logical[..., :18944]
                payload["tensors"][f"L{layer}.D{decode}.up_proj.output"] = logical[..., 18944:]
                payload["tensors"][f"L{layer}.D{decode}.gate_up.input"] = inp.reshape(1, 1, -1)
            elif role == "down":
                payload["tensors"][f"L{layer}.D{decode}.down_proj.output"] = out.reshape(1, 1, -1)
        for (layer, decode), record in sorted(ffn_captures.items()):
            payload["tensors"][f"L{layer}.D{decode}.ffn.input"] = record["input"].cpu().reshape(1, 1, -1)
            payload["tensors"][f"L{layer}.D{decode}.ffn.output"] = record["output"].cpu().reshape(1, 1, -1)
        torch.save(payload, args.tensor_dump)
        tensor_dump_status = {"path": str(args.tensor_dump), "sha256": file_sha(args.tensor_dump),
                              "tensor_count": len(payload["tensors"]), "all_finite": finite}

    status = "PASS" if generated == EXPECTED_TOKENS else "TOKEN_IDENTITY_FAILED"
    result = {
        "status": status, "arm": "B2", "run_index": args.run_index,
        "runtime": "vLLM exact commit df8fd42116f172b7a53bc10c8a680b05232edbed",
        "model_path": str(MODEL), "checkpoint_revision": MODEL.name,
        "generated_token_ids_D0_D3": generated, "all_generated_token_ids": final_tokens,
        "decode_wall_ms": float(state["wall_start"].elapsed_time(state["wall_stop"])),
        "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in state["step_events"]],
        "occurrences": occurrences, "ffn_occurrences": ffn_occurrences,
        "module_census": module_census, "timeline_nvtx": args.timeline_nvtx,
        "tensor_dump": tensor_dump_status, "prompt_tokens": len(prefix),
        "prefill_frontend_steps": prefill_frontend_steps,
        "decode_frontend_steps": decode_frontend_steps,
        "inactive_execute_token_counts": state["inactive_execute_token_counts"],
        "logical_gate_up_slice_shape": [1, 1, 18944], "down_shape": [1, 1, 3584],
        "no_requantization_claim_basis": "CPU canonical identity plus vLLM lossless AWQ repack source; runtime physical layout may differ",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": status, "generated_token_ids_D0_D3": generated,
                      "decode_wall_ms": result["decode_wall_ms"],
                      "kernel_backends": sorted({row["kernel_backend_class"] for row in module_census})}, sort_keys=True))
    for handle in handles:
        handle.remove()
    if status != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
