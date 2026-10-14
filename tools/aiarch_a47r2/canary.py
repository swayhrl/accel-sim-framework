"""One approved tiny CAGRA build; fields recorded before independent predicates."""
import os,sys,json,pathlib,hashlib,faulthandler,resource,importlib.metadata
assert os.environ.get('A47R2_GPU_LOCK_HELD')=='1';faulthandler.enable();resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,[0,2])
ROOT=pathlib.Path(os.environ['A47R2_OUTPUT']);arm=sys.argv[1];assert arm in ['C0','C1']
def emit(phase,**data):
 row={'arm':arm,'phase':phase,**data};print(json.dumps(row),flush=True)
 with (ROOT/f'{arm}_events.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def callable_label(obj):return str(getattr(obj,'__module__',None))+'.'+str(getattr(obj,'__name__',type(obj).__name__))
import numpy as np
import cupy as cp
import cuvs
import rmm
from cuvs.common import Resources
from cuvs.common.dataset import make_device_padded_dataset
from cuvs.neighbors import cagra
assert importlib.metadata.version('cuvs-cu12')=='26.10.0' and cp.__version__=='14.0.1' and cuvs.__git_commit__=='24ee1bf1cb17cad0ac611e39643af39ee1870124'
emit('IMPORT_PASS',python=sys.version.split()[0],cuvs=importlib.metadata.version('cuvs-cu12'),cuvs_commit=cuvs.__git_commit__,rmm=importlib.metadata.version('rmm-cu12'),cupy=cp.__version__,numpy=np.__version__)
cp.cuda.Device(0).use();props=cp.cuda.runtime.getDeviceProperties(0);name=props['name'].decode() if isinstance(props['name'],bytes) else props['name'];assert 'RTX 4080' in name
mr=rmm.mr.get_current_device_resource();mrtype=type(mr).__module__+'.'+type(mr).__name__;allocator=callable_label(cp.cuda.get_allocator())
x=np.random.default_rng(20261014).standard_normal((1024,100),dtype=np.float32);x/=np.linalg.norm(x,axis=1)[:,None];sha=hashlib.sha256(x.tobytes()).hexdigest();assert sha=='01a2c2f8a7e56b7a440fa183734d4297a1945a3dbbd6baedb27c1c3695b2478c','FROZEN_INPUT_IDENTITY'
assert cp.cuda.get_current_stream().ptr==cp.cuda.Stream.null.ptr;g=cp.asarray(x);cp.cuda.runtime.deviceSynchronize();assert np.array_equal(cp.asnumpy(g),x)
emit('GPU_INPUT_PASS',input_sha256=sha,shape=list(x.shape),dtype=str(x.dtype),default_CuPy_stream_preparation=True,default_RMM_type=mrtype,default_CuPy_allocator=allocator,device=name,SM=props['multiProcessorCount'],driver_API=cp.cuda.runtime.driverGetVersion(),runtime_API=cp.cuda.runtime.runtimeGetVersion())
stream_owner=None
if arm=='C0':res=Resources();requested='DEFAULT_RESOURCES_STREAM'
else:stream_owner=cp.cuda.Stream(non_blocking=True);res=Resources(stream=stream_owner.ptr);requested='EXPLICIT_NONBLOCKING_CUPY_STREAM'
ds=make_device_padded_dataset(g,resources=res);res.sync();cp.cuda.runtime.deviceSynchronize();assert ds.layout=='padded' and ds.memory_type=='device' and ds.is_owning is False
emit('PADDED_DATASET_PASS',layout=ds.layout,is_owning=ds.is_owning,memory_type=ds.memory_type,dtype=str(ds.dtype),resource_stream={'classification':'REQUESTED_STREAM','value':requested,'Cplusplus_actual_internal_handle':'UNKNOWN','explicit_Python_stream_owner_retained':stream_owner is not None},owners_retained=['x','g','ds','res','stream_owner_if_C1'])
params=cagra.IndexParams(metric='cosine',build_algo='ivf_pq',graph_degree=64,intermediate_graph_degree=128)
emit('BUILD_ENTER',build_calls=1,params={'metric':'cosine','build_algo':'ivf_pq','graph_degree':64,'intermediate_graph_degree':128})
idx=cagra.build(params,ds,resources=res);res.sync();cp.cuda.runtime.deviceSynchronize();emit('BUILD_RETURN_SYNCHRONIZED')
fields={};errors={};dtype_value=None
readers={'trained':lambda:bool(idx.trained),'size':lambda:int(len(idx)),'dim':lambda:int(idx.dim),'graph_degree':lambda:int(idx.graph_degree),'dtype':lambda:idx.dtype}
for key,reader in readers.items():
 try:
  value=reader()
  if key=='dtype':dtype_value=value;fields['dtype_repr']=repr(value);fields['dtype_normalized']=str(np.dtype(value));emit('FIELD_VALUE',field='dtype',dtype_repr=fields['dtype_repr'],dtype_normalized=fields['dtype_normalized'])
  else:fields[key]=value;emit('FIELD_VALUE',field=key,value=value)
 except Exception as e:errors[key]=repr(e);emit('FIELD_READ_ERROR',field=key,error=repr(e))
predicates={'trained':fields.get('trained') is True,'size':fields.get('size')==1024,'dim':fields.get('dim')==100,'graph_degree':fields.get('graph_degree')==64,'dtype':False}
if 'dtype' not in errors:
 try:predicates['dtype']=bool(np.dtype(dtype_value)==np.dtype('float32'))
 except Exception as e:errors['dtype_compare']=repr(e)
qualified=not errors and all(predicates.values());emit('ASSERT_PREDICATE_MAP',fields=fields,assert_predicate_map=predicates,read_errors=errors,qualified=qualified)
result={'arm':arm,'status':'PASS' if qualified else 'STOP_REAL_FIELDS','input_sha256':sha,'fields':fields,'assert_predicate_map':predicates,'field_read_errors':errors,'build_calls':1,'resource_stream_requested':requested,'Cplusplus_internal_stream':'UNKNOWN','default_RMM_type':mrtype,'default_CuPy_allocator':allocator,'no_allocator_or_pool_overrides':True,'dtype_test':'np.dtype(idx.dtype)==np.dtype(float32)','application_search_recall_performance':'NOT_RUN'}
if not qualified:
 (ROOT/f'{arm}_result.json').write_text(json.dumps(result,indent=2)+'\n');sys.exit(20)
emit('BUILD_FIELDS_PASS',fields=fields)
# Optional public-view diagnostics only; no search/queries/additional build.
try:
 graph_owner=idx.graph
 try:graph=cp.from_dlpack(graph_owner)
 except (AttributeError,TypeError):graph=cp.asarray(graph_owner)
 res.sync();cp.cuda.runtime.deviceSynchronize();graph_cpu=cp.asnumpy(graph)
 optional={'status':'OBSERVED','shape':list(graph_cpu.shape),'dtype':str(graph_cpu.dtype),'min_ID':int(graph_cpu.min()),'max_ID':int(graph_cpu.max()),'shape_matches':graph_cpu.shape==(1024,64),'IDs_in_range':bool((graph_cpu>=0).all() and (graph_cpu<1024).all()),'logical_sha256':hashlib.sha256(graph_cpu.tobytes()).hexdigest(),'not_search_or_numerical_recall_qualification':True}
 if not optional['shape_matches'] or not optional['IDs_in_range']:optional['status']='OPTIONAL_INVALID_GRAPH_OBSERVED'
except Exception as e:optional={'status':'OPTIONAL_NOT_QUALIFIED','error':repr(e)}
result['optional_graph']=optional;emit('OPTIONAL_GRAPH',**optional);res.sync();cp.cuda.runtime.deviceSynchronize();result['peak_RSS_bytes_rusage']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024
(ROOT/f'{arm}_result.json').write_text(json.dumps(result,indent=2)+'\n');emit('CLEAN_EXIT',status='PASS',build_calls=1)
