"""Small API diagnostic only, never a scientific graph or performance result."""
import os,faulthandler
assert os.environ.get('A47_GPU_LOCK_HELD')=='1';faulthandler.enable();os.sched_setaffinity(0,[0,2,4,6])
import numpy as np
import cupy as cp
import rmm
from rmm.allocators.cupy import rmm_cupy_allocator
from cuvs.common import Resources
from cuvs.common.dataset import make_device_padded_dataset
from cuvs.neighbors import cagra
print('FIXTURE_IMPORTS_PASS',flush=True)
cp.cuda.Device(0).use();upstream=rmm.mr.CudaMemoryResource();pool=rmm.mr.PoolMemoryResource(upstream,initial_pool_size=512*1024**2,maximum_pool_size=10*1024**3);rmm.mr.set_current_device_resource(pool);cp.cuda.set_allocator(rmm_cupy_allocator)
stream=cp.cuda.Stream(non_blocking=True);res=Resources(stream=stream.ptr)
x=np.random.default_rng(20261014).standard_normal((1024,100),dtype=np.float32);x/=np.linalg.norm(x,axis=1)[:,None]
with stream:g=cp.asarray(x)
cp.cuda.runtime.deviceSynchronize();print('FIXTURE_GPU_INPUT_PASS',flush=True)
print('ENTRY_MAKE_PADDED_DATASET',flush=True);ds=make_device_padded_dataset(g,resources=res);cp.cuda.runtime.deviceSynchronize();print('FIXTURE_PADDED_DATASET_PASS',ds.layout,ds.is_owning,flush=True)
params=cagra.IndexParams(metric='cosine',build_algo='ivf_pq',graph_degree=64,intermediate_graph_degree=128)
print('ENTRY_SMALL_BUILD_API_ONLY',flush=True);idx=cagra.build(params,ds,resources=res);cp.cuda.runtime.deviceSynchronize();print('FIXTURE_SMALL_API_BUILD_PASS',len(idx),flush=True)
