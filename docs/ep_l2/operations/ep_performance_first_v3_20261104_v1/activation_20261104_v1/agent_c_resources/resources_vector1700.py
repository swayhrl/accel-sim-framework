import pathlib,hashlib,importlib.util
PATH=pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v3_20261104_v1/activation_20261104_v1/agent_c_resources/resources_v3.py');SHA='ebaacc5efecf4e2162532b0722822763df55fb5cab05dbec0e0eaa161e6465bd';REQUEST='EP_L2_VECTOR1700_WV_DECOMPOSITION_V1_20261104'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('V3 resource adapter drift')
 s=importlib.util.spec_from_file_location('readonly_V3_scoped_resources',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get('current_request')!=REQUEST:raise ValueError('cross-family resource snapshot')
 return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
