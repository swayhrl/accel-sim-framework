"""Exact V4 private resource wiring; no registration, mutation, actors or science permission."""
from pathlib import Path
import hashlib,importlib.util
BASE=Path("/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/agent_c_resources/resources_v3.py")
BASE_SHA="ebaacc5efecf4e2162532b0722822763df55fb5cab05dbec0e0eaa161e6465bd"
ROOT=Path("/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1")
NEW_SCOPES={
 "EP_L2_PFV4_A1_STENCIL_SOURCE78_850_L100_V1": ROOT/"track_a/resource_admission_followup_v2/A1/execution",
 "EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1": ROOT/"track_a/resource_admission_followup_v2/A3/execution",
 "EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104": ROOT/"track_b/private_execution/vector1700",
}
def need(v,m):
 if not v:raise ValueError(m)
def shared():
 need(hashlib.sha256(BASE.read_bytes()).hexdigest()==BASE_SHA,"exact prior resource source drift")
 sp=importlib.util.spec_from_file_location("pfv4_private_prior_resources",BASE)
 m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 before=dict(m.SCOPES)
 need(not(set(NEW_SCOPES)&set(before)),"V4 scope collides with old resource scope")
 m.SCOPES.update(NEW_SCOPES)
 need(all(m.SCOPES[k]==v for k,v in before.items()),"old resource mappings changed")
 return m
def snapshot(request):
 need(request in NEW_SCOPES,"outside exact V4 resource scopes")
 s=shared().snapshot(request)
 need(s.get("current_request")==request,"resource snapshot request mismatch")
 s["V4_private_scope_map"]={k:str(v) for k,v in NEW_SCOPES.items()}
 s["V4_resource_mapping_is_not_science_authorization"]=True
 return s
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 request=s.get("current_request")
 need(request in NEW_SCOPES,"outside exact V4 resource scopes")
 need(s.get("current_scope_registered") is True,"V4_REQUEST_NOT_REGISTERED")
 p=dict(policy or {})
 need(p.get("max_global_EP_models",10)in(2,10),"unapproved V4 model cap")
 p["max_global_EP_models"]=p.get("max_global_EP_models",10)
 p["native_safety_floor_bytes"]=max(p.get("native_safety_floor_bytes",0),5*(1<<30))
 return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=p)
def forecast(input_id,history,policy=None):
 return shared().forecast(input_id,history,policy=policy)
