"""Measured local DOWN proxy preconditions; never native application timing."""
import hashlib,json
def run(task,context,out):
 import torch
 import torch.nn.functional as F
 if 'LT' in task:torch.backends.cuda.preferred_blas_library('cublaslt')
 torch.manual_seed(11)
 batch=2 if task.endswith('B2') else 1
 x=torch.randn((batch,11008),device='cuda',dtype=torch.bfloat16)
 w=torch.randn((2048,11008),device='cuda',dtype=torch.bfloat16)
 evict=torch.zeros(128*1024*1024,device='cuda',dtype=torch.float32) if task.startswith('LOCAL') else None
 for _ in range(2):y=F.linear(x,w)
 torch.cuda.synchronize();g=torch.cuda.CUDAGraph()
 with torch.cuda.graph(g):y=F.linear(x,w)
 rows=[];reference=None
 schedule=[(ri,mode) for ri in range(5) for mode in (['REUSE','EVICT'] if ri%2==0 else ['EVICT','REUSE'])] if task.startswith('LOCAL') else [(0,'REUSE')]
 for ri,mode in schedule:
  for _ in range(2):g.replay()
  if mode=='EVICT':evict.add_(1)
  torch.cuda.synchronize()
  torch.cuda.profiler.start();torch.cuda.nvtx.range_push('v11Local')
  g.replay();torch.cuda.synchronize()
  torch.cuda.nvtx.range_pop();torch.cuda.profiler.stop()
  assert bool(torch.isfinite(y).all())
  bits=y.detach().cpu().view(torch.uint16).tolist();h=hashlib.sha256(json.dumps(bits,separators=(',',':')).encode()).hexdigest()
  if reference is None:reference=h
  assert h==reference
  rows.append(dict(index=len(rows),round=ri,precondition=mode,B=batch,K=11008,N=2048,weight_bytes=45088768,eviction_buffer_bytes=536870912 if evict is not None else 0,output_bits_sha256=h,output_finite=True,nominal_FLOPs=2*batch*11008*2048))
  (out/'raw'/(task+'_PROGRESS.json')).write_text(json.dumps(rows,indent=2)+'\n')
 return dict(status='V9_WORKER_COMPLETE',model_initializations=0,proxy=True,shape=dict(B=batch,K=11008,N=2048),dtype='bfloat16',no_bias=True,Graph='torch.cuda.CUDAGraph',rows=rows,output_identical=True,not_model_performance=True,precondition_cost_excluded_from_node_counter=True,actual_DRAM_state_requires_NCU=True)
