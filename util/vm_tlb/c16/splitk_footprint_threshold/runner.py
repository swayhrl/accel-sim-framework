#!/usr/bin/env python3
"""Locked K-parametric runner; CUDA import follows static gate and inherited lock checks."""
import argparse,csv,fcntl,gc,hashlib,importlib.util,json,os,sys
from pathlib import Path
from contracts import *

CELL_ORDER=("A","B","B","A")
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def tensor_sha(torch,t): return hashlib.sha256(t.detach().contiguous().cpu().view(torch.uint8).numpy().tobytes()).hexdigest()
def write_json(path,value): path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')
def require_lock():
 if os.environ.get('C16_GPU_LOCK_HELD')!='1': raise RuntimeError('outer lock attestation absent')
 fd=int(os.environ.get('C16_GPU_LOCK_FD','-1')); os.fstat(fd); fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
def require_gate(repo):
 path=repo/'docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1/STATIC_GATE_BINDING.json'; gate=json.loads(path.read_text())
 if gate.get('gate_status')!='SUPPORTED_PROCEED_NATIVE_THRESHOLD_SCREEN': raise RuntimeError('static gate does not authorize GPU')
 if sha(Path(A_PATH))!=A_SHA or sha(Path(B_PATH))!=B_SHA: raise RuntimeError('accepted binary mismatch')
 if tiny_reference()['reference_sha256']!=TINY_SHA: raise RuntimeError('tiny formula mismatch')
 return gate
def import_ext(path,name):
 spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
def make_tensors(torch,k):
 base=torch.arange(k,dtype=torch.int32,device='cuda'); x=torch.empty((M,k),dtype=torch.float16,device='cuda')
 for r in range(7): x[r::7]=(1+((5*r+3*base)%7)).to(torch.float16)*(2.0**-10)
 return {'input':x,'qweight':torch.full((k,N//8),QWEIGHT_WORD_I32,dtype=torch.int32,device='cuda'),'qzeros':torch.full((k//128,N//8),QZERO_WORD_I32,dtype=torch.int32,device='cuda'),'scales':torch.full((k//128,N),SCALE,dtype=torch.float16,device='cuda')}
def call(ext_a,ext_b,tensors,arm):
 ext,split=(ext_a,8) if arm=='A' else (ext_b,1); return ext.gemm_forward_cuda(tensors['input'],tensors['qweight'],tensors['scales'],tensors['qzeros'],split).reshape(M,N)
def event_ms(torch,fn):
 torch.cuda.synchronize(); a=torch.cuda.Event(enable_timing=True);b=torch.cuda.Event(enable_timing=True);a.record();out=fn();b.record();b.synchronize();return float(a.elapsed_time(b)),out
def correctness(torch,ext_a,ext_b,tensors,k):
 a=call(ext_a,ext_b,tensors,'A');b=call(ext_a,ext_b,tensors,'B');torch.cuda.synchronize();diff=(a.float()-b.float()).abs();den=torch.linalg.vector_norm(a.float());close=torch.isclose(a,b,rtol=1e-2,atol=5e-2)
 row={'point':point_name(k),'K':k,'a_sha256':tensor_sha(torch,a),'b_sha256':tensor_sha(torch,b),'shape':list(a.shape),'dtype':str(a.dtype),'all_finite':bool(torch.isfinite(a).all() and torch.isfinite(b).all()),'max_abs':float(diff.max()),'mean_abs':float(diff.mean()),'relative_l2':float(torch.linalg.vector_norm(a.float()-b.float())/den),'changed_element_count':int(torch.ne(a,b).sum()),'element_count':a.numel(),'rtol':1e-2,'atol':5e-2,'pass':bool(close.all())}
 del a,b,diff,close
 if not row['pass'] or not row['all_finite']: raise RuntimeError(f'correctness fail K={k}')
 return row
def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=('qualify','timing','profile'));p.add_argument('--repo',type=Path,required=True);p.add_argument('--raw',type=Path,required=True);p.add_argument('--K',type=int,choices=KS);p.add_argument('--arm',choices=('A','B'));a=p.parse_args()
 require_lock();gate=require_gate(a.repo);from importlib import import_module;torch=import_module("torch")
 if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable')
 prop=torch.cuda.get_device_properties(0);l2=int(getattr(prop,'L2_cache_size',getattr(prop,'l2_cache_size',-1)))
 if (prop.major,prop.minor)!=(8,9) or l2!=L2_BYTES or prop.total_memory<15*2**30:raise RuntimeError(f'GPU identity {prop}/{l2}')
 ext_a=import_ext(Path(A_PATH),'awq_ext');ext_b=import_ext(Path(B_PATH),'awq_split1_ext');a.raw.mkdir(parents=True,exist_ok=True)
 if a.mode=='qualify':
  rows=[];receipts=[];life=[]
  with torch.inference_mode():
   torch.cuda.cudart().cudaProfilerStart()
   for k in KS:
    torch.cuda.reset_peak_memory_stats();t=make_tensors(torch,k)
    for name,v in t.items():receipts.append({'point':point_name(k),'K':k,'tensor':name,'shape':list(v.shape),'dtype':str(v.dtype),'bytes':v.numel()*v.element_size(),'sha256':tensor_sha(torch,v)})
    c=correctness(torch,ext_a,ext_b,t,k);rows.append(c)
    for arm in ('A','B'):
     label=f'C16_SPLITK_THRESHOLD_AUDIT_{point_name(k)}_{arm}';torch.cuda.nvtx.range_push(label);out=call(ext_a,ext_b,t,arm);torch.cuda.synchronize();torch.cuda.nvtx.range_pop();del out
    life.append({'point':point_name(k),'phase':'assets_live','allocated_bytes':int(torch.cuda.memory_allocated()),'reserved_bytes':int(torch.cuda.memory_reserved()),'peak_allocated_bytes':int(torch.cuda.max_memory_allocated()),'peak_reserved_bytes':int(torch.cuda.max_memory_reserved())})
    del t;gc.collect();torch.cuda.synchronize()
   torch.cuda.cudart().cudaProfilerStop()
  write_json(a.raw/'qualification.json',{'status':'PASS','correctness':rows,'tensor_receipts':receipts,'memory_lifecycle':life,'gate':gate,'gpu':{'name':prop.name,'total_memory':int(prop.total_memory),'l2_bytes':l2}})
 elif a.mode=='timing':
  samples=[];life=[]
  with torch.inference_mode():
   for k in KS:
    torch.cuda.reset_peak_memory_stats();t=make_tensors(torch,k);fns={arm:(lambda arm=arm:call(ext_a,ext_b,t,arm)) for arm in ('A','B')}
    for arm in ('A','B'):
     for _ in range(10):out=fns[arm]();del out
     torch.cuda.synchronize()
    counts={'A':0,'B':0}
    for block in range(25):
     for pos,arm in enumerate(CELL_ORDER):
      warm=fns[arm]();del warm;warm=fns[arm]();del warm;torch.cuda.synchronize();ms,out=event_ms(torch,fns[arm]);del out;samples.append({'point':point_name(k),'K':k,'arm':arm,'block':block,'position':pos,'sample_in_arm':counts[arm],'ms':ms});counts[arm]+=1
    if counts!={'A':50,'B':50}:raise RuntimeError(f'sample count {k}')
    life.append({'point':point_name(k),'allocated_bytes':int(torch.cuda.memory_allocated()),'reserved_bytes':int(torch.cuda.memory_reserved()),'peak_allocated_bytes':int(torch.cuda.max_memory_allocated()),'peak_reserved_bytes':int(torch.cuda.max_memory_reserved())});del t;gc.collect();torch.cuda.synchronize()
  write_json(a.raw/'timing_samples.json',{'status':'PASS','samples':samples,'memory_lifecycle':life})
 else:
  if a.K is None or a.arm is None:raise RuntimeError('profile requires K/arm')
  with torch.inference_mode():
   t=make_tensors(torch,a.K);fn=lambda:call(ext_a,ext_b,t,a.arm);out=fn();del out;out=fn();del out;torch.cuda.synchronize();label=f'C16_SPLITK_THRESHOLD_NCU_{point_name(a.K)}_{a.arm}';torch.cuda.nvtx.range_push(label);out=fn();torch.cuda.synchronize();torch.cuda.nvtx.range_pop()
  print(json.dumps({'status':'PASS_PROFILE','range':label,'point':point_name(a.K),'K':a.K,'arm':a.arm,'shape':list(out.shape),'dtype':str(out.dtype),'finite':bool(torch.isfinite(out).all()),'output_sha256':tensor_sha(torch,out)}))
if __name__=='__main__':main()
