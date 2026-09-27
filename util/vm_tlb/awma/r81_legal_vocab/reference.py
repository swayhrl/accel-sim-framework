#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,time,traceback
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
import xgrammar as xgr
from transformers import AutoModelForCausalLM,AutoTokenizer
from test_masks import unpack_mask

ROOT=Path('/data/c16/awma/r81_legal_vocab_20260927')
MODEL=Path('/data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775')
VOCAB=151936

def sha_bytes(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def canonical(value)->bytes:return json.dumps(value,separators=(',',':'),sort_keys=True).encode()

def load_rows(cohort):
    rows=json.loads((ROOT/'raw/fixture/requests.json').read_text())
    selected=[r for r in rows if r['cohort']==cohort]
    if len(selected)!=4:raise ValueError(f'expected B4 for {cohort}')
    return selected

def make_matchers(rows):
    info=xgr.TokenizerInfo.deserialize_json((ROOT/'raw/fixture/tokenizer_info.json').read_text())
    matchers=[]
    for r in rows:
        sid=r['schema_sha256']
        compiled=xgr.CompiledGrammar.deserialize_json((ROOT/'raw/compiled_grammar'/f'{sid}.json').read_text(),info)
        matchers.append(xgr.GrammarMatcher(compiled))
    return matchers

def batch_inputs(rows,pad_id,device):
    length=max(r['input_token_count'] for r in rows)
    ids=[];attention=[]
    for r in rows:
        pad=length-len(r['input_ids'])
        ids.append([pad_id]*pad+r['input_ids'])
        attention.append([0]*pad+[1]*len(r['input_ids']))
    return torch.tensor(ids,dtype=torch.long,device=device),torch.tensor(attention,dtype=torch.long,device=device)

@torch.inference_mode()
def fill_masks(matchers,done,mask):
    mask.zero_()
    start=time.perf_counter_ns()
    for i,m in enumerate(matchers):
        if not done[i]:m.fill_next_token_bitmask(mask,i)
    elapsed_ms=(time.perf_counter_ns()-start)/1e6
    legal=unpack_mask(mask,VOCAB)
    active=[i for i in range(4) if not done[i]]
    legal_ids=[np.flatnonzero(legal[i]).astype(np.int32,copy=False) for i in range(4)]
    if any(len(legal_ids[i])==0 for i in active):
        raise RuntimeError(f'EMPTY_LEGAL_SUPPORT active={active}')
    return legal_ids,elapsed_ms

def select_dense_vendor(hidden,weight,bitmask,legal_ids,done):
    selected=[None]*4;scores=[None]*4
    rows=[i for i in range(4) if not done[i] and len(legal_ids[i])>1]
    for i in range(4):
        if not done[i] and len(legal_ids[i])==1:
            selected[i]=int(legal_ids[i][0]);scores[i]=None
    if rows:
        subhidden=hidden[rows]
        logits=F.linear(subhidden,weight)
        submask=bitmask[rows].contiguous().to(logits.device)
        xgr.apply_token_bitmask_inplace(logits,submask,vocab_size=VOCAB,backend='cuda')
        indices=torch.argmax(logits,dim=-1)
        winners=indices.tolist()
        winner_scores=logits[torch.arange(len(rows),device=logits.device),indices].float().tolist()
        for k,i in enumerate(rows):
            if not np.isin(winners[k],legal_ids[i]):raise ValueError('selected illegal token')
            if not np.isfinite(winner_scores[k]):raise ValueError('selected legal logit nonfinite')
            selected[i]=int(winners[k]);scores[i]=float(winner_scores[k])
    return selected,scores,rows

def run(cohort):
    rows=load_rows(cohort)
    tok=AutoTokenizer.from_pretrained(MODEL,local_files_only=True,padding_side='left')
    model=AutoModelForCausalLM.from_pretrained(MODEL,local_files_only=True,
        torch_dtype=torch.bfloat16,attn_implementation='sdpa').eval().to('cuda:0')
    assert model.get_output_embeddings().weight.data_ptr()==model.model.embed_tokens.weight.data_ptr()
    assert tuple(model.get_output_embeddings().weight.shape)==(VOCAB,896)
    assert model.get_output_embeddings().weight.dtype==torch.bfloat16
    matchers=make_matchers(rows)
    input_ids,attention_mask=batch_inputs(rows,tok.pad_token_id,'cuda:0')
    done=[False]*4;stop_reasons=[None]*4;generated=[[] for _ in range(4)]
    hidden_rows=[];mask_rows=[];ledger=[]
    cache=None
    outdir=ROOT/'raw/reference'/cohort
    outdir.mkdir(parents=True,exist_ok=True)
    try:
        with torch.inference_mode():
            for step in range(128):
                out=model.model(input_ids=input_ids,attention_mask=attention_mask,
                    past_key_values=cache,use_cache=True,return_dict=True)
                cache=out.past_key_values
                hidden=out.last_hidden_state[:,-1,:].contiguous()
                mask=xgr.allocate_token_bitmask(4,VOCAB)
                legal_ids,grammar_ms=fill_masks(matchers,done,mask)
                head_start=time.perf_counter_ns()
                selected,scores,head_rows=select_dense_vendor(hidden,model.get_output_embeddings().weight,
                                                               mask,legal_ids,done)
                torch.cuda.synchronize()
                head_region_ms=(time.perf_counter_ns()-head_start)/1e6
                active=[i for i in range(4) if not done[i]]
                union=sorted(set().union(*(set(legal_ids[i].tolist()) for i in active))) if active else []
                summary={
                    'cohort':cohort,'step':step,
                    'previous_token_ids':[list(v) for v in generated],
                    'active_request_ids':[rows[i]['request_id'] for i in active],
                    'legal_counts':[len(v) for v in legal_ids],
                    'legal_union_count':len(union),
                    'legal_sum_count':sum(len(legal_ids[i]) for i in active),
                    'logical_shared_union_rows':len(active)*len(union),
                    'logical_ragged_rows':sum(len(legal_ids[i]) for i in active),
                    'singleton_request_count':sum(len(legal_ids[i])==1 for i in active),
                    'head_invoked_rows':head_rows,
                    'grammar_fill_ms_diagnostic':grammar_ms,
                    'dense_head_region_ms_diagnostic':head_region_ms,
                    'mask_sha256':sha_bytes(mask.numpy().tobytes()),
                    'hidden_sha256':sha_bytes(hidden.cpu().view(torch.uint8).numpy().tobytes()),
                    'selected_token_ids':selected,
                    'selected_legal_logits':scores,
                }
                hidden_rows.append(hidden.cpu());mask_rows.append(mask.clone())
                next_ids=[];next_attn=[]
                for i in range(4):
                    if done[i]:
                        next_ids.append(tok.pad_token_id);next_attn.append(0);continue
                    token=selected[i]
                    if token is None:raise RuntimeError('active row without selected token')
                    if not matchers[i].accept_token(token):raise ValueError(f'grammar rejected selected token {i}/{step}/{token}')
                    generated[i].append(token)
                    terminated=matchers[i].is_terminated()
                    eos=token==tok.eos_token_id
                    if eos or terminated:
                        done[i]=True;stop_reasons[i]='EOS' if eos else 'GRAMMAR_TERMINATED'
                    next_ids.append(token if not done[i] else tok.pad_token_id)
                    next_attn.append(0 if done[i] else 1)
                ledger.append(summary)
                if all(done):break
                input_ids=torch.tensor(next_ids,dtype=torch.long,device='cuda:0').view(4,1)
                attention_mask=torch.cat([attention_mask,torch.tensor(next_attn,dtype=torch.long,device='cuda:0').view(4,1)],dim=1)
        for i in range(4):
            if not done[i]:stop_reasons[i]='MAX_128_TRUNCATED'
        final=[]
        for i,r in enumerate(rows):
            text=tok.decode(generated[i],skip_special_tokens=True)
            parse_ok=False
            try:json.loads(text);parse_ok=True
            except Exception:pass
            final.append({'request_id':r['request_id'],'schema_sha256':r['schema_sha256'],
              'input_ids_sha256':r['input_ids_sha256'],
              'generated_token_ids':generated[i],
              'generated_token_ids_sha256':sha_bytes(canonical(generated[i])),
              'generated_text':text,'generated_count':len(generated[i]),
              'stop_reason':stop_reasons[i],'grammar_terminated':matchers[i].is_terminated(),
              'json_parseable':parse_ok})
        torch.save(torch.stack(hidden_rows),outdir/'hidden_bf16.pt')
        torch.save(torch.stack(mask_rows),outdir/'token_bitmask_int32.pt')
        (outdir/'STEP_LEDGER.json').write_text(json.dumps(ledger,indent=2,sort_keys=True)+'\n')
        (outdir/'REQUEST_RESULTS.json').write_text(json.dumps(final,indent=2,sort_keys=True)+'\n')
        receipt={'cohort':cohort,'status':'REFERENCE_COMPLETE','steps':len(ledger),
          'model_weight_sha256':'fdf756fa7fcbe7404d5c60e26bff1a0c8b8aa1f72ced49e7dd0210fe288fb7fe',
          'dtype':'torch.bfloat16','head_shape':[VOCAB,896],
          'head_weight_tied_to_embedding':True,
          'hidden_tensor_sha256':sha_bytes((outdir/'hidden_bf16.pt').read_bytes()),
          'mask_tensor_sha256':sha_bytes((outdir/'token_bitmask_int32.pt').read_bytes()),
          'step_ledger_sha256':sha_bytes((outdir/'STEP_LEDGER.json').read_bytes()),
          'request_results_sha256':sha_bytes((outdir/'REQUEST_RESULTS.json').read_bytes()),
          'stop_reasons':stop_reasons,'generated_counts':[len(v) for v in generated]}
        (outdir/'REFERENCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
        print(json.dumps({'cohort':cohort,'steps':len(ledger),
          'generated_counts':receipt['generated_counts'],'stop_reasons':stop_reasons,
          'first_step_legal_counts':ledger[0]['legal_counts'],
          'first_step_union':ledger[0]['legal_union_count']},sort_keys=True))
    except Exception as exc:
        (outdir/'REFERENCE_FAILURE.json').write_text(json.dumps({'cohort':cohort,'error':repr(exc),
             'traceback':traceback.format_exc()},indent=2)+'\n')
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--cohort',choices=['C0_SHARED_DISCOVERY','C1_HETEROGENEOUS_DISCOVERY','H0_HETEROGENEOUS_HOLDOUT'],required=True)
    run(p.parse_args().cohort)
