from pathlib import Path
import hashlib,importlib.util
PATH=Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_d_workloads/resources_a2_v5.py');SHA='68eceb9b98cc0b82303a5534633101d1111c5aebb4d18743b188fc5395619042'
def shared():
 if hashlib.sha256(PATH.read_bytes()).hexdigest()!=SHA:raise ValueError('V5 resource mapper drift')
 s=importlib.util.spec_from_file_location('v5_A2_qualified_resources',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def snapshot():return shared().snapshot()
def admit(s,a,w,policy=None):return shared().admit(s,a,w,policy)
def forecast(i,h,policy=None):return shared().forecast(i,h,policy)
