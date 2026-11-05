import pathlib,hashlib,importlib.util
P=pathlib.Path;PATH=P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_a_wv/host_private_candidate_v1/resources_a_v5.py');SHA='3c3895390de3eca6e462bff169b45fd7d1d520f792e9b9e0b5bdcfaf05e0667f'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('resource mapping drift')
 s=importlib.util.spec_from_file_location('A_private_resources',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return shared().snapshot()
def admit(s,own_pending_additional_RAM,own_remaining_writes,policy=None):return shared().admit(s,own_pending_additional_RAM,own_remaining_writes,policy)
def forecast(*a,**k):return shared().forecast(*a,**k)
