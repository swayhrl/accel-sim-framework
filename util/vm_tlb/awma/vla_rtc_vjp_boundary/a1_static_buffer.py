#!/usr/bin/env python3
"""Single fallback A1: fixed prefix-buffer/weight reuse, same repaired VJP."""
import csv
import json
import os
import statistics
import time
from pathlib import Path

import numpy as np
import torch

from a0_reference import ROOT, PACK, RAW, MODEL, windows, obs, noise_gen, load_runtime, sha

A1=ROOT/'raw/f4';A1.mkdir(parents=True,exist_ok=True)

def compare(a,b):
    assert a.shape==b.shape
    a=a.detach().cpu();b=b.detach().cpu()
    atol,rtol=(1e-5,1e-4) if a.dtype==torch.float32 else (1e-3,1e-2)
    return {'dtype':str(a.dtype),'max_abs':float((a-b).abs().max()),
            'max_rel':float(((a-b).abs()/(b.abs()+1e-12)).max()),
            'allclose':bool(torch.allclose(a,b,atol=atol,rtol=rtol)),
            'atol':atol,'rtol':rtol}

def make_static_baseline(policy,delay):
    rtc=policy.rtc_processor
    original=rtc.get_prefix_weights
    start=time.perf_counter()
    weights=original(delay,10,50).to('cuda:0')
    previous_buffer=torch.zeros((1,50,32),device='cuda:0',dtype=torch.float32)
    torch.cuda.synchronize()
    init_ms=(time.perf_counter()-start)*1000
    assert weights.dtype==torch.float32 and tuple(weights.shape)==(50,)
    def cached_weights(start,end,total):
        assert (start,end,total)==(delay,10,50)
        return weights
    rtc.get_prefix_weights=cached_weights
    return previous_buffer,weights,init_ms

def run_sequence_static(policy,pre,post,z,rows,delay,buffer,record_time):
    policy.reset()
    gens=[noise_gen(r['noise_seed']) for r in rows]
    previous=None;raw_list=[];committed_list=[];times=[]
    for i,r in enumerate(rows):
        start=time.perf_counter()
        batch=pre(obs(z,i))
        latent=torch.randn((1,50,32),generator=gens[i],device='cuda:0',dtype=torch.float32)
        if previous is None:
            kwargs={}
        else:
            # In the original RTC wrapper this exact zero padding occurs once
            # per denoise/VJP step. A1 performs it once per complete chunk.
            buffer.zero_()
            buffer[:,:10,:7].copy_(previous.unsqueeze(0))
            kwargs={'inference_delay':delay,'prev_chunk_left_over':buffer}
        raw=policy.predict_action_chunk(batch,noise=latent,**kwargs)
        committed=post(raw)
        torch.cuda.synchronize()
        elapsed_ms=(time.perf_counter()-start)*1000
        previous=raw.detach().squeeze(0)[10:20].clone()
        raw_list.append(raw.detach());committed_list.append(committed.detach())
        if record_time:times.append(elapsed_ms)
    return raw_list,committed_list,times

def trajectory_and_graph_gate(policy,pre,post,z,rows,delay,buffer):
    captured=[];rtc=policy.rtc_processor
    old_track=rtc.track;old_debug=rtc.is_debug_enabled
    old_grad=torch.autograd.grad
    counts={'vjp_calls':0,'expert_backward':0,'action_out_backward':0}
    def capture(**kw):
        item={'step_record_index':len(captured) if len(captured)<10 else (len(captured)-10)%20}
        for key in ('time','x_t','v_t','x1_t','correction','err','weights'):
            val=kw.get(key)
            if torch.is_tensor(val):item[key]=val.detach().cpu().clone()
            elif val is not None:item[key]=val
        captured.append(item)
    def grad_wrapper(*args,**kwargs):
        result=old_grad(*args,**kwargs)
        counts['vjp_calls']+=1
        assert torch.isfinite(result[0]).all()
        return result
    def hook(kind):
        def forward(_m,_a,out):
            if torch.is_tensor(out) and out.requires_grad:
                out.register_hook(lambda grad:counts.__setitem__(kind,counts[kind]+1))
        return forward
    qproj=policy.model.vlm_with_expert.lm_expert.layers[0].self_attn.q_proj
    handles=[qproj.register_forward_hook(hook('expert_backward')),
             policy.model.action_out_proj.register_forward_hook(hook('action_out_backward'))]
    rtc.track=capture;rtc.is_debug_enabled=lambda:True;torch.autograd.grad=grad_wrapper
    try:
        raw,committed,_=run_sequence_static(policy,pre,post,z,rows,delay,buffer,False)
    finally:
        rtc.track=old_track;rtc.is_debug_enabled=old_debug;torch.autograd.grad=old_grad
        for h in handles:h.remove()
    assert len(captured)==70,len(captured)
    checks=[]
    for window in (1,2,3):
        ref=torch.load(RAW/f'a0_guided_window{window}_trajectory.pt',map_location='cpu',weights_only=True)
        expected=ref['records']
        actual=captured[10+20*(window-1):10+20*window]
        assert len(expected)==len(actual)==20
        for step,(a,b) in enumerate(zip(actual,expected)):
            assert set(a)==set(b),(window,step,set(a),set(b))
            for key in a:
                if torch.is_tensor(a[key]):
                    checks.append({'window':window,'record':step,'key':key,**compare(a[key],b[key])})
                elif key=='time':
                    checks.append({'window':window,'record':step,'key':key,
                                   'allclose':a[key]==b[key],'max_abs':abs(float(a[key])-float(b[key]))})
    counts['trajectory_comparisons']=len(checks)
    counts['trajectory_pass']=all(x['allclose'] for x in checks)
    counts['trajectory_max_abs']=max(x['max_abs'] for x in checks)
    counts['parameter_grad_count']=sum(p.grad is not None for p in policy.parameters())
    assert counts['vjp_calls']==30 and counts['expert_backward']>=30 and counts['action_out_backward']>=30
    assert counts['trajectory_pass'] and counts['parameter_grad_count']==0
    return counts,checks

def main():
    assert os.environ.get('VLA_GPU_LOCK_HELD')=='1' and os.environ.get('HF_HUB_OFFLINE')=='1'
    graph=json.loads((ROOT/'raw/f0/real_model_graph_canary.json').read_text())
    delay=graph['inference_delay_frames'];assert delay==4
    fixture=torch.load(RAW/'a0_discovery_reference_outputs.pt',map_location='cpu',weights_only=True)
    rows=windows();z=np.load(ROOT/'raw/f1/discovery_observations.npz',allow_pickle=False)
    config,policy,pre,post=load_runtime()
    buffer,weights,init_ms=make_static_baseline(policy,delay)
    raw,committed,_=run_sequence_static(policy,pre,post,z,rows,delay,buffer,False)
    numeric=[]
    for i in range(4):
        numeric.append({'window':i,'raw':compare(raw[i],fixture['raw_actions'][i]),
                        'committed':compare(committed[i],fixture['committed_actions'][i])})
    numeric_pass=all(x['raw']['allclose'] and x['committed']['allclose'] for x in numeric)
    receipt={'arm':'A1_STATIC_BUFFER','initialization_ms':init_ms,
        'buffer_shape':list(buffer.shape),'buffer_dtype':str(buffer.dtype),
        'buffer_address':buffer.data_ptr(),'cached_weights_shape':list(weights.shape),
        'cached_weights_address':weights.data_ptr(),
        'numeric':numeric,'plain_numeric_pass':numeric_pass,
        'checkpoint_sha256':sha(MODEL/'model.safetensors'),
        'full_vjp_reference_source_sha256':graph['rtc_source_sha256']}
    (A1/'a1_static_numeric_pretrajectory.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    assert numeric_pass,'A1 plain numerical gate failed; no formal timing'
    counts,checks=trajectory_and_graph_gate(policy,pre,post,z,rows,delay,buffer)
    receipt.update({'trajectory_and_graph_gate':counts,'status':'A1_FULL_VJP_NUMERIC_QUALIFIED'})
    (A1/'a1_static_trajectory_checks.json').write_text(json.dumps(checks,indent=2,sort_keys=True)+'\n')
    (A1/'a1_static_numeric_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    measured=[];peak=0;max_err=0.0
    torch.cuda.reset_peak_memory_stats(0)
    for group in range(3):
        for rep in range(7):
            warmup=rep<2
            actual_raw,actual_committed,ms=run_sequence_static(policy,pre,post,z,rows,delay,buffer,True)
            for i,(r,value,actual,expected) in enumerate(zip(rows,ms,actual_committed,fixture['committed_actions'])):
                check=compare(actual,expected)
                assert check['allclose']
                max_err=max(max_err,check['max_abs'])
                measured.append({'arm':'A1_STATIC_BUFFER','episode':0,'group':group,'repeat':rep,
                    'status':'WARMUP' if warmup else 'FORMAL','window_ordinal':i,
                    'frame_index':int(r['episode_frame_index']),'guided':i>0,
                    'delay_frames':delay,'observation_ready_to_chunk_commit_ms':f'{value:.9f}',
                    'max_abs_vs_A0_reference':f"{check['max_abs']:.9g}"})
        with (PACK/'A1_TIMING.tsv').open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(measured[0]),delimiter='\t',lineterminator='\n')
            w.writeheader();w.writerows(measured)
    formal=[float(x['observation_ready_to_chunk_commit_ms']) for x in measured if x['status']=='FORMAL']
    guided=[float(x['observation_ready_to_chunk_commit_ms']) for x in measured if x['status']=='FORMAL' and x['guided']]
    assert len(measured)==84 and len(formal)==60 and len(guided)==45
    a0=json.loads((RAW/'a0_timing_summary.json').read_text())
    summary={'arm':'A1_STATIC_BUFFER','formal_rows':60,'warmup_rows':24,
        'complete_chunk_median_ms':statistics.median(formal),
        'complete_chunk_MAD_ms':statistics.median(abs(x-statistics.median(formal)) for x in formal),
        'guided_chunk_median_ms':statistics.median(guided),
        'guided_chunk_MAD_ms':statistics.median(abs(x-statistics.median(guided)) for x in guided),
        'guided_improvement_percent_vs_A0':100*(a0['guided_chunk_median_ms']-statistics.median(guided))/a0['guided_chunk_median_ms'],
        'max_abs_vs_A0_reference':max_err,'allocator_peak_formal_bytes':torch.cuda.max_memory_allocated(0),
        'status':'FORMAL_TIMING_COMPLETE','compiler_attempt':'author max-autotune failed CUDA misaligned address; no mode scan',
        'initialization_ms_separate':init_ms}
    (A1/'a1_static_timing_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'numeric_gate':counts,'summary':summary},sort_keys=True))

if __name__=='__main__':main()
