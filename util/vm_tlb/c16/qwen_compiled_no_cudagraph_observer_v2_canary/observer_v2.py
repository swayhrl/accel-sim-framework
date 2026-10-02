#!/usr/bin/env python3
"""Exact semantic Observer V2 extraction from commit f63d39c8d90ced038445c264fa8242c524a1aa6f."""
import hashlib
import json
import torch

SOURCE_COMMIT = "f63d39c8d90ced038445c264fa8242c524a1aa6f"
SOURCE_SHA256 = "7f2a76a375eaa4f652553fc523f785a753180ef1402291e54beb2256ed02bb22"

def sha_json(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def select_semantic_modules(model, target):
    selected = []
    for name, module in model.named_modules():
        if name.endswith(".self_attn"):
            selected.append((name, module))
        elif target.startswith("QWEN") and name.endswith((".mlp.gate_up_proj", ".mlp.act_fn", ".mlp.down_proj")):
            selected.append((name, module))
        elif target == "OLMOE" and name.endswith((".mlp.gate", ".mlp.experts")):
            selected.append((name, module))
    return selected


class HookSession:
    def __init__(self, modules, collect):
        self.modules = modules
        self.collect = collect
        self.handles = []
        self.pending = {}
        self.ranges = []
        self.order = []
        self.ordinal = 0

    def install(self):
        for name, module in self.modules:
            self.handles.append(module.register_forward_pre_hook(self.make_pre(name)))
            self.handles.append(module.register_forward_hook(self.make_post(name)))
        return self

    def make_pre(self, name):
        def hook(module, args):
            ordinal = self.ordinal; self.ordinal += 1
            label = f"C16_STAGEA_{ordinal}_{name}"
            input_shape = list(args[0].shape) if args and isinstance(args[0], torch.Tensor) else None
            torch.cuda.nvtx.range_push(label)
            self.pending[id(module)] = (ordinal, name, label, input_shape)
        return hook

    def make_post(self, name):
        def hook(module, args, output):
            ordinal, module_name, label, input_shape = self.pending.pop(id(module))
            torch.cuda.nvtx.range_pop()
            value = output[0] if isinstance(output, (tuple, list)) and output and isinstance(output[0], torch.Tensor) else output
            output_shape = list(value.shape) if isinstance(value, torch.Tensor) else None
            if self.collect:
                self.order.append({"ordinal": ordinal, "module": module_name,
                                   "input_shape": input_shape, "output_shape": output_shape})
                self.ranges.append({"ordinal": ordinal, "module": module_name, "label": label,
                                    "input_shape": input_shape, "output_shape": output_shape})
        return hook

    def remove(self):
        for handle in self.handles:
            handle.remove()
        if self.pending:
            raise RuntimeError(f"unclosed semantic hooks: {len(self.pending)}")

    def receipt(self):
        return {"semantic_order": self.order,
                "semantic_order_sha256": sha_json(self.order),
                "semantic_ranges": self.ranges,
                "semantic_ranges_sha256": sha_json(self.ranges)}
