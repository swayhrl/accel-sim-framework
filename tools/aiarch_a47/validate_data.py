"""CPU-only whole HDF5 validation, deterministic split and full-base canary truth."""
import hashlib,json,os,pathlib,resource,time
from budget_io import ROOT,check_disk
os.sched_setaffinity(0,[0,2,4,6]);os.environ['HDF5_PLUGIN_PRELOAD']='::'
import numpy as np
import h5py
started=time.monotonic();p=ROOT/'downloads/glove-100-angular.hdf5';rec=json.loads((ROOT/'data_download_receipt.json').read_text());assert rec['status']=='PASS'
def filehash(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
assert filehash(p)==rec['sha256']
order=sorted(range(10000),key=lambda i:hashlib.sha256(('20261014:'+str(i)).encode()).digest());cal=order[:2000];report=order[2000:];timed=report[:2048];canary=cal[:32]
assert not set(cal)&set(report) and len(set(timed))==2048
pre={'status':'PREREGISTERED_BEFORE_ANY_GPU_RESULT','split_rule':'SHA256 UTF8(20261014:decimal_index), ascending digest','calibration_ids':cal,'report_ids':report,'timing_ids':timed,'canary_ids':canary,'split_sha256':hashlib.sha256(json.dumps(order,separators=(',',':')).encode()).hexdigest(),'timing_ids_sha256':hashlib.sha256(json.dumps(timed,separators=(',',':')).encode()).hexdigest(),'FP32_distance_atol':1e-5,'FP32_distance_rtol':1e-4,'quality_recall':.95,'same_batch_max_recall_difference':.005,'tie_metric':'publisher ann-benchmarks knn absolute threshold GT_distance_k10+0.001; recompute returned-ID cosine on CPU; also strict ID recall as supplementary','publisher_metric_source_blob':'e654f1c85f1b621092d8c86d84ce8da004642381','build':{'metric':'cosine','build_algo':'ivf_pq','graph_degree':64,'intermediate_graph_degree':128,'FP32_uncompressed':True,'build_count_limit':1,'exposed_seed':'UNKNOWN_UNLESS_API_EXPOSES'},'search_common':{'k':10,'itopk_size':128,'search_width':1,'max_iterations':64,'min_iterations':0,'hashmap_max_fill_rate':.5,'persistent':False,'num_random_samplings':1,'rand_xor_mask':0x128394,'team_size':0},'calibration_configs':[{'B':b,'arm':a,'h':h} for b in [1,256] for a,h in [('A',0),('B',9),('B',11)]],'functional_configs':[{'B':1,'arm':'A'},{'B':256,'arm':'A'}],'formal_points':4,'formal_processes':3,'blocks_per_batch_per_process':10,'orders':['ABBA' if i%2==0 else 'BAAB' for i in range(10)],'process_batch_orders':[[1,256],[256,1],[1,256]],'timing_query_count':2048,'warmup':'one complete resident-search and host-wall sequence for each point per fresh process','service_timer':'GPU-resident queries, synchronization-completed host search boundary, includes wrapper/planner; not pure kernel or CUDA events','wall_timer':'preallocated pinned CPU query batch ready -> H2D -> search -> D2H both IDs/distances -> result ready; one batch completion sync','allocator':'same RMM pool initial512MiB maximum10GiB, CuPy and C++ RMM, context margin2GiB; exact API qualification under lock','stream':'one explicit nonblocking CuPy stream + cuVS Resources(stream.ptr), device sync at measurement boundaries','CPU_affinity':[0,2,4,6],'normalization':'raw bytes preserved; CPU FP32 unit-norm normalization, cosine semantics unchanged','no_report_lookahead':True}
(ROOT/'preregistration.json').write_text(json.dumps(pre,indent=2)+'\n');fields={}
with h5py.File(p,'r') as f:
 assert set(f.keys())=={'train','test','neighbors','distances'},list(f.keys())
 for name in f:
  assert isinstance(f.get(name,getlink=True),h5py.HardLink);x=f[name];assert isinstance(x,h5py.Dataset) and not x.external and not x.is_virtual and x.dtype.kind!='O'
  dcpl=x.id.get_create_plist()
  for i in range(dcpl.get_nfilters()):assert dcpl.get_filter(i)[0] in range(1,7),'UNKNOWN_HDF5_FILTER'
  fields[name]={'shape':list(x.shape),'dtype':str(x.dtype),'chunks':x.chunks,'compression':x.compression}
 assert f['train'].shape==(1183514,100) and f['test'].shape==(10000,100) and f['neighbors'].shape==f['distances'].shape==(10000,100)
 assert f['train'].dtype==f['test'].dtype==np.dtype('float32')
 assert f['neighbors'].dtype.kind in 'iu' and f['distances'].dtype.kind=='f'
 attrs={k:str(v) for k,v in f.attrs.items()};assert attrs.get('distance')=='angular',attrs
 base=np.lib.format.open_memmap(ROOT/'base_fp32_unit.npy',mode='w+',dtype=np.float32,shape=f['train'].shape)
 h=hashlib.sha256();minnorm=float('inf');maxnorm=0.;maxunit=0.
 for st in range(0,len(base),32768):
  x=f['train'][st:st+32768];assert np.isfinite(x).all();h.update(x.tobytes());norm=np.linalg.norm(x,axis=1);assert (norm>0).all(),'ZERO_NORM_BASE';minnorm=min(minnorm,float(norm.min()));maxnorm=max(maxnorm,float(norm.max()));base[st:st+len(x)]=x/norm[:,None];maxunit=max(maxunit,float(np.max(np.abs(np.linalg.norm(base[st:st+len(x)],axis=1)-1))));check_disk()
 base.flush();fields['train']['logical_sha256']=h.hexdigest();rawq=f['test'][:];assert np.isfinite(rawq).all();qnorm=np.linalg.norm(rawq,axis=1);assert (qnorm>0).all(),'ZERO_NORM_QUERY';q=rawq/qnorm[:,None];np.save(ROOT/'queries_fp32_unit.npy',q);fields['test']['logical_sha256']=hashlib.sha256(rawq.tobytes()).hexdigest()
 gt=f['neighbors'][:];gtd=f['distances'][:];assert (gt>=0).all() and (gt<len(base)).all() and np.isfinite(gtd).all();assert np.all(np.diff(np.sort(gt,axis=1),axis=1)!=0);assert np.all(np.diff(gtd,axis=1)>=-1e-7),'GT_ORDER';np.save(ROOT/'gt_ids.npy',gt);np.save(ROOT/'gt_distances.npy',gtd)
 fields['neighbors']['logical_sha256']=hashlib.sha256(gt.tobytes()).hexdigest();fields['distances']['logical_sha256']=hashlib.sha256(gtd.tobytes()).hexdigest()
 # Exact full-base cosine from original vectors in FP64, not local subset truth.
 qc=rawq[canary].astype(np.float64);qc/=np.linalg.norm(qc,axis=1)[:,None];best_d=np.full((32,10),np.inf);best_i=np.full((32,10),-1,dtype=np.int64)
 for st in range(0,len(base),32768):
  x=f['train'][st:st+32768].astype(np.float64);x/=np.linalg.norm(x,axis=1)[:,None];ds=1-qc@x.T;which=np.argpartition(ds,9,axis=1)[:,:10];values=np.take_along_axis(ds,which,axis=1);all_d=np.concatenate((best_d,values),axis=1);all_i=np.concatenate((best_i,which+st),axis=1);sel=np.argsort(all_d,axis=1)[:,:10];best_d=np.take_along_axis(all_d,sel,axis=1);best_i=np.take_along_axis(all_i,sel,axis=1)
 assert np.allclose(best_d[:,9],gtd[canary,9],atol=1e-5,rtol=1e-4),'FULL_BASE_GT_COSINE_MISMATCH'
 np.save(ROOT/'canary_exact_ids.npy',best_i);np.save(ROOT/'canary_exact_distances.npy',best_d)
 numeric={'full_base_exact_canary_queries':32,'full_base_count':len(base),'GT_k10_threshold_max_abs_error':float(np.max(np.abs(best_d[:,9]-gtd[canary,9]))),'exact_top10_ids':best_i.tolist(),'exact_top10_distances':best_d.tolist(),'raw_base_min_norm':minnorm,'raw_base_max_norm':maxnorm,'normalized_FP32_max_norm_error':maxunit}
receipt={'status':'PASS','source':rec,'HDF5_fields':fields,'attrs':attrs,'numeric_CPU':numeric,'derived_files':{name:{'sha256':filehash(ROOT/name),'bytes':(ROOT/name).stat().st_size} for name in ['base_fp32_unit.npy','queries_fp32_unit.npy','gt_ids.npy','gt_distances.npy','canary_exact_ids.npy','canary_exact_distances.npy']},'license':{'upstream_vectors':'Stanford GloVe PDDL1.0','upstream_url':'https://nlp.stanford.edu/projects/glove/','HDF5':'author ANN-Benchmarks public benchmark derivative, downloaded only for approved research; not redistributed','dataset_specific_terms_in_HDF5':attrs},'seconds':time.monotonic()-started,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'CUDA_imports':False,'preregistration_sha256':filehash(ROOT/'preregistration.json')}
(ROOT/'data_validation_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('DATA_VALIDATION_PASS',receipt['seconds'],receipt['numeric_CPU']['GT_k10_threshold_max_abs_error'],flush=True)
