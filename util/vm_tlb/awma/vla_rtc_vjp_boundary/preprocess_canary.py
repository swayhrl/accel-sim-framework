#!/usr/bin/env python3
"""CPU-only exact pretrained processor canary on sealed A episode frame 0."""
import hashlib
import json
from pathlib import Path

import numpy as np
import torch
from lerobot.policies.factory import make_pre_post_processors
from lerobot.policies.smolvla.configuration_smolvla import SmolVLAConfig

ROOT=Path('/data/c16/awma/vla_rtc_vjp_boundary_20260930')
MODEL=ROOT/'assets/model'
BASE=ROOT/'assets/base_vlm'

def main():
    config=SmolVLAConfig.from_pretrained(str(MODEL))
    config.device='cpu'
    pre,_=make_pre_post_processors(config,pretrained_path=str(MODEL),
        preprocessor_overrides={'tokenizer_processor':{'tokenizer_name':str(BASE)},
                                'device_processor':{'device':'cpu'}},
        postprocessor_overrides={'device_processor':{'device':'cpu'}})
    with np.load(ROOT/'raw/f1/discovery_observations.npz',allow_pickle=False) as z:
        assert z['frame_index'].tolist()==[0,10,20,30]
        def image(name):
            return torch.from_numpy(z[name][0].copy()).permute(2,0,1).float().div(255)
        obs={'observation.images.image':image('image1_rgb'),
             'observation.images.image2':image('image2_rgb'),
             'observation.state':torch.from_numpy(z['state'][0].copy()),
             'task':str(z['task_text'][0])}
    batch=pre(obs)
    receipt={k:{'shape':list(v.shape),'dtype':str(v.dtype),'device':str(v.device),
        'sha256':hashlib.sha256(v.detach().contiguous().numpy().tobytes()).hexdigest()}
        for k,v in batch.items() if torch.is_tensor(v)}
    assert tuple(batch['observation.state'].shape)==(1,8)
    assert all(v.device.type=='cpu' for v in batch.values() if torch.is_tensor(v))
    path=ROOT/'raw/f1/preprocess_cpu_receipt.json'
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
