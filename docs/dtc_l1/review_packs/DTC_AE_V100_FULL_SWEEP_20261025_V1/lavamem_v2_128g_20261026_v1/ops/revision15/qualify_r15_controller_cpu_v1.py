"""Independent R15 actual-main CPU fixture: no real authority, model, signal or entry actions."""
import ast,copy,hashlib,importlib.util,json,os,pathlib,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops';CONT=O/'revision15/sweep_controller.py';EXPECTED='42fce9797bec4d223b567ee4bbff6726a28e92e70da9632b093a5ee175cc63fe';PRIOR='e33951d0d53677681e422a4e28005327e0b33c4492a1eb7fc02121daa492e413'
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
assert sha(CONT)==EXPECTED
def module(path,name):
 import sys;sys.dont_write_bytecode=True;s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,o):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o))
def safe_top(path):
 a=ast.parse(path.read_text());bad=[]
 for n in a.body:
  if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.AsyncFunctionDef)):continue
  if isinstance(n,ast.Expr)and isinstance(n.value,ast.Constant):continue
  if isinstance(n,ast.If)and isinstance(n.test,ast.Compare)and'__name__'in ast.unparse(n.test):continue
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   bad += [ast.unparse(x)for x in ast.walk(n)if isinstance(x,ast.Call)and ast.unparse(x.func)not in ['P','pathlib.Path']];continue
  bad.append(ast.unparse(n))
 assert not bad,bad
safe_top(CONT);c=module(CONT,'independent_R15_helpers');checks=['AST_import_executes_no_model_authority_entry_or_signal_actions']
ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
with tempfile.TemporaryDirectory(prefix='R15_HELPER_CPU_',dir=O)as td:
 root=P(td);q={'admitted_specs':{x:'SHA'for x in ['A','B','C','D','E','F']},'consumed':{'D':{}},'sealed':['E']}
 for cell,n in [('A',2),('B',1),('C',1),('F',0)]:put(root/'control/specs'/(cell+'.json'),{'expected':{'instructions':n}})
 assert c.admit_order(q,root,{'A':{}},{'F':11},10)==['B','C'];assert c.admit_order(q,root,{'A':{}},{'F':11},11,{'B'})==['F','C']
 assert c.live({'pid':os.getpid(),'start_ticks':ticks})and not c.live({'pid':os.getpid(),'start_ticks':ticks+1})and not c.live({'pid':999999999,'start_ticks':0});assert c.safe_call(lambda _:(_ for _ in()).throw(RuntimeError('fixture')),'X')['model_retries']==0
checks+=['admit_order_respects_consumed_sealed_claims_cooldown_blocked_and_stable_shortest_order','live_requires_actual_generation_non_zombie_and_safe_call_never_retries']
class Boundary(Exception):pass
def scenario(kind):
 with tempfile.TemporaryDirectory(prefix='R15_MAIN_'+kind+'_',dir=O)as td:
  m=module(CONT,'R15_CPU_'+kind);tmp=P(td);orig=tmp/'original';rep=tmp/'new2';oldroot=tmp/'old23';nat=tmp/'native';opsdir=tmp/'ops';m.T,m.R,m.OLD_ROOT,m.N,m.O=orig,rep,oldroot,nat,opsdir
  for root in [orig,rep,oldroot]:
   for sub in ['control','logs','analysis','DTC/run/results','control/qualification_ledger']:(root/sub).mkdir(parents=True,exist_ok=True)
   put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
  (nat/'control/qualification_ledger').mkdir(parents=True);(nat/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').write_bytes(b'');(nat/'bin').mkdir();opsdir.mkdir()
  entry=nat/'bin/native';entry_before='# fixture prefix\n'+str(oldroot/'tools/repair_frontend_v1.py')+'\n# unrelated route remains\n';entry.write_text(entry_before);entry.chmod(0o700)
  exc=['E2-AEV100-85700545918390d7-DM','E2-AEV100-e7c791ce2e4b09ee-DM'];consumed={x:{'uuid':'exception_'+str(i),'charged':1}for i,x in enumerate(exc)};old_live=16 if kind=='caps'else 1 if kind=='benign_receipt'else 0;fresh_count=70 if kind=='caps'else 1;original_cells=[];initial_claims={}
  for i in range(old_live):
   cell='LIVE_'+str(i);original_cells.append(cell);row={'uuid':'fixture_live_'+str(i),'charged':1};consumed[cell]=row;initial_claims[cell]={'host_cpu':64+i,'result_cap_bytes':2**20,'RAM_cap_bytes':16*2**30};put(orig/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks})
  original_cells+=['ORIG_'+str(i)for i in range(fresh_count)];newcells=['E2-AEREPAIR-LAVAMEM2-'+str(i)for i in range(2)]
  def spec(cell,k):return {'cohort':cell,'request':k,'expected':{'instructions':1+len(cell)},'limits':{'max_result_directory_bytes':2**20,'max_process_tree_rss_bytes':(128 if k==m.REPAIR else 16)*2**30}}
  for cell in original_cells:put(orig/'control'/(cell+'_SPEC.json'),spec(cell,m.ORIGINAL))
  for cell in newcells:
   p=rep/'control/specs'/(cell+'.json');put(p,spec(cell,m.REPAIR));alias=rep/'control'/(cell+'_SPEC.json');alias.write_bytes(p.read_bytes())
  oldclaims={};oldrows={}
  for i in range(23):
   cell='OLD23_'+str(i);row={'uuid':'old23_'+str(i),'charged':1};oldrows[cell]=row;out=oldroot/'DTC/run/results'/row['uuid'];put(out/'NATIVE_LAUNCH.json',{'CPU_fixture_only':True})
   if i<15:row['execution_receipt']={'CPU_fixture_only':True};put(oldroot/'control/qualification_ledger'/(cell+'.DONE.json'),{'CPU_fixture_only':True})
   else:put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks});oldclaims[cell]={'host_cpu':160+i-15,'RAM_cap_bytes':16*2**30,'result_cap_bytes':2**20}
  put(oldroot/'control/EXECUTION_PLAN_V1.json',{'allowed_model_CPUs':list(range(160,183))});put(oldroot/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':oldclaims})
  oq={'admitted_specs':{x:'fixture'for x in original_cells+exc},'consumed':consumed,'sealed':[],'budget':356,'remaining':356-len(consumed),'reserved_write_bytes':1<<40,'orchestrator_sha256':PRIOR};oldq={'budget':23,'remaining':0,'consumed':oldrows,'orchestrator_sha256':PRIOR,'reserved_write_bytes':int(8.125*2**30),'execution_plan_sha256':sha(oldroot/'control/EXECUTION_PLAN_V1.json'),'state':'ACTIVE'};reg={'registered_future_requests':{m.ORIGINAL:oq,m.OLD_REPAIR:oldq},'old_history':{'unchanged':True}};oldq_initial=copy.deepcopy(oldq);oldfiles={str(p):p.read_bytes()for p in oldroot.rglob('*')if p.is_file()};epoch={'epoch':2}
  candidate={'budget':2,'remaining':2,'consumed':{},'orchestrator_sha256':sha(CONT),'admitted_specs':{x:sha(rep/'control/specs'/(x+'.json'))for x in newcells},'sealed':[],'reserved_write_bytes':1<<30};put(rep/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',candidate);put(rep/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',{'fixture':True});put(rep/'control/SCIENCE_AUTHORIZATION.json',{'explicit_user_approval':True,'approval_request_sha256':sha(rep/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'budgets':{x:1 for x in newcells}});put(orig/'control/BATCH_LEASE.json',{'pid':999999999,'start_ticks':0,'controller_sha256':PRIOR});put(orig/'control/HOST_EXECUTION_PLAN_V4.json',{'model_CPUs':list(range(64,144))});put(opsdir/'OBSERVER_OLD_ATTEMPTS_FORENSIC_V1.json',{'CPU_fixture_only':True});put(orig/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':initial_claims})
  qp=opsdir/'R15_ZERO_MODEL_QUALIFICATION_V1.json';put(qp,{'status':'PASS','controller_sha256':sha(CONT),'source_pins':[{'path':str(CONT),'sha256':sha(CONT)}],'reviewed_original_engineering_issues':exc,'prior_entry_sha256':sha(entry),'prior_controller_sha256':PRIOR});put(opsdir/'R15_PUBLICATION_READBACK_V1.json',{'verified':True,'controller_sha256':sha(CONT),'qualification_sha256':sha(qp),'commit':'CPU_FIXTURE_ONLY'})
  attempts={};events=[];futures=[];registrations=[];closures=[];time_calls=[0];guard_claims=[];maxima={m.ORIGINAL:old_live,m.REPAIR:0};new_active_seen=[False];original_while_waiting=[]
  def record_done(k,cell):
   root=orig if k==m.ORIGINAL else rep;row=reg['registered_future_requests'][k]['consumed'][cell];row['execution_receipt']={'CPU_fixture_only':True};put(root/'control/qualification_ledger'/(cell+'.DONE.json'),{'CPU_fixture_only':True})
  def evidence(k,cell):
   state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE'if k==m.ORIGINAL else'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'
   if k==m.REPAIR and cell==newcells[0]and kind=='archived_failure':state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'
   if k==m.REPAIR and cell==newcells[0]and kind=='engineering_spent':state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
   return {'state':state,'cohort':cell,'CPU_fixture_only':True}
  def worker(k,cell):
   attempts[(k,cell)]=attempts.get((k,cell),0)+1
   if kind=='blocked_original'and k==m.ORIGINAL:return {'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'model_retries':0}
   if kind=='blocked_new'and k==m.REPAIR:return {'state':'REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'model_retries':0}
   q=reg['registered_future_requests'][k];q['consumed'][cell]={'uuid':'fixture_'+cell,'charged':1};q['remaining']-=1;root=orig if k==m.ORIGINAL else rep
   if (kind=='guardian'and k==m.ORIGINAL)or(kind=='unknown_identity'and k==m.REPAIR):
    if kind=='guardian':put(root/'DTC/run/results'/q['consumed'][cell]['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks})
    return {'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','cohort':cell,'model_retries':0}
   record_done(k,cell);return evidence(k,cell)
  def update(mutator):
   if kind=='benign_receipt'and old_live:
    cell=next(x for x in original_cells if x.startswith('LIVE_'));reg['registered_future_requests'][m.ORIGINAL]['consumed'][cell]['execution_receipt']={'benign_external_receipt':True}
   before=copy.deepcopy(reg)
   mutator(reg);assert reg['old_history']==before['old_history']and reg['registered_future_requests'][m.OLD_REPAIR]==oldq_initial;assert reg['registered_future_requests'][m.REPAIR]==candidate;assert reg['registered_future_requests'][m.ORIGINAL]['consumed']==before['registered_future_requests'][m.ORIGINAL]['consumed']
   expected=copy.deepcopy(before['registered_future_requests'][m.ORIGINAL]);actual=copy.deepcopy(reg['registered_future_requests'][m.ORIGINAL]);expected['orchestrator_sha256']=sha(CONT);actual.pop('operational_continuations',None);expected.pop('operational_continuations',None);assert actual==expected;assert reg['registered_future_requests'][m.REPAIR]['remaining']==2;registrations.append(True)
  n=types.SimpleNamespace(read_current_authority=lambda:(reg,epoch),update_authority=update,resources=lambda *a:{'physical_disk_pass':True,'physical_RAM_pass':True,'native_free_bytes':1<<42,'required_free_bytes':1<<20},spec_for=lambda cell:json.loads((orig/'control'/(cell+'_SPEC.json')).read_text()))
  def close_update(mutator):
   before=copy.deepcopy(reg);mutator(reg);assert reg['registered_future_requests'][m.ORIGINAL]==before['registered_future_requests'][m.ORIGINAL]and reg['registered_future_requests'][m.OLD_REPAIR]==oldq_initial;assert reg['registered_future_requests'][m.REPAIR]['remaining']==0 and reg['registered_future_requests'][m.REPAIR]['reserved_write_bytes']==2**30;closures.append(True)
  def resources(s,*args):
   k=s['request'];pass_=True
   if k==m.REPAIR:
    if kind=='resources':pass_=False
    if kind=='priority'and time_calls[0]<2:pass_=False
    if kind=='one_then_original':pass_=len(json.loads((rep/'control/POOL_DISPATCH_RESERVATIONS.json').read_text())['claims'])<1
   return {'physical_RAM_pass':pass_,'physical_disk_pass':pass_}
  pool_cpus=[160,161]if kind=='collision_plan'else[224,225]
  if kind=='collision_claim':oldclaims[next(iter(oldclaims))]['host_cpu']=224;put(oldroot/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':oldclaims});oldfiles={str(p):p.read_bytes()for p in oldroot.rglob('*')if p.is_file()}
  if kind=='old_plan_SHA':oldq['execution_plan_sha256']='wrong';oldq_initial=copy.deepcopy(oldq)
  rn=types.SimpleNamespace(registered=lambda:True,plan=lambda:{'allowed_model_CPUs':pool_cpus},spec_for=lambda cell:json.loads((rep/'control/specs'/(cell+'.json')).read_text()),resources=resources,output_cap=lambda s:s['limits']['max_result_directory_bytes'],update_authority=close_update)
  old=types.SimpleNamespace(OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE'},finish_evidence=lambda cell:evidence(m.ORIGINAL,cell),run_cell=lambda cell:worker(m.ORIGINAL,cell));rops=types.SimpleNamespace(run_cell=lambda cell:worker(m.REPAIR,cell),finish_evidence=lambda cell:evidence(m.REPAIR,cell));host=types.SimpleNamespace(install=lambda native:native)
  def fake_load(name,path):
   p=str(path)
   if p.endswith('revision12b/sweep_controller.py'):return old
   if p.endswith('sweep_native_cap1m.py'):return n
   if p.endswith('lavamem_native_v2.py'):return rn
   if p.endswith('lavamem_ops_v2.py'):return rops
   if p.endswith('sweep_host_execution_v4.py'):return host
   raise AssertionError(p)
  class Future:
   def __init__(self,value,k,cell):self.value=value;self.k=k;self.cell=cell;self.ready=False
   def done(self):return self.ready
   def result(self):assert self.ready;return self.value
  class Pool:
   def __init__(self,max_workers):assert max_workers==72
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def submit(self,fn,underlying,cell):
    if underlying.__name__=='adopt':
     if 'execution_receipt'not in reg['registered_future_requests'][m.ORIGINAL]['consumed'][cell]:record_done(m.ORIGINAL,cell)
     value=evidence(m.ORIGINAL,cell);k=m.ORIGINAL
    else:value=fn(underlying,cell);k=m.REPAIR if cell.startswith('E2-AEREPAIR-LAVAMEM2-')else m.ORIGINAL
    obj=Future(value,k,cell);futures.append(obj);return obj
  def sleep(seconds):
   time_calls[0]+=1
   if kind in ['guardian','unknown_identity']and seconds==5:
    for k in [m.ORIGINAL,m.REPAIR]:
     for cell in list(reg['registered_future_requests'][k]['consumed']):
      if cell not in exc:record_done(k,cell)
   for obj in futures:obj.ready=True
   for k,root in [(m.ORIGINAL,orig),(m.REPAIR,rep)]:
    claims=load_json(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];maxima[k]=max(maxima[k],len(claims));assert len(claims)<=(40 if k==m.ORIGINAL else 2)
   oc=load_json(orig/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];rc=load_json(rep/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];allcpus=[x['host_cpu']for x in [*oc.values(),*rc.values(),*oldclaims.values()]];assert len(allcpus)==len(set(allcpus))
   assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq_initial
   if kind in ['resources','blocked_original','blocked_new']and time_calls[0]>=4:raise Boundary(kind)
   if kind=='priority'and time_calls[0]<2:assert not attempts
   assert time_calls[0]<100,'CPU fixture did not converge'
  def event(state,**kw):
   events.append((state,kw))
   if state=='DISPATCH_FRESH_EXACT_ATTEMPT'and kw['request']==m.REPAIR:new_active_seen[0]=True
   if state=='DISPATCH_FRESH_EXACT_ATTEMPT'and kw['request']==m.ORIGINAL:
    if not new_active_seen[0]:original_while_waiting.append(kw['cohort'])
   if state=='ENGINEERING_GUARD_RETAIN_CLAIM_AND_SLOT':
    root=orig if kw['request']==m.ORIGINAL else rep;assert kw['cohort']in load_json(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];guard_claims.append(True)
  m.load=fake_load;m.concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Pool));m.time=types.SimpleNamespace(monotonic=lambda:time_calls[0]*10,time=lambda:time_calls[0]*10,sleep=sleep);m.event=event;boundary=False;rejected=False
  try:m.main()
  except Boundary:boundary=True
  except AssertionError:
   if kind in ['collision_plan','collision_claim','old_plan_SHA']:rejected=True
   else:raise
  assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq_initial;assert all(P(p).read_bytes()==b for p,b in oldfiles.items());assert registrations==[True]
  assert entry.read_text()==entry_before.replace(str(oldroot/'tools/repair_frontend_v1.py'),str(rep/'tools/lavamem_frontend_v2.py'))
  lease=load_json(orig/'control/BATCH_LEASE.json');assert lease['additional_requests']==[m.OLD_REPAIR,m.REPAIR]
  if kind in ['collision_plan','collision_claim','old_plan_SHA']:assert rejected and not attempts
  elif kind=='caps':
   assert maxima=={m.ORIGINAL:40,m.REPAIR:2},maxima;assert len(attempts)==fresh_count+2 and all(x==1 for x in attempts.values());assert load_json(rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json')['status']=='ALL2_LAVAMEM_CORRECTNESS_VALIDATION_PASS'
   count=len(attempts)
   try:m.main();raise RuntimeError('one-shot accepted')
   except AssertionError as e:assert'one-shot'in str(e)
   assert len(attempts)==count
  elif kind=='resources':assert boundary and not attempts and not original_while_waiting
  elif kind=='priority':assert not original_while_waiting and attempts[(m.REPAIR,newcells[0])]==1 and attempts[(m.ORIGINAL,original_cells[-1])]==1
  elif kind=='one_then_original':assert attempts[(m.ORIGINAL,original_cells[-1])]==1 and maxima[m.REPAIR]==1
  elif kind=='blocked_original':assert boundary and attempts[(m.ORIGINAL,original_cells[-1])]==1
  elif kind=='blocked_new':assert boundary and all(attempts[(m.REPAIR,x)]==1 for x in newcells)and attempts[(m.ORIGINAL,original_cells[-1])]==1 and not closures
  elif kind in ['guardian','unknown_identity']:assert guard_claims and all(x==1 for x in attempts.values())
  elif kind=='archived_failure':assert closures==[True]and load_json(rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json')['status']=='VALIDATION_CLOSED_WITH_ARCHIVED_FAILURES'
  elif kind=='engineering_spent':assert not closures and len(reg['registered_future_requests'][m.REPAIR]['consumed'])==2 and not(rep/'analysis/REPAIR_VALIDATION_CLOSED_V1.json').exists()
  elif kind=='benign_receipt':assert reg['registered_future_requests'][m.ORIGINAL]['consumed']['LIVE_0']['execution_receipt']=={'benign_external_receipt':True}and attempts[(m.ORIGINAL,'ORIG_0')]==1
  return {'scenario':kind,'max_claims_original':maxima[m.ORIGINAL],'max_claims_new2':maxima[m.REPAIR],'old23_claims_untouched':len(oldclaims),'actual_fake_worker_calls':len(attempts),'old23_q_and_files_unchanged':True,'retained_guard_events':len(guard_claims),'close_updates':len(closures),'entry_exact_one_replacement':True,'CPU_fixture_only':True,'real_models_started':0}
def load_json(p):return json.loads(P(p).read_text())
scenarios=[scenario(k)for k in ['caps','resources','priority','one_then_original','blocked_original','blocked_new','guardian','unknown_identity','archived_failure','engineering_spent','collision_plan','collision_claim','old_plan_SHA','benign_receipt']]
checks+=['actual_main_adopts16_original_generations_and_reaches_original40_plus_independent_new2','registers_exact_two_new_budget_once_without_any_old23_or_original_spent_row_change','old23_all_launched_q_orchestrator_budget_reserved_write_and_files_remain_unchanged','lease_additional_requests_contains_old23_and_new2','entry_changes_exactly_one_old23_router_to_new_router_and_preserves_other_bytes','source_written_claims_respect40_and2_and_do_not_collide_with_old_live_claim_CPUs','large_model_resource_false_suspends_all_new_original_dispatch_without_consuming_attempts','after_one_large_model_starts_original_can_fill_free_slots','resource_recovery_prioritizes_large_model_before_new_original_dispatch','preINTENT_nonresource_new_engineering_blocks_are_not_resubmitted_and_do_not_starve_original','postINTENT_live_and_missing_identity_retain_claim_and_slot_until_benign_receipt_arrives','original_nonresource_engineering_blocks_do_not_retry','new2_close_requires_two_consumed_and_DONE_and_archived_terminal_states','archived_failure_never_reports_all_PASS','spent_engineering_results_never_close_or_release_capacity','close_mutates_only_new2_and_retains_oneGiB_metadata_floor_without_refund','one_shot_rejects_relaunch_before_registration_or_worker','old_plan_SHA_wrong_rejected_before_worker','new_pool_collision_with_old_allowed_pool_or_actual_claim_rejected_before_worker']
# Directly execute the source nested guardian with an absent PID receipt and no
# later execution receipt. Its first poll must occur; model-gone is not inferred.
tree=ast.parse(CONT.read_text());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main');guard=next(n for n in main.body if isinstance(n,ast.FunctionDef)and n.name=='guard_actual_attempt')
with tempfile.TemporaryDirectory(prefix='R15_GUARD_UNKNOWN_',dir=O)as td:
 g={'roots':{'K':P(td)},'n':types.SimpleNamespace(read_current_authority=lambda:({'registered_future_requests':{'K':{'consumed':{'C':{'uuid':'unknown'}}}}},{})),'P':P,'live':lambda x:False,'read':load_json,'time':types.SimpleNamespace(sleep=lambda s:(_ for _ in()).throw(Boundary('still guarded')))};exec(compile(ast.Module(body=[guard],type_ignores=[]),str(CONT),'exec'),g)
 try:g['guard_actual_attempt']('K','C');raise RuntimeError('unknown identity released')
 except Boundary:pass
checks.append('direct_actual_guard_body_keeps_unknown_identity_pending_without_model_gone_completion')
checks.append('original_activation_preserves_a_benign_execution_receipt_added_between_snapshot_and_locked_mutation')
assert sha(CONT)==EXPECTED
result={'schema':'R15_INDEPENDENT_ACTUAL_MAIN_ZERO_MODEL_CPU_RESULT_V1','status':'PASS','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'controller_sha256':EXPECTED,'qualification_driver_sha256':sha(__file__),'checks':checks,'check_count':len(checks),'main_mock_scenarios':scenarios,'scientific_simulator_starts':0,'real_authority_writes':0,'real_entry_changes':0,'real_process_signals':0,'real_historical_receipts_fabricated':0,'scope':'Actual main executes only against private temporary metadata trees and mocked resource/authority/workers. No simulator or original/repair authority process is invoked.','closure_contract_limit':'good union also contains original old.OK. New2 closure scope relies on the pinned lavamem ops contract returning only new2-specific PASS or FAIL_ARCHIVED states; arbitrary injected foreign-scope positive states are not claimed rejected.'};out=O/'R15_CPU_DRIVER_RESULT_V1.json'
with out.open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','check_count':len(checks),'main_scenarios':len(scenarios),'result':str(out),'controller_sha256':EXPECTED,'driver_sha256':sha(__file__)}))
