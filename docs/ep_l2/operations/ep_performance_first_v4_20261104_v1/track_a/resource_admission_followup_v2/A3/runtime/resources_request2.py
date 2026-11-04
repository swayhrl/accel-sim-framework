# Exact Source78 request2 resource wiring; Main-owned additive helper, read-only API.
import pathlib,hashlib,importlib.util
PATH=pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/main/qualified_resources_v4/resources_v4.py');SHA='ee5cc3ba4c49ed95a1ac110e52dc0123d8f90c4a166da4f3ca00bc0e01b73303';REQUEST='EP_L2_PFV4_A3_TRANSPOSE_SOURCE78_850_L100_V1'
def shared():
    if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('Main V4 resource dependency drift')
    sp=importlib.util.spec_from_file_location('Main_v4_exact_resources',PATH);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
    if s.get('current_request')!=REQUEST:raise ValueError('cross-family resource snapshot')
    return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
