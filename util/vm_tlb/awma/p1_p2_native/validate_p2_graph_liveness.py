#!/usr/bin/env python3
from __future__ import annotations
import fcntl,hashlib,json,sys
from pathlib import Path
import torch
ROOT=Path('/data/c16/awma/p1_p2_native_qualification_20260926');WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-p1-p2-native-qualification-v1');sys.path.insert(0,str(WT/'util/vm_tlb/awma/p1_p2_native'))
from p1_p2_native_harness import online,selector,tsha
def main():
 lock=open('/data/c16/locks/c16_gpu_campaign.lock','a+');fcntl.flock(lock,fcntl.LOCK_EX)
 try:
  p=torch.load(ROOT/'input/QWEN25_0P5B_P1_P2_QKV.pt',map_location='cpu',weights_only=True)['p2'];q=p['q'].cuda()[0,:,0,:].contiguous();orig=q.clone();h=q.shape[0];hkv=p['k'].shape[1];g=h//hkv;k=p['k'].cuda()[0,:,:8192].repeat_interleave(g,0).contiguous();v=p['v'].cuda()[0,:,:8192].repeat_interleave(g,0).contiguous();kp=k.reshape(h,512,16,64);vp=v.reshape_as(kp);mi=kp.amin(2);ma=kp.amax(2);rows=[]
  for top in (256,128):
   side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
   with torch.cuda.stream(side):
    for _ in range(3):captured=online(q,mi,ma,kp,vp,top)
   torch.cuda.current_stream().wait_stream(side);graph=torch.cuda.CUDAGraph()
   with torch.cuda.graph(graph):captured=online(q,mi,ma,kp,vp,top)
   graph.replay();torch.cuda.synchronize();base_idx=captured[1].clone();base_eager=selector(q,mi,ma,top)[0];q.copy_(-orig);graph.replay();torch.cuda.synchronize();changed_idx=captured[1].clone();changed_eager=selector(q,mi,ma,top)[0];q.copy_(orig);graph.replay();torch.cuda.synchronize();restored=captured[1].clone()
   rows.append({'top_pages':top,'base_graph_equals_eager':bool(torch.equal(base_idx,base_eager)),'changed_graph_equals_eager':bool(torch.equal(changed_idx,changed_eager)),'changed_differs_from_base':not torch.equal(changed_idx,base_idx),'restored_equals_base':bool(torch.equal(restored,base_idx)),'base_indices_sha256':tsha(base_idx),'changed_indices_sha256':tsha(changed_idx)})
  status='PASS_LIVE_ONLINE_SELECTION' if all(all(x[k] for k in ('base_graph_equals_eager','changed_graph_equals_eager','changed_differs_from_base','restored_equals_base')) for x in rows) else 'FAIL'
  out={'status':status,'method':'mutate static query in place -> graph replay -> exact stable-index comparison with eager selector -> restore','configurations':rows};(ROOT/'P2_STRONG_LIVENESS_RECEIPT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,sort_keys=True));raise SystemExit(status=='FAIL')
 finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if __name__=='__main__':main()
