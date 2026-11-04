"""B-only adapter to Main's exact private V4 scope extension; no science authority."""
from pathlib import Path
import hashlib,importlib.util
PATH=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/main/qualified_resources_v4/resources_v4.py');SHA='ee5cc3ba4c49ed95a1ac110e52dc0123d8f90c4a166da4f3ca00bc0e01b73303'
REQUEST='EP_L2_VECTOR1700_WV_DECOMPOSITION_FRESH_V4_20261104'
EXPECTED_ROOT=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v4_20261104_v1/track_b/private_execution/vector1700')
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('Main qualified V4 resource helper drift')
 s=importlib.util.spec_from_file_location('Main_qualified_V4_resources_for_B',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 if m.NEW_SCOPES.get(REQUEST)!=EXPECTED_ROOT:raise ValueError('Main V4 B request/root mismatch')
 return m
def snapshot():return shared().snapshot(REQUEST)
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):
 if s.get('current_request')!=REQUEST:raise ValueError('cross-family resource snapshot')
 return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy=policy)
def forecast(input_id,history,policy=None):return shared().forecast(input_id,history,policy=policy)
