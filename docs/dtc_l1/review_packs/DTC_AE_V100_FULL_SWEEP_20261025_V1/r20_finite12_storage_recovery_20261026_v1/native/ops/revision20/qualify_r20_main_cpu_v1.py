"""Actual R20 main, private two-scope authority/entry/workers only. No model."""
import pathlib,json,hashlib,copy,importlib.util,tempfile,types,os,datetime
P=pathlib.Path;F=P('/root/data/dtc_failure_repair_20261025_v1');D=F/'ops/revision20';CONT=D/'sweep_controller.py';EXPECTED='de715b527c6194a65b30d0b921c34a26bc8af4433eddd78c957d98c123723c81';sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();read=lambda p:json.loads(P(p).read_bytes());scenarios=[]
def put(p,x):p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x))
def load():s=importlib.util.spec_from_file_location('r20_actual_main_cpu',CONT);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class Boundary(Exception):pass
def scenario(kind):
 with tempfile.TemporaryDirectory(prefix='R20_MAIN_'+kind+'_',dir=D)as td:
  m=load();top=P(td);m.F=top/'F';m.O=m.F/'ops';m.D=m.O/'revision20';m.T=top/'original';m.N=top/'native';m.R=top/'recovery12';roots={m.ORIGINAL:m.T,m.REQ:m.R}
  for root in roots.values():
   for sub in ['control/qualification_ledger','analysis','logs','DTC/run/results']:(root/sub).mkdir(parents=True,exist_ok=True)
  m.O.mkdir(parents=True);(m.N/'control/qualification_ledger').mkdir(parents=True);(m.N/'control/qualification_ledger/NATIVE_QUALIFICATION.lock').touch();(m.N/'bin').mkdir();entry=m.N/'bin/native';oldentry=b'#!/bin/sh\nset -eu\n# ALL PRIOR EP/DTC BYTES\necho prior "$@"\n';entry.write_bytes(oldentry);put(m.T/'control/BATCH_LEASE.json',dict(pid=999999999,start_ticks=0,controller_sha256=m.PRIOR));holes=['GAP_A','GAP_B','GAP_C'];livecells=['ORIGINAL_LIVE_'+str(i)for i in range(8)];closedcells=['ORIGINAL_CLOSED_'+str(i)for i in range(273)];sealed=['HISTORICAL_HOLD_'+str(i)for i in range(68)];oq=dict(budget=356,remaining=72,consumed={},sealed=sealed,admitted_specs={c:'CPU_SPEC_PIN'for c in[*holes,*livecells,*closedcells,*sealed]},orchestrator_sha256=m.PRIOR,state='RUNNING',reserved_write_bytes=32*m.G,history=['PRESERVE']);claims={}
  def done(k,c):
   root=roots[k];row=reg['registered_future_requests'][k]['consumed'][c];receipt=dict(uuid=row['uuid'],CPU_FIXTURE_ONLY=True);row['execution_receipt']=receipt;put(root/'control/qualification_ledger'/(c+'.DONE.json'),receipt);put(root/'DTC/run/results'/row['uuid']/'NATIVE_EXIT.json',receipt);put(root/'DTC/run/results'/row['uuid']/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=999999999,start_ticks=0,fixture_live=False));return receipt
  reg={'registered_future_requests':{m.ORIGINAL:oq},'old_history':['KEEP']}
  for c in holes:oq['consumed'][c]=dict(uuid='uid-'+c,intent_sha256='CPU_INTENT_PIN')
  for i,c in enumerate(livecells):
   oq['consumed'][c]=dict(uuid='uid-'+c,intent_sha256='CPU_INTENT_PIN');claims[c]=dict(host_cpu=64+i,result_cap_bytes=256*2**20,RAM_cap_bytes=16*m.G);put(m.T/'DTC/run/results'/('uid-'+c)/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=100000+i,start_ticks=100+i,fixture_live=True))
  for c in closedcells:
   oq['consumed'][c]=dict(uuid='uid-'+c,intent_sha256='CPU_INTENT_PIN');done(m.ORIGINAL,c)
   if not(kind=='past_unarchived'and c==closedcells[0]):put(m.T/'control'/(c+'_ARCHIVE_RECEIPT.json'),dict(CPU_PRIOR_ARCHIVE=True,uuid='uid-'+c))
  oldqs={}
  for i,k in enumerate(m.OLD):
   oldqs[k]=dict(state='CLOSED',remaining=0,budget=[23,2,4,4][i],consumed={'OLD_'+str(i):dict(uuid='closed-'+str(i),execution_receipt={'CPU_FIXTURE':True})},orchestrator_sha256='UNCHANGED_OLD_'+str(i),reserved_write_bytes=m.G,history=['OLD_Q_BYTES_KEPT'],source_sha256='PRESERVE');reg['registered_future_requests'][k]=copy.deepcopy(oldqs[k])
  put(m.T/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims));put(m.R/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims={}));fresh=['LAVA_DM','LAVA_DH']+['SMALL_'+str(i)for i in range(10)];specs={};admitted={}
  for i,c in enumerate(fresh):
   sp=dict(cohort=c,request=m.REQ,estimated_peak_model_RAM_bytes=(96 if i<2 else 4)*m.G,expected=dict(instructions=100000+i if i<2 else i),limits=dict(max_process_tree_rss_bytes=(128 if i<2 else 16)*m.G,max_result_directory_bytes=256*2**20));specs[c]=sp;put(m.R/'control/specs'/(c+'.json'),sp);put(m.R/'control'/(c+'_SPEC.json'),sp);admitted[c]=sha(m.R/'control/specs'/(c+'.json'))
  candidate=dict(budget=12,remaining=12,consumed={},admitted_specs=admitted,sealed=[],orchestrator_sha256=EXPECTED,reserved_write_bytes=7*m.G,state='ARMED');candidatepath=m.R/'control/REGISTRY_REQUEST_CANDIDATE_V1.json';put(candidatepath,candidate);put(m.R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',dict(CPU_FIXTURE_ONLY=True));put(m.R/'control/SCIENCE_AUTHORIZATION.json',dict(explicit_user_approval=True,approval_request_sha256=sha(m.R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),budgets={c:1 for c in fresh}));qp=m.O/'R20_ZERO_MODEL_QUALIFICATION_V1.json';put(qp,dict(status='PASS',controller_sha256=EXPECTED,source_pins=[dict(path=str(CONT),sha256=EXPECTED)],prior_entry_sha256=sha(entry),reviewed_original_receipt_gaps=holes));pubpath=m.O/'R20_PUBLICATION_READBACK_V1.json';put(pubpath,dict(verified=True,controller_sha256=EXPECTED,qualification_sha256=sha(qp),commit='CPU_FIXTURE_ONLY'))
  if kind=='unknown_oldclaim':claims['UNKNOWN_OLD_UNSPENT']=dict(host_cpu=143);put(m.T/'control/POOL_DISPATCH_RESERVATIONS.json',dict(claims=claims))
  if kind=='oldscope_notclosed':reg['registered_future_requests'][m.OLD[2]]['state']='RUNNING'
  if kind=='wrong_candidate':x=read(candidatepath);x['budget']=11;put(candidatepath,x)
  if kind=='wrong_alias':put(m.R/'control/LAVA_DM_SPEC.json',dict(WRONG=True))
  if kind=='entry_drift':entry.write_bytes(oldentry+b'# concurrent unknown Lane edit\n')
  if kind=='fresh_original':oq['admitted_specs']['UNSPENT_NOT_SEALED']='CPU_SPEC'
  if kind=='wrong_epoch':epochvalue=1
  else:epochvalue=2
  initialreg=copy.deepcopy(reg);initialentry=entry.read_bytes();attempts={};dispatch=[];adopted=[];guarded=[];activations=[];closes=[];futures=[];resourcecalls=[];events=[];loops=[0];maximum=[0];cpuchecks=[]
  def evidence(k,c):
   state='PASS_STRICT_ARCHIVE_NATIVE_RESTORE'if k==m.ORIGINAL else'PASS_REPAIR_CORRECTNESS_STRICT_ARCHIVE_RESTORE'
   if c=='SMALL_0'and kind=='archived_negative':state='FAIL_REPAIR_VALIDATION_ARCHIVED_NO_RETRY'
   if c=='SMALL_0'and kind=='engineering_spent':state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS'
   return dict(state=state,cohort=c,accepted_cycles=None,model_retries=0)
  def worker(c):
   attempts[c]=attempts.get(c,0)+1;q=reg['registered_future_requests'][m.REQ]
   if kind=='zero_start_defer'and c=='SMALL_0'and attempts[c]==1:return dict(state='ADMISSION_DEFERRED_ZERO_START',cohort=c,model_starts=0)
   q['consumed'][c]=dict(uuid='new-'+c,intent_sha256='CPU_INTENT_PIN');q['remaining']-=1;put(m.R/'control/qualification_ledger'/(c+'.INTENT.json'),dict(cohort=c,uuid='new-'+c))
   if kind in['intent_no_pid_guard','live_pid_guard']and c=='SMALL_0':
    if kind=='live_pid_guard':put(m.R/'DTC/run/results'/('new-'+c)/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=100999,start_ticks=999,fixture_live=True))
    return dict(state='REPAIR_ENGINEERING_ISSUE_PRESERVE_ACTUAL_ARTIFACTS',cohort=c)
   done(m.REQ,c)
   if kind=='missing_DONE'and c=='SMALL_0':(m.R/'control/qualification_ledger'/(c+'.DONE.json')).unlink()
   return evidence(m.REQ,c)
  def activate(fn):
   if kind=='benign_receipt':done(m.ORIGINAL,livecells[0])
   before=copy.deepcopy(reg);fn(reg);q=reg['registered_future_requests'][m.ORIGINAL];prior=before['registered_future_requests'][m.ORIGINAL];assert q['consumed']==prior['consumed']and q['budget']==prior['budget']and q['remaining']==prior['remaining']and q['sealed']==prior['sealed']and q['admitted_specs']==prior['admitted_specs']and q['orchestrator_sha256']==EXPECTED;assert all(reg['registered_future_requests'][k]==oldqs[k]for k in m.OLD);assert reg['registered_future_requests'][m.REQ]==candidate;assert set(reg['registered_future_requests'])==set(before['registered_future_requests'])|{m.REQ};activations.append(True)
  def close(fn):
   before=copy.deepcopy(reg);fn(reg);assert all(reg['registered_future_requests'][k]==before['registered_future_requests'][k]for k in[m.ORIGINAL,*m.OLD]);closes.append(True)
  def resources(s,fresh_source=False):
   assert fresh_source and s['request']==m.REQ;resourcecalls.append(s['cohort']);allow=True;current=read(m.R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   if kind in['large_claim','large_intent_no_pid','large_actual_pid']and s['estimated_peak_model_RAM_bytes']>=96*m.G:allow=not any(c.startswith('LAVA_')for c in current)
   return dict(physical_RAM_pass=allow and kind!='RAM_HOLD',physical_disk_pass=kind!='disk_HOLD',native_free_bytes=(15*m.G-1 if kind=='margin_below5G'else 15*m.G if kind=='margin_exact5G'else 30*m.G),required_free_bytes=10*m.G)
  native=types.SimpleNamespace(read_current_authority=lambda:(reg,dict(epoch=epochvalue,state='NATIVE_SCIENCE_ACTIVE',holder=os.uname().nodename)),update_authority=activate)
  def reuse():cpuchecks.append(True)
  engine=types.SimpleNamespace(verify_cpu_reuse=reuse,registered=lambda:True,plan=lambda:{'allowed_model_CPUs':list(range(208,224))},spec_for=lambda c:copy.deepcopy(specs[c]),output_cap=lambda s:256*2**20,update_authority=close);ops=types.SimpleNamespace(run_cell=worker,finish_evidence=lambda c:evidence(m.REQ,c));accounting=types.SimpleNamespace(resources=resources);copygate=types.SimpleNamespace(install_private_outbox=lambda *a,**k:None)
  def fake_load(name,path):return {'sweep_native_cap1m.py':native,'recovery12_native_v1.py':engine,'recovery12_ops_v1.py':ops,'resource_accounting_v1.py':accounting,'copy_gate_v1.py':copygate}[P(path).name]
  class Future:
   def __init__(self,v,c,held=False):self.value=v;self.c=c;self.ready=False;self.held=held
   def done(self):return self.ready
   def result(self):return self.value
  class Pool:
   def __init__(self,max_workers):assert max_workers==64
   def __enter__(self):return self
   def __exit__(self,*a):return False
   def submit(self,fn,underlying,c):
    held=False
    if c in livecells or c in closedcells:
     adopted.append(c)
     if kind=='oldlive_stays_live':held=True;v=None
     else:
      if'execution_receipt'not in reg['registered_future_requests'][m.ORIGINAL]['consumed'][c]:done(m.ORIGINAL,c)
      v=evidence(m.ORIGINAL,c)
    elif c in reg['registered_future_requests'].get(m.REQ,{}).get('consumed',{})and'execution_receipt'not in reg['registered_future_requests'][m.REQ]['consumed'][c]:guarded.append(c);held=True;v=None
    elif kind in['large_claim','large_intent_no_pid','large_actual_pid']and c.startswith('LAVA_'):
     attempts[c]=attempts.get(c,0)+1;held=True;v=None
     if kind!='large_claim':
      q=reg['registered_future_requests'][m.REQ];q['consumed'][c]=dict(uuid='new-'+c);q['remaining']-=1;put(m.R/'control/qualification_ledger'/(c+'.INTENT.json'),dict(cohort=c,uuid='new-'+c))
      if kind=='large_actual_pid':put(m.R/'DTC/run/results'/('new-'+c)/'NATIVE_SIMULATOR_PID_AND_MAPS.json',dict(pid=100999,start_ticks=999,fixture_live=True))
    else:v=fn(underlying,c)
    f=Future(v,c,held);futures.append(f);return f
  def sleep(_):
   loops[0]+=1
   for f in futures:
    if not f.held:f.ready=True
   maximum[0]=max(maximum[0],len(read(m.R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']));assert maximum[0]<=12
   if kind in['RAM_HOLD','disk_HOLD','margin_below5G','intent_no_pid_guard','live_pid_guard','oldlive_stays_live','large_claim','large_intent_no_pid','large_actual_pid']and loops[0]>=5:raise Boundary()
   assert loops[0]<50
  def event(state,**kw):
   events.append(state)
   if state=='DISPATCH_FRESH_EXACT_RECOVER12_ATTEMPT':dispatch.append(kw['cohort'])
  m.load=fake_load;m.live=lambda b:b.get('fixture_live',False);m.concurrent=types.SimpleNamespace(futures=types.SimpleNamespace(ThreadPoolExecutor=Pool));m.time=types.SimpleNamespace(monotonic=lambda:loops[0]*10,monotonic_ns=lambda:loops[0]*10000000000,time=lambda:loops[0]*10,sleep=sleep);m.event=event;rejects={'unknown_oldclaim','oldscope_notclosed','wrong_candidate','wrong_alias','entry_drift','fresh_original','wrong_epoch'};rejected=False;boundary=False
  try:m.main()
  except Boundary:boundary=True
  except AssertionError:
   if kind in rejects:rejected=True
   else:raise
  assert all(reg['registered_future_requests'][k]==initialreg['registered_future_requests'][k]for k in m.OLD)
  assert all(c not in attempts for c in[*holes,*livecells,*closedcells,*sealed]);assert all(c in fresh for c in attempts)
  if kind in rejects:assert rejected and not activations and not attempts and entry.read_bytes()==initialentry and reg==initialreg
  else:
   assert activations==[True]and cpuchecks==[True];transition=read(m.R/'control/NATIVE_ENTRY_TRANSITION_R20.json');block=transition['added_exact_prefix'].encode();assert entry.read_bytes().replace(block,b'',1)==oldentry and transition['other_routes_byte_preserved'];assert set(reg['registered_future_requests'])==set(initialreg['registered_future_requests'])|{m.REQ};assert len(reg['registered_future_requests'][m.ORIGINAL]['consumed'])==284 and reg['registered_future_requests'][m.ORIGINAL]['sealed']==sealed
   assert all(v==1 or(kind=='zero_start_defer'and c=='SMALL_0'and v==2)for c,v in attempts.items())
   if kind in['RAM_HOLD','disk_HOLD','margin_below5G']:assert boundary and not attempts
   if kind=='caps':assert maximum[0]==12 and len(dispatch)==12
   if kind=='short_first':assert all(not c.startswith('LAVA_')for c in dispatch[:10])and all(c.startswith('LAVA_')for c in dispatch[10:])
   if kind=='zero_start_defer':assert attempts['SMALL_0']==2 and len(reg['registered_future_requests'][m.REQ]['consumed'])==12 and len(list((m.R/'analysis/zero_start_deferrals_R20').glob('*.json')))==1
   if kind in['intent_no_pid_guard','live_pid_guard']:assert boundary and guarded==['SMALL_0']and attempts['SMALL_0']==1 and'SMALL_0'in read(m.R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   if kind.startswith('large_'):assert boundary and attempts.get('LAVA_DM')==1 and'LAVA_DH'not in attempts and'LAVA_DM'in read(m.R/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   if kind=='archived_negative':assert read(m.R/'analysis/VALIDATION_CLOSED_R20.json')['status']=='CLOSED_WITH_ARCHIVED_NATIVE_FAILURES'
   if kind in['engineering_spent','missing_DONE']:assert not closes and not(m.R/'analysis/VALIDATION_CLOSED_R20.json').exists()and reg['registered_future_requests'][m.REQ]['state']!='CLOSED'
   if kind in['caps','short_first','past_unarchived','benign_receipt','zero_start_defer','margin_exact5G']:assert closes==[True]and read(m.R/'analysis/VALIDATION_CLOSED_R20.json')['status']=='ALL_FINITE_CORRECTNESS_VALIDATION_PASS'
   if kind=='oldlive_stays_live':assert boundary and len(adopted)==8 and all(c in read(m.T/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']for c in livecells)
   if kind=='past_unarchived':assert closedcells[0]in adopted
  return dict(scenario=kind,status='PASS',max_new12_claims=maximum[0],fake_worker_invocations=len(attempts),actual_main_private_activation_updates=len(activations),old_four_closed_requests_unchanged=True,original284spent_68sealed_3holes_preserved=True,new_original_starts=0,production_mutations=0,scientific_models_started=0)
assert sha(CONT)==EXPECTED
for kind in ['caps','short_first','past_unarchived','oldlive_stays_live','benign_receipt','zero_start_defer','intent_no_pid_guard','live_pid_guard','archived_negative','engineering_spent','missing_DONE','RAM_HOLD','disk_HOLD','margin_below5G','margin_exact5G','large_claim','large_intent_no_pid','large_actual_pid','unknown_oldclaim','oldscope_notclosed','wrong_candidate','wrong_alias','entry_drift','fresh_original','wrong_epoch']:scenarios.append(scenario(kind))
assert sha(CONT)==EXPECTED
obj=dict(schema='R20_ACTUAL_MAIN_PRIVATE_TWO_SCOPE_CPU_QUALIFICATION_V1',status='PASS',controller_path=str(CONT),controller_sha256=EXPECTED,driver_sha256=sha(__file__),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scenario_count=len(scenarios),main_mock_scenarios=scenarios,scope='Actual frozen main executes private entry/authority/claims/event/control paths. Native workers, resource results, guard outcomes and strict/COPY completions are explicit synthetic fixtures. No simulator/production source/entry/q/process modified.',production_authority_or_entry_mutations=0,scientific_model_starts=0,signals=0);out=F/'ops/R20_CPU_DRIVER_RESULT_V1.json'
with out.open('x')as f:json.dump(obj,f,indent=2);f.write('\n')
print(json.dumps(dict(status='PASS',path=str(out),sha256=sha(out),driver_sha256=sha(__file__),scenarios=len(scenarios))))
