"""Actual R18 main in isolated scopes; no real authority, entry, worker or signal."""
import pathlib,types,tempfile,json,copy,hashlib,importlib.util,os,datetime,ast
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision18';CONT=D/'sweep_controller.py';EXPECTED='b7c302aff28712729efc4c06d5744e8cd184c115a069b2536c52b2cba45e6b31';PRIOR='62993baf0d7e1a21de76628a1219287206229fe8c8e67123773396886977eea2'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def put(p,x):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
def load():
 s=importlib.util.spec_from_file_location('independent_r18_main',CONT);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert sha(CONT)==EXPECTED;ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);scenarios=[]
class Boundary(Exception):pass
def scenario(kind):
 with tempfile.TemporaryDirectory(prefix='R18_MAIN_'+kind+'_',dir=D) as td:
  m=load();top=P(td);m.T=top/'orig';m.R=top/'lava';m.L=top/'late';m.OLD_ROOT=top/'old23';m.N=top/'native';m.O=top/'ops';roots={m.ORIGINAL:m.T,m.REPAIR:m.R,m.LATE:m.L}
  for root in [*roots.values(),m.OLD_ROOT]:
   for sub in ['control','analysis','logs','control/qualification_ledger','DTC/run/results']:(root/sub).mkdir(parents=True,exist_ok=True)
   put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{}})
  (m.N/'control/qualification_ledger').mkdir(parents=True);(m.N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').touch();(m.N/'bin').mkdir();m.O.mkdir();entry=m.N/'bin/native';entry_before='prefix\n'+str(m.O/'revision17/frontend_v1.py')+'\nunchanged old route tail\n';entry.write_text(entry_before)
  exc=['GHOST_A','GHOST_B','GHOST_C'];neg='E2-AEV100-769e6d9fd5f9cd53-CH';rows={m.ORIGINAL:{c:{'uuid':'ghost-'+c} for c in exc},m.REPAIR:{},m.LATE:{}};rows[m.ORIGINAL][neg]={'uuid':'reviewed-negative','execution_receipt':{'CPU_FIXTURE_ONLY':True}}
  fresh={m.ORIGINAL:['ORIG_'+str(i) for i in range(70 if kind=='caps' else 3 if kind=='priority_order' else 1)],m.REPAIR:['LAVA_0','LAVA_1'],m.LATE:['LATE_0','LATE_1','LATE_2','LATE_3']};claims={k:{} for k in roots};adopted={k:[] for k in roots}
  if kind in ['caps','adopt3','benign_receipt']:
   counts={m.ORIGINAL:16 if kind=='caps' else 1,m.REPAIR:1,m.LATE:1}
   for k,count in counts.items():
    for i in range(count):
     c='LIVE_'+k+'_'+str(i);rows[k][c]={'uuid':'uid-'+c};adopted[k].append(c);claims[k][c]={'host_cpu':(64 if k==m.ORIGINAL else 224 if k==m.REPAIR else 144)+i};put(roots[k]/'DTC/run/results'/rows[k][c]['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',{'pid':os.getpid(),'start_ticks':ticks})
    if k!=m.ORIGINAL:fresh[k]=fresh[k][count:]
  put(m.O/'revision18/SHORT_FIRST_DISPATCH_POLICY_V1.json',{'points':{c:{'short':True,'estimated_seconds':len(c)}for c in fresh[m.ORIGINAL]}})
  if kind=='long_gated':put(m.O/'revision18/SHORT_FIRST_DISPATCH_POLICY_V1.json',{'points':{c:{'short':False,'estimated_seconds':999999}for c in fresh[m.ORIGINAL]}})
  if kind=='priority_order':put(m.O/'revision18/SHORT_FIRST_DISPATCH_POLICY_V1.json',{'points':{'ORIG_0':{'short':False,'estimated_seconds':999999},'ORIG_1':{'short':True,'estimated_seconds':200},'ORIG_2':{'short':True,'estimated_seconds':100}}})
  hold='HISTORICAL_HOLD';budgets={m.ORIGINAL:288,m.REPAIR:2,m.LATE:4};reg={'registered_future_requests':{},'old_history':['KEEP']}
  for k,root in roots.items():
   allcells=[*fresh[k],*rows[k]]+([hold] if k==m.ORIGINAL else [])
   for c in allcells:put(root/'control'/((c+'_SPEC.json') if k==m.ORIGINAL else 'specs/'+c+'.json'),dict(cohort=c,request=k,expected={'instructions':len(c)},limits={'max_result_directory_bytes':256*2**20,'max_process_tree_rss_bytes':(128 if k==m.REPAIR else 16)*2**30}))
   q=dict(admitted_specs={c:'SHA_FIXTURE' for c in allcells},consumed=rows[k],budget=budgets[k],remaining=budgets[k]-len(rows[k]),sealed=[hold] if k==m.ORIGINAL else [],state='RUNNING',reserved_write_bytes=1<<40,orchestrator_sha256=PRIOR)
   reg['registered_future_requests'][k]=q;put(root/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims[k]})
  oldrows={c:{'uuid':'old-'+str(i)} for i,c in enumerate(['OLD23_'+str(i) for i in range(23)])};oldclaims={}
  for i,(c,row) in enumerate(oldrows.items()):
   put(m.OLD_ROOT/'DTC/run/results'/row['uuid']/'NATIVE_LAUNCH.json',{'CPU_FIXTURE_ONLY':True})
   if i<19:row['execution_receipt']={'CPU_FIXTURE_ONLY':True}
   else:oldclaims[c]={'host_cpu':160+i-19}
  put(m.OLD_ROOT/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':oldclaims});put(m.OLD_ROOT/'control/EXECUTION_PLAN_V1.json',{'allowed_model_CPUs':list(range(160,224))});oldq=dict(budget=23,remaining=0,consumed=oldrows,state='RUNNING',reserved_write_bytes=3*2**30,orchestrator_sha256='R14_KEPT',execution_plan_sha256=sha(m.OLD_ROOT/'control/EXECUTION_PLAN_V1.json'));reg['registered_future_requests'][m.OLD_REPAIR]=oldq;oldq0=copy.deepcopy(oldq);oldfiles={str(p):p.read_bytes() for p in m.OLD_ROOT.rglob('*') if p.is_file()}
  canonical=m.T/'analysis'/(neg+'.RESULT.json');put(canonical,{'state':'ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS','CPU_FIXTURE_ONLY':True});put(m.T/'control/qualification_ledger'/(neg+'.DONE.json'),{'CPU_FIXTURE_ONLY':True});archive={'CPU_FIXTURE_ONLY':True};put(m.T/'control'/(neg+'_ARCHIVE_RECEIPT.json'),archive);np=m.O/'negative.json';put(np,dict(cohort=neg,uuid='reviewed-negative',state='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY',accepted_cycles=None,scientific_acceptance=False,old_RESULT_preserved=True,old_RESULT_sha256=sha(canonical),DONE_sha256=sha(m.T/'control/qualification_ledger'/(neg+'.DONE.json')),archive={'receipt':archive}));negative_before=canonical.read_bytes()
  cert=m.O/'revision17/THREE_DEPARTED_ORIGINAL_RAM_CERTIFICATE_V1.json';put(cert,{'CPU_FIXTURE_ONLY':True});manifest=m.O/'revision18/OPERATIONAL_PARENT_BRIDGE_MANIFEST_V1.json';mapping={'actual_parent_path':str(CONT.resolve()),'actual_parent_sha256':EXPECTED,'scientific_parent_lineage_sha256':PRIOR,'requests':{k:{'authorized_future_cohorts':list(reg['registered_future_requests'][k]['admitted_specs'])} for k in [m.REPAIR,m.LATE]}};put(manifest,mapping);put(m.O/'revision18/operational_parent_bridge_v1.py',{'CPU_FIXTURE_ONLY':True})
  put(m.T/'control/BATCH_LEASE.json',dict(pid=999999999,start_ticks=0,controller_sha256=PRIOR));put(m.T/'control/HOST_EXECUTION_PLAN_V4.json',{'model_CPUs':list(range(64,144))});qp=m.O/'R18_ZERO_MODEL_QUALIFICATION_V1.json';put(qp,dict(status='PASS',controller_sha256=EXPECTED,source_pins=[{'path':str(CONT),'sha256':EXPECTED}],prior_controller_sha256=PRIOR,prior_entry_sha256=sha(entry),short_priority_policy_sha256=sha(m.O/'revision18/SHORT_FIRST_DISPATCH_POLICY_V1.json'),departed_generation_certificate_sha256=sha(cert),reviewed_original_engineering_issues=exc,reviewed_original_closed_negative={neg:{'path':str(np),'sha256':sha(np)}}));put(m.O/'R18_PUBLICATION_READBACK_V1.json',dict(verified=True,controller_sha256=EXPECTED,qualification_sha256=sha(qp),commit='CPU_FIXTURE_ONLY'))
  if kind=='wrong_entry_SHA':entry.write_text('UNEXPECTED_ENTRY_BYTES')
  if kind=='wrong_entry_route':
   entry.write_text('NO_EXPECTED_ROUTE');qualification=read(qp);qualification['prior_entry_sha256']=sha(entry);put(qp,qualification);publication=read(m.O/'R18_PUBLICATION_READBACK_V1.json');publication['qualification_sha256']=sha(qp);put(m.O/'R18_PUBLICATION_READBACK_V1.json',publication)
  initial_entry_bytes=entry.read_bytes()
  if kind=='unknown_claim':claims[m.LATE]['UNCONSUMED_UNKNOWN']={'host_cpu':145};put(m.L/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':claims[m.LATE]})
  attempts={};futures=[];loops=[0];dispatch=[];dispatch_cells=[];parent_resource_calls=[];native_resource_calls=[];activations=[];closed=[];guarded=[];maximum={k:len(v) for k,v in claims.items()};original_snapshot=copy.deepcopy(reg['registered_future_requests'][m.ORIGINAL])
  def evidence(k,c):
   state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE' if k==m.ORIGINAL else 'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'
   if kind=='archived_failure' and k==m.LATE and c==fresh[k][0]:state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'
   if kind=='engineering_spent' and k==m.LATE and c==fresh[k][0]:state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
   return dict(state=state,cohort=c,accepted_cycles=None,model_retries=0)
  def done(k,c):reg['registered_future_requests'][k]['consumed'][c]['execution_receipt']={'CPU_FIXTURE_ONLY':True};put(roots[k]/'control/qualification_ledger'/(c+'.DONE.json'),{'CPU_FIXTURE_ONLY':True})
  def worker(k,c):
   attempts[(k,c)]=attempts.get((k,c),0)+1;q=reg['registered_future_requests'][k]
   if kind=='defer' and k==m.LATE and c==fresh[k][0] and attempts[(k,c)]==1:return dict(state='REPAIR_ADMISSION_DEFERRED_ZERO_START',cohort=c)
   if kind=='blocked_lava' and k==m.REPAIR:return dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,model_retries=0)
   q['consumed'][c]={'uuid':'new-'+c};q['remaining']-=1
   if kind in ['unknown_after_INTENT','guardian'] and k==m.LATE and c==fresh[k][0]:return dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c,model_retries=0)
   done(k,c);return evidence(k,c)
  def activate(fn):
   if kind=='benign_receipt':done(m.ORIGINAL,adopted[m.ORIGINAL][0])
   if kind=='spent_identity_drift':reg['registered_future_requests'][m.ORIGINAL]['consumed'][exc[0]]['uuid']='CHANGED'
   before=copy.deepcopy(reg);fn(reg)
   for k in roots:
    after=reg['registered_future_requests'][k];assert after['consumed']==before['registered_future_requests'][k]['consumed'] and after['remaining']==before['registered_future_requests'][k]['remaining'] and after['budget']==before['registered_future_requests'][k]['budget'] and after['sealed']==before['registered_future_requests'][k]['sealed'] and after['orchestrator_sha256']==EXPECTED
    if k!=m.ORIGINAL:
     cr=after['operational_parent_continuations'][0];assert cr['actual_parent_pid']==os.getpid() and cr['actual_parent_start_ticks']==ticks and cr['actual_parent_qualification_fd']>=0 and set(cr['consumed_prefix_UUIDs'])==set(before['registered_future_requests'][k]['consumed']) and set(cr['effective_future_cohorts'])==set(fresh[k])
   assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0 and reg['old_history']==before['old_history'];activations.append(True)
  def native_resources(s,*a):native_resource_calls.append(s['cohort']);return dict(physical_RAM_pass=kind!='native_guard_hold',physical_disk_pass=True)
  n=types.SimpleNamespace(read_current_authority=lambda:(reg,{'epoch':2}),update_authority=activate,resources=native_resources,spec_for=lambda c:read(m.T/'control'/(c+'_SPEC.json')))
  def close(fn):
   before=copy.deepcopy(reg);fn(reg);assert reg['registered_future_requests'][m.ORIGINAL]==before['registered_future_requests'][m.ORIGINAL] and reg['registered_future_requests'][m.OLD_REPAIR]==oldq0;closed.extend(k for k in [m.REPAIR,m.LATE] if reg['registered_future_requests'][k]!=before['registered_future_requests'][k])
  def resources(s,*a):
   k=s['request'];allow=not(kind in ['resources','long_gated'] and k==m.REPAIR) and not(kind=='priority' and k==m.REPAIR and loops[0]<2)
   if kind=='one_lava' and k==m.REPAIR:allow=len(read(m.R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'])<1
   return dict(physical_RAM_pass=allow,physical_disk_pass=allow and not(kind=='original_disk_hold' and k==m.ORIGINAL))
  cpus={m.REPAIR:list(range(224,256)),m.LATE:list(range(144,160))}
  engines={k:types.SimpleNamespace(registered=lambda:True,plan=lambda k=k:{'allowed_model_CPUs':cpus[k]},spec_for=lambda c,k=k:read(roots[k]/'control/specs'/(c+'.json')),resources=resources,output_cap=lambda s:s['limits']['max_result_directory_bytes'],update_authority=close) for k in [m.REPAIR,m.LATE]}
  def wrapped(original,authority,certificate_path,certificate_sha256):
   assert sha(certificate_path)==certificate_sha256
   def f(s,*a):parent_resource_calls.append(s['request']);assert s['request']==m.ORIGINAL;return original(s,*a)
   return f
  ram=types.SimpleNamespace(ALLOWED={c:'ghost-'+c for c in exc},make_wrapper=wrapped,verified_departed=lambda reg,c:({x:'ghost-'+x for x in exc},[] if kind!='invalid_ghost' else [{'reason':'unknown'}]))
  bridge=types.SimpleNamespace(MANIFEST=manifest,manifest=lambda:mapping,run_cell=lambda k,c:worker(k,c),finish_evidence=lambda k,c:evidence(k,c))
  old=types.SimpleNamespace(OK={'PASS_STRICT_ARCHIVE_NATIVE_RESTORE'},finish_evidence=lambda c:evidence(m.ORIGINAL,c),run_cell=lambda c:worker(m.ORIGINAL,c))
  def fake_load(name,path):
   f=P(path).name
   if f=='sweep_controller.py':return old
   if f=='sweep_native_cap1m.py':return n
   if f=='sweep_host_execution_v4.py':return types.SimpleNamespace(install=lambda x:x)
   return {'lavamem_native_v2.py':engines[m.REPAIR],'late_native_v1.py':engines[m.LATE],'operational_parent_bridge_v1.py':bridge,'admission_resource_adapter_v1.py':ram}[f]
  class Future:
   def __init__(self,v,k,c):self.value=v;self.k=k;self.c=c;self.ready=False
   def done(self):return self.ready
   def result(self):return self.value
  class Pool:
   def __init__(self,max_workers):assert max_workers==72
   def __enter__(self):return self
   def __exit__(self,*args):return False
   def submit(self,fn,underlying,c):
    k=next((k for k in roots if c in fresh[k] or c in adopted[k]),m.ORIGINAL)
    if c in adopted[k]:
     if 'execution_receipt' not in reg['registered_future_requests'][k]['consumed'][c]:done(k,c)
     value=evidence(k,c)
    elif (k,c) in attempts and c in reg['registered_future_requests'][k]['consumed'] and 'execution_receipt' not in reg['registered_future_requests'][k]['consumed'][c]:
     guarded.append((k,c))
     if kind=='unknown_after_INTENT':value=dict(state='ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c)
     else:done(k,c);value=evidence(k,c)
    else:value=fn(underlying,c)
    result=Future(value,k,c);futures.append(result);return result
  def sleep(_):
   loops[0]+=1
   for f in futures:f.ready=True
   for k,root in roots.items():maximum[k]=max(maximum[k],len(read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']));assert maximum[k]<={m.ORIGINAL:40,m.REPAIR:2,m.LATE:4}[k]
   assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0
   if kind in ['resources','blocked_lava','unknown_after_INTENT','native_guard_hold','original_disk_hold','long_gated'] and loops[0]>=5:raise Boundary()
   assert loops[0]<100
  def event(state,**kw):
   if state=='DISPATCH_FRESH_EXACT_ATTEMPT':dispatch.append(kw['request']);dispatch_cells.append((kw['request'],kw['cohort']))
  m.load=fake_load;m.concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Pool));m.time=types.SimpleNamespace(monotonic=lambda:loops[0]*10,time=lambda:loops[0]*10,sleep=sleep);m.event=event;rejected=False;boundary=False
  try:m.main()
  except Boundary:boundary=True
  except AssertionError:
   if kind in ['unknown_claim','invalid_ghost','spent_identity_drift','wrong_entry_SHA','wrong_entry_route']:rejected=True
   else:raise
  assert reg['registered_future_requests'][m.OLD_REPAIR]==oldq0 and all(P(p).read_bytes()==v for p,v in oldfiles.items()) and canonical.read_bytes()==negative_before
  assert all(c not in [cc for _,cc in attempts] for c in [*exc,neg,*[c for cs in adopted.values() for c in cs]])
  if kind in ['unknown_claim','invalid_ghost','spent_identity_drift','wrong_entry_SHA','wrong_entry_route']:assert rejected and not activations and not attempts and entry.read_bytes()==initial_entry_bytes
  else:
   assert activations==[True] and entry.read_text()==entry_before.replace(str(m.O/'revision17/frontend_v1.py'),str(m.O/'revision18/frontend_v1.py'))
   assert all(v==1 or (kind=='defer' and v==2) for v in attempts.values())
   if kind=='caps':assert maximum=={m.ORIGINAL:40,m.REPAIR:2,m.LATE:4}
   if kind=='adopt3':assert all(adopted.values()) and all('execution_receipt' in reg['registered_future_requests'][k]['consumed'][c] for k,cs in adopted.items() for c in cs)
   if kind=='resources':assert boundary and any(k==m.ORIGINAL for k,c in attempts) and not any(k==m.REPAIR for k,c in attempts)
   if kind in ['native_guard_hold','original_disk_hold','long_gated']:assert boundary and not any(k==m.ORIGINAL for k,c in attempts)
   if kind=='priority_order':assert [c for k,c in dispatch_cells if k==m.ORIGINAL]==['ORIG_2','ORIG_1','ORIG_0']
   if kind=='priority':assert dispatch[0]==m.ORIGINAL and dispatch.index(m.ORIGINAL)<dispatch.index(m.REPAIR)
   if kind=='one_lava':assert maximum[m.REPAIR]==1 and any(k==m.ORIGINAL for k,c in attempts)
   if kind=='blocked_lava':assert boundary and any(k==m.ORIGINAL for k,c in attempts) and m.REPAIR not in closed
   if kind=='unknown_after_INTENT':assert boundary and guarded and attempts[(m.LATE,fresh[m.LATE][0])]==1 and fresh[m.LATE][0] in read(m.L/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   if kind=='guardian':assert guarded
   if kind=='engineering_spent':assert m.LATE not in closed
   if kind=='archived_failure':assert read(m.L/'analysis/VALIDATION_CLOSED_R18.json')['status']=='CLOSED_WITH_ARCHIVED_NATIVE_FAILURES'
   assert set(parent_resource_calls)<={m.ORIGINAL};assert all(c.startswith('ORIG_') for c in native_resource_calls)
  return dict(scenario=kind,status='PASS',max_claims=maximum,new_fake_attempts=len(attempts),continuation_updates=len(activations),old23_q_and_files_unchanged=True,closed_original_negative_and_three_holes_not_restarted=True,real_models_started=0)
for kind in ['caps','adopt3','resources','priority','one_lava','blocked_lava','guardian','unknown_after_INTENT','archived_failure','engineering_spent','defer','benign_receipt','unknown_claim','invalid_ghost','spent_identity_drift','wrong_entry_SHA','wrong_entry_route','native_guard_hold','original_disk_hold','long_gated','priority_order']:scenarios.append(scenario(kind))
assert sha(CONT)==EXPECTED
receipt={'schema':'R18_REAL_MAIN_ISOLATED_CONTINUATION_CPU_QUALIFICATION_V1','status':'PASS','controller_sha256':EXPECTED,'driver_sha256':sha(__file__),'scenario_count':len(scenarios),'main_mock_scenarios':scenarios,'checks':['existing3scope resume preserves budget/remaining/spentUUID/old23 and sealedHOLD','exact real R18 operational lineage/generation record added without new registration','all3scope old live work adopted, never relaunched','original40 lava2 late4 caps enforced','native entry exact prior route replacement only','GESUMMV independently closed negative and3holes preserved with no canonical rewrite','unknown unconsumed claim/uncertain departed evidence reject before continuation','changed spent identity rejected before continuation','benign execution receipt additions retained','zero-start resource defer is not spent retry','unknown postINTENT keeps serialized claim and never relaunches','blocked lava engineering does not starve originals','empirical short original tasks dispatch before large repair and are allowed to backfill; active singleLava allows original fill','newq closes only actual good-result budget/DONE; archived negative distinguished','parent resource adapter only ORIGINAL fresh; nativeV4/runtime calls unmodified','short original backfills when large LAVA RAM admission fails','native original RAM and physical disk gates still reject independently','long original candidates still drain for pending large repair when no large is active','actual empirical runtime order overrides raw instruction count'],'real_registry_or_entry_mutations':0,'real_model_or_component_starts':0,'real_signals':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};out=F/'ops/R18_CPU_DRIVER_RESULT_V1.json'
with out.open('x') as f:json.dump(receipt,f,sort_keys=True,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','scenario_count':len(scenarios),'checks':len(receipt['checks']),'receipt':str(out),'sha256':sha(out),'driver_sha256':sha(__file__)},indent=2))
