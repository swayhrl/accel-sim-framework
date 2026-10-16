"""CPU-only identity and deterministic author-self-loop CSC conversion, no torch import."""
from common import *
import numpy as np,resource
assert json.loads((R/'data_extraction.json').read_text())['status']=='PASS';root=R/'data/small/processed';feat=root/'paper/node_feat.npy';labels=root/'paper/node_label_19.npy';edge=root/'paper__cites__paper/edge_index.npy';x=np.load(feat,mmap_mode='r');y=np.load(labels,mmap_mode='r');e=np.load(edge,mmap_mode='r');assert x.shape==(1000000,1024) and x.dtype==np.float32;assert y.shape in [(1000000,),(1000000,1)] and e.ndim==2 and e.shape[1]==2
for start in range(0,len(x),16384):assert np.isfinite(x[start:start+16384]).all(),'NONFINITE_AUTHOR_FEATURE'
assert np.isfinite(y).all() and np.equal(y,np.floor(y)).all() and y.min()>=0 and y.max()<=18,'AUTHOR_19_CLASS_LABEL'
assert e.dtype in [np.dtype('int64'),np.dtype('int32')] and e.min()>=0 and e.max()<1000000
mask=e[:,0]!=e[:,1];removed=int(len(e)-np.count_nonzero(mask));src=np.concatenate((e[mask,0].astype(np.int64),np.arange(1000000,dtype=np.int64)));dst=np.concatenate((e[mask,1].astype(np.int64),np.arange(1000000,dtype=np.int64)));order=np.argsort(dst,kind='stable');indices=src[order];counts=np.bincount(dst,minlength=1000000);indptr=np.concatenate((np.zeros(1,dtype=np.int64),np.cumsum(counts,dtype=np.int64)));assert indptr[-1]==len(indices);out=R/'graph';out.mkdir(exist_ok=True);np.save(out/'indptr.npy',indptr);np.save(out/'indices.npy',indices)
# Preserve direction, multiplicity and the author's remove-all/add-one self-loop rule.
for node in [0,1,13,53,109,100000,999999]:assert np.array_equal(indices[indptr[node]:indptr[node+1]],src[dst==node])
keys=np.sort(dst*1000000+src);np.save(out/'edge_keys_sorted.npy',keys);assert np.all(np.diff(keys)>=0)
fields={}
for p in [feat,labels,edge,out/'indptr.npy',out/'indices.npy',out/'edge_keys_sorted.npy']:fields[str(p)]={'bytes':p.stat().st_size,'sha256':sha(p)}
save('graph_cpu_identity.json',{'status':'PASS_AUTHOR_REAL_NUMERIC_AND_DETERMINISTIC_CSC','N':1000000,'raw_edge_array_shape':list(e.shape),'raw_edge_dtype':str(e.dtype),'original_self_loops_removed':removed,'self_loops_added':1000000,'directed_CSC_edges':len(indices),'direction':'author source[:,0] to destination[:,1]; no reverse edges added','parallel_edges':'preserved; no sum/coalesce/dedup','CSC_ID_dtype':'int64','feature_shape':list(x.shape),'feature_dtype':str(x.dtype),'feature_min_sample':float(np.min(x[:1000])),'feature_max_sample':float(np.max(x[:1000])),'labels_min':int(y.min()),'labels_max':int(y.max()),'class_count':19,'synthetic':0,'files':fields,'CPU_peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'new_disk_bytes':check(),'CUDA_imports':False});print('GRAPH_CPU_IDENTITY_PASS',e.shape,removed,len(indices),flush=True)
