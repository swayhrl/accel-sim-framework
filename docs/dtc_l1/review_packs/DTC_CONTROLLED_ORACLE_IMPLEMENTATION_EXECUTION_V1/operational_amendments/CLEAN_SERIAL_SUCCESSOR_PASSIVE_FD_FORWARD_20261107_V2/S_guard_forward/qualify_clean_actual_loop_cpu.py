"""Actual derived scheduler loop with fake science backend and temporary OFDs.

No native entrypoint, reviewer child, real registry or scientific source is
written. Only nested work/review backends are replaced in the CPU AST fixture.
"""
from pathlib import Path
import ast,copy,contextlib,fcntl,hashlib,json,os,tempfile,threading,time,types,traceback,sys
LATCH_IO='--latch-io'in sys.argv
class MockHealthyDrained(BaseException):pass
pins=json.loads(Path(__file__).with_name('CPU_SOURCE_INPUTS.fixed.json').read_bytes())
P=Path(pins['B2']['path'])
m=types.ModuleType('CPU_B_SOURCE');m.__file__=str(P);exec(compile(P.read_bytes(),str(P),'exec'),m.__dict__)
engine=types.ModuleType('CPU_CLEAN_TRANSFORM');engine.__file__=str(Path(__file__).with_name('oracle_successor_engine.py'));exec(compile(Path(engine.__file__).read_bytes(),engine.__file__,'exec'),engine.__dict__)
source,edits=engine.derive_ops(Path(pins['ops']['path']).read_bytes(),P.read_bytes())
checks=[]
def check(name,value):
 checks.append(dict(name=name,status='PASS'if value else'FAIL'))
def reject(fn):
 try:fn()
 except (AssertionError,RuntimeError):return True
 return False

with tempfile.TemporaryDirectory(prefix='MOCK_NOT_SCIENCE_B_LOOP_')as temp:
 base=Path(temp);root=base/'remaining24';generation_root=base/'generation';generation_root.mkdir()
 (root/'control/specs').mkdir(parents=True);(root/'analysis').mkdir();(root/'control/qualification_ledger').mkdir();(base/'control').mkdir()
 def put(p,v,*args):
  p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(m.encoded(v))
 cpus=sorted(os.sched_getaffinity(0))[:2];needlen=len(cpus)
 q=dict(request=engine.REQUEST,budget=3,remaining=2,consumed={'MOCK_OLD':dict(uuid='MOCK_UUID_OLD')},admitted_specs={})
 qlock=threading.RLock()
 names=['MOCK_OLD','MOCK_A','MOCK_B']
 specs={c:dict(cohort=c,request=q['request'],workload='MOCK_INPUT',program=c,native_simulator_argv=['MOCK_NOT_A_SIMULATOR'],limits=dict(max_result_directory_bytes=1024,max_process_tree_rss_bytes=2048))for c in names}
 plan=dict(stage='remaining24',qualified_modes=[],initial_qualifiers={},new_dispatcher_cpu_allowance=cpus,protected_cpu_ids=[],archive_workers=1)
 for c,v in specs.items():put(root/'control/specs'/(c+'.json'),v)
 put(root/'control/RESOURCE_POLICY.json',{})
 workcalls=[];finishes=[];resource_calls=[];sync_calls=[];archive_active=[0,0];cycle_events=[]
 def pidbind(c,u):
  out=root/'DTC/run/results'/u;out.mkdir(parents=True,exist_ok=True)
  i=dict(uuid=u,cohort=c,output=str(out),oracle_execution_binding=dict(MOCK_NOT_SCIENCE=True,cohort=c))
  ip=root/'control/qualification_ledger'/(c+'.INTENT.json');put(ip,i)
  q['consumed'][c]['intent_sha256']=m.sha(ip)
  put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=999999999,start_ticks=1,maps='MOCK_NOT_A_SIMULATOR',oracle_execution_binding=i['oracle_execution_binding']))
 def close(c):
  row=q['consumed'][c];i=m.rd(root/'control/qualification_ledger'/(c+'.INTENT.json'));out=Path(i['output']);(out/'raw.log.gz').write_bytes(b'MOCK_NOT_SCIENCE_NOT_GZIP')
  d=dict(uuid=row['uuid'],cohort=c,new_attempt_consumed=1,automatic_retry=False,raw_sha256=m.sha(out/'raw.log.gz'),stop_reason=None,launcher_wait_returncode=0,native_simulator_observed=True)
  put(out/'NATIVE_EXIT.json',d);put(root/'control/qualification_ledger'/(c+'.DONE.json'),d);row['execution_receipt']=d
 pidbind('MOCK_OLD','MOCK_UUID_OLD')
 class Engine:
  def registered(self):
   with qlock:return {},{},copy.deepcopy(q),plan
  def assert_parent_lease(self):return True
  def canonical(self,c):return copy.deepcopy(specs[c])
  spec_for=canonical
  def jsonsha(self,v):return hashlib.sha256(m.encoded(v)).hexdigest()
 e=Engine()
 class Wait(RuntimeError):pass
 class Res:
  WaitInitialRuntimeGate=Wait
  def sample_system(self):return dict(cpu_allowed=cpus,observed_affinity_claims=[])
  def admission_hold(self,*args):return None
  def verify_initial_runtime_gate(self,*args):return dict(MOCK_NOT_SCIENCE=True)
  def choose_dispatch(self,pending,sample,claims,**kw):
   available=[c for c in cpus if c not in{x['host_cpu']for x in claims.values()}]
   if not pending or not available:return None
   return dict(cohort=pending[0]['cohort'],host_cpu=available[0],predicted_peak_RAM_bytes=1024)
  def resources(self,spec,*args):
   resource_calls.append(spec['cohort'])
   if len(resource_calls)==1:raise RuntimeError('RESOURCE_HOLD_CPU_PRECLAIM')
   if len(resource_calls)==3:raise RuntimeError('RESOURCE_HOLD_CPU_POSTCLAIM')
   if LATCH_IO and len(resource_calls)==6:raise ValueError('MOCK_UNEXPECTED_WITH_DIAGNOSTIC_IO_FAILURE')
   return dict(physical_RAM_pass=True,physical_disk_pass=True,admission_disk_pass=True,admission_pressure_pass=True)
 res=Res()
 def finish(c):
  path=root/'analysis'/(c+'.RESULT.json')
  if path.exists():return m.rd(path)
  archive_active[0]+=1;archive_active[1]=max(archive_active)
  time.sleep(.005);value=dict(state='PASS_CONTROLLED_ORACLE_DH_STRICT_ARCHIVE_NATIVE_RESTORE',MOCK_NOT_SCIENCE=True,uuid=q['consumed'][c]['uuid']);put(path,value);finishes.append(c);archive_active[0]-=1
  if q['remaining']==0 and all((root/'analysis'/(c+'.RESULT.json')).exists()for c in names):put(base/'control/POOL_STOP_NEW.json',dict(MOCK_NOT_SCIENCE=True))
  return value
 ctx=dict(root=root,request=q['request'],plan=plan,e=e,res=res,consumer=types.SimpleNamespace(safe_finish=finish),points=[dict(cohort=c,mode='OFF_MATCHED')for c in names],cool={},errors={})
 state=dict(lock=threading.RLock(),thread_ident=None,contexts={str(root):ctx},claims={q['request']+':MOCK_OLD':dict(request=q['request'],cohort='MOCK_OLD',host_cpu=cpus[0],uuid='MOCK_UUID_OLD')})
 import __main__
 setattr(__main__,engine.MARKER,state)
 def work(ctx,c):
  with qlock:
   assert c not in q['consumed'];workcalls.append(c);q['remaining']-=1;q['consumed'][c]=dict(uuid='MOCK_UUID_'+c);pidbind(c,'MOCK_UUID_'+c)
  time.sleep(.015)
  with qlock:close(c)
  return dict(state='EXECUTION_CLOSED')
 def old_complete():
  time.sleep(.04)
  with qlock:close('MOCK_OLD')
 oldthread=threading.Thread(target=old_complete,name='MOCK_EXISTING_FRONTEND');oldthread.start()
 # Extract and run the ACTUAL B fresh/harvest/cycle helpers, not equivalents.
 ap=next(x for x in ast.parse(P.read_text()).body if isinstance(x,ast.FunctionDef)and x.name=='apply')
 helpers=[copy.deepcopy(x)for tr in ap.body if isinstance(tr,ast.Try)for x in tr.body if isinstance(x,ast.FunctionDef)and x.name in ['fresh','harvest','cycle_error']]
 assert{x.name for x in helpers}=={'fresh','harvest','cycle_error'}
 def diagnostic_put(path,value,*args):
  if LATCH_IO and(str(path).endswith('.CYCLE_ERROR.json')or Path(path).name=='ENGINEERING_PAUSE_NEW.json'):
   raise OSError('MOCK_DIAGNOSTIC_DIRECTORY_UNWRITABLE')
  return put(path,value,*args)
 henv=dict(m.__dict__,BASE=base,generation_root=generation_root,generation='MOCK_GENERATION',put=diagnostic_put,state=state)
 exec(compile(ast.fix_missing_locations(ast.Module(body=helpers,type_ignores=[])),str(P)+':ACTUAL_CPU_HELPERS','exec'),henv)
 def fresh(ctx,spec,postclaim):
  v=henv['fresh'](ctx,spec,postclaim)
  if v is None:ctx['cool'][spec['cohort']]=time.monotonic()+.005 # CPU cadence only
  return v
 def sync(ctx,claims):
  sync_calls.append(len(claims))
  if len(sync_calls)==1:raise RuntimeError('REGISTRY_SHARED_LOCK_BUSY')
  return dict(MOCK_NOT_SCIENCE=True)
 tree=ast.parse(source);loop=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='run_scheduler')
 for i,node in enumerate(loop.body):
  if isinstance(node,ast.FunctionDef)and node.name in ['work','review']:
   loop.body[i]=ast.parse('def '+node.name+'(ctx,c):\n return _CPU_'+node.name.upper()+'(ctx,c)').body[0]
 # Only science/reviewer backend functions changed. Scheduler source is actual.
 tree=ast.fix_missing_locations(tree)
 ops=types.ModuleType('MOCK_B_DERIVED_LOOP');ops.__file__=str(root/'tools/oracle_ops.py');exec(compile(tree,str(P)+':ACTUAL_LOOP_WITH_MOCK_BACKENDS','exec'),ops.__dict__)
 heldpath=base/'control/SHARED.lock';held=heldpath.open('a+b');fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);st=os.fstat(held.fileno());fdrow=dict(device=st.st_dev,inode=st.st_ino,target=str(heldpath))
 @contextlib.contextmanager
 def inherited_scope(state):yield held.fileno()
 controlled_stop=[False]
 def cpu_sleep(seconds):
  if LATCH_IO and state.get('B_admission_paused_in_memory')and len(finishes)==2 and q['remaining']==1:
   raise MockHealthyDrained()
  time.sleep(min(seconds,.01))
 clock=types.SimpleNamespace(monotonic=time.monotonic,time_ns=time.time_ns,sleep=cpu_sleep)
 ops.__dict__.update(BASE=base,R=root,_C_execution_root=root,_C_owner_pid=os.getpid(),_C_owner_start=1,_C_request=engine.REQUEST,owner=lambda:None,time=clock,put=put,sync_stage_reservation=sync,
  _CPU_WORK=work,_CPU_REVIEW=lambda *a:dict(MOCK_NOT_SCIENCE=True),_B_generation_root=generation_root,_B_generation='MOCK_GENERATION',
  _B_inherited_shared_scope=inherited_scope,_B_verify_shared_scope=lambda state,fd:m.shared_fd_verify(fd,fdrow),
  _B_reconcile_inherited_claims=lambda *a:None,_B_resource=fresh,_B_harvest=henv['harvest'],_B_cycle_error=henv['cycle_error'],
  _B_closed_receipt=m.closed_receipt,_B_unused_identity=m.unused_identity,_B_launch_phase_ready=m.launch_phase_ready,
  _B_cleanup=lambda running,post,reviews:m.cleanup_unused_claims(state,running,post,reviews,henv['cycle_error']))
 def mock_choose(resource,*args,**kwargs):
  value=resource.choose_dispatch(*args,**kwargs)
  if value is not None:value['RSS_history_snapshot_sha256']='MOCK_NO_SCIENCE_HISTORY'
  return value
 ops._B_refresh_RSS_history=lambda *args:None # independent exact-history CPU fixtures cover adapter, no science IO here
 ops._B_choose_with_RSS_history=mock_choose
 def run_loop():
  try:ops.run_scheduler()
  except MockHealthyDrained:controlled_stop[0]=True
 worker=threading.Thread(target=run_loop,name='MOCK_B_LOOP');worker.start();worker.join(10);oldthread.join(1)
 if LATCH_IO:
  check('ACTUAL_DERIVED_LOOP_DRAINS_HEALTHY_WORK_BEFORE_CPU_HARNESS_STOP',controlled_stop[0]and not worker.is_alive())
  check('UNEXPECTED_ERROR_MEMORY_LATCH_SET_BEFORE_FAILED_LOGS',state.get('B_admission_paused_in_memory')is True and state.get('B_diagnostic_IO_errors',0)>=2)
  check('NO_PAUSE_FILE_AVAILABLE_IN_FAULT_CASE',not(base/'control/ENGINEERING_PAUSE_NEW.json').exists())
  check('NO_FURTHER_MODEL_ADMISSION_WITHOUT_PAUSE_FILE',len(workcalls)==1 and q['remaining']==1 and q['budget']==3)
  check('OLD_AND_HEALTHY_NEW_MODEL_ARCHIVES_CONTINUE',len(finishes)==2 and'MOCK_OLD'in finishes)
  check('SOLE_ARCHIVE_WORKER_STILL_ONE',archive_active[1]==1)
  check('SHARED_OFD_RETAINED_DURING_LOGGING_FAILURE',bool(m.shared_fd_verify(held.fileno(),fdrow)))
  held.close()
  report=dict(status='PASS'if all(x['status']=='PASS'for x in checks)else'FAIL',source_sha256=m.sha(P),checks=checks,
    actual_scientific_models_started=0,actual_requests_registered=0,actual_owner_or_tracer_actions=0,
    all_identifiers_are_explicit_MOCK_NOT_SCIENCE=True,work_calls=workcalls,finish_calls=finishes)
  Path(__file__).with_name('ACTUAL_DERIVED_LOOP_LOG_IO_LATCH_QUALIFICATION.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
  print(json.dumps(report,indent=2));raise SystemExit(0 if report['status']=='PASS'else 1)
 check('ACTUAL_DERIVED_LOOP_RETURNS_WITHOUT_NATIVE_MODEL',not worker.is_alive())
 check('OLD_CONSUMED_UUID_NEVER_RESTARTED','MOCK_OLD'not in workcalls and q['consumed']['MOCK_OLD']['uuid']=='MOCK_UUID_OLD')
 check('ONLY_TWO_UNUSED_CPU_IDENTITIES_ONCE',sorted(workcalls)==['MOCK_A','MOCK_B']and q['budget']==3 and q['remaining']==0)
 check('ALL_THREE_MOCK_CLOSED_BACKLOG_CONSUMED_ONCE',sorted(finishes)==sorted(names) and len(finishes)==len(set(finishes)))
 check('SINGLE_ARCHIVE_WORKER',archive_active[1]==1)
 check('PRE_POST_TYPED_RESOURCE_HOLDS_BOTH_EXERCISED',len(resource_calls)>=6)
 check('INITIAL_BUSY_QSYNC_RETRIED_WITHOUT_TPE_UNWIND',len(sync_calls)>1)
 check('NO_CLAIM_STUCK_AND_PENDING_SYNC_CLEARED',not state['claims']and not state.get('B_reservation_sync_pending'))
 check('INHERITED_SHARED_OFD_STILL_LOCKED',bool(m.shared_fd_verify(held.fileno(),fdrow)))
 # Actual helper errors are isolated after loop; never turn into science results.
 class Future:
  def done(self):return True
  def result(self):raise ValueError('MOCK_CPU_FUTURE_FAILURE')
 f=Future();mapping={f:(ctx,'MOCK_A')};value=henv['harvest'](f,mapping,ctx,'MOCK_A','POST')
 check('POST_FUTURE_EXCEPTION_REMOVED_FROM_BUSY',value is None and not mapping)
 check('UNEXPECTED_ERROR_PAUSES_ONLY_NEW_ADMISSION',(base/'control/ENGINEERING_PAUSE_NEW.json').exists())
 # One uncertain INTENT must not prevent independent unused cleanup.
 put(root/'control/qualification_ledger/MOCK_UNCERTAIN.INTENT.json',dict(MOCK_NOT_SCIENCE=True))
 state['claims']={'bad':dict(request=q['request'],cohort='MOCK_UNCERTAIN'),'good':dict(request=q['request'],cohort='MOCK_UNUSED')};errs=[]
 m.cleanup_unused_claims(state,{}, {}, {},errs.append)
 check('UNCERTAIN_INTENT_RETAINED_OTHER_UNUSED_CLAIM_CLEANED','bad'in state['claims']and'good'not in state['claims']and bool(errs))
 state['claims'].clear();state['B_reservation_sync_pending']=True;tries=[0]
 def busy_save():
  tries[0]+=1
  if tries[0]==1:raise RuntimeError('REGISTRY_SHARED_LOCK_BUSY')
  state['B_reservation_sync_pending']=False
 state['saveclaims']=busy_save;m.cleanup_unused_claims(state,{}, {}, {},errs.append);m.cleanup_unused_claims(state,{}, {}, {},errs.append)
 check('PENDING_QSYNC_RETRIED_WITHOUT_ANOTHER_MODEL_RETURN',tries[0]==2 and not state['B_reservation_sync_pending'])
 check('RESOURCE_HOLD_CLASSIFICATION_NARROW',m.resource_hold(RuntimeError('RESOURCE_HOLD_CPU'))and not m.resource_hold(ValueError('RESOURCE_HOLD'))and not m.resource_hold(RuntimeError('IDENTITY_ERROR')))
 q['consumed']['MOCK_A'].pop('execution_receipt')
 check('FINISHED_UNCLOSED_FRONTEND_PREVENTS_NEXT_LAUNCH',reject(lambda:m.launch_phase_ready({f:(ctx,'MOCK_A')})))
 held.close()
 report=dict(status='PASS'if all(x['status']=='PASS'for x in checks)else'FAIL',source_sha256=m.sha(P),
   transformed_source_sha256=hashlib.sha256(source.encode()).hexdigest(),checks=checks,
   actual_scientific_models_started=0,actual_requests_registered=0,actual_reviewer_children=0,
   actual_owner_operations=0,mock_work_calls=workcalls,mock_finish_calls=finishes,
   all_identifiers_are_explicit_MOCK_NOT_SCIENCE=True)
 out=Path(__file__).with_name('ACTUAL_DERIVED_LOOP_CPU_QUALIFICATION.json')
 out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print(json.dumps(report,indent=2))
 if report['status']!='PASS':raise SystemExit(1)
