"""Native zero-payload control for the exact engineering pilot2 COPY phase."""
from pathlib import Path
import os,sys,json,stat,hashlib,subprocess,shlex,resource,time,fcntl,signal,types,shutil
D=Path(__file__).resolve().parent
def hold_unknown_forever(out,diagnostic,writer=None):
 # Preloaded before acquiring asset holds. Signal masking comes before any fallible NAS diagnostic.
 for sig in [signal.SIGTERM,signal.SIGHUP,signal.SIGINT]:signal.signal(sig,signal.SIG_IGN)
 try:
  if writer is None:COPY_DIAGNOSTIC_WRITER(out/'HOLD_UNKNOWN_REMOTE.json',diagnostic)
  else:writer(out/'HOLD_UNKNOWN_REMOTE.json',diagnostic)
 except BaseException:pass
 while True:time.sleep(1)
COPY_DIAGNOSTIC_WRITER=None
def main():
 assert len(sys.argv)==3
 sp=Path(sys.argv[1]);st=sp.stat();assert sp.parent==Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')and st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o600
 raw=sp.read_bytes();assert hashlib.sha256(raw).hexdigest()==sys.argv[2];a=json.loads(raw)
 assert hashlib.sha256((D/'CODE_MANIFEST.json').read_bytes()).hexdigest()==a['code_manifest_sha256']
 mf=json.loads((D/'CODE_MANIFEST.json').read_bytes())
 for n,r in mf['files'].items():
  b=(D/n).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['sha256']
 sys.path.insert(0,str(D));import pilot2_common_v1 as C
 C.scope(sp,sys.argv[2],'ROOT_APPROVED_PILOT2_COPY_PHASE_V1')
 global COPY_DIAGNOSTIC_WRITER
 COPY_DIAGNOSTIC_WRITER=C.put
 assert a['CPU_ids']==[2]
 assert a['phase']in['ORDINARY','DERIVED']and a['native_boot_id']==Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 os.nice(15);resource.setrlimit(resource.RLIMIT_AS,(128*2**20,128*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 helper=Path(a['Native_kernel_helper_ref']['path']);b=helper.read_bytes();assert hashlib.sha256(b).hexdigest()=='06b8abe6c591d86043182b8b398be49104dc6cf9e4e448e98b2c3ef47795fae6'
 K=types.ModuleType('native_kernel');K.__file__=str(helper);exec(compile(b,str(helper),'exec'),K.__dict__)
 assert a['Native_broker_policy']==K.POLICY
 def gate():return K.evaluate(K.collect(),K.POLICY)
 assert gate()['status']=='PASS';assert shutil.disk_usage('/root/data').free>=5*2**30+64*2**20
 locks=[];proc=None;channel=None;remote_closed=False;out=D/('native_'+a['run_id']);out.mkdir();rp=D/('ROOT_'+a['run_id']+'_SCOPE.raw.json');rp.write_bytes(raw)
 try:
  expected=[str(Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/asset_operations')/q/(n+'.lock'))for q in C.IDS for n in ['CAPTURE','INPUT','OUTPUT','RUNTIME']]
  assert [x['path']for x in a['Native_asset4_expected']]==expected
  for r in a['Native_asset4_expected']:
   fd=os.open(r['path'],os.O_RDWR|os.O_NOFOLLOW|os.O_CLOEXEC);s=os.fstat(fd);assert(s.st_dev,s.st_ino)==(r['dev'],r['inode'])and s.st_uid==0 and stat.S_IMODE(s.st_mode)==0o600 and s.st_size==0
   locks.append(fd)
   while True:
    assert time.time()<a['absolute_deadline_unix']
    try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);break
    except BlockingIOError:time.sleep(.1)
  Wire=C.module('ssh_stdin_light_control_v2.py')
  root=str(C.alias(D)).replace(str(C.NB),str(C.ST))
  scope_remote=str(rp).replace(str(C.NB),str(C.ST))
  unit='ep-pilot2-copy-'+a['run_id']
  cmd=['systemd-run','--user','--quiet','--wait','--collect','--pipe','--unit='+unit,'--property=MemoryMax='+str(2*2**30),'--property=MemorySwapMax=0','--property=TasksMax=16','--property=OOMPolicy=kill','--property=KillMode=control-group','--property=AllowedCPUs=2','--property=CPUQuota=100%','--','/usr/bin/python3','-I','-S','-B',root+'/copy_two_exact_pilots_remote_v1.py',scope_remote,sys.argv[2]]
  with(out/'remote.stdout.log').open('xb')as so,(out/'remote.stderr.log').open('xb')as se:
   proc=subprocess.Popen(['ssh','-T','-o','BatchMode=yes','gpu109',shlex.join(cmd)],stdin=subprocess.PIPE,stdout=so,stderr=se,bufsize=0)
   channel=Wire.NativeChannel(proc.stdin.fileno(),sys.argv[2],a['run_id'],gate,a['absolute_deadline_unix']);channel.start()
   C.put(out/'NATIVE_START.json',dict(pid=os.getpid(),ticks=Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19],ssh_pid=proc.pid,scope_sha256=sys.argv[2]))
   def stop(sig,frame):channel.stop('OWN_NATIVE_SIGNAL_'+str(sig))
   for sig in [signal.SIGTERM,signal.SIGINT,signal.SIGHUP]:signal.signal(sig,stop)
   rc=proc.wait()
  # Actual owner/cgroup closure is checked after systemd --wait returned, not assumed from file status.
  run=root+'/runs/'+a['run_id']
  code="from pathlib import Path;import json;P=Path("+repr(run)+");z=json.loads((P/'RESOURCE_AND_CLOSURE.json').read_bytes());pid,t=z['owner'];p=Path('/proc',str(pid),'stat');assert not p.exists()or p.read_text().rsplit(')',1)[1].split()[19]!=t;cg=Path(z['cgroup']);assert not cg.exists()or not(cg/'cgroup.procs').read_text().split();assert z['tracked_children']==[]and z['reader_joined'];print(json.dumps(dict(owned_closed=True,scope_sha256=z['scope_sha256'],error=z['error'])))"
  check=subprocess.run(['ssh','-o','BatchMode=yes','gpu109','python3 -I -S -B -c '+shlex.quote(code)],capture_output=True,text=True,timeout=30);assert check.returncode==0,check.stderr
  w=json.loads(check.stdout);assert w['scope_sha256']==sys.argv[2]and w['owned_closed'];remote_closed=True;C.put(out/'INDEPENDENT109_CLOSURE.json',w)
  C.put(out/'TRUE_WAIT.json',dict(returncode=rc,owned_closed=True));assert rc==0
 finally:
  if proc is not None and not remote_closed:
   # Unknown remote closure retains Native asset holds; no foreign signal, timeout restart or blind unlock.
   hold_unknown_forever(out,dict(ssh_pid=proc.pid))
  if channel is not None:channel.finish_after_owned_closed()
  for fd in reversed(locks):os.close(fd)
  C.put(out/'NATIVE_ASSET8_RELEASED.json',dict(scope_sha256=sys.argv[2],remote_independently_closed=remote_closed,remote_never_launched=proc is None,SourceKEEP=True,release_bytes=0))
if __name__=='__main__':main()
