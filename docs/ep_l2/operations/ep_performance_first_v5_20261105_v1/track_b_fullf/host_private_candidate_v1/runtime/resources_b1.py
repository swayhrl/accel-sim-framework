"""Private exact new-request resource mapping; original accounting retained."""
import importlib.util,hashlib
from pathlib import Path
BASE={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/agent_c_resources/resources_v3.py', 'sha256': 'ebaacc5efecf4e2162532b0722822763df55fb5cab05dbec0e0eaa161e6465bd'}
REQUEST='EP_L2_PFV5_B1_VECTOR4M1700_PRESSURE_EPOCH_MATCHED_F_V1'
EXEC_ROOT='/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_b_fullf/host_private_candidate_v1/execution'
def impl():
 p=Path(BASE['path'])
 if hashlib.sha256(p.read_bytes()).hexdigest()!=BASE['sha256']:raise ValueError('original resource implementation drift')
 s=importlib.util.spec_from_file_location('pfv5_b1_frozen_resources',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.SCOPES[REQUEST]=Path(EXEC_ROOT)
 return m
def snapshot():return impl().snapshot(REQUEST)
def admit(s,additional,writes,policy):
 if not s.get('current_scope_registered',False):
  return dict(pass_admission=False,reason='NEW_EXACT_REQUEST_NOT_REGISTERED',scientific_permission=False)
 return impl().admit(s,additional,writes,policy=policy)
