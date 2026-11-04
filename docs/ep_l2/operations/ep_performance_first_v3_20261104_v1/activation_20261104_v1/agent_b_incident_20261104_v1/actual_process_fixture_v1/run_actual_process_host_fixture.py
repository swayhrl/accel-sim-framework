"""Actual tiny-CPU Host integration fixture. Not GPU simulation, no science authority."""
from pathlib import Path
import json,copy,hashlib,importlib.util,sys,os,contextlib
O=Path(__file__).resolve().parent;I=O.parent;V=I.parent.parent;J=V.parent.parent
H=V/'activation_20261104_v1/agent_b_formal/runtime';C=I/'candidate';R=O/'isolated_root_attempt2'
def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(path=str(p),sha256=sha(p))
def dump(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def module(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
sys.path.insert(0,str(H));sys.path.insert(0,str(C))
eng=module('sealed_engine_under_private_host_fixture',H/'ep_perf_native_wv_modes_draft.py')
schema=module('preconsume_schema_under_fixture',C/'runtime_monitor_schema.py')
failed=J/'execution_vector1700_decomposition_v3_20261104_v1/vector1700/cases/EP_PERF_PFV3_VECTOR4M_W_ONLY_1700_V1/control/FROZEN_SPEC.json'
science_probe=read(failed);science_probe['native_boot_id']=Path('/proc/sys/kernel/random/boot_id').read_text().strip();science_probe['native_mount_namespace']=os.readlink('/proc/self/ns/mnt')
closure=read(C/'SOURCE862_NATIVE_RUNTIME_CLOSURE.json')['pinned_files']
science_probe['pinned_files']={**closure,**science_probe['pinned_files']}
stub=O/'HOST_CPU_STUB_NOT_SIMULATOR';case='HOST_CPU_STUB_INTEGRATION_NOT_SCIENCE';goal='HOST_CPU_FIXTURE_ONLY_NO_SCIENCE_REQUEST'
cpu=min(os.sched_getaffinity(0));(R/'control/qualification_ledger').mkdir(parents=True,exist_ok=True)
s=copy.deepcopy(science_probe);s.update(cohort=case,goal=goal,science_request_id=goal,mode='HOST_CPU_STUB_NO_GPU_MODE',host_cpu=None,binary_path=str(stub),source_identity=dict(binary_sha256=sha(stub),archive_sha256='HOST_CPU_STUB_NO_PRODUCTION_LIBRARY',core_source_commit='HOST_CPU_STUB_NOT_A_GPU_SIMULATOR',framework_source_commit='HOST_CPU_STUB_ONLY',vendor_pybind11_commit='NOT_APPLICABLE'),trace_entry=str(O/'inputs/kernelslist.g'),observer_env={},pinned_files=closure,ordered_configs=[],limits=dict(AS_bytes=1<<30,RSS_bytes=64<<20,result_bytes=8<<20,wall_seconds=20),estimated_peak_RAM_bytes=64<<20)
member=O/'inputs/kernel-1.HOST_CPU_DUMMY';s['all_unique_kernel_members']=[dict(path=str(member),sha256=sha(member),size=member.stat().st_size,member=member.name)]
# Every copied qualification object is a fixture marker, not a scientific review.
for k,n in [('source_qualification_ref','SOURCE_QUALIFICATION.json'),('eligibility_ref','INPUT_ELIGIBILITY.json'),('input_binding_ref','INPUT_BINDING.json')]:
 p=R/'fixture_inputs'/n;dump(p,dict(TEST_ONLY=True,scope='HOST_CPU_STUB_NO_GPU_QUALIFICATION',member_ref=ref(member)));s[k]=ref(p)
dump(R/'cases'/case/'control/FROZEN_SPEC.json',s)
dump(R/'cases'/case/'control/NATIVE_PRELAUNCH_QUALIFICATION.json',dict(TEST_ONLY=True,NO_SCIENCE=True))
dump(R/'control/USER_AUTHORIZATION.json',dict(TEST_ONLY=True,approved_scientific_starts=0))
binding=dict(cohort=case,host_cpu=cpu,spec_sha256=sha(R/'cases'/case/'control/FROZEN_SPEC.json'),TEST_ONLY=True)
dump(R/'control/dispatch_bindings'/(case+'.json'),binding)
claim=dict(state='CLAIMED',host_cpu=cpu,estimated_peak_RAM_bytes=64<<20,remaining_write_bytes=8<<20,spec_sha256=binding['spec_sha256'])
dump(R/'control/DISPATCH_CLAIMS.json',dict(TEST_ONLY=True,claims={case:claim}))
registry=dict(registered_future_requests={goal:dict(TEST_ONLY=True,budget=1,remaining=1,consumed={},state='CPU_FIXTURE_UNCONSUMED')})
events=[]
eng.ROOT=R;eng.LEDGER=R/'control/qualification_ledger';eng.GOAL=goal
eng.GLOBAL_MAIN_ADMISSION_LOCK=R/'control/ADMISSION.lock'
eng.spec_path=lambda c:R/'cases'/c/'control/FROZEN_SPEC.json'
eng.spec_for=lambda c:copy.deepcopy(s)if c==case else (_ for _ in ()).throw(ValueError('fixture exact case only'))
eng.dispatch_binding=lambda c:copy.deepcopy(binding)
def transaction(label,callback):
 before=copy.deepcopy(registry);result=callback(registry);events.append(dict(operation=label,synthetic_authority_only=True,before_remaining=before['registered_future_requests'][goal]['remaining'],after_remaining=registry['registered_future_requests'][goal]['remaining']));return result
eng.transaction=transaction
eng.publish_own_write_carrier=lambda claims:events.append(dict(operation='MOCK_OWN_FIXTURE_WRITE_CARRIER_ONLY',claims=len(claims)))
eng.resource_gate=lambda spec,bind:events.append(dict(operation='MOCK_FIXTURE_RESOURCE_GATE_64M_RSS_1G_AS',host_cpu=bind['host_cpu']))
active_probe=copy.deepcopy(science_probe)
def prepare(c):
 assert c==case
 # Actual proposed pre-consume schema checks real corrected scientific fields first.
 schema.validate_spec_contract(active_probe,check_current_domain=True)
 assert s['native_boot_id']==active_probe['native_boot_id'] and s['native_mount_namespace']==active_probe['native_mount_namespace']
 assert sha(stub)==s['source_identity']['binary_sha256']
 assert s['pinned_files']==closure
 return dict(TEST_ONLY=True,status='PRIVATE_HOST_STUB_PREPARE_NOT_SCIENCE')
eng.prepare=prepare
# Prove missing boot is rejected before synthetic consume/fork, using exact run_native entry.
active_probe.pop('native_boot_id')
try:eng.run_native(case);negative=dict(PASS=False,error='unexpected start')
except Exception as ex:negative=dict(PASS="native_boot_id"in str(ex),error=type(ex).__name__+':'+str(ex))
negative['synthetic_consume_count']=len(registry['registered_future_requests'][goal]['consumed'])
assert negative['PASS']and negative['synthetic_consume_count']==0
active_probe=copy.deepcopy(science_probe)
# Actual sealed eventloop, Popen, loader/strace/helpers, verify_actual, streams, RSS,
# AS/CPU/nice, pipe/select, real PID closure and syscall parser are unchanged.
done=eng.run_native(case)
dump(O/'ACTUAL_EVENTLOOP_DONE.json',done);dump(O/'ISOLATED_TRANSACTION_EVENTS.json',events)
dump(O/'ISOLATED_AUTHORITY_FINAL.json',registry)
dump(O/'BEFORE_CONSUME_NEGATIVE.json',negative)
success=done['launcher_wait_returncode']==0 and done['stop_reason'] is None and done['native_simulator_observed'] is True and done['syscall_proof']['status']=='CLOSED_LOCAL_SYSCALL_INPUT_NETWORK_PROOF_PASS'
out=Path(done['output']);proof=read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')if(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json').exists()else None
receipt=dict(schema='EP_VECTOR_PRIVATE_REAL_CPU_STUB_HOST_EVENTLOOP_INTEGRATION_V1',status='PASS'if success else'FAIL',real_CPU_stub_process_started=True,GPU_application_or_simulator_started=False,science_budget_consumed=0,real_Native_authority_writes=0,shared_Native_route_writes=0,production_Core_ELF_changed=False,actual_sealed_engine_ref=ref(H/'ep_perf_native_wv_modes_draft.py'),actual_helper_ref=s['helpers_ref'],actual_raw_output_module_ref=s['output_module_ref'],stub_ELF_ref=ref(stub),stub_source_ref=ref(O/'host_cpu_stub.c'),isolated_root=str(R),before_consume_negative=negative,done_ref=ref(O/'ACTUAL_EVENTLOOP_DONE.json'),monitor_qualified_CPU_stub=done['native_simulator_observed'],GPU_drain='NOT_APPLICABLE_NOT_CLAIMED',GPU_application_NI='NOT_MEASURED',limitations=['Source/input/mode prepare, resource and authority bindings are explicit CPU-fixture mocks','No GPU application/framework execution, completion/drain validation or scientific acceptance','The tiny program opens only this fixture own dummy input list/member, not real Trace'],eventloop_result=dict(exitcode=done['launcher_wait_returncode'],stop_reason=done['stop_reason'],raw_stream_receipt=done['raw_stream_receipt'],peak_RSS=done['peak_process_tree_RSS_bytes'],peak_hot=done['peak_hot_bytes'],elapsed=done['elapsed_seconds']),actual_model_maps_ref=ref(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')if proof else None)
dump(O/'ACTUAL_PROCESS_HOST_INTEGRATION_RECEIPT.json',receipt)
print(json.dumps(dict(status=receipt['status'],stop_reason=done['stop_reason'],elapsed=done['elapsed_seconds'],RSS=done['peak_process_tree_RSS_bytes'],output=str(out))))
