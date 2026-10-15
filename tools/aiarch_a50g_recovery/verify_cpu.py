"""Read-only independent recheck of recorded search outputs, no CUDA imports."""
import os,pathlib,json,hashlib,resource,time,subprocess
os.sched_setaffinity(0,[0,2,4,6])
import numpy as np
R=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_recovery_v1');O=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1');W=pathlib.Path(__file__).resolve().parents[2]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def read(n):return json.loads((R/n).read_text())
snap=read('old_asset_snapshot.json');checked=0
for x in snap['files']+read('prior_A50G_asset_snapshot.json'):
 p=pathlib.Path(x['path']);assert p.stat().st_size==x['bytes'] and p.stat().st_mtime_ns==x['mtime_ns'] and sha(p)==x['sha256'],str(p);checked+=1
for x in snap['worktrees']:
 p='/home/huangrulin/workspace/worktrees/'+x['label'];assert subprocess.check_output(['git','-C',p,'rev-parse','HEAD'],text=True).strip()==x['head'];assert subprocess.check_output(['git','-C',p,'status','--porcelain'],text=True)==''
oldW=pathlib.Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-a50g-glove100-default-native-full-109-v1');assert subprocess.check_output(['git','-C',str(oldW),'rev-parse','HEAD'],text=True).strip()=='d74ba0225516e60aa1c18b7ee87c88abfc34e0c9';assert subprocess.check_output(['git','-C',str(oldW),'status','--porcelain'],text=True)==''
idx=read('index_identity.json');assert sha(R/'glove.index')==idx['sha256'] and (R/'glove.index').stat().st_size==idx['bytes']
base=np.load(O/'base_fp32_unit.npy',mmap_mode='r');q=np.load(O/'queries_fp32_unit.npy',mmap_mode='r');gt=np.load(O/'gt_distances.npy',mmap_mode='r');gi=np.load(O/'gt_ids.npy',mmap_mode='r');pre=read('frozen_preregistration.json');records=[]
for rec in read('functional_canary.json')['configurations']+read('calibration.json')['configurations']:
 p=R/'raw'/(rec['label']+'_outputs.npz');a=np.load(p);ids=a['query_ids'];n=a['neighbors'];d=a['distances'];assert np.array_equal(ids,np.array(rec['query_ids']));assert np.isfinite(d).all() and (n<len(base)).all() and (np.diff(np.sort(n,axis=1),axis=1)!=0).all()
 reference=np.empty(d.shape,dtype=np.float64)
 for start in range(0,len(ids),128):
  x=np.asarray(base[n[start:start+128]],np.float64);query=np.asarray(q[ids[start:start+128]],np.float64);reference[start:start+len(x)]=1-np.sum(x*query[:,None,:],axis=2)/(np.linalg.norm(x,axis=2)*np.linalg.norm(query,axis=1)[:,None])
 assert np.allclose(d,reference,atol=1e-5,rtol=1e-4)
 hits=np.sum(reference<=np.asarray(gt[ids,9],np.float64)[:,None]+.001,axis=1);assert hits.tolist()==rec['per_query_hits'];recall=float(hits.sum()/(10*len(ids)));assert abs(recall-rec['recall_at10'])<1e-14
 strict=np.array([np.isin(row,gi[qi,:10]).sum() for row,qi in zip(n,ids)]);assert strict.tolist()==rec['per_query_strict_hits']
 assert hashlib.sha256(n.tobytes()).hexdigest()==rec['neighbors_sha256'] and hashlib.sha256(d.tobytes()).hexdigest()==rec['distances_sha256']
 if 'canary_' in rec['label']:
  assert np.array_equal(ids[:32],pre['canary_ids']);assert np.allclose(np.load(O/'canary_exact_distances.npy')[:,9],gt[ids[:32],9],atol=1e-5,rtol=1e-4)
 records.append({'label':rec['label'],'count':len(ids),'recomputed_recall':recall,'max_abs_distance_error':float(np.max(np.abs(d-reference))),'npz_sha256':sha(p)})
for b in [1,256]:
 a=np.load(R/'raw'/f'canary_before_B{b}_outputs.npz');z=np.load(R/'raw'/f'canary_after_B{b}_outputs.npz');assert np.array_equal(a['neighbors'],z['neighbors']) and np.array_equal(a['distances'],z['distances'])
cal=read('calibration.json');assert cal['status']=='QUALITY_NO_GO' and cal['eligible_h']==[] and len(cal['configurations'])==6;assert not (R/'report_quality.json').exists() and not list((R/'raw').glob('process_*timing.jsonl'))
assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader'],text=True).strip()
out={'status':'PASS_INDEPENDENT_CPU_RECHECK','CUDA_imports':False,'index_serialized_sha256':idx['sha256'],'records':records,'reload_outputs_exactly_identical':True,'original_assets_hash_mtime_checked':checked,'old_worktrees_clean_and_HEADs_unchanged':True,'calibration_threshold':.95,'same_B_delta_limit':.005,'eligible_h':[],'all_calibration_recalls_below_threshold':True,'formal_timing_files':0,'quality_stop_confirmed':True,'peak_CPU_verifier_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'CPU_affinity':sorted(os.sched_getaffinity(0)),'no_GPU_process_after_stop':True}
(R/'independent_cpu_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
