"""Consume later author test-only additions on the immutable combined binary."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,resource,shlex,subprocess,sys
repo=Path(__file__).resolve().parents[4];out=Path('/workspace/ep_l2_parallel_lane1/all_data_supplement_r1');out.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
base_receipt=Path('/workspace/ep_l2_parallel_lane1/all_data_release_r1/INTAKE_RECEIPT.json');base=json.loads(base_receipt.read_text());assert base['status']=='ALL_DATA_P2_STRUCTURAL_LOCAL_IDEALS_PRODUCER_PASS_LANE5_INDEPENDENT_QUALIFICATION_REQUIRED'
core=Path('/workspace/worktrees/gpgpu-sim-ep-l2-potential20261017-lane1-all-data-r1');build=Path('/workspace/build/ep-l2-potential20261017-lane1-all-data-r1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'schema':'EPL2_ALL_DATA_SUPPLEMENT_V1','status':'PREFLIGHT','runtime_core':base['core_source_commit'],'runtime_framework':base['framework_source_commit'],'binary_sha256':base['binary_sha256'],'base_receipt_sha256':sha(base_receipt),'author_test_source':'30a5026e3b6d321ed857c78ef12bb8b8f32216af','fixture_source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip(),'tests':[],'expected_rejections':[],'commands':[],'runtime_recompiled':False,'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30}
def save():(out/'SUPPLEMENT_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
cl=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());assert sha(cl['registry_client'])==cl['registry_client_sha256'];sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
sp=importlib.util.spec_from_file_location('guard',repo/'util/ep_l2/ft_lane1/build_r0_1.py');guard=importlib.util.module_from_spec(sp);sp.loader.exec_module(guard)
def resources():
 x=local_resources();s=os.statvfs('/root/share');assert s.f_bavail*s.f_frsize>=40*2**30;return x
def run(cmd,name):return guard.run_owned(['/usr/bin/time','-v',*cmd],name,out,dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'),r,save,resources,process_identity,180)
lease=None
try:
 assert sha(build/'accel-sim.out')==r['binary_sha256']
 for p,h in base['archives_sha256'].items():assert sha(p)==h
 r['resources_before']=resources();lease=Registry(cl['canonical_root']).build_lease('lane1',cpu=1,memory=4*2**30);r['lease_id']=lease;save();flags={}
 for line in (build/'gpgpu-sim/CMakeFiles/ep_l2_ft_a1.dir/flags.make').read_text().splitlines():
  if line.startswith('CXX_'):k,v=line.split(' = ',1);flags[k]=v
 libs=list(base['archives_sha256']);r['sources']={}
 for name in ['reference','clock']:
  src=Path(__file__).with_name('test_all_data_'+('reference_latest.cc' if name=='reference' else 'clock_latest.cc'));r['sources'][str(src)]=sha(src)
  run(['/usr/bin/c++',*shlex.split(flags['CXX_DEFINES']),*shlex.split(flags['CXX_INCLUDES']),'-I'+str(core/'tests/ep_l2'),'-O0','-g0','-fPIC','-std=gnu++17',str(src),'-o',str(out/name),'-Wl,--start-group',*libs,'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],name+'_compile')
 cfgbase=str(core/'configs/tested-cfgs/SM7_QV100/gpgpusim.config');overlay=str(core/'tests/ep_l2/all_data_reference.config')
 for name,cmd in [('cross_warp_reference',[str(out/'reference')]),('latest_native_offset4096',[str(out/'clock'),cfgbase,overlay,'--offset4096'])]:r['tests'].append(run(cmd,name))
 for name,cmd,marker in [('duplicate_native_access',[str(out/'reference'),'--duplicate-access'],'EPL2MEMREF_DUPLICATE_NATIVE_ACCESS'),('unsupported_atomic',[str(out/'clock'),cfgbase,overlay,'--atomic'],'EPL2MEMREF_UNSUPPORTED|atomic=1')]:
  try:run(cmd,name)
  except RuntimeError:
   rec=r['commands'][-1];assert rec['exit_code']==134 and marker in Path(rec['log']).read_text();rec['expected_rejection']=True;r['expected_rejections'].append(rec)
  else:raise AssertionError('unsupported case accepted')
 assert sha(build/'accel-sim.out')==r['binary_sha256'];r['status']='SUPPLEMENT_PASS_2_POSITIVE_2_EXPECTED_REJECTIONS_SAME_IMMUTABLE_RUNTIME'
except BaseException as e:r['status']='FAILED_RETAIN_EVIDENCE';r['error']=repr(e);raise
finally:
 if lease:Registry(cl['canonical_root']).release_build(lease,'lane1');r['lease_released']=True
 r['resources_after']=resources();r['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({'status':r['status'],'positive':len(r['tests']),'expected_rejections':len(r['expected_rejections'])}))
