#!/usr/bin/env python3
"""Isolated A/B/A rotating-window qualification with a true Normal-policy control."""

import argparse
import json
from pathlib import Path

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import PersistenceHelper, qweight_region
from e1_residency_common import AWQ, accepted_text_points, cuda_timed, load_text_input, tensor_sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=("ROTATE_PERSIST_A_B_A", "ROTATE_NORMAL_CONTROL_A_B_A"), required=True)
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--output")
    args = parser.parse_args()
    model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    layer0_up = model.model.model.layers[0].mlp.up_proj
    layer14_up = model.model.model.layers[14].mlp.up_proj
    tensor = load_text_input("up_proj", 1)
    authority = accepted_text_points()[("up_proj", 1, "AWQ_FP16_INPUT")]
    if tensor_sha(tensor) != authority["input_sha"]:
        raise RuntimeError("rotating qualification input identity")
    qweight_bytes = layer0_up.qweight.numel() * layer0_up.qweight.element_size()
    helper = PersistenceHelper()
    rows = []
    persisting = args.condition == "ROTATE_PERSIST_A_B_A"
    for repetition in range(args.repetitions):
        policy = helper.begin_condition(args.condition, qweight_bytes, None, 1.0)
        transitions = []
        try:
            with torch.inference_mode():
                transitions.append(helper.update_access_policy("A_L0_UP_FIRST", layer0_up.qweight, 0.5, persisting))
                output_a0 = layer0_up(tensor)
                output_a1 = layer0_up(tensor)
                transitions.append(helper.update_access_policy("B_L14_UP", layer14_up.qweight, 0.5, persisting))
                output_b0 = layer14_up(tensor)
                output_b1 = layer14_up(tensor)
                transitions.append(helper.update_access_policy("A_L0_UP_RETURN", layer0_up.qweight, 0.5, persisting))
                name = f"C16_E1_ROTATE_{args.condition}_A_RETURN"
                torch.cuda.nvtx.range_push(name)
                output, target_ms = cuda_timed(lambda: layer0_up(tensor))
                torch.cuda.nvtx.range_pop()
                torch.cuda.synchronize()
            output_sha = tensor_sha(output)
            if output_sha != authority["output_sha"]:
                raise RuntimeError("rotating qualification target identity")
        finally:
            policy = helper.end_condition(policy)
        rows.append(
            {
                "condition": args.condition,
                "repetition": repetition,
                "target_ms": target_ms,
                "input_sha256": authority["input_sha"],
                "output_sha256": output_sha,
                "range": name,
                "policy_receipt": policy,
                "window_transitions": transitions,
                "no_reset_between_transitions": True,
                "A_qweight_region": qweight_region(layer0_up, "layer0.mlp.up_proj.qweight"),
                "B_qweight_region": qweight_region(layer14_up, "layer14.mlp.up_proj.qweight"),
            }
        )
    result = {"status": "PASS", "condition": args.condition, "rows": rows}
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
