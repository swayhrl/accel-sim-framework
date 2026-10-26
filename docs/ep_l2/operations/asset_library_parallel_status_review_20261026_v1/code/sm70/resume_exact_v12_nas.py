"""Finite COPY_ONLY archive continuation V3. Import is CPU-test-safe; production starts only main()."""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,signal,traceback
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
EXPECTED_ENGINE='53ca6aedea4f11f2e45fcf9bdd8f33ec5ecd5437af0e5e3ca286458c7cd01b1e'
EXPECTED_DRIVER='5f5d98524b7907e733cf50260c967eaf4391f0a15f3940630ae48bd57ffabf20'
ORIGINAL_COMPLETED_V8_BATCH='89eb4fdd795fad40be6c'
ORIGINAL_ENGINE_V8='c5fac7e8137adb389e9843d26d52c1035727e75a71f780d9603dac6517358a74'
STOP_REQUESTED=False
GATE_CODE=r'''import os,sys
fd=int(sys.argv[1]);parent=int(sys.argv[2]);program=sys.argv[3:]
if os.getppid()!=parent:raise SystemExit(125)
token=os.read(fd,1);os.close(fd)
if token!=b'G' or os.getppid()!=parent:raise SystemExit(126)
os.execv(program[0],program)
'''
def need(x,msg):
 if not x:raise RuntimeError(msg)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def proc_identity(pid):
 try:
  row=Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
  return dict(pid=int(pid),state=row[0],ppid=int(row[1]),pgid=int(row[2]),sid=int(row[3]),start_ticks=int(row[19]))
 except (FileNotFoundError,ProcessLookupError):return None
def deferred_stop(signum,frame):
 global STOP_REQUESTED
 STOP_REQUESTED=True
def owned_members(owner):
 rows=[]
 for p in Path('/proc').iterdir():
  if not p.name.isdigit():continue
  q=proc_identity(int(p.name))
  if q and q['pgid']==owner['pgid'] and q['sid']==owner['sid'] and q['start_ticks']>=owner['start_ticks'] and q['pid']!=os.getpid():rows.append(q)
 return rows
def signal_exact(row,sig):
 now=proc_identity(row['pid'])
 if not now or any(now[k]!=row[k]for k in ['pid','start_ticks','pgid','sid'])or now['state']=='Z':return False
 try:os.kill(row['pid'],sig);return True
 except ProcessLookupError:return False
def cleanup_owned(handle,term_seconds=5.0,kill_seconds=5.0):
 """Inspect the private session even after leader exit; never signal a reused PID or other SID/PGID."""
 if handle.get('cleanup_closed'):return handle['cleanup_receipt']
 owner=handle['identity'];child=handle['child'];seen={};sent=[]
 initial=owned_members(owner)
 def active():
  # Keep the exited leader unreaped until all session work is accounted, reserving its PID/SID against reuse.
  found=owned_members(owner)
  for q in found:seen[(q['pid'],q['start_ticks'])]=q
  return [q for q in found if q['state']!='Z']
 for sig,seconds in [(signal.SIGTERM,term_seconds),(signal.SIGKILL,kill_seconds)]:
  until=time.monotonic()+seconds
  while True:
   rows=active()
   if not rows:break
   for q in rows:
    if signal_exact(q,sig):sent.append(dict(pid=q['pid'],start_ticks=q['start_ticks'],signal=int(sig)))
   if time.monotonic()>=until:break
   time.sleep(min(.1,max(0,until-time.monotonic())))
  if not active():break
 unresolved=active()
 try:child.wait(timeout=.25)
 except subprocess.TimeoutExpired:pass
 receipt=dict(owner=owner,initial_members=initial,observed_members=list(seen.values()),signals=sent,unresolved=unresolved,zombies_not_claimed_reaped=[q for q in owned_members(owner)if q['state']=='Z'])
 if not unresolved:handle['cleanup_closed']=True;handle['cleanup_receipt']=receipt
 return receipt
def launch_gated(command,stdout,register,stop=lambda:STOP_REQUESTED,after_spawn=None,handles=None):
 """No exec until exact session identity is durably registered. Deferred handlers never interrupt Popen→register."""
 need(not stop(),'STOP_REQUESTED_BEFORE_SPAWN')
 readfd,writefd=os.pipe();child=None;handle=None
 try:
  child=subprocess.Popen([sys.executable,'-B','-c',GATE_CODE,str(readfd),str(os.getpid()),*command],pass_fds=(readfd,),stdin=subprocess.DEVNULL,stdout=stdout,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
  os.close(readfd);readfd=None
  q=proc_identity(child.pid)
  need(q is not None and q['pgid']==q['sid']==q['pid'] and q['ppid']==os.getpid(),'new private gated session identity')
  handle=dict(child=child,identity=q,command=command)
  if handles is not None:handles.append(handle)
  if after_spawn:after_spawn(handle)
  register(dict(driver_pid=q['pid'],driver_start_ticks=q['start_ticks'],driver_pgid=q['pgid'],driver_sid=q['sid'],driver_argv=command,driver_exec_released=False))
  if stop():
   os.close(writefd);writefd=None
   cleanup=cleanup_owned(handle);need(not cleanup['unresolved'],'unresolved stopped gate')
   raise RuntimeError('STOP_REQUESTED_BEFORE_EXEC_RELEASE')
  need(os.write(writefd,b'G')==1,'short gate release');os.close(writefd);writefd=None
  handle['exec_released']=True
  return handle
 except BaseException:
  if writefd is not None:os.close(writefd);writefd=None
  if handle is not None:cleanup_owned(handle)
  elif child is not None:
   # No executable driver can start without G. Close pipe first, then reap our direct child only.
   try:child.wait(timeout=3)
   except subprocess.TimeoutExpired:
    q=proc_identity(child.pid)
    if q and q['ppid']==os.getpid():signal_exact(q,signal.SIGKILL)
    child.wait(timeout=3)
  raise
 finally:
  if readfd is not None:os.close(readfd)
  if writefd is not None:os.close(writefd)
def wait_owned(handle,deadline,stop=lambda:STOP_REQUESTED,poll_seconds=.25):
 child=handle['child']
 while True:
  if stop():raise RuntimeError('STOP_REQUESTED_OWNED_DRIVER')
  need(time.monotonic()<deadline,'finite archive continuation deadline')
  event=os.waitid(os.P_PID,child.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
  if event is not None:
   return event.si_status if event.si_code==os.CLD_EXITED else -event.si_status
  time.sleep(min(poll_seconds,max(0,deadline-time.monotonic())))
def wait_retry(deadline,stop=lambda:STOP_REQUESTED,seconds=60):
 until=min(deadline,time.monotonic()+seconds)
 while time.monotonic()<until:
  need(not stop(),'STOP_REQUESTED_RESOURCE_WAIT');time.sleep(min(.25,max(0,until-time.monotonic())))
def new_failure_tail(path,offset):
 p=Path(path);size=p.stat().st_size;need(size>=offset,'own transfer log truncated')
 with p.open('rb')as f:f.seek(max(offset,size-32768));return f.read().decode(errors='replace')
def resource_failure(tail):return 'RESOURCE_HOLD_'in tail or 'BlockingIOError: [Errno 11]'in tail

def pending_tree_partial_holds(bundle,manifest):
 """No partial mutation: Root must quarantine incomplete derived trees outside tree."""
 tree=Path(bundle)/'tree'
 if not tree.exists():return []
 expected={r['relative_path']:r['size'] for r in manifest['members']};holds=[]
 for p in tree.rglob('*.writing'):
  rel=p.relative_to(tree).as_posix();member=rel[:-len('.writing')]
  if p.is_symlink() or not p.is_file():holds.append({'path':str(p),'reason':'NONREGULAR_OR_SYMLINK'});continue
  actual=p.stat().st_size;size=expected.get(member)
  if size is None or actual!=size:holds.append({'path':str(p),'bytes':actual,'expected_bytes':size,'reason':'ROOT_QUARANTINE_OUTSIDE_TREE_REQUIRED'})
 return holds

def main():
 global STOP_REQUESTED
 import resource
 signal.signal(signal.SIGTERM,deferred_stop);signal.signal(signal.SIGINT,deferred_stop)
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 os.environ['PYTHONDONTWRITEBYTECODE']='1'
 code=Path(__file__).resolve().parent
 need(sha(code/'library_copy_v12_nas.py')==EXPECTED_ENGINE,'engine changed')
 need(sha(code/'transfer_exact_v12_nas.py')==EXPECTED_DRIVER,'driver changed')
 sys.path.insert(0,str(code));import library_copy_v12_nas as e
 approval=e.root_approval();e.qualified_archive_request({'manifest':e.read(e.EXACT_MANIFEST),'skip':{}})
 runtime=Path(approval['runtime_root']);need(runtime.is_relative_to(e.NAS/'receipts') and '..'not in runtime.parts,'runtime outside dedicated NAS receipts')
 fs=json.loads(subprocess.check_output(['findmnt','-J','-T',str(e.NAS)],text=True))['filesystems'][0]
 need(fs['fstype']=='fuse.sshfs' and fs['source']=='admin-wcx@10.208.130.164:/home/shared','runtime not genuine164')
 lease=(R/'control/SUPERVISOR.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
 run=runtime/('run_'+str(time.time_ns()));run.mkdir(parents=True,exist_ok=False);(run/'tmp').mkdir()
 os.environ['TMPDIR']=str(run/'tmp')
 deadline=time.monotonic()+72*3600;handles=[];os.nice(19);e.enable_nas_only();guard=e.Resources()
 def status(stage,**kw):
  own=proc_identity(os.getpid());obj={'stage':stage,'unix':time.time(),'pid':os.getpid(),'start_ticks':own['start_ticks'],'engine_sha256':EXPECTED_ENGINE,'driver_sha256':EXPECTED_DRIVER,'run':str(run),'science_or_GPU_started':False,'publication_invoked':False,**kw}
  tmp=run/'STATE.writing';tmp.write_text(json.dumps(obj)+'\n');os.replace(tmp,run/'STATE.json')
  with (run/'events.jsonl').open('a')as f:f.write(json.dumps(obj)+'\n')
 def preflight():
  need(not STOP_REQUESTED,'STOP_REQUESTED');need(sha(code/'library_copy_v12_nas.py')==EXPECTED_ENGINE and sha(code/'transfer_exact_v12_nas.py')==EXPECTED_DRIVER,'frozen source changed')
  e.root_approval();m=e.read(e.EXACT_MANIFEST);e.qualified_archive_request({'manifest':m,'skip':{}})
  health=guard(True);bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1));holds=pending_tree_partial_holds(bundle,m)
  need(not holds,'RESOURCE_HOLD_ROOT_TREE_PARTIAL_QUARANTINE_REQUIRED: '+json.dumps(holds))
  return health
 status('APPROVED_NAS_ONLY_WAIT')
 try:
  while time.monotonic()<deadline:
   need(not STOP_REQUESTED,'STOP_REQUESTED')
   try:health=preflight()
   except RuntimeError as exc:
    if not str(exc).startswith('RESOURCE_HOLD_'):raise
    status('WAIT_RESOURCE_OR_ROOT_PARTIAL',reason=str(exc));wait_retry(deadline);continue
   logpath=run/'driver.log';offset=logpath.stat().st_size if logpath.exists()else 0
   with logpath.open('ab')as log:
    handle=launch_gated(['/usr/bin/python3','-B',str(code/'transfer_exact_v12_nas.py'),str(run)],log,lambda d:status('REGISTERED_GATED',**d),handles=handles)
    status('RUNNING_COPY_ONLY',resources=health,driver_identity=handle['identity'])
    rc=wait_owned(handle,deadline)
   cleanup=cleanup_owned(handle);status('OWN_SESSION_CLOSED',driver_rc=rc,cleanup=cleanup);need(not cleanup['unresolved'],'owned cleanup unresolved')
   if rc==0:
    proof=json.loads((run/'EXACT_BATCH_COMPLETE.json').read_text());need(proof['status']=='PASS_COMMITTED_BATCH' and proof['manifest_sha256']==e.EXACT_MANIFEST_SHA,'exact completion receipt mismatch')
    preflight();status('COPY_ONLY_COMMITTED_PUBLICATION_REVIEW_REQUIRED',receipt=proof);return
   tail=new_failure_tail(logpath,offset)
   if resource_failure(tail):status('WAIT_RESOURCE_OR_ROOT_PARTIAL',reason='OWN_NEW_RESOURCE_HOLD');wait_retry(deadline);continue
   raise RuntimeError('exact driver held; inspect '+str(logpath))
  raise RuntimeError('finite72h deadline')
 except BaseException as exc:status('ATTENTION_RETAINED_NO_PUBLICATION',error=repr(exc),traceback=traceback.format_exc());raise
 finally:
  for handle in handles:
   cleanup=cleanup_owned(handle)
   if cleanup['unresolved']:status('ATTENTION_OWNED_CLEANUP_UNRESOLVED',cleanup=cleanup)
if __name__=='__main__':main()
