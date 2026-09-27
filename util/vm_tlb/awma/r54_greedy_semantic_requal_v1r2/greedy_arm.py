#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import traceback
from pathlib import Path

import torch
from transformers import KernelConfig, Qwen3_5ForConditionalGeneration

ROOT = Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
V1 = Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927')
MODEL = V1/'model/Qwen3_5_0_8B_c6046cd1'
EXPECTED_WEIGHT = '04b1c301231dd422b8860db31311ab2721511346a32cb1e079c4c4e5f1fe4696'
MAMBA_REV = '20b2508ad12ae40260291539bf45183000451850'
FLA_REV = '6d22ed1d2bb627375b6ca8fc135f7f417863e639'

def sha_tensor(t: torch.Tensor) -> str:
    return hashlib.sha256(t.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()

def cache_length(cache):
    if cache is None:
        return None
    if hasattr(cache,'get_seq_length'):
        return int(cache.get_seq_length())
    return None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prefix',choices=['S0','PREFIX_HOLDOUT_2048','PREFIX_DISCOVERY_4096'],required=True)
    parser.add_argument('--arm',choices=['F','H'],required=True)
    args=parser.parse_args()

    raw=ROOT/'raw'/args.prefix/args.arm
    raw.mkdir(parents=True,exist_ok=True)
    receipt=json.loads((ROOT/'R54_V1R2_PREFIX_RECEIPT.json').read_text())
    ids=json.loads((ROOT/'prefix'/f'{args.prefix}.json').read_text())
    ids_cpu=torch.tensor([ids],dtype=torch.long)
    if sha_tensor(ids_cpu)!=receipt['prefixes'][args.prefix]['token_ids_sha256']:
        raise ValueError('Frozen input token SHA mismatch')
    assert len(ids) in [64,2048,4096]
    import kernels, transformers
    if torch.__version__!='2.14.0+cu130' or kernels.__version__!='0.17.0' or transformers.__version__!='5.18.0.dev0':
        raise ValueError('V1R1 backend package identity mismatch')
    config=None
    if args.arm=='H':
        config=KernelConfig(kernel_mapping={
            'causal_conv1d_fn':('kernels-community/mamba-ssm:causal_conv1d_fn',{'revision':MAMBA_REV}),
            'causal_conv1d_update':('kernels-community/mamba-ssm:causal_conv1d_update',{'revision':MAMBA_REV}),
            'chunk_gated_delta_rule':('kernels-community/fla:chunk_gated_delta_rule',{'revision':FLA_REV}),
            'fused_recurrent_gated_delta_rule':('kernels-community/fla:recurrent_gated_delta_rule',{'revision':FLA_REV}),
        },inherit_mapping=False)
    record={
        'stage':'AWMA_R54_GREEDY_SEMANTIC_REQUALIFICATION_V1R2',
        'prefix':args.prefix,'arm':args.arm,'input_token_sha256':sha_tensor(ids_cpu),
        'prefix_len':len(ids),'model_revision':'c6046cd1f7e2763bf1abf5a5aef6ad7878e10ccb',
        'model_weight_sha256':EXPECTED_WEIGHT,'transformers_commit':'96331a9f93b72697f160a958d2883d4b49a56739',
        'torch':torch.__version__,'torch_cuda':torch.version.cuda,
        'kernels':kernels.__version__,'mamba_revision':MAMBA_REV,'fla_revision':FLA_REV,
        'use_kernels':args.arm=='H','backend_mapping':'V1R1_EXACT_GDN_FOUR_FUNCTIONS',
        'gpu':torch.cuda.get_device_name(0),'capability':list(torch.cuda.get_device_capability(0)),
        'eos_token_id':int(receipt['eos_token_id']),'steps':[],
    }
    try:
        model=Qwen3_5ForConditionalGeneration.from_pretrained(
            MODEL,local_files_only=True,dtype=torch.bfloat16,
            device_map={'':'cuda:0'},use_kernels=(args.arm=='H'),kernel_config=config,
        ).eval()
        if bool(model.use_kernels)!=(args.arm=='H'):
            raise ValueError('Runtime use_kernels selection mismatch')
        logits_list=[]
        generated=[]
        eos_position=None
        cache_lengths=[]
        with torch.inference_mode():
            torch.cuda.nvtx.range_push(f'R54_V1R2_{args.prefix}_{args.arm}_PREFILL')
            output=model(input_ids=ids_cpu.to('cuda:0'),use_cache=True,return_dict=True)
            torch.cuda.nvtx.range_pop()
            cache=output.past_key_values
            logits=output.logits[:,-1,:].detach()
            for i in range(64):
                if logits.shape!=(1,248320):
                    raise ValueError(f'Bad logits shape {tuple(logits.shape)} at step {i}')
                if not torch.isfinite(logits).all().item():
                    raise ValueError(f'Nonfinite logits at step {i}')
                top_values,top_indices=torch.topk(logits,8,dim=-1)
                top_ids=[int(v) for v in top_indices[0].tolist()]
                selected=top_ids[0]
                clen=cache_length(cache)
                expected=len(ids)+i
                cache_lengths.append(clen)
                if clen is not None and clen!=expected:
                    raise ValueError(f'Cache length {clen} != expected {expected} at step {i}')
                record['steps'].append({
                    'step':i,'selected_token_id':selected,'top2_ids':top_ids[:2],
                    'top8_ordered_ids':top_ids,'top8_set_ids':sorted(top_ids),
                    'selected_logit':float(top_values[0,0]),
                    'second_logit':float(top_values[0,1]),
                    'margin':float(top_values[0,0]-top_values[0,1]),
                    'cache_seq_length_before_selection':clen,
                })
                logits_list.append(logits.cpu())
                generated.append(selected)
                if selected==record['eos_token_id']:
                    eos_position=i
                    break
                if i<63:
                    one=torch.tensor([[selected]],dtype=torch.long,device='cuda:0')
                    torch.cuda.nvtx.range_push(f'R54_V1R2_{args.prefix}_{args.arm}_DECODE_{i+1:02d}')
                    output=model(input_ids=one,past_key_values=cache,use_cache=True,return_dict=True)
                    torch.cuda.nvtx.range_pop()
                    cache=output.past_key_values
                    logits=output.logits[:,-1,:].detach()
        torch.cuda.synchronize()
        all_logits=torch.cat(logits_list,dim=0)
        torch.save(all_logits,raw/'logits_bf16.pt')
        record['logits_shape']=list(all_logits.shape)
        record['logits_sha256']=sha_tensor(all_logits)
        record['generated_token_ids']=generated
        record['generated_token_ids_sha256']=hashlib.sha256(json.dumps(generated,separators=(',',':')).encode()).hexdigest()
        record['continuation_length']=len(generated)
        record['eos_position_zero_based']=eos_position
        record['stop_reason']='EOS' if eos_position is not None else 'MAX_64'
        record['cache_seq_length_before_last_selection']=cache_lengths[-1]
        record['cache_length_progression_valid']=all(x==len(ids)+i for i,x in enumerate(cache_lengths))
        record['finite']=True
        record['status']='ARM_COMPLETE'
    except Exception as exc:
        record['status']='ARM_FAILED'
        record['error']=repr(exc)
        record['traceback']=traceback.format_exc()
        raise
    finally:
        (raw/'ARM_RECEIPT.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:record[k] for k in ['prefix','arm','status','continuation_length','stop_reason','eos_position_zero_based','generated_token_ids_sha256','cache_length_progression_valid']}))

if __name__=='__main__':main()
