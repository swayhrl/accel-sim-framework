"""Exact current owner wrapper; every other owner remains foreign."""
import pathlib,hashlib,importlib.util
P=pathlib.Path
PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/tools/performance_first_resources.py');SHA='b2a2412fed6dcb3c2cd97da59b3368a58dd17dd794ff34a1b35ed1d33fec3cf4';REQUEST='EP_L2_PF_RETENTION_CLASS_FWT_GEMM_20261103_V1'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('performance-family shared adapter drift')
 s=importlib.util.spec_from_file_location('performance_first_readonly_resources',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get("current_request")!=REQUEST:raise ValueError("cross-scope resource snapshot")
 return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
