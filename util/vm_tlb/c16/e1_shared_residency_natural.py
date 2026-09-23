#!/usr/bin/env python3
"""Natural AWQ decode with fixed-budget rotating/shared qweight windows."""

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
ACCEPTED_BINDINGS = Path("/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-shared-residency-feasibility-109-v1/docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1/NATURAL_OCCURRENCE_BINDINGS.tsv")
EXPECTED_TOKENS = [23578, 11, 323, 3950]
CONDITIONS = ("SETASIDE_ONLY", "ROTATE_CONTROL_3", "SINGLE_L0_UP", "SHARE2_UP", "SHARE2_L0", "SHARE3")


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def policy_spec(condition, target):
    if condition == "ROTATE_CONTROL_3":
        return 1.0 / 3.0, False
    if condition == "SINGLE_L0_UP":
        return 1.0, target == "L0_UP"
    if condition == "SHARE2_UP":
        return 0.5, target in ("L0_UP", "L14_UP")
    if condition == "SHARE2_L0":
        return 0.5, target in ("L0_UP", "L0_DOWN")
    if condition == "SHARE3":
        return 1.0 / 3.0, True
    raise ValueError(condition)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=CONDITIONS, required=True)
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output")
    args = parser.parse_args()
    if hashlib.sha256(TOKENS.read_bytes()).hexdigest() != TOKEN_FILE_SHA:
        raise RuntimeError("token authority mismatch")
    prefix = json.loads(TOKENS.read_text())
    wrapper = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    model = wrapper.model.eval()
    targets = {
        "L0_UP": model.model.layers[0].mlp.up_proj,
        "L14_UP": model.model.layers[14].mlp.up_proj,
        "L0_DOWN": model.model.layers[0].mlp.down_proj,
    }
    qweight_bytes = targets["L0_UP"].qweight.numel() * targets["L0_UP"].qweight.element_size()
    helper = PersistenceHelper()
    policy_receipt = helper.begin_condition(args.condition, qweight_bytes, None, 1.0)
    active_decode = {"value": None}
    phase = {"value": "PREFILL"}
    captures = {}
    pending = {}
    transitions = []
    handles = []

    def make_pre(target):
        def hook(module, module_args):
            if args.condition != "SETASIDE_ONLY":
                hit_ratio, persisting = policy_spec(args.condition, target)
                transition = helper.update_access_policy(
                    f"{phase['value']}:{target}", module.qweight, hit_ratio, persisting
                )
                transition["phase"] = phase["value"]
                transition["target"] = target
                transition["before_target_event"] = True
                transitions.append(transition)
            decode_index = active_decode["value"]
            if decode_index is None:
                return
            key = (target, decode_index)
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            name = f"C16_E1_SHARED_{args.condition}_{target}_D{decode_index}"
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
    token_tensors = []
    step_events = []
    try:
        ids = torch.tensor([prefix], dtype=torch.long, device="cuda")
        with torch.inference_mode():
            prefill = model(input_ids=ids, use_cache=True)
            current = torch.argmax(prefill.logits[:, -1, :], dim=-1, keepdim=True)
            past = prefill.past_key_values
            del prefill
            for decode_index in range(4):
                token_tensors.append(current.detach())
                active_decode["value"] = decode_index
                phase["value"] = f"D{decode_index}"
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
        generated_tokens = [int(token.item()) for token in token_tensors]
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
        if generated_tokens != EXPECTED_TOKENS:
            raise RuntimeError(f"generated token drift: {generated_tokens}")
        accepted = {}
        with ACCEPTED_BINDINGS.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                accepted[(row["target"], int(row["decode_index"]))] = (row["input_sha256"], row["output_sha256"])
        for occurrence in occurrences:
            if (occurrence["input_sha256"], occurrence["output_sha256"]) != accepted[(occurrence["target"], occurrence["decode_index"])]:
                raise RuntimeError(f"occurrence identity drift: {occurrence['target']} D{occurrence['decode_index']}")
        result = {
            "status": "PASS",
            "condition": args.condition,
            "run_index": args.run_index,
            "generated_token_ids_D0_D3": generated_tokens,
            "occurrences": occurrences,
            "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in step_events],
            "policy_receipt": policy_receipt,
            "policy_transitions": transitions,
            "policy_transition_count": len(transitions),
            "policy_calls_before_target_events": True,
            "no_reset_between_transitions": True,
            "qweight_regions": {target: qweight_region(module, f"{target}.qweight") for target, module in targets.items()},
            "no_inner_loop_synchronize": True,
        }
    finally:
        policy_receipt = helper.end_condition(policy_receipt)
    result["policy_receipt"] = policy_receipt
    expected_updates = 0 if args.condition == "SETASIDE_ONLY" else 15
    if result["policy_transition_count"] != expected_updates:
        raise RuntimeError(f"policy transition count {result['policy_transition_count']} != {expected_updates}")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
