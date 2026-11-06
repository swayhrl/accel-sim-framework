from pathlib import Path
import types,os,json,threading,fcntl,hashlib
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/R_same_owner_scheduler_recovery_v1');src=A/'oracle_scheduler_recovery.py';source_sha=hashlib.sha256(src.read_bytes()).hexdigest();checks=[];O=A/'partial_install_cpu';O.mkdir(exist_ok=False)
def module():
 m=types.ModuleType('CPU_ONLY_INSTALL_MODULE');m.__file__=str(src);exec(compile(src.read_bytes(),str(src),'exec'),m.__dict__);return m
for case in ['before_start','after_start']:
 m=module();base=O/case;(base/'control').mkdir(parents=True);m.BASE=base;m.OWNER_PID=os.getpid();m.OWNER_START=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);gate=threading.Event();held=(base/'held').open('a+b');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);dup=os.fdopen(os.dup(held.fileno()),'a+b',buffering=0)
 cap=dict(held=held,held_duplicate=dup,lock_identity=dict(CPU_ONLY=True),original_thread_ident=777,running={},post={},reviews={},original_exception='RESOURCE_HOLD_CPU',original_globals=dict(_gate=gate))
 state=dict(lock=threading.RLock(),contexts={});setattr(__import__('__main__'),'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1',state)
 m.capture_handoff=lambda state:cap;m.owner_fd_snapshot=lambda:dict(CPU_ONLY_FD3_FD4=True);m.scientific_preimage=lambda contexts:dict(CPU_ONLY_IMMUTABLE=True)
 m.transformed_scheduler=lambda original:("def recovery_dispatch_loop():\n with _RECOVERY['cap']['held_duplicate']:\n  _gate.wait()\n",[])
 review=base/'CPU_ONLY_REVIEW.json';review.write_text(json.dumps(dict(status='PASS',subject_source_sha256=source_sha,scope='SAME_OWNER_OPERATIONAL_RECOVERY_CPU_QUALIFICATION',CPU_ONLY_NOT_REAL_RELEASE=True)))
 pre=base/'CPU_ONLY_PREIMAGE.json';pre.write_text('{}\n')
 release=base/'CPU_ONLY_RELEASE.json';release.write_text(json.dumps(dict(schema='DTC_ORACLE_OPERATIONAL_RECOVERY_INSTALL_V1',approved_by_DTC_MAIN=True,source_sha256=source_sha,independent_review=dict(path=str(review),sha256=m.sha(review)),coordinator_preimage=dict(path=str(pre),sha256=m.sha(pre)),CPU_ONLY_NOT_REAL_RELEASE=True)))
 originalput=m.put
 def put(path,value,exclusive=False):
  if Path(path).name==('HANDOFF.fixed.json'if case=='before_start'else'INSTALL_ACK.fixed.json'):raise OSError('CPU_INJECTED_INSTALL_IO_ERROR')
  return originalput(path,value,exclusive)
 m.put=put
 try:m.install(release)
 except OSError:pass
 else:raise AssertionError('INJECTED_FAILURE_NOT_OBSERVED')
 record=state[m.GENERATION]
 if case=='before_start':
  assert dup.closed and not held.closed and record['install_status']=='FAILED_BEFORE_NEW_DISPATCH_FORWARD_ONLY';checks.append('PRESTART_FAILURE_CLOSES_ONLY_DUPLICATE_AND_RECORDS_FORWARD_ONLY')
 else:
  assert not dup.closed and not held.closed and record['install_status']=='STARTED_ACK_UNCERTAIN_FORWARD_ONLY'and record['thread'].is_alive();checks.append('POSTSTART_ACK_FAILURE_PRESERVES_LIVE_DUPLICATE_NO_RESTART')
  gate.set();record['thread'].join(3);assert not record['thread'].is_alive()and dup.closed;checks.append('CONTROLLED_CPU_THREAD_EXIT_CLOSES_OWN_DUPLICATE_ONLY')
 assert not held.closed;held.close()
 # Actual addon is never touched; private mock state retains failed marker and
 # capture_handoff itself rejects duplicate generation.
 try:module().capture_handoff(state)
 except AssertionError:checks.append('PARTIAL_GENERATION_REJECTS_AUTOMATIC_DUPLICATE_HANDOFF_'+case)
 else:raise AssertionError('DUPLICATE_ACCEPTED')
# An unrelated PASS review must not satisfy source-bound independent gate.
m=module();m.OWNER_PID=os.getpid();m.OWNER_START=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);review=O/'WRONG_REVIEW.json';review.write_text(json.dumps(dict(status='PASS',subject_source_sha256='0'*64,scope='OLD_UNRELATED_REVIEW')));release=O/'WRONG_RELEASE.json';release.write_text(json.dumps(dict(schema='DTC_ORACLE_OPERATIONAL_RECOVERY_INSTALL_V1',approved_by_DTC_MAIN=True,source_sha256=source_sha,independent_review=dict(path=str(review),sha256=m.sha(review)))))
try:m.install(release)
except AssertionError:checks.append('UNRELATED_PASS_REVIEW_REJECTED_BEFORE_DUPLICATE')
else:raise AssertionError('UNRELATED_REVIEW_ACCEPTED')
assert hashlib.sha256(src.read_bytes()).hexdigest()==source_sha
report=dict(status='PASS',source_sha256=source_sha,checks=checks,actual_owner_installs=0,actual_models=0,actual_registry_writes=0,all_install_calls_private_CPU_monkey_context_only=True)
with(A/'PARTIAL_INSTALL_CPU_QUALIFICATION.json').open('x')as f:json.dump(report,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps(report,indent=2))
