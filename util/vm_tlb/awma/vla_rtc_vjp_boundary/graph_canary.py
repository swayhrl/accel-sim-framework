#!/usr/bin/env python3
"""Lock-held real SmolVLA full-VJP graph qualification on frozen episode A."""
import csv
import hashlib
import json
import math
import os
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

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def input_observation(z,i):
    def image(key):return torch.from_numpy(z[key][i].copy()).permute(2,0,1).float().div(255)
    return {'observation.images.image':image('image1_rgb'),
            'observation.images.image2':image('image2_rgb'),
            'observation.state':torch.from_numpy(z['state'][i].copy()),
            'task':str(z['task_text'][i])}

def noise(seed):
    gen=torch.Generator(device='cuda:0');gen.manual_seed(int(seed))
    return torch.randn((1,50,32),generator=gen,device='cuda:0',dtype=torch.float32)

def first_tensor(value):
    if torch.is_tensor(value):return value
    if isinstance(value,(list,tuple)):
        for x in value:
            got=first_tensor(x)
            if got is not None:return got
    return None

def main():
    assert os.environ.get('VLA_GPU_LOCK_HELD')=='1'
    assert os.environ.get('HF_HUB_OFFLINE')=='1'
    assert sha(MODEL/'model.safetensors')=='9a9f6413e42c0f332fccbce9a0dc796af2790f82cf002f791cdbf7e01e1afca8'
    apps=os.popen('nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader').read()
    assert not apps.strip(), f'other GPU compute processes: {apps}'
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
    with (PACK/'TARGET_WINDOWS.tsv').open(newline='') as f:
        rows=[r for r in csv.DictReader(f,delimiter='\t') if r['role']=='A_DISCOVERY']
    assert [int(x['episode_frame_index']) for x in rows]==[0,10,20,30]
    z=np.load(ROOT/'raw/f1/discovery_observations.npz',allow_pickle=False)
    assert z['frame_index'].tolist()==[0,10,20,30]
    first=pre(input_observation(z,0))
    start=time.perf_counter()
    raw0=policy.predict_action_chunk(first,noise=noise(rows[0]['noise_seed']))
    committed0=post(raw0)
    torch.cuda.synchronize()
    canary_seconds=time.perf_counter()-start
    assert tuple(raw0.shape)==(1,50,7) and torch.isfinite(raw0).all()
    delay=math.ceil(canary_seconds*10)
    assert 1<=delay<=40, f'RTC inference delay exceeds prior chunk leftover: {delay}'
    previous=raw0.detach().squeeze(0)[10:20].clone()
    # The actual LeRobot RTC rollout truncates an original-action tail to its
    # 10-step execution horizon; do not use demonstration action values.
    second=pre(input_observation(z,1))
    evidence={'action_out_backward_hook_fires':0,'expert_backward_hook_fires':0,
              'action_out_forward_with_grad':0,'expert_forward_with_grad':0,
              'prefix_outputs_require_grad':[],'vjp_calls':0,'vjp_finite':True,
              'vjp_l2_norms':[]}
    def record_output(kind):
        def hook(_module,_args,output):
            tensor=first_tensor(output)
            if tensor is not None and tensor.requires_grad:
                evidence[f'{kind}_forward_with_grad']+=1
                tensor.register_hook(lambda grad: evidence.__setitem__(f'{kind}_backward_hook_fires',
                                             evidence[f'{kind}_backward_hook_fires']+1))
        return hook
    # LeRobot's expert wrapper calls submodules directly rather than invoking
    # the layer's forward(), so a hook on the layer object would never fire.
    expert_qproj=policy.model.vlm_with_expert.lm_expert.layers[0].self_attn.q_proj
    handles=[policy.model.action_out_proj.register_forward_hook(record_output('action_out')),
             expert_qproj.register_forward_hook(record_output('expert'))]
    orig_prefix=policy.model.embed_prefix
    def prefix_wrapper(*args,**kwargs):
        out=orig_prefix(*args,**kwargs)
        evidence['prefix_outputs_require_grad'].append(any(torch.is_tensor(x) and x.requires_grad for x in out))
        return out
    policy.model.embed_prefix=prefix_wrapper
    orig_grad=torch.autograd.grad
    def grad_wrapper(*args,**kwargs):
        out=orig_grad(*args,**kwargs)
        evidence['vjp_calls']+=1
        grad=out[0]
        evidence['vjp_finite']=evidence['vjp_finite'] and bool(torch.isfinite(grad).all())
        evidence['vjp_l2_norms'].append(float(torch.linalg.vector_norm(grad).item()))
        return out
    torch.autograd.grad=grad_wrapper
    try:
        raw1=policy.predict_action_chunk(second,noise=noise(rows[1]['noise_seed']),
            inference_delay=delay,prev_chunk_left_over=previous)
        committed1=post(raw1)
        torch.cuda.synchronize()
    finally:
        torch.autograd.grad=orig_grad
        policy.model.embed_prefix=orig_prefix
        for handle in handles:handle.remove()
    evidence.update({'status':'REAL_MODEL_FULL_VJP_GRAPH_CANARY_OBSERVED',
        'expert_hook_module':'vlm_with_expert.lm_expert.layers[0].self_attn.q_proj',
        'first_chunk_canary_seconds':canary_seconds,'inference_delay_frames':delay,
        'first_chunk_raw_shape':list(raw0.shape),'guided_chunk_raw_shape':list(raw1.shape),
        'first_chunk_commit_shape':list(committed0.shape),
        'guided_chunk_commit_shape':list(committed1.shape),
        'all_weights_frozen':all(not p.requires_grad for p in policy.parameters()),
        'parameter_grad_count':sum(p.grad is not None for p in policy.parameters()),
        'required_steps':config.num_steps,'checkpoint_sha256':sha(MODEL/'model.safetensors'),
        'rtc_source_sha256':sha(ROOT/'source/lerobot_repaired/src/lerobot/policies/rtc/modeling_rtc.py'),
        'torch':torch.__version__,'cuda_device_name':torch.cuda.get_device_name(0),
        'peak_allocated_bytes':torch.cuda.max_memory_allocated(0)})
    out=ROOT/'raw/f0/real_model_graph_canary.json'
    out.write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print(json.dumps(evidence,sort_keys=True))
    assert evidence['vjp_calls']==10
    assert evidence['action_out_backward_hook_fires']>=10
    assert evidence['expert_backward_hook_fires']>=10
    assert evidence['vjp_finite'] and evidence['parameter_grad_count']==0
    assert not any(evidence['prefix_outputs_require_grad'])
    assert torch.isfinite(raw1).all()

if __name__=='__main__':main()
