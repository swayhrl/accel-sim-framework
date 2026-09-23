#!/usr/bin/env python3
"""Optional accepted RAW BF16 full-model natural decode control."""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM


RAW = Path("/data/c16/models/.incoming/qwen2p5_7b_instruct_raw/a09a35458c702b33eeacc393d103063234e8bc28")
TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_FILE_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output")
    args = parser.parse_args()
    if hashlib.sha256(TOKENS.read_bytes()).hexdigest() != TOKEN_FILE_SHA:
        raise RuntimeError("token authority mismatch")
    prefix = json.loads(TOKENS.read_text())
    model = AutoModelForCausalLM.from_pretrained(RAW, torch_dtype=torch.bfloat16, low_cpu_mem_usage=True).cuda().eval()
    module = model.model.layers[0].mlp.up_proj
    active = {"decode": None}
    pending = {}
    captures = {}

    def pre_hook(target_module, module_args):
        decode_index = active["decode"]
        if decode_index is None:
            return
        start = torch.cuda.Event(enable_timing=True)
        stop = torch.cuda.Event(enable_timing=True)
        name = f"C16_E1_RAW_NAT_L0_UP_D{decode_index}"
        torch.cuda.nvtx.range_push(name)
        start.record()
        pending[decode_index] = {"start": start, "stop": stop, "range": name, "input": module_args[0].detach()}

    def post_hook(target_module, module_args, output):
        decode_index = active["decode"]
        if decode_index is None:
            return
        record = pending.pop(decode_index)
        record["stop"].record()
        torch.cuda.nvtx.range_pop()
        record["output"] = output.detach()
        captures[decode_index] = record

    handles = [module.register_forward_pre_hook(pre_hook), module.register_forward_hook(post_hook)]
    ids = torch.tensor([prefix], dtype=torch.long, device="cuda")
    tokens = []
    step_events = []
    with torch.inference_mode():
        result = model(input_ids=ids, use_cache=True)
        past = result.past_key_values
        current = torch.argmax(result.logits[:, -1, :], dim=-1, keepdim=True)
        del result
        for decode_index in range(4):
            tokens.append(current.detach())
            active["decode"] = decode_index
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            start.record()
            result = model(input_ids=current, past_key_values=past, use_cache=True)
            past = result.past_key_values
            current = torch.argmax(result.logits[:, -1, :], dim=-1, keepdim=True)
            stop.record()
            step_events.append((start, stop))
            active["decode"] = None
            del result
    torch.cuda.synchronize()
    for handle in handles:
        handle.remove()
    token_ids = [int(token.item()) for token in tokens]
    occurrences = []
    for decode_index in range(4):
        record = captures[decode_index]
        occurrences.append(
            {
                "target": "L0_UP",
                "decode_index": decode_index,
                "token_id": token_ids[decode_index],
                "range": record["range"],
                "input_sha256": tensor_sha(record["input"]),
                "output_sha256": tensor_sha(record["output"]),
                "input_shape": list(record["input"].shape),
                "output_shape": list(record["output"].shape),
                "module_class": type(module).__name__,
                "target_ms": float(record["start"].elapsed_time(record["stop"])),
            }
        )
    receipt = {
        "status": "PASS",
        "run_index": args.run_index,
        "model_root": str(RAW),
        "dtype": "torch.bfloat16",
        "backend": "transformers.Qwen2ForCausalLM/torch.nn.Linear",
        "offload": False,
        "generated_token_ids_D0_D3": token_ids,
        "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in step_events],
        "occurrences": occurrences,
        "no_inner_loop_synchronize": True,
    }
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
