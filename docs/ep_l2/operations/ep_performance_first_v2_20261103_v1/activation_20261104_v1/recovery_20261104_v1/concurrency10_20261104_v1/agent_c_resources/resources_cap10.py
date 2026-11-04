"""Prospective cap10 readonly adapter; immutable prior owner/resource math retained."""
import pathlib,hashlib,importlib.util
P=pathlib.Path
PRIOR=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/agent_c_resources/resources_recovery.py')
PRIOR_SHA='4e0e21cb4c5e20a4c996c2b89765e3bcdde42c2c16c51b9bcce2db8461ff8423'
G=1<<30
M=1<<20
MAX_EP_MODELS=10
def prior():
 if hashlib.sha256(PRIOR.read_bytes()).hexdigest()!=PRIOR_SHA:raise ValueError('prior recovery adapter drift')
 sp=importlib.util.spec_from_file_location('cap10_immutable_prior_recovery',PRIOR);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def snapshot(current_request):
 s=prior().snapshot(current_request)
 s.update(schema='EP_MAIN_PROSPECTIVE_CAP10_RESOURCE_SNAPSHOT_V1',max_global_EP_models=10,cap_is_prospective=True,existing_running_specs_unchanged=True)
 return s
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 r=prior();v=r.base_runtime()
 if s.get('current_request')not in v.NEW_SCOPES:raise ValueError('unknown/cross-scope current resource request')
 h=v.qualified_math()
 p=dict(v.DEFAULT_POLICY,**(policy or{}));own_floor=p.get('native_safety_floor_bytes',G)
 p['native_safety_floor_bytes']=max(own_floor,s.get('confirmed_foreign_native_floor_bytes',0))
 # Exact prior qualified admission math, excluding only frozen V2's prospective cap2 append.
 d=h.admit(s,own_pending_additional_RAM,own_remaining_writes,policy=p)
 count=s.get('global_EP_consumed_active_count')
 if type(count)is not int or count<0:d['hold_reasons'].append('UNKNOWN_GLOBAL_EP_ACTIVE_COUNT')
 elif count>=MAX_EP_MODELS:d['hold_reasons'].append('GLOBAL_EP_CAP10_REACHED')
 d['pass_admission']=not d['hold_reasons']
 d.update(own_emergency_floor_bytes=own_floor,confirmed_foreign_native_floor_bytes=s.get('confirmed_foreign_native_floor_bytes',0),restore_upper_bound_bytes=384*M,unknown_owners_fail_closed=True,prospective_global_EP_cap=10,existing_running_specs_unchanged=True,global_EP_active_count=count,new_science_permission=False,global_restore_mutex_proven=False)
 return d
def forecast(input_id,history,policy=None):return prior().forecast(input_id,history,policy=policy)
