"""R16 real-main independent fakeRoot CPU qualification. No live operations."""
import ast,copy,hashlib,importlib.util,json,os,pathlib,tempfile,types,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');O=F/'ops';CONT=O/'revision16/sweep_controller.py';EXPECTED='32ebd671924d4e23eda7960c5957708e5a71f225ceb0887edcbe3249f25f65d3';PRIOR='e33951d0d53677681e422a4e28005327e0b33c4492a1eb7fc02121daa492e413'
sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
def read(p):return json.loads(P(p).read_bytes())
def load():
 s=importlib.util.spec_from_file_location('r16_cpu',CONT);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert sha(CONT)==EXPECTED
ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);checks=[]
class Boundary(Exception):pass
def scenario(kind):
 with tempfile.TemporaryDirectory(prefix='R16_MAIN_'+kind+'_',dir=O) as td:
  m=load();tmp=P(td);orig=tmp/'original';r=tmp/'lava';l=tmp/'late';oldroot=tmp/'old23';nat=tmp/'native';opsdir=tmp/'ops';m.T,m.R,m.L,m.OLD_ROOT,m.N,m.O=orig,r,l,oldroot,nat,opsdir;roots={m.ORIGINAL:orig,m.REPAIR:r,m.LATE:l};budgets={m.REPAIR:2,m.LATE:4}
  for root in [orig,r,l,oldroot]:
   for sub in ['control','logs','analysis','DTC/run/results','control/qualification_ledger']:(root/sub).mkdir(parents=True,exist_ok=True)
   put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
  (nat/'control/qualification_ledger').mkdir(parents=True);(nat/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').touch();(nat/'bin').mkdir();opsdir.mkdir();entry=nat/'bin/native';entry_before='prefix\n'+str(oldroot/'tools/repair_frontend_v1.py')+'\nunchanged-original-fallback\n';entry.write_text(entry_before)
  exc=['E2-AEV100-85700545918390d7-DM','E2-AEV100-e7c791ce2e4b09ee-DM'];consumed={c:{'uuid':'exception-'+str(i)} for i,c in enumerate(exc)};old_live=16 if kind=='caps' else 1 if kind=='benign_receipt' else 0;fresh_count=70 if kind=='caps' else 1;initial_claims={};cells={m.ORIGINAL:[],m.REPAIR:['E2-AEREPAIR-LAVAMEM2-'+str(i) for i in range(2)],m.LATE:['E2-AEREPAIR-LATE4-'+str(i) for i in range(4)]}
  for i in range(old_live):
   c='LIVE_'+str(i);consumed[c]={'uuid':'live-'+str(i)};initial_claims[c]={'host_cpu':64+i};put(orig/'DTC/run/results'/consumed[c]['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks})
  cells[m.ORIGINAL]=['ORIG_'+str(i) for i in range(fresh_count)];hold='HISTORICAL_HOLD'
  def spec(c,k):return dict(cohort=c,request=k,expected={'instructions':len(c)},limits={'max_result_directory_bytes':256*2**20,'max_process_tree_rss_bytes':(128 if k==m.REPAIR else 16)*2**30})
  for k,cs in cells.items():
   for c in cs:
    p=roots[k]/'control'/((c+'_SPEC.json') if k==m.ORIGINAL else ('specs/'+c+'.json'));put(p,spec(c,k))
    if k!=m.ORIGINAL:(roots[k]/'control'/(c+'_SPEC.json')).write_bytes(p.read_bytes())
  oq=dict(admitted_specs={c:'fixture' for c in [*cells[m.ORIGINAL],*consumed,hold]},consumed=consumed,sealed=[hold,*cells[m.ORIGINAL]],budget=288,remaining=288-len(consumed),reserved_write_bytes=1<<40,orchestrator_sha256=PRIOR,state='RUNNING')
  oq['operational_repair_admission_barrier']=dict(status='NEW_ORIGINAL_ADMISSION_PAUSED_FOR_QUALIFIED_REPAIR_SUPPLEMENT',original_sealed=[hold],added_cells=cells[m.ORIGINAL],plan_sha256='b'*64)
  oldrows={};oldclaims={}
  for i in range(23):
   c='OLD23_'+str(i);oldrows[c]={'uuid':'old23-'+str(i)};out=oldroot/'DTC/run/results'/oldrows[c]['uuid'];put(out/'NATIVE_LAUNCH.json',{'CPU_fixture_only':True})
   if i<18:oldrows[c]['execution_receipt']={'CPU_fixture_only':True}
   else:put(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks});oldclaims[c]={'host_cpu':160+i-18}
  put(oldroot/'control/EXECUTION_PLAN_V1.json',{'allowed_model_CPUs':list(range(160,183))});put(oldroot/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':oldclaims})
  oldq=dict(budget=23,remaining=0,consumed=oldrows,state='RUNNING',orchestrator_sha256=PRIOR,reserved_write_bytes=int(3.5*2**30),execution_plan_sha256=sha(oldroot/'control/EXECUTION_PLAN_V1.json'));reg={'registered_future_requests':{m.ORIGINAL:oq,m.OLD_REPAIR:oldq},'history':['preserve']};oldq0=copy.deepcopy(oldq);oldfiles={str(p):p.read_bytes() for p in oldroot.rglob('*') if p.is_file()};original_before=copy.deepcopy(oq)
  candidates={}
  for k in [m.REPAIR,m.LATE]:
   root=roots[k];candidate=dict(budget=budgets[k],remaining=budgets[k],consumed={},sealed=[],orchestrator_sha256=EXPECTED,admitted_specs={c:sha(root/'control/specs'/(c+'.json')) for c in cells[k]},reserved_write_bytes=int((1.5 if k==m.REPAIR else 3)*2**30));candidates[k]=candidate;put(root/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',candidate);put(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',{'CPU_fixture_only':True});put(root/'control/SCIENCE_AUTHORIZATION.json',dict(explicit_user_approval=True,approval_request_sha256=sha(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),budgets={c:1 for c in cells[k]}))
  put(orig/'control/BATCH_LEASE.json',dict(pid=999999999,start_ticks=0,controller_sha256=PRIOR));put(orig/'control/HOST_EXECUTION_PLAN_V4.json',{'model_CPUs':list(range(64,144))});put(orig/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':initial_claims})
  qp=opsdir/'R16_ZERO_MODEL_QUALIFICATION_V1.json';put(qp,dict(status='PASS',controller_sha256=EXPECTED,source_pins=[{'path':str(CONT),'sha256':EXPECTED}],reviewed_original_engineering_issues=exc,prior_entry_sha256=sha(entry),prior_controller_sha256=PRIOR));put(opsdir/'R16_PUBLICATION_READBACK_V1.json',dict(verified=True,controller_sha256=EXPECTED,qualification_sha256=sha(qp),commit='CPU_FIXTURE_ONLY'))
  if kind=='barrier_drift':oq['sealed'].append('UNKNOWN')
  if kind=='barrier_spent':oq['consumed'][cells[m.ORIGINAL][0]]={'uuid':'invalid'}
  if kind=='wrong_alias':(l/'control'/(cells[m.LATE][0]+'_SPEC.json')).write_text('wrong')
  if kind=='oldplan_sha':oldq['execution_plan_sha256']='wrong';oldq0=copy.deepcopy(oldq)
  if kind=='preexisting_zero_start':put(l/'analysis'/(cells[m.LATE][0]+'.RESULT.json'),{'state':'ENGINEERING_ZERO_START','CPU_fixture_only':True})
  attempts={};events=[];futures=[];time_calls=[0];maxima={m.ORIGINAL:old_live,m.REPAIR:0,m.LATE:0};registrations=[];closures=[];guards=[];dispatch=[]
  def evidence(k,c):
   state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' if k==m.ORIGINAL else 'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'
   if kind=='archived_failure' and k==m.LATE and c==cells[k][0]:state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'
   if kind=='engineering_spent' and k==m.LATE and c==cells[k][0]:state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
   return dict(state=state,cohort=c,accepted_cycles=None,model_retries=0)
  def done(k,c):
   reg['registered_future_requests'][k]['consumed'][c]['execution_receipt']={'CPU_fixture_only':True};put(roots[k]/'control/qualification_ledger'/(c+'.DONE.json'),{'CPU_fixture_only':True})
  def worker(k,c):
   attempts[(k,c)]=attempts.get((k,c),0)+1
   if kind=='blocked_new' and k==m.REPAIR:return dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,model_retries=0)
   if kind=='blocked_original' and k==m.ORIGINAL:return dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,model_retries=0)
   q=reg['registered_future_requests'][k];q['consumed'][c]={'uuid':'cpu-'+c};q['remaining']-=1
   if kind=='guardian' and k==m.LATE and c==cells[k][0]:return dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,model_retries=0)
   done(k,c);return evidence(k,c)
  def activate(fn):
   if kind=='benign_receipt':reg['registered_future_requests'][m.ORIGINAL]['consumed']['LIVE_0']['execution_receipt']={'benign_external_receipt':True}
   before=copy.deepcopy(reg);fn(reg);assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0 and reg['history']==before['history'];assert reg['registered_future_requests'][m.ORIGINAL]['consumed']==before['registered_future_requests'][m.ORIGINAL]['consumed'];assert reg['registered_future_requests'][m.ORIGINAL]['remaining']==before['registered_future_requests'][m.ORIGINAL]['remaining'];assert reg['registered_future_requests'][m.ORIGINAL]['sealed']==[hold];assert reg['registered_future_requests'][m.ORIGINAL]['operational_repair_admission_barrier']['status']=='RELEASED_BY_QUALIFIED_R16';assert all(reg['registered_future_requests'][k]==v for k,v in candidates.items());registrations.append(True)
  n=types.SimpleNamespace(read_current_authority=lambda:(reg,{'epoch':2}),update_authority=activate,resources=lambda *a:dict(physical_disk_pass=True,physical_RAM_pass=True,native_free_bytes=1<<44,required_free_bytes=1<<20),spec_for=lambda c:read(orig/'control'/(c+'_SPEC.json')))
  def close(fn):
   before=copy.deepcopy(reg);fn(reg)
   assert reg['registered_future_requests'][m.ORIGINAL]==before['registered_future_requests'][m.ORIGINAL] and reg['registered_future_requests'][m.OLD_REPAIR]==oldq0
   changed=[k for k in [m.REPAIR,m.LATE] if reg['registered_future_requests'][k]!=before['registered_future_requests'][k]];assert len(changed)==1;k=changed[0];assert reg['registered_future_requests'][k]['remaining']==0 and reg['registered_future_requests'][k]['reserved_write_bytes']==2**30;closures.append(k)
  def resources(s,*a):
   k=s['request'];allow=True
   if k==m.REPAIR:
    if kind=='resources':allow=False
    if kind=='priority' and time_calls[0]<2:allow=False
    if kind=='one_lava':allow=len(read(r/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'])<1
   return dict(physical_RAM_pass=allow,physical_disk_pass=allow)
  cpus={m.REPAIR:[224,225],m.LATE:[144,145,146,147]}
  if kind=='collision_old':cpus[m.LATE]=[160]
  if kind=='collision_old_claim':
   oldclaims['OLD23_18']['host_cpu']=144;put(oldroot/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':oldclaims});oldfiles={str(p):p.read_bytes() for p in oldroot.rglob('*') if p.is_file()}
  if kind=='collision_new':cpus[m.LATE]=[224]
  engines={k:types.SimpleNamespace(registered=lambda:True,plan=lambda k=k:{'allowed_model_CPUs':cpus[k]},spec_for=lambda c,k=k:read(roots[k]/'control/specs'/(c+'.json')),resources=resources,output_cap=lambda s:s['limits']['max_result_directory_bytes'],update_authority=close) for k in [m.REPAIR,m.LATE]}
  old=types.SimpleNamespace(OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE'},finish_evidence=lambda c:evidence(m.ORIGINAL,c),run_cell=lambda c:worker(m.ORIGINAL,c));ops={k:types.SimpleNamespace(run_cell=lambda c,k=k:worker(k,c),finish_evidence=lambda c,k=k:evidence(k,c)) for k in [m.REPAIR,m.LATE]}
  def fake_load(name,path):
   name=P(path).name
   if name=='sweep_native_cap1m.py':return n
   if name=='sweep_controller.py':return old
   if name=='sweep_host_execution_v4.py':return types.SimpleNamespace(install=lambda x:x)
   return {'lavamem_native_v2.py':engines[m.REPAIR],'late_native_v1.py':engines[m.LATE],'lavamem_ops_v2.py':ops[m.REPAIR],'late_ops_v1.py':ops[m.LATE]}[name]
  class Future:
   def __init__(self,value,k,c):self.value=value;self.k=k;self.c=c;self.ready=False
   def done(self):return self.ready
   def result(self):return self.value
  class Pool:
   def __init__(self,max_workers):assert max_workers==72
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def submit(self,fn,underlying,c):
    k=next((k for k,cc in cells.items() if c in cc),m.ORIGINAL)
    if c.startswith('LIVE_'):
     if 'execution_receipt' not in reg['registered_future_requests'][k]['consumed'][c]:done(k,c)
     value=evidence(k,c)
    elif (k,c) in attempts and c in reg['registered_future_requests'][k]['consumed'] and 'execution_receipt' not in reg['registered_future_requests'][k]['consumed'][c]:guards.append(True);done(k,c);value=evidence(k,c)
    else:value=fn(underlying,c)
    f=Future(value,k,c);futures.append(f);return f
  def sleep(sec):
   time_calls[0]+=1
   for f in futures:f.ready=True
   for k,root in roots.items():maxima[k]=max(maxima[k],len(read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']));assert maxima[k]<=({m.ORIGINAL:40,m.REPAIR:2,m.LATE:4}[k])
   cc=[x['host_cpu'] for root in [*roots.values(),oldroot] for x in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'].values()];assert len(cc)==len(set(cc));assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0
   if kind in ['resources','blocked_new','blocked_original'] and time_calls[0]>=4:raise Boundary()
   if kind=='priority' and time_calls[0]<2:assert not any(k==m.ORIGINAL for k,c in attempts)
   assert time_calls[0]<100
  def event(state,**kw):
   events.append((state,kw))
   if state=='DISPATCH_FRESH_EXACT_ATTEMPT':dispatch.append(kw['request'])
  m.load=fake_load;m.concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Pool));m.time=types.SimpleNamespace(monotonic=lambda:time_calls[0]*10,time=lambda:time_calls[0]*10,sleep=sleep);m.event=event;rejected=False;boundary=False
  try:m.main()
  except Boundary:boundary=True
  except AssertionError:
   if kind in ['collision_old','collision_old_claim','collision_new','oldplan_sha','barrier_drift','barrier_spent','wrong_alias']:rejected=True
   else:raise
  assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0 and all(P(p).read_bytes()==b for p,b in oldfiles.items())
  if kind in ['barrier_drift','barrier_spent','wrong_alias']:assert rejected and not registrations and not attempts and entry.read_text()==entry_before
  else:
   assert registrations==[True] and entry.read_text()==entry_before.replace(str(oldroot/'tools/repair_frontend_v1.py'),str(l/'tools/late_frontend_v1.py'));assert read(orig/'control/BATCH_LEASE.json')['additional_requests']==[m.OLD_REPAIR,m.REPAIR,m.LATE]
   if kind in ['collision_old','collision_old_claim','collision_new','oldplan_sha']:assert rejected and not attempts
   else:
    assert all(v==1 for v in attempts.values())
    if kind=='caps':
     assert maxima=={m.ORIGINAL:40,m.REPAIR:2,m.LATE:4} and len(attempts)==76
     count=len(attempts)
     try:m.main();raise RuntimeError('one shot accepted')
     except AssertionError as e:assert 'One-shot' in str(e)
     assert len(attempts)==count
    if kind=='resources':assert boundary and not any(k in [m.REPAIR,m.ORIGINAL] for k,c in attempts) and sum(k==m.LATE for k,c in attempts)==4
    if kind=='priority':assert dispatch[:4]==[m.LATE]*4 and dispatch.index(m.REPAIR)<dispatch.index(m.ORIGINAL)
    if kind=='one_lava':assert maxima[m.REPAIR]==1 and any(k==m.ORIGINAL for k,c in attempts)
    if kind=='blocked_new':assert boundary and any(k==m.ORIGINAL for k,c in attempts) and m.REPAIR not in closures
    if kind=='blocked_original':assert boundary and attempts[(m.ORIGINAL,cells[m.ORIGINAL][0])]==1
    if kind=='guardian':assert guards
    if kind=='archived_failure':assert read(l/'analysis/VALIDATION_CLOSED_R16.json')['status']=='CLOSED_WITH_ARCHIVED_NATIVE_FAILURES'
    if kind=='engineering_spent':assert m.LATE not in closures and not (l/'analysis/VALIDATION_CLOSED_R16.json').exists()
    if kind=='preexisting_zero_start':assert (l/'analysis/zero_start_preimages_R16'/(cells[m.LATE][0]+'.RESULT.json')).exists()
    if kind=='benign_receipt':assert reg['registered_future_requests'][m.ORIGINAL]['consumed']['LIVE_0']['execution_receipt']=={'benign_external_receipt':True}
  return dict(scenario=kind,status='PASS',max_claims=maxima,actual_fake_workers=len(attempts),registrations=len(registrations),closures=closures,old23_q_and_files_unchanged=True,real_model_starts=0)
scenarios=[scenario(k) for k in ['caps','resources','priority','one_lava','blocked_new','blocked_original','guardian','archived_failure','engineering_spent','collision_old','collision_old_claim','collision_new','oldplan_sha','barrier_drift','barrier_spent','wrong_alias','benign_receipt','preexisting_zero_start']]
checks=['actual main original40 lava2 late4 with 16 adopted original and five untouched old23 models','registers only exact new2+new4 budgets once','barrier exact original HOLD restoration; qremaining/consumed unchanged','entry exactly replaces R1 router with combined late router; fallback unchanged','lease includes old23 lava2 late4','late4 dispatch may proceed while large RAM waiting; original waits until large active','resource recovery prioritizes large before original','single large active allows original fill','zero-start engineering blocked large does not starve original','claims and slots caps40+2+4; CPUs disjoint old23','unknown postINTENT identity retains claim until subsequent independent receipt','finite closures require all DONE and valid archived terminal results','archived failure not all-PASS; engineering spent not closed','oldplan SHA and CPU collisions rejected before worker','barrier drift/spent/wrong alias rejected before registration','benign concurrent original receipt preserved','preINTENT prior result preserved with exact SHA before unused launch']
tree=ast.parse(CONT.read_text());main=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main');guard=next(x for x in main.body if isinstance(x,ast.FunctionDef) and x.name=='guard')
with tempfile.TemporaryDirectory(prefix='R16_UNKNOWN_GUARD_',dir=O) as td:
 g=dict(roots={'K':P(td)},n=types.SimpleNamespace(read_current_authority=lambda:({'registered_future_requests':{'K':{'consumed':{'C':{'uuid':'unknown'}}}}},{})),P=P,read=read,live=lambda _:False,time=types.SimpleNamespace(sleep=lambda _:(_ for _ in()).throw(Boundary())))
 exec(compile(ast.Module(body=[guard],type_ignores=[]),str(CONT),'exec'),g)
 try:g['guard']('K','C');raise RuntimeError('unknown released')
 except Boundary:pass
checks.append('direct real guardian never infers death from missing identity')
helper=load();assert helper.live({'pid':os.getpid(),'start_ticks':ticks}) and not helper.live({'pid':os.getpid(),'start_ticks':ticks+1}) and not helper.live({'pid':999999999,'start_ticks':0})
checks.append('live identity requires exact PID generation; absent PID does not match')
with tempfile.TemporaryDirectory(prefix='R16_ADMIT_HELPER_',dir=O) as td:
 root=P(td)
 for c,n in [('A',2),('B',1),('C',1),('F',0)]:put(root/'control/specs'/(c+'.json'),{'expected':{'instructions':n}})
 q={'admitted_specs':{c:'sha' for c in ['A','B','C','D','E','F']},'consumed':{'D':{}},'sealed':['E']}
 assert helper.admit_order(q,root,{'A':{}},{'F':11},10)==['B','C'] and helper.admit_order(q,root,{'A':{}},{'F':11},11,{'B'})==['F','C']
checks.append('admit helper respects sealed consumed claim cooldown blocked and stable order')
assert helper.safe_call(lambda _:(_ for _ in()).throw(RuntimeError('CPU')),'C')['model_retries']==0
checks.append('safe call engineering failure never grants automatic retry')
checks.append('actual main one-shot rejects before second registration worker or entry edit')
checks.append('new pool collision with out-of-plan old actual claim rejects before worker')
assert sha(CONT)==EXPECTED
result=dict(schema='R16_INDEPENDENT_ACTUAL_MAIN_CPU_RESULT_V1',status='PASS',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),controller_sha256=EXPECTED,driver_sha256=sha(__file__),checks=checks,check_count=len(checks),main_mock_scenarios=scenarios,scientific_simulator_starts=0,real_authority_writes=0,real_entry_changes=0,real_signals=0,scope='Real main against isolated metadata trees; mocked authority/resources/workers. Capacity-collision checks occur after registration but before workers, matching source order; negative fixture registration is not production authorization.',closure_contract_limit='New2/new4 closure relies on pinned ops returning scoped PASS or FAIL_ARCHIVED states; arbitrary foreign positive states are not claimed rejected.')
out=O/'R16_CPU_DRIVER_RESULT_V1.json'
with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(dict(status='PASS',checks=len(checks),main_scenarios=len(scenarios),result=str(out),source_sha256=EXPECTED,driver_sha256=sha(__file__))))
