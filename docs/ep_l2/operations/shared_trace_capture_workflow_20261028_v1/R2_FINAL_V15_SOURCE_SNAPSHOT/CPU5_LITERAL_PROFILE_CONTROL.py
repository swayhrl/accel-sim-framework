
"""Fixed8 prepare-only Native metadata leases and approved SSH stdin control. No Native body IO."""
from pathlib import Path
import os,sys,json,hashlib,types,time,resource,subprocess,shlex,fcntl,stat,signal
P=Path(__file__).resolve().parent
HELPER=Path('/root/share/mnt164/huangrulin/traces/receipts/rtx4080_specialist_adaptation_20261026_v1/native_light512_kernel_resource_prepare_20261029_v2/native_light512_kernel_gate_v2.py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
 if not v:raise RuntimeError(m)
def save(p,j):
 with Path(p).open('x')as f:json.dump(j,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
def tick(pid):
 try:return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
 except FileNotFoundError:return None
def mod(p,name):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def main():
 need(len(sys.argv)==3,'Rootscope+SHA');sp=Path(sys.argv[1]);ss=sp.stat();need(sp.parent==Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')and ss.st_uid==0 and stat.S_IMODE(ss.st_mode)==0o600,'Root0600');raw=sp.read_bytes();h=hashlib.sha256(raw).hexdigest();need(h==sys.argv[2],'exact scope');a=json.loads(raw)
 need(a['schema']=='ROOT_REMAINING3_ENTRY_DERIVE_PREPARE_V5'and a['status']=='ROOT_APPROVED_REMAINING3_ENTRY_DERIVE_PREPARE_ONCE','Root exact prepare');need(a['native_runtime_root']==str(P)and a['not_before_unix']<=time.time()<a['absolute_deadline_unix']<=a['not_before_unix']+a['outer_wall_seconds'],'Root finite3600')
 need(sha(P/'PREPARE_SOURCE_MANIFEST_V1.json')==a['code_manifest_sha256'],'MF');mf=json.loads((P/'PREPARE_SOURCE_MANIFEST_V1.json').read_text())
 for n,r in mf['files'].items():need((P/n).stat().st_size==r['bytes']and sha(P/n)==r['sha256'],'source pin '+n)
 resource.setrlimit(resource.RLIMIT_AS,(128*2**20,128*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0));os.sched_setaffinity(0,{494});os.nice(15)
 need(HELPER.stat().st_size==6262 and sha(HELPER)=='06b8abe6c591d86043182b8b398be49104dc6cf9e4e448e98b2c3ef47795fae6','Root fixed kernel helper');K=mod(HELPER,'cached_kernel512');need(a['Native_broker_policy']==K.POLICY,'exact Native role');need(sha(P/'ssh_stdin_light_control_v2.py')=='63a962a8f9bda7ebb652f07ec143d519d632f98006c540c39e6691b8a6bcda7f','approved channel');Channel=mod(P/'ssh_stdin_light_control_v2.py','approved_stdin_control')
 packet=json.loads((P/'EXACT_REPEAT_ROWS_POST_SMOKE_ARCHIVE_INPUTS_V2.json').read_text());need(a['asset_ids']==[x for r in packet['rows']for x in[r['ordinary_asset_id'],r['derived_asset_id']]],'exact10 IDs');jobs=[r['job_id']for r in packet['rows']];mod(P/'remaining3_derive_packet_contract_v1.py','packet3').validate_packet(packet);need(a['job_ids']==jobs==['CUDA118_CONVOLUTION_SEPARABLE_ORIGINAL_3072_REPEAT2_V1'] and 0<a['per_job_wall_seconds']<=3600 and 0<a['outer_wall_seconds']<=3600*len(jobs),'EXACT_REMAINING3_FINITE_ENTRY_QUEUE');need(a['CPU']==[5]and a['hard_bytes']==a['AS_bytes']==536870912 and a['peer_bytes']==28*2**30,'EXACT_DERIVE_CPU5_512_PEER28');expected=[str(Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/asset_operations')/q/(n+'.lock'))for q in jobs for n in ['CAPTURE','INPUT','OUTPUT','RUNTIME']];need([r['path']for r in a['Native_asset4_expected']]==expected,'exact Native20')
 out=P/'native_prepare_a001';out.mkdir(exist_ok=False);locks=[];proc=None;channel=None;launched=False;last_sample={}
 def sample():
  # Shared cached module baseline; deliberately no NAS/file logger in callback.
  snapshot=K.collect();verdict=K.evaluate(snapshot,K.POLICY);last_sample.clear();last_sample.update(snapshot=snapshot,verdict=verdict);return verdict
 initial=sample();need(initial['status']=='PASS','initial kernel role');me=[os.getpid(),tick(os.getpid())]
 ssh=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','ControlMaster=no','-o','ControlPath=none','gpu109']
 try:
  for r in a['Native_asset4_expected']:
   f=Path(r['path']);need(not f.is_symlink(),'no lock symlink');fd=os.open(f,os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC);z=os.fstat(fd);need((z.st_dev,z.st_ino)==(r['dev'],r['inode'])and z.st_uid==0 and stat.S_IMODE(z.st_mode)==0o600 and z.st_size==0,'existing Root lock');fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(fd)
  with(P/'ROOT_REMAINING3_ENTRY_PREPARE_SCOPE_A001.raw.json').open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  rb=a['runtime_root'];cmd=['systemd-run','--user','--quiet','--wait','--collect','--pipe','--unit='+a['service_unit'],'--property=MemoryMax=536870912','--property=MemorySwapMax=0','--property=LimitAS=536870912','--property=OOMPolicy=kill','--property=CPUQuota=100%','--property=AllowedCPUs=5','--property=RuntimeMaxSec='+str(a['outer_wall_seconds']),'--property=TimeoutStopSec=30','--property=KillMode=control-group','--','/usr/bin/python3','-I','-S','-B',rb+'/derive_repeat_rows_views109_v2.py',rb+'/ROOT_REMAINING3_ENTRY_PREPARE_SCOPE_A001.raw.json',h]
  with(out/'REMOTE.stdout').open('xb')as so,(out/'REMOTE.stderr').open('xb')as se:proc=subprocess.Popen(ssh+[shlex.join(cmd)],stdin=subprocess.PIPE,stdout=so,stderr=se,bufsize=0,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
  launched=True;channel=Channel.NativeChannel(proc.stdin.fileno(),h,a['run_id'],sample,a['absolute_deadline_unix']).start();signal.signal(signal.SIGTERM,lambda *_:channel.stop('NATIVE_OWNER_SIGNAL'));signal.signal(signal.SIGINT,lambda *_:channel.stop('NATIVE_OWNER_SIGNAL'))
  save(out/'START.json',dict(owner=me,ssh_owner=[proc.pid,tick(proc.pid)],scope_sha256=h,run_id=a['run_id'],code_manifest_sha256=a['code_manifest_sha256'],initial_kernel_verdict=initial,Native_AS=resource.getrlimit(resource.RLIMIT_AS),Native_payload_body_IO=False,asset_lock_count=len(expected),stdin_control=True))
  rc=proc.wait();save(out/'SSH_TRUE_WAIT.json',dict(returncode=rc,real_Popen_wait=True))
  script="""from pathlib import Path
import json,resource
resource.setrlimit(resource.RLIMIT_AS,(128*2**20,128*2**20))
P=Path("""+repr(rb)+""");r=json.loads((P/'actual_prepare_a001/FINAL_OWNED_TERMINAL.json').read_text());assert r['scope_sha256']=="""+repr(h)+"""and r['run_id']=="""+repr(a['run_id'])+"""and r['all_owned_children_closed']and r['all_control_threads_closed']
p=r['pid'];t=r['ticks']
try:assert Path('/proc',str(p),'stat').read_text().rsplit(')',1)[1].split()[19]!=t
except FileNotFoundError:pass
cg=Path(r['cgroup']);assert str(cg).endswith('/"""+a['service_unit']+""".service');pop=0 if not cg.exists()else int(dict(x.split()for x in(cg/'cgroup.events').read_text().splitlines())['populated']);assert pop==0
print(json.dumps(dict(status='EXACT_OWNED_AND_CGROUP_CLOSED',terminal=r,cgroup_populated=pop,exact_owner_absent=True)))
"""
  observed=subprocess.run(ssh+['/usr/bin/python3 -I -S -B -c '+shlex.quote(script)],capture_output=True,timeout=30);need(observed.returncode==0,'independent owned closure '+observed.stderr.decode(errors='replace')[-1000:]);obs=json.loads(observed.stdout);save(out/'INDEPENDENT109_CLOSURE.json',obs)
  channel.finish_after_owned_closed();proc.stdin.close();save(out/'CONTROL_SENDER_CLOSED.json',dict(state=channel.snapshot(),last_kernel_sample=last_sample,control_threads_joined=True));channel=None
  for fd in reversed(locks):os.close(fd)
  locks=[];save(out/'NATIVE_ASSET4_RELEASED.json',dict(owner=me,scope_sha256=h,remote_real_service_returncode=rc,remote_status=obs['terminal']['status'],owned_closed=True,SourceKEEP=True,release_bytes=0))
 except BaseException as e:
  save(out/'ATTENTION_RETAINED.json',dict(error=repr(e),channel_error=e.as_dict()if hasattr(e,'as_dict')else None,traceback=__import__('traceback').format_exc(),launched=launched))
  if not launched:
   for fd in reversed(locks):os.close(fd)
   raise
  if channel is not None:channel.stop('NATIVE_CLOSURE_ATTENTION')
  while True:time.sleep(10)
if __name__=='__main__':main()
