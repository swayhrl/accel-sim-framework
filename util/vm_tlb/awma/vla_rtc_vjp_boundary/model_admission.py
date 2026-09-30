#!/usr/bin/env python3
"""CPU-only strict SmolVLA checkpoint/processor admission with pinned local assets."""
import hashlib
import json
import os
from pathlib import Path

import torch
from transformers import AutoProcessor, AutoTokenizer
from lerobot.configs import RTCAttentionSchedule
from lerobot.policies.rtc.configuration_rtc import RTCConfig
from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.factory import make_pre_post_processors

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
MODEL=ROOT/'assets/model'
BASE=ROOT/'assets/base_vlm'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def main():
    assert os.environ.get('HF_HUB_OFFLINE')=='1'
    assert sha(MODEL/'model.safetensors')=='9a9f6413e42c0f332fccbce9a0dc796af2790f82cf002f791cdbf7e01e1afca8'
    torch.set_num_threads(8)
    config=SmolVLAConfig.from_pretrained(str(MODEL))
    original_config=json.loads((MODEL/'config.json').read_text())
    assert config.chunk_size==50 and config.num_steps==10 and not config.use_amp
    config.device='cpu'
    config.load_vlm_weights=False  # strict full checkpoint supplies every weight
    config.vlm_model_name=str(BASE) # same pinned config/processor/tokenizer, no remote weights
    config.rtc_config=RTCConfig(enabled=True,mode='guided',
        prefix_attention_schedule=RTCAttentionSchedule.LINEAR,
        max_guidance_weight=10.0,execution_horizon=10,debug=False)
    policy=SmolVLAPolicy.from_pretrained(str(MODEL),config=config,strict=True,local_files_only=True)
    policy.requires_grad_(False)
    tokenizer=AutoTokenizer.from_pretrained(str(BASE),local_files_only=True)
    processor=AutoProcessor.from_pretrained(str(BASE),local_files_only=True)
    pre,post=make_pre_post_processors(config,pretrained_path=str(MODEL),
        preprocessor_overrides={'tokenizer_processor':{'tokenizer_name':str(BASE)},
                                'device_processor':{'device':'cpu'}},
        postprocessor_overrides={'device_processor':{'device':'cpu'}})
    assert len(list(policy.parameters()))>0
    assert all(not p.requires_grad for p in policy.parameters())
    receipt={'status':'STRICT_LOAD_AND_PROCESSOR_SUCCESS','device':'cpu',
        'parameter_tensors':len(list(policy.parameters())),
        'parameter_count':sum(p.numel() for p in policy.parameters()),
        'torch_version':torch.__version__,'tokenizer_class':type(tokenizer).__name__,
        'processor_class':type(processor).__name__,
        'preprocessor_steps':[type(x).__name__ for x in pre.steps],
        'postprocessor_steps':[type(x).__name__ for x in post.steps],
        'checkpoint_sha256':sha(MODEL/'model.safetensors'),
        'checkpoint_config_vlm_id':original_config['vlm_model_name'],
        'runtime_vlm_config_processor_path':str(BASE),
        'base_vlm_weights_downloaded':False,
        'weight_load_strict':True,'all_weights_frozen':True,
        'rtc_repair_source_sha256':sha(ROOT/'source/lerobot_repaired/src/lerobot/policies/rtc/modeling_rtc.py')}
    out=ROOT/'raw/f1/model_admission_cpu.json'
    out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
