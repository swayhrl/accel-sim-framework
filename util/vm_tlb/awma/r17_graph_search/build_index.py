#!/usr/bin/env python3
"""Build exactly one frozen device-resident CAGRA index under external GPU lock."""
import hashlib
import json
import os
import struct
import subprocess
import threading
import time
from pathlib import Path

import numpy as np

ROOT=Path('/data/c16/awma/r17_graph_search_20260930')
WT=Path('/home/huangrulin/workspace/worktrees/accel-sim-awma-r17-graph-search-native-109-v1')
PACK=WT/'docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1'
BIN=ROOT/'dataset/glove-100-inner'
INDEX=ROOT/'index/cagra_glove100_g64_ig128_sqeuclidean.bin'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def memmap(path,dtype):
    with path.open('rb') as f:n,d=struct.unpack('<ii',f.read(8))
    assert path.stat().st_size==8+n*d*np.dtype(dtype).itemsize
    return np.memmap(path,dtype=dtype,mode='r',offset=8,shape=(n,d))

def main():
    assert os.environ.get('R17_GPU_LOCK_HELD')=='1'
    assert not INDEX.exists(),f'one-index rule: existing output {INDEX}'
    dataset=json.loads((PACK/'DATASET_RECEIPT.json').read_text())
    assert sha(BIN/'base.fbin')==dataset['files']['dataset/glove-100-inner/base.fbin']['sha256']
    import cupy as cp
    import cuvs
    import rmm
    from cuvs.neighbors import cagra
    p=cp.cuda.runtime.getDeviceProperties(0)
    assert p['major']==8 and p['minor']==9
    apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True)
    assert not apps.strip(),f'other compute apps before admission: {apps}'
    runtime={'python':os.sys.version.split()[0],'cuvs':getattr(cuvs,'__version__','NOT_EXPOSED'),
      'cupy':cp.__version__,'rmm':getattr(rmm,'__version__','NOT_EXPOSED'),
      'cuda_runtime_version':cp.cuda.runtime.runtimeGetVersion(),
      'cuda_driver_version':cp.cuda.runtime.driverGetVersion(),
      'GPU_name':p['name'].decode() if isinstance(p['name'],bytes) else str(p['name']),
      'SM':f"{p['major']}{p['minor']}",'SM_count':p['multiProcessorCount'],
      'VRAM_bytes':p['totalGlobalMem'],
      'nvidia_smi':subprocess.check_output(['nvidia-smi','--query-gpu=name,driver_version,memory.total','--format=csv,noheader'],text=True).strip(),
      'source_tag':'v26.08.01','source_commit':'25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab',
      'stable_runtime_wheel_sha256':sha(ROOT/'wheels/cuvs_cu12-26.8.1-cp311-abi3-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl')}
    (PACK/'SOURCE_RUNTIME_RECEIPT.json').write_text(json.dumps(runtime,indent=2,sort_keys=True)+'\n')
    base=memmap(BIN/'base.fbin','<f4')
    assert base.shape==(1183514,100)
    gpu_base=cp.asarray(base)
    cp.cuda.runtime.deviceSynchronize()
    free_before,total=cp.cuda.runtime.memGetInfo()
    # The stable Python IndexParams default is IVF-PQ; do not substitute the
    # distinct C++ heuristic default or change graph construction parameters.
    params=cagra.IndexParams(metric='sqeuclidean',graph_degree=64,intermediate_graph_degree=128)
    assert params.graph_degree==64 and params.intermediate_graph_degree==128
    # The stable C API enum is IVF_PQ=1 (AUTO_SELECT=0).
    assert int(params.build_algo)==1,str(params.build_algo)
    samples=[];stop=threading.Event();pid=os.getpid()
    def sample_peak():
        while not stop.is_set():
            try:
                output=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_gpu_memory',
                    '--format=csv,noheader,nounits'],text=True,stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    pieces=[x.strip() for x in line.split(',')]
                    if int(pieces[0])==pid:samples.append(int(pieces[1]))
            except Exception:pass
            stop.wait(0.1)
    thread=threading.Thread(target=sample_peak,daemon=True);thread.start()
    start=time.perf_counter()
    try:
        index=cagra.build(params,gpu_base)
        cp.cuda.runtime.deviceSynchronize()
        build_seconds=time.perf_counter()-start
    finally:
        stop.set();thread.join(timeout=5)
    assert len(index)==len(base) and index.dim==100 and index.graph_degree==64
    free_after,_=cp.cuda.runtime.memGetInfo()
    cagra.save(str(INDEX),index,include_dataset=True)
    cp.cuda.runtime.deviceSynchronize()
    graph_hash='UNAVAILABLE'
    graph_shape='UNAVAILABLE'
    try:
        graph=cp.asarray(index.graph)
        graph_shape=list(graph.shape)
        graph_hash=hashlib.sha256(graph.get().tobytes()).hexdigest()
    except Exception as exc:
        graph_hash=f'UNAVAILABLE:{type(exc).__name__}:{exc}'
    receipt={'stage':'AWMA_R17_GRAPH_SEARCH_109_V1','dataset_base_sha256':sha(BIN/'base.fbin'),
      'metric':'sqeuclidean on official L2-normalized glove-100-angular; rank-equivalent to cosine/angular',
      'index_count':len(index),'dim':index.dim,'graph_degree':index.graph_degree,
      'intermediate_graph_degree':params.intermediate_graph_degree,
      'build_algo_python_default_requested':'ivf_pq','build_algo_runtime_value':str(params.build_algo),
      'uncompressed':True,'filters':False,'updates':False,
      'build_seconds':build_seconds,'sampled_peak_process_MiB':max(samples) if samples else 'UNAVAILABLE',
      'peak_sample_count':len(samples),'cuda_free_before_build_bytes':free_before,
      'cuda_free_after_build_bytes':free_after,'VRAM_total_bytes':total,
      'cupy_pool_used_bytes_after':cp.get_default_memory_pool().used_bytes(),
      'index_serialized_path':str(INDEX),'index_serialized_bytes':INDEX.stat().st_size,
      'index_serialized_sha256':sha(INDEX),'graph_shape':graph_shape,'graph_sha256':graph_hash,
      'index_and_dataset_resident_at_build_exit':True}
    (PACK/'INDEX_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'runtime':runtime,'index':receipt},sort_keys=True))

if __name__=='__main__':main()
