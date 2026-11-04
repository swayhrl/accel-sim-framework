from pathlib import Path
import sys,ast,types,hashlib,json,os,gzip
sys.dont_write_bytecode=True
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1/agents/A_remaining28_owner_resource_v1');tests=[]
def check(n,b):assert b,n;tests.append(dict(name=n,PASS=True))
def load(n,p):m=types.ModuleType(n);m.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m
srcs={n:O/n for n in ['perf28_parent_addon.py','perf28_ops.py']};before=set(O.rglob('*'));addon=load('perf4_CPU_addon',srcs['perf28_parent_addon.py']);ops=load('perf4_CPU_ops',srcs['perf28_ops.py']);check('imports_no_files_created',set(O.rglob('*'))==before)
check('API_functions_present',callable(addon.apply)and callable(ops.run_scheduler)and callable(ops.actual_runtime_witness))
prior=b'#!/bin/sh\nset -eu\n# prior arbitrary bytes\n\xff\x80\ncase OLD in *) :;; esac\n';block=b'# first4 E2-DTCPF28-* route\n';after=addon.exact_native_route(prior,block);check('native_route_all_prior_bytes_preserved',after.replace(block,b'',1)==prior)
for name,b,bl in [('duplicate_route',after,block),('invalid_header',b'#!/bin/bash\n',block),('empty_block',prior,b''),('wrong_scope_block',prior,b'E2-DTC2A48-*')]:
 try:addon.exact_native_route(b,bl);ok=False
 except AssertionError:ok=True
 check(name+'_rejected',ok)
for name,fn in [('apply_nonowner',lambda:addon.apply(str(addon.R))),('scheduler_nonowner',ops.run_scheduler)]:
 try:fn();ok=False
 except AssertionError:ok=True
 check(name+'_before_any_runtime_sideeffect',ok)
F=O/'fixtures';F.mkdir(exist_ok=True);ops.R=F;co='E2-DTCPF28-'+('a'*16)+'-DH-PHYS768-V1';out=F/'DTC/run/results'/'CPU-ONLY-UUID';out.mkdir(parents=True,exist_ok=True);pidmap=out/'NATIVE_SIMULATOR_PID_AND_MAPS.json';ticks=int(Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]);pidmap.write_text(json.dumps(dict(pid=os.getpid(),start_ticks=ticks)));check('native_live_generation_exact',ops.native_live(pidmap));pidmap.write_text(json.dumps(dict(pid=os.getpid(),start_ticks=ticks+1)));check('native_live_generation_mismatch_rejected',not ops.native_live(pidmap));pidmap.write_text(json.dumps(dict(pid=os.getpid(),start_ticks=ticks)))
e=types.SimpleNamespace(registered=lambda:(None,None,dict(consumed={co:dict(uuid='CPU-ONLY-UUID')})),binding=lambda:dict(runtime_guard_sha256='guard-pin'))
def write_guard(decision='CONTINUE',pin='guard-pin'):(out/'RESOURCE_SAMPLES.jsonl.gz').write_bytes(gzip.compress((json.dumps(dict(DTC_exact_original_policy=dict(decision=dict(decision=decision),runtime_policy_binding=dict(guard_sha256=pin))))+'\n').encode()))
write_guard();check('runtime_witness_matching_guard',ops.actual_runtime_witness(co,e));write_guard('STOP');check('runtime_witness_STOP_rejected',not ops.actual_runtime_witness(co,e));write_guard(pin='changed');check('runtime_witness_source_drift_rejected',not ops.actual_runtime_witness(co,e));(out/'RESOURCE_SAMPLES.jsonl.gz').write_bytes(b'invalid');check('runtime_witness_bad_gzip_rejected',not ops.actual_runtime_witness(co,e))
# Static contract scopes: inspect actual AST/constants; no main callback or thread creation executed.
sa=srcs['perf28_parent_addon.py'].read_text();so=srcs['perf28_ops.py'].read_text();check('no_old_completion_launch_prerequisite','OLD_STAGEI_MODEL_STILL_LIVE'not in sa and 'FIRST16_MODEL_STILL_LIVE'not in sa);check('fixed28_budget_source',"candidate['budget']==candidate['remaining']==28"in sa and 'budget=28'in so);check('exact_FD3_4_retention',"{h.fileno()for h in handles}=={3,4}"in sa);check('protected_mask_before_affinity_change',so.index('PROTECTED_GES_MAIN_CPU_OVERLAP')<so.index('os.sched_setaffinity'));check('sourcepins_enforced',"for x in plan['source_pins']:assert sha(x['path'])==x['sha256']"in sa);check('exact_original_remaining28_scope',len(addon.EXPECTED28_COHORTS)==len(set(addon.EXPECTED28_COHORTS))==28 and set(addon.EXPECTED28_COHORTS)==set(ops.EXPECTED28_COHORTS))
check('first4_gate_before_registration',sa.index('first4_completion_gate(reg)')<sa.index('e.update_authority(register)'))
check('independent_CPU_review_before_registration',sa.index("plan['independent_CPU_review_manifest']")<sa.index('e.update_authority(register)'))
check('no_additional_canary_or_expansion_gate','canaries'not in so and 'expanded'not in so)
result=dict(schema='DRAFT_REMAINING28_OWNER_ADAPTER_CPU_QUALIFICATION_V1',status='PASS_CPU_ONLY_DRAFT_REQUIRES_ROOT_NATIVE_INTEGRATION_REVIEW',tests=tests,n=len(tests),source_pins=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in srcs.values()],actual_owner_callback_applied=False,actual_scheduler_started=False,actual_models_started=0,new_controller_or_service=0,registry_or_native_route_writes=0,R3tools_writes=0,fixture_PID_is_CPU_test_process_not_model=True)
(O/'OWNER_ADAPTER_CPU_QUALIFICATION.json').write_text(json.dumps(result,indent=2)+'\n');print('CPU',len(tests),'sources',result['source_pins'])
