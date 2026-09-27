#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
R53 = Path('/data/c16/awma/r53_online_workset_qualification_20260927')
R54 = Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927')
R1 = Path('/data/c16/awma/r54_fastpath_requal_v1r1_20260927')
MODEL = R54 / 'model/Qwen3_5_0_8B_c6046cd1'

from transformers import AutoTokenizer
import torch

ROOT.mkdir(parents=True, exist_ok=True)
(ROOT/'prefix').mkdir(exist_ok=True)

def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())

def token_sha(ids: list[int]) -> str:
    return sha_bytes(torch.tensor([ids], dtype=torch.long).contiguous().view(torch.uint8).numpy().tobytes())

source=R53/'REQUEST_SELECTION.tsv'
with source.open(newline='') as f:
    source_rows=list(csv.DictReader(f, delimiter='\t'))

order=[('GSM8K','DISCOVERY',range(0,4)),('GSM8K','HOLDOUT',range(4,8)),
       ('HumanEval','DISCOVERY',range(0,4)),('HumanEval','HOLDOUT',range(4,8))]
selected=[]
for domain,cohort,ranks in order:
    for rank in ranks:
        candidates=[r for r in source_rows if r['domain'].lower()==domain.lower()
                    and r['cohort'].upper()==cohort and int(r['selection_rank'])==rank]
        if len(candidates)!=1:
            raise ValueError(f'Need one {domain}/{cohort}/{rank}, got {len(candidates)}')
        row=candidates[0]
        if sha_bytes(row['raw_prompt'].encode()) != row['raw_prompt_sha256']:
            raise ValueError(f'R53 raw prompt hash mismatch for {domain}/{cohort}/{rank}')
        selected.append(row)

sep='\n\n---\n\n'
prompts=[r['raw_prompt'] for r in selected]
tok=AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
stream_text=sep.join(prompts * 12)
stream_ids=tok(stream_text, add_special_tokens=False)['input_ids']
if len(stream_ids)<4608:
    raise ValueError(f'Only {len(stream_ids)} tokens')

r1=json.loads((R1/'R54_V1R1_FASTPATH_RECEIPT.json').read_text())
s0=r1['input_token_ids']
if len(s0)!=64 or token_sha(s0)!=r1['input_token_sha256']:
    raise ValueError('V1R1 S0 input mismatch')

prefixes={'S0':s0,'PREFIX_HOLDOUT_2048':stream_ids[:2048],
          'PREFIX_DISCOVERY_4096':stream_ids[:4096]}
for name,ids in prefixes.items():
    (ROOT/'prefix'/f'{name}.json').write_text(json.dumps(ids, separators=(',',':'))+'\n')

receipt={
    'stage':'AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2',
    'contract':'R54_GREEDY_BACKEND_EQUIVALENCE_V1',
    'accepted_r53_request_selection_path':str(source),
    'accepted_r53_request_selection_sha256':sha_file(source),
    'v1r1_s0_receipt_sha256':sha_file(R1/'R54_V1R1_FASTPATH_RECEIPT.json'),
    'model_revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb',
    'tokenizer_json_sha256':sha_file(MODEL/'tokenizer.json'),
    'tokenizer_config_sha256':sha_file(MODEL/'tokenizer_config.json'),
    'add_special_tokens':False,
    'chat_template_applied':False,
    'separator_repr':repr(sep),
    'prompt_cycle_count':12,
    'raw_prompt_authorities':[{'domain':r['domain'],'cohort':r['cohort'],
       'selection_rank':int(r['selection_rank']),'canonical_id':r['canonical_id'],
       'raw_prompt_sha256':r['raw_prompt_sha256']} for r in selected],
    'combined_text_sha256':sha_bytes(stream_text.encode()),
    'combined_text_token_count':len(stream_ids),
    'prefixes':{name:{'token_count':len(ids),'token_ids_sha256':token_sha(ids),
          'token_json_sha256':sha_file(ROOT/'prefix'/f'{name}.json'),
          'text_authority':'V1R1_S0_CANARY' if name=='S0' else 'R53_RAW_PROMPTS_DETERMINISTIC_CYCLE'}
          for name,ids in prefixes.items()},
    'eos_token_id':tok.eos_token_id,
    'eos_token':tok.eos_token,
}
(ROOT/'R54_V1R2_PREFIX_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2,sort_keys=True))
