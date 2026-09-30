#!/usr/bin/env python3
"""Frozen A0 full-VJP reference timing and separate diagnostics on episode A."""
import csv
import hashlib
import json
import os
import statistics
import time
from pathlib import Path

import numpy as np
import torch
from lerobot.configs import RTCAttentionSchedule
from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.rtc.configuration_rtc import RTCConfig
from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
PACK=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-vla-rtc-vjp-boundary-109-v1/docs/vm_tlb/review_packs/AWMA_VLA_RTC_VJP_BOUNDARY_109_V1')
MODEL=ROOT/'assets/model'; BASE=ROOT/'assets/base_vlm'
RAW=ROOT/'raw/f2'; RAW.mkdir(parents=True,exist_ok=True)

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def load_runtime():
    torch.set_num_threads(8)
    config=SmolVLAConfig.from_pretrained(str(MODEL))
    config.device='cuda:0';config.load_vlm_weights=False;config.vlm_model_name=str(BASE)
    config.rtc_config=RTCConfig(enabled=True,mode='guided',
        prefix_attention_schedule=RTCAttentionSchedule.LINEAR,
        max_guidance_weight=10.0,execution_horizon=10,debug=False)
    policy=SmolVLAPolicy.from_pretrained(str(MODEL),config=config,strict=True,local_files_only=True)
    policy.requires_grad_(False)
    assert all(not p.requires_grad for p in policy.parameters())
    pre,post=make_pre_post_processors(config,pretrained_path=str(MODEL),
        preprocessor_overrides={'tokenizer_processor':{'tokenizer_name':str(BASE)},
                                'device_processor':{'device':'cuda:0'}},
        postprocessor_overrides={'device_processor':{'device':'cpu'}})
    return config,policy,pre,post

def windows():
    with (PACK/'TARGET_WINDOWS.tsv').open(newline='') as f:
        rows=[r for r in csv.DictReader(f,delimiter='\t') if r['role']=='A_DISCOVERY']
    assert [int(x['episode_frame_index']) for x in rows]==[0,10,20,30]
    return rows

def obs(z,i):
    def image(key): return torch.from_numpy(z[key][i].copy()).permute(2,0,1).float().div(255)
    return {'observation.images.image':image('image1_rgb'),
            'observation.images.image2':image('image2_rgb'),
            'observation.state':torch.from_numpy(z['state'][i].copy()),
            'task':str(z['task_text'][i])}

def noise_gen(seed):
    g=torch.Generator(device='cuda:0');g.manual_seed(int(seed));return g

def run_sequence(policy,pre,post,z,rows,delay,record_time):
    policy.reset()
    generators=[noise_gen(r['noise_seed']) for r in rows]
    raw_list=[]; committed_list=[]; times=[]
    previous=None
    for i,r in enumerate(rows):
        start=time.perf_counter()
        batch=pre(obs(z,i))
        latent=torch.randn((1,50,32),generator=generators[i],device='cuda:0',dtype=torch.float32)
        kwargs={} if previous is None else {'inference_delay':delay,'prev_chunk_left_over':previous}
        raw=policy.predict_action_chunk(batch,noise=latent,**kwargs)
        committed=post(raw)
        torch.cuda.synchronize()
        elapsed_ms=(time.perf_counter()-start)*1000
        # The prior *normalized original* action tail is used, as in LeRobot's
        # RTC inference queue. This preparation is outside the finished chunk.
        previous=raw.detach().squeeze(0)[10:20].clone()
        raw_list.append(raw.detach());committed_list.append(committed.detach())
        if record_time: times.append(elapsed_ms)
    return raw_list,committed_list,times

def event_diagnostic(policy,pre,post,z,rows,delay,prior):
    events={k:[] for k in ('embed_prefix','prefix_vlm','denoiser','vjp','rtc_step')}
    def wrap(obj,name,key,original):
        def measured(*args,**kwargs):
            a=torch.cuda.Event(enable_timing=True);b=torch.cuda.Event(enable_timing=True)
            a.record();result=original(*args,**kwargs);b.record()
            events[key].append((a,b));return result
        setattr(obj,name,measured)
        return original
    originals=[]
    originals.append((policy.model,'embed_prefix',wrap(policy.model,'embed_prefix','embed_prefix',policy.model.embed_prefix)))
    originals.append((policy.model,'denoise_step',wrap(policy.model,'denoise_step','denoiser',policy.model.denoise_step)))
    originals.append((policy.rtc_processor,'denoise_step',wrap(policy.rtc_processor,'denoise_step','rtc_step',policy.rtc_processor.denoise_step)))
    orig_forward=policy.model.vlm_with_expert.forward
    def forward_wrapper(*args,**kwargs):
        inputs=kwargs.get('inputs_embeds')
        if inputs is not None and inputs[0] is not None and inputs[1] is None:
            a=torch.cuda.Event(enable_timing=True);b=torch.cuda.Event(enable_timing=True)
            a.record();result=orig_forward(*args,**kwargs);b.record();events['prefix_vlm'].append((a,b));return result
        return orig_forward(*args,**kwargs)
    policy.model.vlm_with_expert.forward=forward_wrapper
    orig_grad=torch.autograd.grad
    def grad_wrapper(*args,**kwargs):
        a=torch.cuda.Event(enable_timing=True);b=torch.cuda.Event(enable_timing=True)
        a.record();result=orig_grad(*args,**kwargs);b.record();events['vjp'].append((a,b));return result
    torch.autograd.grad=grad_wrapper
    try:
        batch=pre(obs(z,1))
        latent=torch.randn((1,50,32),generator=noise_gen(rows[1]['noise_seed']),device='cuda:0')
        start=time.perf_counter()
        raw=policy.predict_action_chunk(batch,noise=latent,
            inference_delay=delay,prev_chunk_left_over=prior.detach().squeeze(0)[10:20].clone())
        committed=post(raw)
        torch.cuda.synchronize()
        wall_ms=(time.perf_counter()-start)*1000
    finally:
        torch.autograd.grad=orig_grad
        policy.model.vlm_with_expert.forward=orig_forward
        for obj,name,original in originals:setattr(obj,name,original)
    parts={k:sum(a.elapsed_time(b) for a,b in pairs) for k,pairs in events.items()}
    counts={k:len(v) for k,v in events.items()}
    assert counts['denoiser']==10 and counts['vjp']==10 and counts['rtc_step']==10
    return {'wall_ms_diagnostic':wall_ms,'event_ms':parts,'event_counts':counts,
            'rtc_step_minus_denoiser_vjp_ms':parts['rtc_step']-parts['denoiser']-parts['vjp'],
            'note':'instrumented CUDA events are diagnostic, not primary timing or disjoint whole-chunk sum'}

def saved_tensor_diagnostic(policy,pre,post,z,rows,delay,window_index,prior):
    # Saved tensors are counted at the PyTorch autograd boundary, distinct from
    # allocator peak and hardware DRAM. Pack hooks return the original tensor.
    step=[0]; per_step={}; records=[]
    def pack(tensor):
        s=per_step.setdefault(step[0],{'pack_calls':0,'raw_logical_bytes':0,'storage_max_logical_bytes':{}})
        n=tensor.numel()*tensor.element_size()
        s['pack_calls']+=1;s['raw_logical_bytes']+=n
        storage=tensor.untyped_storage();key=(str(tensor.device),storage.data_ptr(),storage.nbytes())
        s['storage_max_logical_bytes'][key]=max(n,s['storage_max_logical_bytes'].get(key,0))
        return tensor
    def unpack(tensor):return tensor
    orig_grad=torch.autograd.grad
    def grad_wrapper(*args,**kwargs):
        out=orig_grad(*args,**kwargs);step[0]+=1;return out
    rtc=policy.rtc_processor
    orig_track=rtc.track;orig_debug=rtc.is_debug_enabled
    def capture(**kw):
        item={'step_record_index':len(records)}
        for key in ('time','x_t','v_t','x1_t','correction','err','weights'):
            value=kw.get(key)
            if torch.is_tensor(value):item[key]=value.detach().cpu().clone()
            elif value is not None:item[key]=value
        records.append(item)
    torch.autograd.grad=grad_wrapper;rtc.track=capture;rtc.is_debug_enabled=lambda:True
    torch.cuda.reset_peak_memory_stats(0)
    baseline=torch.cuda.memory_allocated(0)
    try:
        with torch.autograd.graph.saved_tensors_hooks(pack,unpack):
            batch=pre(obs(z,window_index))
            latent=torch.randn((1,50,32),generator=noise_gen(rows[window_index]['noise_seed']),device='cuda:0')
            raw=policy.predict_action_chunk(batch,noise=latent,
                inference_delay=delay,prev_chunk_left_over=prior.detach().squeeze(0)[10:20].clone())
            committed=post(raw)
            torch.cuda.synchronize()
    finally:
        torch.autograd.grad=orig_grad;rtc.track=orig_track;rtc.is_debug_enabled=orig_debug
    peak=torch.cuda.max_memory_allocated(0)
    compact=[]
    for idx in sorted(per_step):
        s=per_step[idx]
        compact.append({'vjp_step':idx,'pack_calls':s['pack_calls'],
            'raw_logical_bytes':s['raw_logical_bytes'],
            'deduplicated_storage_max_logical_bytes':sum(s['storage_max_logical_bytes'].values()),
            'distinct_storage_count':len(s['storage_max_logical_bytes'])})
    assert step[0]==10
    trajectory=RAW/f'a0_guided_window{window_index}_trajectory.pt'
    torch.save({'records':records,'raw_action':raw.detach().cpu(),
                'committed_action':committed.detach().cpu()},trajectory)
    return {'guided_window':window_index,'vjp_calls':step[0],'saved_tensors_by_step':compact,
        'saved_tensor_raw_logical_bytes':sum(x['raw_logical_bytes'] for x in compact),
        'saved_tensor_deduplicated_logical_bytes':sum(x['deduplicated_storage_max_logical_bytes'] for x in compact),
        'allocator_baseline_bytes':baseline,'allocator_peak_bytes':peak,
        'allocator_peak_increment_bytes':peak-baseline,'trajectory_record_count':len(records),
        'trajectory_path':str(trajectory),'trajectory_sha256':sha(trajectory),
        'interpretation':'saved logical bytes, allocator peak and DRAM traffic are different quantities'}

def main():
    assert os.environ.get('VLA_GPU_LOCK_HELD')=='1' and os.environ.get('HF_HUB_OFFLINE')=='1'
    graph=json.loads((ROOT/'raw/f0/real_model_graph_canary.json').read_text())
    assert graph['status']=='REAL_MODEL_FULL_VJP_GRAPH_CANARY_OBSERVED'
    delay=graph['inference_delay_frames'];assert delay==4
    assert sha(MODEL/'model.safetensors')==graph['checkpoint_sha256']
    config,policy,pre,post=load_runtime()
    rows=windows();z=np.load(ROOT/'raw/f1/discovery_observations.npz',allow_pickle=False)
    assert z['frame_index'].tolist()==[0,10,20,30]
    # Frozen clean numerical fixture, separate from formal timings.
    fixture_raw,fixture_committed,_=run_sequence(policy,pre,post,z,rows,delay,False)
    fixture=RAW/'a0_discovery_reference_outputs.pt'
    torch.save({'raw_actions':[x.cpu() for x in fixture_raw],
                'committed_actions':[x.cpu() for x in fixture_committed],
                'episode':0,'frames':[0,10,20,30],'delay':delay},fixture)
    torch.cuda.synchronize()
    measured=[];max_abs=0.0
    torch.cuda.reset_peak_memory_stats(0)
    for group in range(3):
        for rep in range(7):
            warmup=rep<2
            raw,committed,ms=run_sequence(policy,pre,post,z,rows,delay,True)
            for ordinal,(r,value,actual,expected) in enumerate(zip(rows,ms,committed,fixture_committed)):
                error=float((actual.cpu()-expected.cpu()).abs().max().item())
                max_abs=max(max_abs,error)
                assert torch.allclose(actual.cpu(),expected.cpu(),rtol=1e-2,atol=1e-3)
                measured.append({'arm':'A0_FULL_VJP','episode':0,'group':group,'repeat':rep,
                    'status':'WARMUP' if warmup else 'FORMAL','window_ordinal':ordinal,
                    'frame_index':int(r['episode_frame_index']),'guided':ordinal>0,
                    'delay_frames':delay,'observation_ready_to_chunk_commit_ms':f'{value:.9f}',
                    'max_abs_vs_frozen_reference':f'{error:.9g}'})
            if rep==6:
                with (PACK/'A0_TIMING.tsv').open('w',newline='') as f:
                    w=csv.DictWriter(f,fieldnames=list(measured[0]),delimiter='\t',lineterminator='\n')
                    w.writeheader();w.writerows(measured)
    formal=[float(x['observation_ready_to_chunk_commit_ms']) for x in measured if x['status']=='FORMAL']
    guided=[float(x['observation_ready_to_chunk_commit_ms']) for x in measured if x['status']=='FORMAL' and x['guided']]
    assert len(measured)==84 and len(formal)==60 and len(guided)==45
    timing={'formal_rows':len(formal),'warmup_rows':24,'groups':3,'warmups_per_group':2,
        'formal_repeats_per_group':5,'window_count':4,'delay_frames':delay,
        'complete_chunk_median_ms':statistics.median(formal),
        'complete_chunk_MAD_ms':statistics.median(abs(x-statistics.median(formal)) for x in formal),
        'guided_chunk_median_ms':statistics.median(guided),
        'guided_chunk_MAD_ms':statistics.median(abs(x-statistics.median(guided)) for x in guided),
        'max_abs_vs_frozen_reference':max_abs,
        'allocator_peak_formal_bytes':torch.cuda.max_memory_allocated(0),
        'reference_outputs_sha256':sha(fixture),
        'primary_metric':'CPU observation arrays ready to complete CPU action chunk committed; no profiler instrumentation'}
    (RAW/'a0_timing_summary.json').write_text(json.dumps(timing,indent=2,sort_keys=True)+'\n')
    # Diagnostics run after primary timing is frozen. They are not latency authority.
    event=event_diagnostic(policy,pre,post,z,rows,delay,fixture_raw[0])
    (RAW/'a0_event_diagnostic.json').write_text(json.dumps(event,indent=2,sort_keys=True)+'\n')
    saved=[saved_tensor_diagnostic(policy,pre,post,z,rows,delay,i,fixture_raw[i-1]) for i in (1,2,3)]
    (RAW/'a0_saved_tensor_diagnostic.json').write_text(json.dumps(saved,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'timing':timing,'event':event,'saved_tensors':{
        str(x['guided_window']):{k:v for k,v in x.items() if k!='saved_tensors_by_step'} for x in saved}},sort_keys=True))

if __name__=='__main__':main()
