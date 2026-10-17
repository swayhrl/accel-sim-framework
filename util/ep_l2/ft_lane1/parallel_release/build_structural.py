"""Build one isolated structural+local-Ideal candidate under canonical budget.
No old build reuse/mutation; original R0.1 production entry is unchanged.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,resource,subprocess,sys
REPO=Path(__file__).resolve().parents[4]
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-potential20261017-lane1-s64-r1')
FW=Path('/workspace/worktrees/accel-sim-ep-l2-potential20261017-lane1-local-r1')
BUILD=Path('/workspace/build/ep-l2-potential20261017-lane1-structure-r1')
OUT=Path('/workspace/ep_l2_parallel_lane1/structural_build_r2')
EXPECTED='8960ace40bece2acf81e62f95f77fa2d637b258d'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def head(p):return subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()
def main():
 OUT.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0));r={'schema':'EPL2_LANE1_STRUCTURAL_BUILD_V1','status':'PREFLIGHT','authority':'a9ab796f0c905d99eb1ffa3d02ea9305ce0bc900','core_source_commit':head(CORE),'framework_source_commit':head(FW),'driver_source_commit':head(REPO),'build':str(BUILD),'core':str(CORE),'framework':str(FW),'out':str(OUT),'compiler_started':False,'jobs':2,'application_starts':0,'independent_qualification':False,'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'commands':[],'resource_samples':0,'own_process_group_max_rss_bytes':0,'own_process_group_rss_scope':'sampled sum of VmRSS in the owned CMake process group; shared pages may be counted more than once','peak_workspace_growth_bytes':0}
 def save():q=OUT/'BUILD_RECEIPT.tmp';q.write_text(json.dumps(r,indent=2)+'\n');q.replace(OUT/'BUILD_RECEIPT.json')
 clp=Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json');cl=json.loads(clp.read_text());r['registry_source_commit']=cl['registry_source_commit'];r['registry_sha256']=sha(cl['registry_client'])
 if r['registry_sha256']!=cl['registry_client_sha256']:r['status']='CLIENT_BINDING_HOLD_PRELEASE_NO_COMPILER';save();return
 sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
 spec=importlib.util.spec_from_file_location('frozen_build_guard',REPO/'util/ep_l2/ft_lane1/build_r0_1.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
 def resources():
  live=local_resources();share=os.statvfs('/root/share');assert share.f_bavail*share.f_frsize>=40*2**30,'Share safety floor crossed'
  r['resource_samples']+=1;r['min_available_memory_bytes']=min(r.get('min_available_memory_bytes',live['available_memory_bytes']),live['available_memory_bytes']);r['min_workspace_free_bytes']=min(r.get('min_workspace_free_bytes',live['disk_free_bytes']),live['disk_free_bytes']);r['min_share_free_bytes']=min(r.get('min_share_free_bytes',share.f_bavail*share.f_frsize),share.f_bavail*share.f_frsize)
  if 'initial_workspace_free_bytes' in r:r['peak_workspace_growth_bytes']=max(r['peak_workspace_growth_bytes'],r['initial_workspace_free_bytes']-live['disk_free_bytes'])
  if r['commands'] and r['commands'][-1].get('process'):
   pgid=r['commands'][-1]['process']['pid'];rss=0
   for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:
     stat=(p/'stat').read_text().rsplit(')',1)[1].split()
     if int(stat[2])!=pgid:continue
     for line in (p/'status').read_text().splitlines():
      if line.startswith('VmRSS:'):rss+=int(line.split()[1])*1024
    except (FileNotFoundError,ProcessLookupError,PermissionError):pass
   r['own_process_group_max_rss_bytes']=max(r['own_process_group_max_rss_bytes'],rss)
  return live
 lease=None
 try:
  assert r['core_source_commit']==EXPECTED and r['framework_source_commit']=='8ab6013ea90755fdc74819e92090c2de50f4f199'
  for p in [CORE,FW,FW/'gpu-simulator/extern/pybind11']:assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=p)
  assert head(FW/'gpu-simulator/extern/pybind11')=='f90c430c3a1ce8f08c09942a5a1c3a797bb2295b'
  assert not BUILD.exists();before=resources();assert before['disk_free_bytes']>=50*2**30 and before['available_memory_bytes']-8*2**30>=64*2**30
  r['resources_before']=before;r['initial_workspace_free_bytes']=before['disk_free_bytes'];r['filesystems']={str(p):{'realpath':str(p.resolve()),'st_dev':p.stat().st_dev} for p in [Path('/workspace'),OUT,Path('/root/share')]}
  lease=Registry(cl['canonical_root']).build_lease('lane1',cpu=2,memory=8*2**30);r['lease_id']=lease;save()
  env=dict(os.environ,GPGPUSIM_ROOT=str(CORE),CUDA_INSTALL_PATH='/usr/local/cuda-11.8',ACCELSIM_CONFIG='release',PATH='/usr/local/cuda-11.8/bin:'+os.environ['PATH'],OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
  def run(cmd,name):return guard.run_owned(cmd,name,OUT,env,r,save,resources,process_identity,1200)
  r['status']='CONFIGURING';r['compiler_started']=True;save();run(['cmake','-S',str(FW/'gpu-simulator'),'-B',str(BUILD),'-G','Unix Makefiles','-DCUDAToolkit_ROOT=/usr/local/cuda-11.8'],'configure')
  targets=['accel-sim.out','ep_l2_ft_memcpy_clock','ep_l2_ft_host_prefill','ep_l2_ft_directed','ep_l2_ft_partition','ep_l2_ft_a1','ep_l2_common_delta_r16','ep_l2_ideal_wb','ep_l2_ideal_meta','ep_l2_ideal_meta_integrated','ep_l2_ideal_read_hit','ep_l2_ideal_host_prefill_reference','ep_l2_ideal_host_prefill_partition','ep_l2_potential_s64','ep_l2_potential_a1','ep_l2_potential_ucap','ep_l2_potential_ucap_retry']
  r['targets']=targets;r['status']='BUILDING';save();run(['cmake','--build',str(BUILD),'--target',*targets,'-j2'],'build')
  assert head(CORE)==EXPECTED and head(FW)==r['framework_source_commit']
  for p in [CORE,FW]:assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=p)
  flags=list(BUILD.rglob('flags.make'));assert flags and all('-DNDEBUG' not in p.read_text() for p in flags);r['assertion_flags_sha256']={str(p):sha(p) for p in flags};r['binary_sha256']=sha(BUILD/'accel-sim.out');r['binary']=str(BUILD/'accel-sim.out');r['status']='BUILT_NOT_TESTED_NOT_INDEPENDENTLY_QUALIFIED'
 except BaseException as e:r['status']='FAILED_RETAIN_DIAGNOSTICS_NO_RELEASE';r['error']=repr(e);raise
 finally:
  if lease:Registry(cl['canonical_root']).release_build(lease,'lane1');r['lease_released']=True
  r['resources_after']=resources();r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(json.dumps({'status':r['status'],'binary':r.get('binary_sha256'),'lease_released':r.get('lease_released')}))
if __name__=='__main__':main()
