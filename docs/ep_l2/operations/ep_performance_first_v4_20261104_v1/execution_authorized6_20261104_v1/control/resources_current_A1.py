from pathlib import Path
import hashlib,importlib.util
REQUEST='EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1'
HELPER=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_b/foreign_phys4_mapping_addendum_v4/resources_v4_with_phys4_foreign_v2.py')
HELPER_SHA='74d850fe5bb58d27245391e5e6ca95af339c86c5adda6f1451e0cde3999ceac9'
def helper():
 if hashlib.sha256(HELPER.read_bytes()).hexdigest()!=HELPER_SHA:raise ValueError("current strict foreign resource helper drift")
 s=importlib.util.spec_from_file_location("Main_current_strict_foreign_resources",HELPER);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return helper().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get("current_request")!=REQUEST:raise ValueError("cross-scope current resource snapshot")
 return helper().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return helper().forecast(input_id,history,policy=policy)
