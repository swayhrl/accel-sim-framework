import pathlib,json,hashlib,ast,importlib.util,subprocess,shutil,datetime
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'docs-worktree'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):
 with P(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git','-C',str(F),*a],text=True).strip()
def fn(s,k):return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==k),include_attributes=False)
old=read(T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json');assert read(T/'control/CONTINUATION_R12_PUBLICATION_READBACK.json')['verified'] and sha(T/'tools/sweep_live_ram_override_v1.py')==old['patch_source_sha256'] and sha(T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json')==old['live_override_plan_sha256'];checks=['original_13CPU_plus9_parent_RAM_transition_qualification_and_payload_plan_unchanged']
for row in read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V6.json')['source_pins']:assert sha(row['path'])==row['sha256']
checks.append('all78_old_source_pins_unchanged')
f=load('R12B_independent_new_assert_classification','sweep_failure_review_runtime_assert_v1.py');cell='E2-AEV100-09f94fcc7494a03b-DM';cp=T/'analysis'/(cell+'.FAILURE_CLASSIFICATION_R5.json');proof=f.classify(cell);assert proof==read(cp) and proof['accepted_cycles'] is None and proof['status']=='CLOSED_OO_PIB_STATS_ASSERT_ABORT_UNACCEPTED';checks.append('actual_terminal_OO_PIB_assert_raw_identity_sequence_full_SHA_replayed')
for p in (T/'analysis').glob('*.RESULT.json'):
 r=read(p)
 if r.get('state')=='FAIL_CLOSED_UNACCEPTED_ARCHIVED_NO_RETRY':assert f.classify(r['cohort'])==r['failure_classification']
checks.append('all_six_existing_negative_classes_unchanged')
d=load('R12B_closed_target_driver_fixture','sweep_apply_live_ram_override_r12_v2.py');plan=read(T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json');assert d.natural(cell,plan['targets'][cell]);checks.append('closed_target_allowed_only_with_full_unaccepted_classification')
bad=dict(plan['targets'][cell],uuid='wrong')
try:d.natural(cell,bad)
except AssertionError:pass
else:raise AssertionError('wrong target UUID accepted')
checks.append('wrong_closed_target_UUID_rejected')
a=(T/'tools/revision12/sweep_controller.py').read_text().replace('R12','R12B');b=(T/'tools/revision12b/sweep_controller.py').read_text()
for name in ['run_cell','adopt_live','archive_closed','pending_cells','prefork_resource_defer','copy_wait','grow_write_budget']:assert fn(a,name)==fn(b,name)
assert fn(a.replace('sweep_failure_review_telemetry_v1.py','sweep_failure_review_runtime_assert_v1.py'),'finish_evidence')==fn(b,'finish_evidence');checks.append('all_scientific_execution_and_acceptance_AST_unchanged_except_exact_negative_route')
assert not list((T/'control/live_ram_override').glob('*.DEBUG_DELIVERY_INTENT.json')) and not list((T/'control/live_ram_override').glob('*.ACK.json'));checks.append('new_assertion_preceded_any_actual_debugger_delivery')
qp=T/'control/CONTINUATION_R12B_ZERO_MODEL_QUALIFICATION.json';record=dict(old,controller_sha256=sha(T/'tools/revision12b/sweep_controller.py'),apply_driver_sha256=sha(T/'tools/sweep_apply_live_ram_override_r12_v2.py'),failure_classifier_sha256=sha(T/'tools/sweep_failure_review_runtime_assert_v1.py'),closed_target_adjudication_sha256=sha(T/'control/LIVE_RAM_CLOSED_TARGET_ADJUDICATION_R12B.json'),base_R12_qualification_sha256=sha(T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json'),checks=checks,check_count=len(checks),models_started=0,scientific_processes_attached=0,observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());put(qp,record)
assert not git('status','--porcelain');parent=git('rev-parse','HEAD');assert parent=='f3bca8924096e12895b27eea68b57ebebeb20ca6';rel='docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/operational_continuations/R12B_CLOSED_TARGET_ASSERT_ADJUDICATION_V1';D=F/rel;D.mkdir(parents=True)
files=['tools/revision12b/sweep_controller.py','tools/sweep_apply_live_ram_override_r12_v2.py','tools/sweep_failure_review_runtime_assert_v1.py','tools/qualification_r12b_v1.py','control/CONTINUATION_R12B_ZERO_MODEL_QUALIFICATION.json','control/LIVE_RAM_CLOSED_TARGET_ADJUDICATION_R12B.json','analysis/'+cell+'.FAILURE_CLASSIFICATION_R5.json']
for file in files:
 dest=D/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(T/file,dest)
(D/'README.md').write_text('''# Closed native assertion target before any live guard update

The initial published R12 driver stopped before any GDB delivery because a
planned target had independently exited with an OO/PIB terminal-statistics
assertion. Raw SHA,actual runtime identity,authenticated progress and SIGABRT
are independently replayed. This is an unaccepted model failure,not a natural
PASS,telemetry-only success or a hot-update side effect. No partial cycles
are accepted and no model is retried. Six previous negatives delegate intact.

R12B versions only the closed-target disposition and exact negative classifier.
The RAM payload,CPU qualification,plan,target identities,V4host adapter,hard
caps,telemetry and disk policy remain exact published R12 bytes. A closed
target may satisfy the transition barrier only as ORIGINAL_NATURAL_DONE or
ORIGINAL_CLASSIFIED_UNACCEPTED_DONE,with complete identity/classification proof.
Every still-live target still needs an actual override resource sample after
its inside-frontend ACK. The header truthfully says ORIGINAL_CLOSED_DONE.
No new scientific start occurs before that barrier. The original unused R12
controller is never started; R12B acquires the original finite lease and adopts
all180spent cells. Existing failed points remain failed,not refunded/erased.
''');entries=[{'path':p.relative_to(D).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(D.rglob('*')) if p.is_file()];(D/'PACKAGE_MANIFEST.json').write_text(json.dumps({'files':entries,'scientific_models_started':0},indent=2)+'\n');subprocess.run(['git','-C',str(F),'add','--',rel],check=True);subprocess.run(['git','-C',str(F),'diff','--cached','--check'],check=True);subprocess.run(['git','-C',str(F),'commit','-m','Preserve closed OO PIB assertion while qualifying live RAM transition'],check=True);commit=git('rev-parse','HEAD');branch=git('branch','--show-current');bundle=T/'control/continuation_r12b_source.bundle';subprocess.run(['git','-C',str(F),'bundle','create',str(bundle),branch,'^'+parent],check=True);rec={'commit':commit,'parent':parent,'branch':branch,'package_path':rel,'package_tree':git('rev-parse',commit+':'+rel),'bundle':str(bundle),'controller_sha256':sha(T/'tools/revision12b/sweep_controller.py'),'qualification_sha256':sha(qp)};put(T/'control/CONTINUATION_R12B_SOURCE_COMMIT.json',rec);print(json.dumps({'checks':len(checks),'source_commit':rec}))
