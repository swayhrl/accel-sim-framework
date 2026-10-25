import pathlib,json,hashlib,ast,importlib.util,datetime,subprocess,shutil,copy
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'docs-worktree';checks=[]
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,r):
 with P(p).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def fn(s,n):return ast.dump(next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==n),include_attributes=False)
def git(*a):return subprocess.check_output(['git','-C',str(F),*a],text=True).strip()
old=(T/'tools/revision9/sweep_controller.py').read_text();new=(T/'tools/revision10/sweep_controller.py').read_text();a=load('R10_zero_model_controller','revision10/sweep_controller.py');n=load('R10_actual_authority','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];assert len(q['consumed'])==147 and q['budget']==356
wait=load('R10_preserved_waiter_pin_checker','final_consumer_waiter_v4.py');wait.verify_pins(read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V4.json')['source_pins']);checks.append('all62_active_source_pins_unchanged')
for name in ['pending_cells','copy_wait','hold_detail','prefork_resource_defer']:
 assert fn(old,name)==fn(new,name)
checks.append('pre_INTENT_dedup_resource_deferral_and_COPY_error_gates_AST_unchanged')
for name in ['archive_closed','run_cell','adopt_live','grow_write_budget']:
 assert fn(old.replace('R9','R10'),name)==fn(new,name)
checks.append('archive_runtime_adoption_write_floor_and_no_retry_paths_AST_unchanged')
expected=old.replace('R9','R10').replace("'sweep_failure_review_host_v1.py'","'sweep_failure_review_telemetry_v1.py'");assert fn(expected,'finish_evidence')==fn(new,'finish_evidence');checks.append('only_closed_failure_route_changes_no_science_acceptance_relaxation')
f=load('R10_new_exact_negative_classifier','sweep_failure_review_telemetry_v1.py');cell='E2-AEV100-2b93f70cd0666c51-DH';proof=f.classify(cell);assert proof['accepted_cycles'] is None and proof['scientific_acceptance'] is False and proof['progress_records']==6 and proof['last_progress']['completed']==0;checks.append('actual_scalarProd_DH_full_raw_identity_sequence_resources_and_SIGTERM_replayed')
assert f.classify(cell)==proof;checks.append('same_negative_classification_repeat_is_idempotent')
oldfailed=[c for c in q['consumed'] if (T/'analysis'/(c+'.RESULT.json')).exists() and read(T/'analysis'/(c+'.RESULT.json'))['state']=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY']
assert len(oldfailed)==5
for c in oldfailed:assert f.classify(c)==read(T/'analysis'/(c+'.RESULT.json'))['failure_classification']
checks.append('all5_previous_failed_classifications_delegated_and_preserved_exactly')
fixture={'admitted_specs':{'A':'x','B':'x'},'consumed':{},'sealed':[]};assert a.pending_cells(fixture,{'f':{'cell':'A'}},{'A':{}},{},0)==['B'];fixture['consumed']['B']={};assert not a.pending_cells(fixture,{'f':{'cell':'A'}},{},{},0);checks.append('inflight_and_consumed_cells_never_resubmitted')
policy=read(T/'control/ALL_REMAINING_DISPATCH_POLICY_R10.json');assert policy['maximum_jobs']==288 and policy['admissions_per_window']==8 and policy['admission_window_seconds']==5 and policy['host_plan_sha256']==sha(T/'control/HOST_EXECUTION_PLAN_V2.json');assert 'len(admission_times)>=policy' in new and "plan=dict(plan,maximum_jobs=policy['maximum_jobs'])" in new;checks.append('all_remaining_policy_removes40ceiling_and_accelerates_only_resource_gated_dispatch')
assert 'NATIVE_ENTRY_BEFORE_HOST_V2' not in new and "q.setdefault('host_execution_profiles'" not in new;checks.append('active_entry_adapter_profiles_and_hard_caps_never_edited')
negative=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json');put(T/'control/R10_CLOSED_NEGATIVE_STABILITY_REVIEW.json',{'cohort':cell,'uuid':proof['uuid'],'classification_sha256':sha(negative),'intent_sha256':proof['intent_sha256'],'done_sha256':proof['done_sha256'],'raw_sha256':proof['raw_compressed_sha256'],'SOURCE_KEEP':True,'accepted_cycles':None,'models_started':0})
qp=T/'control/CONTINUATION_R10_ZERO_MODEL_QUALIFICATION.json';put(qp,{'status':'PASS','controller_sha256':sha(T/'tools/revision10/sweep_controller.py'),'policy_sha256':sha(T/'control/ALL_REMAINING_DISPATCH_POLICY_R10.json'),'classifier_sha256':sha(T/'tools/sweep_failure_review_telemetry_v1.py'),'checks':checks,'check_count':len(checks),'preserved_spent_count':147,'models_started':0,'models_signaled':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
assert not git('status','--porcelain');parent=git('rev-parse','HEAD');assert parent=='cbc6925fb067615f0a714f94cec1ebc6996b5163';rel='docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/operational_continuations/R10_ALL_REMAINING_RESOURCE_GATED_V1';D=F/rel;D.mkdir(parents=True)
files=['tools/revision10/sweep_controller.py','tools/sweep_failure_review_telemetry_v1.py','tools/qualification_r10_v1.py','control/ALL_REMAINING_DISPATCH_POLICY_R10.json','control/CONTINUATION_R10_ZERO_MODEL_QUALIFICATION.json','control/R10_CLOSED_NEGATIVE_STABILITY_REVIEW.json','analysis/'+cell+'.FAILURE_CLASSIFICATION_R5.json','analysis/'+cell+'.RESULT.json']
for file in files:
 p=D/file;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(T/file,p)
(D/'README.md').write_text('''# All remaining original cells: resource-gated dispatch

The user removed the former40slot ceiling. R10 retains the same finite original
request, spent147prefix, actual live models, unchanged epoch2 entry/hostV2
adapter,16GiB hard caps,5GiB native disk floor, strict science and COPY gates.
All remaining applicable original cells remain eligible. The dispatch maximum
is288, with up to8 pre-fork admissions per5seconds, each separately gated by
fresh RAM/disk and assigned an unused core in the existing80core pool. This
does not assert every model can fit at once. Existing V1 guards require full
hard-cap reservation until their models close. Even the new4GiB minimum would
require564GiB for141unstarted points, beyond this256GiB cgroup. Four reviewed
Cutcp cells retain the original R6 phase handoff; no HOLD or fraction is cleared.

One ScalarProd-DH attempt stopped after32.48s with authenticated6-record
telemetry ending at SIMULATE/completed0 and launcher-recorded stale producer.
Full raw SHA, runtime/UUID/PID/sequence, passing captured outer RAM/disk,
SIGTERM and non-natural termination are independently joined. It is classified
as an unaccepted telemetry guard STOP, with no cycles/retry and unresolved
producer root cause. Old5negative classifications delegate unchanged. Other
unknown failures still checkpoint. R10 recovers its closed negative archive
without launching its model again. Qualification starts no model. All source
publication must be read back before R10 activation. Actual parent-only
transport is separate and preserves every live frontend/model generation.
''')
entries=[]
for p in sorted(D.rglob('*')):
 if p.is_file():entries.append({'path':p.relative_to(D).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
(D/'PACKAGE_MANIFEST.json').write_text(json.dumps({'files':entries},indent=2)+'\n');subprocess.run(['git','-C',str(F),'add','--',rel],check=True);subprocess.run(['git','-C',str(F),'diff','--cached','--check'],check=True);subprocess.run(['git','-C',str(F),'commit','-m','Dispatch all remaining DTC cells under actual resource gates'],check=True)
commit=git('rev-parse','HEAD');branch=git('branch','--show-current');bundle=T/'control/continuation_r10_source.bundle';subprocess.run(['git','-C',str(F),'bundle','create',str(bundle),branch,'^'+parent],check=True);record={'commit':commit,'parent':parent,'branch':branch,'package_path':rel,'package_tree':git('rev-parse',commit+':'+rel),'bundle':str(bundle),'controller_sha256':sha(T/'tools/revision10/sweep_controller.py'),'qualification_sha256':sha(qp)};put(T/'control/CONTINUATION_R10_SOURCE_COMMIT.json',record);print(json.dumps({'checks':len(checks),'source_commit':record,'models_started':0}))
