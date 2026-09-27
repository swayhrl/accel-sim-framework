#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
import torch

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
prefixes=['S0','PREFIX_HOLDOUT_2048','PREFIX_DISCOVERY_4096']
summary=[];diagnostics=[]
for prefix in prefixes:
    arms={a:json.loads((ROOT/'raw'/prefix/a/'ARM_RECEIPT.json').read_text()) for a in ['F','H']}
    f,h=arms['F'],arms['H']
    fl=torch.load(ROOT/'raw'/prefix/'F'/'logits_bf16.pt',map_location='cpu',weights_only=True)
    hl=torch.load(ROOT/'raw'/prefix/'H'/'logits_bf16.pt',map_location='cpu',weights_only=True)
    assert tuple(fl.shape)==tuple(hl.shape)==(f['continuation_length'],248320)
    assert f['prefix_len']==h['prefix_len']
    tokens_equal=f['generated_token_ids']==h['generated_token_ids']
    eos_equal=f['eos_position_zero_based']==h['eos_position_zero_based'] and f['stop_reason']==h['stop_reason']
    length_equal=f['continuation_length']==h['continuation_length']
    cache_valid=f['cache_length_progression_valid'] and h['cache_length_progression_valid']
    cache_same=[s['cache_seq_length_before_selection'] for s in f['steps']]==[s['cache_seq_length_before_selection'] for s in h['steps']]
    finite=f['finite'] and h['finite'] and torch.isfinite(fl).all().item() and torch.isfinite(hl).all().item()
    passed=all([tokens_equal,eos_equal,length_equal,cache_valid,cache_same,finite])
    summary.append({'prefix':prefix,'prefix_len':f['prefix_len'],
        'fallback_tokens_sha256':f['generated_token_ids_sha256'],
        'hub_tokens_sha256':h['generated_token_ids_sha256'],
        'generated_token_ids_equal':tokens_equal,'eos_stop_equal':eos_equal,
        'continuation_length_equal':length_equal,'cache_progression_valid':cache_valid,
        'cache_length_equal':cache_same,'finite':finite,'generated_count':f['continuation_length'],
        'eos_position':f['eos_position_zero_based'],'first_divergence_step':next((i for i,(x,y) in enumerate(zip(f['generated_token_ids'],h['generated_token_ids'])) if x!=y),''),
        'greedy_gate_pass':passed})
    for i,(fs,hs) in enumerate(zip(f['steps'],h['steps'])):
        diff=(fl[i].float()-hl[i].float()).abs()
        diagnostics.append({'prefix':prefix,'step':i,
            'selected_token_id_F':fs['selected_token_id'],
            'selected_token_id_H':hs['selected_token_id'],
            'top2_order_F':json.dumps(fs['top2_ids'],separators=(',',':')),
            'top2_order_H':json.dumps(hs['top2_ids'],separators=(',',':')),
            'top2_order_equal':fs['top2_ids']==hs['top2_ids'],
            'top8_order_F':json.dumps(fs['top8_ordered_ids'],separators=(',',':')),
            'top8_order_H':json.dumps(hs['top8_ordered_ids'],separators=(',',':')),
            'top8_order_equal':fs['top8_ordered_ids']==hs['top8_ordered_ids'],
            'top8_set_equal':fs['top8_set_ids']==hs['top8_set_ids'],
            'selected_logit_F':fs['selected_logit'],'selected_logit_H':hs['selected_logit'],
            'second_logit_F':fs['second_logit'],'second_logit_H':hs['second_logit'],
            'margin_F':fs['margin'],'margin_H':hs['margin'],
            'max_abs_logit_difference':float(diff.max()),
            'mean_abs_logit_difference':float(diff.mean()),
            'differing_logits':int(torch.count_nonzero(fl[i]!=hl[i]))})

for name,rows in [('R54_V1R2_GREEDY_RESULTS.tsv',summary),('R54_V1R2_NUMERICAL_DIAGNOSTICS.tsv',diagnostics)]:
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
state='R54_V1R2_GREEDY_BACKEND_QUALIFIED' if all(r['greedy_gate_pass'] for r in summary) else 'R54_V1R2_GREEDY_BACKEND_NOT_QUALIFIED'
decision={'stage':'AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2',
          'contract':'R54_GREEDY_BACKEND_EQUIVALENCE_V1','state':state,
          'all_prefixes_pass':all(r['greedy_gate_pass'] for r in summary),
          'prefix_results':summary,
          'top2_diagnostic_mismatch_count':sum(not r['top2_order_equal'] for r in diagnostics),
          'top8_order_diagnostic_mismatch_count':sum(not r['top8_order_equal'] for r in diagnostics),
          'top8_set_diagnostic_mismatch_count':sum(not r['top8_set_equal'] for r in diagnostics),
          'diagnostic_steps':len(diagnostics),
          'prior_v1':'R54_RUNTIME_FASTPATH_NOT_QUALIFIED_V1',
          'prior_v1r1':'R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED',
          'next_phase':'RESUME_ORIGINAL_R54_MEASUREMENT_CONTRACT' if all(r['greedy_gate_pass'] for r in summary) else 'STOP_AFTER_CLOSURE'}
(ROOT/'R54_V1R2_DECISION.json').write_text(json.dumps(decision,indent=2,sort_keys=True)+'\n')
print(json.dumps({k:decision[k] for k in ['state','top2_diagnostic_mismatch_count','top8_order_diagnostic_mismatch_count','top8_set_diagnostic_mismatch_count','diagnostic_steps']},indent=2))
