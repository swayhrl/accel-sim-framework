#!/usr/bin/env python3
"""Exact Q05 S2 driver with NVTX labels for lightweight NSYS kernel census only."""
import hashlib
import json
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM

MODEL = Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
TOKENS = Path('/data/c16/inputs/.incoming/qwen2p5_0p5b_instruct/S2_TEXT/payload/TEXT_S2_T2048_token_ids.json')
EXPECTED = '0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha(TOKENS) != EXPECTED:
        raise SystemExit('frozen token authority mismatch')
    ids = json.loads(TOKENS.read_text())
    if not isinstance(ids, list) or len(ids) != 2048:
        raise SystemExit('S2 exact token cardinality mismatch')
    torch.manual_seed(0)
    model = AutoModelForCausalLM.from_pretrained(
        str(MODEL), local_files_only=True, torch_dtype=torch.float16,
        attn_implementation='sdpa', trust_remote_code=False,
    ).eval().to('cuda:0')
    with torch.inference_mode():
        torch.cuda.nvtx.range_push('C16_PHASE=PREFILL;SCENARIO=S2_TEXT;B=1;T=2048;D=32')
        out = model(input_ids=torch.tensor([ids], dtype=torch.long, device='cuda'), use_cache=True)
        torch.cuda.nvtx.range_pop()
        token = int(out.logits[:, -1, :].argmax(dim=-1).item())
        past = out.past_key_values
        generated = []
        for step in range(1, 33):
            torch.cuda.nvtx.range_push(f'C16_PHASE=DECODE;STEP={step};SCENARIO=S2_TEXT;B=1;T=1')
            generated.append(token)
            out = model(input_ids=torch.tensor([[token]], dtype=torch.long, device='cuda'), past_key_values=past, use_cache=True)
            torch.cuda.nvtx.range_pop()
            past = out.past_key_values
            token = int(out.logits[:, -1, :].argmax(dim=-1).item())
    torch.cuda.synchronize()
    print(json.dumps({
        'status': 'EXACT_Q05_S2_KERNEL_CENSUS_EXECUTION_COMPLETE',
        'model_id': 'Qwen/Qwen2.5-0.5B-Instruct',
        'revision': '7ae557604adf67be50417f59c2c2f167def9a775',
        'backend': 'sdpa', 'dtype': 'float16', 'prefill_tokens': 2048,
        'decode_tokens': 32, 'token_ids_sha256': sha(TOKENS),
        'generated_tokens': generated,
    }, sort_keys=True))


if __name__ == '__main__':
    main()
