"""Actual R19 main in isolated fake authority; no real entry, models or signals."""
import pathlib,types,tempfile,json,copy,hashlib,importlib.util,os,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision19';CONT=D/'sweep_controller.py';EXPECTED='c4cc1f48e404f949afb5bfe942044031bfc6650fe6f4032b97757b370f82f532';PRIOR='b7c302aff28712729efc4c06d5744e8cd184c115a069b2536c52b2cba45e6b31'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,x):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
def load():
 s=importlib.util.spec_from_file_location('root_actual_r19_main',CONT);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert sha(CONT)==EXPECTED;ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);scenarios=[]
class Boundary(Exception):pass
def scenario(kind):
 with tempfile.TemporaryDirectory(prefix='R19_MAIN_'+kind+'_',dir=D)as td:
  m=load();top=P(td);m.T=top/'orig';m.R=top/'lava';m.L=top/'late';m.X=top/'remaining';m.OLD_ROOT=top/'old23';m.N=top/'native';m.O=top/'ops';roots={m.ORIGINAL:m.T,m.REPAIR:m.R,m.LATE:m.L,m.EXTRA:m.X};existing=[m.ORIGINAL,m.REPAIR,m.LATE]
  for root in [*roots.values(),m.OLD_ROOT]:
   for sub in ['control','analysis','logs','control/qualification_ledger','DTC/run/results']:(root/sub).mkdir(parents=True,exist_ok=True)
   put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
  (m.N/'control/qualification_ledger').mkdir(parents=True);(m.N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').touch();(m.N/'bin').mkdir();m.O.mkdir();entry=m.N/'bin/native';entry_before='prefix\n'+str(m.O/'revision18/frontend_v1.py')+'\nold route tail\n';entry.write_text(entry_before)
  exc=['GHOST_A','GHOST_B','GHOST_C'];negs=['E2-AEV100-769e6d9fd5f9cd53-CH','E2-AEV100-c885293ad99e21ee-CM','E2-AEV100-c885293ad99e21ee-DH'];rows={k:{}for k in roots};rows[m.ORIGINAL]={c:{'uuid':'ghost-'+c}for c in exc}
  rows[m.ORIGINAL].update({c:{'uuid':'negative-'+str(i),'execution_receipt':{'CPU_FIXTURE_ONLY':True}}for i,c in enumerate(negs)})
  fresh={m.ORIGINAL:['ORIG_'+str(i)for i in range(70 if kind=='caps'else 3 if kind=='priority_order'else 1)],m.REPAIR:['LAVA_0','LAVA_1'],m.LATE:['LATE_'+str(i)for i in range(4)],m.EXTRA:['EXTRA_SMALL_0','EXTRA_SMALL_1','EXTRA_SMALL_2','EXTRA_LAVA']};claims={k:{}for k in roots};adopted={k:[]for k in roots}
  if kind in ['caps','adopt3','benign_receipt']:
   for k,count in {m.ORIGINAL:16 if kind=='caps'else 1,m.REPAIR:1,m.LATE:1}.items():
    for i in range(count):
     c='LIVE_'+k+'_'+str(i);rows[k][c]={'uuid':'uid-'+c};adopted[k].append(c);claims[k][c]={'host_cpu':({m.ORIGINAL:64,m.REPAIR:224,m.LATE:144}[k])+i};put(roots[k]/'DTC/run/results'/rows[k][c]['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks})
    if k!=m.ORIGINAL:fresh[k]=fresh[k][count:]
  longkind=kind in ['long_gated','large_claim','large_intent_no_pid','large_actual_pid'];policy={c:{'short':not longkind,'estimated_seconds':len(c)}for c in fresh[m.ORIGINAL]}
  if kind=='priority_order':policy={'ORIG_0':{'short':False,'estimated_seconds':999999},'ORIG_1':{'short':True,'estimated_seconds':200},'ORIG_2':{'short':True,'estimated_seconds':100}}
  put(m.O/'revision19/SHORT_FIRST_DISPATCH_POLICY_V1.json',{'points':policy});hold='HISTORICAL_HOLD';budgets={m.ORIGINAL:356,m.REPAIR:2,m.LATE:4,m.EXTRA:4};reg={'registered_future_requests':{},'old_history':['KEEP']};qall={}
  for k,root in roots.items():
   allcells=[*fresh[k],*rows[k]]+([hold]if k==m.ORIGINAL else[]);admitted={}
   for c in allcells:
    sp=dict(cohort=c,request=k,expected={'instructions':len(c)},estimated_peak_model_RAM_bytes=(96 if k==m.REPAIR or c=='EXTRA_LAVA'else 4)*2**30,limits={'max_result_directory_bytes':256*2**20,'max_process_tree_rss_bytes':(128 if k==m.REPAIR or c=='EXTRA_LAVA'else 16)*2**30});p=root/'control'/((c+'_SPEC.json')if k==m.ORIGINAL else'specs/'+c+'.json');put(p,sp);admitted[c]=sha(p)
    if k==m.EXTRA:put(root/'control'/(c+'_SPEC.json'),sp);assert sha(root/'control'/(c+'_SPEC.json'))==admitted[c]
   q=dict(admitted_specs=admitted,consumed=rows[k],budget=budgets[k],remaining=budgets[k]-len(rows[k]),sealed=[hold]if k==m.ORIGINAL else[],state='RUNNING',reserved_write_bytes=1<<40,orchestrator_sha256=EXPECTED if k==m.EXTRA else PRIOR);qall[k]=q
   if k!=m.EXTRA:reg['registered_future_requests'][k]=q
   put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims[k]})
  put(m.X/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',qall[m.EXTRA]);put(m.X/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',{'CPU_FIXTURE_ONLY':True});put(m.X/'control/SCIENCE_AUTHORIZATION.json',dict(explicit_user_approval=True,approval_request_sha256=sha(m.X/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),budgets={c:1 for c in fresh[m.EXTRA]}))
  oldrows={'OLD23_'+str(i):{'uuid':'old-'+str(i),'execution_receipt':{'CPU_FIXTURE_ONLY':True}}for i in range(23)};oldclaims={c:{'host_cpu':160+i}for i,c in enumerate(list(oldrows)[-4:])};put(m.OLD_ROOT/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':oldclaims});put(m.OLD_ROOT/'control/EXECUTION_PLAN_V1.json',{'allowed_model_CPUs':list(range(160,224))});oldq=dict(budget=23,remaining=0,consumed=oldrows,state='CLOSED',reserved_write_bytes=3*2**30,orchestrator_sha256='R14_KEPT',execution_plan_sha256=sha(m.OLD_ROOT/'control/EXECUTION_PLAN_V1.json'));reg['registered_future_requests'][m.OLD_REPAIR]=oldq;oldq0=copy.deepcopy(oldq);oldfiles={str(p):p.read_bytes()for p in m.OLD_ROOT.rglob('*')if p.is_file()};negative_before={};negative_pins={}
  for c in negs:
   canonical=m.T/'analysis'/(c+'.RESULT.json');put(canonical,{'state':'RESOLVING_ISSUE_NO_MODEL_RETRY','CPU_FIXTURE_ONLY':True});put(m.T/'control/qualification_ledger'/(c+'.DONE.json'),{'CPU_FIXTURE_ONLY':True});archive={'CPU_FIXTURE_ONLY':True};put(m.T/'control'/(c+'_ARCHIVE_RECEIPT.json'),archive);np=m.O/(c+'.negative.json');put(np,dict(cohort=c,uuid=rows[m.ORIGINAL][c]['uuid'],state='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY',accepted_cycles=None,scientific_acceptance=False,old_RESULT_preserved=True,old_RESULT_sha256=sha(canonical),DONE_sha256=sha(m.T/'control/qualification_ledger'/(c+'.DONE.json')),archive={'receipt':archive}));negative_before[str(canonical)]=canonical.read_bytes();negative_pins[c]=dict(path=str(np),sha256=sha(np))
  cert=m.O/'revision17/THREE_DEPARTED_ORIGINAL_RAM_CERTIFICATE_V1.json';put(cert,{'CPU_FIXTURE_ONLY':True});manifest=m.O/'revision19/OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json';mapping=dict(actual_parent_path=str(CONT.resolve()),actual_parent_sha256=EXPECTED,scientific_parent_lineage_sha256='R16_FIXTURE_LINEAGE',requests={k:{'authorized_future_cohorts':list(qall[k]['admitted_specs'])}for k in[m.REPAIR,m.LATE]});put(manifest,mapping);put(m.O/'revision19/operational_parent_bridge_v1.py',{'CPU_FIXTURE_ONLY':True})
  put(m.T/'control/BATCH_LEASE.json',dict(pid=999999999,start_ticks=0,controller_sha256=PRIOR));put(m.T/'control/HOST_EXECUTION_PLAN_V4.json',{'model_CPUs':list(range(64,144))});qp=m.O/'R19_ZERO_MODEL_QUALIFICATION_V1.json';put(qp,dict(status='PASS',controller_sha256=EXPECTED,source_pins=[dict(path=str(CONT),sha256=EXPECTED)],prior_controller_sha256=PRIOR,prior_entry_sha256=sha(entry),short_priority_policy_sha256=sha(m.O/'revision19/SHORT_FIRST_DISPATCH_POLICY_V1.json'),departed_generation_certificate_sha256=sha(cert),reviewed_original_engineering_issues=exc,reviewed_original_closed_negative=negative_pins));put(m.O/'R19_PUBLICATION_READBACK_V1.json',dict(verified=True,controller_sha256=EXPECTED,qualification_sha256=sha(qp),commit='CPU_FIXTURE_ONLY'))
  if kind=='wrong_entry_SHA':entry.write_text('UNEXPECTED_ENTRY_BYTES')
  if kind=='wrong_entry_route':
   entry.write_text('NO_EXPECTED_ROUTE');q=read(qp);q['prior_entry_sha256']=sha(entry);put(qp,q);pub=read(m.O/'R19_PUBLICATION_READBACK_V1.json');pub['qualification_sha256']=sha(qp);put(m.O/'R19_PUBLICATION_READBACK_V1.json',pub)
  if kind=='unknown_claim':claims[m.EXTRA]['UNKNOWN']={'host_cpu':192};put(m.X/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims[m.EXTRA]})
  if kind=='wrong_candidate':q=read(m.X/'control/REGISTRY_REQUEST_CANDIDATE_V1.json');q['budget']=5;put(m.X/'control/REGISTRY_REQUEST_CANDIDATE_V1.json',q)
  if kind=='wrong_alias':put(m.X/'control'/('EXTRA_LAVA_SPEC.json'),{'wrong':True})
  initial_entry=entry.read_bytes();attempts={};futures=[];loops=[0];dispatch=[];activations=[];closed=[];guarded=[];maximum={k:len(v)for k,v in claims.items()};resource_calls=[];stale_calls=[];runtime_calls=[]
  def evidence(k,c):
   state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE'if k==m.ORIGINAL else'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'
   if kind=='archived_failure'and k==m.EXTRA and c==fresh[k][0]:state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'
   if kind=='engineering_spent'and k==m.EXTRA and c==fresh[k][0]:state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
   return dict(state=state,cohort=c,accepted_cycles=None,model_retries=0)
  def done(k,c):reg['registered_future_requests'][k]['consumed'][c]['execution_receipt']={'CPU_FIXTURE_ONLY':True};put(roots[k]/'control/qualification_ledger'/(c+'.DONE.json'),{'CPU_FIXTURE_ONLY':True})
  def worker(k,c):
   attempts[k,c]=attempts.get((k,c),0)+1;q=reg['registered_future_requests'][k]
   if kind=='defer'and k==m.EXTRA and c==fresh[k][0]and attempts[k,c]==1:return dict(state='REPAIR_ADMISSION_DEFERRED_ZERO_START',cohort=c)
   q['consumed'][c]={'uuid':'new-'+c};q['remaining']-=1
   if kind in ['guardian','unknown_after_INTENT']and k==m.EXTRA and c==fresh[k][0]:return dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,model_retries=0)
   done(k,c);return evidence(k,c)
  def activate(fn):
   if kind=='benign_receipt':done(m.ORIGINAL,adopted[m.ORIGINAL][0])
   if kind=='spent_identity_drift':reg['registered_future_requests'][m.ORIGINAL]['consumed'][exc[0]]['uuid']='CHANGED'
   before=copy.deepcopy(reg);fn(reg)
   for k in existing:
    q=reg['registered_future_requests'][k];b=before['registered_future_requests'][k];assert q['consumed']==b['consumed']and q['remaining']==b['remaining']and q['budget']==b['budget']and q['sealed']==b['sealed']and q['orchestrator_sha256']==EXPECTED
    if k!=m.ORIGINAL:
     cr=q['operational_parent_continuations'][0];assert cr['actual_parent_pid']==os.getpid()and cr['actual_parent_start_ticks']==ticks and cr['actual_parent_qualification_fd']>=0 and set(cr['consumed_prefix_UUIDs'])==set(b['consumed'])and set(cr['effective_future_cohorts'])==set(fresh[k])
   assert reg['registered_future_requests'][m.EXTRA]==qall[m.EXTRA]and reg['registered_future_requests'][m.OLD_REPAIR]==oldq0 and reg['old_history']==before['old_history'];activations.append(True)
  def close(fn):
   before=copy.deepcopy(reg);fn(reg);assert reg['registered_future_requests'][m.ORIGINAL]==before['registered_future_requests'][m.ORIGINAL]and reg['registered_future_requests'][m.OLD_REPAIR]==oldq0;closed.extend(k for k in[m.REPAIR,m.LATE,m.EXTRA]if reg['registered_future_requests'][k]!=before['registered_future_requests'][k])
  def resources(s,*a):
   resource_calls.append(s['cohort']);k=s['request'];allow=not(kind in['resources','long_gated']and(k==m.REPAIR or s['cohort']=='EXTRA_LAVA'))
   return dict(physical_RAM_pass=allow and not(kind=='RAM_hold'and k==m.ORIGINAL),physical_disk_pass=not(kind=='disk_hold'and k==m.ORIGINAL))
  def stale(s,*a):stale_calls.append(s['cohort']);return dict(physical_RAM_pass=False,physical_disk_pass=False)
  n=types.SimpleNamespace(read_current_authority=lambda:(reg,{'epoch':2}),update_authority=activate,resources=stale,spec_for=lambda c:read(m.T/'control'/(c+'_SPEC.json')))
  cpus={m.REPAIR:list(range(224,256)),m.LATE:list(range(144,160)),m.EXTRA:list(range(192,208))}
  engines={k:types.SimpleNamespace(registered=lambda:True,plan=lambda k=k:{'allowed_model_CPUs':cpus[k]},spec_for=lambda c,k=k:read(roots[k]/'control/specs'/(c+'.json')),output_cap=lambda s:s['limits']['max_result_directory_bytes'],update_authority=close)for k in[m.REPAIR,m.LATE,m.EXTRA]};engines[m.EXTRA].verify_cpu_reuse=lambda:True
  ram=types.SimpleNamespace(ALLOWED={c:'ghost-'+c for c in exc},verified_departed=lambda reg,c:({x:'ghost-'+x for x in exc},[]if kind!='invalid_ghost'else[{'reason':'unknown'}]))
  bridge=types.SimpleNamespace(MANIFEST=manifest,manifest=lambda:mapping,run_cell=lambda k,c:worker(k,c),finish_evidence=lambda k,c:evidence(k,c));old=types.SimpleNamespace(OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE'},finish_evidence=lambda c:evidence(m.ORIGINAL,c),run_cell=lambda c:worker(m.ORIGINAL,c))
  def runtime(registry):
   runtime_calls.append(True)
   if kind=='runtime_missing':raise AssertionError('missing actual runtime ACK/sample')
   return dict(status='CPU_FIXTURE_RUNTIME_PROOF_ONLY')
  def fake_load(name,path):
   f=P(path).name
   if f=='sweep_controller.py':return old
   if f=='sweep_native_cap1m.py':return n
   if f=='sweep_host_execution_v4.py':return types.SimpleNamespace(install=lambda x:x)
   return {'lavamem_native_v2.py':engines[m.REPAIR],'late_native_v1.py':engines[m.LATE],'remaining_native_v1.py':engines[m.EXTRA],'remaining_ops_v1.py':types.SimpleNamespace(run_cell=lambda c:worker(m.EXTRA,c),finish_evidence=lambda c:evidence(m.EXTRA,c)),'operational_parent_bridge_v1.py':bridge,'admission_resource_adapter_v1.py':ram,'resource_accounting_v1.py':types.SimpleNamespace(resources=resources),'runtime_resource_override_v1.py':types.SimpleNamespace(require_all_live_original_runtime_corrections=runtime)}[f]
  class Future:
   def __init__(self,v,k,c,held=False):self.value=v;self.k=k;self.c=c;self.ready=False;self.held=held
   def done(self):return self.ready
   def result(self):return self.value
  class Pool:
   def __init__(self,max_workers):assert max_workers==72
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def submit(self,fn,underlying,c):
    k=next((k for k in roots if c in fresh[k]or c in adopted[k]),m.ORIGINAL);held=False
    if kind.startswith('large_')and(k==m.REPAIR or c=='EXTRA_LAVA'):
     held=True;value=None
     if kind!='large_claim':
      q=reg['registered_future_requests'][k];q['consumed'][c]={'uuid':'fixture-prepopen-'+c};q['remaining']-=1
      if kind=='large_actual_pid':put(roots[k]/'DTC/run/results'/q['consumed'][c]['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=os.getpid(),start_ticks=ticks))
    elif c in adopted[k]:
     if 'execution_receipt'not in reg['registered_future_requests'][k]['consumed'][c]:done(k,c)
     value=evidence(k,c)
    elif(k,c)in attempts and c in reg['registered_future_requests'][k]['consumed']and'execution_receipt'not in reg['registered_future_requests'][k]['consumed'][c]:
     guarded.append((k,c))
     if kind=='unknown_after_INTENT':value=dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c)
     else:done(k,c);value=evidence(k,c)
    else:value=fn(underlying,c)
    future=Future(value,k,c,held);futures.append(future);return future
  def sleep(_):
   loops[0]+=1
   for f in futures:
    if not f.held:f.ready=True
   for k,root in roots.items():maximum[k]=max(maximum[k],len(read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']));assert maximum[k]<={m.ORIGINAL:40,m.REPAIR:2,m.LATE:4,m.EXTRA:4}[k]
   assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0
   if(kind in['resources','unknown_after_INTENT','RAM_hold','disk_hold','long_gated']or kind.startswith('large_'))and loops[0]>=5:raise Boundary()
   assert loops[0]<100
  def event(state,**kw):
   if state=='DISPATCH_FRESH_EXACT_ATTEMPT':dispatch.append((kw['request'],kw['cohort']))
  m.load=fake_load;m.concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Pool));m.time=types.SimpleNamespace(monotonic=lambda:loops[0]*10,time=lambda:loops[0]*10,sleep=sleep);m.event=event;rejected=False;boundary=False;rejects=['unknown_claim','invalid_ghost','spent_identity_drift','wrong_entry_SHA','wrong_entry_route','runtime_missing','wrong_candidate','wrong_alias']
  try:m.main()
  except Boundary:boundary=True
  except AssertionError:
   if kind in rejects:rejected=True
   else:raise
  assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0 and all(P(p).read_bytes()==v for p,v in{**oldfiles,**negative_before}.items())
  assert all(c not in[cc for _,cc in attempts]for c in[*exc,*negs,*[c for cs in adopted.values()for c in cs]])
  if kind in rejects:assert rejected and not activations and not attempts and entry.read_bytes()==initial_entry
  else:
   assert activations==[True]and runtime_calls==[True]and entry.read_text()==entry_before.replace(str(m.O/'revision18/frontend_v1.py'),str(m.X/'tools/remaining_frontend_v1.py'))and not stale_calls
   assert all(v==1 or(kind=='defer'and v==2)for v in attempts.values())
   if kind=='caps':assert maximum=={m.ORIGINAL:40,m.REPAIR:2,m.LATE:4,m.EXTRA:4}
   if kind=='adopt3':assert all(adopted[k]for k in existing)
   if kind=='resources':assert boundary and any(k==m.ORIGINAL for k,c in attempts)and not any(k==m.REPAIR for k,c in attempts)
   if kind in['RAM_hold','disk_hold','long_gated','large_claim','large_intent_no_pid']:assert boundary and not any(k==m.ORIGINAL for k,c in attempts)
   if kind=='large_actual_pid':assert boundary and any(k==m.ORIGINAL for k,c in attempts)
   if kind=='priority_order':assert[c for k,c in dispatch if k==m.ORIGINAL]==['ORIG_2','ORIG_1','ORIG_0']
   if kind=='unknown_after_INTENT':assert boundary and guarded and attempts[m.EXTRA,fresh[m.EXTRA][0]]==1 and fresh[m.EXTRA][0]in read(m.X/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   if kind=='guardian':assert guarded
   if kind=='engineering_spent':assert m.EXTRA not in closed
   if kind=='archived_failure':assert read(m.X/'analysis/VALIDATION_CLOSED_R19.json')['status']=='CLOSED_WITH_ARCHIVED_NATIVE_FAILURES'
  return dict(scenario=kind,status='PASS',max_claims=maximum,new_fake_attempts=len(attempts),continuation_updates=len(activations),old23_q_files_and_three_negative_results_unchanged=True,real_scientific_models_started=0)
for k in['caps','adopt3','resources','guardian','unknown_after_INTENT','archived_failure','engineering_spent','defer','benign_receipt','unknown_claim','invalid_ghost','spent_identity_drift','wrong_entry_SHA','wrong_entry_route','RAM_hold','disk_hold','long_gated','priority_order','large_claim','large_intent_no_pid','large_actual_pid','runtime_missing','wrong_candidate','wrong_alias']:scenarios.append(scenario(k))
assert sha(CONT)==EXPECTED
r=dict(schema='R19_REAL_MAIN_ISOLATED_FOUR_SCOPE_CPU_QUALIFICATION_V1',status='PASS',controller_sha256=EXPECTED,driver_sha256=sha(__file__),scenario_count=len(scenarios),main_mock_scenarios=scenarios,real_registry_or_entry_mutations=0,real_scientific_model_starts=0,real_signals=0,checks=['Old three scopes budget/remaining/spent/HOLD immutable; new independent finite4 only','Closed old23 request and four historical claims unchanged; selected extra CPU pool disjoint','40/2/4/4 caps and live work adopted without restart','Three independent negatives and three receipt gaps retain originals and acceptance null','Unknown claims/departed proof/spent UUID/entry/candidate/alias drift rejected','Actual old-live runtime proof required before registration','Unified valid accounting replaces obsolete secondary V4 veto; actual RAM and disk fails still gate','Large claim-only and INTENT-without-PID cannot authorize long-original backfill; real observed PID can','Zero-start defer not consumed retry; unknown postINTENT guardian retains claim','Closure requires finite budget and good full result; archived negative and engineering remain distinct','Short measured runtime priority remains; no original failed generation relaunched'],observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
out=F/'ops/R19_CPU_DRIVER_RESULT_V1.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='PASS',scenario_count=len(scenarios),checks=len(r['checks']),receipt=str(out),sha256=sha(out),driver_sha256=sha(__file__))))
