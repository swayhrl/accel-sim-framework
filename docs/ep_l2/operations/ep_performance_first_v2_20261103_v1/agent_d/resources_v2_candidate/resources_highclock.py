"""Strict current-family readonly wrapper; scientific permission is separate."""
import pathlib,hashlib,importlib.util
P=pathlib.Path;PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/agent_d/resources_v2_candidate/resources_v2.py');SHA='cd11412b41a754fddbd66c836a4fda59ac4f31683b0677d9f67faa7bd5652da6';REQUEST='EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('V2 resource adapter drift')
 s=importlib.util.spec_from_file_location('readonly_v2_scopes',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get('current_request')!=REQUEST:raise ValueError('cross-family snapshot rejected')
 return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
