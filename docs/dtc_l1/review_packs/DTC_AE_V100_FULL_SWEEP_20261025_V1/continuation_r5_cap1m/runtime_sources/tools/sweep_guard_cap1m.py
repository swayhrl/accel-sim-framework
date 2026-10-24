"""Source-pinned observational receiver capacity plus explicit WALL90 profile."""
import pathlib,sys,importlib.util,hashlib
T=pathlib.Path('/root/data/dtc_main_v100_sweep_20261025_v1');sys.path.insert(0,'/root/data/ep_l2_dtc_l1_native_v2/tools')
import native_dtc_guard as original
from sweep_storage_guard import native_admission
def load(name,p,expected):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
receiver=load('observational_cap1m_receiver',T/'telemetry_v2/telemetry_receiver_cap1m.py','f523975b9780b498b988e2b3145ba5b4aebdef4d0e9b0146392d3a31a99a4ec1')
wall=load('observational_cap1m_wall90',T/'tools/runtime_policy_wall90_v1.py','d1a3f21ce1c9eac89b8428f0732000d81936577d080b7bcf1c48ebe38980f187')
class NativeDTCGuard(original.NativeDTCGuard):
 def __init__(self,channel,binding,output,started_ns):
  super().__init__(channel,binding,output,started_ns)
  self.receiver=receiver.TelemetryReceiver(channel,binding,started_ns=started_ns,opt_in=True)
  self.policy=wall.RuntimePolicyB(self.policy.original.first,output,resource_module=original.resources,started_ns=started_ns,opt_in=True)
