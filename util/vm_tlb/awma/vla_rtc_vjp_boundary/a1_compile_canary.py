#!/usr/bin/env python3
"""One preregistered author-supported torch.compile A1 canary; no formal timing."""
import json
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

from a0_reference import ROOT, MODEL, BASE, RAW, windows, run_sequence, sha

def load_compiled():
    torch.set_num_threads(8)
    cfg=SmolVLAConfig.from_pretrained(str(MODEL))
    cfg.device='cuda:0';cfg.load_vlm_weights=False;cfg.vlm_model_name=str(BASE)
    cfg.rtc_config=RTCConfig(enabled=True,mode='guided',
        prefix_attention_schedule=RTCAttentionSchedule.LINEAR,
        max_guidance_weight=10.0,execution_horizon=10,debug=False)
    cfg.compile_model=True
    assert cfg.compile_mode=='max-autotune'
    policy=SmolVLAPolicy.from_pretrained(str(MODEL),config=cfg,strict=True,local_files_only=True)
    policy.requires_grad_(False)
    pre,post=make_pre_post_processors(cfg,pretrained_path=str(MODEL),
        preprocessor_overrides={'tokenizer_processor':{'tokenizer_name':str(BASE)},
                                'device_processor':{'device':'cuda:0'}},
        postprocessor_overrides={'device_processor':{'device':'cpu'}})
    return cfg,policy,pre,post

def compare(a,b):
    assert a.shape==b.shape
    a=a.detach().cpu();b=b.detach().cpu()
    atol,rtol=(1e-5,1e-4) if a.dtype==torch.float32 else (1e-3,1e-2)
    return {'dtype':str(a.dtype),'max_abs':float((a-b).abs().max()),
            'max_rel':float(((a-b).abs()/(b.abs()+1e-12)).max()),
            'allclose':bool(torch.allclose(a,b,atol=atol,rtol=rtol)),
            'atol':atol,'rtol':rtol}

def main():
    assert os.environ.get('VLA_GPU_LOCK_HELD')=='1' and os.environ.get('HF_HUB_OFFLINE')=='1'
    graph=json.loads((ROOT/'raw/f0/real_model_graph_canary.json').read_text())
    delay=graph['inference_delay_frames'];assert delay==4
    fixture=torch.load(RAW/'a0_discovery_reference_outputs.pt',map_location='cpu',weights_only=True)
    rows=windows();z=np.load(ROOT/'raw/f1/discovery_observations.npz',allow_pickle=False)
    cfg,policy,pre,post=load_compiled()
    start=time.perf_counter()
    raw,committed,first_call_times=run_sequence(policy,pre,post,z,rows,delay,True)
    compilation_plus_first_sequence_seconds=time.perf_counter()-start
    results=[]
    for i in range(4):
        results.append({'window':i,'raw':compare(raw[i],fixture['raw_actions'][i]),
                        'committed':compare(committed[i],fixture['committed_actions'][i])})
    plain_pass=all(x['raw']['allclose'] and x['committed']['allclose'] for x in results)
    trajectory_checks=[]
    if plain_pass:
        captured=[]
        rtc=policy.rtc_processor
        old_track=rtc.track;old_debug=rtc.is_debug_enabled
        def capture(**kw):
            item={'step_record_index':len(captured) if len(captured)<10 else (len(captured)-10)%20}
            for key in ('time','x_t','v_t','x1_t','correction','err','weights'):
                value=kw.get(key)
                if torch.is_tensor(value):item[key]=value.detach().cpu().clone()
                elif value is not None:item[key]=value
            captured.append(item)
        rtc.track=capture;rtc.is_debug_enabled=lambda:True
        try:
            run_sequence(policy,pre,post,z,rows,delay,False)
        finally:
            rtc.track=old_track;rtc.is_debug_enabled=old_debug
        assert len(captured)==70, len(captured)
        for window in (1,2,3):
            ref=torch.load(RAW/f'a0_guided_window{window}_trajectory.pt',map_location='cpu',weights_only=True)
            expected=ref['records']
            actual=captured[10+20*(window-1):10+20*window]
            assert len(expected)==len(actual)==20
            checks=[]
            for step,(a,b) in enumerate(zip(actual,expected)):
                assert set(a)==set(b),(window,step,set(a),set(b))
                for key in a:
                    if torch.is_tensor(a[key]):
                        checks.append({'step_record':step,'key':key,**compare(a[key],b[key])})
                    elif key=='time':
                        checks.append({'step_record':step,'key':key,'allclose':a[key]==b[key],
                                       'max_abs':abs(float(a[key])-float(b[key]))})
            trajectory_checks.append({'window':window,'tensor_checks':checks,
                                      'passed':all(x['allclose'] for x in checks)})
    trajectory_pass=plain_pass and len(trajectory_checks)==3 and all(x['passed'] for x in trajectory_checks)
    receipt={'status':'COMPILE_CANARY_TRAJECTORY_PASS' if trajectory_pass else 'COMPILE_NUMERIC_NOT_QUALIFIED',
        'compile_mode':cfg.compile_mode,'compile_enabled':cfg.compile_model,
        'first_sequence_including_compilation_seconds':compilation_plus_first_sequence_seconds,
        'first_call_window_ms':first_call_times,
        'numeric_results':results,'plain_numeric_pass':plain_pass,
        'trajectory_results':trajectory_checks,'trajectory_pass':trajectory_pass,
        'checkpoint_sha256':sha(MODEL/'model.safetensors'),
        'reference_outputs_sha256':sha(RAW/'a0_discovery_reference_outputs.pt'),
        'parameter_grad_count':sum(p.grad is not None for p in policy.parameters())}
    out=ROOT/'raw/f4/a1_compile_canary.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))
    if not trajectory_pass:raise SystemExit(2)

if __name__=='__main__':main()
