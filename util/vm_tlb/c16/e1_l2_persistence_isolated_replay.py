#!/usr/bin/env python3
"""Single isolated semantic replay under baseline or exact-qweight persistence."""

import argparse
import json

import torch
from awq import AutoAWQForCausalLM

from e1_cuda_persistence import PersistenceHelper, qweight_region
from e1_residency_common import AWQ, PRESSURE_ELEMENTS, accepted_text_points, load_text_input, pressure_touch, tensor_sha, warm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--condition", choices=("ISO_BASELINE_DENSE", "ISO_QWEIGHT_PERSIST_DENSE"), required=True)
    args = parser.parse_args()
    pressure = torch.ones(PRESSURE_ELEMENTS, dtype=torch.float32, device="cuda")
    torch.cuda.synchronize()
    model = AutoAWQForCausalLM.from_quantized(AWQ, fuse_layers=False)
    module = model.model.model.layers[0].mlp.up_proj
    qweight = module.qweight
    qweight_bytes = qweight.numel() * qweight.element_size()
    tensor = load_text_input("up_proj", 1)
    authority = accepted_text_points()[("up_proj", 1, "AWQ_FP16_INPUT")]
    if tensor_sha(tensor) != authority["input_sha"]:
        raise RuntimeError("isolated input identity")
    persistent = args.condition == "ISO_QWEIGHT_PERSIST_DENSE"
    helper = PersistenceHelper()
    receipt = helper.begin_condition(args.condition, qweight_bytes if persistent else 0, qweight if persistent else None, 1.0)
    name = f"C16_E1_L2P_{args.condition}"
    try:
        with torch.inference_mode():
            warm(module, tensor)
            pressure_ms = pressure_touch(pressure, "DENSE_MEMORY_PRESSURE")
            torch.cuda.nvtx.range_push(name)
            output = module(tensor)
            torch.cuda.synchronize()
            torch.cuda.nvtx.range_pop()
        output_sha = tensor_sha(output)
        if output_sha != authority["output_sha"]:
            raise RuntimeError("isolated output identity")
    finally:
        receipt = helper.end_condition(receipt)
    print(
        json.dumps(
            {
                "status": "PASS",
                "condition": args.condition,
                "range": name,
                "input_sha256": authority["input_sha"],
                "output_sha256": output_sha,
                "module_class": type(module).__name__,
                "pressure_ms": pressure_ms,
                "qweight_region": qweight_region(module, "layer0.mlp.up_proj.qweight"),
                "policy_receipt": receipt,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
