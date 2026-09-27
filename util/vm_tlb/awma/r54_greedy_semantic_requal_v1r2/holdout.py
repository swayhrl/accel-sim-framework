#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,statistics,time
from pathlib import Path
import torch
from transformers import DynamicCache
from production import Context,build_resources,load_model,make_slot,reference_boundary_hashes,slot_hashes
from semantic_gate import semantic,thash,kv_hashes
from restore import restore

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
IDS=json.loads((ROOT/'prefix/PREFIX_HOLDOUT_2048.json').read_text())
SUFFIX=json.loads((ROOT/'prefix/HOLDOUT_SUFFIX_256.json').read_text())
ARMS=['P0','P2_D512','R1_HOLDOUT','L1_HOLDOUT','F1_HOLDOUT']

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n',extrasaction='ignore')
        w.writeheader();w.writerows(rows)

def metadata_from(cache,slot):
    return {i:{'has_previous_state':cache.layers[i].has_previous_state[0],
      'is_conv_states_initialized':cache.layers[i].is_conv_states_initialized[0],
      'is_recurrent_states_initialized':cache.layers[i].is_recurrent_states_initialized[0],
      'conv_kernel_size':cache.layers[i].conv_kernel_size[0],
      'record_past':cache.layers[i].record_past} for i in slot}

@torch.inference_mode()
def prod_run(ctx,resources,arm,kind,rep,parts,collect_reference=False):
    r=resources[arm]
    cache=DynamicCache(config=ctx.model.config)
    state={'kind':'P2' if arm=='P2_D512' else 'P0','density':512 if arm=='P2_D512' else 0,
      'cache':cache,'slots':r['slots'],'events':r['events'],'snapshot_stream':r['snapshot_stream'],
      'slot_idx':None,'last_done':{},'all_copies':[],'hook_invocations':0,'source_reuse_waits':0,
      'host_copy_schedule_ns':0}
    ctx.active=state
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    stream=torch.cuda.current_stream();start=torch.cuda.Event(enable_timing=True)
    done=torch.cuda.Event(enable_timing=True)
    refs=[];host_start=time.perf_counter_ns();start.record(stream)
    try:
        for j in range(4):
            state['slot_idx']=j if arm=='P2_D512' else None
            out=ctx.model(input_ids=parts[j],past_key_values=cache,use_cache=True,return_dict=True)
            if cache.get_seq_length()!=(j+1)*512:raise ValueError('holdout cache progression')
            if collect_reference:
                torch.cuda.synchronize()
                refs.append(reference_boundary_hashes(cache))
        if arm=='P2_D512':
            for s,i in state['all_copies']:
                stream.wait_event(r['events'][s][i]['copy_end'])
        done.record(stream);torch.cuda.synchronize();host_end=time.perf_counter_ns()
        row={'arm':arm,'kind':kind,'rep':rep,'total_gpu_ms':start.elapsed_time(done),
          'host_elapsed_ms':(host_end-host_start)/1e6,
          'host_snapshot_schedule_ms':state['host_copy_schedule_ns']/1e6,
          'copy_gpu_ms_sum':sum(r['events'][s][i]['copy_start'].elapsed_time(r['events'][s][i]['copy_end']) for s,i in state['all_copies']) if arm=='P2_D512' else 0.0,
          'snapshot_bytes_total':4*19759104 if arm=='P2_D512' else 0,
          'source_reuse_waits':state['source_reuse_waits'],
          'cache_seq_length':int(cache.get_seq_length()),
          'argmax_token_id':int(out.logits[:,-1,:].argmax()),
          'logits_finite':bool(torch.isfinite(out.logits[:,-1,:]).all()),
          'peak_allocated_bytes':torch.cuda.max_memory_allocated()}
        if kind=='CANARY':
            if collect_reference:row['reference_boundary_hashes']=refs
            if arm=='P2_D512':
                row['slot_hashes']=[slot_hashes(s) for s in r['slots']]
                row['metadata']=metadata_from(cache,r['slots'][-1])
                row['full_attention_kv_hashes']=kv_hashes(cache)
            sem,_=semantic(ctx.model,out)
            row['continuation_token_ids']=sem['tokens']
            row['continuation_top8_set']=sem['top8_set'];row['continuation_top2']=sem['top2']
        return row
    finally:ctx.active=None

def prep_prefix(model,parts):
    cache=DynamicCache(config=model.config)
    out=None
    for part in parts:out=model(input_ids=part,past_key_values=cache,use_cache=True,return_dict=True)
    if cache.get_seq_length()!=2048:raise ValueError('prefix2048 cache')
    return out

@torch.inference_mode()
def suffix_run(model,arm,kind,rep,parts,suffix,slot,metadata):
    cache=None
    if arm!='F1_HOLDOUT':
        prior=prep_prefix(model,parts)
        cache=prior.past_key_values
        if arm=='R1_HOLDOUT':
            for i in slot:
                layer=cache.layers[i]
                layer.conv_states[0].zero_();layer.recurrent_states[0].zero_()
                layer.has_previous_state[0]=False
                layer.is_conv_states_initialized[0]=False
                layer.is_recurrent_states_initialized[0]=False
            torch.cuda.synchronize()
    torch.cuda.synchronize();torch.cuda.reset_peak_memory_stats()
    stream=torch.cuda.current_stream();start=torch.cuda.Event(enable_timing=True)
    copy_end=torch.cuda.Event(enable_timing=True);done=torch.cuda.Event(enable_timing=True)
    host_start=time.perf_counter_ns();start.record(stream)
    if arm=='R1_HOLDOUT':
        restore(cache,slot,metadata);copy_end.record(stream)
    if arm=='F1_HOLDOUT':
        prior=prep_prefix(model,parts);cache=prior.past_key_values
    out=model(input_ids=suffix,past_key_values=cache,use_cache=True,return_dict=True)
    done.record(stream);torch.cuda.synchronize();host_end=time.perf_counter_ns()
    if cache.get_seq_length()!=2304:raise ValueError('holdout suffix cache length')
    top=torch.topk(out.logits[:,-1,:],8).indices[0].tolist()
    row={'arm':arm,'kind':kind,'rep':rep,'total_gpu_ms':start.elapsed_time(done),
         'restore_copy_gpu_ms':start.elapsed_time(copy_end) if arm=='R1_HOLDOUT' else 0.0,
         'host_elapsed_ms':(host_end-host_start)/1e6,
         'checkpoint_bytes':19759104 if arm=='R1_HOLDOUT' else 0,
         'cache_seq_length':int(cache.get_seq_length()),
         'argmax_token_id':top[0],
         'top8_set':json.dumps(sorted(top),separators=(',',':')),
         'top2_order':json.dumps(top[:2],separators=(',',':')),
         'logits_finite':bool(torch.isfinite(out.logits[:,-1,:]).all()),
         'peak_allocated_bytes':torch.cuda.max_memory_allocated()}
    if kind=='CANARY':
        sem,_=semantic(model,out)
        row['continuation_token_ids']=sem['tokens']
        row['continuation_top8_set']=sem['top8_set'];row['continuation_top2']=sem['top2']
    return row

def main():
    model=load_model()
    ctx=Context(model)
    parts=[torch.tensor([IDS[j*512:(j+1)*512]],dtype=torch.long,device='cuda:0') for j in range(4)]
    suffix=torch.tensor([SUFFIX],dtype=torch.long,device='cuda:0')
    with torch.inference_mode():sample=model(input_ids=parts[0],use_cache=True,return_dict=True)
    resources=build_resources(sample.past_key_values)
    for arm in ['P0','P2_D512']:
        resources[arm]['slots']=resources[arm]['slots'][:4]
        resources[arm]['events']=resources[arm]['events'][:4]
    canaries={}
    canaries['P0']=prod_run(ctx,resources,'P0','CANARY',0,parts,True)
    canaries['P2_D512']=prod_run(ctx,resources,'P2_D512','CANARY',0,parts)
    snap_ok=canaries['P2_D512']['slot_hashes']==canaries['P0']['reference_boundary_hashes']
    p2_sem=(canaries['P2_D512']['continuation_token_ids']==canaries['P0']['continuation_token_ids'] and
            canaries['P2_D512']['continuation_top8_set']==canaries['P0']['continuation_top8_set'] and
            canaries['P2_D512']['continuation_top2']==canaries['P0']['continuation_top2'])
    slot=resources['P2_D512']['slots'][-1]
    metadata={int(i):v for i,v in canaries['P2_D512']['metadata'].items()}
    for arm in ARMS[2:]:canaries[arm]=suffix_run(model,arm,'CANARY',0,parts,suffix,slot,metadata)
    live=canaries['L1_HOLDOUT']
    suffix_gate={a:{'same_greedy_16':canaries[a]['continuation_token_ids']==live['continuation_token_ids'],
                    'same_top8_set':canaries[a]['continuation_top8_set']==live['continuation_top8_set'],
                    'same_top2_order':canaries[a]['continuation_top2']==live['continuation_top2'],
                    'same_cache_length':canaries[a]['cache_seq_length']==live['cache_seq_length']==2304,
                    'finite':canaries[a]['logits_finite'] and live['logits_finite']}
                  for a in ['R1_HOLDOUT','F1_HOLDOUT']}
    qualified=snap_ok and p2_sem and all(all(v.values()) for v in suffix_gate.values())
    (ROOT/'HOLDOUT_CANARY_RECEIPT.json').write_text(json.dumps({'qualified':qualified,
      'p2_snapshot_content_exact':snap_ok,'p2_semantics':p2_sem,
      'suffix_semantics':suffix_gate,'canaries':canaries},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'holdout_canary_qualified':qualified,'snapshot_exact':snap_ok,'p2_semantics':p2_sem,'suffix_semantics':suffix_gate},sort_keys=True))
    if not qualified:return
    def execute(arm,kind,rep):
        return prod_run(ctx,resources,arm,kind,rep,parts) if arm in ('P0','P2_D512') else suffix_run(model,arm,kind,rep,parts,suffix,slot,metadata)
    for warmup in range(2):
        for arm in ARMS:execute(arm,'WARMUP',warmup)
    formal=[]
    for rep in range(7):
        order=ARMS[rep%len(ARMS):]+ARMS[:rep%len(ARMS)]
        for arm in order:
            r=execute(arm,'FORMAL',rep)
            if not r['logits_finite'] or r['argmax_token_id']!=canaries[arm]['argmax_token_id']:
                raise ValueError(f'holdout formal identity {arm}/{rep}')
            formal.append(r)
            print(json.dumps({'arm':arm,'rep':rep,'gpu_ms':r['total_gpu_ms']}))
    write_tsv(ROOT/'HOLDOUT_RESULTS.tsv',formal)
    summary={}
    for arm in ARMS:
        values=[r['total_gpu_ms'] for r in formal if r['arm']==arm]
        med=statistics.median(values)
        summary[arm]={'median_ms':med,'values_ms':values,
          'max_relative_jitter':max(abs(v-med) for v in values)/med}
    base=summary['P0'];p2=summary['P2_D512']
    overhead=(p2['median_ms']-base['median_ms'])/base['median_ms']
    noise=max(p2['max_relative_jitter'],base['max_relative_jitter'])
    summary['P2_D512']['overhead_fraction_vs_p0']=overhead
    summary['P2_D512']['larger_conservative_jitter_fraction']=noise
    summary['P2_D512']['effect_over_jitter_ratio']=overhead/noise if noise else None
    summary['P2_D512']['stable_material_cost']=overhead>=0.05 and overhead>3*noise
    (ROOT/'HOLDOUT_ANALYSIS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'holdout_p2_overhead_fraction':overhead,'stable_material_cost':summary['P2_D512']['stable_material_cost']}))

if __name__=='__main__':main()
