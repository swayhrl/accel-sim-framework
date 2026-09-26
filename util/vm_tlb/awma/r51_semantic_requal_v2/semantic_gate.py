#!/usr/bin/env python3
from __future__ import annotations
import csv,fcntl,hashlib,json
from pathlib import Path
import torch
import torch.nn.functional as F
ROOT=Path('/data/c16/awma/r51_semantic_requal_v2_20260926');V1=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926');LOCK='/data/c16/locks/c16_gpu_campaign.lock'
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def ordered(t):
 b=t.contiguous().view(torch.int16).to(torch.int32)&0xffff;return torch.where((b&0x8000)!=0,0x8000-(b&0x7fff),0x8000+b)
def graph_chunk(h,w,n):
 rows=w.shape[0]//n;stream=torch.cuda.Stream()
 def fn():return torch.cat([F.linear(h,w[i*rows:(i+1)*rows]) for i in range(n)],-1)
 with torch.cuda.stream(stream):
  for _ in range(3):out=fn()
 torch.cuda.synchronize();g=torch.cuda.CUDAGraph()
 with torch.cuda.graph(g,stream=stream):out=fn()
 g.replay();torch.cuda.synchronize();return out.clone()
def main():
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  states=torch.load(ROOT/'input/R51_V2_SEMANTIC_STATES.pt',map_location='cpu',weights_only=True)['states'];v1=torch.load(V1/'input/R51_TARGET_PAYLOAD.pt',map_location='cpu',weights_only=True);w=v1['background_weight'].cuda();rows=[]
  for step in (8,16,24):
   h=states[step]['hidden'].cuda();ref=states[step]['reference'].cuda();outs={'B0':F.linear(h,w),'B8':graph_chunk(h,w,8),'B32':graph_chunk(h,w,32)};torch.cuda.synchronize()
   if not torch.equal(outs['B0'],ref):raise RuntimeError(f'B0 reference mismatch step{step}')
   b0_top8=torch.topk(outs['B0'].float(),8,dim=-1).indices[0].tolist();b0_set=sorted(b0_top8);b0_top2=b0_top8[:2];b0_arg=int(outs['B0'].argmax(-1).item())
   for arm,o in outs.items():
    d=(o-outs['B0']).abs();top8=torch.topk(o.float(),8,dim=-1).indices[0].tolist();gates={'shape_exact':list(o.shape)==list(outs['B0'].shape),'dtype_exact':o.dtype==outs['B0'].dtype,'finite':bool(torch.isfinite(o).all()),'argmax_exact':int(o.argmax(-1).item())==b0_arg,'top8_set_exact':sorted(top8)==b0_set,'top1_top2_order_exact':top8[:2]==b0_top2};rows.append({'step':step,'state_role':'PRIMARY' if step==16 else 'HOLDOUT','arm':arm,'output_shape':','.join(map(str,o.shape)),'dtype':str(o.dtype),'output_sha256':tsha(o),'argmax_token_id':int(o.argmax(-1).item()),'top8_token_ids_ordered':','.join(map(str,top8)),'top8_token_ids_set':','.join(map(str,sorted(top8))),'top1_top2_order':','.join(map(str,top8[:2])),**gates,'required_gate_pass':all(gates.values()),'different_fp16_elements':int((o!=outs['B0']).sum()),'max_abs':float(d.max()),'mean_abs':float(d.float().mean()),'max_fp16_ordered_code_distance':int((ordered(o)-ordered(outs['B0'])).abs().max())})
  with (ROOT/'SEMANTIC_EQUIVALENCE_RESULTS.tsv').open('w',newline='') as f:wri=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');wri.writeheader();wri.writerows(rows)
  safe=[r for r in rows if r['arm'] in ('B8','B32')];decision='SEMANTIC_EQUIVALENCE_PASS' if all(r['required_gate_pass'] for r in safe) else 'SEMANTIC_EQUIVALENCE_FAIL';receipt={'status':decision,'contract':'GREEDY_DECODE_SEMANTIC_EQUIVALENCE_V1','states':[8,16,24],'arms':['B8','B32'],'all_required_gates_pass':decision.endswith('PASS'),'strict_bitwise_v1_failure_preserved':True};(ROOT/'SEMANTIC_GATE_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True));raise SystemExit(decision!='SEMANTIC_EQUIVALENCE_PASS')
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
