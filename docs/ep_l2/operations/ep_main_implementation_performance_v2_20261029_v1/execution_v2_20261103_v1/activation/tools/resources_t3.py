"""Read-only exact current-scope wrapper; imports no actors."""
import pathlib,hashlib,importlib.util
P=pathlib.Path
PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_v2_20261103_v1/tools/stage2_resources.py');SHA='23a4f6afb11ecbe2a0171ec3ffe7f7a3016725973293397ff3a4bfac55a90f67';REQUEST='EP_L2_T_THREE_ARM_CAUSAL_CONV16X8_V1'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('shared resource module drift')
 sp=importlib.util.spec_from_file_location('stage2_resources_shared',PATH);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
