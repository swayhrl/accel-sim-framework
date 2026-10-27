"""Exact33 finite capture-only Native dispatcher. No historical queue or SC-success dependency."""
import pathlib,sys,hashlib
_p=pathlib.Path(__file__).with_name('ordinary33_common_v1.py');_b=_p.read_bytes()
if hashlib.sha256(_b).hexdigest()!='673152596e7afb688925679b68ad7247c59231064c7ea2e207e8fe6d6a52ef55':raise RuntimeError('COMMON_PIN')
C=type(sys)('o33common');C.__file__=str(_p);exec(compile(_b,str(_p),'exec'),C.__dict__)
import os,json,time,argparse,resource,subprocess,threading,signal,shlex,socket
D=pathlib.Path(__file__).resolve().parent
def await_SC_boundary(a,limits,stopped,probe,pause=time.sleep,now=time.time):
 if not limits['require_SC_POST_inactive']:return True
 while True:
  if stopped()or now()>=C.DEADLINE:return False
  z=probe();C.need(z['status']in ['SC_ACTIVE_WAIT','SC_CLOSED'],'SC_WAIT_PROBE_SCHEMA')
  if stopped()or now()>=C.DEADLINE:return False
  if z['status']=='SC_CLOSED':return True
  pause(min(2,max(0,C.DEADLINE-now())))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scope',required=True);ap.add_argument('--scope-sha',required=True);ap.add_argument('--code-sha',required=True);x=ap.parse_args()
 C.need(D==C.NB,'ROOT_STAGED_CODE');mf=C.code_check(D,x.code_sha);p=pathlib.Path(x.scope)
 C.need(p.parent==pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control')and p.stat().st_uid==0 and p.stat().st_mode&0o022==0,'ROOT_NATIVE_APPROVAL')
 raw=p.read_bytes();a=C.readref(dict(path=str(p),bytes=len(raw),sha256=x.scope_sha));AL=json.loads((D/'ALLOWLIST33.json').read_bytes());C.validate_scope(a,AL)
 C.need(a['code_manifest_sha256']==x.code_sha and a['Native_host']==socket.gethostname()and a['Native_boot_id']==pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'SCOPE_CODE_HOST_BOOT')
 os.umask(0o077);os.nice(15);os.sched_setaffinity(0,set(a['Native_cpu_ids']));resource.setrlimit(resource.RLIMIT_AS,(512*2**20,512*2**20));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 Lease,O=C.dependencies(D,mf);O.set_subreaper();me=O.ident(os.getpid());Gate=C.rawmodule(D/'native_control_resource_v1.py',mf['files']['native_control_resource_v1.py']['sha256'],'ordinaryNativeGate')
 campaign=C.NB/'runs'/a['campaign_id'];campaign.mkdir(parents=True,exist_ok=False);C.save(campaign/'NATIVE_CAMPAIGN_START.json',dict(owner=me,scope_sha256=x.scope_sha,SC_success_prerequisite=False,old_STOP_or_queue_modified=False))
 stop=threading.Event()
 for s in [signal.SIGTERM,signal.SIGHUP,signal.SIGINT]:signal.signal(s,lambda sig,f:stop.set())
 outcomes={};sshbase=['ssh','-T','-o','BatchMode=yes','-o','ConnectTimeout=8','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no','-o','ControlMaster=no','-o','ControlPath=none','-o','ControlPersist=no','gpu109']
 for index,jid in enumerate(a['ordered_job_ids']):
  if stop.is_set()or(campaign/'STOP_AFTER_CURRENT_JOB').exists()or time.time()>=C.DEADLINE:break
  root=campaign/jid;root.mkdir();sf=root/'ROOT_SCOPE.raw.json'
  with sf.open('xb')as f:f.write(raw);f.flush();os.fsync(f.fileno())
  Gate.native_gate(a,root)
  job,limits=C.job_parameters(a,AL,jid)
  probes=[0]
  def peer_probe():
   argv=['/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',x.scope_sha,'--code-sha',x.code_sha,'--peer-preflight']
   cp=subprocess.run(sshbase+[shlex.join(argv)],capture_output=True,timeout=30,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
   C.need(cp.returncode==0,'SC_PEER_PREFLIGHT_UNKNOWN_HOLD');z=json.loads(cp.stdout);C.need(z['scope_sha256']==x.scope_sha and z['job_id']==jid,'SC_WAIT_EXACT_SCOPE_JOB')
   probes[0]+=1
   if probes[0]==1 or z['status']=='SC_CLOSED':C.save(root/('SC_WAIT_'+str(probes[0])+'.json'),dict(z,probe_count=probes[0]))
   return z
  if not await_SC_boundary(a,limits,lambda:stop.is_set()or(campaign/'STOP_AFTER_CURRENT_JOB').exists(),peer_probe):break
  Gate.native_gate(a,root) # Fresh again after potentially long SC wait; no renewed deadline.
  control=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control/asset_operations')/jid
  paths=[control/n for n in ['CAPTURE.lock','INPUT.lock','OUTPUT.lock','RUNTIME.lock']]
  # Hold human time/SC blocker admission on Native, before starting a 109 service.
  while True:
   if stop.is_set()or(campaign/'STOP_AFTER_CURRENT_JOB').exists()or time.time()>=C.DEADLINE:break
   if time.time()<a['Root_GPU_not_before_unix']:time.sleep(.25);continue
   args=['/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',x.scope_sha,'--code-sha',x.code_sha,'--blocker-preflight']
   cp=subprocess.run(sshbase+[shlex.join(args)],capture_output=True,timeout=30,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
   C.need(cp.returncode==0,'SC_CPU_ONLY_BLOCKER_UNKNOWN_HOLD');w=json.loads(cp.stdout);C.need(w['scope_sha256']==x.scope_sha and w['job_id']==jid,'BLOCKER_EXACT_SCOPE_JOB')
   if not w['blocked']:break
   time.sleep(2)
  if stop.is_set()or(campaign/'STOP_AFTER_CURRENT_JOB').exists()or time.time()>=C.DEADLINE:break
  h=None # Canonical109 Comfy lock must be held before any Native asset4 acquisition.
  C.need(not stop.is_set()and time.time()<C.DEADLINE,'FRESH_DEADLINE_AFTER_WAIT_AND_NATIVE_IO')
  unit='ordinary33-'+a['campaign_id']+'-'+str(index)
  args=['systemd-run','--user','--quiet','--wait','--pipe','--unit='+unit,'--property=MemoryMax='+str(limits['memory_max_bytes']),'--property=MemorySwapMax=0','--property=LimitAS=infinity','--property=OOMPolicy=kill','--property=CPUQuota=200%','--property=AllowedCPUs='+','.join(map(str,a['remote_cpu_ids'])),'--property=KillMode=control-group','--property=TimeoutStopSec=30','--','/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',x.scope_sha,'--code-sha',x.code_sha]
  proc=None;launched=False;released=False;finished=threading.Event();seq=[0];transport=threading.Lock()
  def frame(kind):
   with transport:
    seq[0]+=1;proc.stdin.write((json.dumps(dict(kind=kind,scope_sha256=x.scope_sha,job_id=jid,seq=seq[0]))+'\n').encode());proc.stdin.flush()
  def heartbeat():
   while not finished.is_set():
    try:frame('STOP'if stop.is_set()or time.time()>=C.DEADLINE else'BEAT')
    except(BrokenPipeError,OSError,ValueError):pass
    time.sleep(.2)
  try:
   with(root/'remote.stdout.log').open('xb')as out,(root/'remote.stderr.log').open('xb')as err:
    launched=True;proc=subprocess.Popen(sshbase+[shlex.join(args)],stdin=subprocess.PIPE,stdout=out,stderr=err,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
   thread=threading.Thread(target=heartbeat,daemon=True);thread.start();last_resource=time.monotonic()
   while not(root/'REMOTE_CLOSED_PROPOSAL.json').exists():
    C.need(proc.poll()is None,'SSH_EXIT_WITHOUT_CLOSURE')
    if h is None and not stop.is_set()and(root/'SHARED_COMFY_LOCK_HELD.json').exists():
     observe=['/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',x.scope_sha,'--code-sha',x.code_sha,'--observe-shared']
     cp=subprocess.run(sshbase+[shlex.join(observe)],capture_output=True,timeout=30,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'));C.need(cp.returncode==0,'SHARED_CANONICAL_ACTUAL_OBSERVER')
     w=json.loads(cp.stdout);C.need(w['scope_sha256']==x.scope_sha and w['job_id']==jid and w['canonical_fd_actual_verified']is True and w['shared_receipt_sha256']==C.sha(root/'SHARED_COMFY_LOCK_HELD.json'),'SHARED_CANONICAL_OBSERVER_BIND')
     try:h=Lease.GuardLeases(paths,dict(scope_sha256=x.scope_sha,campaign_id=a['campaign_id'],job_id=jid))
     except BlockingIOError:stop.set()
     if h is not None:
      C.save(root/'NATIVE_KEEPER.json',dict(owner=me,leases=h.descriptor,scope_sha256=x.scope_sha))
      C.save(root/'NATIVE_ASSET4_READY.json',dict(scope_sha256=x.scope_sha,job_id=jid,shared_receipt_sha256=w['shared_receipt_sha256'],owner=me))
    if time.monotonic()-last_resource>=30:
     try:Gate.native_gate(a,root)
     except BaseException:stop.set()
     last_resource=time.monotonic()
    time.sleep(.2)
   observe=['/usr/bin/python3','-I','-S','-B',str(C.RB/'remote_capture_once_v1.py'),'--campaign',a['campaign_id'],'--job-id',jid,'--scope-sha',x.scope_sha,'--code-sha',x.code_sha,'--observe']
   cp=subprocess.run(sshbase+[shlex.join(observe)],capture_output=True,timeout=30,env=dict(PATH='/usr/bin:/bin',HOME='/root',LC_ALL='C'))
   C.need(cp.returncode==0,'INDEPENDENT_REMOTE_CLOSURE');w=json.loads(cp.stdout);C.need(w['scope_sha256']==x.scope_sha and w['job_id']==jid and w['owned_closed']is True and w['proposal_sha256']==C.sha(root/'REMOTE_CLOSED_PROPOSAL.json'),'EXACT_CLOSURE')
   C.save(root/'REMOTE_CLOSURE_OBSERVATION.json',w);C.save(root/'NATIVE_CLEANUP_ACK.json',dict(scope_sha256=x.scope_sha,proposal_sha256=w['proposal_sha256'],owner=me))
   end=time.monotonic()+30
   while not(root/'REMOTE_ACK_CONSUMED.json').exists():C.need(time.monotonic()<end,'ACK_NOT_CONSUMED');time.sleep(.1)
   ack=json.loads((root/'REMOTE_ACK_CONSUMED.json').read_bytes());C.need(ack['scope_sha256']==x.scope_sha and ack['ACK_sha256']==C.sha(root/'NATIVE_CLEANUP_ACK.json'),'ACK_RAW_BINDING')
   finished.set();thread.join(timeout=2);C.need(not thread.is_alive(),'HEARTBEAT_THREAD_NOT_CLOSED');proc.stdin.close();proc.wait(timeout=30);O.reap();C.need(not O.children(me),'LOCAL_OWNED_CLOSED');
   if h is not None:h.close_after_closed(lambda:O.children(me))
   released=True
   z=json.loads((root/'REMOTE_CLOSED_PROPOSAL.json').read_bytes());outcomes[jid]=dict(status=z['status'],proposal_ref=C.ref(root/'REMOTE_CLOSED_PROPOSAL.json'),worker_service_returncode=proc.returncode)
   C.save(root/'NATIVE_RELEASED.json',dict(status='ASSET_FOUR_LOCKS_CLOSED_AFTER_REMOTE_GPU_IO_CLOSURE'if h is not None else'NO_NATIVE_ASSET_LOCKS_ACQUIRED_ADMISSION_DEFERRED',scope_sha256=x.scope_sha,job_id=jid,owner=me))
   if a['stop_after_first_closed_job']:
    stopfile=campaign/'STOP_AFTER_CURRENT_JOB'
    if not stopfile.exists():
     try:C.save(stopfile,dict(reason='ROOT_INITIAL_PILOT_FIRST_JOB_CLOSED',scope_sha256=x.scope_sha,job_id=jid,status=z['status']))
     except FileExistsError:pass
    stop.set()
   if z['status']not in ['CAPTURED_POST_PENDING','PENDING_SPECIALIST_EXTENSION']:break
   end_yield=time.monotonic()+a['inter_job_yield_seconds']
   while time.monotonic()<end_yield and not stop.is_set()and time.time()<C.DEADLINE:time.sleep(.1)
  except BaseException as e:
   stop.set()
   if launched and not released:
    if proc is not None and proc.stdin and not proc.stdin.closed:proc.stdin.close()
    O.hold(root/'NATIVE_HOLD_UNKNOWN.json',e,[]if h is None else h.fds)
   else:
    
    if h is not None:h.close_after_closed(lambda:O.children(me))
    raise
 C.save(campaign/'CAMPAIGN_CAPTURE_PHASE_TERMINAL.json',dict(status='FINITE_CAPTURE_PHASE_DEFERRED_SOURCE_KEEP'if any(v['status']=='CAPTURE_ADMISSION_DEFERRED_BEFORE_GPU'for v in outcomes.values())else'FINITE_CAPTURE_PHASE_CLOSED_POST_PENDING',scope_sha256=x.scope_sha,outcomes=outcomes,unvisited=[j for j in a['ordered_job_ids']if j not in outcomes],full_record_POST_archive_or_science_granted=False,source_KEEP=True,old_STOP_or_queue_modified=False))
if __name__=='__main__':main()
