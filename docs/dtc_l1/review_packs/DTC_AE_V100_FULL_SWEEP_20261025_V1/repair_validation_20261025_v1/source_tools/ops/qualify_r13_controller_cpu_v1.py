"""Independent zero-model CPU qualification of frozen R13 source.

All main-loop workers/authority/entry/claims/DONE files in tests are temporary
fixture metadata; no simulator binary, process, live ledger or entry is touched.
"""
import ast,copy,hashlib,importlib.util,json,os,pathlib,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops';R=F/'validation';T=P('/root/data/dtc_main_v100_sweep_20261025_v1');CONT=O/'sweep_controller.py';FRONT=O/'original_frontend_observer_v1.py';EXPECTED='3c75d688788076bcb9f9cbd66ce6478a198d1569f8b7779b2a7c043c09555e96'
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha(CONT)==EXPECTED
def module(path,name):
 import sys;sys.dont_write_bytecode=True;s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,o):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o))
def safe_top(path):
 a=ast.parse(path.read_text());bad=[]
 for n in a.body:
  if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef)):continue
  if isinstance(n,ast.Expr) and isinstance(n.value,ast.Constant):continue
  if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and '__name__' in ast.unparse(n.test):continue
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   for x in ast.walk(n):
    if isinstance(x,ast.Call) and ast.unparse(x.func) not in ['P','pathlib.Path']:bad.append(ast.unparse(x))
   continue
  bad.append(ast.unparse(n))
 assert not bad,bad
safe_top(CONT);safe_top(FRONT);c=module(CONT,'independent_R13_cpu_controller');f=module(FRONT,'independent_R13_cpu_frontend');checks=['AST_proves_controller_and_original_frontend_imports_have_no_model_or_native_entry_calls']
with tempfile.TemporaryDirectory(prefix='R13_HELPER_CPU_',dir=O) as td:
 root=P(td);q={'admitted_specs':{x:'SHA' for x in ['C','A','B','D','E','F']},'consumed':{'D':{}},'sealed':['E']}
 for cell,insn in [('A',2),('B',1),('C',1),('F',0)]:put(root/'control/specs'/(cell+'.json'),{'expected':{'instructions':insn}})
 assert c.admit_order(q,root,{'A':{}},{'F':11},10)==['B','C']
 assert c.admit_order(q,root,{'A':{}},{'F':11},11,{'B'})==['F','C']
 ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);assert c.live({'pid':os.getpid(),'start_ticks':ticks});assert not c.live({'pid':os.getpid(),'start_ticks':ticks+1});assert not c.live({'pid':999999999,'start_ticks':0})
 assert c.safe_call(lambda _:(_ for _ in ()).throw(RuntimeError('fixture')),'C')['model_retries']==0
checks+=['admit_order_excludes_consumed_sealed_claimed_cooldown_blocked_and_sorts_shortest_then_stable_ID','live_identity_requires_real_PID_start_generation_and_non_zombie','safe_call_preserves_unknown_errors_without_model_retry']

class Boundary(Exception):pass
def scenario(kind):
 with tempfile.TemporaryDirectory(prefix='R13_MAIN_'+kind+'_',dir=O) as td:
  m=module(CONT,'r13_cpu_'+kind);tmp=P(td);orig=tmp/'original';rep=tmp/'repair';nat=tmp/'native';opsdir=tmp/'ops'
  m.T,m.R,m.N,m.O=orig,rep,nat,opsdir
  for root in [orig,rep]:
   for sub in ['control','logs','analysis','DTC/run/results','control/qualification_ledger']: (root/sub).mkdir(parents=True,exist_ok=True)
   put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
  (nat/'control/qualification_ledger').mkdir(parents=True);(nat/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').write_bytes(b'');(nat/'bin').mkdir();opsdir.mkdir()
  entry=nat/'bin/native';entry.write_text('# CPU fixture entry only\n'+str(orig/'tools/sweep_frontend_host_v4.py')+'\n');entry.chmod(0o700)
  exc=['E2-AEV100-85700545918390d7-DM','E2-AEV100-e7c791ce2e4b09ee-DM'];consumed={x:{'uuid':'fixture_exception_'+str(i)} for i,x in enumerate(exc)};old_live=16 if kind=='caps' else 0;fresh_count=70 if kind=='caps' else 1;original_cells=[];initial_claims={}
  for i in range(old_live):
   cell='LIVE_'+str(i);original_cells.append(cell);row={'uuid':'fixture_live_'+str(i)};consumed[cell]=row;initial_claims[cell]={'host_cpu':64+i,'result_cap_bytes':2**20,'RAM_cap_bytes':16*2**30};put(orig/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks})
  original_cells+=['ORIG_'+str(i) for i in range(fresh_count)];repair_cells=['REPAIR_'+str(i) for i in range(23)]
  def spec(cell,request):return {'cohort':cell,'request':request,'expected':{'instructions':1+len(cell)},'limits':{'max_result_directory_bytes':2**20,'max_process_tree_rss_bytes':16*2**30}}
  for cell in original_cells:put(orig/'control'/(cell+'_SPEC.json'),spec(cell,m.ORIGINAL))
  for cell in repair_cells:put(rep/'control/specs'/(cell+'.json'),spec(cell,m.REPAIR))
  oq={'admitted_specs':{x:'fixture' for x in original_cells+exc},'consumed':consumed,'sealed':[],'budget':356,'remaining':356-len(consumed),'reserved_write_bytes':1<<40,'orchestrator_sha256':'retired'};reg={'registered_future_requests':{m.ORIGINAL:oq},'old_history':{'unchanged':True}};epoch={'epoch':2}
  candidate={'budget':23,'remaining':23,'consumed':{},'orchestrator_sha256':sha(CONT),'admitted_specs':{x:'fixture' for x in repair_cells},'sealed':[],'reserved_write_bytes':1<<30}
  put(rep/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',candidate);put(rep/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',{'fixture':True});put(rep/'control/SCIENCE_AUTHORIZATION.json',{'explicit_user_approval':True,'approval_request_sha256':m.sha(rep/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'budgets':{x:1 for x in repair_cells}});put(orig/'control/BATCH_LEASE.json',{'pid':999999999,'start_ticks':0});put(orig/'control/HOST_EXECUTION_PLAN_V4.json',{'model_CPUs':list(range(64,144))});put(opsdir/'OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json',{'fixture_only':True})
  qpath=opsdir/'R13_ZERO_MODEL_QUALIFICATION_V1.json';put(qpath,{'status':'PASS','controller_sha256':sha(CONT),'source_pins':[{'path':str(CONT),'sha256':sha(CONT)}],'reviewed_original_engineering_issues':exc,'prior_entry_sha256':sha(entry)});put(opsdir/'R13_PUBLICATION_READBACK_V1.json',{'verified':True,'controller_sha256':sha(CONT),'qualification_sha256':sha(qpath),'commit':'CPU_FIXTURE_NOT_A_PUBLICATION'})
  put(orig/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':initial_claims});attempts={};events=[];futures=[];registrations=[];maxima={m.ORIGINAL:old_live,m.REPAIR:0};time_calls=[0];guard_claims=[]
  def record_done(k,cell):
   root=orig if k==m.ORIGINAL else rep;q=reg['registered_future_requests'][k];row=q['consumed'][cell];row['execution_receipt']={'fixture_only':True};put(root/'control/qualification_ledger'/(cell+'.DONE.json'),{'fixture_only':True})
  def evidence(k,cell):
   state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' if k==m.ORIGINAL else 'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'
   if k==m.REPAIR and cell=='REPAIR_0' and kind=='repair_archived_failure':state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'
   if k==m.REPAIR and cell=='REPAIR_0' and kind=='repair_engineering_spent':state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
   return {'state':state,'cohort':cell,'fixture_only':True}
  def worker(k,cell):
   attempts[(k,cell)]=attempts.get((k,cell),0)+1
   if kind=='blocked' and k==m.ORIGINAL:return {'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'model_retries':0}
   if kind=='repair_blocked' and k==m.REPAIR and cell=='REPAIR_0':return {'state':'REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'model_retries':0}
   q=reg['registered_future_requests'][k];q['consumed'][cell]={'uuid':'fixture_'+cell};q['remaining']-=1;root=orig if k==m.ORIGINAL else rep
   if kind=='guardian' and k==m.ORIGINAL:
    put(root/'DTC/run/results'/q['consumed'][cell]['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks});return {'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'model_retries':0}
   record_done(k,cell);return evidence(k,cell)
  def update(mutator):
   before=copy.deepcopy(reg);mutator(reg);assert reg['old_history']==before['old_history'];assert reg['registered_future_requests'][m.ORIGINAL]['consumed']==before['registered_future_requests'][m.ORIGINAL]['consumed'];assert reg['registered_future_requests'][m.REPAIR]['budget']==23;registrations.append(True)
  n=types.SimpleNamespace(read_current_authority=lambda:(reg,epoch),update_authority=update,resources=lambda *a:{'physical_disk_pass':True,'physical_RAM_pass':True,'native_free_bytes':1<<50,'required_free_bytes':1<<20},spec_for=lambda cell:json.loads((orig/'control'/(cell+'_SPEC.json')).read_text()))
  closures=[]
  def close_update(mutator):
   before=copy.deepcopy(reg);mutator(reg);assert reg['registered_future_requests'][m.ORIGINAL]==before['registered_future_requests'][m.ORIGINAL];assert reg['old_history']==before['old_history'];assert reg['registered_future_requests'][m.REPAIR]['remaining']==0 and reg['registered_future_requests'][m.REPAIR]['reserved_write_bytes']==2**30;closures.append(True)
  rn=types.SimpleNamespace(registered=lambda:True,plan=lambda:{'allowed_model_CPUs':list(range(144,167))},spec_for=lambda cell:json.loads((rep/'control/specs'/(cell+'.json')).read_text()),resources=lambda *a:{'physical_disk_pass':kind!='resources','physical_RAM_pass':kind!='resources'},output_cap=lambda s:s['limits']['max_result_directory_bytes'],update_authority=close_update)
  old=types.SimpleNamespace(OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE'},finish_evidence=lambda cell:evidence(m.ORIGINAL,cell),run_cell=lambda cell:worker(m.ORIGINAL,cell));rops=types.SimpleNamespace(run_cell=lambda cell:worker(m.REPAIR,cell),finish_evidence=lambda cell:evidence(m.REPAIR,cell));host=types.SimpleNamespace(install=lambda native:native)
  def fake_load(name,path):
   path=str(path)
   if path.endswith('revision12b/sweep_controller.py'):return old
   if path.endswith('sweep_native_cap1m.py'):return n
   if path.endswith('repair_native_v1.py'):return rn
   if path.endswith('repair_ops_v1.py'):return rops
   if path.endswith('sweep_host_execution_v4.py'):return host
   raise AssertionError(path)
  class Future:
   def __init__(self,value,k,cell):self.value=value;self.k=k;self.cell=cell;self.ready=False
   def done(self):return self.ready
   def result(self):assert self.ready;return self.value
  class Pool:
   def __init__(self,max_workers):assert max_workers==72
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def submit(self,fn,underlying,cell):
    if underlying.__name__=='adopt':record_done(m.ORIGINAL,cell);value=evidence(m.ORIGINAL,cell);k=m.ORIGINAL
    else:
     value=fn(underlying,cell);k=m.REPAIR if cell.startswith('REPAIR_') else m.ORIGINAL
    obj=Future(value,k,cell);futures.append(obj);return obj
  def sleep(seconds):
   time_calls[0]+=1
   if kind=='guardian' and seconds==5:
    for cell in original_cells:
     if cell in reg['registered_future_requests'][m.ORIGINAL]['consumed']:record_done(m.ORIGINAL,cell)
   for obj in futures:obj.ready=True
   # Main's reservations represent queued/running workers; inspect the
   # actual source-written claims rather than a mirrored admission formula.
   for k,root in [(m.ORIGINAL,orig),(m.REPAIR,rep)]:
    claims=json.loads((root/'control/POOL_DISPATCH_RESERVATIONS.json').read_text())['claims'];maxima[k]=max(maxima[k],len(claims));assert len(claims)<=(40 if k==m.ORIGINAL else 23)
   oc=json.loads((orig/'control/POOL_DISPATCH_RESERVATIONS.json').read_text())['claims'];rc=json.loads((rep/'control/POOL_DISPATCH_RESERVATIONS.json').read_text())['claims'];cpus=[x['host_cpu'] for x in [*oc.values(),*rc.values()]];assert len(cpus)==len(set(cpus))
   if kind in ['resources','blocked','repair_blocked'] and time_calls[0]>=3:raise Boundary(kind)
   assert time_calls[0]<100,'fixture main unexpectedly never converged'
  real_event=m.event
  def event(state,**kw):
   events.append((state,kw))
   if state=='ENGINEERING_GUARD_RETAIN_CLAIM_AND_SLOT':
    root=orig if kw['request']==m.ORIGINAL else rep;assert kw['cohort'] in json.loads((root/'control/POOL_DISPATCH_RESERVATIONS.json').read_text())['claims'];guard_claims.append(True)
  m.load=fake_load;m.concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Pool));m.time=types.SimpleNamespace(monotonic=lambda:time_calls[0]*10,time=lambda:time_calls[0]*10,sleep=sleep);m.event=event
  boundary=False
  try:m.main()
  except Boundary:boundary=True
  assert registrations==[True];assert entry.read_text().count(str(rep/'tools/repair_frontend_v1.py'))==1;assert str(orig/'tools/sweep_frontend_host_v4.py') not in entry.read_text()
  if kind=='caps':
   assert maxima=={m.ORIGINAL:40,m.REPAIR:23},maxima;assert all(v==1 for v in attempts.values());assert len(attempts)==fresh_count+23
   assert json.loads((rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').read_text())['status']=='ALL23_CORRECTNESS_VALIDATION_PASS'
   count=len(attempts)
   try:m.main();raise AssertionError('one-shot did not reject')
   except AssertionError as e:assert 'one-shot' in str(e)
   assert len(attempts)==count
  elif kind=='resources':assert boundary and not attempts
  elif kind=='blocked':
   assert boundary and attempts[(m.ORIGINAL,original_cells[-1])]==1
   state=json.loads((rep/'analysis/BATCH_STATE_R13.json').read_text());assert original_cells[-1] in state['blocked_engineering_cells'][m.ORIGINAL]
   assert not (rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').exists() or len(reg['registered_future_requests'][m.REPAIR]['consumed'])==23
  elif kind=='guardian':assert guard_claims and all(v==1 for v in attempts.values())
  elif kind=='repair_blocked':assert boundary and attempts[(m.REPAIR,'REPAIR_0')]==1 and len(reg['registered_future_requests'][m.REPAIR]['consumed'])==22 and not closures and not (rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').exists()
  elif kind=='repair_archived_failure':assert closures==[True] and json.loads((rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').read_text())['status']=='VALIDATION_CLOSED_WITH_ARCHIVED_FAILURES'
  elif kind=='repair_engineering_spent':assert not closures and len(reg['registered_future_requests'][m.REPAIR]['consumed'])==23 and not (rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').exists()
  if kind in ['caps','guardian','repair_archived_failure']:assert closures==[True]
  return {'scenario':kind,'max_claims_original':maxima[m.ORIGINAL],'max_claims_repair':maxima[m.REPAIR],'actual_fake_worker_invocations':len(attempts),'retained_live_guard_claim_events':len(guard_claims),'one_shot_rejected':kind=='caps','closed_repair_authority_updates':len(closures),'CPU_fixture_only':True,'real_model_starts':0}
scenarios=[scenario(k) for k in ['caps','resources','blocked','guardian','repair_blocked','repair_archived_failure','repair_engineering_spent']]
checks+=['actual_main_mock_run_adopts16_live_generations_then_reaches_original40_and_independent_repair23','serialized_source_written_claims_never_exceed_each_scope_cap_and_CPU_pools_never_collide','registration_mutator_preserves_all_original_spent_rows_and_old_history','source_entry_switch_is_exact_one_route_replacement_in_temporary_tree_only','resource_false_prevents_all_fresh_dispatches','non_resource_pre_INTENT_errors_are_blocked_and_never_resubmitted','post_INTENT_worker_error_retains_actual_live_generation_claim_and_slot_until_guard_receipt','repair_closed_marker_requires_all23_consumed_and_DONE_with_exact_success_states','archived_repair_failure_closes_with_failure_status_never_all_PASS','spent_engineering_error_and_preINTENT_blocked_never_close_or_release_repair_capacity','repair_close_changes_only_own_q_and_retains_oneGiB_metadata_floor_without_refund','controller_one_shot_rejects_second_start_before_worker_or_mutation']

# Execute the actual nested guardian body with a missing identity: the first
# polling sleep must be reached, never the model-gone terminal branch.
tree=ast.parse(CONT.read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main');guard=next(n for n in main.body if isinstance(n,ast.FunctionDef) and n.name=='guard_actual_attempt')
with tempfile.TemporaryDirectory(prefix='R13_GUARD_UNKNOWN_',dir=O) as td:
 root=P(td);g={'roots':{'K':root},'n':types.SimpleNamespace(read_current_authority=lambda:({'registered_future_requests':{'K':{'consumed':{'C':{'uuid':'unknown_fixture'}}}}},{})),'P':P,'live':lambda x:False,'read':lambda p:json.loads(P(p).read_text()),'time':types.SimpleNamespace(sleep=lambda s:(_ for _ in ()).throw(Boundary('unknown remains guarded')))}
 exec(compile(ast.Module(body=[guard],type_ignores=[]),str(CONT),'exec'),g)
 try:g['guard_actual_attempt']('K','C');raise AssertionError('unknown identity falsely released')
 except Boundary:pass
checks.append('actual_nested_guard_treats_missing_PID_after_INTENT_as_unknown_and_keeps_polling_without_releasing')

# Original route differential: preserved prefix and unrelated commands fall
# through; only future original cells receive host+observer installation.
calls=[];native=types.SimpleNamespace(COHORTS={'NEW':'DTC','OLD':'DTC'},prepare=lambda cell:('prepared',cell),finish_cell=lambda cell:('run',cell));host=types.SimpleNamespace(plan=lambda n:({}, {'preserved_prefix_cells':['OLD']}),install=lambda n:(calls.append('host') or n));observer=types.SimpleNamespace(install=lambda n:(calls.append('observer') or n));fallback=types.SimpleNamespace(main=lambda argv:('fallback',argv))
f.load=lambda name,path:native if str(path).endswith('sweep_native_cap1m.py') else host if str(path).endswith('sweep_host_execution_v4.py') else observer if str(path).endswith('observer_exit_race_v1.py') else fallback
assert f.main(['experiment','prepare','NEW'])==('prepared','NEW') and calls==['host','observer'];calls.clear();assert f.main(['experiment','run-native','NEW'])==('run','NEW') and calls==['host','observer'];calls.clear();assert f.main(['experiment','run-native','OLD'])[0]=='fallback' and not calls;assert f.main(['result','archive','NEW'])[0]=='fallback' and not calls
checks.append('original_frontend_wraps_future_original_prepare_and_run_only_and_preserves_prefix_result_and_unrelated_routes')
assert sha(CONT)==EXPECTED
o={'schema':'R13_INDEPENDENT_ZERO_MODEL_CPU_DRIVER_RESULT_V1','status':'PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controller_sha256':EXPECTED,'original_frontend_sha256':sha(FRONT),'qualification_driver_sha256':sha(__file__),'checks':checks,'check_count':len(checks),'main_mock_scenarios':scenarios,'scientific_simulator_starts':0,'real_native_entry_changes':0,'real_authority_writes':0,'real_process_signals':0,'real_historical_receipts_created':0,'scope':'Main was executed only with isolated temporary filesystem and mocked authority/workers/resources. Temporary fixture DONE records are not scientific artifacts and never touch native authority or result directories.'}
path=O/'R13_CPU_DRIVER_RESULT_V1.json'
with path.open('x') as out:json.dump(o,out,indent=2);out.write('\n')
print(json.dumps(o,indent=2))
