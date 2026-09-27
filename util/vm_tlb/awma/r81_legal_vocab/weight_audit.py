#!/usr/bin/env python3
import hashlib,json
from pathlib import Path
import torch
from safetensors import safe_open

root=Path('/data/c16/awma/r81_legal_vocab_20260927')
file=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors')
with safe_open(file,framework='pt',device='cpu') as source:
    names=[n for n in source.keys() if n=='model.embed_tokens.weight']
    if len(names)!=1:raise ValueError(f'Expected exact tied embedding weight, got {names}')
    weight=source.get_tensor(names[0])
    head_sha=hashlib.sha256(weight.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
    fp16_sha=hashlib.sha256(weight.to(torch.float16).contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
data={'file_sha256_expected':'fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe',
      'head_key':names[0],'head_shape':list(weight.shape),'head_dtype':str(weight.dtype),
      'head_is_tied_embedding':True,
      'head_sha256':head_sha,'accepted_head_sha256':'d74257dc547b48be5ae7b93f1c9af072c0c42dbbb85503078e25c59cd09e68d0',
      'fp16_cast_head_sha256':fp16_sha,
      'native_bf16_matches_accepted_fp16_hash':head_sha=='d74257dc547b48be5ae7b93f1c9af072c0c42dbbb85503078e25c59cd09e68d0',
      'fp16_cast_matches_accepted_head':fp16_sha=='d74257dc547b48be5ae7b93f1c9af072c0c42dbbb85503078e25c59cd09e68d0'}
(root/'HEAD_WEIGHT_IDENTITY.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
print(json.dumps(data,sort_keys=True))
if list(weight.shape)!=[151936,896] or not data['fp16_cast_matches_accepted_head']:
    raise SystemExit(2)
