"""Isolated operational same-owner recovery; not installed by this module import.

Frozen scientific source, binary, plan, approval, request and identities remain
unchanged. A separately approved Main-thread install retains the old flock OFD,
observes inherited futures, and supplies one new operational dispatch generation.
"""
from pathlib import Path
import ast,copy,fcntl,hashlib,json,os,queue,sys,threading,time,types,traceback
P=Path
BASE=P('/root/data/dtc_controlled_oracle_20261106_v1')
OPS=BASE/'initial8/tools/oracle_ops.py'
OPS_SHA='29a97d55dc2acc4e84c3fa228025f7d2f619ef7d1fbc1af867645ec279047fb4'
GENERATION='DTC_ORACLE_OPERATIONAL_RECOVERY_GENERATION_V1'
OWNER_PID=1498278;OWNER_START=977758783

def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def rd(p):return json.loads(P(p).read_bytes())
def put(p,value,exclusive=False):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);b=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
 if exclusive:
  with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 else:
  q=p.with_name('.'+p.name+'.RECOVERY_WRITING');q.write_bytes(b);os.replace(q,p)
def resource_hold(error):
 return isinstance(error,RuntimeError)and str(error).startswith(('RESOURCE_HOLD','REGISTRY_SHARED_LOCK_BUSY','REGISTRY_EX_BUSY','REGISTRY_BUSY'))

class PoolBusy(RuntimeError):pass
class PlainFuture:
 def __init__(self):self.event=threading.Event();self.value=None;self.error=None
 def done(self):return self.event.is_set()
 def result(self,timeout=None):
  if not self.event.wait(timeout):raise TimeoutError('CPU_PLAIN_FUTURE_TIMEOUT')
  if self.error is not None:raise self.error
  return self.value
class PlainPool:
 """Bounded nonblocking queue; no atexit/TPE globals/flag changes."""
 def __init__(self,max_workers,thread_name_prefix,queue_capacity=None):
  assert 0<max_workers<=128
  self.limit=max_workers;self.name=thread_name_prefix;self.q=queue.Queue(queue_capacity or 256)
  self.lock=threading.Lock();self.threads=[];self.closed=False
 def submit(self,fn,*args,**kwargs):
  with self.lock:
   if self.closed:raise RuntimeError('PLAIN_POOL_ALREADY_CLOSED')
   f=PlainFuture()
   if len(self.threads)<self.limit:
    t=threading.Thread(target=self._worker,name=self.name+'_'+str(len(self.threads)),daemon=False);t.start();self.threads.append(t)
   try:self.q.put_nowait((f,fn,args,kwargs))
   except queue.Full:raise PoolBusy('RESOURCE_HOLD_PLAIN_POOL_QUEUE_FULL')
   return f
 def _worker(self):
  while True:
   item=self.q.get()
   try:
    if item is None:return
    f,fn,args,kwargs=item
    try:f.value=fn(*args,**kwargs)
    except BaseException as error:f.error=error
    finally:f.event.set()
   finally:self.q.task_done()
 def shutdown(self,wait=True):
  with self.lock:
   if not self.closed:
    self.closed=True
    # Only final shutdown, never in the admission/safety cadence.
    for _ in self.threads:self.q.put(None)
  if wait:
   for t in self.threads:t.join()
 def __enter__(self):return self
 def __exit__(self,*exc):self.shutdown(True)

def inspect_unwinding_scheduler(thread_id,ops_path=OPS):
 """Read an existing suspended unwind. Never resumes or edits its frame."""
 chain=[];f=sys._current_frames().get(thread_id)
 while f is not None:chain.append(f);f=f.f_back
 matches=[f for f in chain if f.f_code.co_name=='run_scheduler'and P(f.f_code.co_filename)==P(ops_path)]
 assert len(matches)==1,'ONE_OLD_SCHEDULER_FRAME_REQUIRED'
 frame=matches[0];names=[f.f_code.co_name for f in chain[:chain.index(frame)]]
 assert 'shutdown'in names and '__exit__'in names and ('join'in names or '_wait_for_tstate_lock'in names),'OLD_LOOP_NOT_PROVEN_UNWINDING'
 loc=frame.f_locals
 for name in ['workers','archives','review_pool']:
  pool=loc[name];assert pool._shutdown is True,'OLD_EXECUTOR_STILL_ADMITTING'
  if name!='workers':assert all(not t.is_alive()for t in pool._threads),'OLD_POSTPROCESS_STILL_ACTIVE'
 ex=sys._current_exceptions().get(thread_id)
 assert ex is not None and resource_hold(ex[1]),'EXPECTED_ORIGINAL_RESOURCE_UNWIND_REQUIRED'
 held=loc['held'];assert not held.closed
 return dict(frame=frame,held=held,running=dict(loc['running']),post=dict(loc['post']),reviews=dict(loc['reviews']),
  work=loc['work'],review=loc['review'],dispatch_index=loc['dispatch_index'],original_exception=repr(ex[1]),
  original_thread_ident=thread_id,original_globals=frame.f_globals)

def capture_handoff(state,ops_path=OPS):
 assert GENERATION not in state,'RECOVERY_ALREADY_INSTALLED_NO_DUPLICATE'
 cap=inspect_unwinding_scheduler(state['thread_ident'],ops_path)
 st=os.fstat(cap['held'].fileno());expected=os.stat(P(ops_path).parents[2]/'control/SHARED_DISPATCH_OWNER.lock')
 assert(st.st_dev,st.st_ino)==(expected.st_dev,expected.st_ino),'WRONG_DISPATCH_LOCK_INODE'
 dup=os.dup(cap['held'].fileno());os.set_inheritable(dup,False)
 cap['held_duplicate']=os.fdopen(dup,'a+b',buffering=0)
 assert os.fstat(dup).st_ino==st.st_ino
 # Never LOCK_UN: dup and old held share one OFD. Closing old fd later does not
 # release our surviving reference; no competing open/flock is introduced.
 cap['lock_identity']=dict(device=st.st_dev,inode=st.st_ino,original_fd=cap['held'].fileno(),duplicate_fd=dup,same_OFD_by_os_dup=True)
 return cap

def closed_receipt(ctx,c):
 q=ctx['e'].registered()[2];row=q['consumed'][c];root=ctx['root'];ip=root/'control/qualification_ledger'/(c+'.INTENT.json')
 intent=rd(ip);done=rd(ip.with_name(c+'.DONE.json'));out=P(intent['output'])
 assert done==row['execution_receipt']==rd(out/'NATIVE_EXIT.json')and done['uuid']==intent['uuid']==row['uuid'],'REAL_CLOSED_RECEIPT_REQUIRED_TO_RELEASE_CLAIM'
 return done

def unused_identity(ctx,c):
 q=ctx['e'].registered()[2]
 assert c not in q['consumed'],'CONSUMED_IDENTITY_MUST_NEVER_BE_RESUBMITTED'
 assert not(ctx['root']/'control/qualification_ledger'/(c+'.INTENT.json')).exists(),'UNCERTAIN_INTENT_PRESERVE_CLAIM'
 return True

def launch_phase_ready(running):
 """Short admission phase ends on real consumption+PID binding, not model exit."""
 for future,(ctx,c)in list(running.items()):
  finished=future.done()
  q=ctx['e'].registered()[2]
  if c not in q['consumed']:
   if finished:unused_identity(ctx,c);continue
   return False
  row=q['consumed'][c]
  if row.get('execution_receipt'):
   closed_receipt(ctx,c);continue
  assert not finished,'FINISHED_FRONTEND_WITHOUT_CLOSED_RECEIPT_FAIL_CLOSED'
  ip=ctx['root']/'control/qualification_ledger'/(c+'.INTENT.json')
  if not ip.exists():return False
  intent=rd(ip);assert intent['uuid']==row['uuid']
  pp=P(intent['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
  if not pp.exists():return False
  pid=rd(pp);spec=ctx['e'].spec_for(c)
  assert type(pid['pid'])is int and pid['pid']>0 and type(pid['start_ticks'])is int and pid['start_ticks']>0
  assert pid['oracle_execution_binding']==intent['oracle_execution_binding'] and spec['native_simulator_argv'][0]in pid['maps'],'ACTUAL_PID_BINDING_REQUIRED_BEFORE_NEXT_ADMISSION'
 return True

def cleanup_orphans(state,running,post,reviews,on_error):
 """Per-claim error isolation; uncertain claims never block healthy harvest."""
 busy={ctx['request']+':'+c for ctx,c in list(running.values())+list(post.values())+list(reviews.values())}
 changed=0
 with state['lock']:
  by_request={ctx['request']:ctx for ctx in state['contexts'].values()}
  for key,claim in list(state['claims'].items()):
   if key in busy:continue
   try:
    ctx=by_request[claim['request']];c=claim['cohort'];q=ctx['e'].registered()[2]
    if c in q['consumed']:
     if not q['consumed'][c].get('execution_receipt'):continue
     closed_receipt(ctx,c)
    else:unused_identity(ctx,c)
    state['claims'].pop(key,None);state[GENERATION]['reservation_sync_pending']=True;changed+=1
   except BaseException as error:on_error(error)
 if state[GENERATION].get('reservation_sync_pending'):
  try:state['saveclaims']()
  except BaseException as error:on_error(error)
 return changed

def transformed_scheduler(original):
 assert hashlib.sha256(original.encode()).hexdigest()==OPS_SHA,'FROZEN_OPERATIONAL_PREIMAGE_REQUIRED'
 tree=ast.parse(original);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='run_scheduler');src=ast.get_source_segment(original,node)
 changes=[]
 def replace(old,new):
  nonlocal src
  assert src.count(old)==1,'EXACT_TRANSFORM_ANCHOR:'+old[:80]
  src=src.replace(old,new,1);changes.append(dict(old=old,new=new))
 replace('def run_scheduler():','def recovery_dispatch_loop():')
 replace("assert state['thread_ident']is None,'SECOND_SCIENTIFIC_DISPATCH_POOL_FORBIDDEN';state['thread_ident']=threading.get_ident()","assert state['thread_ident']==_RECOVERY['cap']['original_thread_ident'];state[_RECOVERY['generation']]['thread_ident']=threading.get_ident()")
 replace('running={};post={};reviews={};dispatch_index=0',"running=dict(_RECOVERY['cap']['running']);post=dict(_RECOVERY['cap']['post']);reviews=dict(_RECOVERY['cap']['reviews']);dispatch_index=_RECOVERY['cap']['dispatch_index']")
 replace(" def saveclaims():\n  with state['lock']:"," def saveclaims():\n  state[_RECOVERY['generation']]['reservation_sync_pending']=True\n  with state['lock']:")
 replace("for ctx in state['contexts'].values():sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})","for ctx in state['contexts'].values():sync_stage_reservation(ctx,{v['cohort']:v for v in state['claims'].values()if v['request']==ctx['request']})\n  state[_RECOVERY['generation']]['reservation_sync_pending']=False")
 begin=src.index(' def work(ctx,c):');end=src.index(" with(BASE/'control/SHARED_DISPATCH_OWNER.lock')",begin)
 src=src[:begin]+" work=_RECOVERY['cap']['work'];review=_RECOVERY['cap']['review']\n"+src[end:];changes.append(dict(kind='REUSE_EXACT_EXISTING_WORK_REVIEW_CLOSURES'))
 replace(" with(BASE/'control/SHARED_DISPATCH_OWNER.lock').open('a+b')as held:\n  fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);put(BASE/'control/SHARED_DISPATCH_STARTED.json',dict(UTC=stamp(),pid=os.getpid(),start_ticks=977758783,thread_ident=threading.get_ident(),CPU_allowance=sorted(mask),single_dispatcher=True),True);saveclaims()", " with _RECOVERY['cap']['held_duplicate']as held:\n  state[_RECOVERY['generation']]['reservation_sync_pending']=True")
 replace("with concurrent.futures.ThreadPoolExecutor(max_workers=min(128,len(mask)),thread_name_prefix='DTC_ORACLE_SHARED_MODEL')as workers,concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='DTC_ORACLE_ARCHIVE')as archives,concurrent.futures.ThreadPoolExecutor(max_workers=1,thread_name_prefix='DTC_ORACLE_INDEPENDENT_CPU_REVIEW')as review_pool:","with _PlainPool(max_workers=min(128,len(mask)),thread_name_prefix='DTC_ORACLE_RECOVERY_MODEL')as workers,_PlainPool(max_workers=1,thread_name_prefix='DTC_ORACLE_RECOVERY_ARCHIVE')as archives,_PlainPool(max_workers=1,thread_name_prefix='DTC_ORACLE_RECOVERY_REVIEW')as review_pool:")
 replace("value=future.result();running.pop(future);event(ctx,'MODEL_WORKER_RETURN',cohort=c,result=value)","value=_RECOVERY['harvest'](future,running,ctx,c,'MODEL')\n     if value is None:continue\n     event(ctx,'MODEL_WORKER_RETURN',cohort=c,result=value)")
 replace("value=future.result();post.pop(future);event(ctx,'RESULT_CONSUMED',cohort=c,state=value['state']);saveclaims()","value=_RECOVERY['harvest'](future,post,ctx,c,'POST')\n     if value is None:continue\n     event(ctx,'RESULT_CONSUMED',cohort=c,state=value['state']);saveclaims()")
 replace("if value['state']=='EXECUTION_CLOSED':\n      with state['lock']:","if value['state']=='EXECUTION_CLOSED':\n      _closed_receipt(ctx,c)\n      with state['lock']:")
 replace("elif c not in ctx['e'].registered()[2]['consumed']:\n      with state['lock']:","elif c not in ctx['e'].registered()[2]['consumed']:\n      _unused_identity(ctx,c)\n      with state['lock']:")
 replace("for _ in range(min(128,len(mask))-len(running)):","if state[_RECOVERY['generation']].get('reservation_sync_pending')or not _launch_phase_ready(running):all_pending=[]\n    for _ in range(min(1,max(0,min(128,len(mask))-len(running)))):")
 replace("ctx,spec=next((k,s)for k,s in all_pending if s['cohort']==decision['cohort']);c=spec['cohort'];fresh=ctx['res'].resources(spec,True)","ctx,spec=next((k,s)for k,s in all_pending if s['cohort']==decision['cohort']);c=spec['cohort'];fresh=_RECOVERY['resource'](ctx,spec,False)\n     if fresh is None:continue")
 replace("charged=ctx['res'].resources(spec,True)","charged=_RECOVERY['resource'](ctx,spec,True)\n     if charged is None:\n      _unused_identity(ctx,c)\n      with state['lock']:state['claims'].pop(key(ctx,c),None);saveclaims()\n      continue")
 replace("if not all(charged[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):\n      with state['lock']:","if not all(charged[k]for k in ['physical_RAM_pass','physical_disk_pass','admission_disk_pass','admission_pressure_pass']):\n      _unused_identity(ctx,c)\n      with state['lock']:")
 replace("running[workers.submit(work,ctx,c)]=(ctx,c)","_unused_identity(ctx,c);running[workers.submit(work,ctx,c)]=(ctx,c)")
 # The original loop would tear down all executors for a resource deferral.
 # Retain workers and postprocessing after typed resource HOLD; all other
 # exceptions create an explicit global no-new-admission pause and evidence.
 lines=src.splitlines();wi=next(i for i,l in enumerate(lines)if l=='   while True:');body=lines[wi+1:]
 lines=lines[:wi+1]+['    try:',"     if not state[_RECOVERY['generation']].get('loop_observed'):_RECOVERY['running_ack']();state[_RECOVERY['generation']]['loop_observed']=True","     _RECOVERY['cleanup'](running,post,reviews)"]+[' '+l for l in body]+["    except BaseException as recovery_error:","     _RECOVERY['cycle_error'](recovery_error)","     time.sleep(2)"]
 src='\n'.join(lines)+'\n';changes.append(dict(kind='CYCLE_ERROR_ISOLATION_TYPED_DEFER_OTHER_FAIL_CLOSED'))
 compile(src,'RECOVERY_OPERATIONAL_TRANSFORM','exec')
 return src,changes

def owner_fd_snapshot():
 return {str(fd):dict(target=os.readlink('/proc/self/fd/'+str(fd)),device=os.fstat(fd).st_dev,inode=os.fstat(fd).st_ino)for fd in [3,4]}
def scientific_preimage(contexts):
 out={}
 for ctx in contexts:
  q=ctx['e'].registered()[2];root=ctx['root'];rows={}
  for c,row in q['consumed'].items():
   ip=root/'control/qualification_ledger'/(c+'.INTENT.json');item=dict(uuid=row['uuid'])
   if ip.exists():
    intent=rd(ip);pp=P(intent['output'])/'NATIVE_SIMULATOR_PID_AND_MAPS.json'
    if pp.exists():
     pid=rd(pp);item.update(pid=pid['pid'],start_ticks=pid['start_ticks'])
   rows[c]=item
  out[ctx['request']]=dict(budget=q['budget'],consumed_UUID_PID_start=rows,plan_sha256=sha(root/'control/EXECUTION_PLAN.json'),approval_sha256=sha(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'))
 return out

def install(release_path):
 """Side effects only after independent review and explicit coordinator release.

 Never called during preparation/CPU qualification. No real simulator is
 launched by install itself; the sole adopted dispatch generation uses only the
 existing registered request, frozen frontend and one-use consumption path.
 """
 assert threading.current_thread()is threading.main_thread()and os.getpid()==OWNER_PID
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==OWNER_START and not sys.is_finalizing()
 release=rd(release_path)
 assert release['schema']=='DTC_ORACLE_OPERATIONAL_RECOVERY_INSTALL_V1'and release['approved_by_DTC_MAIN']is True
 assert release['source_sha256']==sha(__file__)
 review=release['independent_review'];assert sha(review['path'])==review['sha256']
 reviewed=rd(review['path']);assert reviewed['status']=='PASS'and reviewed['subject_source_sha256']==sha(__file__)and reviewed['scope']=='SAME_OWNER_OPERATIONAL_RECOVERY_CPU_QUALIFICATION'
 preimage=release['coordinator_preimage'];assert sha(preimage['path'])==preimage['sha256']
 assert sha(OPS)==OPS_SHA
 main=sys.modules['__main__'];state=getattr(main,'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1')
 with state['lock']:
  assert set(state['contexts'])<={str(BASE/'initial8'),str(BASE/'remaining24')}
  fds_before=owner_fd_snapshot();science_before=scientific_preimage(state['contexts'].values())
  for ctx in state['contexts'].values():ctx['e'].assert_parent_lease();ctx['e'].registered()
  code,edits=transformed_scheduler(OPS.read_text())
  cap=capture_handoff(state)
 recovery_thread_started=False
 try:
  record=dict(schema='DTC_ORACLE_OPERATIONAL_RECOVERY_HANDOFF_V1',generation=GENERATION,source_sha256=sha(__file__),original_ops_sha256=OPS_SHA,
   original_thread_ident=cap['original_thread_ident'],FD3_FD4_before=fds_before,scientific_preimage=science_before,coordinator_preimage=release['coordinator_preimage'],lock_identity=cap['lock_identity'],inherited_model_futures=len(cap['running']),inherited_archive_futures=len(cap['post']),inherited_review_futures=len(cap['reviews']),
   original_exception=cap['original_exception'],no_model_restarts=True,source_binary_plan_request_approval_UUIDs_unchanged=True,independent_review=review,thread_ident=None)
  record['transformed_scheduler_sha256']=hashlib.sha256(code.encode()).hexdigest()
  root=BASE/'control/operational_scheduler_recovery_v1';root.mkdir(exist_ok=False)
  put(root/'HANDOFF.fixed.json',record,True);put(root/'EXACT_OPERATIONAL_TRANSFORMS.fixed.json',edits,True)
  (root/'TRANSFORMED_OPERATIONAL_SCHEDULER.py').write_text(code)
  state[GENERATION]=record
  def event(kind,**data):put(root/(str(time.time_ns())+'_'+kind+'.json'),dict(kind=kind,**data),True)
  def fresh(ctx,spec,postclaim):
   try:return ctx['res'].resources(spec,True)
   except BaseException as error:
    if not resource_hold(error):raise
    ctx['cool'][spec['cohort']]=time.monotonic()+30
    event('EXPECTED_RESOURCE_DEFERRAL',cohort=spec['cohort'],postclaim=postclaim,error=repr(error));return None
  def cycle_error(error):
   if resource_hold(error):event('EXPECTED_CYCLE_RESOURCE_DEFERRAL',error=repr(error));return
   event('FAIL_CLOSED_ENGINEERING',error=repr(error),traceback=traceback.format_exc())
   pause=BASE/'control/ENGINEERING_PAUSE_NEW.json'
   if not pause.exists():
    try:put(pause,dict(reason='RECOVERY_UNEXPECTED_ENGINEERING_FAIL_CLOSED',error=repr(error),generation=GENERATION,no_healthy_model_signals=True,model_retries=0),True)
    except FileExistsError:pass
  def harvest(future,mapping,ctx,c,kind):
   try:
    value=future.result()
    assert isinstance(value,dict)and'state'in value,'FUTURE_RESULT_SCHEMA_FAIL_CLOSED'
    return value
   except BaseException as error:
    ctx['errors'][c]=dict(reason='RECOVERY_'+kind+'_FUTURE_ENGINEERING',error=repr(error))
    ctx['cool']['post:'+c]=time.monotonic()+60
    cycle_error(error);return None
   finally:mapping.pop(future,None)
  env=dict(cap['original_globals']);env.update(_PlainPool=PlainPool,_closed_receipt=closed_receipt,_unused_identity=unused_identity,_launch_phase_ready=launch_phase_ready)
  env['_RECOVERY']=dict(cap=cap,generation=GENERATION,resource=fresh,cycle_error=cycle_error,harvest=harvest,cleanup=lambda running,post,reviews:cleanup_orphans(state,running,post,reviews,cycle_error),running_ack=lambda:event('RECOVERY_DISPATCH_RUNNING_SAME_OFD'))
  exec(compile(code,str(root/'TRANSFORMED_OPERATIONAL_SCHEDULER.py'),'exec'),env)
  thread=threading.Thread(target=env['recovery_dispatch_loop'],name='DTC_ORACLE_ONE_OPERATIONAL_RECOVERY',daemon=False)
  state[GENERATION]['thread']=thread;state[GENERATION]['module']=sys.modules.get(__name__);state[GENERATION]['environment']=env
  assert owner_fd_snapshot()==fds_before,'OWNER_FD3_FD4_CHANGED'
  after=scientific_preimage(state['contexts'].values())
  assert after==science_before,'SCIENTIFIC_UUID_PID_SOURCE_CHANGED_DURING_HANDOFF'
  thread.start()
  ack=dict(status='SAME_OWNER_OPERATIONAL_RECOVERY_GENERATION_STARTED',generation=GENERATION,source_sha256=sha(__file__),handoff_sha256=sha(root/'HANDOFF.fixed.json'),new_scientific_requests=0,model_restarts=0,shutdown_flags_reset=False,same_OFD_continuous=True,FD3_FD4_after=owner_fd_snapshot(),scientific_preimage_unchanged=after==science_before)
  put(root/'INSTALL_ACK.fixed.json',ack,True);return ack
 except BaseException as install_error:
  active=locals().get('thread')
  recovery_thread_started=bool(active is not None and active.ident is not None)
  if not recovery_thread_started:
   cap['held_duplicate'].close() # Never LOCK_UN and never close original held.
  status='STARTED_ACK_UNCERTAIN_FORWARD_ONLY'if recovery_thread_started else'FAILED_BEFORE_NEW_DISPATCH_FORWARD_ONLY'
  state.setdefault(GENERATION,{}).update(install_status=status,install_error=repr(install_error))
  evidence=dict(status=status,error=repr(install_error),new_thread_started=recovery_thread_started,our_duplicate_closed=not recovery_thread_started,old_held_untouched=True,automatic_retry=False)
  try:put(BASE/'control'/('RECOVERY_INSTALL_PARTIAL_'+str(time.time_ns())+'.json'),evidence,True)
  except BaseException:pass
  raise
