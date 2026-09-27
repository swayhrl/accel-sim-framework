#!/usr/bin/env python3
import hashlib,json,math
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from safetensors import safe_open
from test_masks import unpack_mask

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors')
COHORTS=['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT']
with safe_open(MODEL,framework='pt',device='cpu') as source:
    weight=source.get_tensor('model.embed_tokens.weight').to('cuda:0')
report={}
with torch.inference_mode():
    for cohort in COHORTS:
        root=ROOT/'raw/reference'/cohort
        hidden=torch.load(root/'hidden_bf16.pt',map_location='cpu',weights_only=True).to('cuda:0')
        masks=torch.load(root/'token_bitmask_int32.pt',map_location='cpu',weights_only=True)
        ledger=json.loads((root/'STEP_LEDGER.json').read_text())
        req=[r for r in json.loads((ROOT/'raw/fixture/requests.json').read_text()) if r['cohort']==cohort]
        checked=0;nontrivial=0;minimum_margin=math.inf
        for step,s in enumerate(ledger):
            legal_bool=unpack_mask(masks[step],151936)
            active=[i for i in range(4) if req[i]['request_id'] in s['active_request_ids']]
            logits=F.linear(hidden[step,active],weight)
            legal_gpu=torch.from_numpy(legal_bool[active]).to('cuda:0')
            if not bool((torch.isfinite(logits)|~legal_gpu).all()):
                raise ValueError(f'nonfinite legal logit {cohort} step {step}')
            logits.masked_fill_(~legal_gpu,float('-inf'))
            winners=logits.argmax(dim=1).tolist()
            for row,i in enumerate(active):
                if winners[row]!=s['selected_token_ids'][i]:
                    raise ValueError(f'dense argmax mismatch {cohort} step {step} row {i}')
                checked+=1
                if s['legal_counts'][i]>1:
                    top=torch.topk(logits[row],2).values.float()
                    margin=float(top[0]-top[1])
                    minimum_margin=min(minimum_margin,margin)
                    nontrivial+=1
        report[cohort]={'status':'PASS','steps':len(ledger),'active_row_steps_checked':checked,
          'nontrivial_row_steps':nontrivial,
          'all_legal_dense_logits_finite':True,
          'masked_argmax_matches_frozen_reference':True,
          'minimum_reference_top1_minus_top2_margin':minimum_margin if nontrivial else None,
          'tie_rule':'ascending token ID via dense argmax first occurrence'}
(ROOT/'LEGAL_LOGIT_VALIDATION.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report,sort_keys=True))
