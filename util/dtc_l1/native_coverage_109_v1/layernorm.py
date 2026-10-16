#!/usr/bin/env python3
import argparse, hashlib, json, pathlib
import torch
import torch.nn.functional as F
p=argparse.ArgumentParser();p.add_argument('action',choices=['timing','profile','capture']);p.add_argument('--rows',type=int,default=1024);a=p.parse_args()
torch.manual_seed(109);torch.set_grad_enabled(False)
x_cpu=torch.randn((a.rows,1024),dtype=torch.float32);x=x_cpu.cuda();w=torch.ones(1024,device='cuda');b=torch.zeros(1024,device='cuda')
def op(): return F.layer_norm(x,(1024,),w,b,1e-5)
for _ in range(3): y=op()
torch.cuda.synchronize();samples=[]
if a.action=='timing':
 for _ in range(10):
  s=torch.cuda.Event(enable_timing=True);e=torch.cuda.Event(enable_timing=True);s.record();y=op();e.record();e.synchronize();samples.append(s.elapsed_time(e))
else:
 torch.cuda.cudart().cudaProfilerStart();y=op();torch.cuda.synchronize();torch.cuda.cudart().cudaProfilerStop()
# FP64 CPU reference, all elements; fixed numerical contract before measurement.
r=x_cpu.double();r=(r-r.mean(-1,keepdim=True))/torch.sqrt(r.var(-1,unbiased=False,keepdim=True)+1e-5)
got=y.cpu();torch.testing.assert_close(got.double(),r,rtol=2e-5,atol=2e-6)
print(json.dumps(dict(family='LayerNorm',operator='torch.nn.functional.layer_norm',shape=list(x.shape),dtype=str(x.dtype),eps=1e-5,seed=109,torch=torch.__version__,torch_cuda=torch.version.cuda,input_sha256=hashlib.sha256(x_cpu.numpy().tobytes()).hexdigest(),output_sha256=hashlib.sha256(got.numpy().tobytes()).hexdigest(),max_abs_error=(got.double()-r).abs().max().item(),samples_ms=samples,warmups=3,correctness='PASS_FP64_ALL_ELEMENTS',action=a.action)))
