#!/usr/bin/env python3
from __future__ import annotations
import fcntl,hashlib,json
from pathlib import Path
import torch
import torch.nn.functional as F
ROOT=Path('/data/c16/awma/r51_r52_lifecycle_qualification_20260926');LOCK='/data/c16/locks/c16_gpu_campaign.lock'
def tsha(t):return hashlib.sha256(t.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
def delta(o,r):
 d=(o-r).abs();return {'bitwise':bool(torch.equal(o,r)),'different_elements':int((o!=r).sum()),'max_abs':float(d.max()),'mean_abs':float(d.float().mean()),'output_sha256':tsha(o)}
def main():
 lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  p=torch.load(ROOT/'input/R51_TARGET_PAYLOAD.pt',map_location='cpu',weights_only=True);h=p['background_hidden'].cuda();w=p['background_weight'].cuda();ref=p['background_reference'].cuda();rows=[]
  ops={'F_LINEAR_2D':lambda ww:F.linear(h,ww).reshape(-1),'F_LINEAR_1D':lambda ww:F.linear(h[0],ww).reshape(-1),'TORCH_MV':lambda ww:torch.mv(ww,h[0]),'TORCH_MATMUL':lambda ww:torch.matmul(ww,h[0]),'TORCH_MM':lambda ww:torch.mm(h,ww.t()).reshape(-1),'TORCH_ADDMV':lambda ww:torch.addmv(torch.zeros(ww.shape[0],device='cuda',dtype=torch.float16),ww,h[0])}
  for chunks in (8,32):
   n=w.shape[0]//chunks
   for name,fn in ops.items():
    o=torch.cat([fn(w[i*n:(i+1)*n]) for i in range(chunks)]).reshape_as(ref);torch.cuda.synchronize();rows.append({'attempt':1 if name=='F_LINEAR_2D' else 2,'implementation':name,'chunks':chunks,**delta(o,ref)})
   # Correct graph liveness against the exact eager chunk implementation, separate from B0 equality.
   side=torch.cuda.Stream();
   def chunked():return torch.cat([F.linear(h,w[i*n:(i+1)*n]) for i in range(chunks)],-1)
   with torch.cuda.stream(side):
    for _ in range(3):captured=chunked()
   torch.cuda.synchronize();g=torch.cuda.CUDAGraph()
   with torch.cuda.graph(g,stream=side):captured=chunked()
   original=h.clone();g.replay();torch.cuda.synchronize();base=captured.clone();h.copy_(-original);g.replay();torch.cuda.synchronize();changed=captured.clone();eager_changed=chunked();torch.cuda.synchronize();h.copy_(original);g.replay();torch.cuda.synchronize();restored=captured.clone();rows.append({'attempt':'GRAPH_LIVENESS','implementation':'F_LINEAR_2D_CUDA_GRAPH','chunks':chunks,'base_graph_equals_eager':bool(torch.equal(base,torch.cat([F.linear(h,w[i*n:(i+1)*n]) for i in range(chunks)],-1))),'changed_graph_equals_eager_chunked':bool(torch.equal(changed,eager_changed)),'changed_differs_from_base':not torch.equal(changed,base),'restored_equals_base':bool(torch.equal(restored,base))})
  out={'status':'SOFTWARE_SAFEPOINT_NUMERIC_CONTRACT_NOT_CLOSED','attempt_limit':2,'attempts':rows,'rejected_non_strong_option':'full-size zero/dummy-row padding would preserve dispatch only by 8x/32x redundant full-vocabulary arithmetic and is not a credible strong safe-point baseline'};(ROOT/'NUMERIC_ATTEMPT_AUDIT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True))
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
