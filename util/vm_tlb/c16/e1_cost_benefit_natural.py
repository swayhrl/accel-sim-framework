#!/usr/bin/env python3
"""Up-proj budget sweep with all FFN child and non-overlapping top-level timing."""

import argparse,hashlib,json
from pathlib import Path
import torch
from awq import AutoAWQForCausalLM
from e1_cuda_persistence import PersistenceHelper,qweight_region
from e1_residency_common import AWQ

ROOT=Path('/data/c16/e1_residency_cost_benefit_closure_v1')
TOKENS=Path('/data/c16/inputs/.incoming/qwen2p5_7b_instruct_raw/S2_TEXT/payload/token_ids.json')
TOKEN_SHA='0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9'
EXPECTED=[23578,11,323,3950]
ROLES=('gate_proj','up_proj','down_proj')

def tsha(x):return hashlib.sha256(x.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def out_tensor(x):
 if isinstance(x,torch.Tensor):return x
 if isinstance(x,(tuple,list)) and x and isinstance(x[0],torch.Tensor):return x[0]
 raise RuntimeError(f'unsupported module output {type(x)}')
def spec(condition,contract):
 if condition=='AUTHORITY_TOPLEVEL_NO_PERSIST':return {'mode':'AUTHORITY','budget_name':None,'requested':0,'ratio':0.0,'persist':False}
 prefix,budget_name=condition.split('_',1);entry=next(x for x in contract['budgets'] if x['name']==budget_name);requested=entry['requested_bytes'];ratio=min(1.0,requested/(28*33_947_648));return {'mode':'POLICY','budget_name':budget_name,'requested':requested,'ratio':ratio,'persist':prefix=='FAIR'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--condition',required=True);p.add_argument('--run-index',type=int,default=0);p.add_argument('--output');a=p.parse_args();contract=json.loads((ROOT/'contracts/BUDGET_MATRIX_PRECONTRACT.json').read_text());cfg=spec(a.condition,contract)
 if hashlib.sha256(TOKENS.read_bytes()).hexdigest()!=TOKEN_SHA:raise RuntimeError('token authority')
 wrapper=AutoAWQForCausalLM.from_quantized(AWQ,fuse_layers=False);model=wrapper.model.eval();layers=model.model.layers
 if len(layers)!=28:raise RuntimeError('layer count')
 children={};child_census=[];tops={};top_census=[]
 for li,layer in enumerate(layers):
  for role in ROLES:
   m=getattr(layer.mlp,role)
   if not hasattr(m,'qweight'):raise RuntimeError(f'unsupported L{li} {role}')
   children[(li,role)]=m;row={'layer':li,'category':role,'module_class':type(m).__name__};row.update(qweight_region(m,f'layer{li}.mlp.{role}.qweight'));child_census.append(row)
  for cat in ('input_layernorm','self_attn','post_attention_layernorm','mlp'):
   if not hasattr(layer,cat):raise RuntimeError(f'missing top module L{li} {cat}')
   m=getattr(layer,cat);tops[(li,cat)]=m;top_census.append({'layer':li,'category':cat,'module_class':type(m).__name__})
 final_modules={}
 if hasattr(model.model,'norm'):final_modules['final_norm']=model.model.norm
 if hasattr(model,'lm_head'):final_modules['lm_head']=model.lm_head
 if set(final_modules)!= {'final_norm','lm_head'}:raise RuntimeError(f'final stages unavailable {final_modules.keys()}')
 helper=PersistenceHelper();receipt=helper.begin_condition(a.condition,cfg['requested'],None,1.0)
 if cfg['mode']=='POLICY' and receipt['actual_setaside_bytes']>46_137_344:raise RuntimeError('actual exceeds runtime max')
 active={'d':None};phase={'v':'PREFILL'};child_pending={};child_caps={};top_pending={};top_caps={};active_top={'key':None};transitions=[];child_order=[];top_order=[];handles=[];child_ord={'v':0};top_ord={'v':0}
 def child_pre(li,role):
  def h(m,args):
   o=child_ord['v'];child_ord['v']+=1;child_order.append({'phase':phase['v'],'ordinal':o,'layer':li,'category':role})
   if cfg['mode']=='POLICY' and role=='up_proj':
    t=helper.update_access_policy(f"{phase['v']}:{o}:L{li}:up_proj",m.qweight,cfg['ratio'],cfg['persist']);t.update({'phase':phase['v'],'ordinal':o,'layer':li,'category':role,'before_target_event':True});transitions.append(t)
   d=active['d']
   if d is None:return
   k=(li,role,d);s=torch.cuda.Event(enable_timing=True);e=torch.cuda.Event(enable_timing=True);name=f'C16_E1_COST_{a.condition}_L{li}_{role.upper()}_D{d}';torch.cuda.nvtx.range_push(name);s.record();child_pending[k]={'s':s,'e':e,'range':name,'input':args[0].detach(),'class':type(m).__name__}
  return h
 def child_post(li,role):
  def h(m,args,out):
   d=active['d']
   if d is None:return
   k=(li,role,d);r=child_pending.pop(k);r['e'].record();torch.cuda.nvtx.range_pop();r['output']=out_tensor(out).detach();child_caps[k]=r
  return h
 def top_pre(key):
  def h(m,args,kwargs):
   o=top_ord['v'];top_ord['v']+=1;top_order.append({'phase':phase['v'],'ordinal':o,'layer':key[0],'category':key[1]})
   d=active['d']
   if d is None:return
   if active_top['key'] is not None:raise RuntimeError(f'overlapping top-level {active_top["key"]} -> {key}')
   input_tensor=args[0] if args else next((v for v in kwargs.values() if isinstance(v,torch.Tensor)),None)
   if input_tensor is None:raise RuntimeError(f'no tensor input for top-level {key}')
   active_top['key']=(key,d);s=torch.cuda.Event(enable_timing=True);e=torch.cuda.Event(enable_timing=True);name=f'C16_E1_COST_{a.condition}_{"FINAL" if key[0]==-1 else "L"+str(key[0])}_{key[1].upper()}_D{d}';torch.cuda.nvtx.range_push(name);s.record();top_pending[(key,d)]={'s':s,'e':e,'range':name,'input':input_tensor.detach(),'class':type(m).__name__}
  return h
 def top_post(key):
  def h(m,args,out):
   d=active['d']
   if d is None:return
   if active_top['key']!=(key,d):raise RuntimeError('top-level nesting/order')
   r=top_pending.pop((key,d));r['e'].record();torch.cuda.nvtx.range_pop();r['output']=out_tensor(out).detach();top_caps[(key,d)]=r;active_top['key']=None
  return h
 for (li,role),m in children.items():handles += [m.register_forward_pre_hook(child_pre(li,role)),m.register_forward_hook(child_post(li,role))]
 for key,m in tops.items():handles += [m.register_forward_pre_hook(top_pre(key),with_kwargs=True),m.register_forward_hook(top_post(key))]
 for cat,m in final_modules.items():key=(-1,cat);handles += [m.register_forward_pre_hook(top_pre(key),with_kwargs=True),m.register_forward_hook(top_post(key))]
 toks=[];steps=[]
 try:
  ids=torch.tensor([json.loads(TOKENS.read_text())],dtype=torch.long,device='cuda')
  with torch.inference_mode():
   phase['v']='PREFILL';child_ord['v']=0;top_ord['v']=0;pref=model(input_ids=ids,use_cache=True);cur=torch.argmax(pref.logits[:,-1,:],dim=-1,keepdim=True);past=pref.past_key_values;del pref
   for d in range(4):
    toks.append(cur.detach());active['d']=d;phase['v']=f'D{d}';child_ord['v']=0;top_ord['v']=0;s=torch.cuda.Event(enable_timing=True);e=torch.cuda.Event(enable_timing=True);s.record();res=model(input_ids=cur,past_key_values=past,use_cache=True);past=res.past_key_values;cur=torch.argmax(res.logits[:,-1,:],dim=-1,keepdim=True);e.record();steps.append((s,e));active['d']=None;del res
  torch.cuda.synchronize()
  for h in handles:h.remove()
  if child_pending or top_pending or active_top['key'] is not None or len(child_caps)!=336 or len(top_caps)!=456 or len(child_order)!=420 or len(top_order)!=570:raise RuntimeError(f'closure child={len(child_caps)} top={len(top_caps)} orders={len(child_order)}/{len(top_order)}')
  token_ids=[int(x.item()) for x in toks]
  if token_ids!=EXPECTED:raise RuntimeError('token drift')
  child=[]
  for li,role in sorted(children):
   for d in range(4):
    r=child_caps[(li,role,d)];child.append({'layer':li,'role':role,'decode_index':d,'token_id':token_ids[d],'range':r['range'],'input_sha256':tsha(r['input']),'output_sha256':tsha(r['output']),'module_class':r['class'],'target_ms':float(r['s'].elapsed_time(r['e']))})
  top=[]
  for key in sorted(tops):
   for d in range(4):
    r=top_caps[(key,d)];top.append({'layer':key[0],'category':key[1],'decode_index':d,'token_id':token_ids[d],'range':r['range'],'input_sha256':tsha(r['input']),'output_sha256':tsha(r['output']),'module_class':r['class'],'target_ms':float(r['s'].elapsed_time(r['e']))})
  for cat in ('final_norm','lm_head'):
   key=(-1,cat)
   for d in range(4):
    r=top_caps[(key,d)];top.append({'layer':-1,'category':cat,'decode_index':d,'token_id':token_ids[d],'range':r['range'],'input_sha256':tsha(r['input']),'output_sha256':tsha(r['output']),'module_class':r['class'],'target_ms':float(r['s'].elapsed_time(r['e']))})
  if cfg['mode']=='POLICY':
   auth=json.loads((ROOT/'contracts/TOPLEVEL_AUTHORITY.json').read_text());ci={(x['layer'],x['role'],x['decode_index']):(x['input_sha256'],x['output_sha256']) for x in auth['child_bindings']};ti={(x['layer'],x['category'],x['decode_index']):(x['input_sha256'],x['output_sha256']) for x in auth['top_bindings']}
   if child_order!=auth['child_call_order'] or top_order!=auth['top_call_order']:raise RuntimeError('call order drift')
   for x in child:
    if (x['input_sha256'],x['output_sha256'])!=ci[(x['layer'],x['role'],x['decode_index'])]:raise RuntimeError('child identity')
   for x in top:
    if (x['input_sha256'],x['output_sha256'])!=ti[(x['layer'],x['category'],x['decode_index'])]:raise RuntimeError('top identity')
  result={'status':'PASS','condition':a.condition,'run_index':a.run_index,'mode':cfg['mode'],'budget_name':cfg['budget_name'],'requested_budget_bytes':cfg['requested'],'hit_ratio':cfg['ratio'],'target_persisting':cfg['persist'],'generated_token_ids_D0_D3':token_ids,'decode_step_ms':[float(s.elapsed_time(e)) for s,e in steps],'child_occurrences':child,'top_occurrences':top,'child_call_order':child_order,'top_call_order':top_order,'child_module_census':child_census,'top_module_census':top_census+[{'layer':-1,'category':k,'module_class':type(v).__name__} for k,v in final_modules.items()],'policy_receipt':receipt,'policy_transitions':transitions,'policy_transition_count':len(transitions),'top_level_nonoverlap_asserted':True,'no_inner_loop_synchronize':True}
 finally:receipt=helper.end_condition(receipt)
 result['policy_receipt']=receipt;expected_updates=0 if cfg['mode']=='AUTHORITY' else 140
 if len(transitions)!=expected_updates:raise RuntimeError('transition count')
 text=json.dumps(result,indent=2,sort_keys=True)+'\n'
 if a.output:Path(a.output).write_text(text)
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
