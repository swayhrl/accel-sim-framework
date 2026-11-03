"""Read-only broad observation config construction; no publication/install."""
import pathlib,json,hashlib,copy
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1')
ID='DTC_STRACE_BROAD_SHARED_CPU_V1';REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ROLES={'entry','frontend','producer','extra_strict','consumer'}
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def source_set(paths):
 assert set(paths)==ROLES
 return{k:sha(v)for k,v in paths.items()}
def expected_pins(resource_configuration_path,policy_source_path=None):
 resource=read(resource_configuration_path);pins=copy.deepcopy(resource['expected_pins']);policy=P(policy_source_path or R/'control/operational_amendments/strace_bpf_future_entry_v3/future_policy.py')
 for path in [R/'tools/l2_native.py',P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_native_cap1m.py'),policy,P('/root/data/ep_l2_dtc_l1_native_v2/bin/native')]:pins[str(path)]=sha(path)
 # Mutable ACTIVE files are not permanent source pins. They are captured by
 # immutable per-birth cfg/snapshot SHA and historical source-bound replay.
 return pins
def make_configuration(resource_configuration_path,source_paths,QA_path,readback_path,policy_source_path=None,root=R,qualification_only=False):
 resource=read(resource_configuration_path);app=read(resource['broad_approval_path']);gate=app['actual_gate'];policy=P(policy_source_path or R/'control/operational_amendments/strace_bpf_future_entry_v3/future_policy.py');v2=A/'agents/B/strace_bpf_future_entry_v2/native-entry/bin/experiment';exclusion=A/'coordinator/bpf_canary_orchestration_v1/ENGINEERING_EXCLUSION_CONTRACT.json';ir=A/'agents/B/incident11_recovery_trials_plan_v1/DRAFT_PLAN.json'
 assert resource['root']==str(root)and resource['qualification_only']is qualification_only
 return dict(schema=ID,request=REQ,overlay_id=ID,status='ACTIVE_FUTURE_SCOPED',root=str(root),qualification_only=qualification_only,future_primary_policy='MATRIX_REGISTERED_UNSPENT_BPF_REQUIRED',future_ir_policy='EXACT_REGISTERED_IR11_BPF_REQUIRED',source_paths={k:str(v)for k,v in source_paths.items()},qualified_sources=source_set(source_paths),expected_pins=expected_pins(resource_configuration_path,policy),QA_path=str(QA_path),QA_sha256=sha(QA_path),readback_path=str(readback_path),readback_sha256=sha(readback_path),native_source_path=str(R/'tools/l2_native.py'),memory_frontend_path=str(R/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'),memory_frontend_sha256=sha(R/'control/operational_amendments/future_memory_admission_v1/memory_frontend.py'),memory_configuration_path=str(resource_configuration_path),resource_configuration_path=str(resource_configuration_path),resource_configuration_sha256=sha(resource_configuration_path),default_native_entry='/root/data/ep_l2_dtc_l1_native_v2/bin/native',v2_entry_path=str(v2),v2_entry_sha256=sha(v2),exclusion_contract_path=str(exclusion),exclusion_contract_sha256=sha(exclusion),policy_source_path=str(policy),policy_source_sha256=sha(policy),ir_plan_path=str(ir),ir_plan_sha256=sha(ir),canary4_prerequisite_path=gate['path'],canary4_prerequisite_sha256=gate['sha256'],broad_approval_path=resource['broad_approval_path'],broad_approval_sha256=resource['broad_approval_sha256'],scope_contract_path=resource['scope_contract_path'],scope_contract_sha256=resource['scope_contract_sha256'])
def operational_record(cfg):
 return dict(request=REQ,overlay_id=ID,configuration_sha256=hashlib.sha256((json.dumps(cfg,sort_keys=True,indent=2)+'\n').encode()).hexdigest(),qualified_sources=cfg['qualified_sources'],expected_pins=cfg['expected_pins'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],future_primary_policy=cfg['future_primary_policy'],future_ir_policy=cfg['future_ir_policy'],policy_source_sha256=cfg['policy_source_sha256'],canary4_prerequisite_sha256=cfg['canary4_prerequisite_sha256'],resource_configuration_sha256=cfg['resource_configuration_sha256'],broad_approval_sha256=cfg['broad_approval_sha256'],scope_contract_sha256=cfg['scope_contract_sha256'],status='ACTIVE')
