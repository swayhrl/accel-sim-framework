#!/usr/bin/env python3
import csv,hashlib,json
from pathlib import Path
import torch
from transformers import AutoTokenizer

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
R53=Path('/data/c16/awma/r53_online_workset_qualification_20260927')
MODEL=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927/model/Qwen3_5_0_8B_c6046cd1')

def tok_sha(ids):
    return hashlib.sha256(torch.tensor([ids],dtype=torch.long).view(torch.uint8).numpy().tobytes()).hexdigest()

with (R53/'REQUEST_SELECTION.tsv').open(newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
order=[('GSM8K','DISCOVERY',range(4)),('GSM8K','HOLDOUT',range(4,8)),
       ('HumanEval','DISCOVERY',range(4)),('HumanEval','HOLDOUT',range(4,8))]
selected=[]
for domain,cohort,ranks in order:
    for rank in ranks:
        x=[r for r in rows if r['domain'].lower()==domain.lower() and r['cohort']==cohort and int(r['selection_rank'])==rank]
        assert len(x)==1
        selected.append(x[0]['raw_prompt'])
sep='\n\n---\n\n'
tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True)
text=sep.join(selected*12)
ids=tok(text,add_special_tokens=False)['input_ids']
rotated=selected[5:]+selected[:5]
rotated_text=sep.join(rotated*12)
rotated_ids=tok(rotated_text,add_special_tokens=False)['input_ids']
parts={'PREFIX_DISCOVERY_4096':ids[:4096],
       'PREFIX_HOLDOUT_2048':ids[:2048],
       'SUFFIX_A_512':ids[4096:4608],
       'SUFFIX_B_512':rotated_ids[:512],
       'HOLDOUT_SUFFIX_256':ids[2048:2304]}
for name,values in parts.items():
    assert len(values)==int(name.rsplit('_',1)[1])
    (ROOT/'prefix'/f'{name}.json').write_text(json.dumps(values,separators=(',',':'))+'\n')
previous=json.loads((ROOT/'R54_V1R2_PREFIX_RECEIPT.json').read_text())
for name in ('PREFIX_DISCOVERY_4096','PREFIX_HOLDOUT_2048'):
    assert tok_sha(parts[name])==previous['prefixes'][name]['token_ids_sha256']
receipt={'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2',
    'source':'R53_REQUEST_SELECTION_TSV_RAW_PROMPTS',
    'source_sha256':previous['accepted_r53_request_selection_sha256'],
    'model_revision':previous['model_revision'],
    'tokenizer_json_sha256':previous['tokenizer_json_sha256'],
    'separator_repr':repr(sep),'prompt_cycle_count':12,
    'combined_text_sha256':hashlib.sha256(text.encode()).hexdigest(),
    'rotated_text_sha256':hashlib.sha256(rotated_text.encode()).hexdigest(),
    'parts':{name:{'token_count':len(v),'token_ids_sha256':tok_sha(v),
                   'json_sha256':hashlib.sha256((ROOT/'prefix'/f'{name}.json').read_bytes()).hexdigest()}
             for name,v in parts.items()}}
(ROOT/'FULL_R54_FIXTURE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt['parts'],indent=2))
