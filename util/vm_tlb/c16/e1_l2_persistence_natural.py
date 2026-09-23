#!/usr/bin/env python3
"""Natural four-step AWQ decode under an audited CUDA L2 persistence condition."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import PersistenceHelper, qweight_region
from e1_residency_common import AWQ


TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_FILE_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"
ACCEPTED_BINDINGS = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-l2-persistence-intervention-109-v1/docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1/NATURAL_OCCURRENCE_BINDINGS.tsv")
EXPECTED_TOKENS = [23578, 11, 323, 3950]
CONDITIONS = ("BASELINE", "SETASIDE_ONLY", "PERSIST_L0_UP", "PERSIST_L14_UP", "PERSIST_L0_DOWN", "BUDGET_L0_UP")


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def range_name(condition, target, decode_index):
    return f"C16_E1_L2P_{condition}_{target}_D{decode_index}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--budget-bytes", type=int)
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output")
    args = parser.parse_args()
    if hashlib.sha256(TOKENS.read_bytes()).hexdigest() != TOKEN_FILE_SHA:
        raise RuntimeError("token authority mismatch")
    prefix = json.loads(TOKENS.read_text())
    model_wrapper = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    model = model_wrapper.model.eval()
    targets = {
        "L0_UP": model.model.layers[0].mlp.up_proj,
        "L14_UP": model.model.layers[14].mlp.up_proj,
        "L0_DOWN": model.model.layers[0].mlp.down_proj,
    }
    qweights = {
        "PERSIST_L0_UP": targets["L0_UP"].qweight,
        "PERSIST_L14_UP": targets["L14_UP"].qweight,
        "PERSIST_L0_DOWN": targets["L0_DOWN"].qweight,
        "BUDGET_L0_UP": targets["L0_UP"].qweight,
    }
    full_qweight_bytes = targets["L0_UP"].qweight.numel() * targets["L0_UP"].qweight.element_size()
    if args.condition == "BASELINE":
        requested_budget = 0
        policy_tensor = None
        hit_ratio = 1.0
    elif args.condition == "SETASIDE_ONLY":
        requested_budget = full_qweight_bytes
        policy_tensor = None
        hit_ratio = 1.0
    elif args.condition == "BUDGET_L0_UP":
        if args.budget_bytes is None or args.budget_bytes <= 0:
            raise RuntimeError("budget sweep condition requires positive --budget-bytes")
        requested_budget = args.budget_bytes
        policy_tensor = qweights[args.condition]
        hit_ratio = min(1.0, requested_budget / full_qweight_bytes)
    else:
        requested_budget = full_qweight_bytes
        policy_tensor = qweights[args.condition]
        hit_ratio = 1.0
    helper = PersistenceHelper()
    policy_receipt = helper.begin_condition(args.condition, requested_budget, policy_tensor, hit_ratio)
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
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            name = range_name(args.condition, target, decode_index)
            torch.cuda.nvtx.range_push(name)
            start.record()
            pending[key] = {"start": start, "stop": stop, "range": name, "input": module_args[0].detach(), "module_class": type(module).__name__}
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
    token_tensors = []
    step_events = []
    prefill_events = (torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True))
    try:
        input_ids = torch.tensor([prefix], dtype=torch.long, device="cuda")
        with torch.inference_mode():
            prefill_events[0].record()
            prefill = model(input_ids=input_ids, use_cache=True)
            current = torch.argmax(prefill.logits[:, -1, :], dim=-1, keepdim=True)
            prefill_events[1].record()
            past = prefill.past_key_values
            del prefill
            for decode_index in range(4):
                token_tensors.append(current.detach())
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
            raise RuntimeError("occurrence closure")
        token_ids = [int(token.item()) for token in token_tensors]
        occurrences = []
        for decode_index in range(4):
            for target in ("L0_UP", "L14_UP", "L0_DOWN"):
                record = captures[(target, decode_index)]
                occurrences.append(
                    {
                        "target": target,
                        "decode_index": decode_index,
                        "token_id": token_ids[decode_index],
                        "range": record["range"],
                        "input_sha256": tensor_sha(record["input"]),
                        "output_sha256": tensor_sha(record["output"]),
                        "input_shape": list(record["input"].shape),
                        "output_shape": list(record["output"].shape),
                        "module_class": record["module_class"],
                        "target_ms": float(record["start"].elapsed_time(record["stop"])),
                    }
                )
        if token_ids != EXPECTED_TOKENS:
            raise RuntimeError(f"generated token identity drift: {token_ids}")
        accepted = {}
        with ACCEPTED_BINDINGS.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                accepted[(row["target"], int(row["decode_index"]))] = (row["input_sha256"], row["output_sha256"])
        for occurrence in occurrences:
            expected = accepted[(occurrence["target"], occurrence["decode_index"])]
            if (occurrence["input_sha256"], occurrence["output_sha256"]) != expected:
                raise RuntimeError(f"occurrence identity drift: {occurrence['target']} D{occurrence['decode_index']}")
        result = {
            "status": "PASS",
            "condition": args.condition,
            "run_index": args.run_index,
            "generated_token_ids_D0_D3": token_ids,
            "token_file_sha256": TOKEN_FILE_SHA,
            "occurrences": occurrences,
            "prefill_ms": float(prefill_events[0].elapsed_time(prefill_events[1])),
            "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in step_events],
            "policy_receipt": policy_receipt,
            "qweight_regions": {name: qweight_region(module, f"{name}.qweight") for name, module in targets.items()},
            "no_inner_loop_synchronize": True,
        }
    finally:
        policy_receipt = helper.end_condition(policy_receipt)
    result["policy_receipt"] = policy_receipt
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
