"""Independent synthetic BF16 dense proxies; not native model measurements."""
import json,time,statistics,gc
from pathlib import Path
def run(task,context,out):
 import torch
 import torch.nn.functional as F
 torch.manual_seed(0)
 if task.startswith('PILOT'):
  x=torch.randn((1,2048),device='cuda',dtype=torch.bfloat16);w=torch.randn((2560,2048),device='cuda',dtype=torch.bfloat16)
  for _ in range(2):y=F.linear(x,w)
  torch.cuda.synchronize();g=torch.cuda.CUDAGraph()
  with torch.cuda.graph(g):y=F.linear(x,w)
  for _ in range(2):g.replay()
  torch.cuda.synchronize();torch.cuda.profiler.start();torch.cuda.nvtx.range_push('V10_PROXY_QKV_FIRST_NODE')
  g.replay();torch.cuda.synchronize();torch.cuda.nvtx.range_pop();torch.cuda.profiler.stop()
  assert bool(torch.isfinite(y).all())
  return dict(status='V9_WORKER_COMPLETE',model_initializations=0,proxy=True,shape=dict(B=1,K=2048,N=2560),dtype='bfloat16',Graph='torch.cuda.CUDAGraph',metrics_not_formal=True)
 rows=[];identity=[];shapes=[('QKV',2048,2560),('GATE_UP',2048,22016)]
 for label,k,n in shapes:
  weights=[torch.randn((n,k),device='cuda',dtype=torch.bfloat16) for _ in range(8)]
  graphs={};outputs={};inputs={}
  for batch in [1,2]:
   x=torch.randn((batch,k),device='cuda',dtype=torch.bfloat16);inputs[batch]=x
   for mode in ['HOT','STREAM']:
    for _ in range(2):
     for j in range(8):y=F.linear(x,weights[0 if mode=='HOT' else j])
    torch.cuda.synchronize();g=torch.cuda.CUDAGraph()
    with torch.cuda.graph(g):
     ys=[F.linear(x,weights[0 if mode=='HOT' else j]) for j in range(8)]
    graphs[(batch,mode)]=g;outputs[(batch,mode)]=ys
  orders=[[(1,'HOT'),(2,'STREAM'),(1,'STREAM'),(2,'HOT')],[(2,'HOT'),(1,'STREAM'),(2,'STREAM'),(1,'HOT')]]
  for role,repeats in [('WARMUP',2),('FORMAL',5)]:
   for ri in range(repeats):
    for batch,mode in orders[ri%2]:
     g=graphs[(batch,mode)];torch.cuda.synchronize();a=torch.cuda.Event(enable_timing=True);b=torch.cuda.Event(enable_timing=True)
     a.record();g.replay();b.record();torch.cuda.synchronize();elapsed=float(a.elapsed_time(b))
     assert elapsed>0 and elapsed<float('inf')
     row=dict(shape=label,B=batch,K=k,N=n,mode=mode,role=role,round=ri,graph_nodes_dense=8,total_event_ms=elapsed,ms_per_dense_op=elapsed/8,weight_bytes_each=k*n*2,distinct_weights=1 if mode=='HOT' else 8,working_set_weight_bytes=k*n*2*(1 if mode=='HOT' else 8))
     rows.append(row)
     (out/'raw/MICRO_PROGRESS.json').write_text(json.dumps(dict(samples=rows),indent=2)+'\n')
  assert all(bool(torch.isfinite(y).all()) for ys in outputs.values() for y in ys)
  identity.append(dict(shape=label,K=k,N=n,source='Qwenconfigprojectiondimensions;F.linearTorchdispatchproxy,noclaimofnativeexactkernel',kernel_names_not_captured=True,cache_state='Graphrepeats;HOToneweight/STREAMeightweights;notguaranteedL2residencyorDRAMbytes'))
  del graphs,outputs,weights,inputs,x,y,ys,g;gc.collect();torch.cuda.empty_cache()
 return dict(status='V9_WORKER_COMPLETE',model_initializations=0,proxy=True,samples=rows,identity=identity,clock_changes=False,not_model_performance=True)
