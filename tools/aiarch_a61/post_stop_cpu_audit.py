"""Read-only CPU recheck after actual G1 qualification STOP; no Torch import."""
from common import *
import subprocess,resource,re
pre=json.loads((R/'pre_GPU_script_identity.json').read_text());bad=[]
for rel,expected in pre['scripts'].items():
 if sha(W/rel)!=expected:bad.append(rel)
assert not bad,('EXECUTED_SOURCE_CHANGED',bad)
for record in json.loads((R/'graph_cpu_identity.json').read_text())['files'].values():pass
for path,record in json.loads((R/'graph_cpu_identity.json').read_text())['files'].items():assert pathlib.Path(path).stat().st_size==record['bytes'] and sha(pathlib.Path(path))==record['sha256'],path
bindings=json.loads((R/'readonly_runtime_bindings.json').read_text());oldroot=pathlib.Path('/data/c16/aiarch_a26gr1_gsscale_rubble_109_20261014/venv/lib/python3.10/site-packages');n=0
for dist in bindings['distributions']:
 for x in dist['verified_installed_files']:
  p=oldroot/x['path'];assert p.stat().st_size==x['bytes'] and p.stat().st_mtime_ns==x['mtime_ns'] and sha(p)==x['sha256'],str(p);n+=1
cache=[];flags=[]
for root in [R/'cache',R/'tmp']:
 for p in root.rglob('*'):
  if p.is_file():
   cache.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
   if p.suffix in ['.py','.ttir','.ttgir','.ptx']:
    lines=p.read_text(errors='replace').splitlines();hits=[line.strip()[:250] for line in lines if any(k in line.lower() for k in ['allow_tf32','tf32','precision','fma.'])]
    if hits:flags.append({'path':str(p),'hits':hits[:12]})
log=(R/'logs/native_attempt0_compile.log').read_text();assert 'COMPILED_UPDATE_NUMERIC_GATE layers.0.lin_r.weight' in log;assert not (R/'formal_admission.json').exists() and not list(R.glob('wall_*.json'));ledger=json.loads((R/'gpu_ledger.json').read_text());assert ledger['attempts'][-1]['shared_lock_released'] and ledger['attempts'][-1]['all_own_GPU_children_ended']
# Observe existing lock records only; never reacquire the GPU lock after STOP.
ino=pathlib.Path('/data/c16/locks/c16_gpu_campaign.lock').stat().st_ino;active=[s for s in pathlib.Path('/proc/locks').read_text().splitlines() if len(s.split())>5 and s.split()[5].split(':')[-1]==str(ino)];assert not active,'LOCK_REUSED_BY_ANOTHER_TASK_REPORT_INSTEAD_OF_INTERFERE'
old=[]
for name,head in [('accel-sim-aiarch-a59-graphsage-products-109-v1','0e52f088d21e0a88ff471cdf5ad76a7a539cf616'),('accel-sim-aiarch-a59-license-authority-cpu-109-v1','81db397d477222b90dee56d31cd6cf66982d627c'),('accel-sim-aiarch-a50g-recovery-109-v1','995f557c569e7d6ef3fbdbec87481e664993291f')]:
 p=W.parent/name;actual=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip();status=subprocess.check_output(['git','-C',str(p),'status','--porcelain'],text=True);assert actual==head and status=='';old.append({'worktree':str(p),'HEAD':actual,'clean':True})
save('compiled_cache_manifest.json',{'files':cache,'flags':flags,'new_Triton_artifacts_observed':any('.cubin' in x['path'] for x in cache),'scope':'generated compiler artifacts only; no new device execution and no claim of fullgraphfusion or compilerbug'})
save('post_stop_cpu_audit.json',{'status':'PASS_READONLY_IDENTITY_AND_FAILURE_RECEIPT_RECHECK','old_runtime_files_SHA_and_mtime_reverified':n,'raw_input_and_CSC_SHA_reverified':True,'exact_executed_script_SHA_reverified':True,'old_worktrees':old,'no_formal_admission_or_wall_files':True,'native_child_ended_and_lock_released':True,'compiled_failure_observed':'joint predicate n==n2 AND allclose updatedweights failed at layers.0.lin_r.weight','compiled_second_name_actual_delta_and_init_state_hashes':'NOT_CAPTURED; cannot prove compiler defect, precision violation or exclude comparison/input-lifetime issue','cache_artifact_count':len(cache),'CPU_self_peak_RSS_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'CPU_only_no_Torch_or_CUDA_import':True,'no_GPU_resume':True,'new_disk_bytes':check()});print('POST_STOP_CPU_AUDIT_PASS',n,len(cache),'NEW_DISK',check(),flush=True)
