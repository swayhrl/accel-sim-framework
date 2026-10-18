"""Bounded native-baseline fixture link, not a new simulator build.
Keeps runtime48GiB/Share40GiB/RAM64GiB guards, reserves256MiB for this
single small link. Formal candidate simulator retains50GiB preflight.
"""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,resource,shlex,subprocess,sys
REPO=Path(__file__).resolve().parents[4]
CORE=Path('/workspace/worktrees/gpgpu-sim-ep-l2-potential20261017-lane1-all-data-r1')
TEST=Path('/workspace/worktrees/gpgpu-sim-ep-l2-microopt20261018-lane1-v1/tests/ep_l2/test_micro_mq2.cc')
BUILD=Path('/workspace/build/ep-l2-potential20261017-lane1-all-data-r1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 global TEST
 if len(sys.argv)>2:TEST=Path(sys.argv[2])
 out=Path(sys.argv[1]);out.mkdir(exist_ok=False,parents=True);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 r={'authority':'c8aa87bdbe220853eb2d27d8babd448cff02a66e','kind':'BASELINE_NATIVE_FIXTURE_LINK_ONLY_NOT_FORMAL_SIMULATOR_BUILD','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PREFLIGHT','commands':[],'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'source':str(TEST),'source_sha256':sha(TEST),'baseline_core':'9bd30ed913c5058b5d952fbeb2e67cb5e4644b3f','application_starts':0,'compiler_started':False,'output_bound_bytes':256*2**20}
 def save():(out/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
 cl=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());r['client_expected']=cl['registry_client_sha256'];r['client_actual']=sha(cl['registry_client'])
 if r['client_expected']!=r['client_actual']:r['status']='CLIENT_BINDING_HOLD';save();return
 sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
 s=importlib.util.spec_from_file_location('guard',REPO/'util/ep_l2/ft_lane1/build_r0_1.py');g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
 def resources():
  live=local_resources();v=os.statvfs('/root/share');assert v.f_bavail*v.f_frsize>=40*2**30
  assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file())<r['output_bound_bytes']
  return live
 lease=None
 try:
  live=resources();r['resources_before']=live
  if live['disk_free_bytes']<48*2**30+r['output_bound_bytes']:r['status']='SMALL_FIXTURE_RESOURCE_HOLD';return
  assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CORE,text=True).strip()==r['baseline_core']
  libs=[BUILD/'gpgpu-sim'/f for f in ['libentrypoint.a','libcuda/libcuda.a','src/cuda-sim/libptxsim.a','src/gpgpu-sim/libgpgpusim.a','src/intersim2/libintersim.a','src/accelwattch/libaccelwattch.a']]
  r['native_archives_sha256']={str(p):sha(p) for p in libs}
  flags={}
  for line in (BUILD/'gpgpu-sim/CMakeFiles/ep_l2_potential_p2.dir/flags.make').read_text().splitlines():
   if line.startswith('CXX_'):k,v=line.split(' = ',1);flags[k]=v
  lease=Registry(cl['canonical_root']).build_lease('lane1',cpu=1,memory=2*2**30);r['lease_id']=lease;save()
  def run(cmd,name):g.run_owned(cmd,name,out,dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'),r,save,resources,process_identity,180)
  # Force fixture includes to frozen baseline Core; no candidate ABI before runtime build.
  src=(TEST.parent/'micro_fixture.h').read_text().replace('"../../','"'+str(CORE)+'/')
  (out/'micro_fixture.h').write_text(src);
  extra=TEST.parent/'micro_partition_fixture.h'
  if extra.exists():(out/extra.name).write_text(extra.read_text().replace('"../../','"'+str(CORE)+'/'))
  (out/'test_micro_mq2.cc').write_text(TEST.read_text())
  r['compiler_started']=True;run(['/usr/bin/c++',*shlex.split(flags['CXX_DEFINES']),*shlex.split(flags['CXX_INCLUDES']),'-O0','-g0','-std=gnu++17',str(out/'test_micro_mq2.cc'),'-Wl,--strip-debug','-o',str(out/'reproduce'),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'link')
  r['fixture_binary_sha256']=sha(out/'reproduce')
  base=CORE/'configs/tested-cfgs/SM7_QV100/gpgpusim.config';ov=CORE/'tests/ep_l2/ft_wbuf.config'
  for mode,s64 in [(1,0),(1,1),(2,0)]:
   overlay=out/f'mode{mode}_s64{s64}.config';overlay.write_text(ov.read_text()+f'\n-gpgpu_ep_l2_static_s64 {s64}\n-gpgpu_dram_partition_queues 32:32:32:1\n')
   run([str(out/'reproduce'),str(base),str(overlay),str(mode),*(['16',str(s64),'0','1'] if 'partition' in TEST.name else ['0'])],f'baseline_{mode}_{s64}')
  r['status']='BASELINE_OPPORTUNITY_REPRODUCED_THREE_FINITE_MODES'
 except BaseException as e:r['status']='FAILED_RETAIN_DIAGNOSTICS';r['error']=repr(e);raise
 finally:
  if lease:Registry(cl['canonical_root']).release_build(lease,'lane1');r['lease_released']=True
  r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(r['status'])
if __name__=='__main__':main()
