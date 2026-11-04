"""Finite DELTA integration test only, private CPU stub, no simulator/science authority."""
from pathlib import Path
import json,hashlib,copy,sys,os,importlib.util,ast
P=Path('/root/data/ep_l2_full_workload_performance_20261027_v1');O=Path(__file__).resolve().parent;H=O/'private_runtime';V=P/'research/performance_first_v3_20261104_v1/activation_20261104_v1';I=V/'agent_b_incident_20261104_v1';F=O/'delta_fixture';F.mkdir(exist_ok=True);R=F/'isolated_root'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_bytes())
def dump(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def module(n,p):sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
sys.path.insert(0,str(H));eng=module('private_v4_delta_engine',H/'ep_perf_native_wv_modes_draft.py');schema=module('delta_schema',H/'runtime_monitor_schema.py')
# AST equivalence: monitor protections and all original eventloop statements preserved.
a=ast.parse((V/'agent_b_formal/runtime/ep_perf_native_wv_modes_draft.py').read_text());b=ast.parse((H/'ep_perf_native_wv_modes_draft.py').read_text())
ad={n.name:n for n in a.body if isinstance(n,ast.FunctionDef)};bd={n.name:n for n in b.body if isinstance(n,ast.FunctionDef)}
unchanged=['verify_actual','fresh_input','dispatch_binding','resource_gate','accepted_cell','prepare']
for n in unchanged:assert ast.dump(ad[n])==ast.dump(bd[n]),n
before=copy.deepcopy(bd['run_native']);before.body=[n for n in before.body if not(isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)and isinstance(n.value.func,ast.Name)and n.value.func.id=='validate_spec_contract')]
assert ast.dump(before)==ast.dump(ad['run_native']),'eventloop changed beyond preconsume validation'
dump(F/'MONITOR_EQUIVALENCE.json',dict(status='PASS',unchanged_functions=unchanged,run_native_all_original_statements_preserved=True,only_run_native_addition='full schema bound-CPU/current-domain/exact-dependencies before transaction/fork',prior124_not_rerun=True))
production=read(O/'proposal/specs/W_ONLY.json');production_schema_refs=copy.deepcopy(eng._SCHEMA_REFS)
# Mock authority only for harmless stub; actual unmodified monitor/eventloop and loader/strace run.
stub=F/'HOST_CPU_STUB_NOT_SIMULATOR';stub.write_bytes((I/'actual_process_fixture_v2/HOST_CPU_STUB_NOT_SIMULATOR').read_bytes());stub.chmod(0o755)
inputs=F/'inputs';inputs.mkdir(exist_ok=True)
for n in ['kernelslist.g','kernel-1.HOST_CPU_DUMMY']:(inputs/n).write_bytes((I/'actual_process_fixture_v2/inputs'/n).read_bytes())
# Rewrite tiny command list so no old or genuine Trace path can be opened.
(inputs/'kernelslist.g').write_text('kernel-1.HOST_CPU_DUMMY\n')
case='HOST_CPU_STUB_V4_DELTA_NOT_SCIENCE';goal='HOST_CPU_STUB_V4_DELTA_NO_SCIENCE_AUTHORITY';cpu=min(os.sched_getaffinity(0));s=copy.deepcopy(production)
s.update(cohort=case,goal=goal,science_request_id=goal,mode='HOST_CPU_STUB_NO_GPU_MODE',host_cpu=None,binary_path=str(stub),source_identity=dict(binary_sha256=sha(stub),archive_sha256='0'*64,core_source_commit='0'*40,framework_source_commit='0'*40,vendor_pybind11_commit='0'*40),trace_entry=str(inputs/'kernelslist.g'),observer_env={},limits=dict(AS_bytes=1<<30,RSS_bytes=64<<20,result_bytes=8<<20,wall_seconds=20),estimated_peak_RAM_bytes=64<<20,same_background_peer_cohort='HOST_CPU_STUB_UNUSED_PEER',fixture_source_marker='CPU_STUB_NOT_SIMULATOR_NO_PRODUCTION_SOURCE')
s['expected_effective_options']['-trace']=s['trace_entry'];member=inputs/'kernel-1.HOST_CPU_DUMMY';s['all_unique_kernel_members']=[dict(path=str(member),sha256=sha(member),size=member.stat().st_size,member=member.name)]
for k,n in [('source_qualification_ref','SOURCE_QUALIFICATION.json'),('eligibility_ref','INPUT_ELIGIBILITY.json'),('input_binding_ref','INPUT_BINDING.json')]:p=R/'fixture_inputs'/n;dump(p,dict(TEST_ONLY=True,NO_SCIENCE=True,member_ref=ref(member)));s[k]=ref(p)
cl=read(H/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json');cl['Source5']=s['source_identity'];cl['scope']='EXPLICIT_CPU_FIXTURE_ONLY_NOT_SOURCE862_QUALIFICATION';dump(F/'CPU_FIXTURE_EXPLICIT_CLOSURE.json',cl)
ex=read(H/'TRACE_CHILD_HOST_DEPENDENCIES.json');ex['Source5']=s['source_identity'];ex['scope']='EXPLICIT_CPU_FIXTURE_ONLY';dump(F/'CPU_FIXTURE_EXTRA_DEPS.json',ex)
eng._SCHEMA_REFS={**production_schema_refs,'closure_ref':ref(F/'CPU_FIXTURE_EXPLICIT_CLOSURE.json'),'extra_dependencies_ref':ref(F/'CPU_FIXTURE_EXTRA_DEPS.json')}
for d in ex['dependencies']:s['pinned_files'][d['path']]=d['sha256']
eng.ROOT=R;eng.LEDGER=R/'control/qualification_ledger';eng.LEDGER.mkdir(parents=True,exist_ok=True);eng.GOAL=goal;eng.GLOBAL_MAIN_ADMISSION_LOCK=R/'control/ADMISSION.lock'
eng.spec_path=lambda c:R/'cases'/c/'control/FROZEN_SPEC.json';dump(eng.spec_path(case),s)
dump(R/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',dict(TEST_ONLY=True,NO_SCIENCE=True));dump(R/'control/USER_AUTHORIZATION.json',dict(TEST_ONLY=True,approved_scientific_starts=0))
binding=dict(cohort=case,host_cpu=cpu,spec_sha256=sha(eng.spec_path(case)),TEST_ONLY=True);dump(R/'control/dispatch_bindings'/(case+'.json'),binding)
claim=dict(state='CLAIMED',host_cpu=cpu,estimated_peak_RAM_bytes=64<<20,remaining_write_bytes=8<<20,spec_sha256=binding['spec_sha256']);dump(R/'control/DISPATCH_CLAIMS.json',dict(TEST_ONLY=True,claims={case:claim}))
registry=dict(registered_future_requests={goal:dict(TEST_ONLY=True,budget=1,remaining=1,consumed={},state='CPU_FIXTURE_UNCONSUMED')});events=[]
eng.spec_for=lambda c:copy.deepcopy(s)if c==case else (_ for _ in ()).throw(ValueError('exact CPU fixture only'))
eng.dispatch_binding=lambda c:copy.deepcopy(binding)
def transaction(label,callback):before=copy.deepcopy(registry);out=callback(registry);events.append(dict(operation=label,synthetic_authority_only=True,before_remaining=before['registered_future_requests'][goal]['remaining'],after_remaining=registry['registered_future_requests'][goal]['remaining']));return out
eng.transaction=transaction;eng.publish_own_write_carrier=lambda claims:events.append(dict(operation='MOCK_CPU_FIXTURE_CARRIER',count=len(claims)));eng.resource_gate=lambda a,b:events.append(dict(operation='MOCK_CPU_FIXTURE_RESOURCE_ONLY',host_cpu=b['host_cpu']))
def prepare(c):
 assert c==case
 proof=schema.validate_spec_contract(production,**production_schema_refs,check_current_domain=True,check_current_dependencies=True)
 events.append(dict(operation='REAL_PRODUCTION_SOURCE862_FULL_SCHEMA_BEFORE_CPU_FIXTURE_CONSUME',proof=proof))
 return dict(TEST_ONLY=True)
eng.prepare=prepare
# Novel checks exercise newly wired run_native validator, not old124 suite.
base=copy.deepcopy(s);negative=[]
for label,mutate in [('wrong_exact_Source5',lambda x:x['source_identity'].update(core_source_commit='1'*40)),('new_shell_dependency_missing',lambda x:x['pinned_files'].pop('/bin/sh')),('malformed_nested_reference',lambda x:x.update(output_module_ref={'path':'/tmp/invalid','sha256':'bad'})),('full282_options_missing',lambda x:x['expected_effective_options'].pop('-trace'))]:
 s=copy.deepcopy(base);mutate(s);count=len(events)
 try:eng.run_native(case);raise AssertionError('unexpected start')
 except ValueError as e:negative.append(dict(test=label,status='PASS',rejected=str(e),synthetic_consumes=len(registry['registered_future_requests'][goal]['consumed']),model_forks=0));assert not registry['registered_future_requests'][goal]['consumed']
s=copy.deepcopy(base)
done=eng.run_native(case);dump(F/'ACTUAL_EVENTLOOP_DONE.json',done);dump(F/'DELTA_PRECONSUME_NEGATIVES.json',negative);dump(F/'ISOLATED_TRANSACTION_EVENTS.json',events);dump(F/'ISOLATED_AUTHORITY_FINAL.json',registry)
success=done['launcher_wait_returncode']==0 and done['stop_reason']is None and done['native_simulator_observed']is True and done['syscall_proof']['status']=='CLOSED_LOCAL_SYSCALL_INPUT_NETWORK_PROOF_PASS'
receipt=dict(schema='EP_PFV4_NEW_WIRING_CPU_STUB_DELTA_INTEGRATION_V1',status='PASS'if success else'FAIL',production_engine_ref=ref(H/'ep_perf_native_wv_modes_draft.py'),schema_ref=ref(H/'runtime_monitor_schema.py'),real_CPU_stub_started=True,model_ELF_started=False,science_budget_consumed=0,real_authority_writes=0,real_route_writes=0,synthetic_fixture_consumes=len(registry['registered_future_requests'][goal]['consumed']),full_production_schema_preconsume=True,preconsume_delta_negatives=negative,eventloop=dict(exitcode=done['launcher_wait_returncode'],stop_reason=done['stop_reason'],elapsed=done['elapsed_seconds'],peak_RSS=done['peak_process_tree_RSS_bytes'],syscall_status=done['syscall_proof']['status']),limitations=['CPU fixture uses explicit stub Source5 closure and mocked authority/resource/input qualification','Does not qualify GPU application NI/completion/drain or grant scientific authorization'],monitor_equivalence_ref=ref(F/'MONITOR_EQUIVALENCE.json'))
dump(F/'DELTA_INTEGRATION_RECEIPT.json',receipt);print(json.dumps(receipt));assert success
