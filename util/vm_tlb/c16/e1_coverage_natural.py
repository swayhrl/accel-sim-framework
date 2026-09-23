#!/usr/bin/env python3
"""Full-model FFN census and fixed-budget up_proj coverage conditions."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import PersistenceHelper, qweight_region
from e1_residency_common import AWQ


ROOT = Path("/data/c16/e1_coverage_scaling_v1")
TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_FILE_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"
EXPECTED_TOKENS = [23578, 11, 323, 3950]
ROLES = ("gate_proj", "up_proj", "down_proj")


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def parse_condition(condition, manifest):
    if condition == "CENSUS_FFN_NO_PERSIST":
        return {"mode": "CENSUS", "set_name": None, "layers": [], "hit_ratio": 0.0, "persisting": False}
    if condition.startswith("CONTROL_FULL_"):
        set_name = condition.removeprefix("CONTROL_FULL_")
        return {"mode": "COVERAGE", "set_name": set_name, "layers": manifest["sets"][set_name], "hit_ratio": 1.0, "persisting": False}
    if condition.startswith("FULLHINT_"):
        set_name = condition.removeprefix("FULLHINT_")
        return {"mode": "COVERAGE", "set_name": set_name, "layers": manifest["sets"][set_name], "hit_ratio": 1.0, "persisting": True}
    prefix, set_name = condition.split("_", 1)
    layers = manifest["sets"][set_name]
    return {"mode": "COVERAGE", "set_name": set_name, "layers": layers, "hit_ratio": 1.0 / len(layers), "persisting": prefix == "FAIR"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=True)
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output")
    args = parser.parse_args()
    manifest = json.loads((ROOT / "contracts/LAYER_SELECTION_PRECONTRACT.json").read_text())
    spec = parse_condition(args.condition, manifest)
    if hashlib.sha256(TOKENS.read_bytes()).hexdigest() != TOKEN_FILE_SHA:
        raise RuntimeError("token authority mismatch")
    prefix = json.loads(TOKENS.read_text())
    wrapper = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    model = wrapper.model.eval()
    layers = model.model.layers
    if len(layers) != 28:
        raise RuntimeError(f"layer count {len(layers)} != 28")
    module_map = {}
    module_census = []
    roles_to_hook = ROLES if spec["mode"] == "CENSUS" else ("up_proj",)
    for layer_index, layer in enumerate(layers):
        for role in ROLES:
            module = getattr(layer.mlp, role)
            supported = hasattr(module, "qweight")
            row = {"layer": layer_index, "role": role, "module_class": type(module).__name__, "supported_qweight_family": supported}
            if supported:
                row.update(qweight_region(module, f"layer{layer_index}.mlp.{role}.qweight"))
            module_census.append(row)
            if role in roles_to_hook:
                if not supported:
                    raise RuntimeError(f"unsupported requested module layer{layer_index}.{role}")
                module_map[(layer_index, role)] = module
    qweight_bytes = module_map[(0, "up_proj")].qweight.numel() * module_map[(0, "up_proj")].qweight.element_size()
    helper = PersistenceHelper()
    budget = 0 if spec["mode"] == "CENSUS" else qweight_bytes
    policy_receipt = helper.begin_condition(args.condition, budget, None, 1.0)
    if spec["mode"] == "COVERAGE":
        if budget != 33_947_648 or policy_receipt["actual_setaside_bytes"] != 37_748_736:
            raise RuntimeError(f"fixed persistence budget mismatch requested={budget} actual={policy_receipt['actual_setaside_bytes']}")
        for layer_index in spec["layers"]:
            module = module_map[(layer_index, "up_proj")]
            if module.qweight.numel() * module.qweight.element_size() != 33_947_648 or not module.qweight.is_contiguous():
                raise RuntimeError(f"selected qweight geometry mismatch layer {layer_index}")
    active_decode = {"value": None}
    phase = {"value": "PREFILL"}
    pending = {}
    captures = {}
    transitions = []
    handles = []

    def make_pre(layer_index, role):
        def hook(module, module_args):
            if spec["mode"] == "COVERAGE" and role == "up_proj" and layer_index in spec["layers"]:
                transition = helper.update_access_policy(
                    f"{phase['value']}:L{layer_index}:up_proj",
                    module.qweight,
                    spec["hit_ratio"],
                    spec["persisting"],
                )
                transition.update({"phase": phase["value"], "layer": layer_index, "role": role, "before_target_event": True})
                transitions.append(transition)
            decode_index = active_decode["value"]
            if decode_index is None:
                return
            key = (layer_index, role, decode_index)
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            name = f"C16_E1_COV_{args.condition}_L{layer_index}_{role.upper()}_D{decode_index}"
            torch.cuda.nvtx.range_push(name)
            start.record()
            pending[key] = {"start": start, "stop": stop, "range": name, "input": module_args[0].detach(), "module_class": type(module).__name__}
        return hook

    def make_post(layer_index, role):
        def hook(module, module_args, output):
            decode_index = active_decode["value"]
            if decode_index is None:
                return
            key = (layer_index, role, decode_index)
            record = pending.pop(key)
            record["stop"].record()
            torch.cuda.nvtx.range_pop()
            record["output"] = output.detach()
            captures[key] = record
        return hook

    for (layer_index, role), module in module_map.items():
        handles.append(module.register_forward_pre_hook(make_pre(layer_index, role)))
        handles.append(module.register_forward_hook(make_post(layer_index, role)))
    tokens = []
    step_events = []
    try:
        ids = torch.tensor([prefix], dtype=torch.long, device="cuda")
        with torch.inference_mode():
            prefill = model(input_ids=ids, use_cache=True)
            current = torch.argmax(prefill.logits[:, -1, :], dim=-1, keepdim=True)
            past = prefill.past_key_values
            del prefill
            for decode_index in range(4):
                tokens.append(current.detach())
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
        expected_occurrences = len(module_map) * 4
        if pending or len(captures) != expected_occurrences:
            raise RuntimeError(f"occurrence closure {len(captures)} != {expected_occurrences}")
        token_ids = [int(token.item()) for token in tokens]
        if token_ids != EXPECTED_TOKENS:
            raise RuntimeError(f"token drift {token_ids}")
        occurrences = []
        for layer_index, role in sorted(module_map):
            for decode_index in range(4):
                record = captures[(layer_index, role, decode_index)]
                occurrences.append(
                    {
                        "layer": layer_index,
                        "role": role,
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
        if spec["mode"] == "COVERAGE":
            authority = json.loads((ROOT / "contracts/CENSUS_AUTHORITY.json").read_text())
            accepted = {(row["layer"], row["role"], row["decode_index"]): (row["input_sha256"], row["output_sha256"]) for row in authority["occurrence_bindings"] if row["role"] == "up_proj"}
            for row in occurrences:
                if (row["input_sha256"], row["output_sha256"]) != accepted[(row["layer"], row["role"], row["decode_index"])]:
                    raise RuntimeError(f"coverage occurrence identity drift L{row['layer']} D{row['decode_index']}")
        result = {
            "status": "PASS",
            "condition": args.condition,
            "run_index": args.run_index,
            "mode": spec["mode"],
            "set_name": spec["set_name"],
            "selected_layers": spec["layers"],
            "hit_ratio": spec["hit_ratio"],
            "target_persisting": spec["persisting"],
            "generated_token_ids_D0_D3": token_ids,
            "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in step_events],
            "occurrences": occurrences,
            "module_census": module_census,
            "policy_receipt": policy_receipt,
            "policy_transitions": transitions,
            "policy_transition_count": len(transitions),
            "all_up_proj_instrumented": spec["mode"] == "COVERAGE",
            "no_reset_between_transitions": True,
            "no_inner_loop_synchronize": True,
        }
    finally:
        policy_receipt = helper.end_condition(policy_receipt)
    result["policy_receipt"] = policy_receipt
    expected_updates = 0 if spec["mode"] == "CENSUS" else len(spec["layers"]) * 5
    if result["policy_transition_count"] != expected_updates:
        raise RuntimeError(f"transition count {result['policy_transition_count']} != {expected_updates}")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
