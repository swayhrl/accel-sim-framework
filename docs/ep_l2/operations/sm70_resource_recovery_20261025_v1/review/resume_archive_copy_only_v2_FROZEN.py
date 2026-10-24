"""Finite COPY_ONLY archive continuation V2. Import is CPU-test-safe; production starts only main()."""
from pathlib import Path
import os,sys,time,json,hashlib,fcntl,subprocess,signal,traceback
R=Path('/root/data/shared_sm70_trace_library_20261024_v1')
EXPECTED_ENGINE='c5fac7e8137adb389e9843d26d52c1035727e75a71f780d9603dac6517358a74'
EXPECTED_DRIVER='a843e650d63af5d87dc3ec9de62aed8131cd5fd4c6616dcd9582d54ec762e190'
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

def main():
 """Root alone may invoke this production entry. No deployment/publication/scientific calls."""
 global STOP_REQUESTED
 signal.signal(signal.SIGTERM,deferred_stop);signal.signal(signal.SIGINT,deferred_stop)
 need(sha(R/'tools/library_copy_v8.py')==EXPECTED_ENGINE,'frozen engine changed before import')
 sys.path.insert(0,str(R/'tools'));import library_copy_v8 as engine
 need(hashlib.sha256(engine.SELF_BYTES).hexdigest()==EXPECTED_ENGINE,'imported engine SHA changed')
 lease=(R/'control/SUPERVISOR.lock').open('a');fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
 manifest_list=R/'control/ARCHIVE_BATCHES.json';list_sha=sha(manifest_list);deadline=time.monotonic()+72*3600;guard=engine.Resources();handles=[];os.nice(19)
 def status(stage,**kw):
  own=proc_identity(os.getpid());d={'schema':'FINITE_ARCHIVE_COPY_ONLY_RESUME_V2','stage':stage,'utc_unix':time.time(),'pid':os.getpid(),'start_ticks':own['start_ticks'],'science_or_GPU_started':False,'publication_invoked':False,'engine_sha256':EXPECTED_ENGINE,'driver_sha256':EXPECTED_DRIVER,'list_sha256':list_sha,**kw}
  path=R/'control/ARCHIVE_COPY_ONLY_RESUME_STATE_V2.json';tmp=path.with_suffix('.writing')
  with tmp.open('w')as f:f.write(json.dumps(d)+'\n');f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
  with (R/'logs/archive_copy_only_resume_v2.jsonl').open('a')as f:f.write(json.dumps(d)+'\n');f.flush();os.fsync(f.fileno())
  print(json.dumps(d),flush=True)
 def preflight():
  need(not STOP_REQUESTED,'STOP_REQUESTED_BEFORE_PREFLIGHT')
  need(sha(manifest_list)==list_sha,'batch list changed');need(sha(R/'tools/library_copy_v8.py')==EXPECTED_ENGINE,'frozen engine changed');need(sha(R/'tools/transfer_batches.py')==EXPECTED_DRIVER,'driver changed')
  promotion=json.loads((R/'control/ENGINE_V8_PROMOTION.json').read_bytes());need(promotion['status']=='PASS_PROMOTED_AT_CLOSED_BATCH_BOUNDARY'and promotion['engine_sha256']==EXPECTED_ENGINE,'engine promotion changed')
  health=guard(True);need(health['SSD_free_bytes']>=health['required_SSD_bytes']+128*1024**2,'RESOURCE_HOLD_RESUME_128M_HYSTERESIS')
  batches=json.loads(manifest_list.read_bytes())
  for batch in batches:
   need(not STOP_REQUESTED,'STOP_REQUESTED_SCOPE_PREFLIGHT');mf=Path(batch['manifest']);need(sha(mf)==batch['sha256'],'manifest SHA changed');m=json.loads(mf.read_bytes())
   if (R/'control'/('BATCH_'+batch['id']+'.json')).exists():
    validate_one_batch(batch,m);continue
   need(m['source_backend']=='archive'and m['source_host']=='174-new','unexpected pending source')
   need(engine.same_source(engine.identity(m['archive_path']),m['archive_identity']),'frozen archive exact identity changed')
  return health,batches
 def validate_one_batch(b,m=None):
  need(not STOP_REQUESTED,'STOP_REQUESTED_BATCH_COMPLETION')
  receipt=json.loads((R/'control'/('BATCH_'+b['id']+'.json')).read_bytes());need(receipt['status']=='PASS_COMMITTED_BATCH'and receipt['batch']==b,'exact batch receipt mismatch');need(receipt['selected_engine_sha256']==EXPECTED_ENGINE,'batch selected engine mismatch')
  m=json.loads(Path(b['manifest']).read_bytes())if m is None else m
  bundle=Path(m['new_true164_bundle'].replace('/home/shared','/root/share/mnt164',1))
  stored=json.loads((bundle/'SOURCE_MANIFEST.json').read_bytes());commit=json.loads((bundle/'COMMIT.json').read_bytes());closed=json.loads((bundle/'RECEIPT.json').read_bytes());need(stored==m,'committed manifest differs from frozen input');mh=engine.digest(engine.canon(m));need(commit['manifest_sha256']==closed['manifest_sha256']==mh and commit['object_id']==closed['object_id']==m['object_id'],'completed COMMIT/receipt identity')
  need(closed['Source_full_SHA_matches']is True and closed['true164_closed_reopen_whole_SHA_matches']is True,'completed closed SHA scope')
  need(sha(bundle/'TREE_VERIFICATION.json')==commit['tree_verification_sha256']and sha(bundle/'RANGE_INDEX.json')==commit['range_index_sha256'],'completed metadata chain SHA')
 def validate_complete(batches):
  need(not STOP_REQUESTED,'STOP_REQUESTED_COMPLETION')
  marker=json.loads((R/'control/ARCHIVE_BATCHES_TRANSFER_COMPLETE.json').read_bytes());need(marker['status']=='PASS'and marker['batches']==len(batches),'completion marker invalid')
  for b in batches:validate_one_batch(b)
  return True
 status('WAIT_UNCHANGED_RESOURCE_GUARD')
 try:
  while time.monotonic()<deadline:
   need(not STOP_REQUESTED,'STOP_REQUESTED_BEFORE_ATTEMPT')
   try:health,batches=preflight()
   except RuntimeError as e:
    if not str(e).startswith('RESOURCE_HOLD_'):raise
    status('WAIT_UNCHANGED_RESOURCE_GUARD',reason=str(e));wait_retry(deadline);continue
   path=R/'logs/transfer_ARCHIVE_BATCHES.jsonl';offset=path.stat().st_size if path.exists()else 0
   status('COPY_ONLY_DRIVER_START',resources=health,retained_partial_policy='UNCHANGED_V8_INCOMING_RANGE_PREFIX_FULL_SHA')
   with (R/'logs/archive_copy_only_resume_driver_v2.log').open('ab')as log:
    handle=launch_gated(['/usr/bin/python3','-B',str(R/'tools/transfer_batches.py'),'ARCHIVE_BATCHES.json'],log,lambda d:status('COPY_ONLY_DRIVER_REGISTERED_GATED',**d),handles=handles)
    status('COPY_ONLY_DRIVER_RUNNING',driver_identity=handle['identity'],driver_exec_released=True)
    rc=wait_owned(handle,deadline)
   residual=[q for q in owned_members(handle['identity'])if q['state']!='Z'];cleanup=cleanup_owned(handle);status('OWN_DRIVER_SESSION_CLOSED',driver_rc=rc,cleanup=cleanup);need(not cleanup['unresolved'],'owned driver session cleanup unresolved')
   if rc==0:
    need(not residual,'successful driver left active own descendants');preflight();validate_complete(batches);need(not STOP_REQUESTED,'STOP_REQUESTED_BEFORE_FINAL_PUBLICATION');status('ARCHIVE_COPY_COMPLETE_FUTURE_PUBLICATION_REVIEW_REQUIRED',batch_count=len(batches));return
   tail=new_failure_tail(path,offset)
   if resource_failure(tail):status('WAIT_UNCHANGED_RESOURCE_GUARD',driver_rc=rc,reason='OWN_DRIVER_NEW_LOG_RESOURCE_OR_LEASE_HOLD',failure_log=str(path));wait_retry(deadline);continue
   raise RuntimeError('archive driver non-resource HOLD; inspect '+str(path))
  raise RuntimeError('finite72h continuation deadline')
 except BaseException as e:
  status('ATTENTION_RETAINED_NO_PUBLICATION',error=repr(e),traceback=traceback.format_exc());raise
 finally:
  # No leader-poll shortcut: orphaned sender/decoder processes keep their private SID/PGID.
  failures=[]
  for h in handles:
   cleanup=cleanup_owned(h)
   if cleanup['unresolved']:failures.append(cleanup)
  if failures:status('ATTENTION_OWNED_CLEANUP_UNRESOLVED',cleanup_failures=failures)
if __name__=='__main__':main()
