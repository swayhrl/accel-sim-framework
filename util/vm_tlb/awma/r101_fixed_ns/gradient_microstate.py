#!/usr/bin/env python3
from __future__ import annotations
import argparse,gc,hashlib,json,traceback
from pathlib import Path

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM
from himuon.optimizers.himuon import HiMuon

ROOT=Path('/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
ROLES=['self_attn.q_proj.weight','mlp.up_proj.weight','mlp.down_proj.weight']

def sha_tensor(t):
    return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()

def main(which):
    fixture='TRAIN_DISCOVERY_256' if which=='discovery' else 'TRAIN_HOLDOUT_256'
    layer=0 if which=='discovery' else 12
    input_receipt=json.loads((ROOT/'R101_INPUT_RECEIPT.json').read_text())
    tokens=json.loads((ROOT/'raw'/f'{fixture}.json').read_text())
    assert len(tokens)==256
    assert hashlib.sha256(json.dumps(tokens,separators=(',',':'),sort_keys=True).encode()).hexdigest()==input_receipt['parts'][fixture]['token_ids_json_sha256']
    names=[f'model.layers.{layer}.{role}' for role in ROLES]
    receipt={'stage':'AWMA_R101_FIXED_NS_INTERMEDIATE_LIFECYCLE_V1',
      'microstate_class':'REAL_MODEL_FIRST_STEP_GRADIENT_DERIVED_MICROSTATE',
      'fixture':fixture,'input_ids_sha256':input_receipt['parts'][fixture]['token_ids_json_sha256'],
      'model_revision':'7ae557604adf67be50417f59c2c2f167def9a775',
      'model_weight_sha256':'fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe',
      'gradient_step':1,'optimizer_update_applied':False,
      'next_token_loss':{'input':'tokens[:-1]','labels':'tokens[1:]','reduction':'mean','label_smoothing':0.0},
      'momentum':0.95,'nesterov':True,'initial_momentum_zero':True,
      'parameter_names':names,'status':'RUNNING','parameters':{}}
    out=ROOT/'raw'/f'{which}_gradient_microstate.pt'
    try:
        torch.manual_seed(0)
        model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,
          torch_dtype=torch.bfloat16,attn_implementation='sdpa').train().to('cuda:0')
        named=dict(model.named_parameters())
        if not all(name in named for name in names):
            raise ValueError(f'Exact target names unavailable: {names}; candidates={list(named)[:12]}')
        selected=[named[name] for name in names]
        before={name:sha_tensor(named[name].data) for name in names}
        model.zero_grad(set_to_none=True)
        inputs=torch.tensor(tokens[:-1],dtype=torch.long,device='cuda:0').unsqueeze(0)
        labels=torch.tensor(tokens[1:],dtype=torch.long,device='cuda:0')
        outputs=model(input_ids=inputs,use_cache=False,return_dict=True)
        logits=outputs.logits.squeeze(0)
        loss=F.cross_entropy(logits.float(),labels,reduction='mean',label_smoothing=0.0)
        if not torch.isfinite(loss):raise ValueError('nonfinite loss')
        receipt['loss_fp32']=float(loss.detach().cpu())
        receipt['logits_shape']=list(logits.shape)
        loss.backward()
        opt=HiMuon(selected,momentum=0.95,nesterov=True,tile_size=512,ns_steps=5,cuda_graph=False)
        data={}
        for name,p in zip(names,selected):
            if p.grad is None:raise ValueError(f'missing gradient {name}')
            grad=p.grad.detach()
            if grad.dtype!=torch.bfloat16 or grad.ndim!=2 or not torch.isfinite(grad).all():
                raise ValueError(f'invalid gradient {name} {grad.dtype} {tuple(grad.shape)}')
            ns_input=opt._compute_momentum(p,grad,0.95,True).detach()
            buf=opt.state[p]['momentum_buffer'].detach()
            if not torch.equal(buf,grad):raise ValueError(f'first-step momentum buffer not equal gradient {name}')
            if not torch.isfinite(ns_input).all():raise ValueError(f'nonfinite NS input {name}')
            fp32_ideal=grad.float()*1.95
            param_record={'shape':list(grad.shape),'dtype':str(grad.dtype),
              'gradient_sha256':sha_tensor(grad),'momentum_buffer_sha256':sha_tensor(buf),
              'nesterov_input_sha256':sha_tensor(ns_input),
              'gradient_norm_fp32':float(torch.linalg.vector_norm(grad.float())),
              'nesterov_input_norm_fp32':float(torch.linalg.vector_norm(ns_input.float())),
              'author_bf16_vs_ideal_fp32_max_abs':float((ns_input.float()-fp32_ideal).abs().max()),
              'nesterov_input_finite':True}
            data[name]={'grad':grad.cpu().contiguous(),
                        'momentum_buffer':buf.cpu().contiguous(),
                        'nesterov_input':ns_input.cpu().contiguous()}
            receipt['parameters'][name]=param_record
        after={name:sha_tensor(named[name].data) for name in names}
        receipt['parameter_weights_unchanged']=before==after
        if before!=after:raise ValueError('parameter changed without optimizer step')
        torch.save(data,out)
        receipt['payload_sha256']=hashlib.sha256(out.read_bytes()).hexdigest()
        receipt['payload_size_bytes']=out.stat().st_size
        receipt['torch']=torch.__version__
        receipt['torch_cuda']=torch.version.cuda
        receipt['gpu']=torch.cuda.get_device_name(0)
        receipt['peak_allocated_bytes']=torch.cuda.max_memory_allocated()
        receipt['status']='MICROSTATE_COMPLETE'
    except Exception as exc:
        receipt['status']='MICROSTATE_FAILED'
        receipt['error']=repr(exc)
        receipt['traceback']=traceback.format_exc()
        raise
    finally:
        (ROOT/f'R101_GRADIENT_MICROSTATE_RECEIPT_{which.upper()}.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        if torch.cuda.is_initialized():torch.cuda.synchronize()
        gc.collect()
        if torch.cuda.is_initialized():torch.cuda.empty_cache()
    print(json.dumps({'fixture':fixture,'status':receipt['status'],'loss_fp32':receipt.get('loss_fp32'),
      'parameter_shapes':{k:v['shape'] for k,v in receipt['parameters'].items()},
      'payload_sha256':receipt.get('payload_sha256')},sort_keys=True))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--which',choices=['discovery','holdout'],required=True)
    main(parser.parse_args().which)
