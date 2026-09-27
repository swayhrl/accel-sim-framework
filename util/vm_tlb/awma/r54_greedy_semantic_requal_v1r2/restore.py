#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,statistics,time,traceback
from pathlib import Path
import torch
from transformers import DynamicCache
from semantic_gate import config,prefill,semantic,thash,kv_hashes
from production import Context,build_resources,load_model,run_once

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
PREFIX=json.loads((ROOT/'prefix/PREFIX_DISCOVERY_4096.json').read_text())
SUFFIX={
 'A':json.loads((ROOT/'prefix/SUFFIX_A_512.json').read_text()),
 'B':json.loads((ROOT/'prefix/SUFFIX_B_512.json').read_text()),
}
ARMS=['R0','L1A','R1A','F1A','L1B','R1B','F1B']

def checkpoint_from_p2(model):
    ctx=Context(model)
    sample=model(input_ids=torch.tensor([PREFIX[:512]],dtype=torch.long,device='cuda:0'),use_cache=True,return_dict=True)
    resources=build_resources(sample.past_key_values)
    row=run_once(ctx,resources,'P2_D512','CHECKPOINT_AUTHORITY',0)
    assert row['cache_seq_length']==4096
    source=ctx.last_cache
    slot=resources['P2_D512']['slots'][-1]
    metadata={i:{
       'has_previous_state':layer.has_previous_state[0],
       'is_conv_states_initialized':layer.is_conv_states_initialized[0],
       'is_recurrent_states_initialized':layer.is_recurrent_states_initialized[0],
       'conv_kernel_size':layer.conv_kernel_size[0],
       'record_past':layer.record_past,
    } for i,layer in enumerate(source.layers) if i in slot}
    exact=all(torch.equal(slot[i]['conv'],source.layers[i].conv_states[0]) and
              torch.equal(slot[i]['recurrent'],source.layers[i].recurrent_states[0]) for i in slot)
    if not exact:raise ValueError('P2 final checkpoint does not match source state')
    checkpoint_hashes={i:{k:thash(v) for k,v in s.items()} for i,s in slot.items()}
    accepted=json.loads((ROOT/'PRODUCTION_CANARY_RECEIPT.json').read_text())['canaries']['P2_D512']['slot_hashes'][-1]
    if checkpoint_hashes!={int(i):v for i,v in accepted.items()}:
        raise ValueError('P2 checkpoint content differs from accepted production canary')
    authority={'source_arm':'P2_D512','boundary_token':4096,
      'gdn_layer_count':len(slot),'checkpoint_bytes':sum(t.numel()*t.element_size() for s in slot.values() for t in s.values()),
      'checkpoint_hashes':checkpoint_hashes,'metadata':metadata,
      'full_attention_kv_hashes_separate':kv_hashes(source),
      'production_canary_sha256':hashlib.sha256((ROOT/'PRODUCTION_CANARY_RECEIPT.json').read_bytes()).hexdigest()}
    (ROOT/'R54_P2_CHECKPOINT_AUTHORITY.json').write_text(json.dumps(authority,indent=2,sort_keys=True)+'\n')
    for handle in ctx.handles:handle.remove()
    return slot,metadata,authority

def restore(cache,slot,metadata):
    for i,s in slot.items():
        layer=cache.layers[i]
        layer.conv_states[0].copy_(s['conv'],non_blocking=True)
        layer.recurrent_states[0].copy_(s['recurrent'],non_blocking=True)
        for k,v in metadata[i].items():
            if k in ('has_previous_state','is_conv_states_initialized','is_recurrent_states_initialized','conv_kernel_size'):
                getattr(layer,k)[0]=v
            else:
                setattr(layer,k,v)

def valid_restored(cache,slot,metadata):
    return all(torch.equal(cache.layers[i].conv_states[0],s['conv']) and
      torch.equal(cache.layers[i].recurrent_states[0],s['recurrent']) and
      all((getattr(cache.layers[i],k)[0] if k!='record_past' else getattr(cache.layers[i],k))==v
          for k,v in metadata[i].items()) for i,s in slot.items())

def prepare_dest(model,slot):
    out=prefill(model,PREFIX,512)
    cache=out.past_key_values
    if cache.get_seq_length()!=4096:raise ValueError('bad prepared KV length')
    if any(cache.layers[i].conv_states[0].data_ptr()==s['conv'].data_ptr() or
           cache.layers[i].recurrent_states[0].data_ptr()==s['recurrent'].data_ptr()
           for i,s in slot.items()):raise ValueError('destination aliases checkpoint')
    for i in slot:
        layer=cache.layers[i]
        layer.conv_states[0].zero_();layer.recurrent_states[0].zero_()
        layer.has_previous_state[0]=False
        layer.is_conv_states_initialized[0]=False
        layer.is_recurrent_states_initialized[0]=False
    torch.cuda.synchronize()
    return out

@torch.inference_mode()
def run_arm(model,arm,kind,rep,slot,metadata,prefix_parts,suffix_tensors):
    suffix_name=arm[-1] if arm!='R0' else None
    cache=None;prefix_out=None
    if arm.startswith('R'):
        prefix_out=prepare_dest(model,slot)
        cache=prefix_out.past_key_values
    elif arm.startswith('L'):
        prefix_out=prefill(model,PREFIX,512)
        cache=prefix_out.past_key_values
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    stream=torch.cuda.current_stream()
    start=torch.cuda.Event(enable_timing=True);copy_end=torch.cuda.Event(enable_timing=True);done=torch.cuda.Event(enable_timing=True)
    host_start=time.perf_counter_ns()
    start.record(stream)
    with torch.inference_mode():
        if arm.startswith('R'):
            restore(cache,slot,metadata)
            copy_end.record(stream)
        if arm.startswith('F'):
            cache=DynamicCache(config=model.config)
            for part in prefix_parts:
                out=model(input_ids=part,past_key_values=cache,use_cache=True,return_dict=True)
            if cache.get_seq_length()!=4096:raise ValueError('full prefix recompute cache length')
        if arm!='R0':
            out=model(input_ids=suffix_tensors[suffix_name],past_key_values=cache,use_cache=True,return_dict=True)
        else:
            out=prefix_out
        done.record(stream)
        torch.cuda.synchronize()
        host_end=time.perf_counter_ns()
        cache_len=int(cache.get_seq_length())
        expected=4096 if arm=='R0' else 4608
        if cache_len!=expected:raise ValueError(f'{arm} cache length {cache_len} != {expected}')
        logits=out.logits[:,-1,:]
        top8=torch.topk(logits,8).indices[0].tolist()
        finite=bool(torch.isfinite(logits).all())
        row={'arm':arm,'kind':kind,'rep':rep,'suffix':suffix_name or '',
           'total_gpu_ms':start.elapsed_time(done),
           'restore_copy_gpu_ms':start.elapsed_time(copy_end) if arm.startswith('R') else 0.0,
           'host_elapsed_ms':(host_end-host_start)/1e6,
           'checkpoint_bytes':sum(t.numel()*t.element_size() for s in slot.values() for t in s.values()) if arm.startswith('R') else 0,
           'cache_seq_length':cache_len,'logits_finite':finite,
           'argmax_token_id':top8[0],'top8_set':json.dumps(sorted(top8),separators=(',',':')),
           'top2_order':json.dumps(top8[:2],separators=(',',':')),
           'peak_allocated_bytes':torch.cuda.max_memory_allocated(),
           'peak_reserved_bytes':torch.cuda.max_memory_reserved()}
        if kind in ('CANARY','PROFILE'):
            if arm.startswith('R'):
                row['restore_copy_bitwise_exact']=valid_restored(cache,slot,metadata) if arm=='R0' else None
            sem,_=semantic(model,out)
            row['continuation_token_ids']=sem['tokens']
            row['continuation_sha256']=sem['tokens_sha256']
            row['continuation_top8_set']=sem['top8_set']
            row['continuation_top2']=sem['top2']
            row['continuation_cache_len']=sem['cache_len']
        return row

def write_tsv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['formal','profile'],required=True)
    p.add_argument('--arm',choices=ARMS);args=p.parse_args()
    model=load_model()
    with torch.inference_mode():slot,metadata,authority=checkpoint_from_p2(model)
    prefix_parts=[torch.tensor([PREFIX[j*512:(j+1)*512]],dtype=torch.long,device='cuda:0') for j in range(8)]
    suffix_tensors={k:torch.tensor([v],dtype=torch.long,device='cuda:0') for k,v in SUFFIX.items()}
    if args.mode=='profile':
        if args.arm is None:raise ValueError('--arm required')
        torch.cuda.nvtx.range_push(f'R54_RESTORE_PROFILE_{args.arm}')
        try:row=run_arm(model,args.arm,'PROFILE',0,slot,metadata,prefix_parts,suffix_tensors)
        finally:torch.cuda.nvtx.range_pop()
        d=ROOT/'raw'/'restore_profile'/args.arm;d.mkdir(parents=True,exist_ok=True)
        (d/'CANARY.json').write_text(json.dumps(row,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'arm':args.arm,'total_gpu_ms':row['total_gpu_ms']}))
        return
    canaries={a:run_arm(model,a,'CANARY',0,slot,metadata,prefix_parts,suffix_tensors) for a in ARMS}
    sem={}
    sem['R0']={'copy_bitwise_exact':bool(canaries['R0']['restore_copy_bitwise_exact']),
               'cache_length_valid':canaries['R0']['cache_seq_length']==4096}
    for suffix in ('A','B'):
        live=canaries[f'L1{suffix}']
        for arm in [f'R1{suffix}',f'F1{suffix}']:
            row=canaries[arm]
            sem[arm]={'same_greedy_16':row['continuation_token_ids']==live['continuation_token_ids'],
                      'same_top8_set':row['continuation_top8_set']==live['continuation_top8_set'],
                      'same_top2_order':row['continuation_top2']==live['continuation_top2'],
                      'same_cache_length':row['cache_seq_length']==live['cache_seq_length']==4608,
                      'finite':row['logits_finite'] and live['logits_finite']}
    qualified=all(all(v.values()) for v in sem.values())
    (ROOT/'RESTORE_CANARY_RECEIPT.json').write_text(json.dumps({'qualified':qualified,'semantic_gates':sem,
       'checkpoint_authority':authority,'canaries':canaries},indent=2,sort_keys=True)+'\n')
    print(json.dumps({'restore_semantics_qualified':qualified,'semantic_gates':sem},sort_keys=True))
    if not qualified:return
    for warmup in range(2):
        for arm in ARMS:
            r=run_arm(model,arm,'WARMUP',warmup,slot,metadata,prefix_parts,suffix_tensors)
            if not r['logits_finite']:raise ValueError('warmup nonfinite')
    formal=[]
    for rep in range(7):
        order=ARMS[rep%len(ARMS):]+ARMS[:rep%len(ARMS)]
        for arm in order:
            r=run_arm(model,arm,'FORMAL',rep,slot,metadata,prefix_parts,suffix_tensors)
            if not r['logits_finite'] or r['argmax_token_id']!=canaries[arm]['argmax_token_id']:
                raise ValueError(f'formal identity failed {arm}/{rep}')
            formal.append(r)
            print(json.dumps({'arm':arm,'rep':rep,'gpu_ms':r['total_gpu_ms']}))
    write_tsv(ROOT/'RESTORE_TIMING.tsv',formal)
    summary={}
    for arm in ARMS:
        values=[r['total_gpu_ms'] for r in formal if r['arm']==arm]
        med=statistics.median(values)
        summary[arm]={'median_ms':med,'values_ms':values,'max_relative_jitter':max(abs(v-med) for v in values)/med}
    (ROOT/'RESTORE_ANALYSIS.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
