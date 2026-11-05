from pathlib import Path
import hashlib,json,datetime
import importlib.util
O=Path(__file__).parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 b=(json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
 with(O/n).open('xb')as f:f.write(b)
 return hashlib.sha256(b).hexdigest()
sp=importlib.util.spec_from_file_location('inactive_future_policy',O/'future_policy.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
qa=read(O/'CPU_POLICY_QUALIFICATION.json')
assert qa['source_sha256']==sha(O/'future_policy.py')and qa['driver_sha256']==sha(O/'qualify_policy.py')and qa['count']==23
ex,ir=m.pinned_contracts();observations=[]
for c in ex['scope_cohorts']:
 p=m.ROOT/'analysis'/(c+'.RESULT.json');r={'cohort':c,'RESULT_exists':p.exists()}
 if p.exists():
  try:r.update(RESULT_sha256=sha(p),state=read(p).get('state'),complete_readonly_replay_performed=False)
  except Exception as e:r['unreadable']=repr(e)
 observations.append(r)
put('CANARY_PREREQUISITE_READONLY.json',{'UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'status':'NOT_ELIGIBLE_NOT_INSTALLED','production_permission':False,'observations':observations,
 'limitation':'Existence/state observation only; no actual owner readonly replay or V3 runtime qualification. This artifact grants nothing.'})
put('INTERFACE.json',{'schema':'DTC_FUTURE_BPF_POLICY_V3_CANDIDATE_INTERFACE','status':'NOT_ELIGIBLE_NOT_INSTALLED',
 'source_sha256':sha(O/'future_policy.py'),'actual_models_qualified':False,'production_ready':False,
 'APIs':{
  'classify_registered':'(cohort,spec,canonical_sha,q,matrix,frozen_scope,memory_config,exclusion,ir_plan,frozen_bindings,stage=ADMISSION) -> policy; all outputs production_permission=False',
  'canary4_release_eligibility':'(actual_scheduler_frame,actual_main) -> complete real V2 readonly-replay prerequisite result or NOT_ELIGIBLE; never installs',
  'check_terminal_semantics':'(policy,spec,proof,DONE,EXIT,authority_execution_receipt,verified_activation,verified_archive) -> CPU semantic verdict only, not evidence authentication',
  'deployment_status':'() -> NOT_ELIGIBLE_NOT_INSTALLED'},
 'IR_plan_sha256':m.IR_PLAN_SHA,'IR_authority_plan_key':'recovery_plan_sha256',
 'V2_exact4_contract_sha256':m.EXCLUSION_SHA,'V2_exact4_rule':'Immutable V2 exact delegate; existing reference cycles/counts unchanged',
 'PRIMARY_IR_cycles':'Actual positive strict cycles; no equality with P0, another profile or a failed original',
 'scope':'Real MATRIX registered unspent frozen35 primary including future journal profiles, or exactly registered IR11 from immutable plan; q/memory append mandatory; other cohorts exact-old delegate',
 'remaining_required':['Qualified V3 native producer/source snapshot/threebindings and exact role readers','Full V3 strict/consumer/archive/readonly replay and same-owner router qualification','Actual4 complete natural accepted/replayed evidence','Main explicit qualified activation'],
 'no_installer':True,'models_started':0,'new_grants':0,'production_changes':0})
members=[{'path':p.name,'sha256':sha(p),'bytes':p.stat().st_size}for p in sorted(O.iterdir())if p.is_file()and p.name!='MANIFEST.json']
h=put('MANIFEST.json',{'schema':'DTC_E_INACTIVE_POLICY_CANDIDATE_MANIFEST_V1','status':'FROZEN_CPU_POLICY_ONLY_NOT_RUNTIME_QUALIFIED','files':members})
print(json.dumps({'source_sha256':sha(O/'future_policy.py'),'QA_sha256':sha(O/'CPU_POLICY_QUALIFICATION.json'),'manifest_sha256':h,'checks':23}))
