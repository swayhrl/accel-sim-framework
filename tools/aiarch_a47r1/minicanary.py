"""Exactly one tiny build per fresh process; C1 changes only Resources stream."""
import faulthandler,hashlib,importlib.metadata,json,os,pathlib,resource,sys
assert os.environ.get('A47R1_GPU_LOCK_HELD')=='1';faulthandler.enable(all_threads=True);resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,[0,2])
ROOT=pathlib.Path(os.environ['A47R1_OUTPUT']);arm=sys.argv[1];assert arm in ['C0','C1'];buildcalls=0

def record(phase,**values):
 row={'phase':phase,'arm':arm,**values};print(json.dumps(row),flush=True)
 with (ROOT/f'{arm}_events.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
import numpy as np
import cupy as cp
import cuvs
import rmm
from cuvs.common import Resources
from cuvs.common.dataset import make_device_padded_dataset
from cuvs.neighbors import cagra
assert importlib.metadata.version('cuvs-cu12')=='26.10.0' and cp.__version__=='14.0.1' and cuvs.__git_commit__=='24ee1bf1cb17cad0ac611e39643af39ee1870124'
record('IMPORT_PASS',python=sys.version.split()[0],cuvs=importlib.metadata.version('cuvs-cu12'),cuvs_commit=cuvs.__git_commit__,cupy=cp.__version__,rmm=importlib.metadata.version('rmm-cu12'),numpy=np.__version__)
cp.cuda.Device(0).use();props=cp.cuda.runtime.getDeviceProperties(0);name=props['name'].decode() if isinstance(props['name'],bytes) else props['name'];assert 'RTX 4080' in name
# No allocator/pool setters. Read-only introspection of actual default state.
mr=rmm.mr.get_current_device_resource();allocator=cp.cuda.get_allocator();mrname=type(mr).__module__+'.'+type(mr).__name__;allocname=str(getattr(allocator,'__module__',None))+'.'+str(getattr(allocator,'__name__',type(allocator).__name__))
x=np.random.default_rng(20261014).standard_normal((1024,100),dtype=np.float32);x/=np.linalg.norm(x,axis=1)[:,None];assert x.shape==(1024,100) and x.dtype==np.float32 and np.isfinite(x).all()
input_sha=hashlib.sha256(x.tobytes()).hexdigest()
# Deliberately identical default-stream preparation in both arms.
assert cp.cuda.get_current_stream().ptr==cp.cuda.Stream.null.ptr
g=cp.asarray(x);cp.cuda.runtime.deviceSynchronize();assert np.array_equal(cp.asnumpy(g),x)
record('GPU_INPUT_PASS',shape=list(x.shape),dtype=str(x.dtype),input_sha256=input_sha,prepared_on_default_CuPy_stream=True,default_stream_ptr_is_zero=cp.cuda.get_current_stream().ptr==0,default_RMM_type=mrname,default_CuPy_allocator=allocname,device=name,SM_count=props['multiProcessorCount'],driver_API=cp.cuda.runtime.driverGetVersion(),runtime_API=cp.cuda.runtime.runtimeGetVersion())
stream_owner=None
if arm=='C0':res=Resources();requested='DEFAULT_RESOURCES_STREAM'
else:
 stream_owner=cp.cuda.Stream(non_blocking=True);assert stream_owner.ptr!=0;res=Resources(stream=stream_owner.ptr);requested='EXPLICIT_NONBLOCKING_CUPY_STREAM'
record('RESOURCES_READY',stream_identity_class='REQUESTED_STREAM',requested=requested,Python_stream_owner_retained=stream_owner is not None,Cplusplus_internal_stream_or_faulting_handle='UNKNOWN')
ds=make_device_padded_dataset(g,resources=res);res.sync();cp.cuda.runtime.deviceSynchronize();assert ds.layout=='padded' and ds.memory_type=='device'
record('PADDED_DATASET_PASS',layout=ds.layout,is_owning=ds.is_owning,dtype=str(ds.dtype),x_g_ds_res_owners_retained=True)
params=cagra.IndexParams(metric='cosine',build_algo='ivf_pq',graph_degree=64,intermediate_graph_degree=128);assert params.metric=='cosine'
record('BUILD_ENTER',params={'metric':'cosine','build_algo':'ivf_pq','graph_degree':64,'intermediate_graph_degree':128},build_calls=1,input_sha256=input_sha)
buildcalls+=1;idx=cagra.build(params,ds,resources=res);res.sync();cp.cuda.runtime.deviceSynchronize()
assert idx.trained and len(idx)==1024 and idx.dim==100 and idx.graph_degree==64 and str(idx.dtype)=='float32'
record('BUILD_PASS',trained=bool(idx.trained),size=len(idx),dim=idx.dim,graph_degree=idx.graph_degree,dtype=str(idx.dtype),build_calls=buildcalls)
# Owners remain alive through the successful final synchronization and receipt.
res.sync();cp.cuda.runtime.deviceSynchronize()
result={'status':'PASS','arm':arm,'input_sha256':input_sha,'build_calls':buildcalls,'index':{'trained':bool(idx.trained),'size':len(idx),'dim':idx.dim,'graph_degree':idx.graph_degree,'dtype':str(idx.dtype)},'default_RMM_type':mrname,'default_CuPy_allocator':allocname,'stream_identity_class':'REQUESTED_STREAM','requested_stream':requested,'Cplusplus_internal_stream':'UNKNOWN','search_or_recall_or_performance':False,'peak_RSS_bytes_rusage':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024}
(ROOT/f'{arm}_result.json').write_text(json.dumps(result,indent=2)+'\n');record('CLEAN_EXIT',build_calls=buildcalls,qualification_only=True)
