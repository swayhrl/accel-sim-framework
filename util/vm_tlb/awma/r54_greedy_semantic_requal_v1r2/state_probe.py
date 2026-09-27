#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
import torch
from transformers import Qwen3_5ForConditionalGeneration,KernelConfig

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
MODEL=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927/model/Qwen3_5_0_8B_c6046cd1')

config=KernelConfig(kernel_mapping={
 'causal_conv1d_fn':('kernels-community/mamba-ssm:causal_conv1d_fn',{'revision':'20b2508ad12ae40260291539bf45183000451850'}),
 'causal_conv1d_update':('kernels-community/mamba-ssm:causal_conv1d_update',{'revision':'20b2508ad12ae40260291539bf45183000451850'}),
 'chunk_gated_delta_rule':('kernels-community/fla:chunk_gated_delta_rule',{'revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639'}),
 'fused_recurrent_gated_delta_rule':('kernels-community/fla:recurrent_gated_delta_rule',{'revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639'}),
},inherit_mapping=False)

def sha_tensor(t):
    return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()

def flatten(prefix,value):
    if isinstance(value,dict):
        for k,v in value.items():yield from flatten(f'{prefix}[{k!r}]',v)
    elif isinstance(value,(list,tuple)):
        for k,v in enumerate(value):yield from flatten(f'{prefix}[{k}]',v)
    else:
        yield prefix,value

def cls(path):
    if "['keys']" in path:return 'FULL_ATTN_K'
    if "['values']" in path:return 'FULL_ATTN_V'
    if 'conv_states' in path and not 'is_conv' in path:return 'GDN_CONV'
    if 'recurrent_states' in path and not 'is_recurrent' in path:return 'GDN_RECURRENT'
    if 'has_previous_state' in path or 'is_conv_states_initialized' in path or 'is_recurrent_states_initialized' in path or "['is_initialized']" in path:return 'INIT_FLAG'
    if 'record_past' in path:return 'INIT_FLAG'
    if 'conv_kernel_size' in path:return 'POSITION_OR_LENGTH'
    if '_seq' in path or 'length' in path or '_seen' in path:return 'POSITION_OR_LENGTH'
    if 'number_of_states' in path or "['dtype']" in path or "['device']" in path:return 'STATIC_CONFIG'
    return 'CACHE_CONTROL'

def snapshot(cache):
    result={}
    for k,v in flatten('cache',cache.__dict__):
        if k.startswith("cache['layers']"):continue
        result[k]=v
    for i,layer in enumerate(cache.layers):
        for k,v in flatten(f'cache.layers[{i}]',layer.__dict__):result[k]=v
    return result

def main():
    model=Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL,local_files_only=True,dtype=torch.bfloat16,
        device_map={'':'cuda:0'},use_kernels=True,kernel_config=config).eval()
    ids=json.loads((ROOT/'prefix/PREFIX_DISCOVERY_4096.json').read_text())[:512]
    with torch.inference_mode():
        out=model(input_ids=torch.tensor([ids],device='cuda:0'),use_cache=True,return_dict=True)
        cache=out.past_key_values
        torch.cuda.synchronize()
        first=snapshot(cache)
        before={k:(int(v.data_ptr()),sha_tensor(v)) for k,v in first.items() if isinstance(v,torch.Tensor)}
        next_token=int(out.logits[:,-1,:].argmax())
        out2=model(input_ids=torch.tensor([[next_token]],device='cuda:0'),past_key_values=cache,use_cache=True,return_dict=True)
        torch.cuda.synchronize()
        second=snapshot(out2.past_key_values)
    rows=[]
    for path,value in first.items():
        layer_num=int(path.split('cache.layers[')[1].split(']')[0]) if path.startswith('cache.layers[') else ''
        layer_type=model.config.text_config.layer_types[layer_num] if layer_num!='' else 'GLOBAL'
        state_class=cls(path)
        is_tensor=isinstance(value,torch.Tensor)
        after=second.get(path)
        if is_tensor:
            logical=int(value.numel()*value.element_size())
            storage=int(value.untyped_storage().nbytes())
            after_ptr=int(after.data_ptr()) if isinstance(after,torch.Tensor) else None
            after_hash=sha_tensor(after) if isinstance(after,torch.Tensor) else None
            before_ptr,before_hash=before[path]
            changed=before_hash!=after_hash
            inplace=before_ptr==after_ptr
            shape=str(tuple(value.shape));dtype=str(value.dtype);device=str(value.device)
            val='TENSOR'
        else:
            logical=storage=0;before_ptr=after_ptr=None;changed=value!=after
            inplace='NA';shape=dtype=device='';val=repr(value)[:100]
        required='YES' if state_class in ('GDN_CONV','GDN_RECURRENT','FULL_ATTN_K','FULL_ATTN_V','INIT_FLAG','POSITION_OR_LENGTH') else 'NO_STATIC_OR_RUNTIME_CONTROL'
        include='YES' if state_class in ('GDN_CONV','GDN_RECURRENT') else 'NO_SEPARATE_PREFIX_KV' if layer_type=='full_attention' and state_class=='INIT_FLAG' else 'METADATA' if state_class in ('INIT_FLAG','POSITION_OR_LENGTH') else 'NO_SEPARATE_PREFIX_KV' if state_class in ('FULL_ATTN_K','FULL_ATTN_V') else 'NO'
        anchor='cache_utils.py:1029-1118 / modeling_qwen3_5.py:574-653' if state_class.startswith('GDN_') else 'cache_utils.py:114-212 / modeling_qwen3_5.py attention forward' if state_class.startswith('FULL_') else 'cache_utils.py:905-1120'
        rows.append({'layer_index':layer_num,'layer_type':layer_type,'field_path':path,
          'value_or_kind':val,'tensor_shape':shape,'dtype':dtype,'device':device,
          'logical_bytes':logical,'storage_bytes':storage,
          'changed_after_one_decode':changed,'same_storage_pointer_after_one_decode':inplace,
          'exact_continuation_required':required,'state_class':state_class,
          'recurrent_snapshot_inclusion':include,'source_anchor':anchor})
    with (ROOT/'R54_EXACT_STATE_SCHEMA.tsv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n')
        w.writeheader();w.writerows(rows)
    summary={'cache_class':type(cache).__name__,'layer_count':len(cache.layers),
      'cache_length_after_prefix':512,'cache_length_after_one_decode':int(cache.get_seq_length()),
      'gdn_layer_count':sum(t=='linear_attention' for t in model.config.text_config.layer_types),
      'attention_layer_count':sum(t=='full_attention' for t in model.config.text_config.layer_types),
      'classes':{},'total_recurrent_snapshot_bytes':0,
      'unresolved_fields':[r['field_path'] for r in rows if r['exact_continuation_required']=='REVIEW'],
      'source_commit':'96331a9f93b72697f160a958d2883d4b49a56739'}
    for r in rows:
        c=r['state_class'];summary['classes'][c]=summary['classes'].get(c,0)+1
        if c in ('GDN_CONV','GDN_RECURRENT'):summary['total_recurrent_snapshot_bytes']+=r['logical_bytes']
    (ROOT/'R54_STATE_PROBE_RECEIPT.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))

if __name__=='__main__':main()
