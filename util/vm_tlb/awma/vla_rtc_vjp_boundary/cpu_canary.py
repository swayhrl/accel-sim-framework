#!/usr/bin/env python3
"""CPU analytic VJP canary around exact pinned LeRobot RTC source module."""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import sys
import types
from enum import Enum
from pathlib import Path

import torch

class RTCAttentionSchedule(Enum):
    ZEROS='zeros'; ONES='ones'; LINEAR='linear'; EXP='exp'

def install_import_stubs():
    for name in ('lerobot','lerobot.policies','lerobot.policies.rtc'):
        module=types.ModuleType(name); module.__path__=[]; sys.modules[name]=module
    configs=types.ModuleType('lerobot.configs')
    configs.RTCAttentionSchedule=RTCAttentionSchedule
    sys.modules['lerobot.configs']=configs
    rtc_config=types.ModuleType('lerobot.policies.rtc.configuration_rtc')
    rtc_config.RTCConfig=object
    sys.modules[rtc_config.__name__]=rtc_config
    debug=types.ModuleType('lerobot.policies.rtc.debug_tracker')
    debug.Tracker=object
    sys.modules[debug.__name__]=debug

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--variant',choices=('upstream','repaired'),required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    install_import_stubs()
    name='lerobot.policies.rtc.modeling_rtc'
    spec=importlib.util.spec_from_file_location(name,args.source)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    RTCProcessor=module.RTCProcessor
    config=types.SimpleNamespace(enabled=True,mode='guided',debug=False,
        prefix_attention_schedule=RTCAttentionSchedule.ONES,
        max_guidance_weight=10.0,execution_horizon=8)
    rows=[]
    for shape in ((8,3),(1,8,3),(2,8,5)):
        for t in (0.2,0.5,0.8):
            processor=RTCProcessor(config)
            observed={}
            processor.track=lambda **kw: observed.update(kw)
            x=torch.arange(1,1+int(torch.tensor(shape).prod()),dtype=torch.float64).reshape(shape)/100
            prev=torch.full(shape,0.3,dtype=torch.float64)
            # Public predict_action_chunk runs under no_grad; RTC must re-enable
            # gradient only for this action-latent VJP.
            with torch.no_grad():
                result=processor.denoise_step(x_t=x,prev_chunk_left_over=prev,
                    inference_delay=3,time=t,
                    original_denoise_step_partial=lambda z:2*z,
                    execution_horizon=8)
            correction=observed['correction']
            error=observed['err']
            expected=(1-2*t)*error
            max_err=float((correction-expected).abs().max())
            identity_err=float((correction-error).abs().max())
            nonzero=bool(torch.count_nonzero(error).item())
            assert nonzero and torch.isfinite(result).all()
            rows.append({'variant':args.variant,'shape':str(shape),'t':t,
                'source_sha256':sha(args.source),'max_abs_vjp_error_vs_full_jacobian':f'{max_err:.17g}',
                'max_abs_vjp_error_vs_identity_only':f'{identity_err:.17g}',
                'expected_factor':f'{1-2*t:.17g}',
                'full_jacobian_pass':max_err<1e-12,
                'identity_only_pass':identity_err<1e-12,
                'outer_no_grad':True,'error_nonzero':nonzero})
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        writer.writeheader();writer.writerows(rows)
    print(json.dumps({'variant':args.variant,'source_sha256':sha(args.source),
        'full_jacobian_passes':sum(x['full_jacobian_pass'] for x in rows),
        'identity_only_passes':sum(x['identity_only_pass'] for x in rows),
        'cases':len(rows)},sort_keys=True))

if __name__=='__main__':main()
