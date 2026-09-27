#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,statistics,time,traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM,AutoTokenizer

from heads import HeadArms
from reference import MODEL,ROOT,VOCAB,load_rows,make_matchers,batch_inputs,fill_masks

ARMS=['A0_DENSE_VENDOR','A1_DENSE_FUSED','A2_INDEXED_UNION','A3_RAGGED_DIRECT']

def token_sha(ids):
    return hashlib.sha256(json.dumps(ids,separators=(',',':'),sort_keys=True).encode()).hexdigest()

@torch.inference_mode()
def generation(model,head,tok,rows,arm,executor):
    matchers=make_matchers(rows)
    input_ids,attention_mask=batch_inputs(rows,tok.pad_token_id,'cuda:0')
    done=[False]*4;stop=[None]*4;generated=[[] for _ in range(4)]
    completion_ms=[None]*4
    cache=None;grammar_ms_total=0.0;head_ms_total=0.0
    wall_start=time.perf_counter_ns()
    for step in range(128):
        mask=torch.empty((4,(VOCAB+31)//32),dtype=torch.int32)
        future=executor.submit(fill_masks,matchers,list(done),mask)
        out=model.model(input_ids=input_ids,attention_mask=attention_mask,
                        past_key_values=cache,use_cache=True,return_dict=True)
        cache=out.past_key_values
        hidden=out.last_hidden_state[:,-1,:].contiguous()
        legal_ids,grammar_ms=future.result()
        grammar_ms_total+=grammar_ms
        head_start=time.perf_counter_ns()
        selected,scores,metadata=head.select(arm,hidden,mask,done)
        torch.cuda.synchronize()
        head_ms_total+=(time.perf_counter_ns()-head_start)/1e6
        next_ids=[];next_attention=[]
        for i in range(4):
            if done[i]:
                next_ids.append(tok.pad_token_id);next_attention.append(0);continue
            token=selected[i]
            if token is None or token not in legal_ids[i]:raise ValueError(f'{arm}: illegal/null winner request {i} step {step}')
            if not matchers[i].accept_token(token):raise ValueError(f'{arm}: matcher rejected winner request {i} step {step}')
            generated[i].append(token)
            if token==tok.eos_token_id or matchers[i].is_terminated():
                done[i]=True
                stop[i]='EOS' if token==tok.eos_token_id else 'GRAMMAR_TERMINATED'
                completion_ms[i]=(time.perf_counter_ns()-wall_start)/1e6
            next_ids.append(token if not done[i] else tok.pad_token_id)
            next_attention.append(0 if done[i] else 1)
        if all(done):break
        input_ids=torch.tensor(next_ids,dtype=torch.long,device='cuda:0').view(4,1)
        attention_mask=torch.cat([attention_mask,torch.tensor(next_attention,dtype=torch.long,device='cuda:0').view(4,1)],dim=1)
    torch.cuda.synchronize()
    wall_ms=(time.perf_counter_ns()-wall_start)/1e6
    for i in range(4):
        if not done[i]:
            stop[i]='MAX_128_TRUNCATED';completion_ms[i]=wall_ms
    return {'arm':arm,'wall_ms':wall_ms,'grammar_fill_ms_sum_diagnostic':grammar_ms_total,
      'head_region_ms_sum_diagnostic':head_ms_total,
      'generated_token_ids':generated,'generated_token_ids_sha256':[token_sha(v) for v in generated],
      'generated_counts':[len(v) for v in generated],
      'stop_reasons':stop,'request_completion_ms':completion_ms,
      'valid_token_count':sum(len(v) for v in generated),
      'all_json_parseable':all_json_parseable(tok,generated,stop),
      'cache_policy':'fresh dynamic cache per B4 run; left-padded prompt; stopped rows masked with pad',
      'mask_backbone_overlap':'CPU matcher.fill_next_token_bitmask submitted concurrently with GPU backbone forward'}

def all_json_parseable(tok,generated,stop):
    for ids,status in zip(generated,stop):
        if status=='MAX_128_TRUNCATED':return False
        try:json.loads(tok.decode(ids,skip_special_tokens=True))
        except Exception:return False
    return True

def compare_to_reference(cohort,result):
    source=json.loads((ROOT/'raw/reference'/cohort/'REQUEST_RESULTS.json').read_text())
    for i,r in enumerate(source):
        expected=r['generated_token_ids'];actual=result['generated_token_ids'][i]
        if expected!=actual:
            k=next((j for j,(x,y) in enumerate(zip(expected,actual)) if x!=y),min(len(expected),len(actual)))
            return False,{'request_id':r['request_id'],'first_divergence_step':k,
              'expected_token':expected[k] if k<len(expected) else None,
              'actual_token':actual[k] if k<len(actual) else None}
        if r['stop_reason']!=result['stop_reasons'][i]:
            return False,{'request_id':r['request_id'],'stop_reason_expected':r['stop_reason'],
                          'stop_reason_actual':result['stop_reasons'][i]}
    return True,None

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def run(cohort):
    rows=load_rows(cohort)
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,
      torch_dtype=torch.bfloat16,attn_implementation='sdpa').eval().to('cuda:0')
    head=HeadArms(model.get_output_embeddings().weight)
    out=ROOT/'raw/full_generation'/cohort
    out.mkdir(parents=True,exist_ok=True)
    head_canary=json.loads((ROOT/'raw/head_replay'/cohort/'CANARY_RESULTS.json').read_text())
    eligible=[a for a in ARMS if head_canary['status'][a]=='QUALIFIED']
    with ThreadPoolExecutor(max_workers=1) as executor:
        canaries={}
        for arm in eligible:
            try:
                result=generation(model,head,tok,rows,arm,executor)
                passed,divergence=compare_to_reference(cohort,result)
                result['semantic_exact']=passed
                result['first_divergence']=divergence
                canaries[arm]=result
            except Exception as exc:
                canaries[arm]={'arm':arm,'semantic_exact':False,'error':repr(exc),'traceback':traceback.format_exc()}
            print(json.dumps({'cohort':cohort,'arm':arm,'semantic_exact':canaries[arm]['semantic_exact'],
                              'first_divergence':canaries[arm].get('first_divergence')},sort_keys=True))
        (out/'CANARY_RESULTS.json').write_text(json.dumps(canaries,indent=2,sort_keys=True)+'\n')
        qualified=[a for a in eligible if canaries[a]['semantic_exact']]
        if not qualified:return
        for warmup in range(2):
            for arm in qualified:
                result=generation(model,head,tok,rows,arm,executor)
                passed,divergence=compare_to_reference(cohort,result)
                if not passed:raise ValueError(f'warmup divergence {arm}: {divergence}')
        formal=[];raw=[]
        for rep in range(7):
            order=qualified[rep%len(qualified):]+qualified[:rep%len(qualified)]
            for arm in order:
                result=generation(model,head,tok,rows,arm,executor)
                passed,divergence=compare_to_reference(cohort,result)
                if not passed:raise ValueError(f'formal divergence {arm}: {divergence}')
                formal.append({'cohort':cohort,'arm':arm,'rep':rep,'wall_ms':result['wall_ms'],
                  'valid_token_count':result['valid_token_count'],
                  'generated_counts':json.dumps(result['generated_counts'],separators=(',',':')),
                  'stop_reasons':json.dumps(result['stop_reasons'],separators=(',',':')),
                  'request_completion_ms':json.dumps(result['request_completion_ms'],separators=(',',':')),
                  'head_region_ms_sum_diagnostic':result['head_region_ms_sum_diagnostic'],
                  'grammar_fill_ms_sum_diagnostic':result['grammar_fill_ms_sum_diagnostic'],
                  'semantic_exact':True,'all_json_parseable':result['all_json_parseable']})
                raw.append({'rep':rep,**result})
                print(json.dumps({'cohort':cohort,'arm':arm,'rep':rep,'wall_ms':result['wall_ms'],
                                  'valid_token_count':result['valid_token_count']}))
        write_tsv(out/'TIMING_RESULTS.tsv',formal)
        (out/'FORMAL_RUNS.json').write_text(json.dumps(raw,indent=2,sort_keys=True)+'\n')
        summary={a:{'median_wall_ms':statistics.median(r['wall_ms'] for r in formal if r['arm']==a),
           'wall_ms':[r['wall_ms'] for r in formal if r['arm']==a]} for a in qualified}
        (out/'TIMING_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'cohort':cohort,'summary':summary},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--cohort',choices=['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT'],required=True)
    run(p.parse_args().cohort)
