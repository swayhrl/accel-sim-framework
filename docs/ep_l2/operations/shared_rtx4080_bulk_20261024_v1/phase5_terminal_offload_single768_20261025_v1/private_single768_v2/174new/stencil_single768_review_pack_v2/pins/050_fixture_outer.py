"""Finite Native-only post supervisor with gated startup and operational failure reconciliation."""
import pathlib,json,hashlib,importlib.util,subprocess,time,os,signal,shutil,sys,fcntl
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/dynamic_foreign_growth_own_twoPG/control');N=C.parent;B=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/stencil768_private_qualification_A3/dynamic_foreign_growth_own_twoPG/fake_library');ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';WORK=N/(ID+'_post_epoch4_single768')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o):
 assert not p.exists();tmp=p.with_name(p.name+'.tmp')
 with tmp.open('x')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def replace(p,o):
 tmp=p.with_name(p.name+'.tmp')
 with tmp.open('w')as f:json.dump(o,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def module(p,name,h):
 assert sha(p)==h;s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def reconcile_failure(failure,unresolved):
 commitpath=B/'objects'/ID/'COMMIT.json';commit=None
 if commitpath.exists():
  commit=json.loads(commitpath.read_text());assert commit['asset_id']==ID and commit['status']=='COMMITTED_VERIFIED'
  assert sha(commitpath.parent/'MANIFEST.json')==commit['manifest_sha256']
 note={'status':'CPU_POST_OUTER_FAILURE_RETAINED'if not commit else'COMMIT_PRESENT_NOT_OVERRIDDEN_BY_OUTER_FAILURE','failure':failure,'unresolved_exact_own_processes':unresolved,'commit':commit,'no_GPU_or_SIM_runs':True,'source_KEEP':True,'unix':time.time()}
 note_path=C/(ID+'_POST_EPOCH4_OUTER_FAILURE.json')
 with(C/'RTX4080_QUEUE.lock').open('a')as f:
  fcntl.flock(f,fcntl.LOCK_EX);save(note_path,note);rows=json.loads((C/'QUEUE.json').read_text());row=next(x for x in rows if x['id']==ID)
  if not commit and row.get('status')!='COMMITTED_VERIFIED':row.update(status='FAILED_RETAINED',failure_receipt=str(note_path),CPU_post_epoch=4)
  elif commit:
   row['outer_failure_after_commit_note']=str(note_path)
   receipt=B/'receipts'/(ID+'_RECEIVER_READBACK.json')
   closed=json.loads(receipt.read_text())if receipt.exists()else{}
   if closed.get('manifest_sha256')==commit['manifest_sha256']:row.update(status='COMMITTED_VERIFIED',commit=commit)
   elif row.get('status')!='COMMITTED_VERIFIED':row.update(status='COMMIT_PRESENT_CLOSEOUT_PENDING',commit=commit)
  replace(C/'QUEUE.json',rows)
  statepath=C/(ID+'_POST_EPOCH4_STATE.json')
  if statepath.exists():save(C/(ID+'_POST_EPOCH4_STATE_BEFORE_OUTER_FAILURE.json'),json.loads(statepath.read_text()))
  replace(statepath,{'status':'FAILED_RETAINED_CPU_POST_ONLY'if not commit else'COMMIT_PRESENT_NOT_FAILED_REQUIRES_LOCAL_CLOSEOUT','failure_receipt':str(note_path),'unresolved_exact_own_processes':unresolved,'source_KEEP':True,'unix':time.time()})
 return note
# Bootstrap cannot execute or spawn controller work until its exact PID/start and durable journal exist.
BOOTSTRAP="import os,sys;fd=int(sys.argv[1]);token=os.read(fd,1);os.close(fd);sys.exit(125)if token!=b'G'else None;os.execv(sys.executable,[sys.executable,'-B',sys.argv[2],sys.argv[3]])"
def main():
 grantpath=pathlib.Path(sys.argv[1]);grant=json.loads(grantpath.read_text());assert grant['supervisor_sha256']==sha(pathlib.Path(__file__))
 assert hasattr(os,'pidfd_open')and hasattr(signal,'pidfd_send_signal')
 controller=C/'resume_stencil_single768_epoch4_v2.py';assert sha(controller)==grant['controller_sha256']
 u=module(C/'stencil768_common_v2.py','common768',grant['common_sha256']);post=u.SCAN
 proc=module(C/'validate_app_hot_resume_v4r3.py','proc','85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909')
 initial=u.resources(True,stage_budget=u.LIMIT,admission=True)
 maxval=pathlib.Path('/sys/fs/cgroup/memory.max').read_text().strip();current=int(pathlib.Path('/sys/fs/cgroup/memory.current').read_text());assert maxval=='max'or int(maxval)-current>=4*2**30
 suffixes=['_POST_EPOCH4_SUPERVISOR.json','_POST_EPOCH4_RESOURCE_EVENTS.jsonl','_POST_EPOCH4_SUPERVISOR_TERMINAL.json','_POST_EPOCH4_OUTER_FAILURE.json','_POST_EPOCH4_CONTROLLER.log']
 for suffix in suffixes:assert not(C/(ID+suffix)).exists(),'ABSENT outer attempt controls required'
 stop_requested=[]
 def interrupted(signum,frame):stop_requested.append(signum)
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 p=None;immediate=None;known={};gate_read=gate_write=None;deadline=time.time()+6*3600;peakrss=peakbytes=0;telemetry_samples_dropped=0;failure=None;unresolved=[];reconciliation=None
 def close_gate():
  nonlocal gate_read,gate_write
  for name in ['gate_read','gate_write']:
   fd=gate_read if name=='gate_read'else gate_write
   if fd is not None:
    try:os.close(fd)
    except OSError:pass
   if name=='gate_read':gate_read=None
   else:gate_write=None
 def process(pid):
  row=pathlib.Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()
  return {'pid':int(pid),'ticks':row[19],'ppid':int(row[1]),'pgid':int(row[2]),'sid':int(row[3]),'state':row[0],'rss':max(0,int(row[21]))*os.sysconf('SC_PAGE_SIZE')}
 def exited():
  # Do not let poll()/wait() release the direct controller identity before cleanup.
  if p is None:return None
  return os.waitid(os.P_PID,p.pid,os.WEXITED|os.WNOHANG|os.WNOWAIT)
 def ownership_sessions():
  sessions=[]
  if immediate is not None:sessions.append({'sid':immediate['sid'],'pgid':immediate['pgid'],'start_floor_ticks':int(immediate['ticks'])})
  if WORK.exists():
   for file in WORK.glob('CORE_PROCESS_START_*.json'):
    q=json.loads(file.read_text());assert q['parent_pid']==p.pid
    assert q['sid']==q['pgid']==q['pid'] and q['start_floor_ticks']==int(q['ticks'])
    try:leader=process(q['pid'])
    except(FileNotFoundError,ProcessLookupError):leader=None
    if leader is not None and leader['ticks']!=q['ticks']:continue
    sessions.append(q)
  return sessions
 def refresh():
  if p is None:return
  sessions=ownership_sessions()
  # A private child session may still have a sort process after its leader exited.
  for entry in pathlib.Path('/proc').iterdir():
   if not entry.name.isdigit():continue
   try:now=process(int(entry.name))
   except(FileNotFoundError,ProcessLookupError):continue
   if any(now['sid']==s['sid']and now['pgid']==s['pgid']and int(now['ticks'])>=s['start_floor_ticks']for s in sessions):known[now['pid']]=now
 def live_owned():
  found=[]
  for q in known.values():
   try:now=process(q['pid'])
   except(FileNotFoundError,ProcessLookupError):continue
   if(now['ticks'],now['sid'],now['pgid'])==(q['ticks'],q['sid'],q['pgid'])and now['state']not in ['Z','X','x']:found.append(now)
  return found
 def exact_signal(q,sig):
  # pidfd pins the process across the identity-check/signal race; never killpg.
  assert q['pid']!=os.getpid()
  try:fd=os.pidfd_open(q['pid'])
  except ProcessLookupError:return
  try:
   try:now=process(q['pid'])
   except(FileNotFoundError,ProcessLookupError):return
   if(now['ticks'],now['sid'],now['pgid'])!=(q['ticks'],q['sid'],q['pgid']):return
   if now['state']in ['Z','X','x']:return
   signal.pidfd_send_signal(fd,sig)
  except ProcessLookupError:pass
  finally:os.close(fd)
 def stopped(q):
  try:
   rows=list(pathlib.Path('/proc',str(q['pid']),'task').glob('*/stat'))
   return all(x.read_text().rsplit(')',1)[1].split()[0]in ['T','t','Z','X','x']for x in rows)
  except(FileNotFoundError,ProcessLookupError):return True
 def cleanup():
  close_gate()
  if p is None:return []
  if immediate is None:
   # Unreleased bootstrap has no descendants; direct child remains unreaped.
   try:now=process(p.pid);known[p.pid]=now
   except(FileNotFoundError,ProcessLookupError):pass
  end=time.monotonic()+3;previous=None
  while time.monotonic()<end:
   refresh();active=live_owned()
   for q in active:exact_signal(q,signal.SIGSTOP)
   ids={(q['pid'],q['ticks'])for q in active}
   if ids==previous and all(stopped(q)for q in active):break
   previous=ids;time.sleep(.05)
  for sig in [signal.SIGTERM,signal.SIGKILL]:
   # Rediscover and revalidate every exact PID at each signaling round.
   refresh()
   for q in live_owned():
    exact_signal(q,sig)
    if sig==signal.SIGTERM:exact_signal(q,signal.SIGCONT)
   end=time.monotonic()+3
   while time.monotonic()<end:
    refresh()
    if not live_owned():break
    time.sleep(.05)
  refresh();remaining=live_owned()
  # Reap only after all owned SID/PG members have been checked/cleaned.
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:remaining.append({'pid':p.pid,'direct_child_not_reaped_after_cleanup':True})
  return remaining

 try:
  assert not stop_requested,'stop requested before child startup'
  gate_read,gate_write=os.pipe()
  with(C/(ID+'_POST_EPOCH4_CONTROLLER.log')).open('x')as log:
   p=subprocess.Popen([sys.executable,'-c',BOOTSTRAP,str(gate_read),str(controller),str(grantpath)],pass_fds=(gate_read,),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  assert hasattr(os,'pidfd_open')and hasattr(signal,'pidfd_send_signal')
  immediate=process(p.pid);assert immediate['sid']==immediate['pgid']==p.pid;known[p.pid]=immediate
  save(C/(ID+'_POST_EPOCH4_SUPERVISOR.json'),{'pid':os.getpid(),'start_ticks':proc.proc(os.getpid())['ticks'],'controller':immediate,'deadline_unix':deadline,'startup_gate_released_only_after_this_durable_journal':True,'whole_epoch_Native_bytes_polled_bound':u.LIMIT,'whole_tree_plus_supervisor_RSS_polled_bound':4*2**30,'minimum_free':'DYNAMIC5GiB+ALLreserved+1GiB+64MiB; own remaining768MiB during stage;128MiB admission hysteresis','no_GPU_or_record_revalidation':True})
  assert not stop_requested,'stop requested while child remained behind startup gate'
  os.write(gate_write,b'G');close_gate()
  with(C/(ID+'_POST_EPOCH4_RESOURCE_EVENTS.jsonl')).open('x')as log:
   while exited()is None:
    refresh();ps=live_owned();rss=sum(q['rss']for q in ps)+proc.proc(os.getpid())['rss'];usage=u.epoch_native_usage();used=usage['total_bytes'];budget=u.LIMIT
    statepath=C/(ID+'_POST_EPOCH4_STATE.json')
    if statepath.exists():
     state=json.loads(statepath.read_text());assert state['pid']==p.pid and state['ticks']==immediate['ticks'];budget=state['stage_budget'];assert budget in [0,u.LIMIT]
     if budget==0:assert state['status']in ['OLD98_CLOSED_CHAIN_RECHECKED','FINAL_ALL100_NO_NATIVE_PAYLOAD_REMAINING','COMMITTED_VERIFIED_FULL100_NO_GPU_REPLAY']
    resource=u.resources(stage_budget=budget);free=resource['Native_free'];peakrss=max(peakrss,rss);peakbytes=max(peakbytes,used)
    event=(json.dumps({'unix':time.time(),'RSS_including_sort_and_supervisor':rss,'whole_epoch_Native_tree_bytes':used,'Native_usage_breakdown':usage,'free':free,'resource':resource,'active_stage_budget':budget,'processes':ps})+'\n').encode()
    if log.tell()+len(event)<=8*2**20:log.write(event.decode());log.flush()
    else:telemetry_samples_dropped+=1
    assert not stop_requested and time.time()<deadline and rss<4*2**30 and used<=u.LIMIT,'whole epoch stop/deadline/RSS/Native polled threshold'
    time.sleep(.5)
   status=exited();assert status is not None
   rc=status.si_status if status.si_code==os.CLD_EXITED else-status.si_status
   assert not stop_requested and rc==0,('CPU post controller exit',rc)
   refresh();assert not live_owned(),'controller ended with live private session members'
   assert p.wait(timeout=3)==0
 except BaseException as e:
  failure=repr(e)
  try:unresolved=cleanup()
  except BaseException as cleanup_error:unresolved=[{'cleanup_error':repr(cleanup_error)}]
  reconciliation=reconcile_failure(failure,unresolved)
 finally:
  close_gate()
  terminal_status='PASS'if not failure else'COMMIT_PRESENT_CLOSEOUT_NOTE'if reconciliation and reconciliation.get('commit')else'FAILED_RETAINED'
  save(C/(ID+'_POST_EPOCH4_SUPERVISOR_TERMINAL.json'),{'status':terminal_status,'failure':failure,'controller_returncode':None if p is None else p.returncode,'recursive_RSS_peak_bytes':peakrss,'telemetry_JSONL_cap_bytes':8*2**20,'telemetry_samples_dropped':telemetry_samples_dropped,'control_bytes_in_768MiB_accounting':True,'whole_Native_tree_peak_bytes':peakbytes,'unresolved_exact_own_processes':unresolved,'operational_reconciliation':reconciliation,'source_KEEP':True,'no_GPU_or_SIM_runs':True,'bounds_are_polled_not_quotas':True})
 if failure:sys.exit(1)
if __name__=='__main__':main()
