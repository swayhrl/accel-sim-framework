#!/usr/bin/env python3
"""Host measurement/API compatibility edits only; original CUDA kernel unchanged."""
from pathlib import Path
import hashlib, json, shutil, subprocess
root=Path('/data/c16/dtc_native_coverage_109_v1');src=root/'assets/parboil';dst=root/'assets/spmv_build'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=src,text=True).strip()=='4e0fc54866546efa44fe93af57c9cef62f6c8eb9'
shutil.copytree(src/'benchmarks/spmv/src/cuda',dst,dirs_exist_ok=True)
p=dst/'spmv_jds.h';s=p.read_text();assert s.count('texture<float,1> tex_x_float;')==1;p.write_text(s.replace('texture<float,1> tex_x_float;','// Unused legacy texture declaration removed for CUDA12 compatibility.'))
p=dst/'main.cu';s=p.read_text();s='#include <cuda_runtime.h>\n#include <cuda_profiler_api.h>\n#include <cstring>\n'+s;s=s.replace('cudaThreadSynchronize()', 'cudaDeviceSynchronize()')
begin=s.index('\t//main execution');end=s.index('\t\t\t\t\t\t\t',s.index('dim);',begin))+7 if False else s.index('\n    CUERR',begin)
s=s[:begin]+r'''
 const char* action=getenv("DTC_ACTION");if(!action)action="timing";
 for(int i=0;i<3;i++)spmv_jds<<<grid,block>>>(d_Ax_vector,d_data,d_indices,d_perm,d_x_vector,d_nzcnt,dim);
 if(cudaDeviceSynchronize()!=cudaSuccess)return 2;
 cudaFuncAttributes attr;cudaFuncGetAttributes(&attr,spmv_jds);int active;cudaOccupancyMaxActiveBlocksPerMultiprocessor(&active,spmv_jds,block,0);
 printf("DTC_JSON {\"family\":\"SpMV\",\"kernel\":\"spmv_jds\",\"dim\":%d,\"jds_entries\":%d,\"grid\":%u,\"block\":%u,\"registers\":%d,\"static_shared\":%zu,\"max_active_blocks_per_sm\":%d,\"warmups\":3,\"samples_ms\":[",dim,len,grid,block,attr.numRegs,attr.sharedSizeBytes,active);
 if(strcmp(action,"timing")==0){
  cudaEvent_t start,stop;cudaEventCreate(&start);cudaEventCreate(&stop);
  for(int i=0;i<10;i++){cudaEventRecord(start);spmv_jds<<<grid,block>>>(d_Axx_vector,d_data,d_indices,d_perm,d_x_vector,d_nzcnt,dim);cudaEventRecord(stop);cudaEventSynchronize(stop);float ms;cudaEventElapsedTime(&ms,start,stop);printf("%s%.9g",i?",":"",ms);}
  cudaEventDestroy(start);cudaEventDestroy(stop);
 }else {cudaProfilerStart();spmv_jds<<<grid,block>>>(d_Ax_vector,d_data,d_indices,d_perm,d_x_vector,d_nzcnt,dim);cudaDeviceSynchronize();cudaProfilerStop();}
 printf("]}\n");
'''.replace('d_Axx_vector','d_Ax_vector')+s[end:];p.write_text(s)
k=src/'benchmarks/spmv/src/cuda/jds_kernels.cu';assert k.read_bytes()==(dst/'jds_kernels.cu').read_bytes()
paths=[k,src/'datasets/spmv/small/input/1138_bus.mtx',src/'datasets/spmv/small/input/vector.bin',src/'datasets/spmv/small/output/1138_bus.mtx.out',src/'benchmarks/spmv/tools/compare-output',src/'benchmarks/spmv/common_src/convert-dataset/convert_dataset.c',dst/'main.cu',dst/'spmv_jds.h']
(root/'raw/spmv_source_input_identity.json').write_text(json.dumps([{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in paths],indent=2)+'\n')
