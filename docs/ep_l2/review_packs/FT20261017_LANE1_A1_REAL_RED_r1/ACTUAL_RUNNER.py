from pathlib import Path
import importlib.util,json,sys,os,resource,hashlib,shlex,time,datetime,fcntl,subprocess
parent=Path(__file__).resolve().parent.parent
out=parent/'a1_red_r4';out.mkdir(exist_ok=False)
source=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-red-r2')
old_source=Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261017-lane1-a1-red')
old_build=Path('/workspace/build/ep-l2-ft20261017-lane1-a1-red/gpgpu-sim')
build=Path('/workspace/build/ep-l2-ft20261017-lane1-a1-red-r2');assert not build.exists()
client=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());p=Path(client['registry_client']);assert hashlib.sha256(p.read_bytes()).hexdigest()==client['registry_client_sha256'];sys.path.insert(0,str(p.parent))
from registry import Registry,local_resources,process_identity,ACTIVE
spec=importlib.util.spec_from_file_location('build_red','/workspace/worktrees/accel-sim-ep-l2-ft20261017-lane1-a1-red/util/ep_l2/ft_lane1/build_r0_1.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
resource.setrlimit(resource.RLIMIT_CORE,(0,0));reg=Registry(client['canonical_root'])
r={'status':'PREFLIGHT','source_core':subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip(),'runtime_source':'088146f7f85b4073deb5d166a0a4484c7f3b48b2','disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'results':[],'archive_reuse':'Immutable complete native red build; test-only/header observers do not change class layout or runtime bodies','independent_scientific_qualification':False}
def save():(out/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
def confirm():
 d=local_resources();assert d['disk_free_bytes']>=50*2**30 and d['available_memory_bytes']-2**30>=64*2**30
 f=os.statvfs('/root/share');assert f.f_bavail*f.f_frsize>=40*2**30
 with reg.locked() as state:
  active={k:v for k,v in state['resource_leases'].items() if v['status'] in ACTIVE}
  r['other_active_build_leases']=active
  assert not any(v['owner']=='lane1' for v in active.values())
 return dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),resources=d)
r['first_confirmation']=json.loads((parent/'a1_red_r3/RECEIPT.json').read_text())['first_confirmation'];assert (datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(r['first_confirmation']['at_utc'])).total_seconds()>=61;r['second_confirmation']=confirm();r['scope']='R16_LIGHT_DIRECTED_FIXTURE_RELINK_1_CPU_REAL_REGISTRY_QUOTA_NOT_FORMAL_FULL_PRODUCER';save()
lease=reg.build_lease('lane1',cpu=1,memory=2**30);r['lease_id']=lease;build.mkdir()
try:
 flags={}
 for line in (old_build/'CMakeFiles/ep_l2_ft_a1.dir/flags.make').read_text().splitlines():
  if line.startswith('CXX_'):k,v=line.split(' = ',1);flags[k]=v
 obj=build/'fixture.o';binary=build/'ep_l2_ft_a1'
 cmd=['/usr/bin/c++']
 for key in ['CXX_DEFINES','CXX_INCLUDES','CXX_FLAGS']:cmd+=shlex.split(flags[key].replace(str(old_source),str(source)))
 cmd+=['-c',str(source/'tests/ep_l2/test_ft_a1.cc'),'-o',str(obj)]
 driver.run_owned(cmd,'build',out,os.environ.copy(),r,save,local_resources,process_identity,180)
 link=shlex.split((old_build/'CMakeFiles/ep_l2_ft_a1.dir/link.txt').read_text());j=link.index('-o');link[j+1]=str(binary)
 for i,v in enumerate(link):
  if v.endswith('.o'):link[i]=str(obj)
  elif v.endswith('.a') and not v.startswith('/'):link[i]=str(old_build/v)
 r['archive_sha256']={v:driver.digest(v) for v in link if v.endswith('.a')};r['fixture_sha256']=driver.digest(source/'tests/ep_l2/test_ft_a1.cc')
 driver.run_owned(link,'link',out,os.environ.copy(),r,save,local_resources,process_identity,180)
 r['binary_sha256']=driver.digest(binary)
 for mode,c in [(1,8),(1,16),(2,8),(2,16)]:
  cmd=[str(binary),str(source/'configs/tested-cfgs/SM7_QV100/gpgpusim.config'),str(source/'tests/ep_l2/ft_wbuf.config'),str(mode),str(c)]
  try:driver.run_owned(cmd,f'a1_red_{mode}_{c}',out,os.environ.copy(),r,save,local_resources,process_identity,30)
  except RuntimeError:pass
  record=r['commands'][-1];log=Path(record['log']).read_text();assert record['exit_code']==-6 and 'A1 armed' in log and 'p.tag_index == index && probe == MISS' in log,(mode,c,record,log[-1800:])
  r['results'].append({'mode':mode,'wbuf':c,'status':'REPRODUCED_OLD_NATIVE_ASSERT_SIGABRT','log_sha256':record['log_sha256']})
 r['status']='FOUR_REAL_A1_REPRODUCTIONS_CONFIRMED'
finally:
 reg.release_build(lease,'lane1');r['lease_released']=True;save()
print(json.dumps({k:r[k] for k in ['status','source_core','binary_sha256','results']}))
