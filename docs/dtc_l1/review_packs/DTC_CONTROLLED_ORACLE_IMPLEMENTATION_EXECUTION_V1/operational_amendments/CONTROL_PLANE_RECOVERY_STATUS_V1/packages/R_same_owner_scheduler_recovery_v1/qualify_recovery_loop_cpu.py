from pathlib import Path
import types,json,hashlib,threading,time,ast,copy,os,tempfile,traceback
A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_controlled_oracle_implementation_execution_20261106_v1/agents/R_same_owner_scheduler_recovery_v1');p=A/'oracle_scheduler_recovery.py'
m=types.ModuleType('CPU_RECOVERY');m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);startsha=m.sha(p);checks=[]
def check(name,f):
 try:f();checks.append(dict(name=name,status='PASS'))
 except BaseException as e:checks.append(dict(name=name,status='FAIL',error=repr(e),traceback=traceback.format_exc()))
def rejected(fn):
 try:fn()
 except (AssertionError,RuntimeError):return
 raise AssertionError('EXPECTED_FAIL_CLOSED')
source,edits=m.transformed_scheduler(m.OPS.read_text());check('EXACT_18_SOURCE_TRANSFORMS_COMPILE',lambda:exec('assert len(edits)==18'))
check('WRONG_ORIGINAL_SOURCE_REJECTED',lambda:rejected(lambda:m.transformed_scheduler(m.OPS.read_text()+'\n')))
# Actual local functions extracted as AST from install: CPU closures get only
# independent scratch roots and no real registration/owner/module state.
install=next(x for x in ast.parse(p.read_text()).body if isinstance(x,ast.FunctionDef)and x.name=='install')
helpernodes=[copy.deepcopy(n)for n in install.body if isinstance(n,ast.Try) for n in n.body if isinstance(n,ast.FunctionDef)]
assert {n.name for n in helpernodes}=={'event','fresh','cycle_error','harvest'}
O=A/'cpu_fixture_v2';O.mkdir(exist_ok=False)
oldmod=types.ModuleType('CPU_FROZEN_OPS');oldmod.__file__=str(m.OPS);exec(compile(m.OPS.read_bytes(),str(m.OPS),'exec'),oldmod.__dict__)
base=O/'base';root=base/'initial8';(root/'control/specs').mkdir(parents=True);(root/'analysis').mkdir();(root/'control/qualification_ledger').mkdir();(base/'control').mkdir()
PASS=oldmod.PASS
lock=threading.RLock();workcalls=[];finishes=[];resource_calls=[];failures=[];sync_calls=[];postactive=[0,0]
q=dict(request='CPU_ONLY_NOT_SCIENTIFIC',budget=3,remaining=2,consumed={'CPU_OLD':dict(uuid='CPU_UUID_OLD')},admitted_specs={})
specs={c:dict(cohort=c,request=q['request'],workload='CPU_INPUT',native_simulator_argv=['CPU_NOT_A_MODEL'],limits=dict(max_result_directory_bytes=1024,max_process_tree_rss_bytes=2048),program=c)for c in ['CPU_OLD','CPU_A','CPU_B']}
for c,s in specs.items():m.put(root/'control/specs'/(c+'.json'),s)
plan=dict(stage='initial8',qualified_modes=[],initial_qualifiers={},new_dispatcher_cpu_allowance=[min(os.sched_getaffinity(0))],protected_cpu_ids=[],archive_workers=1)
def pidbind(c,uid):
 out=root/'DTC/run/results'/uid;out.mkdir(parents=True,exist_ok=True);intent=dict(uuid=uid,output=str(out),oracle_execution_binding=dict(CPU_ONLY=True,cohort=c))
 m.put(root/'control/qualification_ledger'/(c+'.INTENT.json'),intent)
 m.put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=os.getpid(),start_ticks=1,maps='CPU_NOT_A_MODEL',oracle_execution_binding=intent['oracle_execution_binding']))
 return intent
def close(c):
 uid=q['consumed'][c]['uuid'];intent=json.loads((root/'control/qualification_ledger'/(c+'.INTENT.json')).read_bytes());d=dict(uuid=uid,CPU_ONLY=True)
 q['consumed'][c]['execution_receipt']=d;m.put(root/'control/qualification_ledger'/(c+'.DONE.json'),d);m.put(Path(intent['output'])/'NATIVE_EXIT.json',d)
pidbind('CPU_OLD','CPU_UUID_OLD')
class Engine:
 def registered(self):return {},{},q,plan
 def assert_parent_lease(self):return True
 def canonical(self,c):return copy.deepcopy(specs[c])
 spec_for=canonical
 def jsonsha(self,v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
e=Engine()
class Wait(RuntimeError):pass
class Res:
 WaitInitialRuntimeGate=Wait
 def sample_system(self):return dict(cpu_allowed=plan['new_dispatcher_cpu_allowance']+[min(os.sched_getaffinity(0))+1],observed_affinity_claims=[])
 def admission_hold(self,q,s):return None
 def verify_initial_runtime_gate(self,*args):return dict(CPU_ONLY_GATE=True)
 def verify_mode_extension_receipt(self,*args):raise Wait('CPU_GATE2_NOT_REAL')
 def choose_dispatch(self,pending,sample,claims,**kw):
  used={x['host_cpu']for x in claims.values()};available=[x for x in sample['cpu_allowed']if x not in used]
  if not pending or not available:return None
  return dict(cohort=pending[0]['cohort'],host_cpu=available[0],predicted_peak_RAM_bytes=1024)
 def resources(self,s,admit):
  c=s['cohort'];resource_calls.append(c)
  if len(resource_calls)==1:raise RuntimeError('RESOURCE_HOLD_CPU_PRECLAIM')
  if len(resource_calls)==3:raise RuntimeError('RESOURCE_HOLD_CPU_POSTCLAIM')
  return dict(physical_RAM_pass=True,physical_disk_pass=True,admission_disk_pass=True,admission_pressure_pass=True)
res=Res()
def safe_finish(c):
 rp=root/'analysis'/(c+'.RESULT.json')
 if rp.exists():return json.loads(rp.read_bytes())
 postactive[0]+=1;postactive[1]=max(postactive[1],postactive[0]);time.sleep(.01);v=dict(state=PASS,CPU_ONLY=True,uuid=q['consumed'][c]['uuid']);m.put(rp,v);finishes.append(c);postactive[0]-=1
 if q['remaining']==0 and all((root/'analysis'/(x+'.RESULT.json')).exists()for x in specs):m.put(base/'control/POOL_STOP_NEW.json',dict(CPU_ONLY=True))
 return v
ctx=dict(root=root,request=q['request'],plan=plan,e=e,res=res,consumer=types.SimpleNamespace(safe_finish=safe_finish),points=[dict(cohort=c,mode='OFF_MATCHED',program=c)for c in specs],cool={},errors={})
state=dict(lock=lock,thread_ident=999,contexts={str(root):ctx},claims={},**{m.GENERATION:dict(thread_ident=None,reservation_sync_pending=False)})
# Two CPUs in legal mask permit parallel CPU tasks; no native model command.
plan['new_dispatcher_cpu_allowance']=res.sample_system()['cpu_allowed'];m.put(root/'control/RESOURCE_POLICY.json',{})
setattr(__import__('__main__'),'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1',state)
oldfuture=m.PlainFuture()
def old_cpu_complete():time.sleep(.2);close('CPU_OLD');oldfuture.value=dict(state='EXECUTION_CLOSED');oldfuture.event.set()
threading.Thread(target=old_cpu_complete).start()
def work(ctx,c):
 assert c not in q['consumed'],'CPU_DUPLICATE_CONSUMPTION';workcalls.append(c);q['remaining']-=1;q['consumed'][c]=dict(uuid='CPU_UUID_'+c);pidbind(c,'CPU_UUID_'+c);time.sleep(.15);close(c);return dict(state='EXECUTION_CLOSED')
cap=dict(running={oldfuture:(ctx,'CPU_OLD')},post={},reviews={},dispatch_index=0,original_thread_ident=999,work=work,review=lambda *a:None,held_duplicate=(base/'control/held').open('a+b'))
def sync(ctx,claims):
 sync_calls.append(len(claims))
 if len(sync_calls)==1:raise RuntimeError('REGISTRY_SHARED_LOCK_BUSY')
 return dict(CPU_ONLY=True)
# Actual extracted error/harvest helpers in isolated globals.
helperenv=dict(m.__dict__,BASE=base,root=O/'events');helperenv['root'].mkdir();exec(compile(ast.fix_missing_locations(ast.Module(body=helpernodes,type_ignores=[])),str(p)+':ACTUAL_EXTRACTED_CPU_HELPERS','exec'),helperenv)
def resource(ctx,s,postclaim):
 v=helperenv['fresh'](ctx,s,postclaim)
 if v is None:ctx['cool'][s['cohort']]=time.monotonic()+.01
 return v
rec=dict(cap=cap,generation=m.GENERATION,resource=resource,cycle_error=helperenv['cycle_error'],harvest=helperenv['harvest'],cleanup=lambda running,post,reviews:m.cleanup_orphans(state,running,post,reviews,helperenv['cycle_error']),running_ack=lambda:None)
env=dict(oldmod.__dict__,BASE=base,R=root,owner=lambda:None,_RECOVERY=rec,_PlainPool=m.PlainPool,_closed_receipt=m.closed_receipt,_unused_identity=m.unused_identity,_launch_phase_ready=m.launch_phase_ready,sync_stage_reservation=sync)
# Actual loop's time.sleep cadence remains 2sec. CPU bound task waits are short.
exec(compile(source,str(A/'TRANSFORMED_OPERATIONAL_PREVIEW.py'),'exec'),env)
worker=threading.Thread(target=env['recovery_dispatch_loop']);worker.start();worker.join(25)
check('ACTUAL_TRANSFORMED_LOOP_TERMINATES_NO_MODEL',lambda:exec('assert not worker.is_alive()'))
check('INHERITED_SPENT_UUID_NEVER_RESTARTED',lambda:exec("assert 'CPU_OLD'not in workcalls and q['consumed']['CPU_OLD']['uuid']=='CPU_UUID_OLD'"))
check('ONLY_TWO_UNUSED_IDENTITIES_CONSUMED_ONCE',lambda:exec("assert sorted(workcalls)==['CPU_A','CPU_B']and q['remaining']==0 and q['budget']==3"))
check('ALL_CLOSED_UUIDS_ARCHIVED_ONCE',lambda:exec("assert sorted(finishes)==['CPU_A','CPU_B','CPU_OLD']and len(set(finishes))==3"))
check('SINGLE_ARCHIVE_CONSUMER_WORKER',lambda:exec('assert postactive[1]==1'))
check('PRECLAIM_POSTCLAIM_HOLD_BOTH_DEFERRED',lambda:exec('assert len(resource_calls)>=6'))
check('STARTUP_BUSY_SYNC_DEFERRED_WITHOUT_LOOP_UNWIND',lambda:exec('assert len(sync_calls)>1'))
check('ALL_COMPLETED_CLAIMS_RELEASED_AND_RESYNCED',lambda:exec('assert state[\'claims\']=={}and not state[m.GENERATION][\'reservation_sync_pending\']and sync_calls'))
# Per-future failures pop busy, fail closed, and allow other closed work.
f=m.PlainFuture();f.error=ValueError('CPU_BAD_FUTURE');f.event.set();mapping={f:(ctx,'CPU_A')};check('THROWING_FUTURE_ISOLATED_REMOVED_FROM_BUSY',lambda:exec("assert helperenv['harvest'](f,mapping,ctx,'CPU_A','POST')is None and not mapping"))
check('UNEXPECTED_ERROR_PAUSES_NEW_ADMISSION',lambda:exec("assert(base/'control/ENGINEERING_PAUSE_NEW.json').exists()"))
f=m.PlainFuture();f.value='bad schema';f.event.set();mapping={f:(ctx,'CPU_B')};check('BAD_FUTURE_SCHEMA_REMOVED_FROM_BUSY',lambda:exec("assert helperenv['harvest'](f,mapping,ctx,'CPU_B','POST')is None and not mapping"))
# Uncertain INTENT must retain claim yet not block cleanup of independent rows.
q['admitted_specs']['CPU_UNCERTAIN']='not_science';m.put(root/'control/qualification_ledger/CPU_UNCERTAIN.INTENT.json',dict(CPU_ONLY=True));state['claims']={'bad':dict(request=q['request'],cohort='CPU_UNCERTAIN'),'good':dict(request=q['request'],cohort='CPU_ZERO')};errs=[]
check('UNCERTAIN_INTENT_RETAINED_OTHER_ORPHAN_CLEANED',lambda:exec("assert m.cleanup_orphans(state,{}, {}, {},errs.append)==1 and 'bad'in state['claims']and'good'not in state['claims']and errs"))
# Pending qsync is retried even without another model completion.
state['claims'].clear();state[m.GENERATION]['reservation_sync_pending']=True;oldsave=state['saveclaims'];attempt=[0]
def busy_save():
 attempt[0]+=1
 if attempt[0]==1:raise RuntimeError('REGISTRY_SHARED_LOCK_BUSY')
 state[m.GENERATION]['reservation_sync_pending']=False
state['saveclaims']=busy_save;errs=[];m.cleanup_orphans(state,{}, {}, {},errs.append);m.cleanup_orphans(state,{}, {}, {},errs.append)
check('FAILED_RESERVATION_SYNC_RETRIED_NEXT_TICK',lambda:exec("assert attempt[0]==2 and not state[m.GENERATION]['reservation_sync_pending']and errs"))
# Busy per-claim registry read preserves it, and a later tick clears exactunused.
registered=e.registered;reads=[0]
def busy_registered():
 reads[0]+=1
 if reads[0]==1:raise RuntimeError('REGISTRY_SHARED_LOCK_BUSY')
 return registered()
e.registered=busy_registered;state['claims']={'orphan':dict(request=q['request'],cohort='CPU_ZERO')};m.cleanup_orphans(state,{}, {}, {},errs.append);m.cleanup_orphans(state,{}, {}, {},errs.append)
check('ZERO_START_BUSY_ORPHAN_RETRIED_NOT_STUCK',lambda:exec("assert reads[0]>=2 and not state['claims']"))
e.registered=registered
# Finished frontend with spent but no DONE cannot release the next launch phase.
f=m.PlainFuture();f.value=dict(state='UNRESOLVED_EXECUTION');f.event.set();q['consumed']['CPU_A'].pop('execution_receipt');check('FINISHED_UNCLOSED_FRONTEND_FAIL_CLOSED',lambda:rejected(lambda:m.launch_phase_ready({f:(ctx,'CPU_A')})))
check('RESOURCE_HOLD_CLASSIFICATION_NARROW',lambda:exec("assert m.resource_hold(RuntimeError('RESOURCE_HOLD_CPU'))and not m.resource_hold(AssertionError('source'))and not m.resource_hold(RuntimeError('identity'))"))
check('SOURCE_UNCHANGED_DURING_CPU_TESTS',lambda:exec('assert m.sha(p)==startsha'))
report=dict(status='PASS'if all(x['status']=='PASS'for x in checks)else'FAIL',source_sha256=startsha,checks=checks,actual_owner_installs=0,actual_models_started=0,scientific_requests_registered=0,fixture_only_UUID_strings=True,work_calls=workcalls,finish_calls=finishes)
with(A/'RECOVERY_LOOP_CPU_QUALIFICATION_V2.json').open('x')as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print(json.dumps(report,indent=2))
