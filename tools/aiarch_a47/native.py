"""Bounded official cuVS CAGRA native stages, called ONLY under the shared lock."""
import gc,hashlib,importlib.metadata,json,math,os,pathlib,sys,time
from budget_io import ROOT
assert os.environ.get('A47_GPU_LOCK_HELD')=='1'
os.sched_setaffinity(0,[0,2,4,6])
import numpy as np
import cupy as cp
import cuvs
import rmm
from rmm.allocators.cupy import rmm_cupy_allocator
from cuvs.neighbors import cagra
from cuvs.common import Resources
from cuvs.common.dataset import Dataset
assert importlib.metadata.version('cuvs-cu12')=='26.10.0'
assert cuvs.__git_commit__=='24ee1bf1cb17cad0ac611e39643af39ee1870124'
assert importlib.metadata.version('libcuvs-cu12')=='26.10.0'
assert cp.__version__=='14.0.1'
PRE=json.loads((ROOT/'preregistration.json').read_text());MODE=sys.argv[1]
cp.cuda.Device(0).use()
upstream=rmm.mr.CudaMemoryResource();pool=rmm.mr.PoolMemoryResource(upstream,initial_pool_size=512*1024**2,maximum_pool_size=10*1024**3);rmm.mr.set_current_device_resource(pool)
cp.cuda.set_allocator(rmm_cupy_allocator)
stream=cp.cuda.Stream(non_blocking=True);res=Resources(stream=stream.ptr)
base=np.load(ROOT/'base_fp32_unit.npy',mmap_mode='r');queries=np.load(ROOT/'queries_fp32_unit.npy',mmap_mode='r');gt=np.load(ROOT/'gt_ids.npy',mmap_mode='r');gtd=np.load(ROOT/'gt_distances.npy',mmap_mode='r')
def sync():cp.cuda.runtime.deviceSynchronize()
def write(name,d):
 (ROOT/name).write_text(json.dumps(d,indent=2)+'\n')
def safe():
 assert time.monotonic()<float(os.environ['A47_GPU_DEADLINE'])-25,'GPU_TIME_BUDGET'
def filehash(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def view(x):
 try:return cp.from_dlpack(x)
 except (AttributeError,TypeError):return cp.asarray(x)
def arrayhash(x):
 h=hashlib.sha256()
 for i in range(0,len(x),32768):h.update(cp.asnumpy(x[i:i+32768]).tobytes())
 sync();return h.hexdigest()
def make_params(b,arm,h=0):
 common={k:v for k,v in PRE['search_common'].items() if k!='k'}
 return cagra.SearchParams(**common,max_queries=b,algo='auto' if arm=='A' else 'single_cta',hashmap_mode='auto' if arm=='A' else 'small',hashmap_min_bitlen=0 if arm=='A' else h,thread_block_size=0 if arm=='A' else 128)
def requested(sp):
 return {'repr':repr(sp),'fields':{k:str(getattr(sp,k)) for k in ['max_queries','itopk_size','max_iterations','algo','team_size','search_width','min_iterations','thread_block_size','hashmap_mode','hashmap_min_bitlen','hashmap_max_fill_rate','num_random_samplings','rand_xor_mask']}}
def load_index():
 safe();t=time.monotonic();idx=cagra.Index();owner=Dataset();cagra.load(idx,str(ROOT/'cagra_glove.index'),out_dataset=owner,resources=res);sync()
 assert idx.trained and len(idx)==1183514 and idx.dim==100 and idx.graph_degree==64 and str(idx.dtype)=='float32'
 return idx,owner,time.monotonic()-t
class Buffers:
 def __init__(self,b):
  self.b=b;self.gq=cp.empty((b,100),dtype=cp.float32);self.gi=cp.empty((b,10),dtype=cp.uint32);self.gd=cp.empty((b,10),dtype=cp.float32)
  self.pi=cp.cuda.alloc_pinned_memory(b*10*4);self.pd=cp.cuda.alloc_pinned_memory(b*10*4);self.pq=cp.cuda.alloc_pinned_memory(b*100*4)
  self.hi=np.frombuffer(self.pi,dtype=np.uint32).reshape(b,10);self.hd=np.frombuffer(self.pd,dtype=np.float32).reshape(b,10);self.hq=np.frombuffer(self.pq,dtype=np.float32).reshape(b,100)
 def search(self,index,sp,q):
  cagra.search(sp,index,q,10,neighbors=self.gi,distances=self.gd,resources=res)
 def wall(self,index,sp,q):
  with stream:
   self.gq.set(q,stream=stream);self.search(index,sp,self.gq)
   self.gi.get(out=self.hi,stream=stream,blocking=False);self.gd.get(out=self.hd,stream=stream,blocking=False)
  sync()
def quality(index,sp,ids,b):
 safe();buf=Buffers(b);out_i=[];out_d=[];t=time.monotonic()
 for start in range(0,len(ids),b):
  chosen=ids[start:start+b];n=len(chosen)
  if n<b:
   supplement=[x for x in ids if x not in set(chosen)][:b-n];chosen=chosen+supplement
  np.copyto(buf.hq,queries[chosen]);buf.wall(index,sp,buf.hq);out_i.append(buf.hi[:n].copy());out_d.append(buf.hd[:n].copy())
 ni=np.concatenate(out_i);ds=np.concatenate(out_d);assert (ni<len(base)).all() and np.isfinite(ds).all();assert (np.diff(np.sort(ni,axis=1),axis=1)!=0).all()
 # Recompute exact cosine for returned IDs; threshold is publisher GT kth+0.001.
 reference=np.empty(ds.shape,dtype=np.float64)
 for start in range(0,len(ids),256):
  ix=ni[start:start+256];x=np.asarray(base[ix],dtype=np.float64);q=np.asarray(queries[ids[start:start+256]],dtype=np.float64);reference[start:start+len(ix)]=1-np.einsum('ijk,ik->ij',x,q)/(np.linalg.norm(x,axis=2)*np.linalg.norm(q,axis=1)[:,None])
 assert np.allclose(ds,reference,atol=1e-5,rtol=1e-4),'RETURN_DISTANCE_MISMATCH'
 hits=(reference<=np.asarray(gtd[ids,9],dtype=np.float64)[:,None]+.001).sum(axis=1);strict=np.array([np.isin(row,np.asarray(gt[qi,:10])).sum() for row,qi in zip(ni,ids)])
 return {'recall':float(hits.mean()/10),'strict_ID_recall':float(strict.mean()/10),'per_query_hits':hits.tolist(),'per_query_strict_hits':strict.tolist(),'query_ids':ids,'distances_max_abs_error':float(np.max(np.abs(ds-reference))),'evaluation_seconds':time.monotonic()-t,'output_ids_sha256':hashlib.sha256(ni.tobytes()).hexdigest(),'output_distances_sha256':hashlib.sha256(ds.tobytes()).hexdigest(),'actual_batch':b,'max_queries':sp.max_queries,'tail_pad_real_queries':(b-len(ids)%b)%b},ni,ds

def timed_sequences(index,sp,b,qcpu,qgpu):
 safe();buf=Buffers(b);sync();t=time.perf_counter_ns()
 for st in range(0,len(qcpu),b):
  with stream:buf.search(index,sp,qgpu[st:st+b])
  sync()
 service=(time.perf_counter_ns()-t)/1e9
 sync();t=time.perf_counter_ns()
 for st in range(0,len(qcpu),b):buf.wall(index,sp,qcpu[st:st+b])
 wall=(time.perf_counter_ns()-t)/1e9
 return {'GPU_resident_sync_host_search_seconds':service,'CPU_H2D_search_D2H_wall_seconds':wall,'queries':len(qcpu),'batches':len(qcpu)//b}

if MODE=='build_qualify':
 safe();assert not (ROOT/'build_attempt_started.json').exists(),'ONLY_ONE_FULL_BUILD_ALLOWED';None # actual build marker is written immediately before the unique API call
 props=cp.cuda.runtime.getDeviceProperties(0);assert 'RTX 4080' in props['name'].decode() and props['major']==8 and props['minor']==9
 device={'name':props['name'].decode(),'SM_count':props['multiProcessorCount'],'compute_capability':[props['major'],props['minor']],'driver_version':cp.cuda.runtime.driverGetVersion(),'runtime_version':cp.cuda.runtime.runtimeGetVersion(),'cupy':cp.__version__,'cuvs':importlib.metadata.version('cuvs-cu12'),'rmm':rmm.__version__,'cuvs_git_commit':cuvs.__git_commit__,'stream_ptr':stream.ptr,'timer':'sync-completed host service, not CUDA events','pool_initial_bytes':512*1024**2,'pool_maximum_bytes':10*1024**3}
 mapped=set()
 for line in pathlib.Path('/proc/self/maps').read_text().splitlines():
  part=line.split()[-1]
  if part.startswith('/') and '.so' in part and any(x in part for x in ['cuvs','cupy','rmm','libraft','libcuda','libcudart','nvrtc']):mapped.add(part)
 device['loaded_library_sha256']={p: filehash(p) for p in sorted(mapped) if pathlib.Path(p).is_file()}
 write('device_identity.json',device)
 with stream:
  can=cp.asarray(np.array([1.,2.,3.],dtype=np.float32));assert cp.asnumpy(can*2).tolist()==[2.,4.,6.]
  data=cp.asarray(base)
 sync();buildparams=cagra.IndexParams(metric='cosine',build_algo='ivf_pq',graph_degree=64,intermediate_graph_degree=128)
 write('build_attempt_started.json',{'monotonic':time.monotonic(),'request':PRE['build']});t=time.monotonic();index=cagra.build(buildparams,data,resources=res);sync();buildseconds=time.monotonic()-t
 assert len(index)==len(base) and index.dim==100 and index.graph_degree==64
 buildinfo={'status':'BUILT_ONCE','build_seconds':buildseconds,'request':PRE['build'],'params_repr':repr(buildparams),'exposed_defaults':{k:str(getattr(buildparams,k)) for k in ['intermediate_graph_degree','graph_degree','build_algo','metric','nn_descent_niter','refinement_rate'] if hasattr(buildparams,k)},'build_random_seed':'UNKNOWN_NOT_EXPOSED','actual_size':len(index),'actual_dim':index.dim,'graph_degree':index.graph_degree,'dtype':str(index.dtype)}
 graph=view(index.graph);dataset=view(index.dataset);buildinfo['graph_logical_sha256']=arrayhash(graph);buildinfo['index_dataset_logical_sha256']=arrayhash(dataset);buildinfo['index_dataset_shape']=list(dataset.shape)
 maxerror=0.
 for st in range(0,len(base),32768):maxerror=max(maxerror,float(np.max(np.abs(cp.asnumpy(dataset[st:st+32768])-base[st:st+32768]))))
 assert maxerror<=1e-5,'INDEX_DATASET_IDENTITY_CHANGED';buildinfo['dataset_vs_normalized_input_max_abs']=maxerror
 before={}
 for b in [1,256]:
  sp=make_params(b,'A');out,ni,ds=quality(index,sp,PRE['calibration_ids'][:256] if b==256 else PRE['canary_ids'],b)
  before[b]=(ni,ds);write(f'canary_before_reload_B{b}.json',out)
 t=time.monotonic();cagra.save(str(ROOT/'cagra_glove.index'),index,include_dataset=True,resources=res);sync();buildinfo['save_seconds']=time.monotonic()-t;buildinfo['serialized_bytes']=(ROOT/'cagra_glove.index').stat().st_size;buildinfo['serialized_sha256']=filehash(ROOT/'cagra_glove.index');write('build_index_identity.json',buildinfo)
 del dataset,graph,index,data;gc.collect();sync();index,owner,loadsec=load_index();buildinfo['load_seconds']=loadsec;buildinfo['loaded_owner']={'owning':owner.is_owning,'layout':owner.layout,'memory_type':owner.memory_type,'dtype':str(owner.dtype)}
 loadedgraph=view(index.graph);loadeddataset=view(index.dataset);assert arrayhash(loadedgraph)==buildinfo['graph_logical_sha256'];assert arrayhash(loadeddataset)==buildinfo['index_dataset_logical_sha256']
 for b in [1,256]:
  out,ni,ds=quality(index,make_params(b,'A'),PRE['calibration_ids'][:256] if b==256 else PRE['canary_ids'],b)
  assert np.array_equal(ni,before[b][0]) and np.allclose(ds,before[b][1],atol=1e-5,rtol=1e-4),'RELOAD_CANARY_CHANGED';out['reload_same_IDs']=True;write(f'canary_after_reload_B{b}.json',out)
 buildinfo['status']='PASS_BUILD_SAVE_LOAD_GRAPH_DATASET_CANARY';write('build_index_identity.json',buildinfo)
 # Precisely six fixed calibration configurations, no further candidates.
 cals=[]
 for b in [1,256]:
  for arm,h in [('A',0),('B',9),('B',11)]:
   sp=make_params(b,arm,h);out,ni,ds=quality(index,sp,PRE['calibration_ids'],b);out.update(arm=arm,h=h,requested=requested(sp));cals.append(out);write('calibration.json',{'status':'IN_PROGRESS','configurations':cals});print('CALIBRATION',b,arm,h,out['recall'],flush=True)
 eligible=[]
 for h in [9,11]:
  pairs=[(next(x for x in cals if x['actual_batch']==b and x['arm']=='A'),next(x for x in cals if x['actual_batch']==b and x['arm']=='B' and x['h']==h)) for b in [1,256]]
  if all(a['recall']>=.95 and z['recall']>=.95 and abs(a['recall']-z['recall'])<=.005 for a,z in pairs):eligible.append(h)
 if not eligible:
  write('calibration.json',{'status':'QUALITY_NO_GO','configurations':cals,'eligible_h':[]});print('QUALITY_NO_GO_CALIBRATION',flush=True);sys.exit(20)
 # Use complete host wall on calibration queries only for h selection.
 calids=PRE['calibration_ids'][:1792];assert len(set(calids))==1792
 pin=cp.cuda.alloc_pinned_memory(1792*100*4);qcpu=np.frombuffer(pin,dtype=np.float32).reshape(1792,100);np.copyto(qcpu,queries[calids]);qgpu=cp.asarray(qcpu);sync();cal_times=[]
 for h in eligible:
  perquery=[]
  for b in [1,256]:
   vals=[]
   for repeat in range(3):vals.append(timed_sequences(index,make_params(b,'B',h),b,qcpu,qgpu))
   med=np.median([v['CPU_H2D_search_D2H_wall_seconds'] for v in vals])/1792;perquery.append(med);cal_times.append({'h':h,'B':b,'values':vals,'median_wall_seconds_per_query':float(med)})
  score=math.sqrt(perquery[0]*perquery[1])
  next(x for x in cals if x['arm']=='B' and x['h']==h)['selection_score']=score
 scores={h:next(x['selection_score'] for x in cals if x['arm']=='B' and x['h']==h and 'selection_score' in x) for h in eligible};selected=min(eligible,key=lambda h:(scores[h],h))
 freeze={'status':'PASS_CALIBRATED_FROZEN_BEFORE_REPORT','selected_h':selected,'configurations':cals,'eligible_h':eligible,'selection_times':cal_times,'selection_scores':scores,'formal_parameters':{f'B{b}_{arm}':requested(make_params(b,arm,selected)) for b in [1,256] for arm in ['A','B']}}
 write('calibration.json',freeze);print('CALIBRATION_FROZEN_H',selected,flush=True)
 # Four report points, complete8000 report queries at the actual B/max_queries.
 reports=[]
 for b in [1,256]:
  for arm in ['A','B']:
   out,ni,ds=quality(index,make_params(b,arm,selected),PRE['report_ids'],b);out.update(arm=arm,h=selected if arm=='B' else 0);reports.append(out);np.savez(ROOT/'private_raw'/f'report_B{b}_{arm}.npz',query_ids=np.array(PRE['report_ids']),ids=ni,distances=ds);write('report_quality.json',{'status':'IN_PROGRESS','points':reports});print('REPORT_QUALITY',b,arm,out['recall'],flush=True)
 good=all(x['recall']>=.95 for x in reports) and all(abs(next(x['recall'] for x in reports if x['actual_batch']==b and x['arm']=='A')-next(x['recall'] for x in reports if x['actual_batch']==b and x['arm']=='B'))<=.005 for b in [1,256])
 write('report_quality.json',{'status':'PASS' if good else 'QUALITY_NO_GO','points':reports});sys.exit(0 if good else 20)
elif MODE=='measure':
 process=int(sys.argv[2]);assert json.loads((ROOT/'report_quality.json').read_text())['status']=='PASS';freeze=json.loads((ROOT/'calibration.json').read_text());h=freeze['selected_h'];index,owner,loadsec=load_index()
 pin=cp.cuda.alloc_pinned_memory(2048*100*4);qcpu=np.frombuffer(pin,dtype=np.float32).reshape(2048,100);np.copyto(qcpu,queries[PRE['timing_ids']]);qgpu=cp.asarray(qcpu);sync()
 out=ROOT/'private_raw'/f'process_{process}_timing.jsonl';warm=[];recordcount=0
 with out.open('w') as f:
  for b in PRE['process_batch_orders'][process]:
   for arm in ['A','B']:warm.append({'B':b,'arm':arm,'values':timed_sequences(index,make_params(b,arm,h),b,qcpu,qgpu)})
   # Same buffer policy; ABBA/BAAB alternating, ten paired blocks per batch.
   for block,order in enumerate(PRE['orders']):
    for position,arm in enumerate(order):
     vals=timed_sequences(index,make_params(b,arm,h),b,qcpu,qgpu);row={'process':process,'B':b,'block':block,'order':order,'position':position,'arm':arm,'h':h if arm=='B' else 0,'timer':'un-instrumented complete synchronized host boundaries','values':vals};f.write(json.dumps(row)+'\n');f.flush();recordcount+=1
    print('MEASURE_BLOCK',process,b,block,flush=True)
 write(f'measure_process_{process}.json',{'status':'PASS','process':process,'loaded_same_index_sha256':filehash(ROOT/'cagra_glove.index'),'load_seconds':loadsec,'warmup':warm,'records':recordcount,'stream_policy':'explicit stream/resources plus device-completion sync','service_is_not_kernel_only':True,'selected_h':h})
else:raise ValueError(MODE)
safe();sync();print('NATIVE_STAGE_PASS',MODE,flush=True)
