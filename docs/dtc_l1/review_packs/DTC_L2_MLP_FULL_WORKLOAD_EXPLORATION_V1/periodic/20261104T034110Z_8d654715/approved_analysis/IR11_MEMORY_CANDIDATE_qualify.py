"""IR11-only private real-flock/forward-recovery qualification. No production apply."""
from pathlib import Path
import json,hashlib,importlib.util,types,copy,tempfile,fcntl,threading,os
P=Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');N=P('/root/data/ep_l2_dtc_l1_native_v2')
D=A/'coordinator/incident11_memory_scope_transaction_v1'
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
t=load('ir11_tx_qualified',D/'scope_transaction.py');proposal=load('ir11_scope_proposal',D/'scope_proposal.py');prep=read(D/'PREPARATION.json');bridge=load('ir11_actual_scope',prep['scope_path'])
plan=read(prep['plan_path']);q0=read(N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json')['registered_future_requests']['DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1']
matrix=read(R/'control/MATRIX_CURRENT.json');scope0=read(R/'control/SCOPE.json');irkeys={r['new_cohort']for r in plan['rows']};legacy=set(q0['admitted_specs'])-{p['cohort']for p in matrix['points']}-irkeys
scope=bridge.IncidentScope(plan,legacy);contract=read(D/'EXACT11_SCOPE_CONTRACT.json');activepath=R/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json';old=read(activepath);lib=load('ir11_actual_cpu2',old['library_path']);lib.validate(old,q0)
oldsha=sha(activepath);root=P(tempfile.mkdtemp(prefix='IR11_PRIVATE_',dir=D));checks=[]
def check(n,fn):fn();checks.append(dict(name=n,status='PASS'))
def refuses(fn):
 try:fn()
 except Exception:return
 raise AssertionError('EXPECTED_REJECTION')
def fixture(name):
 f=root/name;f.mkdir();q=copy.deepcopy(q0);private_active=f/'ACTIVE_MEMORY.json';put(private_active,old)
 for n,v in [('MATRIX_CURRENT.json',matrix),('SCOPE.json',scope0),('POOL_DISPATCH_RESERVATIONS.json',dict(claims={}))]:put(f/'control'/n,v)
 for c in scope.rows:
  b=(R/'control/specs'/(c+'.json')).read_bytes()
  for p in [f/'control/specs'/(c+'.json'),f/'control'/(c+'_SPEC.json')]:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 lock=f/'PRIVATE_AUTHORITY.lock';calls=[];inside=[False];authority=dict(registered_future_requests={q['request']:q})
 def guarded():
  if inside[0]:calls.append('FORBIDDEN_AUTHORITY_REENTRY')
  with lock.open('a+b')as fd:fcntl.flock(fd,fcntl.LOCK_SH|fcntl.LOCK_NB)
 def canonical(c):guarded();s=read(f/'control/specs'/(c+'.json'));assert sha(f/'control/specs'/(c+'.json'))==q['admitted_specs'][c];return s
 def mutate(callback):
  # Simulate an independent original receipt appended before EX was acquired.
  q['private_concurrent_receipt']=dict(uuid='PRIVATE_OLD_RECEIPT',refunds=0)
  with lock.open('a+b')as fd:
   fcntl.flock(fd,fcntl.LOCK_EX);inside[0]=True
   try:callback(authority)
   finally:inside[0]=False
 memory=dict(lib=lib,aging=types.SimpleNamespace(lock=threading.RLock()),context=dict(cfg=copy.deepcopy(old)))
 sync=types.SimpleNamespace(root=f,memory=memory,cfg=dict(memory_active_path=str(private_active)),lock=threading.RLock())
 sync.engine=types.SimpleNamespace(canonical=canonical,update_authority=mutate)
 def stable():assert read(private_active)==memory['context']['cfg'];lib.validate(memory['context']['cfg'],q);return q,memory['context']['cfg']
 sync.check=lambda:(q,None);sync.stable_memory=stable
 def update(new,owner_assert):owner_assert();memory['context']['cfg']=copy.deepcopy(new)
 sync.owner_module=types.SimpleNamespace(update_scope_in_owner=update)
 obj=t.ScopeTransaction(sync,scope,D/'EXACT11_SCOPE_CONTRACT.json',proposal,{},dict(pid=os.getpid()),f/'transactions')
 # Main/lease/source binding is separately preserved from the frozen base;
 # this private fixture substitutes only owner identity assertion/context.
 obj.owner_assert=lambda:None
 return obj,q,memory,private_active,calls,f
def pure_proposal():
 def canonical(c):return read(R/'control/specs'/(c+'.json')),sha(R/'control/specs'/(c+'.json'))
 p=proposal.propose_scope_append(old,q0,scope,contract,matrix,scope0,canonical,lib)
 assert len(p['new_config']['allowed_cohorts'])==len(old['allowed_cohorts'])+11
 assert p['new_full_record']==dict(p['old_full_record'],**lib.record(p['new_config']))
 assert p['grant_changes']==p['production_changes']==0
check('actual_CPU2_validate_exact11_proposal_preserves_full_record_and_policy',pure_proposal)
def forward():
 obj,q,m,ap,calls,f=fixture('full_forward');before=copy.deepcopy(q);p=obj.prepare();a=obj.apply(p)
 assert a['status']=='EXACT11_INCIDENT_CPU2_SCOPE_APPEND_ACK'and a['grants_added']==a['models_started']==0
 assert len(m['context']['cfg']['allowed_cohorts'])==len(old['allowed_cohorts'])+11 and not calls
 expected=copy.deepcopy(before);expected['private_concurrent_receipt']=dict(uuid='PRIVATE_OLD_RECEIPT',refunds=0);expected['additional_operational_overlays'][lib.ID]=read(p)['new_record'];assert q==expected
 assert obj.apply(p)==a
check('full_forward_real_independent_FD_EX_no_reentry_preserves_concurrent_receipt_and_idempotent_ACK',forward)
def recovery(phase):
 obj,q,m,ap,calls,f=fixture(phase);p=obj.prepare()
 def fail(x):
  if x==phase:raise RuntimeError('PRIVATE_FAULT_'+phase)
 obj.fault_hook=fail;refuses(lambda:obj.apply(p));assert not p.with_name('ACK.json').exists()
 obj.fault_hook=None;a=obj.apply(p);assert a['new_config_sha256']==sha(ap)and not calls
 assert q['remaining']==q0['remaining']and q['consumed']==q0['consumed']
for phase in ['AFTER_AUTHORITY','AFTER_ACTIVE_FILE','AFTER_OWNER_CONTEXT']:
 check('forward_recovery_'+phase,lambda phase=phase:recovery(phase))
def alias_and_lineage():
 obj,q,m,ap,calls,f=fixture('negative_alias_lineage');p=obj.prepare();c=sorted(scope.rows)[0];alias=f/'control'/(c+'_SPEC.json');b=alias.read_bytes();before=copy.deepcopy(q)
 alias.write_bytes(b'{}\n');refuses(lambda:obj.apply(p));before['private_concurrent_receipt']=dict(uuid='PRIVATE_OLD_RECEIPT',refunds=0);assert q==before;alias.write_bytes(b)
 s=read(alias);s['incident_recovery_trial_lineage']['original_uuid']='PRIVATE_WRONG_ORIGINAL_UUID'
 for path in [alias,f/'control/specs'/(c+'.json')]:put(path,s)
 q['admitted_specs'][c]=sha(alias);before=copy.deepcopy(q);refuses(lambda:obj.apply(p));assert q==before and sha(ap)==oldsha and not calls
check('alias_and_lineage_drift_fail_before_private_authority_mutation',alias_and_lineage)
assert sha(activepath)==oldsha,'PRODUCTION_ACTIVE_CHANGED_DURING_READONLY_QUALIFICATION'
report=dict(schema='IR11_MEMORY_SCOPE_REAL_FLOCK_FORWARD_QUALIFICATION_V1',status='PASS',checks=checks,source_sha256=sha(D/'scope_transaction.py'),proposal_sha256=sha(D/'scope_proposal.py'),contract_sha256=sha(D/'EXACT11_SCOPE_CONTRACT.json'),scope_sha256=prep['scope_sha256'],driver_sha256=sha(__file__),actual_CPU2_library_sha256=sha(lib.__file__),private_fixture_root=str(root),real_independent_FD_EX_lock=True,production_lock_used=False,standins=['owner identity assertion and private owner context update','private authority storage preserving actual request data'],production_mutations=0,new_grants=0,models_started=0,production_eligible=False)
t.exclusive_bytes(D/'CPU_QUALIFICATION.json',t.raw(report))
print(json.dumps(dict(status='PASS',checks=len(checks),QA_sha256=sha(D/'CPU_QUALIFICATION.json'),source_sha256=report['source_sha256'],production_eligible=False)))
