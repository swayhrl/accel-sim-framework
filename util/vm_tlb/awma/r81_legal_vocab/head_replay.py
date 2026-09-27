#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,statistics,time,traceback
from pathlib import Path

import torch
from safetensors import safe_open
from heads import HeadArms

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775/model.safetensors')
ARMS=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT']

def sha_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def load_authority(cohort):
    root=ROOT/'raw/reference'/cohort
    receipt=json.loads((root/'REFERENCE_RECEIPT.json').read_text())
    for name,key in [('hidden_bf16.pt','hidden_tensor_sha256'),
                     ('token_bitmask_int32.pt','mask_tensor_sha256'),
                     ('STEP_LEDGER.json','step_ledger_sha256')]:
        if sha_file(root/name)!=receipt[key]:raise ValueError(f'authority hash mismatch {name}')
    hidden=torch.load(root/'hidden_bf16.pt',weights_only=True,map_location='cpu').to('cuda:0')
    masks=torch.load(root/'token_bitmask_int32.pt',weights_only=True,map_location='cpu')
    ledger=json.loads((root/'STEP_LEDGER.json').read_text())
    req=json.loads((ROOT/'raw/fixture/requests.json').read_text())
    request_ids=[r['request_id'] for r in req if r['cohort']==cohort]
    if len(hidden)!=len(masks)!=len(ledger):raise ValueError('step count mismatch')
    if len(hidden)!=len(ledger):raise ValueError('step count mismatch')
    return hidden,masks,ledger,request_ids,receipt

def load_weight():
    with safe_open(MODEL,framework='pt',device='cpu') as f:
        weight=f.get_tensor('model.embed_tokens.weight').to('cuda:0')
    if tuple(weight.shape)!=(151936,896) or weight.dtype!=torch.bfloat16:
        raise ValueError('weight identity')
    return weight

def divergence_detail(hidden,weight,expected,actual,row):
    if expected is None or actual is None:return {}
    ids=torch.tensor([expected,actual],device='cuda:0',dtype=torch.long)
    scores=torch.nn.functional.linear(hidden[row:row+1],weight[ids]).float()[0].tolist()
    return {'reference_token_score_recomputed':scores[0],
            'candidate_token_score_recomputed':scores[1],
            'pair_margin_reference_minus_candidate':scores[0]-scores[1]}

def eval_once(head,arm,hidden,mask,ledger,ids,record_details):
    details=[];total_ms=0.0
    for step,s in enumerate(ledger):
        active=set(s['active_request_ids'])
        done=[request_id not in active for request_id in ids]
        start=time.perf_counter_ns()
        chosen,scores,metadata=head.select(arm,hidden[step],mask[step],done)
        torch.cuda.synchronize()
        elapsed=(time.perf_counter_ns()-start)/1e6
        total_ms+=elapsed
        for b in range(4):
            if done[b]:continue
            expected=s['selected_token_ids'][b]
            if chosen[b]!=expected:
                d={'cohort':s['cohort'],'arm':arm,'step':step,'request_id':ids[b],
                   'reference_token_id':expected,'candidate_token_id':chosen[b],
                   'reference_selected_score':s['selected_legal_logits'][b],
                   'candidate_selected_score':scores[b],
                   'mask_sha256':s['mask_sha256'],'hidden_sha256':s['hidden_sha256'],
                   'legal_count':s['legal_counts'][b],
                   'implementation_difference':arm,
                   **divergence_detail(hidden[step],head.weight,expected,chosen[b],b)}
                return False,total_ms,d,details
        if record_details:
            details.append({'cohort':s['cohort'],'arm':arm,'step':step,
              'elapsed_head_region_ms':elapsed,'metadata_cpu_ms':metadata['metadata_cpu_ms'],
              'active_rows':metadata['active_rows'],'head_rows':metadata['head_rows'],
              'singleton_rows':metadata['singleton_rows'],'union_count':metadata['union_count'],
              'gather_bytes':metadata['gather_bytes'],'group_count':metadata['group_count']})
    return True,total_ms,None,details

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def run(cohort,phase):
    hidden,masks,ledger,ids,authority=load_authority(cohort)
    weight=load_weight()
    head=HeadArms(weight)
    out=ROOT/'raw/head_replay'/cohort
    out.mkdir(parents=True,exist_ok=True)
    if phase=='canary':
        result={'cohort':cohort,'reference_receipt_sha256':sha_file(ROOT/'raw/reference'/cohort/'REFERENCE_RECEIPT.json'),
                'status':{},'first_divergence':{},'arm_total_canary_ms':{}}
        for arm in ARMS:
            try:
                passed,ms,divergence,_=eval_once(head,arm,hidden,masks,ledger,ids,False)
                result['status'][arm]='QUALIFIED' if passed else 'NUMERICAL_COMPARABILITY_NOT_QUALIFIED'
                result['first_divergence'][arm]=divergence
                result['arm_total_canary_ms'][arm]=ms
            except Exception as exc:
                result['status'][arm]='ENGINEERING_ERROR'
                result['first_divergence'][arm]={'error':repr(exc),'traceback':traceback.format_exc()}
            print(json.dumps({'arm':arm,'status':result['status'][arm],
                              'first_divergence':result['first_divergence'][arm]},sort_keys=True))
        (out/'CANARY_RESULTS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        canary=json.loads((out/'CANARY_RESULTS.json').read_text())
        eligible=[arm for arm in ARMS if canary['status'][arm]=='QUALIFIED']
        if not eligible:raise ValueError('no qualified arm')
        for warmup in range(2):
            for arm in eligible:
                passed,_,divergence,_=eval_once(head,arm,hidden,masks,ledger,ids,False)
                if not passed:raise ValueError(f'warmup divergence {arm}: {divergence}')
        reps=[];steps=[]
        for rep in range(7):
            order=eligible[rep%len(eligible):]+eligible[:rep%len(eligible)]
            for arm in order:
                passed,total,divergence,per_step=eval_once(head,arm,hidden,masks,ledger,ids,True)
                if not passed:raise ValueError(f'formal divergence {arm}: {divergence}')
                reps.append({'cohort':cohort,'arm':arm,'rep':rep,'total_head_region_ms':total,
                             'steps':len(ledger),'selected_sequences_exact':True})
                steps.extend({'rep':rep,**v} for v in per_step)
                print(json.dumps({'cohort':cohort,'arm':arm,'rep':rep,'head_region_ms':total}))
        write_tsv(out/'TIMING_REPETITIONS.tsv',reps)
        write_tsv(out/'TIMING_STEPS.tsv',steps)
        summary={arm:{'median_head_region_ms':statistics.median(r['total_head_region_ms'] for r in reps if r['arm']==arm),
           'values_ms':[r['total_head_region_ms'] for r in reps if r['arm']==arm]} for arm in eligible}
        (out/'TIMING_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print(json.dumps(summary,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--cohort',choices=['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT'],required=True)
    p.add_argument('--phase',choices=['canary','timing'],required=True)
    a=p.parse_args();run(a.cohort,a.phase)
