#!/usr/bin/env python3
"""Explicit deployment adapters; no model-family name is a runtime identity."""
from __future__ import annotations

from dataclasses import dataclass

from c16_native_common import ContractError


@dataclass(frozen=True)
class Adapter:
    name: str
    model_loader: str
    required_quantization: str
    allowed_dtypes: tuple[str, ...]


ADAPTERS = {
    "llama32_1b": Adapter("llama32_1b", "TRANSFORMERS_CAUSAL_LM", "NONE", ("float16", "bfloat16")),
    "qwen25_05b": Adapter("qwen25_05b", "TRANSFORMERS_CAUSAL_LM", "NONE", ("float16", "bfloat16")),
    "qwen25_7b_raw": Adapter("qwen25_7b_raw", "TRANSFORMERS_CAUSAL_LM", "NONE", ("float16", "bfloat16")),
    "qwen25_7b_awq": Adapter("qwen25_7b_awq", "AUTOAWQ_CAUSAL_LM", "AWQ", ("float16",)),
}


def resolve_adapter(name: str, dtype: str, quantization: str) -> Adapter:
    if name not in ADAPTERS:
        raise ContractError(f"unknown C16 Wave-1 adapter: {name}")
    adapter = ADAPTERS[name]
    if dtype not in adapter.allowed_dtypes:
        raise ContractError(f"adapter {name} does not allow dtype {dtype}")
    if quantization != adapter.required_quantization:
        raise ContractError(f"adapter {name} requires quantization {adapter.required_quantization}, got {quantization}")
    return adapter
