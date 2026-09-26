#!/usr/bin/env python3
from __future__ import annotations
import fcntl,hashlib,json,os,time
from pathlib import Path
import torch
from torch.utils.cpp_extension import load_inline
ROOT=Path('/data/c16/awma/uvm_model_derived_characterization_20260926')
OUT=ROOT/'PYTORCH_MANAGED_TENSOR_BRIDGE_STATUS.json';LOCK=Path('/data/c16/locks/c16_gpu_campaign.lock')
CPP=r'''
#include <torch/extension.h>
#include <cuda_runtime_api.h>
torch::Tensor managed_bf16(int64_t rows,int64_t cols){
 void* p=nullptr;auto e=cudaMallocManaged(&p,(size_t)rows*cols*2,cudaMemAttachGlobal);TORCH_CHECK(e==cudaSuccess,cudaGetErrorString(e));
 auto del=[](void*q){cudaFree(q);};
 return torch::from_blob(p,{rows,cols},del,torch::TensorOptions().dtype(torch::kBFloat16).device(torch::kCUDA,0));
}
pybind11::dict attrs(torch::Tensor t){cudaPointerAttributes a{};auto e=cudaPointerGetAttributes(&a,t.data_ptr());TORCH_CHECK(e==cudaSuccess,cudaGetErrorString(e));pybind11::dict d;d["type"]=(int)a.type;d["device"]=a.device;d["is_managed"]=(a.type==cudaMemoryTypeManaged);return d;}
void prefetch(torch::Tensor t){auto e=cudaMemPrefetchAsync(t.data_ptr(),t.numel()*t.element_size(),0);TORCH_CHECK(e==cudaSuccess,cudaGetErrorString(e));}
PYBIND11_MODULE(TORCH_EXTENSION_NAME,m){m.def("managed_bf16",&managed_bf16);m.def("attrs",&attrs);m.def("prefetch",&prefetch);}
'''
def main():
 receipt={'attempt_count':1,'scope':'bounded 4096x4096 BF16 managed weight + torch.mv','torch_version':torch.__version__,'torch_cuda':torch.version.cuda,'source_sha256':hashlib.sha256(CPP.encode()).hexdigest(),'status':'NOT_READY'}
 try:
  mod=load_inline(name='awma_managed_bridge_v1',cpp_sources=CPP,functions=None,extra_cflags=['-O2'],extra_ldflags=['-lcudart'],with_cuda=False,build_directory=str(ROOT/'bridge_build'),verbose=True)
  receipt['compile_status']='PASS'
  lock=open(LOCK,'a+');fcntl.flock(lock,fcntl.LOCK_EX)
  try:
   w=mod.managed_bf16(4096,4096);a=dict(mod.attrs(w));w.fill_(0.000244140625);x=torch.ones(4096,device='cuda',dtype=torch.bfloat16);mod.prefetch(w);torch.cuda.synchronize();t=time.perf_counter();y=torch.mv(w,x);torch.cuda.synchronize();ms=(time.perf_counter()-t)*1000
   expected=1.0;got=float(y[0]);receipt.update(status='READY',pointer_attributes=a,operation='torch.mv',result_first=got,expected=expected,semantic_check=abs(got-expected)<0.01,elapsed_ms=ms,allocation_bytes=w.numel()*w.element_size())
  finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
 except Exception as e:receipt.update(error_type=type(e).__name__,error=str(e)[:4000])
 OUT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
