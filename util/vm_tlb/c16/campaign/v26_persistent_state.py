import gc,hashlib,json,sys,time,os
from pathlib import Path
import torch
from safetensors import safe_open
from transformers import AutoConfig,AutoModelForCausalLM
from transformers.cache_utils import DynamicCache

ROOT=Path('/data/c16/models/.incoming/deepseek_v2_lite/604d5664dddd88a0433dbae533b7fe9472482de0')
PAYLOAD=Path('/data/c16/deepseek_v23/authority/deepseek-v2-lite__S2_TEXT.json')
OUT=Path('/data/c16/deepseek_v26/state');OUT.mkdir(parents=True,exist_ok=True)
def sha_file(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def tsha(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
def info(t):return {'shape':list(t.shape),'dtype':str(t.dtype),'stride':list(t.stride()),'bytes':t.numel()*t.element_size(),'sha256':tsha(t)}
def ginfo(t):
 s=t.untyped_storage();return {**info(t),'data_ptr_hex':hex(t.data_ptr()),'storage_ptr_hex':hex(s.data_ptr()),'storage_bytes':s.nbytes()}
cfg=AutoConfig.from_pretrained(ROOT,trust_remote_code=True,local_files_only=True)
with torch.device('meta'):model=AutoModelForCausalLM.from_config(cfg,trust_remote_code=True)
model=model.to(dtype=torch.bfloat16).eval();wmap=json.loads((ROOT/'model.safetensors.index.json').read_text())['weight_map']
if set(wmap)!=set(model.state_dict()):raise RuntimeError('model/index keyset mismatch')
layer_cls=type(model.model.layers[0]);norm_cls=type(model.model.norm);attn_cls=type(model.model.layers[0].self_attn);gate_cls=type(model.model.layers[1].mlp.gate);expert_cls=type(model.model.layers[1].mlp.experts[0])
def load(names):
 out={}
 for shard in sorted({wmap[n] for n in names}):
  with safe_open(ROOT/shard,framework='pt',device='cpu') as f:
   for n in names:
    if wmap[n]==shard:out[n]=f.get_tensor(n)
 if set(out)!=set(names):raise RuntimeError('incomplete load')
 return out
def on(module,prefix):
 names=[n for n in wmap if n.startswith(prefix)];vals=load(names);local={n[len(prefix):]:v for n,v in vals.items()};expected=module.state_dict()
 if set(local)!=set(expected):raise RuntimeError('module key mismatch '+prefix)
 for n,v in local.items():
  if tuple(v.shape)!=tuple(expected[n].shape) or v.dtype!=expected[n].dtype:raise RuntimeError('shape/dtype '+prefix+n)
 module.load_state_dict(local,strict=True,assign=True);module.to('cuda');return {'tensor_count':len(local),'weight_bytes':sum(x.numel()*x.element_size() for x in local.values())}
def off(module):module.to_empty(device='meta');torch.cuda.empty_cache();gc.collect()
def run_layer(i,h,cache,mask,pos):
 if cfg.n_routed_experts is not None and i>=cfg.first_k_dense_replace and i%cfg.moe_layer_freq==0:return run_moe_layer(i,h,cache,mask,pos)
 layer=layer_cls(cfg,i).to(dtype=torch.bfloat16);rec=on(layer,f'model.layers.{i}.')
 try:
  out=layer(h,attention_mask=mask,position_ids=pos,past_key_value=cache,output_attentions=False,use_cache=True)[0];torch.cuda.synchronize();return out,rec
 finally:off(layer)
def run_moe_layer(i,h,cache,mask,pos,capture=False):
 rec={'tensor_count':0,'weight_bytes':0}
 def use(module,prefix):
  x=on(module,prefix);rec['tensor_count']+=x['tensor_count'];rec['weight_bytes']+=x['weight_bytes'];return module
 norm1=norm_cls(cfg.hidden_size,eps=cfg.rms_norm_eps).to(dtype=torch.bfloat16);use(norm1,f'model.layers.{i}.input_layernorm.');
 try:hn=norm1(h)
 finally:off(norm1)
 attn=attn_cls(cfg,i).to(dtype=torch.bfloat16);use(attn,f'model.layers.{i}.self_attn.');
 try:a=attn(hn,attention_mask=mask,position_ids=pos,past_key_value=cache,output_attentions=False,use_cache=True)[0]
 finally:off(attn)
 identity=h+a;norm2=norm_cls(cfg.hidden_size,eps=cfg.rms_norm_eps).to(dtype=torch.bfloat16);use(norm2,f'model.layers.{i}.post_attention_layernorm.');
 try:x=norm2(identity)
 finally:off(norm2)
 gate=gate_cls(cfg).to(dtype=torch.bfloat16);use(gate,f'model.layers.{i}.mlp.gate.');
 try:
  top_ids,top_weight,_=gate(x);logits=torch.nn.functional.linear(x.view(-1,x.shape[-1]).float(),gate.weight.float()).detach().cpu().contiguous()
 finally:off(gate)
 flat=x.view(-1,x.shape[-1]);counts=top_ids.new_zeros((top_ids.shape[0],cfg.n_routed_experts));counts.scatter_(1,top_ids,1);per=counts.sum(dim=0).cpu().numpy();idxs=top_ids.view(-1).argsort();sorted_tokens=flat[idxs//top_ids.shape[1]];outputs=[];chosen=int(top_ids[0,0]) if capture else None;captured=None;start=0
 for e,n in enumerate(per):
  end=start+int(n)
  if n:
   expert=expert_cls(cfg,intermediate_size=cfg.moe_intermediate_size).to(dtype=torch.bfloat16);use(expert,f'model.layers.{i}.mlp.experts.{e}.')
   hook=None
   if capture and e==chosen:
    def dp(_m,args):
     if os.environ.get('C16_V23R1_NVTX')=='1':torch.cuda.nvtx.range_push('C16_V23R1_MOE_EXPERT_DOWN_INCONTEXT')
    def dh(_m,args,out):
     nonlocal captured;captured={'input':args[0].detach().cpu().contiguous(),'output':out.detach().cpu().contiguous()}
     if os.environ.get('C16_V23R1_NVTX')=='1':torch.cuda.nvtx.range_pop()
    pre=expert.down_proj.register_forward_pre_hook(dp);hook=expert.down_proj.register_forward_hook(dh)
   try:outputs.append(expert(sorted_tokens[start:end]))
   finally:
    if hook:hook.remove();pre.remove()
    off(expert)
  start=end
 outs=torch.cat(outputs,dim=0) if outputs else sorted_tokens.new_empty(0);new=torch.empty_like(outs);new[idxs]=outs;y=(new.view(*top_ids.shape,-1).type(top_weight.dtype).mul_(top_weight.unsqueeze(-1)).sum(dim=1).type(new.dtype))
 if cfg.n_shared_experts is not None:
  shared=expert_cls(cfg,intermediate_size=cfg.moe_intermediate_size*cfg.n_shared_experts).to(dtype=torch.bfloat16);use(shared,f'model.layers.{i}.mlp.shared_experts.')
  try:y=y+shared(identity)
  finally:off(shared)
 if capture:
  if captured is None:raise RuntimeError('selected natural expert did not execute')
  moe.update({'gate_input':x.detach().cpu().contiguous(),'topk_ids':top_ids.detach().cpu().contiguous(),'topk_weight':top_weight.detach().cpu().contiguous(),'router_logits':logits,'selected_down':captured})
 torch.cuda.synchronize();return identity+y,rec
ids=json.loads(PAYLOAD.read_text())['token_ids'][0]
if sha_file(PAYLOAD)!='2ca11cff95f13bcdd0efcb3f5b2d6c0b8f7e30c9e67492d6b291362c09ff6935' or len(ids)!=2048:raise RuntimeError('input authority mismatch')
emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,cfg.pad_token_id,dtype=torch.bfloat16);on(emb,'model.embed_tokens.')
try:h=emb(torch.tensor([ids],device='cuda',dtype=torch.long))
finally:off(emb)
cache=DynamicCache();module=sys.modules[type(model).__module__];maskfn=module._prepare_4d_causal_attention_mask
layer_rows=[];start=time.time()
with torch.inference_mode():
 for i in range(cfg.num_hidden_layers):
  pos=torch.arange(h.shape[1],device='cuda').unsqueeze(0);mask=maskfn(None,(1,h.shape[1]),h,0);h,rec=run_layer(i,h,cache,mask,pos);layer_rows.append({'phase':'PREFILL','layer':i,'output':info(h),'materialized':rec,'cache_length':cache.get_seq_length()})
 norm=norm_cls(cfg.hidden_size,eps=cfg.rms_norm_eps).to(dtype=torch.bfloat16);head=torch.nn.Linear(cfg.hidden_size,cfg.vocab_size,bias=False,dtype=torch.bfloat16);on(norm,'model.norm.');on(head,'lm_head.')
 try:nxt=int(torch.argmax(head(norm(h))[:,-1,:],dim=-1).item())
 finally:off(head);off(norm)
 emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,cfg.pad_token_id,dtype=torch.bfloat16);on(emb,'model.embed_tokens.')
 try:h=emb(torch.tensor([[nxt]],device='cuda',dtype=torch.long))
 finally:off(emb)
 pos=torch.tensor([[2048]],device='cuda');mask=torch.zeros((1,1,1,2049),device='cuda',dtype=h.dtype)
 # Persistent MLA decode audit: exact layer-0 cache-before/update/cache-after and core operands.
def cpair():return {'key':cache.key_cache[0].detach().cpu().contiguous(),'value':cache.value_cache[0].detach().cpu().contiguous()}
cache_before_1=cpair();cache_meta_before_1={k:ginfo(v) for k,v in cache.key_cache[:1] and {'key':cache.key_cache[0],'value':cache.value_cache[0]}.items()};persistent={};persistent_meta={};old_matmul=torch.matmul
def observed_matmul(a,b,*args,**kwargs):
 isq=len(a.shape)==4 and len(b.shape)==4 and a.shape[-2]==1 and b.shape[-2]==a.shape[-1] and b.shape[-1]>a.shape[-1]
 if isq and os.environ.get('C16_V26_NVTX')=='1':torch.cuda.nvtx.range_push('C16_V26_MIXED_PERSISTENT_QK_INCONTEXT')
 out=old_matmul(a,b,*args,**kwargs)
 if isq and os.environ.get('C16_V26_NVTX')=='1':torch.cuda.nvtx.range_pop()
 if len(a.shape)==4 and len(b.shape)==4 and a.shape[-2]==1:
  if b.shape[-2]==a.shape[-1] and b.shape[-1]>a.shape[-1]:persistent['qk']={'query':a.detach().cpu().contiguous(),'key_transposed':b.detach().cpu().contiguous(),'output':out.detach().cpu().contiguous()};persistent_meta['qk']={'query':ginfo(a),'key_transposed':ginfo(b),'output':ginfo(out)}
  elif b.shape[-2]==a.shape[-1] and b.shape[-1]==cfg.v_head_dim:persistent['av']={'weights':a.detach().cpu().contiguous(),'value':b.detach().cpu().contiguous(),'output':out.detach().cpu().contiguous()};persistent_meta['av']={'weights':ginfo(a),'value':ginfo(b),'output':ginfo(out)}
 return out
torch.matmul=observed_matmul
 # MLA: capture exact kv_b expansion input/output in true layer-0 first decode.
l0=layer_cls(cfg,0).to(dtype=torch.bfloat16);on(l0,'model.layers.0.');mla={}
def kvb_pre(_m,args):
 if os.environ.get('C16_V23R1_NVTX')=='1':torch.cuda.nvtx.range_push('C16_V23R1_MLA_KV_B_INCONTEXT')
def kvb_hook(_m,args,out):
 mla.update({'input':args[0].detach().cpu().contiguous(),'output':out.detach().cpu().contiguous()})
 if os.environ.get('C16_V23R1_NVTX')=='1':torch.cuda.nvtx.range_pop()
prehook=l0.self_attn.kv_b_proj.register_forward_pre_hook(kvb_pre);hook=l0.self_attn.kv_b_proj.register_forward_hook(kvb_hook)
try:
 with torch.inference_mode():h=l0(h,attention_mask=mask,position_ids=pos,past_key_value=cache,output_attentions=False,use_cache=True)[0];torch.cuda.synchronize()
finally:
 hook.remove();prehook.remove();torch.matmul=old_matmul;off(l0)
cache_after_1=cpair();cache_meta_after_1={k:ginfo(v) for k,v in {'key':cache.key_cache[0],'value':cache.value_cache[0]}.items()}
if not mla:raise RuntimeError('MLA kv_b capture absent')
# MoE: exact native moe_infer algebra with one real selected expert materialized at a time.
moe_layer=next(i for i,x in enumerate(model.model.layers) if x.mlp.__class__.__name__=='DeepseekV2MoE');moe={}
with torch.inference_mode():h,moe_rec=run_moe_layer(moe_layer,h,cache,mask,pos,capture=True)
flat_ids=moe['topk_ids'].reshape(-1,moe['topk_ids'].shape[-1]);flat_weights=moe['topk_weight'].reshape(-1,moe['topk_weight'].shape[-1]);selected=int(flat_ids[0,0]);selected_slot=int((flat_ids[0]==selected).nonzero()[0,0]);
for i in range(moe_layer+1,cfg.num_hidden_layers):
 h,rec=run_layer(i,h,cache,mask,pos);layer_rows.append({'phase':'DECODE','layer':i,'output':info(h),'materialized':rec,'cache_length':cache.get_seq_length()})
norm=norm_cls(cfg.hidden_size,eps=cfg.rms_norm_eps).to(dtype=torch.bfloat16);head=torch.nn.Linear(cfg.hidden_size,cfg.vocab_size,bias=False,dtype=torch.bfloat16);on(norm,'model.norm.');on(head,'lm_head.')
try:decode_next=int(torch.argmax(head(norm(h))[:,-1,:],dim=-1).item())
finally:off(head);off(norm)
emb=torch.nn.Embedding(cfg.vocab_size,cfg.hidden_size,cfg.pad_token_id,dtype=torch.bfloat16);on(emb,'model.embed_tokens.')
try:h2=emb(torch.tensor([[decode_next]],device='cuda',dtype=torch.long))
finally:off(emb)
cache_before_2=cpair();cache_meta_before_2={k:ginfo(v) for k,v in {'key':cache.key_cache[0],'value':cache.value_cache[0]}.items()};l2=layer_cls(cfg,0).to(dtype=torch.bfloat16);on(l2,'model.layers.0.')
try:
 with torch.inference_mode():l2(h2,attention_mask=torch.zeros((1,1,1,2050),device='cuda',dtype=h2.dtype),position_ids=torch.tensor([[2049]],device='cuda'),past_key_value=cache,output_attentions=False,use_cache=True)[0];torch.cuda.synchronize()
finally:off(l2)
cache_after_2=cpair();cache_meta_after_2={k:ginfo(v) for k,v in {'key':cache.key_cache[0],'value':cache.value_cache[0]}.items()}
mla_state={'input':mla['input'],'output':mla['output']};moe_state={'selected_expert_id':selected,'selected_route_weight':flat_weights[0,selected_slot],'router_logits':moe['router_logits'],'topk_ids':moe['topk_ids'],'topk_weight':moe['topk_weight'],'down_input':moe['selected_down']['input'],'down_output':moe['selected_down']['output']}
torch.save(mla_state,OUT/'MLA_TARGET_STATE.pt');torch.save(moe_state,OUT/'MOE_TARGET_STATE.pt')
r_persist={'cache_before_decode1':cache_before_1,'cache_after_decode1':cache_after_1,'cache_before_decode2':cache_before_2,'cache_after_decode2':cache_after_2,'qk':persistent.get('qk'),'av':persistent.get('av')};torch.save(r_persist,OUT/'PERSISTENT_MLA_STATE.pt')
r={'schema_version':1,'status':'PASS','model_id':'deepseek-ai/DeepSeek-V2-Lite','revision':'604d5664dddd88a0433dbae533b7fe9472482de0','scenario':'S2_TEXT','payload_sha256':sha_file(PAYLOAD),'token_count':len(ids),'first_decode_input_token':nxt,'first_decode_next_token':decode_next,'cache_type':str(type(cache)),'cache_length':cache.get_seq_length(),'moe_layer':moe_layer,'natural_topk_ids':moe['topk_ids'].tolist(),'natural_topk_weights':moe['topk_weight'].tolist(),'selected_expert_id':selected,'selected_route_weight':float(moe_state['selected_route_weight']),'mla_kv_b_input':info(mla['input']),'mla_kv_b_output':info(mla['output']),'moe_router_logits':info(moe['router_logits']),'moe_down_input':info(moe['selected_down']['input']),'moe_down_output':info(moe['selected_down']['output']),'elapsed_seconds':time.time()-start,'layers':layer_rows}
(OUT/'PERSISTENT_MLA_LIFETIME.json').write_text(json.dumps({'cache_before_decode1':cache_meta_before_1,'cache_after_decode1':cache_meta_after_1,'cache_before_decode2':cache_meta_before_2,'cache_after_decode2':cache_meta_after_2,'qk_operands':persistent_meta.get('qk',{}),'av_operands':persistent_meta.get('av',{}),'logical_prefix_persistence':'cache_after_decode1 content is retained as prefix in cache_before_decode2; storage replacement is explicitly recorded by pointers'},indent=2,sort_keys=True)+'\n')
(OUT/'EXACT_STATE_CHAIN.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':'PASS','moe_layer':moe_layer,'selected_expert_id':selected,'elapsed_seconds':r['elapsed_seconds']},sort_keys=True))
