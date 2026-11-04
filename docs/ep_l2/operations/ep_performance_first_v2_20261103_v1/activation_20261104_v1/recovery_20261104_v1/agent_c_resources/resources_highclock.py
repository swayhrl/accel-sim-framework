"""Readonly current-family recovery wrapper; cannot grant scientific permission."""
import pathlib,hashlib,importlib.util
P=pathlib.Path;PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1/activation_20261104_v1/recovery_20261104_v1/agent_c_resources/resources_recovery.py');SHA='4e0e21cb4c5e20a4c996c2b89765e3bcdde42c2c16c51b9bcce2db8461ff8423';REQUEST='EP_L2_CC_CAM_REPAIRED_VECTOR4M_850_1275_1700_V1'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('recovery resource adapter drift')
 s=importlib.util.spec_from_file_location('known_DTC16_readonly_recovery',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get('current_request')!=REQUEST:raise ValueError('cross-family snapshot rejected')
 return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
