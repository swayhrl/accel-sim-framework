#!/usr/bin/env python3
"""CPU-only tokenizer/template probe; no model loading or generated text."""

import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from transformers import AutoTokenizer  # noqa: E402


MODEL = "/data/c16/aiarch_hybrid_asset_qualification_20261110_v1/models/qwen3_5_4b"


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True, trust_remote_code=False)
    messages = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hello"},
        {"role": "user", "content": "continue"},
    ]
    ids = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True)
    import torch

    if hasattr(ids, "keys"):
        token_count = len(ids["input_ids"])
        output_type = f"{type(ids).__name__}:{sorted(ids)}"
    else:
        token_count = len(ids)
        output_type = type(ids).__name__
    print({"tokenizer_class": type(tokenizer).__name__, "vocab_size": len(tokenizer),
           "template_output": output_type, "template_probe_tokens": token_count,
           "cuda_initialized": torch.cuda.is_initialized()})
    if torch.cuda.is_initialized():
        raise RuntimeError("CUDA was initialized")


if __name__ == "__main__":
    main()
