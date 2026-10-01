#!/usr/bin/env python3
"""Capture one natural Qwen2.5 MLP projection input/weight under GPU lock."""
import hashlib
import json
import os
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM

OLD=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
NEW=Path('/data/c16/awma/r19_fp8_readiness_20261001')
TARGET='model.layers.0.mlp.up_proj'
WEIGHT_SHA='fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe'
TOKEN_SHA='179439d64cb3ba775457854c336633a21d066eceb67a8ad8bfeb99ca78f5208d'

def sha_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):
            h.update(b)
    return h.hexdigest()

def sha_tensor(t):
    b=t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(b).hexdigest()

def main():
    assert os.environ.get('R19_GPU_LOCK_HELD')=='1'
    assert sha_file(MODEL/'model.safetensors')==WEIGHT_SHA
    input_receipt=json.loads((OLD/'R101_INPUT_RECEIPT.json').read_text())
    tokens=json.loads((OLD/'raw/TRAIN_DISCOVERY_256.json').read_text())
    assert len(tokens)==256
    assert hashlib.sha256(json.dumps(tokens,separators=(',',':'),sort_keys=True).encode()).hexdigest()==TOKEN_SHA
    assert input_receipt['parts']['TRAIN_DISCOVERY_256']['token_ids_json_sha256']==TOKEN_SHA
    model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,
        torch_dtype=torch.bfloat16,attn_implementation='sdpa').eval().to('cuda:0')
    modules=dict(model.named_modules())
    assert TARGET in modules
    module=modules[TARGET]
    captured=[]
    def hook(_module,inputs):
        x=inputs[0]
        assert x.device.type=='cuda' and x.dtype==torch.bfloat16
        captured.append(x.detach().cpu().contiguous())
    handle=module.register_forward_pre_hook(hook)
    input_ids=torch.tensor(tokens,dtype=torch.long,device='cuda:0').unsqueeze(0)
    with torch.no_grad():
        logits=model(input_ids=input_ids,use_cache=False,return_dict=True).logits
    torch.cuda.synchronize();handle.remove()
    assert len(captured)==1
    x=captured[0]
    weight=module.weight.detach().cpu().contiguous()
    assert x.ndim==3 and x.shape[0]==1 and x.shape[1]==256
    assert weight.ndim==2 and x.shape[2]==weight.shape[1]
    assert x.shape[1]%16==0 and x.shape[2]%16==0 and weight.shape[0]%16==0
    assert torch.isfinite(x).all() and torch.isfinite(weight).all() and torch.isfinite(logits).all()
    out=NEW/'raw/QWEN25_LAYER0_UP_PROJ_REAL_INPUT_WEIGHT.pt'
    out.parent.mkdir(parents=True,exist_ok=True)
    torch.save({'input':x,'weight':weight,'tokens':tokens,'target':TARGET},out)
    receipt={'stage':'AWMA_R19_FP8_READINESS_109_V1','input_class':'ACCEPTED_R101_TRAIN_DISCOVERY_256_REAL_QWEN_FORWARD',
        'model':'Qwen/Qwen2.5-0.5B-Instruct','model_revision':'7ae557604adf67be50417f59c2c2f167def9a775',
        'model_weight_sha256':WEIGHT_SHA,'token_ids_sha256':TOKEN_SHA,
        'accepted_token_json_file_sha256':sha_file(OLD/'raw/TRAIN_DISCOVERY_256.json'),
        'target_module':TARGET,'hook_count':len(captured),
        'input_shape':list(x.shape),'weight_shape':list(weight.shape),
        'input_dtype':str(x.dtype),'weight_dtype':str(weight.dtype),
        'input_tensor_sha256':sha_tensor(x),'weight_tensor_sha256':sha_tensor(weight),
        'input_max_abs':float(x.abs().max()),'weight_max_abs':float(weight.abs().max()),
        'GEMM_MNK':[x.shape[0]*x.shape[1],weight.shape[0],x.shape[2]],
        'TE_alignment_MNK_multiple_16':True,
        'logits_shape':list(logits.shape),'source_forward_eval_no_grad':True,
        'payload_path':str(out),'payload_sha256':sha_file(out),'payload_bytes':out.stat().st_size,
        'torch':torch.__version__,'torch_cuda':torch.version.cuda,
        'GPU':torch.cuda.get_device_name(0),'peak_allocated_bytes':torch.cuda.max_memory_allocated(0)}
    (NEW/'raw/REAL_PROJECTION_INPUT_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
