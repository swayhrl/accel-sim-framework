import os,pathlib,json,hashlib,time,ast,subprocess,importlib.metadata,shutil
os.sched_setaffinity(0,[0,2,4,6]);W=pathlib.Path(__file__).resolve().parents[2];R=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_recovery_v1');P=pathlib.Path('/data/c16/aiarch_a50g_glove100_default_full_109_v1');O=pathlib.Path('/data/c16/aiarch_a47_cagra_glove100_109_v1')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(8*1024**2),b''):h.update(b)
 return h.hexdigest()
def snapshot(root):return [{'path':str(p),'bytes':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns,'sha256':sha(p)} for p in root.rglob('*') if p.is_file()]
old=json.loads((R/'old_asset_snapshot.json').read_text());bad=[]
for x in old['files']:
 p=pathlib.Path(x['path'])
 if not p.exists() or p.stat().st_size!=x['bytes'] or p.stat().st_mtime_ns!=x['mtime_ns'] or sha(p)!=x['sha256']:bad.append(str(p))
assert not bad,bad
(R/'prior_A50G_asset_snapshot.json').write_text(json.dumps(snapshot(P),indent=2))
expected={'cuvs-cu12':'26.10.0','libcuvs-cu12':'26.10.0','pylibraft-cu12':'26.10.0','rmm-cu12':'26.10.0','librmm-cu12':'26.10.0','cupy-cuda12x':'14.0.1','numpy':'2.5.4'}
versions={k:importlib.metadata.version(k) for k in expected};assert versions==expected
import numpy as np
base=np.load(O/'base_fp32_unit.npy',mmap_mode='r');assert base.shape==(1183514,100) and base.dtype==np.float32
pre=json.loads((R/'frozen_preregistration.json').read_text());assert pre['split_sha256']=='0fb3e14cd9b4b9c97397235c5dddcd73b1a53bb5979b04ac5e3762f8c559c650' and pre['timing_ids_sha256']=='f7ebf0825b6ba7e351df18c20f8e0cb559b37fdbf0775142d989161df7baafea'
assert len(pre['calibration_ids'])==2000 and len(pre['report_ids'])==8000 and not set(pre['calibration_ids'])&set(pre['report_ids']) and len(set(pre['timing_ids']))==2048
codes={}
for p in (W/'tools/aiarch_a50g_recovery').glob('*.py'):
 s=p.read_text();compile(s,str(p),'exec');tree=ast.parse(s)
 for n in ast.walk(tree):
  if isinstance(n,ast.Call):
   name=ast.unparse(n.func)
   assert not any(z in name for z in ['PoolMemoryResource','set_current_device_resource','set_allocator','cuda.Stream']),name
 codes[str(p.relative_to(W))]=sha(p)
s=(W/'tools/aiarch_a50g_recovery/native.py').read_text();assert s.count('cagra.build(')==1 and "count=b*100" in s and s.index('PINNED_ALLOCATION_TRANSFER_PREFLIGHT_PASS')<s.index('FULL_BUILD_ENTER') and s.index('cagra.save(')<s.index('# Two fixed functional')
assert shutil.disk_usage(R).free>=64*1024**3
record={'status':'PASS','old_frozen_files_checked':len(old['files']),'old_identity_mtime_hash_failures':bad,'prior_A50G_snapshot':str(R/'prior_A50G_asset_snapshot.json'),'versions':versions,'code_sha256':codes,'default_policy_AST':True,'one_additional_build_callsite':1,'remaining_original_GPU_seconds':2700-3.9592992877587676,'prior_A50G_download_install_bytes':0,'new_download_install_bytes':0,'prior_A50G_CPU_prep_seconds':278.1733889579773,'recovery_CPU_prep_seconds':time.time()-json.loads((R/'start.json').read_text())['epoch'],'prior_asset_read_only':True,'latest_authorization':'User: 那你改正。然后接着做; interpreted and announced as one additional build within original cumulative caps; no change to science/configuration/quality','publish_branch':'hrl/aiarch-a50g-glove100-default-native-full-109-v1','recovery_worktree_branch_is_local_only':True}
(R/'preflight.json').write_text(json.dumps(record,indent=2));print(json.dumps(record))
