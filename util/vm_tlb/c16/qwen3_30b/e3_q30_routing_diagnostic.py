#!/usr/bin/env python3
"""Lightweight E3 N/U/H/P routing diagnostic; no tracer/profiler use."""
import hashlib,json,math,statistics,time
from pathlib import Path
import torch
import torch.nn.functional as F
from util.vm_tlb.c16.qwen3_30b.q30_s0_executor import Q30, load_blob, thaw, fsha

REPO=Path('/home/huangrulin/workspace/worktrees/accel-sim-c16-e3-q30-routing-diagnostic-109-v1')
MODEL=Path('/data/c16/models/qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39')
STATE=Path('/data/c16/qwen3_30b/bringup/Q30_S2_STREAM_V1_20260917T001000Z/target_states/prefill')
OUT=Path('/data/c16/qwen3_30b/e3_routing_v1/E3_Q30_ROUTING_DIAGNOSTIC_109_V1')
LAYER=24; M=2048; E=128; K=8; SEED=20260922

def tsha(x):
 x=x.detach().contiguous().cpu();h=hashlib.sha256();h.update(repr((tuple(x.shape),str(x.dtype))).encode());h.update(x.view(torch.uint8).numpy().tobytes());return h.hexdigest()
def fsha2(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def stat(values):
 return {'raw_ms':values,'min_ms':min(values),'median_ms':statistics.median(values),'max_ms':max(values),'cv':statistics.pstdev(values)/statistics.mean(values) if statistics.mean(values) else 0.0}
def timer(fn):
 torch.cuda.synchronize();a=time.perf_counter_ns();result=fn();torch.cuda.synchronize();return result,(time.perf_counter_ns()-a)/1e6
def distinct(ids): return bool(torch.all(torch.sort(ids,dim=1).values[:,1:]!=torch.sort(ids,dim=1).values[:,:-1]))
def route_stats(ids,weights):
 hist=torch.bincount(ids.reshape(-1),minlength=E); active=torch.nonzero(hist).flatten();nz=hist[active].tolist();
 return {'assignments':int(ids.numel()),'active_experts':int(active.numel()),'histogram':hist.tolist(),'histogram_cv':statistics.pstdev(nz)/statistics.mean(nz) if nz else 0.0,'active_min':min(nz) if nz else 0,'active_median':statistics.median(nz) if nz else 0,'active_max':max(nz) if nz else 0,'top_expert_fraction':max(nz)/int(ids.numel()) if nz else 0,'selected_expert_ids_sha256':tsha(ids),'routing_weights_sha256':tsha(weights),'per_token_distinct':distinct(ids)}
def invariants(name,ids,weights,natural_weights):
 s=route_stats(ids,weights)
 if ids.shape!=(M,K) or not s['per_token_distinct'] or s['assignments']!=M*K:raise RuntimeError(name+' route invariant')
 if name=='U' and set(s['histogram'])!={128}:raise RuntimeError('U balance')
 if name=='H' and (s['active_experts']!=8 or set(x for x in s['histogram'] if x)!={2048}):raise RuntimeError('H hot set')
 if name in ('U','H') and not torch.equal(weights,natural_weights):raise RuntimeError(name+' weight preservation')
 return s
def body(mlp,x,ids,weights):
 flat=x.reshape(-1,x.shape[-1]);out=torch.zeros_like(flat);calls=[]
 for expert in range(E):
  slot,tok=torch.where((ids==expert).transpose(0,1))
  if not len(tok):continue
  y=mlp.experts[expert](flat[None,tok].reshape(-1,flat.shape[-1]))*weights[tok,slot,None]
  out.index_add_(0,tok,y.to(out.dtype));calls.append({'expert_id':expert,'assignments':int(len(tok))})
 return out.reshape_as(x),calls
def capacity(mlp,active):
 components={};per=[]
 for expert in range(E):
  part={name:sum(p.numel()*p.element_size() for n,p in mlp.experts[expert].named_parameters() if n.startswith(name)) for name in ('gate_proj','up_proj','down_proj')}
  per.append(part)
 for name in ('gate_proj','up_proj','down_proj'):components[name]=per[0][name]
 return {'label':'SEMANTIC_ACTIVE_WEIGHT_CAPACITY','per_expert_bytes':sum(components.values()),'components_per_expert_bytes':components,'active_expert_count':len(active),'active_expert_weight_capacity_bytes':sum(sum(per[e].values()) for e in active)}
def main():
 if OUT.exists():raise SystemExit('output exists')
 manifest=json.loads((STATE/'manifest.json').read_text());arts={x['name']:x['sha256'] for x in manifest['artifacts']}
 for n in ('call_boundary.pt','source_oracle.pt'):
  if fsha(STATE/n)!=arts[n]:raise RuntimeError('state artifact hash '+n)
 call=load_blob(STATE/'call_boundary.pt');oracle=load_blob(STATE/'source_oracle.pt')
 if tuple(call['hidden_states'].shape)!=(1,M,2048):raise RuntimeError('exact S2 shape')
 q=Q30(MODEL);layer=q.model.model.layers[LAYER];captured={}
 def pre(_,args):captured['input']=args[0].detach().clone()
 def post(_,args,out):captured['output']=out[0].detach().clone()
 q.on(layer,f'model.layers.{LAYER}.');hooks=[layer.mlp.register_forward_pre_hook(pre),layer.mlp.register_forward_hook(post)]
 try:
  with torch.inference_mode():
   h=call['hidden_states'].to('cuda'); full_out,router_logits,*_=layer(h,**thaw(call));
   x=captured['input'];actual_n=captured['output'];mlp=layer.mlp
   logits=mlp.gate(x.reshape(-1,x.shape[-1]));rw=F.softmax(logits,dim=1,dtype=torch.float);nw,nids=torch.topk(rw,K,dim=-1)
   if mlp.norm_topk_prob:nw=nw/nw.sum(dim=-1,keepdim=True)
   nw=nw.to(x.dtype)
   nout,ncalls=body(mlp,x,nids,nw)
   if not torch.equal(nout,actual_n):raise RuntimeError('N body does not reproduce actual MLP output')
   uids=((torch.arange(M,device='cuda')[:,None]*K+torch.arange(K,device='cuda')[None,:])%E).long();uids,_=torch.sort(uids,dim=1)
   natural_hist=torch.bincount(nids.reshape(-1),minlength=E);hot=torch.argsort(natural_hist,descending=True,stable=True)[:K];hids=hot[None,:].expand(M,-1).clone()
   perm=torch.randperm(M,generator=torch.Generator(device='cpu').manual_seed(SEED)).to('cuda');inverse=torch.empty_like(perm);inverse[perm]=torch.arange(M,device='cuda');pids=nids[perm];pweights=nw[perm];
   conditions={'N':(x,nids,nw),'U':(x,uids,nw),'H':(x,hids,nw),'P':(x[:,perm,:],pids,pweights)}
   routes={name:{'ids':ids.cpu(),'weights':weights.cpu()} for name,(_,ids,weights) in conditions.items()};torch.save({'routes':routes,'perm':perm.cpu(),'inverse':inverse.cpu()},OUT/'ROUTES.pt') if OUT.parent.exists() else None
   summaries={};outputs={};calls={}
   for name,(_,ids,weights) in conditions.items():summaries[name]=invariants(name,ids,weights,nw);outputs[name],calls[name]=body(mlp,conditions[name][0],ids,weights)
   pout=outputs['P'][:,inverse,:]
   if not torch.equal(pout,nout):raise RuntimeError('P inverse equivalence')
   warm=2;meas=5;times={name:[] for name in conditions};router_times=[]
   order=['N','U','H','P']
   for rep in range(warm+meas):
    rotated=order[rep%4:]+order[:rep%4]
    for name in rotated:
     _,elapsed=timer(lambda n=name:body(mlp,*conditions[n]));
     if rep>=warm:times[name].append(elapsed)
    _,rt=timer(lambda:(torch.topk(F.softmax(mlp.gate(x.reshape(-1,x.shape[-1])),dim=1,dtype=torch.float),K,dim=-1)))
    if rep>=warm:router_times.append(rt)
   for name in conditions:
    active=[x['expert_id'] for x in calls[name]];summaries[name].update({'condition':'NATURAL_ROUTING' if name in ('N','P') else 'SYNTHETIC_ROUTING','expert_calls':len(calls[name]),'expert_calls_detail':calls[name],'expert_batch_sizes':[x['assignments'] for x in calls[name]],'semantic_active_weight_capacity':capacity(mlp,active),'body_timing':stat(times[name]),'backend':'Qwen3MoeSparseMoeBlock expert loop','dtype':str(x.dtype),'layout':'accepted Layer24 MLP input'})
   OUT.mkdir(parents=True);torch.save({'routes':routes,'perm':perm.cpu(),'inverse':inverse.cpu()},OUT/'ROUTES.pt')
   result={'status':'PASS','upstream_state_manifest_sha256':fsha(STATE/'manifest.json'),'state_hidden_sha256':tsha(call['hidden_states']),'layer':LAYER,'M':M,'E':E,'k':K,'warmups':warm,'measurements':meas,'router_timing_N_only':stat(router_times),'conditions':summaries,'natural_router_logits_sha256':tsha(logits),'natural_body_output_sha256':tsha(nout),'actual_mlp_output_sha256':tsha(actual_n),'p_inverse_output_sha256':tsha(pout),'p_equivalence_bitwise':True,'permutation_seed':SEED,'permutation_sha256':tsha(perm),'inverse_permutation_sha256':tsha(inverse),'forbidden_tools_used':[],'limitation':'Only whole dispatch->experts->combine body timing is reported; no fabricated sub-times.'}
   (OUT/'E3_RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 finally:
  for hook in hooks:hook.remove()
  q.off(layer)
 print(json.dumps({'status':'PASS','output':str(OUT)},sort_keys=True))
if __name__=='__main__':main()
