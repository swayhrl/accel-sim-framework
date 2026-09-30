#!/usr/bin/env python3
"""One bounded NSYS A1 guided-chunk target with nested semantic NVTX ranges."""
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import torch

from a0_reference import ROOT, RAW, windows, obs, noise_gen, load_runtime
from a1_static_buffer import make_static_baseline, run_sequence_static

OUT=ROOT/'raw/f5'

def main():
    assert os.environ.get('VLA_GPU_LOCK_HELD')=='1'
    graph=json.loads((ROOT/'raw/f0/real_model_graph_canary.json').read_text())
    assert graph['inference_delay_frames']==4
    rows=windows();z=np.load(ROOT/'raw/f1/discovery_observations.npz',allow_pickle=False)
    cfg,policy,pre,post=load_runtime()
    buffer,weights,_=make_static_baseline(policy,4)
    for _ in range(2):
        warm_raw,_,_=run_sequence_static(policy,pre,post,z,rows,4,buffer,False)
    prior=warm_raw[0].detach().squeeze(0)[10:20].clone()
    counters={'denoiser':0,'vjp':0,'rtc':0,'prefix_vlm':0}
    saved=[]
    def wrap(obj,name,label,original):
        def wrapped(*args,**kwargs):
            index=counters[label];counters[label]+=1
            torch.cuda.nvtx.range_push(f'{label.upper()}_{index}')
            try:return original(*args,**kwargs)
            finally:torch.cuda.nvtx.range_pop()
        setattr(obj,name,wrapped);saved.append((obj,name,original))
    wrap(policy.model,'denoise_step','denoiser',policy.model.denoise_step)
    wrap(policy.rtc_processor,'denoise_step','rtc',policy.rtc_processor.denoise_step)
    wrap(torch.autograd,'grad','vjp',torch.autograd.grad)
    orig_embed=policy.model.embed_prefix
    def embed(*args,**kwargs):
        torch.cuda.nvtx.range_push('PREFIX_EMBED')
        try:return orig_embed(*args,**kwargs)
        finally:torch.cuda.nvtx.range_pop()
    policy.model.embed_prefix=embed;saved.append((policy.model,'embed_prefix',orig_embed))
    orig_forward=policy.model.vlm_with_expert.forward
    def forward(*args,**kwargs):
        inputs=kwargs.get('inputs_embeds')
        if inputs is not None and inputs[0] is not None and inputs[1] is None:
            counters['prefix_vlm']+=1
            torch.cuda.nvtx.range_push('PREFIX_VLM')
            try:return orig_forward(*args,**kwargs)
            finally:torch.cuda.nvtx.range_pop()
        return orig_forward(*args,**kwargs)
    policy.model.vlm_with_expert.forward=forward
    torch.cuda.nvtx.range_push('VLA_A1_GUIDED_WINDOW1')
    begin=time.perf_counter()
    try:
        torch.cuda.nvtx.range_push('OBSERVATION_PREPROCESS')
        try:batch=pre(obs(z,1))
        finally:torch.cuda.nvtx.range_pop()
        latent=torch.randn((1,50,32),generator=noise_gen(rows[1]['noise_seed']),device='cuda:0',dtype=torch.float32)
        buffer.zero_();buffer[:,:10,:7].copy_(prior.unsqueeze(0))
        raw=policy.predict_action_chunk(batch,noise=latent,inference_delay=4,prev_chunk_left_over=buffer)
        torch.cuda.nvtx.range_push('CORRECTION_COMMIT')
        try:committed=post(raw);torch.cuda.synchronize()
        finally:torch.cuda.nvtx.range_pop()
    finally:
        elapsed_ms=(time.perf_counter()-begin)*1000
        torch.cuda.nvtx.range_pop()
        policy.model.vlm_with_expert.forward=orig_forward
        for obj,name,original in reversed(saved):setattr(obj,name,original)
    reference=torch.load(RAW/'a0_discovery_reference_outputs.pt',map_location='cpu',weights_only=True)
    assert torch.allclose(committed.cpu(),reference['committed_actions'][1],atol=1e-5,rtol=1e-4)
    assert counters['denoiser']==counters['vjp']==counters['rtc']==10 and counters['prefix_vlm']==1
    receipt={'status':'NSYS_SINGLE_GUIDED_CHUNK_COMPLETE','arm':'A1_STATIC_BUFFER',
        'episode':0,'frame':10,'delay_frames':4,'window_numerical_match_A0':True,
        'nested_NVTX_counts':counters,'instrumented_wall_ms':elapsed_ms,
        'profile_time_not_primary':True,
        'committed_sha256':hashlib.sha256(committed.detach().cpu().contiguous().numpy().tobytes()).hexdigest()}
    (OUT/'nsys_target_receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
