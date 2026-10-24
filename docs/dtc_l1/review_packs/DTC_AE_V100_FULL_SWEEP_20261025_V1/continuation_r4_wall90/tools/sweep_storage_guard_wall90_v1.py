"""Independent future-start wall profile; original receiver and non-wall guards."""
import pathlib,sys,importlib.util,hashlib
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1')
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_native_v2/tools')
import native_dtc_guard as original
from sweep_storage_guard import native_admission
p=T/'tools/runtime_policy_wall90_v1.py'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='d1a3f21ce1c9eac89b8428f0732000d81936577d080b7bcf1c48ebe38980f187'
s=importlib.util.spec_from_file_location('wall90_frozen_policy',p);wall=importlib.util.module_from_spec(s);s.loader.exec_module(wall)
class NativeDTCGuard(original.NativeDTCGuard):
 def __init__(self,channel,binding,output,started_ns):
  super().__init__(channel,binding,output,started_ns)
  self.policy=wall.RuntimePolicyB(self.policy.original.first,output,resource_module=original.resources,started_ns=started_ns,opt_in=True)
