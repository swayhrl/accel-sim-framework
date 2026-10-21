from pathlib import Path
import copy,hashlib,importlib,json,sys,time
root=Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-e-eval-v1')
pack=root/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/limits_removal_r1'
sys.path[:0]=[str(pack/'candidate'),str(root/'util/ep_l2/mechanism_e')]
import limits_policy as p, capacity_policy as cap, coordinator as coord
original=json.loads(Path('/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json').read_text())[coord.FIELD]
original_bytes=json.dumps(original,sort_keys=True)
checks=[]
def yes(name,fn):
 assert fn(),name
 checks.append(dict(name=name,status='PASS'))
def rejects(name,fn):
 try:fn()
 except (ValueError,KeyError,TypeError):checks.append(dict(name=name,status='PASS'));return
 raise AssertionError(name)
yes('absent amendment preserves original bounded policy',lambda: cap.effective_limits(original)['maximum_actual_starts']==46)
rejects('adoption refuses live controller and existing app states',lambda:p.amend(copy.deepcopy(original),p.APPROVAL_PATH,time.time()))
# Pure in-memory safe-boundary fixture: real current rows are copied; no live data is changed.
safe=copy.deepcopy(original);safe['controller']['state']='STOPPED'
for a in safe['attempts']:
 if a['state'] in ('RUNNING','RESERVED','START_INTENT_UNRECONCILED'):a['state']='SYNTHETIC_TERMINAL_FOR_PURE_CONTROL_ONLY'
before=copy.deepcopy(safe)
yes('pure safe-boundary adoption succeeds',lambda:p.amend(safe,p.APPROVAL_PATH,time.time()))
yes('repeated adoption idempotent',lambda:p.amend(safe,p.APPROVAL_PATH,time.time()) is False)
yes('history and T0 conserved exactly',lambda:safe['attempts']==before['attempts'] and safe['t0_unix']==before['t0_unix'])
yes('original matrix source and all buckets unchanged',lambda:all(safe[k]==before[k] for k in ('full_system_matrix','final_source_identity','reservations','capacity_diagnostic_matrix')))
yes('old limits46 and capacity10 and deadlines retained in amendment history',lambda:safe[p.FIELD]['old_limits']['maximum_actual_starts']==46 and safe[p.FIELD]['old_capacity_start_allowance']==10 and safe[p.FIELD]['old_limits']['start_deadline_unix']==1792663200)
yes('removed scalar values explicit JSON null',lambda:all(k in safe and safe[k] is None for k in p.REMOVED+p.DISPLAYS+('remaining_start_capacity','per_end_timeout_seconds','maximum_capacity_diagnostic_starts')))
yes('effective limits preserve10and24GiB only remove max and dates',lambda:cap.effective_limits(safe)['maximum_actual_starts'] is None and cap.effective_limits(safe)['additional_results_max_bytes']==10*2**30 and cap.effective_limits(safe)['old_plus_new_results_max_bytes']==24*2**30)
yes('deadline truly opens after arbitrarily late time',lambda:p.deadline_open(None,10**100))
yes('legacy deadline still closes normally',lambda:not p.deadline_open(100,100))
spec=json.loads((root/'docs/ep_l2/review_packs/MS20261021_E2_CAPACITY_DIAGNOSTIC_r1/input_preparation/materialized/convolutionSeparable/S_ON_SPEC.json').read_text())
yes('exact existing scientific scope admitted',lambda:p.scope_allowed(safe,spec) and p.has_start_capacity(safe,spec))
for field,value in [('condition_id','UNAPPROVED_EXTRA'),('profile','F'),('budget_bucket','contingency'),('retry_reason','automatic')]:
 bad=copy.deepcopy(spec);bad[field]=value
 yes('out of scope refused '+field,lambda bad=bad:not p.scope_allowed(safe,bad))
bad=copy.deepcopy(spec);bad['identity']['binary_sha256']='0'*64
yes('wrong binary scope refused',lambda:not p.scope_allowed(safe,bad))
yes('old bounded spec remains truthfully10800',lambda:p.effective_timeout(safe,spec)==10800)
new=copy.deepcopy(spec);new['timeout_seconds']=None
rejects('null timeout without exact operational approval rejected',lambda:p.effective_timeout(safe,new))
new['operational_limits_override']=p.operational_override(new)
yes('new exact operational override truly returns None',lambda:p.effective_timeout(safe,new) is None)
yes('new override retains old scientific identity and run key data',lambda:new['identity']==spec['identity'] and new['qualification_id']==spec['qualification_id'])
for field,value in [('scientific_scope_unchanged',False),('effective_timeout_seconds',10**100),('condition_id','X')]:
 bad=copy.deepcopy(new);bad['operational_limits_override'][field]=value
 rejects('inaccurate operational override rejected '+field,lambda bad=bad:p.effective_timeout(safe,bad))
cap.bucket_guard(safe,spec)
checks.append(dict(name='approved capacity bucket numerical cap removed',status='PASS'))
bad=copy.deepcopy(spec);bad['budget_bucket']='contingency'
rejects('old bucket cannot borrow approved removal',lambda:cap.bucket_guard(safe,bad))
# A pure synthetic extra charged row proves there is no46 or capacity10 numerical check.
beyond=copy.deepcopy(safe)
for i in range(50):beyond['attempts'].append(dict(actual_start=True,state='SYNTHETIC_TERMINAL',budget_bucket=cap.BUCKET,selection_id='X',profile='X'))
coord.counts(beyond)
yes('count beyond46 never refunded or numerically capped',lambda:beyond['actual_starts']==before['actual_starts']+50 and beyond['remaining_start_capacity'] is None)
cap.bucket_guard(beyond,spec)
checks.append(dict(name='capacity bucket beyond10 still subject to exact scientific scope',status='PASS'))
already=copy.deepcopy(safe);already['attempts'].append(dict(actual_start=True,state='COMPLETE_VALID',budget_bucket=cap.BUCKET,selection_id=spec['selection_id'],profile=spec['profile']))
rejects('accepted endpoint cannot rerun by changed runtime key',lambda:p.assert_condition_unstarted(already,spec))
for key,value in [('additional_results_max_bytes',11*2**30),('old_plus_new_results_max_bytes',25*2**30),('maximum_actual_starts',10**100)]:
 bad=copy.deepcopy(safe);bad[key]=value
 rejects('resource policy or fake infinity modification rejected '+key,lambda bad=bad:p.active(bad))
bad=copy.deepcopy(safe);bad['t0_unix']+=1
rejects('original T0 cannot reset',lambda:p.active(bad))
bad=copy.deepcopy(safe);bad['reservations']['contingency']=9
rejects('contingency historical8 unchanged',lambda:p.active(bad))
bad=copy.deepcopy(safe);bad['attempts'][0]['actual_start']=False
rejects('historical attempt no refund',lambda:p.active(bad))
bad=copy.deepcopy(safe);bad['campaign_id']='OTHER_PROJECT'
rejects('other project not affected',lambda:p.active(bad))
yes('no removal record legacy budget exhaustion remains false',lambda:not p.has_start_capacity(dict(remaining_start_capacity=0),spec))
yes('read-only snapshot bytes unchanged',lambda:json.dumps(original,sort_keys=True)==original_bytes)
# Coordinator guards are compared against the production source: only numerical/time paths changed.
old=(root/'util/ep_l2/mechanism_e/coordinator.py').read_text();newsource=(pack/'candidate/coordinator.py').read_text()
oldgate=old[old.index('def resource_gate('):old.index('\nclass Coordinator:')]
newgate=newsource[newsource.index('def resource_gate('):newsource.index('\nclass Coordinator:')]
yes('CPU RAM disk Share reservation growth resource_gate byte identical',lambda:oldgate==newgate)
receipt=dict(schema='E2_START_TIME_LIMITS_REMOVAL_PURE_CONTROLS_V1',status='PASS',control_count=len(checks),
 true_native_invocations=0,true_full_application_starts=0,central_registry_writes=0,client_writes=0,
 tests_use_synthetic_in_memory_safe_boundary=True,real_snapshot_actual_starts=original['actual_starts'],controls=checks)
(pack/'PURE_CONTROLS.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(dict(status='PASS',controls=len(checks),actual_app_starts=0)))
