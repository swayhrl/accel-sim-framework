import types
"""New request only: original authenticated telemetry, explicit pressure-admission policy."""
from pathlib import Path
import importlib.util,hashlib,sys,time
R=Path('/root/data/dtc_perf_first_v2_codesign16_layout_r1_20261105_v1');T=Path('/root/data/dtc_main_v100_sweep_20261025_v1')
sys.path.insert(0,'/root/data/ep_l2_dtc_l1_native_v2/tools')
import native_dtc_guard as original

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n,p,h):
 assert sha(p)==h
 m=types.ModuleType(n);m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
receiver=load('perf16r1_original_cap1m_receiver',T/'telemetry_v2/telemetry_receiver_cap1m.py','f523975b9780b498b988e2b3145ba5b4aebdef4d0e9b0146392d3a31a99a4ec1')
POLICY_SHA='193eee1b868b9f204d69e17df961ec9db47d6c3fd2f96ee8524ebc381639456d'
policy=load('perf16r1_independent_runtime_policy',R/'tools/perf16r1_guard_policy.py',POLICY_SHA)
class NativeDTCGuard:
 def __init__(self,channel,binding,output,started_ns):
  self.receiver=receiver.TelemetryReceiver(channel,binding,started_ns=started_ns,opt_in=True)
  self.policy=policy.RuntimePolicyB(original.snapshot(output),output,resource_module=original.resources,started_ns=started_ns,opt_in=True)
  self.last_full=started_ns;self.last_faults=0
 def drain(self):return self.receiver.drain(time.monotonic_ns)
 def sample(self,output,safety_checks,io_impact,own_major_faults):
  current=original.snapshot(output);decision=self.policy.observe(current,own_major_faults,self.last_faults,progress=self.receiver.last_semantic,safety_checks=safety_checks,io_impact=io_impact);self.last_faults=own_major_faults;self.last_full=current['monotonic_ns']
  return dict(sample=current,decision=decision,runtime_policy_binding=dict(schema='DTC_PERFV2_CODESIGN16_LAYOUT_R1_ADMISSION_PRESSURE_ONLY_RUNTIME_V1',policy_sha256=POLICY_SHA,guard_sha256=sha(__file__),original_pressure_STOPs_not_inherited=True,telemetry_receiver_sha256=sha(receiver.__file__)))
 def quick_stop(self):return self.policy.quick_stop()
