"""Finite Native-only post supervisor with gated startup and operational failure reconciliation."""
import pathlib,json,hashlib,importlib.util,subprocess,time,os,signal,shutil,sys,fcntl
C=pathlib.Path('/root/data/shared_rtx4080_trace_library_20261024_v1/control');N=C.parent;B=pathlib.Path('/root/share/mnt164/huangrulin/traces/rtx4080_sm89/bulk_20261024_v1');ID='ORD_LATE_stencil_c3e987b033b4_A002_CPU_ADOPT_V2';WORK=N/(ID+'_post_native_epoch3')
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
 note_path=C/(ID+'_POST_EPOCH3_OUTER_FAILURE.json')
 with(C/'RTX4080_QUEUE.lock').open('a')as f:
  fcntl.flock(f,fcntl.LOCK_EX);save(note_path,note);rows=json.loads((C/'QUEUE.json').read_text());row=next(x for x in rows if x['id']==ID)
  if not commit and row.get('status')!='COMMITTED_VERIFIED':row.update(status='FAILED_RETAINED',failure_receipt=str(note_path),CPU_post_epoch=3)
  elif commit:
   row['outer_failure_after_commit_note']=str(note_path)
   receipt=B/'receipts'/(ID+'_RECEIVER_READBACK.json')
   closed=json.loads(receipt.read_text())if receipt.exists()else{}
   if closed.get('manifest_sha256')==commit['manifest_sha256']:row.update(status='COMMITTED_VERIFIED',commit=commit)
   elif row.get('status')!='COMMITTED_VERIFIED':row.update(status='COMMIT_PRESENT_CLOSEOUT_PENDING',commit=commit)
  replace(C/'QUEUE.json',rows)
  statepath=C/(ID+'_POST_EPOCH3_STATE.json')
  if statepath.exists():save(C/(ID+'_POST_EPOCH3_STATE_BEFORE_OUTER_FAILURE.json'),json.loads(statepath.read_text()))
  replace(statepath,{'status':'FAILED_RETAINED_CPU_POST_ONLY'if not commit else'COMMIT_PRESENT_NOT_FAILED_REQUIRES_LOCAL_CLOSEOUT','failure_receipt':str(note_path),'unresolved_exact_own_processes':unresolved,'source_KEEP':True,'unix':time.time()})
 return note
# Bootstrap cannot execute or spawn controller work until its exact PID/start and durable journal exist.
BOOTSTRAP="import os,sys;fd=int(sys.argv[1]);token=os.read(fd,1);os.close(fd);sys.exit(125)if token!=b'G'else None;os.execv(sys.executable,[sys.executable,'-B',sys.argv[2],sys.argv[3]])"
def main():
 grantpath=pathlib.Path(sys.argv[1]);grant=json.loads(grantpath.read_text());assert grant['supervisor_sha256']==sha(pathlib.Path(__file__))
 controller=C/'resume_stencil_native8_post_epoch3_v3.py';assert sha(controller)==grant['controller_sha256']
 post=module(C/'post_app_parallel_v5.py','post','c6fdc374344f4bb1d9cdec8f396807a9aef8d9b1fcf4741fc8477b18b86a0c2a')
 proc=module(C/'validate_app_hot_resume_v4r3.py','proc','85ff5d68408632a4f15634bfa6a6d7a504429821ed8067f1ab8f39ce1b9a6909')
 authority=module(C/'read_native_foreign_reserve_v1.py','auth','441fec1917c436781cc0aa6e7e0b35f7a9aa0dc019b2fe96540fca27c78a29ba')
 foreign=authority.snapshot();assert foreign['registry_sha256']==grant['foreign_registry_sha256']and foreign['epoch_sha256']==grant['foreign_epoch_sha256']and foreign['sum_all_records_reserved_write_bytes']==grant['foreign_reserved_sum_bytes']<=2281701376
 suffixes=['_POST_EPOCH3_SUPERVISOR.json','_POST_EPOCH3_RESOURCE_EVENTS.jsonl','_POST_EPOCH3_SUPERVISOR_TERMINAL.json','_POST_EPOCH3_OUTER_FAILURE.json','_POST_EPOCH3_CONTROLLER.log']
 for suffix in suffixes:assert not(C/(ID+suffix)).exists(),'ABSENT outer attempt controls required'
 stop_requested=[]
 def interrupted(signum,frame):stop_requested.append(signum)
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 p=None;immediate=None;known={};gate_read=gate_write=None;deadline=time.time()+48*3600;peakrss=peakbytes=0;failure=None;unresolved=[];foreign_checked=0;reconciliation=None
 def close_gate():
  nonlocal gate_read,gate_write
  for name in ['gate_read','gate_write']:
   fd=gate_read if name=='gate_read'else gate_write
   if fd is not None:
    try:os.close(fd)
    except OSError:pass
   if name=='gate_read':gate_read=None
   else:gate_write=None
 def refresh():
  if p is None:return
  try:now=proc.proc(p.pid)
  except(FileNotFoundError,ProcessLookupError):return
  if immediate is None or now['ticks']==immediate['ticks']:
   for q in proc.descendants(p.pid):known[q['pid']]=q
 def cleanup():
  # Closing an unreleased gate makes startup child exit125 without any controller side effects.
  close_gate()
  if p is None:return []
  refresh()
  if immediate is None and p.returncode is None:
   # Direct unreaped Popen child PID cannot be reused; it is still blocked at startup gate.
   try:os.killpg(p.pid,signal.SIGTERM)
   except ProcessLookupError:pass
   try:p.wait(timeout=3)
   except subprocess.TimeoutExpired:
    try:os.killpg(p.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    try:p.wait(timeout=3)
    except subprocess.TimeoutExpired:return [{'pid':p.pid,'ownership':'direct_unreaped_Popen_child_behind_startup_gate','signal_pending':True}]
   return []
  end=time.monotonic()+3;previous=None;active=[]
  while time.monotonic()<end:
   refresh();active=[]
   for q in list(known.values()):
    try:
     now=proc.proc(q['pid'])
     if now['ticks']==q['ticks']and now['pgid']==q['pgid']:
      active.append(now)
      try:os.kill(q['pid'],signal.SIGSTOP)
      except ProcessLookupError:pass
    except(FileNotFoundError,ProcessLookupError):pass
   ids={(q['pid'],q['ticks'])for q in active}
   if ids==previous:break
   previous=ids;time.sleep(.05)
  groups={q['pgid']for q in active};assert os.getpgrp()not in groups
  for sig in[signal.SIGTERM,signal.SIGKILL]:
   for pg in groups:
    try:os.killpg(pg,sig);os.killpg(pg,signal.SIGCONT)
    except ProcessLookupError:pass
   time.sleep(3)
  remaining=[]
  for q in active:
   try:
    now=proc.proc(q['pid']);state=pathlib.Path('/proc',str(q['pid']),'stat').read_text().split(') ',1)[1].split()[0]
    if now['ticks']==q['ticks']and state!='Z':remaining.append(now)
   except(FileNotFoundError,ProcessLookupError):pass
  try:p.wait(timeout=3)
  except subprocess.TimeoutExpired:pass
  return remaining
 try:
  assert not stop_requested,'stop requested before child startup'
  gate_read,gate_write=os.pipe()
  with(C/(ID+'_POST_EPOCH3_CONTROLLER.log')).open('x')as log:
   p=subprocess.Popen([sys.executable,'-c',BOOTSTRAP,str(gate_read),str(controller),str(grantpath)],pass_fds=(gate_read,),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  immediate=proc.proc(p.pid);known[p.pid]=immediate
  save(C/(ID+'_POST_EPOCH3_SUPERVISOR.json'),{'pid':os.getpid(),'start_ticks':proc.proc(os.getpid())['ticks'],'controller':immediate,'deadline_unix':deadline,'startup_gate_released_only_after_this_durable_journal':True,'whole_epoch_Native_bytes_polled_bound':4*2**30,'whole_tree_plus_supervisor_RSS_polled_bound':16*2**30,'minimum_free':9*2**30,'no_GPU_or_record_revalidation':True})
  assert not stop_requested,'stop requested while child remained behind startup gate'
  os.write(gate_write,b'G');close_gate()
  with(C/(ID+'_POST_EPOCH3_RESOURCE_EVENTS.jsonl')).open('x')as log:
   while p.poll()is None:
    refresh();ps=proc.descendants(p.pid);rss=sum(q['rss']for q in ps)+proc.proc(os.getpid())['rss'];used=post.tree_size_race_safe(WORK);free=shutil.disk_usage(C).free;peakrss=max(peakrss,rss);peakbytes=max(peakbytes,used)
    if time.time()-foreign_checked>=10:foreign=authority.snapshot();assert foreign['sum_all_records_reserved_write_bytes']<=2281701376;foreign_checked=time.time()
    log.write(json.dumps({'unix':time.time(),'RSS_including_sort_and_supervisor':rss,'whole_epoch_Native_tree_bytes':used,'free':free,'foreign':foreign,'processes':ps})+'\n');log.flush()
    assert not stop_requested and time.time()<deadline and rss<16*2**30 and used<4*2**30 and free>9*2**30,'whole epoch stop/deadline/RSS/Native/free polled threshold'
    time.sleep(.5)
   assert not stop_requested and p.returncode==0,('CPU post controller exit',p.returncode)
 except BaseException as e:
  failure=repr(e)
  try:unresolved=cleanup()
  except BaseException as cleanup_error:unresolved=[{'cleanup_error':repr(cleanup_error)}]
  reconciliation=reconcile_failure(failure,unresolved)
 finally:
  close_gate()
  terminal_status='PASS'if not failure else'COMMIT_PRESENT_CLOSEOUT_NOTE'if reconciliation and reconciliation.get('commit')else'FAILED_RETAINED'
  save(C/(ID+'_POST_EPOCH3_SUPERVISOR_TERMINAL.json'),{'status':terminal_status,'failure':failure,'controller_returncode':None if p is None else p.returncode,'recursive_RSS_peak_bytes':peakrss,'whole_Native_tree_peak_bytes':peakbytes,'unresolved_exact_own_processes':unresolved,'operational_reconciliation':reconciliation,'source_KEEP':True,'no_GPU_or_SIM_runs':True,'bounds_are_polled_not_quotas':True})
 if failure:sys.exit(1)
if __name__=='__main__':main()
