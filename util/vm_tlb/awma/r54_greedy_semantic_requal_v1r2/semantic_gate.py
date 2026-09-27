#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,traceback
from pathlib import Path
import torch
from transformers import Qwen3_5ForConditionalGeneration,KernelConfig

ROOT=Path('/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927')
MODEL=Path('/data/c16/awma/r54_checkpoint_lifecycle_20260927/model/Qwen3_5_0_8B_c6046cd1')

def config():
    return KernelConfig(kernel_mapping={
      'causal_conv1d_fn':('kernels-community/mamba-ssm:causal_conv1d_fn',{'revision':'20b2508ad12ae40260291539bf45183000451850'}),
      'causal_conv1d_update':('kernels-community/mamba-ssm:causal_conv1d_update',{'revision':'20b2508ad12ae40260291539bf45183000451850'}),
      'chunk_gated_delta_rule':('kernels-community/fla:chunk_gated_delta_rule',{'revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639'}),
      'fused_recurrent_gated_delta_rule':('kernels-community/fla:recurrent_gated_delta_rule',{'revision':'6d22ed1d2bb627375b6ca8fc135f7f417863e639'}),
    },inherit_mapping=False)

def thash(x):
    return hashlib.sha256(x.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()

def prefill(model,ids,chunk):
    cache=None;out=None
    for i in range(0,len(ids),chunk):
        part=torch.tensor([ids[i:i+chunk]],dtype=torch.long,device='cuda:0')
        out=model(input_ids=part,past_key_values=cache,use_cache=True,return_dict=True)
        cache=out.past_key_values
        if int(cache.get_seq_length())!=i+len(ids[i:i+chunk]):
            raise ValueError(f'Cache length after chunk at {i} invalid')
    assert out is not None
    return out

def recurrent_layers(cache):
    for i,layer in enumerate(cache.layers):
        if hasattr(layer,'recurrent_states'):
            yield i,layer

def take_snapshot(cache):
    bundle={}
    for i,layer in recurrent_layers(cache):
        assert layer.is_conv_states_initialized[0] and layer.is_recurrent_states_initialized[0]
        conv=layer.conv_states[0];rec=layer.recurrent_states[0]
        bundle[i]={
          'conv':torch.empty_like(conv),'recurrent':torch.empty_like(rec),
          'has_previous_state':layer.has_previous_state[0],
          'is_conv_states_initialized':layer.is_conv_states_initialized[0],
          'is_recurrent_states_initialized':layer.is_recurrent_states_initialized[0],
          'conv_kernel_size':layer.conv_kernel_size[0],
          'record_past':layer.record_past,
        }
        bundle[i]['conv'].copy_(conv);bundle[i]['recurrent'].copy_(rec)
    torch.cuda.synchronize()
    return bundle

def kv_hashes(cache):
    return {i:(thash(layer.keys),thash(layer.values)) for i,layer in enumerate(cache.layers) if hasattr(layer,'keys') and layer.keys is not None}

def restore_bundle(cache,bundle):
    for i,s in bundle.items():
        layer=cache.layers[i]
        layer.conv_states[0].copy_(s['conv'])
        layer.recurrent_states[0].copy_(s['recurrent'])
        layer.has_previous_state[0]=s['has_previous_state']
        layer.is_conv_states_initialized[0]=s['is_conv_states_initialized']
        layer.is_recurrent_states_initialized[0]=s['is_recurrent_states_initialized']
        layer.conv_kernel_size[0]=s['conv_kernel_size']
        layer.record_past=s['record_past']
    torch.cuda.synchronize()

def semantic(model, out, count=16):
    cache=out.past_key_values
    logits=out.logits[:,-1,:]
    first_logits=logits.detach().cpu()
    first_top=torch.topk(logits,8).indices[0].tolist()
    tokens=[]
    for i in range(count):
        if not torch.isfinite(logits).all().item():raise ValueError('nonfinite')
        t=int(logits.argmax());tokens.append(t)
        if i<count-1:
            out=model(input_ids=torch.tensor([[t]],dtype=torch.long,device='cuda:0'),
                      past_key_values=cache,use_cache=True,return_dict=True)
            cache=out.past_key_values;logits=out.logits[:,-1,:]
    torch.cuda.synchronize()
    return {'tokens':tokens,'tokens_sha256':hashlib.sha256(json.dumps(tokens,separators=(',',':')).encode()).hexdigest(),
      'top8':first_top,'top8_set':sorted(first_top),'top2':first_top[:2],
      'argmax':first_top[0],'cache_len':int(cache.get_seq_length()),
      'initial_logits_sha256':thash(first_logits)},first_logits

def main():
    result={'stage':'AWMA_R54_EXACT_RECURRENT_CHECKPOINT_LIFECYCLE_V1R2',
            'backend':'V1R1_HUB_GENERIC_FOUR_FUNCTIONS','status':'RUNNING'}
    try:
        model=Qwen3_5ForConditionalGeneration.from_pretrained(
            MODEL,local_files_only=True,dtype=torch.bfloat16,
            device_map={'':'cuda:0'},use_kernels=True,kernel_config=config()).eval()
        ids=json.loads((ROOT/'prefix/PREFIX_DISCOVERY_4096.json').read_text())
        with torch.inference_mode():
            ref=prefill(model,ids[:512],512)
            bundle=take_snapshot(ref.past_key_values)
            dest=prefill(model,ids[:512],512)
            dest_cache=dest.past_key_values
            kv_reference=kv_hashes(ref.past_key_values)
            kv_before=kv_hashes(dest_cache)
            alias=[]
            for i,s in bundle.items():
                layer=dest_cache.layers[i]
                alias.extend([layer.conv_states[0].data_ptr()==s['conv'].data_ptr(),
                              layer.recurrent_states[0].data_ptr()==s['recurrent'].data_ptr()])
                layer.conv_states[0].zero_();layer.recurrent_states[0].zero_()
                layer.has_previous_state[0]=False
            restore_bundle(dest_cache,bundle)
            copied=all(torch.equal(dest_cache.layers[i].conv_states[0],s['conv']) and
                       torch.equal(dest_cache.layers[i].recurrent_states[0],s['recurrent'])
                       for i,s in bundle.items())
            metadata=all(dest_cache.layers[i].has_previous_state[0]==s['has_previous_state'] and
                         dest_cache.layers[i].is_conv_states_initialized[0]==s['is_conv_states_initialized'] and
                         dest_cache.layers[i].is_recurrent_states_initialized[0]==s['is_recurrent_states_initialized'] and
                         dest_cache.layers[i].conv_kernel_size[0]==s['conv_kernel_size'] and
                         dest_cache.layers[i].record_past==s['record_past'] for i,s in bundle.items())
            kv_after=kv_hashes(dest_cache)
            ref_sem,ref_logits=semantic(model,ref)
            dest_sem,dest_logits=semantic(model,dest)
            diff=(ref_logits.float()-dest_logits.float()).abs()
            restore_pass=all([copied,metadata,kv_reference==kv_before==kv_after,not any(alias),
              ref_sem['argmax']==dest_sem['argmax'],ref_sem['top8_set']==dest_sem['top8_set'],
              ref_sem['top2']==dest_sem['top2'],ref_sem['tokens']==dest_sem['tokens'],
              ref_sem['cache_len']==dest_sem['cache_len']])
            result['restore_512']={'pass':restore_pass,'gdn_layers':len(bundle),
              'snapshot_bytes':sum(s['conv'].numel()*s['conv'].element_size()+s['recurrent'].numel()*s['recurrent'].element_size() for s in bundle.values()),
              'no_alias':not any(alias),'copy_exact':copied,'metadata_exact':metadata,
              'full_attention_kv_untouched':kv_before==kv_after,
              'full_attention_kv_equal_to_independent_reference':kv_reference==kv_before,
              'reference':ref_sem,'restored':dest_sem,
              'max_abs_logit_diff':float(diff.max()),'mean_abs_logit_diff':float(diff.mean())}
            if not restore_pass:
                result['status']='RESTORE_SEMANTICS_NOT_QUALIFIED'
            else:
                mono=prefill(model,ids,4096)
                chunk=prefill(model,ids,512)
                mono_sem,mono_logits=semantic(model,mono)
                chunk_sem,chunk_logits=semantic(model,chunk)
                diff=(mono_logits.float()-chunk_logits.float()).abs()
                m0p0_pass=all([mono_sem['argmax']==chunk_sem['argmax'],
                   mono_sem['top8_set']==chunk_sem['top8_set'],mono_sem['top2']==chunk_sem['top2'],
                   mono_sem['tokens']==chunk_sem['tokens'],mono_sem['cache_len']==chunk_sem['cache_len']])
                result['m0_p0_4096']={'pass':m0p0_pass,'monolithic':mono_sem,
                    'chunked512':chunk_sem,'max_abs_logit_diff':float(diff.max()),
                    'mean_abs_logit_diff':float(diff.mean()),
                    'same_selected':mono_sem['argmax']==chunk_sem['argmax'],
                    'same_top8_set':mono_sem['top8_set']==chunk_sem['top8_set'],
                    'same_top2_order':mono_sem['top2']==chunk_sem['top2'],
                    'same_16_token_continuation':mono_sem['tokens']==chunk_sem['tokens']}
                result['status']='SEMANTIC_GATES_PASS' if m0p0_pass else 'M0_P0_SEMANTICS_NOT_QUALIFIED'
    except Exception as exc:
        result['status']='ERROR';result['error']=repr(exc);result['traceback']=traceback.format_exc()
        raise
    finally:
        (ROOT/'R54_SEMANTIC_GATE_RECEIPT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'restore_512_pass':result.get('restore_512',{}).get('pass'),
                      'm0_p0_4096_pass':result.get('m0_p0_4096',{}).get('pass'),
                      'm0_p0_4096_top2_same':result.get('m0_p0_4096',{}).get('same_top2_order')},sort_keys=True))

if __name__=='__main__':main()
