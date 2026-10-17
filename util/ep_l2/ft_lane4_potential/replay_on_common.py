"""Compile only new fixtures against an exact already-built Lane1 runtime."""
import argparse,hashlib,importlib.util,json,os,resource,shlex,shutil,subprocess,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def head(p):return subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--producer-receipt',type=Path,required=True)
 p.add_argument('--author-core',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 b=json.loads(a.producer_receipt.read_text());assert b['status'].startswith('BUILT'),b['status']
 frozen=Path(b['core']);build=Path(b['build']);assert head(frozen)==b['core_source_commit']
 for tree in [frozen,a.author_core]:assert not subprocess.check_output(['git','-C',str(tree),'status','--porcelain','--untracked-files=no'])
 cpath=Path('/workspace/ep_l2_ft20261016_shared/CLIENT_CONTRACT.json');client=json.loads(cpath.read_text());path=Path(client['registry_client'])
 assert sha(path)==client['registry_client_sha256'],'current client hash mismatch'
 spec=importlib.util.spec_from_file_location('lane4_common_replay_registry',path);api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
 reg=api.Registry(client['canonical_root']);a.out.mkdir(parents=True,exist_ok=False);lease=None
 r=dict(status='PREFLIGHT',producer_receipt=str(a.producer_receipt),producer_receipt_sha256=sha(a.producer_receipt),
  runtime_source=b['core_source_commit'],author_fixture_source=head(a.author_core),client_contract_sha256=sha(cpath),
  registry_sha256=sha(path),driver_sha256=sha(__file__),full_application_starts=0,commands=[],runtime_blobs={})
 def save():(a.out/'REPLAY_RECEIPT.json').write_text(json.dumps(r,indent=2)+'\n')
 def resources():
  v=api.local_resources();assert v['disk_free_bytes']>=48*1024**3 and v['available_memory_bytes']>=64*1024**3
  assert v['share_disk_free_bytes']>=40*1024**3
  return v
 def run(name,cmd,expected=0,marker=None):
  resources();log=a.out/(name+'.log');start=time.monotonic()
  with log.open('x') as f:q=subprocess.run(cmd,cwd=build/'gpgpu-sim',stdout=f,stderr=subprocess.STDOUT,timeout=180)
  passed=q.returncode==expected and (not marker or marker in log.read_text(errors='replace'))
  r['commands'].append(dict(name=name,command=cmd,returncode=q.returncode,expected_returncode=expected,
   required_log_marker=marker,passed=passed,log=str(log),log_sha256=sha(log),seconds=time.monotonic()-start));save()
  print(name,q.returncode,'PASS' if passed else 'FAIL',flush=True)
  return passed
 try:
  resources();lease=reg.build_lease('lane4',cpu=1,memory=2*1024**3);r['lease_id']=lease;save()
  for file in ['ep-l2-all-data-reference.h','ep-l2-all-data-ldst.inc','ep-l2-ideal-reference.h']:
   left=frozen/'src/gpgpu-sim'/file;right=a.author_core/'src/gpgpu-sim'/file
   assert sha(left)==sha(right),'runtime reference differs; review/adapt before replay'
   r['runtime_blobs'][file]=sha(left)
  r['common_binary_sha256']=sha(build/'accel-sim.out')
  root=a.out/'source';test=root/'tests/ep_l2';test.mkdir(parents=True)
  (root/'src').symlink_to(frozen/'src',target_is_directory=True);(root/'libcuda').symlink_to(frozen/'libcuda',target_is_directory=True)
  for file in ['ft_test_fixture.h','ideal_test_fixture.h']:shutil.copy2(frozen/'tests/ep_l2'/file,test/file)
  r['fixture_headers']={f:sha(test/f) for f in ['ft_test_fixture.h','ideal_test_fixture.h']};r['artifacts']={}
  resource.setrlimit(resource.RLIMIT_CORE,(0,0))
  for name in ['ideal_meta','all_data_reference','all_data_ldst']:
   src=a.author_core/'tests/ep_l2'/('test_'+name+'.cc');dest=test/src.name;shutil.copy2(src,dest)
   cm=build/'gpgpu-sim/CMakeFiles'/('ep_l2_'+name+'.dir')
   flags={line.split(' = ')[0]:shlex.split(line.split(' = ')[1]) for line in (cm/'flags.make').read_text().splitlines() if ' = ' in line}
   cmd=shlex.split((cm/'link.txt').read_text());cmd[1:1]=flags['CXX_DEFINES']+flags['CXX_INCLUDES']+flags['CXX_FLAGS']
   cmd=[str(dest) if x.endswith(src.name+'.o') else x for x in cmd];cmd[cmd.index('-o')+1]=str(a.out/('ep_l2_'+name))
   r.setdefault('runtime_libraries',{}).update({x:sha(build/'gpgpu-sim'/x) for x in cmd if x.endswith('.a')})
   assert run('compile_'+name,cmd),'fixture compile failed'
   r['artifacts'][name]=dict(source_sha256=sha(dest),binary_sha256=sha(a.out/('ep_l2_'+name)));save()
  base=str(frozen/'configs/tested-cfgs/SM7_QV100/gpgpusim.config');t=frozen/'tests/ep_l2'
  native=str(a.out/'ep_l2_all_data_ldst');ref=str(a.out/'ep_l2_all_data_reference')
  tests=[('metadata_real_requests',[str(a.out/'ep_l2_ideal_meta'),base,str(t/'ft_wbuf.config')],0,'tests: PASS'),
   ('reference',[ref],0,'ALL_DATA_REFERENCE_RAW_WAR_MASK_HOST_CLOCK_BURST_SHARED_SCOPE PASS'),
   ('duplicate_instruction',[ref,'--duplicate'],-6,'EPL2MEMREF_DUPLICATE_ORIGINAL_INSTRUCTION'),
   ('duplicate_access',[ref,'--duplicate-access'],-6,'EPL2MEMREF_DUPLICATE_NATIVE_ACCESS'),
   ('native_ldst',[native,base,str(t/'all_data_reference.config')],0,'ALL_DATA_NATIVE_LDST_SPACES_PENDING_REGISTER_STORE_COMPLETION PASS'),
   ('native_clock4096',[native,base,str(t/'all_data_reference.config'),'--offset4096'],0,'ALL_DATA_NATIVE_LDST_SPACES_PENDING_REGISTER_STORE_COMPLETION PASS'),
   ('unsupported_ldgsts',[native,base,str(t/'all_data_reference.config'),'--unsupported'],-6,'EPL2MEMREF_UNSUPPORTED|atomic=0|ldgsts=1'),
   ('unsupported_atomic',[native,base,str(t/'all_data_reference.config'),'--atomic'],-6,'EPL2MEMREF_UNSUPPORTED|atomic=1|ldgsts=0'),
   ('native_read_hit_rop160',[str(build/'gpgpu-sim/ep_l2_ideal_read_hit'),base,str(a.author_core/'tests/ep_l2/ideal_read_hit_rop160.config')],0,'I_READ_HIT_ACTUAL_ROP_GPU_CYCLES=160')]
  for name,cmd,want,marker in tests:run(name,cmd,want,marker)
  assert head(frozen)==b['core_source_commit'] and head(a.author_core)==r['author_fixture_source']
  assert sha(build/'accel-sim.out')==r['common_binary_sha256']
  r['status']='PRODUCER_FIXTURES_PASS_NOT_INDEPENDENT_QUALIFICATION' if all(c['passed'] for c in r['commands']) else 'FIXTURE_FAILURE_PRESERVED'
 except BaseException as error:r.update(status='FAILED_OR_RESOURCE_HOLD',error=repr(error));raise
 finally:
  if lease is not None:reg.release_build(lease,'lane4')
  save()
 if r['status']!='PRODUCER_FIXTURES_PASS_NOT_INDEPENDENT_QUALIFICATION':raise SystemExit(1)
if __name__=='__main__':main()
