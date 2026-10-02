#!/usr/bin/env python3
"""Freeze source-derived Qwen BF16 V2 hook order before any observer run."""

import argparse
import csv
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads(args.model_config.read_text(encoding="utf-8"))
    assert config["architectures"] == ["Qwen2ForCausalLM"]
    assert config["num_hidden_layers"] == 36
    assert config["hidden_size"] == 2048
    assert config["intermediate_size"] == 11008
    assert config["hidden_act"] == "silu"
    fields = ["point_id", "ordinal", "forward_index", "generated_step", "forward_phase", "layer", "module_role", "module_name", "expected_input_shape", "expected_output_shape"]
    roles = ["self_attn", "gate_up_proj", "act_fn", "down_proj"]
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for point, batch in (("MP02", 1), ("MP03", 4)):
            for forward_index in range(32):
                tokens = batch * (512 if forward_index == 0 else 1)
                phase = "PREFILL_PRODUCES_D0" if forward_index == 0 else "DECODE_PRODUCES_D%d" % forward_index
                for layer in range(36):
                    for role_index, role in enumerate(roles):
                        ordinal = forward_index * 144 + layer * 4 + role_index
                        prefix = f"model.layers.{layer}"
                        module_name = f"{prefix}.self_attn" if role == "self_attn" else f"{prefix}.mlp.{role}"
                        if role == "self_attn":
                            input_shape, output_shape = None, [tokens, 2048]
                        elif role == "gate_up_proj":
                            input_shape, output_shape = [tokens, 2048], [tokens, 22016]
                        elif role == "act_fn":
                            input_shape, output_shape = [tokens, 22016], [tokens, 11008]
                        else:
                            input_shape, output_shape = [tokens, 11008], [tokens, 2048]
                        writer.writerow({
                            "point_id": point,
                            "ordinal": ordinal,
                            "forward_index": forward_index,
                            "generated_step": f"D{forward_index}",
                            "forward_phase": phase,
                            "layer": layer,
                            "module_role": role,
                            "module_name": module_name,
                            "expected_input_shape": json.dumps(input_shape, separators=(",", ":")),
                            "expected_output_shape": json.dumps(output_shape, separators=(",", ":")),
                        })


if __name__ == "__main__":
    main()
