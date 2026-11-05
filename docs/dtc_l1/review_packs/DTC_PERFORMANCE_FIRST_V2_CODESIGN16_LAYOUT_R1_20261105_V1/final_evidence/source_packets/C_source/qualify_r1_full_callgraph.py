"""CPU-only complete INTENT callgraph with real private registry flock/atomic files."""
from pathlib import Path
import copy,json,hashlib,types,fcntl,time,ast
R=Path('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_layout_r1_execution_20261105_v1');O=A/'agents/C_spec_strict_v1';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();rd=lambda p:json.loads(Path(p).read_bytes())
def load(p,name):
 m=types.ModuleType(name);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
def save(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
checks=[];rows=[]
def ck(n,v):assert v,n;checks.append({'check':n,'PASS':True})
actualmatrix=rd(R/'control/MATRIX.fixed.json');first=next(p['cohort']for p in actualmatrix['points']if p['program']=='vectorAdd'and p['profile']=='PHYS768_OOPIB192_TAG64x8');other=next(p['cohort']for p in actualmatrix['points']if p['program']=='vectorAdd'and p['profile']=='PHYS1024_OOPIB192_TAG64x8');rm=load(R/'tools/perf16r1_resources.py','CPU_ACTUAL_R1_RESOURCES');observer=Path('/root/data/dtc_failure_repair_20261025_v1/ops/observer_exit_race_v1.py')
for mode in ['PASS_FULL_CALLGRAPH','PROFILE_HOLD_FULL_CALLGRAPH','NONFIRST_GATE_MISSING_FULL_CALLGRAPH']:
 F=O/'cpu_full_chain_fixture_v3'/mode;F.mkdir(parents=True,exist_ok=False);N=F/'native_authority';C=F/'request';(N/'control/science_authority/request_history').mkdir(parents=True);(C/'control/qualification_ledger').mkdir(parents=True);(C/'control/dispatch_bindings').mkdir();(C/'tools').mkdir();(N/'control/science_authority/REGISTRY_UPDATE.lock').touch()
 for name in ['PROJECT_AUTHORITY.fixed.json','BUILD_PROFILE.json','SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json','MATRIX.fixed.json']:(C/'control'/name).write_bytes((R/'control'/name).read_bytes())
 for name in ['perf16r1_native.py','perf16r1_resources.py','perf16r1_guard.py','perf16r1_guard_policy.py','perf16r1_capacity_strict.py','perf16r1_layout.py']:(C/'tools'/name).write_bytes((R/'tools'/name).read_bytes())
 (C/'control/specs').mkdir();cohort=other if mode.startswith('NONFIRST')else first
 for n in [cohort]:
  raw=(R/'control/specs'/(n+'.json')).read_bytes();(C/'control/specs'/(n+'.json')).write_bytes(raw);(C/'control'/(n+'_SPEC.json')).write_bytes(raw)
 spec=rd(C/'control/specs'/(cohort+'.json'));save(C/'control/dispatch_bindings'/(cohort+'.json'),{'cohort':cohort,'canonical_spec_sha256':sha(C/'control/specs'/(cohort+'.json')),'host_cpu':1,'resolved_spec_sha256':hashlib.sha256((json.dumps(dict(spec,host_cpu=1),sort_keys=True,indent=2)+'\n').encode()).hexdigest()});save(C/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{cohort:{'host_cpu':1}}})
 plan={'direction_release':rd(R/'control/RESOURCE_POLICY.json')['direction_release'],'parent_pid':1498278,'source_pins':[],'project_authority':{'path':str(A/'control/PROJECT_AUTHORITY.fixed.json'),'sha256':sha(A/'control/PROJECT_AUTHORITY.fixed.json')},'launcher_layout':{'path':str(R/'control/LAUNCHER_LAYOUT.fixed.json'),'sha256':sha(R/'control/LAUNCHER_LAYOUT.fixed.json')},'launcher_native_cwd_qualification':{'path':str(R/'control/LAUNCHER_NATIVE_CWD_QUALIFICATION.fixed.json'),'sha256':sha(R/'control/LAUNCHER_NATIVE_CWD_QUALIFICATION.fixed.json')},'observer_overlay':{'path':str(observer),'sha256':sha(observer)},'runtime_guard':{'path':str(C/'tools/perf16r1_guard.py'),'sha256':sha(C/'tools/perf16r1_guard.py')}};save(C/'control/EXECUTION_PLAN.json',plan)
 e=load(R/'tools/perf16r1_native.py','CPU_REAL_R1_ENGINE');e.R=C;e.N=N;e._RESOURCES_MODULE=rm;e.assert_parent_lease=lambda:{'pid':1498278,'start_ticks':977758783};q={'request':e.REQ,'engine_sha256':sha(R/'tools/perf16r1_native.py'),'execution_plan_sha256':sha(C/'control/EXECUTION_PLAN.json'),'spec_request_sha256':sha(C/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'model_automatic_retries':0,'budget':16,'remaining':16,'admitted_specs':{p['cohort']:p['canonical_spec_sha256']for p in actualmatrix['points']},'consumed':{},'sealed':{},'state':'ARMED','runtime_release_evidence':rm.verify_direction_release(plan),'admission_holds':{}}
 if mode.startswith('PROFILE'):
  ev=F/'EVIDENCE.json';save(ev,{'CPU_ONLY_TYPED_HOLD':True});q['admission_holds'][spec['profile']]={'profile':spec['profile'],'classification':'CONFIGURATION_OR_LIFECYCLE_SAFETY_HOLD','decided_by':'DTC_MAIN','reason':'CPU_ONLY','created_utc':'CPU_ONLY','evidence_path':str(ev),'evidence_sha256':sha(ev)}
 reg={'registered_future_requests':{e.REQ:q,'FOREIGN_WITHOUT_REMAINING':{'budget':7,'consumed':7}},'old_source_history':['CPU_HISTORY_SENTINEL'],'qualification_history':['CPU_HISTORY_SENTINEL'],'new_scientific_budget_remaining':16};rp=N/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json';ep=N/'control/CURRENT_SCIENCE_EPOCH.json';save(rp,reg);save(ep,{'epoch':2,'native_registry_sha256':sha(rp),'new_budget_remaining':16});reg_before=copy.deepcopy(reg);e.registered();n=e.engine(cohort)
 ip=C/'control/qualification_ledger'/(cohort+'.INTENT.json');began=time.monotonic();error=None
 try:n.exclusive(ip,{'cohort':cohort,'uuid':'CPU_ONLY_NOT_A_SCIENTIFIC_UUID','output':str(F/'CPU_FAKE_OUTPUT'),'automatic_retry':False})
 except(AssertionError,RuntimeError,KeyError)as x:error=repr(x)
 elapsed=time.monotonic()-began;after=rd(rp);passed=mode=='PASS_FULL_CALLGRAPH';ck(mode+'_actual_whole_exclusive_mutator_expected_path',(error is None)==passed);ck(mode+'_no_registry_lock_self_reentry',elapsed<1.0);ck(mode+'_exclusive_INTENT_iff_eligible',ip.exists()==passed);ck(mode+'_budget_exact_no_refund',after['registered_future_requests'][e.REQ]['remaining']==(15 if passed else 16));ck(mode+'_foreign_and_old_histories_preserved',after['registered_future_requests']['FOREIGN_WITHOUT_REMAINING']==reg_before['registered_future_requests']['FOREIGN_WITHOUT_REMAINING']and after['old_source_history']==reg_before['old_source_history']and after['qualification_history']==reg_before['qualification_history']);ck(mode+'_epoch_hash_consistent',rd(ep)['native_registry_sha256']==sha(rp));rows.append({'case':mode,'elapsed_seconds':elapsed,'error':error,'INTENT_created_in_CPU_private_fixture':ip.exists(),'private_remaining':after['registered_future_requests'][e.REQ]['remaining']})
 # Real bounded-SH behavior: same PID separate FD must fail within2s, not hang.
 with(N/'control/science_authority/REGISTRY_UPDATE.lock').open('rb')as held:
  fcntl.flock(held,fcntl.LOCK_EX);t=time.monotonic();blocked=False
  try:e.authority()
  except RuntimeError as err:blocked='REGISTRY_SHARED_LOCK_BUSY'in str(err)
  dt=time.monotonic()-t;ck(mode+'_bounded_actual_samePID_SH_under_EX',blocked and 1.9<=dt<2.6)
  # The actual runtime sampler remains fast while authority is contended because
  # it is strictly local and never calls registry/peer/full-budget functions.
  forbidden=[];oldfull=rm._full_resources;oldbound=rm.bounded_authority
  rm._full_resources=lambda *a,**k:(_ for _ in()).throw(AssertionError('FORBIDDEN_FULL_RUNTIME'));rm.bounded_authority=lambda *a,**k:(_ for _ in()).throw(AssertionError('FORBIDDEN_REGISTRY_RUNTIME'))
  try:sample=rm.resources(spec,False)
  finally:rm._full_resources=oldfull;rm.bounded_authority=oldbound
  ck(mode+'_real_runtime_sample_local_fast_no_registry',sample['registry_or_peer_reads']==sample['true164_reads']==0 and sample['sample_wall_seconds']<.2 and sample['admission_disk_pass']is False)
ck('no_real_scientific_request_registration',not any((R/'control/qualification_ledger').glob('*.INTENT.json')))
report={'schema':'DTC_LAYOUT_R1_FULL_NATIVE_CALLGRAPH_REAL_FLOCK_CPU_V1','status':'PASS_COMPLETE_PRIVATE_REGISTRY_MUTATOR_CHAIN_NOT_MODEL_EXECUTION','checks':checks,'count':len(checks),'rows':rows,'source_native_sha256':sha(R/'tools/perf16r1_native.py'),'actual_immutable_base_sha256':sha(Path('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py')),'resource_source_sha256':sha(R/'tools/perf16r1_resources.py'),'observer_source_sha256':sha(observer),'real_registry_or_owner_or_scientific_model_actions':0,'guard_30s_cadence_unchanged':True};(O/'CPU_FULL_CALLGRAPH_LOCK_QUALIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'checks':len(checks),'cases':len(rows)}))



