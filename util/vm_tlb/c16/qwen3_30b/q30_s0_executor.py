#!/usr/bin/env python3
"""Exact Q30 S0 semantic streamer and whole-layer replay canary executor."""
import argparse, hashlib, io, json, os, sys, time
from pathlib import Path

import torch
from transformers import AutoConfig, DynamicCache
from transformers.models.qwen3_moe.modeling_qwen3_moe import Qwen3MoeForCausalLM
from util.vm_tlb.c16.qwen3_30b.materializer import Materializer
from util.vm_tlb.c16.qwen3_30b.state import freeze, validate

MODEL_ID='Qwen/Qwen3-30B-A3B'; REV='ad44e777bcd18fa416d9da3bd8f70d33ebb85d39'; LAYER=24
TOKEN_SHA='5800e1ffaa5546dd2d4331fff1c6687fe46e3b58fe95b1f768405244da3908d6'
RECEIPT_SHA='4b69d23ecce9925569b299c28af17de553f416730c9b57552b3f561dd12e05b6'

def fsha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8<<20),b''): h.update(b)
 return h.hexdigest()
def tsha(t):
 t=t.detach().contiguous().cpu(); h=hashlib.sha256(); h.update(repr((tuple(t.shape),str(t.dtype))).encode()); h.update(t.view(torch.uint8).numpy().tobytes()); return h.hexdigest()
def tinfo(t): return {'shape':list(t.shape),'dtype':str(t.dtype),'bytes':t.numel()*t.element_size(),'sha256':tsha(t)}
def serial(obj):
 b=io.BytesIO(); torch.save(obj,b); return b.getvalue()
def load_blob(p): return torch.load(p,map_location='cpu',weights_only=True)
def router(logits):
 cpu=logits.detach().cpu(); sel=torch.topk(torch.softmax(cpu.float(),dim=-1),8,dim=-1).indices
 return {'router_logits':tinfo(cpu),'selected_expert_ids':sel.tolist(),'selected_expert_ids_sha256':tsha(sel),'expert_token_counts':torch.bincount(sel.reshape(-1),minlength=cpu.shape[-1]).tolist()}
def cache_cpu(c): return {'key_cache':[x.detach().cpu().contiguous() for x in c.key_cache],'value_cache':[x.detach().cpu().contiguous() for x in c.value_cache],'seen_tokens':int(c.get_seq_length())}
def cache_cuda(s):
 c=DynamicCache(); c.key_cache=[x.to('cuda') for x in s['key_cache']]; c.value_cache=[x.to('cuda') for x in s['value_cache']]; c._seen_tokens=int(s['seen_tokens']); return c
def cache_layer(c,i):
 return {'key':tinfo(c.key_cache[i]),'value':tinfo(c.value_cache[i])} if len(c.key_cache)>i and c.key_cache[i].numel() else None

class Q30:
 def __init__(self,root):
  self.root=Path(root); self.config=AutoConfig.from_pretrained(self.root,local_files_only=True)
  with torch.device('meta'): self.model=Qwen3MoeForCausalLM(self.config)
  self.model=self.model.to(dtype=torch.bfloat16); self.model.eval()
  self.wmap=json.loads((self.root/'model.safetensors.index.json').read_text())['weight_map']
  if len(self.wmap)!=18867 or set(self.wmap)!=set(self.model.state_dict()): raise RuntimeError('canonical model/index closure invalid')
  self.mat=Materializer(self.root,self.wmap)
 def names(self,p): return sorted(n for n in self.wmap if n.startswith(p))
 def on(self,m,p):
  r=self.mat.inject(m,self.names(p),p); m.to('cuda'); return r
 def off(self,m): self.mat.release(m); torch.cuda.synchronize()
 def embed(self,ids):
  m=self.model.model.embed_tokens; self.on(m,'model.embed_tokens.')
  try: return m(ids.to('cuda'))
  finally: self.off(m)
 def next_token(self,h):
  norm=self.model.model.norm; head=self.model.lm_head; self.on(norm,'model.norm.'); self.on(head,'lm_head.')
  try: return int(torch.argmax(head(norm(h))[:,-1,:],dim=-1).item())
  finally: self.off(head); self.off(norm)
 def kwargs(self,h,am,c,cp):
  pi=cp.unsqueeze(0); causal=self.model.model._update_causal_mask(am,h,cp,c,False); pe=self.model.model.rotary_emb(h,pi)
  return {'attention_mask':causal,'position_ids':pi,'past_key_value':c,'output_attentions':False,'output_router_logits':True,'use_cache':True,'cache_position':cp,'position_embeddings':pe}
 def layer(self,i,h,k):
  m=self.model.model.layers[i]; torch.cuda.reset_peak_memory_stats(); before={'allocated':torch.cuda.memory_allocated(),'reserved':torch.cuda.memory_reserved()}; rec=self.on(m,'model.layers.%d.'%i)
  try:
   out=m(h,**k); torch.cuda.synchronize(); result=(out[0],out[-1],rec,before,{'allocated':torch.cuda.max_memory_allocated(),'reserved':torch.cuda.max_memory_reserved()})
  finally: self.off(m)
  post={'allocated':torch.cuda.memory_allocated(),'reserved':torch.cuda.memory_reserved()}; return (*result,post)

def boundary(h,k):
 return {'hidden_states':h.detach().cpu().contiguous(),'attention_mask':k['attention_mask'].detach().cpu().contiguous() if k['attention_mask'] is not None else None,'position_ids':k['position_ids'].detach().cpu().contiguous(),'cache_position':k['cache_position'].detach().cpu().contiguous(),'position_embeddings':tuple(x.detach().cpu().contiguous() for x in k['position_embeddings']),'past_cache':cache_cpu(k['past_key_value'])}
def thaw(b):
 return {'attention_mask':b['attention_mask'].to('cuda') if b['attention_mask'] is not None else None,'position_ids':b['position_ids'].to('cuda'),'past_key_value':cache_cuda(b['past_cache']),'output_attentions':False,'output_router_logits':True,'use_cache':True,'cache_position':b['cache_position'].to('cuda'),'position_embeddings':tuple(x.to('cuda') for x in b['position_embeddings'])}
def contract(b):
 out={'hidden_states':tinfo(b['hidden_states']),'position_ids':tinfo(b['position_ids']),'cache_position':tinfo(b['cache_position']),'position_embeddings':[tinfo(x) for x in b['position_embeddings']],'past_key_cache':[tinfo(x) for x in b['past_cache']['key_cache']],'past_value_cache':[tinfo(x) for x in b['past_cache']['value_cache']]}
 out['attention_mask']=tinfo(b['attention_mask']) if b['attention_mask'] is not None else None; return out
def diag(actual,expected):
 a=actual.float(); b=expected.float(); d=(a-b).abs(); neq=actual.ne(expected); idx=neq.nonzero(); return {'differing_elements':int(neq.sum()),'max_abs':float(d.max()),'max_rel':float((d/(b.abs()+1e-30)).max()),'first_mismatch':idx[0].tolist() if len(idx) else None}

def stream(a):
 if fsha(a.tokens)!=TOKEN_SHA or fsha(a.receipt)!=RECEIPT_SHA: raise RuntimeError('S0 authority SHA mismatch')
 ids=json.loads(Path(a.tokens).read_text());
 if len(ids)!=128: raise RuntimeError('S0 context must be exactly 128')
 run=Path(a.run_dir); sem=run/'semantic'; states=run/'target_states';
 if (sem/'SEMANTIC_RUN_RECEIPT.json').exists() or (states/'TARGET_LAYER_STATE_INDEX.json').exists(): raise FileExistsError(run)
 for d in (sem,states,run/'replay',run/'logs',run/'receipts'): d.mkdir(parents=True,exist_ok=True)
 q=Q30(a.model_root); c=DynamicCache(); layer_rows=[]; router_rows=[]; captures={}; decode=[]; start=time.time()
 def phase(name,tid,step=None):
  h=q.embed(tid); prior=c.get_seq_length(); cp=torch.arange(prior,prior+h.shape[1],device='cuda'); am=torch.ones((1,prior+h.shape[1]),device='cuda',dtype=torch.long); k=q.kwargs(h,am,c,cp)
  for i in range(48):
   key=('prefill' if name=='PREFILL' else 'decode3') if i==LAYER and (name=='PREFILL' or step==3) else None
   if key: b=boundary(h,k)
   out,rl,mat,before,peak,post=q.layer(i,h,k); rs=router(rl); cs=cache_layer(c,i)
   layer_rows.append({'phase':name,'decode_step':step,'layer_id':i,'input':tinfo(h),'output':tinfo(out),'materialized_tensor_count':mat['tensor_count'],'weight_bytes':mat['bytes'],'cache':cs,'gpu_before':before,'gpu_peak':peak,'gpu_post_release':post})
   router_rows.append({'phase':name,'decode_step':step,'layer_id':i,**rs})
   if key: captures[key]={'call':b,'source':{'output':out.detach().cpu().contiguous(),'router_logits':rl.detach().cpu().contiguous(),'router':rs}}
   h=out
  return q.next_token(h)
 with torch.inference_mode():
  nxt=phase('PREFILL',torch.tensor([ids],device='cuda',dtype=torch.long)); prefill_token=nxt
  for st in range(4):
   current=nxt; nxt=phase('DECODE',torch.tensor([[current]],device='cuda',dtype=torch.long),st); decode.append({'decode_step':st,'input_token_id':current,'next_token_id':nxt})
 if set(captures)!={'prefill','decode3'}: raise RuntimeError('fixed target capture missing')
 receipt={'schema_version':'Q30_S0_SEMANTIC_STREAM_V1','status':'Q30_SEMANTIC_STREAMING_S0_PASS','run_id':run.name,'scenario':'Q30_S0_TEXT','batch':1,'context':128,'decode_forwards':4,'decode_numbering':'zero-based; decode_step 0 is first forward after Prefill','prefill_next_token_id':prefill_token,'decode':decode,'model_id':MODEL_ID,'model_revision':REV,'working_copy_receipt_sha':a.copy_sha,'runtime_authority_sha':a.runtime_sha,'input_token_ids_sha':TOKEN_SHA,'input_receipt_sha':RECEIPT_SHA,'git_execution_commit':a.git_commit,'deployment_identity':a.deployment,'layers':layer_rows,'router':router_rows,'elapsed_seconds':time.time()-start}
 (sem/'SEMANTIC_RUN_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n'); srsha=fsha(sem/'SEMANTIC_RUN_RECEIPT.json')
 index=[]
 for key,cap in captures.items():
  phase_name='PREFILL' if key=='prefill' else 'DECODE'; step=None if key=='prefill' else 3; bundle=states/key
  manifest={'model_id':MODEL_ID,'model_revision':REV,'runtime_identity':a.runtime_sha,'working_copy_receipt_sha':a.copy_sha,'input_binding_sha':RECEIPT_SHA,'scenario':'Q30_S0_TEXT_B1_T128_D4','phase':phase_name,'layer_id':LAYER,'decode_step':step,'source_semantic_run_receipt_sha':srsha,'git_execution_commit':a.git_commit,'deployment_identity':a.deployment,'forward_tensor_contract':contract(cap['call']),'source_router_summary':cap['source']['router']}
  freeze(bundle,manifest,{'call_boundary.pt':serial(cap['call']),'source_oracle.pt':serial(cap['source'])}); m=validate(bundle,REV,LAYER)
  arts=[]
  for x in m['artifacts']: arts.append(x)
  index.append({'bundle':str(bundle),'manifest_sha256':fsha(bundle/'manifest.json'),'phase':phase_name,'decode_step':step,'layer_id':LAYER,'source_semantic_run_receipt_sha':srsha,'artifacts':arts,'forward_tensor_contract':manifest['forward_tensor_contract']})
 (states/'TARGET_LAYER_STATE_INDEX.json').write_text(json.dumps({'status':'Q30_TARGET_LAYER_STATE_PASS','run_id':run.name,'states':index},sort_keys=True,indent=2)+'\n')
 print(json.dumps({'status':'Q30_TARGET_LAYER_STATE_PASS','run_dir':str(run),'semantic_receipt_sha256':srsha,'target_state_index_sha256':fsha(states/'TARGET_LAYER_STATE_INDEX.json'),'prefill_next_token_id':prefill_token,'decode_next_token_ids':[x['next_token_id'] for x in decode]},sort_keys=True))

def replay(a):
 bundle=Path(a.bundle); m=validate(bundle,REV,LAYER); call=load_blob(bundle/'call_boundary.pt'); source=load_blob(bundle/'source_oracle.pt'); q=Q30(a.model_root)
 with torch.inference_mode():
  h=call['hidden_states'].to('cuda'); out,rl,mat,before,peak,post=q.layer(LAYER,h,thaw(call)); out=out.cpu(); rl=rl.cpu()
 out_eq=torch.equal(out,source['output']); router_eq=torch.equal(rl,source['router_logits']); rs=router(rl); rs_eq=rs==source['router']
 res={'bundle':str(bundle),'phase':m['phase'],'decode_step':m.get('decode_step'),'source_output':tinfo(source['output']),'replay_output':tinfo(out),'source_router':source['router'],'replay_router':rs,'output_shape_exact':tuple(out.shape)==tuple(source['output'].shape),'output_dtype_exact':out.dtype==source['output'].dtype,'output_bitwise_equal':out_eq,'router_bitwise_equal':router_eq,'router_summary_exact':rs_eq,'numeric_diagnostics':None if out_eq else diag(out,source['output']),'materialized_tensor_count':mat['tensor_count'],'weight_bytes':mat['bytes'],'gpu_before':before,'gpu_peak':peak,'gpu_post_release':post,'status':'PASS' if out_eq and router_eq and rs_eq else 'FAIL'}
 print(json.dumps(res,sort_keys=True));
 if res['status']!='PASS': sys.exit(2)

def main():
 p=argparse.ArgumentParser(); p.add_argument('--mode',choices=('stream','replay'),required=True); p.add_argument('--model-root',required=True); p.add_argument('--run-dir'); p.add_argument('--tokens'); p.add_argument('--receipt'); p.add_argument('--bundle'); p.add_argument('--copy-sha'); p.add_argument('--runtime-sha'); p.add_argument('--git-commit'); p.add_argument('--deployment')
 a=p.parse_args(); stream(a) if a.mode=='stream' else replay(a)
if __name__=='__main__': main()
