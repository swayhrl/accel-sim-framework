"""Read-only native source syntax checks under a bounded fixture lease; no linking/runtime release."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import importlib.util,json,os,shlex,sys,resource,hashlib,subprocess,datetime
R=Path(__file__).resolve().parents[4];C=Path('/workspace/worktrees/gpgpu-sim-ep-l2-microopt20261018-lane1-v1');B=Path('/workspace/build/ep-l2-potential20261017-lane1-all-data-r1')
def main():
 o=Path(sys.argv[1]);o.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0));r={'status':'PREFLIGHT','commands':[],'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'scope':'SOURCE_SYNTAX_AND_STANDALONE_ARBITER_NOT_SIMULATOR_RELEASE','application_starts':0}
 r['framework_trace_sha256']=hashlib.sha256((R/'gpu-simulator/trace-driven/trace_driven.cc').read_bytes()).hexdigest();r['started_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['core_head']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=C,text=True).strip();r['source_sha256']={str(p.relative_to(C)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [C/'src/abstract_hardware_model.h',C/'src/gpgpu-sim/gpu-cache.h',C/'src/gpgpu-sim/ep-l2-rg1.inc',C/'src/gpgpu-sim/ep-l2-ft-cache.inc',C/'src/gpgpu-sim/gpu-cache.cc',C/'src/gpgpu-sim/gpu-sim.cc',C/'src/gpgpu-sim/l2cache.cc',C/'src/gpgpu-sim/l2cache.h',*sorted((C/'tests/ep_l2').glob('*micro*'))]};r['uncommitted_tracked_changes']=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=C,text=True)
 def save():(o/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
 cl=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text())
 if hashlib.sha256(Path(cl['registry_client']).read_bytes()).hexdigest()!=cl['registry_client_sha256']:
  r['status']='CLIENT_BINDING_HOLD_PRELEASE';save();return
 sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
 s=importlib.util.spec_from_file_location('guard',R/'util/ep_l2/ft_lane1/build_r0_1.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
 def resources():
  v=local_resources();q=os.statvfs('/root/share');assert q.f_bavail*q.f_frsize>=40*2**30
  for k in ['available_memory_bytes','disk_free_bytes','share_disk_free_bytes']:
   if k in v:r['min_'+k]=min(r.get('min_'+k,v[k]),v[k])
  return v
 flags={}
 for l in (B/'gpgpu-sim/src/gpgpu-sim/CMakeFiles/gpgpusim.dir/flags.make').read_text().splitlines():
  if l.startswith('CXX_'):k,v=l.split(' = ',1);flags[k]=v
 opts=shlex.split(flags['CXX_DEFINES']+' '+flags['CXX_INCLUDES']);opts=[p.replace('gpgpu-sim-ep-l2-potential20261017-lane1-all-data-r1','gpgpu-sim-ep-l2-microopt20261018-lane1-v1') if p.startswith('-I/workspace/worktrees') else p for p in opts]
 lease=None
 try:
  v=resources();assert v['disk_free_bytes']>=48*2**30+64*2**20
  lease=Registry(cl['canonical_root']).build_lease('lane1',cpu=1,memory=2*2**30);r['lease_id']=lease
  for i,f in enumerate(['src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-sim.cc','src/gpgpu-sim/l2cache.cc','tests/ep_l2/test_micro_mq2.cc','tests/ep_l2/test_micro_rg1_partition.cc','tests/ep_l2/test_micro_rg1_arbiter.cc']):
   g.run_owned(['/usr/bin/c++',*opts,'-DEPL2_MICROOPT_CANDIDATE=1','-std=gnu++17','-fsyntax-only',str(C/f)],f'check_{i}',o,dict(os.environ),r,save,resources,process_identity,180)
  tf={}
  for l in (B/'trace-driven/CMakeFiles/trace-driven.dir/flags.make').read_text().splitlines():
   if l.startswith('CXX_'):k,v=l.split(' = ',1);tf[k]=v
  topts=shlex.split(tf['CXX_DEFINES']+' '+tf['CXX_INCLUDES'])
  topts=[p.replace('gpgpu-sim-ep-l2-potential20261017-lane1-all-data-r1','gpgpu-sim-ep-l2-microopt20261018-lane1-v1').replace('accel-sim-ep-l2-potential20261017-lane1-local-r1','accel-sim-ep-l2-microopt20261018-lane1-v1') for p in topts]
  g.run_owned(['/usr/bin/c++',*topts,'-std=gnu++17','-fsyntax-only',str(R/'gpu-simulator/trace-driven/trace_driven.cc')],'check_trace_decode',o,dict(os.environ),r,save,resources,process_identity,180)
  g.run_owned(['/usr/bin/c++',*opts,'-std=gnu++17','-O0','-g0',str(C/'tests/ep_l2/test_micro_rg1_arbiter.cc'),'-o',str(o/'arbiter')],'link_arbiter',o,dict(os.environ),r,save,resources,process_identity,180)
  g.run_owned([str(o/'arbiter')],'run_arbiter',o,dict(os.environ),r,save,resources,process_identity,180)
  r['status']='PASS_SOURCE_SYNTAX_AND_STANDALONE_ARBITER'
 except BaseException as e:r['status']='FAIL_RETAIN_LOGS';r['error']=repr(e);raise
 finally:
  if lease:Registry(cl['canonical_root']).release_build(lease,'lane1');r['lease_released']=True
  r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(r['status'])
if __name__=='__main__':main()
