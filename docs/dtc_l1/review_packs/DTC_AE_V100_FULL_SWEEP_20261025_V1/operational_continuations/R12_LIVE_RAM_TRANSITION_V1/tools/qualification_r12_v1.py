import pathlib,json,hashlib,ast,importlib.util,datetime,subprocess,shutil,os
P=pathlib.Path;T=P('/root/data/dtc_main_v100_sweep_20261025_v1');F=T/'docs-worktree';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def put(p,x):
 with P(p).open('x') as f:json.dump(x,f,indent=2);f.write('\n')
def load(name,file):
 s=importlib.util.spec_from_file_location(name,T/'tools'/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git','-C',str(F),*a],text=True).strip()
def fn(s,name):return ast.dump(next(n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef) and n.name==name),include_attributes=False)
qa=read(T/'control/LIVE_RAM_GUARD_CPU_QUALIFICATION_R12.json');assert qa['status']=='PASS';patchsha=sha(T/'tools/sweep_live_ram_override_v1.py');assert patchsha=='313bbb7f9a34cb514842132af8f0f43e0342994a96806f30d636052b9905e1b3';assert patchsha in json.dumps(qa) and sha(T/'tools/qualify_live_ram_patch_cpu_v1.py') in json.dumps(qa);checks=['CPU_only_main_thread_pending_call_and_wrapper_13case_qualification_bound']
for row in read(T/'control/FINAL_CONSUMER_WAITER_CONFIG_V6.json')['source_pins']:assert sha(row['path'])==row['sha256']
checks.append('all78_previous_source_pins_and_scientific_runtime_unchanged')
p=read(T/'control/HOST_EXECUTION_PLAN_V4.json');plan=read(T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json');policy=read(T/'control/ALL_REMAINING_DISPATCH_POLICY_R12.json');assert p['legacy_V1_cells']==[] and p['maximum_jobs']==40 and p['per_job_hard_cap_unchanged_bytes']==16*G and policy['host_plan_sha256']==sha(T/'control/HOST_EXECUTION_PLAN_V4.json') and p['live_RAM_override_plan_sha256']==policy['live_RAM_override_plan_sha256']==sha(T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json') and plan['patch_source_sha256']==patchsha;checks.append('explicit_RAM_only_transition_plan_and_fixed4G40_policy_bound')
for row in p['source_pins']:assert sha(row['path'])==row['sha256']
for row in plan['targets'].values():assert sha(row['resource_function_source_path'])==row['resource_function_source_sha256']
checks.append('all_actual_target_resource_function_sources_frozen')
old=(T/'tools/revision11/sweep_controller.py').read_text().replace('R11','R12');new=(T/'tools/revision12/sweep_controller.py').read_text()
for name in ['run_cell','finish_evidence','adopt_live','archive_closed','pending_cells','prefork_resource_defer','copy_wait','grow_write_budget']:assert fn(old,name)==fn(new,name)
checks.append('scientific_execution_strict_failure_COPY_and_no_retry_functions_AST_unchanged')
assert "LIVE_RAM_OVERRIDE_ACTIVATION_BARRIER_R12.json" in new and "ALL_LIVE_TARGET_RAM_OVERRIDES_OBSERVED_OR_ORIGINAL_NATURAL_DONE" in new and "sweep_frontend_host_v4.py" in new;checks.append('actual_first_override_sample_barrier_required_before_new_model_dispatch')
n=load('R12_qualification_native','sweep_native_cap1m.py');q=n.read_current_authority()[0]['registered_future_requests'][n.REQUEST];before=read(T/'control/REQUEST_AT_R11_RETIREMENT_FOR_R12.json');assert q['budget']==356 and set(q['consumed'])==set(before['consumed'])==set(p['preserved_prefix_cells'])
for c,row in before['consumed'].items():assert all(q['consumed'][c][k]==v for k,v in row.items())
checks.append('all180_spent_identities_and_finite_budget_preserved')
a=load('R12_qualification_host_adapter','sweep_host_execution_v4.py');assert a.envelope(16*G,0,10*G)==4*G and a.envelope(16*G,15*G,0)==15*G and a.ram_decision(300*G,str(256*G),64*G,32*G,160*G,640*G,True,False)[0];checks.append('40_initial4GiB_envelopes_fit_without16GiB_future_overreservation')
a.plan=lambda native:(q,dict(p,plan_sha256=sha(T/'control/HOST_EXECUTION_PLAN_V4.json')));n=a.install(n);c=next(c for c in q['admitted_specs'] if c not in q['consumed'] and c not in q.get('sealed',[]));r=n.resources(n.spec_for(c),True);assert not r['legacy_host_V1_live_cells'] and r['physical_RAM_pass'];checks.append('real_current_candidate_passes_actual4GiB_RAM_gate_after_transition')
qp=T/'control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json';put(qp,{'status':'PASS','controller_sha256':sha(T/'tools/revision12/sweep_controller.py'),'plan_sha256':sha(T/'control/HOST_EXECUTION_PLAN_V4.json'),'policy_sha256':sha(T/'control/ALL_REMAINING_DISPATCH_POLICY_R12.json'),'live_override_plan_sha256':sha(T/'control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json'),'patch_source_sha256':patchsha,'CPU_qualification_sha256':sha(T/'control/LIVE_RAM_GUARD_CPU_QUALIFICATION_R12.json'),'apply_driver_sha256':sha(T/'tools/sweep_apply_live_ram_override_r12.py'),'checks':checks,'check_count':len(checks),'actual_candidate_resources_diagnostic':r,'models_started':0,'scientific_processes_attached':0,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
assert not git('status','--porcelain');parent=git('rev-parse','HEAD');assert parent=='10010d23062d40201716a8a11f011dfa48642667';rel='docs/dtc_l1/review_packs/DTC_AE_V100_FULL_SWEEP_20261025_V1/operational_continuations/R12_LIVE_RAM_TRANSITION_V1';D=F/rel;D.mkdir(parents=True)
files=['tools/sweep_live_ram_override_v1.py','tools/sweep_apply_live_ram_override_r12.py','tools/qualify_live_ram_patch_cpu_v1.py','tools/qualification_r12_v1.py','tools/sweep_host_execution_v4.py','tools/sweep_frontend_host_v4.py','tools/revision12/sweep_controller.py','control/LIVE_RAM_GUARD_CPU_QUALIFICATION_R12.json','control/LIVE_RAM_GUARD_OVERRIDE_PLAN_R12.json','control/CONTINUATION_R12_ZERO_MODEL_QUALIFICATION.json','control/HOST_EXECUTION_PLAN_V4.json','control/ALL_REMAINING_DISPATCH_POLICY_R12.json','control/R11_PARENT_RETIREMENT_LIVE_MODELS_PRESERVED_R12.json']
for file in files:
 dest=D/file;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(T/file,dest)
# Retain all CPU-only fixture result/identity/sequence evidence, never scientific raw.
fixture_root=P(qa.get('fixture_root',qa.get('root','/nonexistent')))
if not fixture_root.exists():
 candidates=[d for d in (T/'control').glob('CPU_RAM_PATCH_*') if str(d) in json.dumps(qa)];assert len(candidates)==1;fixture_root=candidates[0]
for path in fixture_root.rglob('*'):
 if path.is_file() and path.suffix in ['.json','.py','.gdb']:
  dest=D/'CPU_only_fixtures'/path.relative_to(fixture_root);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
(D/'README.md').write_text('''# Qualified live outer-RAM predicate transition

The user explicitly requested removal of the old reservation bottleneck.
No existing reload API existed. This separate operational adapter uses a
qualified GDB pending call in the frontend main Python thread to replace only
its global resources lookup. It calls the original function and retains all
original dictionary fields except physical_RAM_pass. The replacement uses a
separately captured actual64GiB host/48GiB effective-cgroup headroom sample;
the prior boolean and full fresh counters are appended for independent replay.
Telemetry,raw lossless capture,BA policy,hard16GiB cap,disk,simulator/cache and
all original source/spec/UUID/spent ledger identities remain unchanged. This
is explicitly an in-memory host-guard amendment,not an unchanged old runtime.

CPU-only qualification covers original run frame/model generation/pipe/UDS
sequence continuity,main-thread callback,bad identity rejection,stable code
fingerprints,RAM/credit boundaries and sole-field replacement. The earlier
marshal-code hash was rejected during fixtures; stable recursive structural
JSON fingerprints are used instead. No scientific process was attached by
qualification. Runtime application attaches frontends only,never models;exact
source+compiled-function identity and model/frontend generation must match.
Each inside-frontend ACK is insufficient alone:every still-live target must
emit an actual independently checked override resource row before dispatch.
Only then may R12 use40slots with4GiB initial reservations and actual RSS
growth. Unknown issues checkpoint without model retry. Original four reviewed
Cutcp cells and all final full-input SHA/strict/archive/restore gates remain.
This package is source/qualification evidence before any live transition;
actual delivery and barrier receipts establish whether application completed.
''');entries=[{'path':p.relative_to(D).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(D.rglob('*')) if p.is_file()];(D/'PACKAGE_MANIFEST.json').write_text(json.dumps({'files':entries,'scientific_models_started_by_qualification':0},indent=2)+'\n');subprocess.run(['git','-C',str(F),'add','--',rel],check=True);subprocess.run(['git','-C',str(F),'diff','--cached','--check'],check=True);subprocess.run(['git','-C',str(F),'commit','-m','Qualify live frontend RAM predicate transition without restarting models'],check=True);commit=git('rev-parse','HEAD');branch=git('branch','--show-current');bundle=T/'control/continuation_r12_source.bundle';subprocess.run(['git','-C',str(F),'bundle','create',str(bundle),branch,'^'+parent],check=True);rec={'commit':commit,'parent':parent,'branch':branch,'package_path':rel,'package_tree':git('rev-parse',commit+':'+rel),'bundle':str(bundle),'controller_sha256':sha(T/'tools/revision12/sweep_controller.py'),'qualification_sha256':sha(qp)};put(T/'control/CONTINUATION_R12_SOURCE_COMMIT.json',rec);print(json.dumps({'additional_checks':len(checks),'source_commit':rec,'models_started':0}))
