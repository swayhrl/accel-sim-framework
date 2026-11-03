"""Read-only exact current-scope wrapper; imports no actors."""
import pathlib,hashlib,importlib.util
P=pathlib.Path
PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_stencil_wv_20261103_v1/tools/stage2_resources_stencil.py');SHA='4869dab32f58c99a6f9e41a53722f176d2965195f7a5636d56073cd64af1264a';REQUEST='EP_L2_WV_STENCIL_DECOMPOSITION_20261103_V1'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('shared resource module drift')
 sp=importlib.util.spec_from_file_location('stage2_resources_shared',PATH);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
