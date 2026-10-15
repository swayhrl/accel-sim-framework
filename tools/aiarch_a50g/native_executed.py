"""A50G fixed real-input stages. Default allocators/default streams exclusively."""
import os,sys,pathlib,json,hashlib,importlib.metadata,math,time,gc,resource,faulthandler
assert os.environ.get('A50G_GPU_LOCK_HELD')=='1';faulthandler.enable();resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,[0,2,4,6])
ROOT=pathlib.Path(os.environ['A50G_OUTPUT']);OLD=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');mode=sys.argv[1]
import numpy as np
import cupy as cp
import cuvs
import rmm
from cuvs.common import Resources
from cuvs.common.dataset import Dataset,make_device_padded_dataset
from cuvs.neighbors import cagra
assert cuvs.__git_commit__=='24ee1bf1cb17cad0ac611e39643af39ee1870124' and importlib.metadata.version('cuvs-cu12')=='26.10.0' and cp.__version__=='14.0.1'
cp.cuda.Device(0).use();assert cp.cuda.get_current_stream().ptr==cp.cuda.Stream.null.ptr;res=Resources()
PRE=json.loads((ROOT/'frozen_preregistration.json').read_text());base=np.load(OLD/'base_fp32_unit.npy',mmap_mode='r');query=np.load(OLD/'queries_fp32_unit.npy',mmap_mode='r');gt=np.load(OLD/'gt_ids.npy',mmap_mode='r');gtd=np.load(OLD/'gt_distances.npy',mmap_mode='r')
assert base.shape==(1183514,100) and base.dtype==np.float32 and query.shape==(10000,100)

def write(name,d):
 (ROOT/name).write_text(json.dumps(d,indent=2)+'\n')
def note(phase,**kw):
 row={'phase':phase,'mode':mode,**kw};print(json.dumps(row),flush=True)
 with (ROOT/'raw'/('events_'+mode+('_'+sys.argv[2] if len(sys.argv)>2 else '')+'.jsonl')).open('a') as f:f.write(json.dumps(row)+'\n')
def sync():res.sync();cp.cuda.runtime.deviceSynchronize()
def safe():assert time.monotonic()<float(os.environ['A50G_DEADLINE'])-25,'LOCK_DEADLINE'
def sha_file(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def fields(index,label):
 out={};errors={};dtype=None
 for k,fn in [('trained',lambda:bool(index.trained)),('size',lambda:int(len(index))),('dim',lambda:int(index.dim)),('graph_degree',lambda:int(index.graph_degree)),('dtype',lambda:index.dtype)]:
  try:
   v=fn()
   if k=='dtype':dtype=v;out['dtype_repr']=repr(v);out['dtype_normalized']=str(np.dtype(v))
   else:out[k]=v
   note('INDEX_FIELD',label=label,field=k,value=repr(v) if k=='dtype' else v)
  except Exception as e:errors[k]=repr(e);note('FIELD_READ_ERROR',label=label,field=k,error=repr(e))
 predicates={'trained':out.get('trained') is True,'size':out.get('size')==1183514,'dim':out.get('dim')==100,'graph_degree':out.get('graph_degree')==64,'dtype':dtype is not None and np.dtype(dtype)==np.dtype('float32')}
 record={'fields':out,'assert_predicate_map':predicates,'errors':errors};note('INDEX_PREDICATES',label=label,**record)
 if errors or not all(predicates.values()):raise RuntimeError('INVALID_REQUIRED_INDEX_FIELDS '+json.dumps(record))
 return record

def params(b,arm,h=0):
 return cagra.SearchParams(max_queries=b,itopk_size=128,search_width=1,max_iterations=64,min_iterations=0,hashmap_max_fill_rate=.5,persistent=False,num_random_samplings=1,rand_xor_mask=0x128394,team_size=0,algo='auto' if arm=='A' else 'single_cta',hashmap_mode='auto' if arm=='A' else 'small',thread_block_size=0 if arm=='A' else 128,hashmap_min_bitlen=0 if arm=='A' else h)
class Buffers:
 def __init__(self,b):
  self.b=b;self.gq=cp.empty((b,100),dtype=cp.float32);self.gi=cp.empty((b,10),dtype=cp.uint32);self.gd=cp.empty((b,10),dtype=cp.float32)
  self.pq=cp.cuda.alloc_pinned_memory(b*100*4);self.pi=cp.cuda.alloc_pinned_memory(b*10*4);self.pd=cp.cuda.alloc_pinned_memory(b*10*4)
  self.hq=np.frombuffer(self.pq,dtype=np.float32).reshape(b,100);self.hi=np.frombuffer(self.pi,dtype=np.uint32).reshape(b,10);self.hd=np.frombuffer(self.pd,dtype=np.float32).reshape(b,10)
 def search(self,index,sp,gq):cagra.search(sp,index,gq,10,neighbors=self.gi,distances=self.gd,resources=res)
 def wall(self,index,sp,hq):
  self.gq.set(hq);cp.cuda.runtime.deviceSynchronize();self.search(index,sp,self.gq);sync();self.gi.get(out=self.hi);self.gd.get(out=self.hd);cp.cuda.runtime.deviceSynchronize()

def evaluate(index,sp,ids,b,label):
 safe();buf=Buffers(b);neighbors=[];distances=[]
 for start in range(0,len(ids),b):
  selected=ids[start:start+b];n=len(selected)
  if n<b:
   used=set(selected);selected=selected+[x for x in ids if x not in used][:b-n]
  np.copyto(buf.hq,query[selected]);buf.wall(index,sp,buf.hq);neighbors.append(buf.hi[:n].copy());distances.append(buf.hd[:n].copy())
 ni=np.concatenate(neighbors);ds=np.concatenate(distances);assert (ni<len(base)).all() and np.isfinite(ds).all(),'INVALID_SEARCH_ID_DISTANCE';assert (np.diff(np.sort(ni,axis=1),axis=1)!=0).all(),'DUPLICATE_SEARCH_ID'
 ref=np.empty(ds.shape,dtype=np.float64)
 for start in range(0,len(ids),256):
  ix=ni[start:start+256];x=np.asarray(base[ix],dtype=np.float64);q=np.asarray(query[ids[start:start+256]],dtype=np.float64);ref[start:start+len(ix)]=1-np.einsum('ijk,ik->ij',x,q)/(np.linalg.norm(x,axis=2)*np.linalg.norm(q,axis=1)[:,None])
 assert np.allclose(ds,ref,atol=1e-5,rtol=1e-4),'GPU_DISTANCE_NUMERIC_GATE'
 hits=(ref<=np.asarray(gtd[ids,9],dtype=np.float64)[:,None]+.001).sum(axis=1);strict=np.array([np.isin(row,gt[qi,:10]).sum() for row,qi in zip(ni,ids)])
 out={'label':label,'B':b,'max_queries':sp.max_queries,'query_ids':ids,'query_count':len(ids),'recall_at10':float(hits.mean()/10),'strict_ID_recall':float(strict.mean()/10),'per_query_hits':hits.tolist(),'per_query_strict_hits':strict.tolist(),'max_abs_distance_error':float(np.max(np.abs(ds-ref))),'neighbors_sha256':hashlib.sha256(ni.tobytes()).hexdigest(),'distances_sha256':hashlib.sha256(ds.tobytes()).hexdigest(),'tail_real_query_pad_count':(b-len(ids)%b)%b,'requested_params':repr(sp)}
 np.savez(ROOT/'raw'/f'{label}_outputs.npz',query_ids=np.array(ids,dtype=np.int32),neighbors=ni,distances=ds)
 note('QUALITY_OBSERVATION',label=label,B=b,recall=out['recall_at10'],max_abs_error=out['max_abs_distance_error']);return out,ni,ds

def sequences(index,sp,b,cpuq,gpuq):
 safe();buf=Buffers(b);sync();t=time.perf_counter_ns()
 for start in range(0,len(cpuq),b):buf.search(index,sp,gpuq[start:start+b]);sync()
 service=(time.perf_counter_ns()-t)/1e9;sync();t=time.perf_counter_ns()
 for start in range(0,len(cpuq),b):buf.wall(index,sp,cpuq[start:start+b])
 wall=(time.perf_counter_ns()-t)/1e9
 return {'resident_sync_host_service_seconds':service,'CPU_ready_H2D_search_D2H_wall_seconds':wall,'queries':len(cpuq),'batches':len(cpuq)//b}

def loaded():
 safe();t=time.monotonic();index=cagra.Index();owner=Dataset();cagra.load(index,str(ROOT/'glove.index'),out_dataset=owner,resources=res);sync();f=fields(index,'reloaded');note('LOAD_PASS',owner_layout=owner.layout,owner_is_owning=owner.is_owning,owner_memory=owner.memory_type)
 return index,owner,{'budget_load_elapsed_seconds':time.monotonic()-t,'fields':f,'owner':{'layout':owner.layout,'is_owning':owner.is_owning,'memory_type':owner.memory_type}}

note('IMPORT_AND_DEFAULT_POLICY_PASS',cuvs=cuvs.__version__,cuvs_commit=cuvs.__git_commit__,cupy=cp.__version__,RMM_type=type(rmm.mr.get_current_device_resource()).__name__,CuPy_allocator=str(getattr(cp.cuda.get_allocator(),'__module__',None))+'.'+str(getattr(cp.cuda.get_allocator(),'__name__','unknown')),default_stream=cp.cuda.get_current_stream().ptr==cp.cuda.Stream.null.ptr)
if mode=='build_qualify':
 assert not (ROOT/'full_build_enter.json').exists(),'UNIQUE_FULL_BUILD_ALREADY_CONSUMED';safe()
 props=cp.cuda.runtime.getDeviceProperties(0);name=props['name'].decode() if isinstance(props['name'],bytes) else props['name'];assert 'RTX 4080' in name
 write('device_identity.json',{'name':name,'SM':props['multiProcessorCount'],'CC':[props['major'],props['minor']],'driver_API':cp.cuda.runtime.driverGetVersion(),'runtime_API':cp.cuda.runtime.runtimeGetVersion(),'RMM':'DEFAULT_NO_OVERRIDE','CuPy_allocator':'DEFAULT_NO_OVERRIDE','cuVS_resources':'Resources_DEFAULT','stream_identity':'REQUESTED_DEFAULT; internal_Cpp_handle_UNKNOWN'})
 g=cp.asarray(base);sync();ds=make_device_padded_dataset(g,resources=res);sync();note('FULL_INPUT_READY',shape=list(base.shape),dtype=str(base.dtype),dataset_layout=ds.layout,is_owning=ds.is_owning)
 bp=cagra.IndexParams(metric='cosine',build_algo='ivf_pq',graph_degree=64,intermediate_graph_degree=128);write('full_build_enter.json',{'full_API_calls':1,'shape':list(base.shape),'params':{'metric':'cosine','build_algo':'ivf_pq','graph_degree':64,'intermediate_graph_degree':128},'monotonic':time.monotonic()});note('FULL_BUILD_ENTER')
 t=time.monotonic();index=cagra.build(bp,ds,resources=res);sync();build_seconds=time.monotonic()-t;fi=fields(index,'built');write('build_observation.json',{'status':'BUILD_FIELDS_PASS','budget_build_elapsed_seconds':build_seconds,'fields':fi,'params_repr':repr(bp),'seed':'UNKNOWN_NOT_EXPOSED','graph_logical_hash':'UNKNOWN_PUBLIC_VIEW_NOT_REQUIRED'})
 # Two fixed functional configurations. B256 padding uses genuine calibration IDs.
 before={};canary_records=[];exact=np.load(OLD/'canary_exact_distances.npy');assert exact.shape==(32,10)
 for b in [1,256]:
  ids=PRE['canary_ids'] if b==1 else PRE['calibration_ids'][:256];out,ni,dd=evaluate(index,params(b,'A'),ids,b,f'canary_before_B{b}');out['canary_first32_recall']=float(np.asarray(out['per_query_hits'][:32]).mean()/10);out['full_base_FP64_reference_k10_max_abs_vs_GT']=float(np.max(np.abs(exact[:,9]-np.asarray(gtd[PRE['canary_ids'],9]))));assert np.allclose(exact[:,9],gtd[PRE['canary_ids'],9],atol=1e-5,rtol=1e-4),'FROZEN_FULL_BASE_ORACLE_IDENTITY';before[b]=(ni,dd);canary_records.append(out)
 write('functional_canary.json',{'status':'BEFORE_SAVE_PASS','configurations':canary_records,'full_base_exact_reference_reused_readonly':True})
 safe();t=time.monotonic();cagra.save(str(ROOT/'glove.index'),index,include_dataset=True,resources=res);sync();saved={'status':'SAVED','bytes':(ROOT/'glove.index').stat().st_size,'sha256':sha_file(ROOT/'glove.index'),'budget_save_elapsed_seconds':time.monotonic()-t,'include_dataset':True,'logical_graph_hash':'UNKNOWN_PUBLIC_VIEW_NOT_REQUIRED'};write('index_identity.json',saved)
 del index,ds,g;gc.collect();sync();index,owner,li=loaded();saved['load']=li
 for b in [1,256]:
  ids=PRE['canary_ids'] if b==1 else PRE['calibration_ids'][:256];out,ni,dd=evaluate(index,params(b,'A'),ids,b,f'canary_after_B{b}');assert np.array_equal(ni,before[b][0]) and np.allclose(dd,before[b][1],atol=1e-5,rtol=1e-4),'RELOAD_RESULTS_CHANGED';out['same_IDs_as_before']=True;out['full_base_reference_count']=1183514;canary_records.append(out)
 saved['status']='PASS_SAME_SERIALIZED_INDEX_RELOADED';write('index_identity.json',saved);write('functional_canary.json',{'status':'PASS','configurations':canary_records,'functional_configuration_count':2,'oracle':'frozen full_base_FP64_exact32 + original GT tie threshold; returned-ID distances separately recomputed'})
 cal=[]
 for b in [1,256]:
  for arm,h in [('A',0),('B',9),('B',11)]:
   out,ni,dd=evaluate(index,params(b,arm,h),PRE['calibration_ids'],b,f'cal_B{b}_{arm}_h{h}');out.update(arm=arm,h=h);cal.append(out);write('calibration.json',{'status':'IN_PROGRESS','configurations':cal})
 eligible=[]
 for h in [9,11]:
  pairs=[(next(x for x in cal if x['B']==b and x['arm']=='A'),next(x for x in cal if x['B']==b and x['arm']=='B' and x['h']==h)) for b in [1,256]]
  if all(a['recall_at10']>=.95 and z['recall_at10']>=.95 and abs(a['recall_at10']-z['recall_at10'])<=.005 for a,z in pairs):eligible.append(h)
 if not eligible:write('calibration.json',{'status':'QUALITY_NO_GO','eligible_h':[],'configurations':cal});sys.exit(20)
 # Original frozen calibration timing subset1792, no duplicated timing vectors.
 calids=PRE['calibration_timing_query_ids'];assert len(calids)==1792 and len(set(calids))==1792 and set(calids)<=set(PRE['calibration_ids'])
 pin=cp.cuda.alloc_pinned_memory(len(calids)*100*4);cpuq=np.frombuffer(pin,dtype=np.float32).reshape(len(calids),100);np.copyto(cpuq,query[calids]);gpuq=cp.asarray(cpuq);sync();scores={};cal_times=[]
 for h in eligible:
  perquery=[]
  for b in [1,256]:
   warm=sequences(index,params(b,'B',h),b,cpuq,gpuq);vals=[sequences(index,params(b,'B',h),b,cpuq,gpuq) for _ in range(3)];median=float(np.median([x['CPU_ready_H2D_search_D2H_wall_seconds'] for x in vals]))/len(calids);perquery.append(median);cal_times.append({'h':h,'B':b,'warmup':warm,'raw':vals,'median_wall_perquery':median})
  scores[h]=math.sqrt(perquery[0]*perquery[1])
 chosen=min(eligible,key=lambda h:(scores[h],h));write('calibration.json',{'status':'PASS_FROZEN_BEFORE_REPORT','chosen_h':chosen,'eligible_h':eligible,'scores':scores,'timing':cal_times,'configurations':cal,'search_configuration_count':6});note('CALIBRATION_FROZEN',chosen_h=chosen)
 reports=[]
 for b in [1,256]:
  for arm in ['A','B']:
   out,ni,dd=evaluate(index,params(b,arm,chosen),PRE['report_ids'],b,f'report_B{b}_{arm}');out.update(arm=arm,h=0 if arm=='A' else chosen);reports.append(out);write('report_quality.json',{'status':'IN_PROGRESS','points':reports})
 good=all(x['recall_at10']>=.95 for x in reports) and all(abs(next(x['recall_at10'] for x in reports if x['B']==b and x['arm']=='A')-next(x['recall_at10'] for x in reports if x['B']==b and x['arm']=='B'))<=.005 for b in [1,256])
 write('report_quality.json',{'status':'PASS' if good else 'QUALITY_NO_GO','points':reports});sys.exit(0 if good else 20)
elif mode=='measure':
 proc=int(sys.argv[2]);assert json.loads((ROOT/'report_quality.json').read_text())['status']=='PASS';chosen=json.loads((ROOT/'calibration.json').read_text())['chosen_h'];index,owner,li=loaded();assert sha_file(ROOT/'glove.index')==json.loads((ROOT/'index_identity.json').read_text())['sha256']
 ids=PRE['timing_ids'];pin=cp.cuda.alloc_pinned_memory(2048*100*4);cpuq=np.frombuffer(pin,dtype=np.float32).reshape(2048,100);np.copyto(cpuq,query[ids]);gpuq=cp.asarray(cpuq);sync();warm=[];count=0
 with (ROOT/'raw'/f'process_{proc}_timing.jsonl').open('w') as f:
  for b in PRE['process_batch_orders'][proc]:
   for arm in ['A','B']:warm.append({'B':b,'arm':arm,'values':sequences(index,params(b,arm,chosen),b,cpuq,gpuq)})
   for block,order in enumerate(PRE['orders']):
    for position,arm in enumerate(order):
     value=sequences(index,params(b,arm,chosen),b,cpuq,gpuq);row={'process':proc,'B':b,'block':block,'order':order,'position':position,'arm':arm,'chosen_h':chosen,'values':value};f.write(json.dumps(row)+'\n');f.flush();count+=1
    note('FORMAL_BLOCK_COMPLETE',process=proc,B=b,block=block)
 write(f'process_{proc}_receipt.json',{'status':'PASS','records':count,'warmup':warm,'load':li,'same_index_sha256':json.loads((ROOT/'index_identity.json').read_text())['sha256'],'service_is_synchronized_host_not_pure_kernel':True});note('MEASUREMENT_PROCESS_PASS',process=proc,records=count)
else:raise ValueError(mode)
