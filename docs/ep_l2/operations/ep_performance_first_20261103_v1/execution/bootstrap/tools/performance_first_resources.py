"""Read-only finite performance-family resource adapter; no actors or mutations.
Frozen H mathematics and peer commitments retained. New scopes count each other.
"""
import pathlib,hashlib,importlib.util
P=pathlib.Path
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1')
X=J/'execution_performance_first_20261103_v1'
FROZEN=J/'execution_stencil_wv_20261103_v1/tools/stage2_resources_stencil.py'
FROZEN_SHA='4869dab32f58c99a6f9e41a53722f176d2965195f7a5636d56073cd64af1264a'
REQUESTS={'retention':'EP_L2_PF_RETENTION_CLASS_FWT_GEMM_20261103_V1','service':'EP_L2_PF_DRAM_SERVICE_FWT_GEMM_VECTOR4M_20261103_V1'}
def qualified_module():
 if hashlib.sha256(FROZEN.read_bytes()).hexdigest()!=FROZEN_SHA:raise ValueError('frozen prior scope adapter drift')
 sp=importlib.util.spec_from_file_location('pf_frozen_readonly_resource_math',FROZEN);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 m.SCOPES=dict(m.SCOPES,**{q:X/g for g,q in REQUESTS.items()})
 return m
def snapshot(current_request):
 if current_request not in REQUESTS.values():raise ValueError('unknown current performance-family scope')
 s=qualified_module().snapshot(current_request)
 s.update(schema='EP_PERFORMANCE_FIRST_SCOPED_RESOURCE_SNAPSHOT_V1',performance_family_scopes=REQUESTS,prior_scope_adapter_sha256=FROZEN_SHA,dispatcher_created=False)
 return s
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 return qualified_module().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return qualified_module().forecast(input_id,history,policy=policy)
DEFAULT_POLICY=dict(qualified_module().DEFAULT_POLICY)
