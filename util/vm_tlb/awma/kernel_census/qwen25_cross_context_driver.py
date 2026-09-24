#!/usr/bin/env python3
"""Frozen-input native workload used only for the Lane F NSYS census."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM

MODEL = Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
REVISION = '7ae557604adf67be50417f59c2c2f167def9a775'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument('--scenario', required=True)
    p.add_argument('--tokens', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--prefill', type=int, required=True)
    p.add_argument('--decode', type=int, required=True)
    p.add_argument('--batch', type=int, required=True)
    p.add_argument('--input-authority', required=True)
    return p.parse_args()


def main() -> None:
    a = parse()
    actual = sha256(a.tokens)
    if actual != a.expected_sha256:
        raise SystemExit(f'token authority mismatch: {actual}')
    ids = json.loads(a.tokens.read_text())
    if not isinstance(ids, list) or len(ids) != a.prefill:
        raise SystemExit('token cardinality mismatch')
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL), local_files_only=True, torch_dtype=torch.float16,
        attn_implementation='sdpa', trust_remote_code=False,
    ).eval().to('cuda:0')
    inputs = torch.tensor([ids] * a.batch, dtype=torch.long, device='cuda')
    with torch.inference_mode():
        torch.cuda.nvtx.range_push(
            f'C16_PHASE=PREFILL;SCENARIO={a.scenario};B={a.batch};T={a.prefill};D={a.decode}'
        )
        out = model(input_ids=inputs, use_cache=True)
        torch.cuda.nvtx.range_pop()
        token = out.logits[:, -1, :].argmax(dim=-1)
        past = out.past_key_values
        generated: list[list[int]] = []
        for step in range(1, a.decode + 1):
            torch.cuda.nvtx.range_push(
                f'C16_PHASE=DECODE;STEP={step};SCENARIO={a.scenario};B={a.batch};T=1'
            )
            generated.append([int(x) for x in token.tolist()])
            out = model(input_ids=token[:, None], past_key_values=past, use_cache=True)
            torch.cuda.nvtx.range_pop()
            past = out.past_key_values
            token = out.logits[:, -1, :].argmax(dim=-1)
    torch.cuda.synchronize()
    print(json.dumps({
        'status': 'AWMA_QWEN25_CROSS_CONTEXT_CENSUS_EXECUTION_COMPLETE',
        'scenario': a.scenario, 'model_id': 'Qwen/Qwen2.5-0.5B-Instruct',
        'revision': REVISION, 'backend': 'sdpa', 'dtype': 'float16',
        'batch': a.batch, 'prefill_tokens': a.prefill, 'decode_tokens': a.decode,
        'token_ids_sha256': actual, 'input_authority': a.input_authority,
        'generated_tokens_per_step': generated,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
