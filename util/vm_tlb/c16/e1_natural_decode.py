#!/usr/bin/env python3
"""Four-step deterministic natural AWQ decode with occurrence-level timing/NVTX."""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM


AWQ = "/data/c16/models/.incoming/qwen2p5_7b_instruct_awq/b25037543e9394b818fdfca67ab2a00ecc7dd641"
TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_FILE_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tensor_sha(tensor):
    raw = tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(raw).hexdigest()


def range_name(target, decode_index):
    return f"C16_E1_NAT_{target}_D{decode_index}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output")
    args = parser.parse_args()
    if file_sha(TOKENS) != TOKEN_FILE_SHA:
        raise RuntimeError("S2_TEXT token authority mismatch")
    token_ids = json.loads(TOKENS.read_text())
    if len(token_ids) != 2048:
        raise RuntimeError("S2_TEXT token length mismatch")

    torch.manual_seed(0)
    wrapper = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    model = wrapper.model.eval()
    targets = {
        "L0_UP": model.model.layers[0].mlp.up_proj,
        "L14_UP": model.model.layers[14].mlp.up_proj,
        "L0_DOWN": model.model.layers[0].mlp.down_proj,
    }
    active_decode = {"value": None}
    captures = {}
    pending = {}
    handles = []

    def make_pre(target):
        def hook(module, module_args):
            decode_index = active_decode["value"]
            if decode_index is None:
                return
            key = (target, decode_index)
            if key in captures or key in pending:
                raise RuntimeError(f"duplicate occurrence {key}")
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            name = range_name(target, decode_index)
            torch.cuda.nvtx.range_push(name)
            start.record()
            pending[key] = {
                "start": start,
                "stop": stop,
                "range": name,
                "input": module_args[0].detach(),
                "module_class": type(module).__name__,
            }
        return hook

    def make_post(target):
        def hook(module, module_args, output):
            decode_index = active_decode["value"]
            if decode_index is None:
                return
            key = (target, decode_index)
            record = pending.pop(key)
            record["stop"].record()
            torch.cuda.nvtx.range_pop()
            record["output"] = output.detach()
            captures[key] = record
        return hook

    for target, module in targets.items():
        handles.append(module.register_forward_pre_hook(make_pre(target)))
        handles.append(module.register_forward_hook(make_post(target)))

    input_ids = torch.tensor([token_ids], dtype=torch.long, device="cuda")
    decode_token_tensors = []
    step_events = []
    with torch.inference_mode():
        prefill = model(input_ids=input_ids, use_cache=True)
        past = prefill.past_key_values
        current = torch.argmax(prefill.logits[:, -1, :], dim=-1, keepdim=True)
        del prefill
        for decode_index in range(4):
            decode_token_tensors.append(current.detach())
            active_decode["value"] = decode_index
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            start.record()
            result = model(input_ids=current, past_key_values=past, use_cache=True)
            past = result.past_key_values
            current = torch.argmax(result.logits[:, -1, :], dim=-1, keepdim=True)
            stop.record()
            step_events.append((start, stop))
            active_decode["value"] = None
            del result
    torch.cuda.synchronize()
    for handle in handles:
        handle.remove()
    if pending or len(captures) != 12:
        raise RuntimeError(f"occurrence closure failed: captures={len(captures)} pending={len(pending)}")

    generated_tokens = [int(token.item()) for token in decode_token_tensors]
    occurrences = []
    for decode_index in range(4):
        for target in ("L0_UP", "L14_UP", "L0_DOWN"):
            record = captures[(target, decode_index)]
            occurrences.append(
                {
                    "target": target,
                    "decode_index": decode_index,
                    "token_id": generated_tokens[decode_index],
                    "range": record["range"],
                    "input_sha256": tensor_sha(record["input"]),
                    "output_sha256": tensor_sha(record["output"]),
                    "input_shape": list(record["input"].shape),
                    "output_shape": list(record["output"].shape),
                    "module_class": record["module_class"],
                    "target_ms": float(record["start"].elapsed_time(record["stop"])),
                }
            )
    result = {
        "status": "PASS",
        "run_index": args.run_index,
        "model_root": AWQ,
        "backend": "AutoAWQForCausalLM/WQLinear_GEMM",
        "token_file_sha256": TOKEN_FILE_SHA,
        "prefix_tokens": len(token_ids),
        "generated_token_ids_D0_D3": generated_tokens,
        "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in step_events],
        "occurrences": occurrences,
        "no_inner_loop_synchronize": True,
        "prefill_excluded_from_M1_occurrences": True,
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
