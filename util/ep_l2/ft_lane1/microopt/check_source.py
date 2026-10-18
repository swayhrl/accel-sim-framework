"""Read-only native source syntax checks under a bounded fixture lease; no linking/runtime release."""
from pathlib import Path
import importlib.util,json,os,shlex,sys,resource,hashlib
R=Path(__file__).resolve().parents[4];C=Path('/workspace/worktrees/gpgpu-sim-ep-l2-microopt20261018-lane1-v1');B=Path('/workspace/build/ep-l2-potential20261017-lane1-all-data-r1')
def main():
 o=Path(sys.argv[1]);o.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0));r={'status':'PREFLIGHT','commands':[],'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'scope':'SYNTAX_ONLY_NO_RUNTIME_NO_BINARY','application_starts':0}
 def save():(o/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
 cl=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());assert hashlib.sha256(Path(cl['registry_client']).read_bytes()).hexdigest()==cl['registry_client_sha256']
 sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
 s=importlib.util.spec_from_file_location('guard',R/'util/ep_l2/ft_lane1/build_r0_1.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
 def resources():
  v=local_resources();q=os.statvfs('/root/share');assert q.f_bavail*q.f_frsize>=40*2**30;return v
 flags={}
 for l in (B/'gpgpu-sim/src/gpgpu-sim/CMakeFiles/gpgpusim.dir/flags.make').read_text().splitlines():
  if l.startswith('CXX_'):k,v=l.split(' = ',1);flags[k]=v
 opts=shlex.split(flags['CXX_DEFINES']+' '+flags['CXX_INCLUDES']);opts=[p.replace('gpgpu-sim-ep-l2-potential20261017-lane1-all-data-r1','gpgpu-sim-ep-l2-microopt20261018-lane1-v1') if p.startswith('-I/workspace/worktrees') else p for p in opts]
 lease=None
 try:
  v=resources();assert v['disk_free_bytes']>=48*2**30+64*2**20
  lease=Registry(cl['canonical_root']).build_lease('lane1',cpu=1,memory=2*2**30);r['lease_id']=lease
  for i,f in enumerate(['src/gpgpu-sim/gpu-cache.cc','src/gpgpu-sim/gpu-sim.cc','tests/ep_l2/test_micro_mq2.cc']):
   g.run_owned(['/usr/bin/c++',*opts,'-DEPL2_MICROOPT_CANDIDATE=1','-std=gnu++17','-fsyntax-only',str(C/f)],f'check_{i}',o,dict(os.environ),r,save,resources,process_identity,180)
  r['status']='PASS_SOURCE_SYNTAX_ONLY'
 except BaseException as e:r['status']='FAIL_RETAIN_LOGS';r['error']=repr(e);raise
 finally:
  if lease:Registry(cl['canonical_root']).release_build(lease,'lane1');r['lease_released']=True
  save()
 print(r['status'])
if __name__=='__main__':main()
