"""Read-only V3 configuration assembly. Never registers, installs or writes."""
import pathlib,json,hashlib,importlib.util
P=pathlib.Path;ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def source_set(source_paths):
 assert set(source_paths)=={'entry','frontend','producer','extra_strict','consumer'}
 return {k:sha(v)for k,v in source_paths.items()}
def expected_pins(policy_source_path,old_pins=None):
 pins=dict(old_pins if old_pins is not None else read(A/'agents/B/strace_bpf_future_entry_v2/DELIVERY.json')['expected_pins']);pins[str(policy_source_path)]=sha(policy_source_path)
 for p,h in pins.items():assert sha(p)==h
 return pins
def make_configuration(source_paths,QA_path,readback_path,canary4_prerequisite_path,*,policy_source_path=None,v2_entry_path=None,old_pins=None):
 """All arguments must identify real Main-controlled immutable artifacts.

 Missing real4 prerequisite file prevents even complete active-config assembly.
 This function still creates no permission; producer.validate and owner install
 authenticate the full real4 replay and original native lease separately.
 """
 source_paths={k:str(P(v))for k,v in source_paths.items()};policy_source_path=P(policy_source_path or A/'agents/E/strace_bpf_future_policy_v3/future_policy.py');v2_entry_path=P(v2_entry_path or ROOT/'control/operational_amendments/strace_bpf_future_entry_v2/native-entry/bin/experiment')
 sources=source_set(source_paths);pins=expected_pins(policy_source_path,old_pins);qa=read(QA_path);back=read(readback_path)
 assert qa['status']=='PASS'and all(qa[k]is True for k in ['native_prefix_qualified','extra_strict_qualified','consumer_archive_qualified'])and back['verified']is True
 assert qa['qualified_sources']==back['qualified_sources']==sources and qa['expected_pins']==back['expected_pins']==pins and back['QA_sha256']==sha(QA_path)
 ir=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json';exclusion=A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json';mf=ROOT/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'
 return dict(schema='DTC_STRACE_FUTURE_ENTRY_V3',request='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1',overlay_id='DTC_STRACE_FUTURE_ENTRY_V3',status='ACTIVE_FUTURE_SCOPED',root=str(ROOT),qualification_only=False,future_primary_policy='MATRIX_REGISTERED_UNSPENT_BPF_REQUIRED',future_ir_policy='EXACT_REGISTERED_IR11_BPF_REQUIRED',source_paths=source_paths,qualified_sources=sources,expected_pins=pins,QA_path=str(QA_path),QA_sha256=sha(QA_path),readback_path=str(readback_path),readback_sha256=sha(readback_path),native_source_path=str(ROOT/'tools/l2_native.py'),memory_frontend_path=str(mf),memory_frontend_sha256=sha(mf),memory_configuration_path=str(ROOT/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json'),default_native_entry='/root/data/ep_l2_dtc_l1_native_v2/bin/native',v2_entry_path=str(v2_entry_path),v2_entry_sha256=sha(v2_entry_path),exclusion_contract_path=str(exclusion),exclusion_contract_sha256=sha(exclusion),policy_source_path=str(policy_source_path),policy_source_sha256=sha(policy_source_path),ir_plan_path=str(ir),ir_plan_sha256=sha(ir),canary4_prerequisite_path=str(canary4_prerequisite_path),canary4_prerequisite_sha256=sha(canary4_prerequisite_path))
def operational_record(configuration):
 path=configuration['source_paths']['producer'];assert sha(path)==configuration['qualified_sources']['producer'];s=importlib.util.spec_from_file_location('V3_record_source_only',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 return dict(m.record(configuration),status='ACTIVE') # return data only; caller writes authority outside this helper
