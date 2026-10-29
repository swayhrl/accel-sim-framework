"""Native exact2 per-kernel multistream records and grouped data POST metadata/lease/SSH relay only; no body or model on Native."""
from pathlib import Path
import os,sys,json,hashlib,resource,subprocess,shlex,time,fcntl,signal,types,stat,traceback
P=Path(__file__).resolve().parent
def need(v,m):
 if not v:raise RuntimeError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,j,replace=False):
 p=Path(p);q=p.with_name(p.name+'.own_tmp')if replace else p
 with q.open('x')as f:json.dump(j,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 if replace:os.replace(q,p)
def tick(pid):
 try:return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
 except FileNotFoundError:return None
def main():
 need(len(sys.argv)==3,'Rootscope rawSHA');sp=Path(sys.argv[1]);st=sp.stat();need(sp.parent==Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')and st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o600,'ROOT_NATIVE0600')
 raw=sp.read_bytes();h=hashlib.sha256(raw).hexdigest();need(h==sys.argv[2],'ROOT_RAW_SCOPE');a=json.loads(raw)
 need(a['coactivity_role']=='CPU_POST'and type(a['cpu_slot_index'])is int and a['cpu_slot_index']in [0,1]and a['cpu_ids']==[[2],[3]][a['cpu_slot_index']],'ROOT_EXACT_CPU_POST_SHARED_ROLE_SLOT')
 need(type(a['post_scratch_budget_bytes'])is int and a['post_scratch_budget_bytes']==24*2**30,'ROOT_EXACT_24GIB_NAS_SCRATCH_NOT_RAM')
 need(a['status']=='ROOT_APPROVED_CPU_ONLY_REPEAT_ONLY_F9_POST_NO_MODEL'and a['schema']=='ROOT_REPEAT_ONLY_SINGLE_STREAM_NAS_CPU1_SCOPE_V1','NEW_CPU6_ROLE_ADMISSION')
 need(a['unknown_owned_closure_policy']=='HOLD_GUARD_AND_CANONICAL_IO_NO_SYSTEMD_RUNTIME_KILL','EXACT_UNKNOWN_GUARD_HOLD_POLICY')
 need(a['native_runtime_root']==str(P)and a['not_before_unix']<=time.time()<a['absolute_deadline_unix']<=a['not_before_unix']+7200,'EXACT_NATIVE_ROOT_FINITE7200')
 need(__import__('socket').gethostname()==a['native_host'] and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==a['native_boot_id'],'ROOT_NATIVE_HOST_BOOT')
 need(sha(P/'CODE_MANIFEST.json')==a['code_manifest_sha256'],'MF_SOURCE')
 for n,r in json.loads((P/'CODE_MANIFEST.json').read_text())['files'].items():need((P/n).stat().st_size==r['bytes']and sha(P/n)==r['sha256'],'EXACT_SMALL_CODE_METADATA '+n)
 resource.setrlimit(resource.RLIMIT_AS,(128*2**20,128*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.nice(15);os.sched_setaffinity(0,{501})
 helper=a['Native_kernel_helper_ref'];need(helper=={'path': '/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/native_light512_kernel_resource_prepare_20261029_v2/native_light512_kernel_gate_v2.py', 'bytes': 6262, 'sha256': '06b8abe6c591d86043182b8b398be49104dc6cf9e4e448e98b2c3ef47795fae6'},'ROOT_EXACT_APPROVED_KERNEL_HELPER')
 q=Path(helper['path']);b=q.read_bytes();need(len(b)==helper['bytes']and hashlib.sha256(b).hexdigest()==helper['sha256'],'APPROVED_KERNEL_SOURCE_SAME_RAW_PIN');R=types.ModuleType('cached_native_kernel_role');R.__file__=str(q);exec(compile(b,str(q),'exec'),R.__dict__)
 need(a['Native_broker_policy']==R.POLICY,'EXACT_KERNEL_ONLY_NATIVE512_ROLE')
 def kernel_gate(out):
  snapshot=R.collect();verdict=R.evaluate(snapshot,R.POLICY);save(out/('NATIVE_RESOURCE_'+str(time.time_ns())+'.json'),dict(snapshot=snapshot,kernel_only_verdict=verdict,foreign_forecast_not_claimed_PASS=True,helper_ref=helper));need(verdict['status']=='PASS','NATIVE_KERNEL512_HEADROOM_OOM_PSI')
 out=P/'native_actual_a001';need(not out.exists(),'ONE_NATIVE_ATTEMPT');out.mkdir();kernel_gate(out)
 locks=[];stopped=False;launched=False;proc=None;channel=None;me=[os.getpid(),tick(os.getpid())]
 need(a['cpu_ids']in [[2],[3]],'ONE_APPROVED_CPU_2_OR_3');jobs=a['qids'];need(type(jobs)is list and len(jobs)==1 and len(set(jobs))==1 and a['runtime_root']==a['remote_runtime_root'],'EXACT_REPEAT_ONLY_QIDS_AND_REMOTE_ALIAS')
 expected=['/root/data/shared_rtx4080_trace_library_20261024_v1/control/asset_operations/'+job+'/'+name+'.lock'for job in jobs for name in ['CAPTURE','INPUT','OUTPUT','RUNTIME']]
 need([r['path']for r in a['Native_asset4_expected']]==expected,'ONLY_EXACT_G6_NATIVE_ASSET4')
 for row in a['Native_asset4_expected']:
  p=Path(row['path']);need(not p.is_symlink(),'EXACT_EXISTING_ASSET_LOCK');fd=os.open(p,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC);z=os.fstat(fd)
  need((z.st_dev,z.st_ino)==(row['dev'],row['inode'])and z.st_uid==0 and stat.S_IMODE(z.st_mode)==0o600 and z.st_size==0,'FIXED_NATIVE_ASSET4')
  fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(fd)
 with(P/'ROOT_REPEAT_ONLY_CPU_SCOPE.raw.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
 def stop(sig,frame):
  nonlocal stopped
  stopped=True
  if channel is not None:channel.stop('NATIVE_SIGNAL_'+str(sig))
 for sig in[signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,stop)
 cp=P/'ssh_stdin_light_control_v2.py';cb=cp.read_bytes();need(hashlib.sha256(cb).hexdigest()==a['control_channel_sha256']=='63a962a8f9bda7ebb652f07ec143d519d632f98006c540c39e6691b8a6bcda7f','ROOT_SHARED_CONTROL_SOURCE')
 Wire=types.ModuleType('Root_shared_ssh_stdin_control');Wire.__file__=str(cp);exec(compile(cb,str(cp),'exec'),Wire.__dict__)
 need(a['control_transport']=='SSH_STDIN_LIGHT_CONTROL_V1' and a['owned_lease_type']=='ROOT_PRIVATE_MEMFD_FLOCK_NO_GLOBAL_CPU6','ROOT_NEW_CHANNEL_PRIVATE_FD_ROLE')
 def sample_only_kernel():
  # Single cached helper instance: the sampler thread alone updates its BASELINES after initial preflight.
  return R.evaluate(R.collect(),R.POLICY)
 rb=a['remote_runtime_root'];unit='ep-repeat_only-single-'+a['run_id']
 cmd=['systemd-run','--user','--quiet','--wait','--collect','--pipe','--unit='+unit,'--property=MemoryMax='+str(2*2**30),'--property=MemorySwapMax=0','--property=TasksMax=32','--property=LimitAS=infinity','--property=OOMPolicy=kill','--property=CPUQuota=100%','--property=AllowedCPUs='+str(a['cpu_ids'][0]),'--property=KillMode=control-group','--property=TimeoutStopSec=30','--','/usr/bin/python3','-I','-S','-B',rb+'/repeat_only_f9_post_once_v1.py',rb+'/ROOT_REPEAT_ONLY_CPU_SCOPE.raw.json',h]
 ssh=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','ControlMaster=no','-o','ControlPath=none','gpu109']
 try:
  with(out/'REMOTE.stdout.log').open('xb')as stdout,(out/'REMOTE.stderr.log').open('xb')as stderr:proc=subprocess.Popen(ssh+[shlex.join(cmd)],stdin=subprocess.PIPE,bufsize=0,stdout=stdout,stderr=stderr,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
  launched=True
  channel=Wire.NativeChannel(proc.stdin.fileno(),h,a['run_id'],sample_only_kernel,a['absolute_deadline_unix'])
  channel.start()
  save(out/'NATIVE_START.json',dict(owner=me,ssh_owner=[proc.pid,tick(proc.pid)],scope_sha256=h,run_id=a['run_id'],code_manifest_sha256=a['code_manifest_sha256'],Native_role_AS=[128*2**20,128*2**20],Native_total_metadata_envelope=512*2**20,Native_body_IO_allowed=False))
  last=0
  while proc.poll()is None:
   if time.time()>=a['absolute_deadline_unix']:channel.stop('NATIVE_ABSOLUTE_DEADLINE')
   if stopped:channel.stop('NATIVE_OWN_STOP_REQUESTED')
   # NAS diagnostics are main-thread-only and cannot block sender or pure-kernel sampler.
   if time.time()-last>=30:
    save(out/('NATIVE_CHANNEL_STATE_'+str(time.time_ns())+'.json'),channel.snapshot());last=time.time()
   time.sleep(1)
  rc=proc.wait()
  script="""from pathlib import Path
import json,os,fcntl,hashlib,stat
P=Path("""+repr(rb)+""");T=P/'runs'/"""+repr(a['run_id'])+"""
def readsmall(p):
 assert not p.is_symlink()
 with p.open('rb')as f:
  x=os.fstat(f.fileno());assert stat.S_ISREG(x.st_mode)and x.st_size<=4*2**20
  chunks=[];n=0
  while True:
   b=f.read(65536)
   if not b:break
   n+=len(b);assert n<=4*2**20;chunks.append(b)
  z=os.fstat(f.fileno());key=lambda v:(v.st_dev,v.st_ino,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
  assert key(x)==key(z)
 raw=b''.join(chunks);q=p.stat();assert(x.st_dev,x.st_size,x.st_mtime_ns,x.st_ctime_ns)==(q.st_dev,q.st_size,q.st_mtime_ns,q.st_ctime_ns)
 return raw,dict(path=str(p),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
sr,sref=readsmall(T/'START.json');tr,tref=readsmall(T/'RESOURCE_AND_CLOSURE.json');s=json.loads(sr);t=json.loads(tr)
assert s['scope_sha256']==t['scope_sha256']=="""+repr(h)+"""
assert s['run_id']==t['run_id']=="""+repr(a['run_id'])+"""
assert s['code_manifest_sha256']==t['code_manifest_sha256']=="""+repr(a['code_manifest_sha256'])+"""
assert s['owner']==t['owner'] and s['boot']==t['boot']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
assert s['cgroup']==t['cgroup'] and t['tracked_children']==[] and t['CPU_slot_closed_after_owned_wait'] is True
assert t['SSH_stdin_reader_joined_after_owned'] is True
assert t['canonical_IO_closed_after_owned'] is True
if t['canonical_IO_descriptor'] is not None:
 expected_sp=t['canonical_IO_descriptor']['bindings']['io_coactivity'];assert expected_sp['role']=='CPU_POST'and expected_sp['slot_index']in [0,1]
 assert [r['path']for r in t['canonical_IO_descriptor']['files']]==['/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_NAS_SHARED_CPU_POST_ROLE_'+str(expected_sp['slot_index'])+'.lock','/data/c16/rtx4080_suite_fill_20261024_v1/control/RTX4080_LOCAL_IO.lock']
 assert [r['lock_mode']for r in t['canonical_IO_descriptor']['files']]==['WRITE','READ']
 assert expected_sp['contract_ref']=="""+repr(a['coactivity_contract_ref'])+"""
 assert expected_sp['slot_index']=="""+repr(a['cpu_slot_index'])+""" and expected_sp['cpu_ids']=="""+repr(a['cpu_ids'])+"""
 assert expected_sp['code_manifest_sha256']==s['code_manifest_sha256'] and expected_sp['job_id']=="""+repr(a['qids'][0])+"""
 assert expected_sp['source_manifest_sha256']=="""+repr(a['source_manifest_ref']['sha256'])+""" and expected_sp['input_identity_sha256']=="""+repr(a['input_identity_ref']['sha256'])+"""
 assert t['canonical_IO_descriptor']['bindings']['Root_sha256']==t['scope_sha256']

 assert t['canonical_IO_descriptor']['bindings']['scope_sha256']==t['scope_sha256'] and t['canonical_IO_descriptor']['bindings']['run_id']==t['run_id']
def gone(pid,ticks):
 try:return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]!=ticks
 except FileNotFoundError:return True
assert gone(t['owner'][0],t['owner'][1])
cg=Path(t['cgroup']);assert str(cg).endswith('/"""+unit+""".service')
pop=0 if not cg.exists()else int(dict(l.split()for l in(cg/'cgroup.events').read_text().splitlines()).get('populated',1));assert pop==0
owned=s['CPU_slot'];assert owned['type']=='ROOT_PRIVATE_MEMFD_FLOCK'and owned['path']=='/memfd:REPEAT_ONLY_OWNED_CPU_POST_LEASE (deleted)'
ls=[line.split()[2:]for line in owned['actual_fdinfo'].splitlines()if line.startswith('lock:')]
assert len(ls)==1 and ls[0][:4]==['FLOCK','ADVISORY','WRITE',str(t['owner'][0])]
# Private descriptor has no global pathname/queue: after exact owner absent+cgempty, no owned copy can remain.
result_ref=failure_ref=None;qualification='FAILED_RETAINED';qual_error=None
if(T/'CPU_FAILURE_RETAINED.json').exists():
 fr,failure_ref=readsmall(T/'CPU_FAILURE_RETAINED.json')
if(T/'CPU_RESULT.json').exists():
 rr,result_ref=readsmall(T/'CPU_RESULT.json')
 try:
  result=json.loads(rr)
  ok=result['scope_sha256']==s['scope_sha256']and result['run_id']==s['run_id']and result['code_manifest_sha256']==s['code_manifest_sha256']
  ok=ok and t['error']is None and result['status']=='REPEAT_ONLY_SINGLE_STREAM_F9_RECORDS_AND_GROUPS_CLOSED'
  ok=ok and len(result['cases'])==1 and result['strict_single_stream_ordinary']is True and result['inter_stream_happens_before']=='NOT_APPLICABLE_SINGLE_EXPLICIT_STREAM'and result['full_application_concurrent_model']is False and result['consumer_qualification']is False and result['whole_input_functional']is False and result['numeric_performance_science_genericCFI']is False and result['actual_input_capsules']is False
  if ok:qualification='PASS_REPEAT_ONLY_SINGLE_STREAM_F9_GROUP_DATA_NO_MODEL'
  else:qual_error='CPU result not matching exact accepted conditions; original raw refs retained'
 except (ValueError,KeyError,TypeError)as e:qual_error=type(e).__name__
else:qual_error='CPU_RESULT_MISSING_OR_FAILED; resources independently closed; no qualification granted'
terminal=dict(status=qualification,scope_sha256=t['scope_sha256'],run_id=t['run_id'],code_manifest_sha256=t['code_manifest_sha256'],owner=t['owner'],boot=t['boot'],cgroup=t['cgroup'],resources_closed=True,qualification_error=qual_error,CPU_result_ref=result_ref,CPU_failure_ref=failure_ref,resource_closure_ref=tref,START_ref=sref,last_resource_summary=t.get('last_resource_summary'),resource_snapshot_count=len(t.get('resource_snapshot_refs',[])))
print(json.dumps(dict(status='EXACT_REPEAT_ONLY_SCOPE_KERNEL_AND_OWNED_CLOSED',terminal=terminal,cgroup_populated=pop,all_identity_absent=True,private_memfd_owned_copies_closed_by_PID_and_cgroup=True)))
"""
  z=subprocess.run(ssh+['/usr/bin/python3 -I -S -B -c '+shlex.quote(script)],capture_output=True,timeout=30);need(z.returncode==0,'REAL_INDEPENDENT_109_CLOSURE '+z.stderr.decode(errors='replace')[-1500:])
  observed=json.loads(z.stdout);save(out/'INDEPENDENT109_CLOSURE.json',observed)
  channel.finish_after_owned_closed();save(out/'SSH_STDIN_CHANNEL_THREADS_CLOSED.json',dict(state=channel.snapshot(),remote_owned_independently_closed=True,SSH_returncode=rc))
  proc.stdin.close()
  for fd in reversed(locks):os.close(fd)
  locks=[];save(out/'NATIVE_ASSET4_RELEASED.json',dict(status='REMOTE_TERMINAL_EXACT_KERNEL_EMPTY_ASSET4_RELEASED',scope_sha256=h,run_id=a['run_id'],owner=me,remote_service_returncode=rc,remote_status=observed['terminal']['status'],Native_body_IO_performed=False,source_KEEP=True,release_bytes=0))
 except BaseException as e:
  if channel is not None:channel.stop('NATIVE_RETAINED_CONTROL_ERROR')
  save(out/'ATTENTION_RETAINED.json',dict(error=repr(e),traceback=traceback.format_exc(),launched=launched,channel_state=None if channel is None else channel.snapshot()))
  if not launched:
   for fd in reversed(locks):os.close(fd)
   raise
  # Never release Native source leases after SSH/closure uncertainty.
  while True:time.sleep(10)
if __name__=='__main__':main()
