#!/usr/bin/env python3
"""CPU-only independent audit of frozen OLMoE Graph OFF/ON canary outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter,defaultdict
from pathlib import Path


EXPECTED_OFF_SHA='97f24bed45b544353a477872da68af2cdc058d41cd88487f00dff619befad201'
EXPECTED_ON_SHA='c2c2cff5ec04929e752329c987b1655e83d4f3d61556f89360b41225a87a0456'
EXPECTED_SCALARS=4761
ATOL=0.05
RTOL=0.01
PROMPT_TOKENS=512
GENERATED_TOKENS=32
LAYERS=16
TOPK=8


def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''):
            h.update(chunk)
    return h.hexdigest()


def tsv(path: Path,rows: list[dict]) -> None:
    if not rows:raise AssertionError('empty '+str(path))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)


def write_json(path: Path,value: dict) -> None:
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n',encoding='utf-8')


def classify_event(left: list[int],right: list[int]) -> tuple[str,int,int,int,float]:
    if len(left)!=len(right):return 'STRUCTURE_SHIFT',0,0,0,0.0
    mismatches=sum(a!=b for a,b in zip(left,right))
    a,b=set(left),set(right)
    intersection=len(a&b);union=len(a|b)
    jaccard=intersection/union if union else 1.0
    if not mismatches:return 'EXACT_MATCH',0,intersection,union,jaccard
    if a==b:return 'ORDER_ONLY_SWAP',mismatches,intersection,union,jaccard
    return 'EXPERT_SET_SUBSTITUTION',mismatches,intersection,union,jaccard


def step_for_position(position: int) -> tuple[int,str]:
    if position<PROMPT_TOKENS:return 0,'PROMPT_FORWARD_TO_D0'
    return position-PROMPT_TOKENS+1,'DECODE_FORWARD_TO_D'+str(position-PROMPT_TOKENS+1)


def sampled_logprob(row: list[dict],token: int) -> float:
    matches=[x['logprob'] for x in row if x['token_id']==token]
    if len(matches)!=1:raise AssertionError('sampled-token logprob missing/duplicated')
    return float(matches[0])


def analyze(off: dict,on: dict) -> tuple[dict,list[dict],list[dict],list[dict]]:
    if off['status']!='PASS' or on['status']!='PASS':raise AssertionError('raw canary arm failed')
    off_runs=[row for row in off['native_runs'] if row['arm']=='OFF']
    if not off_runs or not on['native_runs'] or on['native_runs'][0]['arm']!='GRAPH_ON':
        raise AssertionError('missing selected native arm')
    left=off_runs[0]['output'];right=on['native_runs'][0]['output']
    routes_a=left['routed_experts'];routes_b=right['routed_experts']
    if routes_a is None or routes_b is None:raise AssertionError('missing routed experts')
    shape_a=(len(routes_a),tuple(sorted(set(len(x) for x in routes_a))),
             tuple(sorted(set(len(layer) for x in routes_a for layer in x))))
    shape_b=(len(routes_b),tuple(sorted(set(len(x) for x in routes_b))),
             tuple(sorted(set(len(layer) for x in routes_b for layer in x))))
    shape_equal=shape_a==shape_b
    if shape_a!=(PROMPT_TOKENS+GENERATED_TOKENS-1,(LAYERS,),(TOPK,)) or not shape_equal:
        raise AssertionError(f'unexpected or shifted raw structure {shape_a} {shape_b}')
    tokens_a=left['tokens'];tokens_b=right['tokens']
    if len(tokens_a)!=GENERATED_TOKENS or len(tokens_b)!=GENERATED_TOKENS:
        raise AssertionError('not 32 generated tokens')
    event_rows=[];by_step=defaultdict(lambda:Counter());first={};first_class={};scalar=0;duplicates=Counter()
    scalar_by_class=Counter();substitution_jaccards=[];intersection_histogram=Counter()
    for pos,(layers_a,layers_b) in enumerate(zip(routes_a,routes_b)):
        step,scope=step_for_position(pos)
        for layer,(ids_a,ids_b) in enumerate(zip(layers_a,layers_b)):
            if any(not isinstance(x,int) or not 0<=x<64 for x in ids_a+ids_b):
                raise AssertionError('non-integer or out-of-range expert ID')
            category,count,inter,union,jaccard=classify_event(ids_a,ids_b)
            if category!='EXACT_MATCH' and category not in first_class:
                first_class[category]=(pos,layer,next((i for i,(a,b) in enumerate(zip(ids_a,ids_b)) if a!=b),-1))
            duplicates['off']+=len(set(ids_a))!=len(ids_a)
            duplicates['on']+=len(set(ids_b))!=len(ids_b)
            scalar+=count
            scalar_by_class[category]+=count
            if category=='EXPERT_SET_SUBSTITUTION':
                substitution_jaccards.append(jaccard)
                intersection_histogram[inter]+=1
            c=by_step[step];c['events']+=1;c[category]+=1;c['positional_mismatches']+=count
            if category!='EXACT_MATCH':
                c['affected_events']+=1
                c[f'layer_{layer}']+=1
                if step not in first:
                    first[step]=(pos,layer,next((i for i,(a,b) in enumerate(zip(ids_a,ids_b)) if a!=b),-1))
            event_rows.append(dict(route_position=pos,decode_output_step=f'D{step}',route_scope=scope,
                                   layer_index=layer,off_ordered_ids=','.join(map(str,ids_a)),
                                   on_ordered_ids=','.join(map(str,ids_b)),
                                   off_unordered_set=','.join(map(str,sorted(set(ids_a)))),
                                   on_unordered_set=','.join(map(str,sorted(set(ids_b)))),
                                   ordered_equal=str(ids_a==ids_b).lower(),set_equal=str(set(ids_a)==set(ids_b)).lower(),
                                   intersection_size=inter,union_size=union,jaccard=f'{jaccard:.12g}',
                                   positional_mismatch_count=count,event_class=category))
    if scalar!=EXPECTED_SCALARS:raise AssertionError(f'producer scalar mismatch {scalar}')
    step_rows=[]
    for step in range(GENERATED_TOKENS):
        c=by_step[step]
        expected_events=(PROMPT_TOKENS if step==0 else 1)*LAYERS
        if c['events']!=expected_events:raise AssertionError('step event count')
        start,end=(0,PROMPT_TOKENS-1) if step==0 else (PROMPT_TOKENS+step-1,PROMPT_TOKENS+step-1)
        first_pos,first_layer,first_k=first.get(step,(-1,-1,-1))
        affected_layers=sorted(int(k[6:]) for k,v in c.items() if k.startswith('layer_') and v)
        classes=[name for name in ('ORDER_ONLY_SWAP','EXPERT_SET_SUBSTITUTION','STRUCTURE_SHIFT') if c[name]]
        classification=classes[0] if len(classes)==1 else 'MIXED' if classes else 'NO_DIFFERENCE'
        step_rows.append(dict(decode_output_step=f'D{step}',route_scope='PROMPT_FORWARD' if step==0 else 'DECODE_FORWARD',
                              route_position_start=start,route_position_end=end,routing_event_count=c['events'],
                              ordered_equal_events=c['EXACT_MATCH'],order_only_swap_events=c['ORDER_ONLY_SWAP'],
                              expert_set_substitution_events=c['EXPERT_SET_SUBSTITUTION'],
                              structure_shift_events=c['STRUCTURE_SHIFT'],affected_routing_events=c['affected_events'],
                              positional_mismatch_count=c['positional_mismatches'],
                              affected_layers_count=len(affected_layers),affected_layers=','.join(map(str,affected_layers)),
                              set_equal_event_count=c['EXACT_MATCH']+c['ORDER_ONLY_SWAP'],
                              first_divergence_position=first_pos,first_divergence_layer=first_layer,
                              first_divergence_topk_position=first_k,classification=classification))
    log_rows=[];max_abs=0.0
    if len(left['logprobs'])!=GENERATED_TOKENS or len(right['logprobs'])!=GENERATED_TOKENS:
        raise AssertionError('logprob step mismatch')
    for step,(token_a,token_b,log_a,log_b) in enumerate(zip(tokens_a,tokens_b,left['logprobs'],right['logprobs'])):
        if token_a!=token_b:raise AssertionError('generated token difference')
        a=sampled_logprob(log_a,token_a);b=sampled_logprob(log_b,token_a)
        delta=abs(a-b);limit=ATOL+RTOL*abs(a);max_abs=max(max_abs,delta)
        log_rows.append(dict(decode_output_step=f'D{step}',sampled_token_id=token_a,
                             graph_off_logprob=repr(a),graph_on_logprob=repr(b),abs_delta=repr(delta),
                             original_atol=ATOL,original_rtol=RTOL,original_limit=repr(limit),
                             exceeds_original_tolerance=str(delta>limit).lower()))
    if abs(max_abs-0.10254716873168945)>1e-12:raise AssertionError('historical logprob cross-check')
    total=Counter()
    for c in by_step.values():total.update(c)
    if total['events']!=543*LAYERS:raise AssertionError('event conservation')
    if total['EXPERT_SET_SUBSTITUTION']:
        final='OLMOE_GRAPH_MODE_EXPERT_SET_DIVERGENCE'
    elif total['STRUCTURE_SHIFT']:
        final='OLMOE_GRAPH_MODE_CORRECTNESS_CAUSE_UNRESOLVED'
    elif total['ORDER_ONLY_SWAP']:
        final='OLMOE_GRAPH_MODE_ROUTE_ORDER_ONLY_DIFFERENCE'
    else:
        final='OLMOE_GRAPH_MODE_CORRECTNESS_CAUSE_UNRESOLVED'
    structure=dict(raw_nested_shape={'graph_off':[shape_a[0],LAYERS,TOPK],
                                      'graph_on':[shape_b[0],LAYERS,TOPK]},
                   prompt_token_count=PROMPT_TOKENS,generated_token_count=GENERATED_TOKENS,
                   per_generated_output_step_route_shape={'D0':[PROMPT_TOKENS,LAYERS,TOPK],
                                                           'D1_to_D31':[1,LAYERS,TOPK]},
                   mapping='D0 contains 512 prompt-forward routes; D1-D31 each contains one forwarded prior generated token; last D31 sampled token has no separate route',
                   route_position_count=543,routing_event_count=total['events'],
                   ordered_equal_events=total['EXACT_MATCH'],order_only_swap_events=total['ORDER_ONLY_SWAP'],
                   expert_set_substitution_events=total['EXPERT_SET_SUBSTITUTION'],
                   structure_shift_events=total['STRUCTURE_SHIFT'],
                   positional_mismatch_count=scalar,duplicate_ids_within_topk=duplicates,
                   positional_mismatches_by_event_class=dict(sorted(scalar_by_class.items())),
                   set_substitution_intersection_histogram={str(k):v for k,v in sorted(intersection_histogram.items())},
                   set_substitution_jaccard_min=min(substitution_jaccards) if substitution_jaccards else None,
                   set_substitution_jaccard_mean=sum(substitution_jaccards)/len(substitution_jaccards) if substitution_jaccards else None,
                   affected_event_order_only_fraction=total['ORDER_ONLY_SWAP']/(total['ORDER_ONLY_SWAP']+total['EXPERT_SET_SUBSTITUTION']) if total['ORDER_ONLY_SWAP']+total['EXPERT_SET_SUBSTITUTION'] else 0.0,
                   positional_mismatches_prefill=by_step[0]['positional_mismatches'],
                   positional_mismatches_decode=sum(by_step[s]['positional_mismatches'] for s in range(1,GENERATED_TOKENS)),
                   first_divergence_global=first.get(min(first),None) if first else None,
                   first_divergence_by_event_class=first_class,
                   sampled_token_ids_equal=True,
                   logprob_max_abs_delta=max_abs,logprob_exceeds_steps=[r['decode_output_step'] for r in log_rows if r['exceeds_original_tolerance']=='true'],
                   first_logprob_nonzero_step=next((r['decode_output_step'] for r in log_rows if float(r['abs_delta'])>0),None),
                   first_logprob_tolerance_failure_step=next((r['decode_output_step'] for r in log_rows if r['exceeds_original_tolerance']=='true'),None),
                   final_classification=final)
    return structure,step_rows,event_rows,log_rows


def build(raw: Path,pack: Path,out: Path) -> dict:
    off_path=raw/'OLMOE_off.json';on_path=raw/'OLMOE_on.json'
    off_sha=sha_file(off_path);on_sha=sha_file(on_path)
    if (off_sha,on_sha)!=(EXPECTED_OFF_SHA,EXPECTED_ON_SHA):
        raise AssertionError('durable raw SHA mismatch')
    historical=json.loads((pack/'FINAL_DECISION.json').read_bytes())
    receipt=json.loads((pack/'OLMOE_RUNTIME_RECEIPT.json').read_bytes())
    thresholds=json.loads((pack/'CORRECTNESS_AND_NEUTRALITY_THRESHOLDS.json').read_bytes())
    if historical['target_readiness']['OLMOE']['blocker']!='CORRECTNESS_OR_BACKEND_IDENTITY_FAILED':
        raise AssertionError('original failed decision changed')
    if receipt['graph_off_on_correctness']['routing_mismatch_count']!=EXPECTED_SCALARS:
        raise AssertionError('original mismatch count changed')
    if thresholds['correctness']['logprob_numeric']['OLMOE']!={'atol':ATOL,'rtol':RTOL}:
        raise AssertionError('frozen tolerance changed')
    off=json.loads(off_path.read_bytes());on=json.loads(on_path.read_bytes())
    structure,steps,events,logprobs=analyze(off,on)
    off_native_routing_hashes=sorted({row['output']['routing_sha256'] for row in off['native_runs']})
    on_native_routing_hashes=sorted({row['output']['routing_sha256'] for row in on['native_runs']})
    if len(off_native_routing_hashes)!=1 or len(on_native_routing_hashes)!=1:
        raise AssertionError('native arm has inconsistent routing snapshots')
    structure.update(authority_commit='3f62f909a474e4c56695ffacf36ddcb5d7b5f147',
                     original_failure='CORRECTNESS_OR_BACKEND_IDENTITY_FAILED',
                     raw_off_sha256=off_sha,raw_on_sha256=on_sha,
                     selected_off_native_arm='first native_runs entry with arm OFF',
                     selected_on_native_arm='native_runs[0] in OLMOE_on.json',
                     graph_off_native_run_count=len(off['native_runs']),
                     graph_off_unique_native_routing_sha256=off_native_routing_hashes,
                     graph_on_native_run_count=len(on['native_runs']),
                     graph_on_unique_native_routing_sha256=on_native_routing_hashes,
                     field_semantics='captured logical topk_ids by token-forward position and layer before EPLB mapping;source audited separately')
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/'ROUTING_STRUCTURE.json',structure)
    tsv(out/'ROUTING_MISMATCH_BY_STEP.tsv',steps)
    tsv(out/'ROUTING_SET_VS_ORDER.tsv',events)
    tsv(out/'LOGPROB_DELTA_BY_STEP.tsv',logprobs)
    decision=dict(status=structure['final_classification'],original_canary_status='CORRECTNESS_OR_BACKEND_IDENTITY_FAILED',
                  original_failure_preserved=True,original_tolerance_preserved=True,
                  graph_off_on_tokens_exact=True,backend_identity_exact=receipt['graph_off_on_correctness']['backend_identity_exact'],
                  ordered_scalar_mismatch_count=EXPECTED_SCALARS,
                  order_only_swap_events=structure['order_only_swap_events'],
                  expert_set_substitution_events=structure['expert_set_substitution_events'],
                  structure_shift_events=structure['structure_shift_events'],
                  logprob_max_abs_delta=structure['logprob_max_abs_delta'],
                  logprob_outside_original_tolerance_steps=structure['logprob_exceeds_steps'],
                  bottom_level_numeric_cause='UNKNOWN',
                  graph_only_causation='NOT_IDENTIFIED_ENFORCE_EAGER_ALSO_CHANGES_COMPILATION',
                  v2_canary_draft_generated=False,
                  new_gpu_execution_authorized=False)
    write_json(out/'FINAL_DECISION.json',decision)
    print(json.dumps(dict(status=decision['status'],events=structure['routing_event_count'],
                          mismatch_scalars=EXPECTED_SCALARS,order_only=decision['order_only_swap_events'],
                          set_substitution=decision['expert_set_substitution_events'],
                          logprob_fail_steps=decision['logprob_outside_original_tolerance_steps']),sort_keys=True))
    return decision


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--raw',type=Path,required=True)
    p.add_argument('--authority-pack',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args();build(args.raw,args.authority_pack,args.out)


if __name__=='__main__':main()
