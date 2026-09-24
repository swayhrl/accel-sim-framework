#!/usr/bin/env python3
"""Natural full-model operator-family policy experiment with all 84 FFN timings."""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import PersistenceHelper, qweight_region
from e1_residency_common import AWQ


ROOT = Path("/data/c16/e1_operator_family_expansion_v1")
TOKENS = Path("/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json")
TOKEN_FILE_SHA = "0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9"
EXPECTED_TOKENS = [23578, 11, 323, 3950]
ROLES = ("gate_proj", "up_proj", "down_proj")


def tensor_sha(tensor):
    return hashlib.sha256(tensor.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()


def condition_spec(condition, contract):
    if condition == "CENSUS_FFN_CALL_ORDER":
        return {"mode": "CENSUS", "set_name": None, "selected_roles": [], "selected_count": 0, "hit_ratio": 0.0, "persisting": False}
    if condition in ("CONTROL_FULL_GUD84", "FULLHINT_GUD84"):
        roles = contract["condition_sets"]["GUD84"]["selected_roles"]
        return {"mode": "POLICY", "set_name": "GUD84", "selected_roles": roles, "selected_count": 84, "hit_ratio": 1.0, "persisting": condition == "FULLHINT_GUD84"}
    for set_name, entry in contract["condition_sets"].items():
        if condition == entry["control_condition"]:
            return {"mode": "POLICY", "set_name": set_name, "selected_roles": entry["selected_roles"], "selected_count": entry["selected_module_count"], "hit_ratio": entry["hit_ratio"], "persisting": False}
        if condition == entry["fair_condition"]:
            return {"mode": "POLICY", "set_name": set_name, "selected_roles": entry["selected_roles"], "selected_count": entry["selected_module_count"], "hit_ratio": entry["hit_ratio"], "persisting": True}
    raise RuntimeError(f"condition not in frozen matrix: {condition}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", required=True)
    parser.add_argument("--run-index", type=int, default=0)
    parser.add_argument("--output")
    args = parser.parse_args()
    contract = json.loads((ROOT / "contracts/CONDITION_MATRIX_PRECONTRACT.json").read_text())
    spec = condition_spec(args.condition, contract)
    if hashlib.sha256(TOKENS.read_bytes()).hexdigest() != TOKEN_FILE_SHA:
        raise RuntimeError("token authority mismatch")
    prefix = json.loads(TOKENS.read_text())
    wrapper = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    model = wrapper.model.eval()
    layers = model.model.layers
    if len(layers) != 28:
        raise RuntimeError("layer-count mismatch")
    module_map = {}
    module_census = []
    for layer_index, layer in enumerate(layers):
        for role in ROLES:
            module = getattr(layer.mlp, role)
            if not hasattr(module, "qweight"):
                raise RuntimeError(f"unsupported FFN module layer{layer_index}.{role}")
            module_map[(layer_index, role)] = module
            row = {"layer": layer_index, "role": role, "module_class": type(module).__name__, "supported_qweight_family": True}
            row.update(qweight_region(module, f"layer{layer_index}.mlp.{role}.qweight"))
            module_census.append(row)
    helper = PersistenceHelper()
    budget = 0 if spec["mode"] == "CENSUS" else contract["fixed_requested_setaside_bytes"]
    policy_receipt = helper.begin_condition(args.condition, budget, None, 1.0)
    if spec["mode"] == "POLICY":
        if policy_receipt["actual_setaside_bytes"] != contract["expected_actual_setaside_bytes"]:
            raise RuntimeError("runtime actual setaside mismatch")
    active_decode = {"value": None}
    phase = {"value": "PREFILL"}
    phase_ordinal = {"value": 0}
    call_order = []
    transitions = []
    pending = {}
    captures = {}
    handles = []

    def make_pre(layer_index, role):
        def hook(module, module_args):
            ordinal = phase_ordinal["value"]
            phase_ordinal["value"] += 1
            call_order.append({"phase": phase["value"], "ordinal": ordinal, "layer": layer_index, "role": role})
            if spec["mode"] == "POLICY" and role in spec["selected_roles"]:
                transition = helper.update_access_policy(f"{phase['value']}:{ordinal}:L{layer_index}:{role}", module.qweight, spec["hit_ratio"], spec["persisting"])
                transition.update({"phase": phase["value"], "ordinal": ordinal, "layer": layer_index, "role": role, "before_target_event": True})
                transitions.append(transition)
            decode_index = active_decode["value"]
            if decode_index is None:
                return
            key = (layer_index, role, decode_index)
            start = torch.cuda.Event(enable_timing=True)
            stop = torch.cuda.Event(enable_timing=True)
            name = f"C16_E1_OPF_{args.condition}_L{layer_index}_{role.upper()}_D{decode_index}"
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
    token_tensors = []
    step_events = []
    try:
        ids = torch.tensor([prefix], dtype=torch.long, device="cuda")
        with torch.inference_mode():
            phase["value"] = "PREFILL"
            phase_ordinal["value"] = 0
            prefill = model(input_ids=ids, use_cache=True)
            current = torch.argmax(prefill.logits[:, -1, :], dim=-1, keepdim=True)
            past = prefill.past_key_values
            del prefill
            for decode_index in range(4):
                token_tensors.append(current.detach())
                active_decode["value"] = decode_index
                phase["value"] = f"D{decode_index}"
                phase_ordinal["value"] = 0
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
        if pending or len(captures) != 336 or len(call_order) != 420:
            raise RuntimeError(f"call/occurrence closure calls={len(call_order)} captures={len(captures)}")
        token_ids = [int(token.item()) for token in token_tensors]
        if token_ids != EXPECTED_TOKENS:
            raise RuntimeError(f"token drift {token_ids}")
        occurrences = []
        for layer_index, role in sorted(module_map):
            for decode_index in range(4):
                record = captures[(layer_index, role, decode_index)]
                occurrences.append({"layer": layer_index, "role": role, "decode_index": decode_index, "token_id": token_ids[decode_index], "range": record["range"], "input_sha256": tensor_sha(record["input"]), "output_sha256": tensor_sha(record["output"]), "input_shape": list(record["input"].shape), "output_shape": list(record["output"].shape), "module_class": record["module_class"], "target_ms": float(record["start"].elapsed_time(record["stop"]))})
        if spec["mode"] == "POLICY":
            authority = json.loads((ROOT / "contracts/CALL_ORDER_AUTHORITY.json").read_text())
            if call_order != authority["call_order"]:
                raise RuntimeError("natural FFN call order drift")
            accepted = {(row["layer"], row["role"], row["decode_index"]): (row["input_sha256"], row["output_sha256"]) for row in authority["occurrence_bindings"]}
            for row in occurrences:
                if (row["input_sha256"], row["output_sha256"]) != accepted[(row["layer"], row["role"], row["decode_index"])]:
                    raise RuntimeError(f"occurrence identity drift L{row['layer']} {row['role']} D{row['decode_index']}")
        result = {"status": "PASS", "condition": args.condition, "run_index": args.run_index, "mode": spec["mode"], "set_name": spec["set_name"], "selected_roles": spec["selected_roles"], "selected_module_count": spec["selected_count"], "hit_ratio": spec["hit_ratio"], "target_persisting": spec["persisting"], "generated_token_ids_D0_D3": token_ids, "decode_step_ms": [float(start.elapsed_time(stop)) for start, stop in step_events], "occurrences": occurrences, "module_census": module_census, "call_order": call_order, "policy_receipt": policy_receipt, "policy_transitions": transitions, "policy_transition_count": len(transitions), "all_84_ffn_instrumented": True, "no_reset_between_transitions": True, "no_inner_loop_synchronize": True}
    finally:
        policy_receipt = helper.end_condition(policy_receipt)
    result["policy_receipt"] = policy_receipt
    expected_updates = 0 if spec["mode"] == "CENSUS" else spec["selected_count"] * 5
    if result["policy_transition_count"] != expected_updates:
        raise RuntimeError(f"transition count {result['policy_transition_count']} != {expected_updates}")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
