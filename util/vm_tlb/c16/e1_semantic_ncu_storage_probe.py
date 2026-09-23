#!/usr/bin/env python3
"""Freeze the exact packed-storage footprint of the accepted AWQ up_proj."""

import argparse
import json

from awq import AutoAWQForCausalLM


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    model = AutoAWQForCausalLM.from_quantized(args.model, fuse_layers=False)
    module = model.model.model.layers[0].mlp.up_proj
    tensors = []
    total = 0
    for name, tensor in sorted(module.state_dict().items()):
        byte_count = tensor.numel() * tensor.element_size()
        total += byte_count
        tensors.append(
            {
                "name": name,
                "shape": list(tensor.shape),
                "dtype": str(tensor.dtype),
                "element_count": tensor.numel(),
                "element_size_bytes": tensor.element_size(),
                "storage_bytes": byte_count,
            }
        )
    result = {
        "status": "PASS",
        "model_root": args.model,
        "module": "model.layers.0.mlp.up_proj",
        "module_class": type(module).__name__,
        "state_dict_tensors": tensors,
        "packed_weight_storage_bytes": total,
        "definition": "sum(numel * element_size) over exact accepted AWQ up_proj state_dict tensors",
    }
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
