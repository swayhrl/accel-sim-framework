"""Private exact4 resource wiring over successful V5 accounting. No authority writes."""
from pathlib import Path
import hashlib,importlib.util,json
P=Path
HERE=P(__file__).resolve().parent
EXEC=HERE.parent
BASE=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_d_workloads/resources_a2_v5.py')
BASE_SHA='68eceb9b98cc0b82303a5534633101d1111c5aebb4d18743b188fc5395619042'
V5=EXEC.parent.parent/'performance_first_v5_20261105_v1'
J=P('/root/data/ep_l2_full_workload_performance_20261027_v1')
V5=J/'research/performance_first_v5_20261105_v1'
REQUESTS={'CONV':'EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1','SCAN':'EP_L2_UMT1_SCAN_CF8D1C4D_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1'}
ROOTS={REQUESTS[g]:EXEC/'engineering_host'/g.lower()/'execution' for g in REQUESTS}
PRIOR_SCOPES={'EP_L2_PFV5_A_FWT_G32W8_COLD_PROOF_MATCHED3_V1':V5/'track_a_wv/host_private_candidate_v1/main_materialized/37e5a2db776190ee3f74/execution','EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1':V5/'track_b_fullf/host_private_candidate_v1/execution','EP_L2_PFV4_A2_3MM_SOURCE78_850_L100_V1':V5/'track_d_workloads/three_mm/execution'}
def need(v,m):
 if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def module(request):
 need(request in ROOTS,'unknown exact4 resource scope')
 need(sha(BASE)==BASE_SHA,'successful V5 resource accounting drift')
 sp=importlib.util.spec_from_file_location('umt_exact4_successful_resource_base_'+request,BASE);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 m.REQUEST=request;m.ROOT=ROOTS[request]
 previous=m.shared
 def shared():
  b=previous()
  for req,root in dict(PRIOR_SCOPES,**ROOTS).items():
   if req in b.SCOPES:need(b.SCOPES[req]==root,'exact resource scope collision '+req)
   b.SCOPES[req]=root
  return b
 m.shared=shared
 return m
class Scope:
 def __init__(self,request):need(request in ROOTS,'unknown exact4 scope');self.request=request
 def snapshot(self):
  s=module(self.request).snapshot()
  need(s['current_request']==self.request,'cross-request resource snapshot')
  # The inherited activity count uses only consumed rows in RUNNING/CONSUMED_BEFORE_FORK,
  # not the budget's top-level RUNNING state. Historical closed rows are not live models.
  s['UMT_exact_private_roots']={k:str(v)for k,v in ROOTS.items()}
  s['UMT_historical_budget_RUNNING_is_not_model_liveness']=True
  s['UMT_snapshot_is_readonly_not_science_admission']=True
  return s
 def admit(self,s,additional,writes,policy=None):
  need(s.get('current_request')==self.request,'cross-scope exact4 admission')
  p=dict(policy or {});p['max_global_EP_models']=10
  p['native_safety_floor_bytes']=max(p.get('native_safety_floor_bytes',0),5*(1<<30))
  return module(self.request).admit(s,additional,writes,p)
 def forecast(self,*a,**k):return module(self.request).forecast(*a,**k)
def for_scope(request):return Scope(request)
