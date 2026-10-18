"""Source-bound native candidate validation; default dry-run, no applications.
Run MQ2 and publish its receipt before invoking RG1 with the same binary.
"""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import argparse,datetime,hashlib,importlib.util,json,os,resource,shlex,shutil,subprocess,sys
R=Path('/workspace/worktrees/accel-sim-ep-l2-microopt20261018-lane1-v1');C=Path('/workspace/worktrees/gpgpu-sim-ep-l2-microopt20261018-lane1-v1');B=Path('/workspace/build/ep-l2-microopt20261018-lane1-v1')
PUBLISH=Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def head(p):return subprocess.check_output(['git','rev-parse','HEAD'],cwd=p,text=True).strip()
def mod(name,p):s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
NEGATIVE_CASES={'reject_'+n for n in ['combined','P2','Ideal','quota','legacy']}
REJECTION_PROOF='EP-L2 service candidate supports single-factor'
def verify_prior_command(row):
 # A successful producer receipt includes deliberate native constructor
 # rejections. Accept only the named, proven negative cases, never arbitrary
 # nonzero exits or a resource/timeout stop masquerading as an expected fail.
 assert sha(row['log'])==row['log_sha256']
 assert 'resource_stop' not in row
 name=row['case_name'];expected=row['expected_exit_code']
 assert Path(row['log']).stem==name and row['exit_code']==expected
 if expected:
  assert name in NEGATIVE_CASES and expected==134 and row.get('expected_failure') is True
  assert row.get('error')==repr(RuntimeError(f'{name} exited {expected}'))
  assert REJECTION_PROOF in Path(row['log']).read_text()
 else:assert name not in NEGATIVE_CASES and not row.get('expected_failure',False) and 'error' not in row

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--phase',choices=['mq2','rg1'],default='mq2');p.add_argument('--execute',action='store_true');p.add_argument('--build-receipt',type=Path);p.add_argument('--reuse-off-receipt',type=Path);a=p.parse_args();o=a.out.resolve();o.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 r={'authority':'c8aa87bdbe220853eb2d27d8babd448cff02a66e','phase':a.phase,'status':'DRY_RUN_PREPARING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'core_source_commit':head(C),'framework_source_commit':head(R),'application_starts':0,'independent_qualification':False,'commands':[],'tests':[],'disk_floor_bytes':48*2**30,'memory_floor_bytes':64*2**30,'profiles':{}}
 def save():(o/'RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
 g=mod('original_guard',R/'util/ep_l2/ft_lane1/build_r0_1.py');base=str(C/'configs/tested-cfgs/SM7_QV100/gpgpusim.config');test=C/'tests/ep_l2';original=g.repair_commands(B,C)
 profiles=[('B16',1,0,'B16_OFF'),('S64',1,1,'S64'),('Unified',2,0,'U_WB16_OFF')]
 old=json.loads((PUBLISH/'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane1/PARALLEL_ALL_DATA_CONFIG_MANIFEST_R1.json').read_text())
 tests=[] if a.reuse_off_receipt else list(original)
 for mode,m,s,profile in profiles:
  for enabled in [0,1]:
   folder=o/'configs'/f'{mode}_{a.phase}_{enabled}';folder.mkdir(parents=True);assets=[]
   for i,x in enumerate(old['profiles'][profile]['configs']):
    src=Path(x['path']);dst=folder/f'config-{i}.config';shutil.copy2(src,dst);assets.append({'name':dst.name,'path':str(dst),'sha256':sha(dst)})
   flag=folder/'service.config';flag.write_text(f'-gpgpu_ep_l2_mq2 {enabled if a.phase=="mq2" else 0}\n-gpgpu_ep_l2_rg1 {enabled if a.phase=="rg1" else 0}\n');assets.append({'name':flag.name,'path':str(flag),'sha256':sha(flag)})
   ordered=[{'name':x['name'],'sha256':x['sha256'],'bytes':Path(x['path']).stat().st_size} for x in assets]
   r['profiles'][folder.name]={'configs':assets,'ordered_config_manifest':ordered,'runtime_config_sha256':hashlib.sha256(json.dumps(ordered,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'effective_status':'NOT_RUN','qualification':'NOT_INHERITED','feature_delta':{'mq2':bool(enabled and a.phase=='mq2'),'rg1':bool(enabled and a.phase=='rg1'),'bank_ops':1,'payload_slots':1168,'banks':4}}
  overlay=o/f'{mode}_{a.phase}.config';overlay.write_text((test/'ft_wbuf.config').read_text()+f'\n-gpgpu_ep_l2_ft_mode {m}\n-gpgpu_ep_l2_wbuf_entries 16\n-gpgpu_ep_l2_static_s64 {s}\n-gpgpu_ep_l2_mq2 {int(a.phase=="mq2")}\n-gpgpu_ep_l2_rg1 {int(a.phase=="rg1")}\n')
  if a.phase=='mq2':
   for variant in ['ordinary','unknown','lower-full']:tests.append((f'MQ2_{mode}_{variant}',[str(B/'gpgpu-sim/ep_l2_micro_mq2'),base,str(overlay),str(m),'1',variant]))
   for target,args in [('ft_host_prefill',[str(m),'16']),('ft_memcpy_clock',[str(m),'16','0']),('ft_memcpy_clock',[str(m),'16','4096']),('ft_a1',[str(m),'16'])]:tests.append((f'MQ2_{mode}_{target}_'+args[-1],[str(B/'gpgpu-sim'/('ep_l2_'+target)),base,str(overlay),*args]))
  else:
   for offset in ['0','4096']:tests.append((f'RG1_{mode}_partition_{offset}',[str(B/'gpgpu-sim/ep_l2_micro_rg1_partition'),base,str(overlay),str(m),'16',str(s),'0','1','1',offset]))
   target='potential_ucap' if m==2 else 'potential_s64';tests.append((f'RG1_{mode}_WB_WAD_copy_drain',[str(B/'gpgpu-sim'/('ep_l2_'+target)),base,str(overlay),str(m),'16',str(s),'0','1']))
 if a.phase=='rg1':tests.append(('RG1_bounded_identity_arbiter',[str(B/'gpgpu-sim/ep_l2_micro_rg1_arbiter')]))
 r['planned_tests']=tests;save()
 if not a.execute:r['status']='DRY_RUN_ONLY_NO_COMPILER_NO_SIMULATOR';save();print(r['status']);return
 assert a.build_receipt
 author=json.loads(a.build_receipt.read_text());assert author['status']=='BUILT_NOT_TESTED_NOT_INDEPENDENTLY_QUALIFIED';assert author['core_source_commit']==head(C) and author['framework_source_commit']==head(R)
 for x in [C,R]:assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=x)
 assert sha(B/'accel-sim.out')==author['binary_sha256'];r['binary_sha256']=author['binary_sha256'];r['author_build_receipt_sha256']=sha(a.build_receipt)
 if a.reuse_off_receipt:
  reuse=json.loads(a.reuse_off_receipt.read_text());assert reuse['status']=='PRODUCER_MQ2_PASS_PENDING_LANE5' and reuse['binary_sha256']==r['binary_sha256'] and reuse['core_source_commit']==r['core_source_commit'] and reuse['framework_source_commit']==r['framework_source_commit']
  for row in reuse['commands']:verify_prior_command(row)
  assert {row['case_name'] for row in reuse['commands'] if row.get('expected_failure')}==NEGATIVE_CASES
  assert {n for n,_ in original}<={row['case_name'] for row in reuse['commands'] if row['exit_code']==0}
  assert set(n for n,_ in original)<=set(reuse['tests']);r['reused_same_binary_OFF_receipt']={'path':str(a.reuse_off_receipt),'sha256':sha(a.reuse_off_receipt)}
 cl=json.loads(Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json').read_text());r['registry_client_sha256']=sha(cl['registry_client'])
 if r['registry_client_sha256']!=cl['registry_client_sha256']:r['status']='CLIENT_BINDING_HOLD_PRELEASE';save();return
 sys.path.insert(0,str(Path(cl['registry_client']).parent));from registry import Registry,local_resources,process_identity
 def resources():
  v=local_resources();s=os.statvfs('/root/share');assert s.f_bavail*s.f_frsize>=40*2**30
  for k in ['disk_free_bytes','available_memory_bytes','share_disk_free_bytes']:
   if k in v:r['min_'+k]=min(r.get('min_'+k,v[k]),v[k])
  return v
 lease=None
 try:
  v=resources();assert v['disk_free_bytes']>=48*2**30+256*2**20
  lease=Registry(cl['canonical_root']).build_lease('lane1',cpu=1,memory=4*2**30);r['lease_id']=lease
  def run(cmd,name,expected=0):
   try:rec=g.run_owned(['/usr/bin/time','-v',*cmd],name,o,dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1'),r,save,resources,process_identity,180)
   except RuntimeError:
    rec=r['commands'][-1]
    if not expected or rec.get('exit_code')!=expected:raise
   assert rec['exit_code']==expected
   rec.update(case_name=name,expected_exit_code=expected,expected_failure=bool(expected))
   verify_prior_command(rec)
   save();return rec
  r['status']='TESTING';save()
  # Test-only capacity correction; simulator/runtime archives remain frozen.
  fixture=Path(__file__).parent/'mq2_recovery_fixtures/test_ft_memcpy_clock_s64.cc'
  r['validation_driver_sha256']=sha(__file__)
  r['fixture_source_sha256']=sha(fixture)
  r['fixture_parent_source_sha256']=sha(C/'tests/ep_l2/test_ft_memcpy_clock.cc')
  fixture_flags={}
  for line in (B/'gpgpu-sim/CMakeFiles/ep_l2_ft_memcpy_clock.dir/flags.make').read_text().splitlines():
   if line.startswith('CXX_'):key,value=line.split(' = ',1);fixture_flags[key]=value
  fixture_libs=[B/'gpgpu-sim'/x for x in ['libentrypoint.a','libcuda/libcuda.a','src/cuda-sim/libptxsim.a','src/gpgpu-sim/libgpgpusim.a','src/intersim2/libintersim.a','src/accelwattch/libaccelwattch.a']]
  exe=o/'clock_s64_fixture'
  run(['/usr/bin/c++',*shlex.split(fixture_flags['CXX_DEFINES']),*shlex.split(fixture_flags['CXX_INCLUDES']),'-I'+str(C/'tests/ep_l2'),'-std=gnu++17','-O0','-g0','-Wl,--strip-debug',str(fixture),'-o',str(exe),'-Wl,--start-group',*map(str,fixture_libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'link_s64_clock_fixture')
  r['corrected_fixture_executable_sha256']=sha(exe)
  r['fixture_archives_sha256']={str(lib):sha(lib) for lib in fixture_libs}
  tests=[(name,[str(exe),*cmd[1:]]) if name.startswith('MQ2_S64_ft_memcpy_clock_') else (name,cmd) for name,cmd in tests]
  r['actual_tests']=tests;save()
  for name,cmd in tests:run(cmd,name);r['tests'].append(name);save()
  # Native effective parser, compiled only against the exact candidate archives.
  flags={}
  for l in (B/'gpgpu-sim/CMakeFiles/ep_l2_ft_a1.dir/flags.make').read_text().splitlines():
   if l.startswith('CXX_'):k,v=l.split(' = ',1);flags[k]=v
  maininc=next(l.split(' = ',1)[1] for l in (B/'CMakeFiles/accel-sim.out.dir/flags.make').read_text().splitlines() if l.startswith('CXX_INCLUDES = '))
  libs=[B/'gpgpu-sim'/x for x in ['libentrypoint.a','libcuda/libcuda.a','src/cuda-sim/libptxsim.a','src/gpgpu-sim/libgpgpusim.a','src/intersim2/libintersim.a','src/accelwattch/libaccelwattch.a']]+[B/'trace-driven/libtrace-driven.a',B/'trace-parser/libtrace-parser.a'];r['archives_sha256']={str(p):sha(p) for p in libs}
  exe=o/'effective';src=R/'util/ep_l2/ft_lane1/parallel_release/effective_config.cc'
  run(['/usr/bin/c++',*shlex.split(flags['CXX_DEFINES']),*shlex.split(maininc),*shlex.split(flags['CXX_INCLUDES']),'-std=gnu++17','-O0','-g0','-Wl,--strip-debug',str(src),'-o',str(exe),'-Wl,--start-group',*map(str,libs),'-Wl,--end-group','-lz','-ldl','-lGL','-lpthread','-lm'],'link_effective')
  r['effective_entry_sha256']=sha(exe)
  for name,row in r['profiles'].items():
   rec=run([str(exe),*[x['path'] for x in row['configs']]],'effective_'+name);text=Path(rec['log']).read_text();assert 'PARALLEL_EFFECTIVE_PASS|' in text
   opts={}
   for l in text.split('NATIVE_EFFECTIVE_OPTIONS_BEGIN\n',1)[1].split('NATIVE_EFFECTIVE_OPTIONS_END',1)[0].splitlines():
    fields=l.split('#',1)[0].strip().split(None,1)
    if fields and fields[0].startswith('-'):opts[fields[0]]=fields[1].strip() if len(fields)>1 else ''
   assert opts['-gpgpu_ep_l2_mq2']==str(int(row['feature_delta']['mq2'])) and opts['-gpgpu_ep_l2_rg1']==str(int(row['feature_delta']['rg1'])) and opts['-gpgpu_ep_l2_bank_ops']=='1'
   row.update(effective_status='NATIVE_PASS',native_options=opts,effective_log_sha256=rec['log_sha256'])
  anchor=next(v for k,v in r['profiles'].items() if k.startswith('B16_') and k.endswith('_0'))
  for name,extra in [('combined','-gpgpu_ep_l2_mq2 1\n-gpgpu_ep_l2_rg1 1'),('P2','-gpgpu_ep_l2_bank_ops 2'),('Ideal','-gpgpu_ep_l2_ideal_meta 1'),('quota','-gpgpu_ep_l2_wb_local_cap 16'),('legacy','-gpgpu_ep_l2_ft_mode 0\n-gpgpu_ep_l2_wbuf_entries 0')]:
   bad=o/('reject_'+name+'.config');bad.write_text(f'-gpgpu_ep_l2_{a.phase} 1\n'+extra+'\n')
   rec=run([str(exe),*[x['path'] for x in anchor['configs']],str(bad)],'reject_'+name,134)
   assert 'EP-L2 service candidate supports single-factor' in Path(rec['log']).read_text()
  assert sha(B/'accel-sim.out')==r['binary_sha256'];r['status']='PRODUCER_'+a.phase.upper()+'_PASS_PENDING_LANE5'
 except BaseException as e:r['status']='FAILED_RETAIN_ALL_NO_RELEASE';r['error']=repr(e);raise
 finally:
  if lease:Registry(cl['canonical_root']).release_build(lease,'lane1');r['lease_released']=True
  r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
 print(r['status'])
if __name__=='__main__':main()
