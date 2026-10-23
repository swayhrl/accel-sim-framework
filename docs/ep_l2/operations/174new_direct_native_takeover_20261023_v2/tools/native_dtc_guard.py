"""Target adapter over unchanged BA telemetry and resource decision modules.

No launcher/signals/ledger API. Original RuntimePolicyB freshness, semantic
retirement, OOM/swap/memory persistence and warning-only I/O policy are retained.
The user-approved Target preflight replaces Source-only host identity admission;
samples below always report the real Target hostname and actual devices.
"""
import os,pathlib,sys,time,importlib.util
P=pathlib.Path;ROOT=P('/root/data/ep_l2_dtc_l1_native_v2')
AG8=ROOT/'DTC/src/owner-control/docs/dtc_l1/review_packs/DTC_AG8R1_FINITE_RESUME_20261021_V1/prepared_ag8r1'
AG6=ROOT/'DTC/src/owner-control/docs/dtc_l1/iscas2027/evidence_closure_20261019_v1/execution/prepared_ag6'
sys.path.insert(0,str(AG8))
from telemetry_receiver import TelemetryReceiver
from runtime_io_warning import RuntimePolicyB
spec=importlib.util.spec_from_file_location('native_exact_resources_v2',AG6/'resources_v2.py')
resources=importlib.util.module_from_spec(spec);spec.loader.exec_module(resources)

def snapshot(output):
 c=P('/sys/fs/cgroup');vm={k:int(v) for k,v in (x.split() for x in P('/proc/vmstat').read_text().splitlines())}
 group={k:(c/k).read_text().strip() for k in ['memory.max','memory.current','memory.swap.current','memory.pressure','io.pressure']}
 group['events']={k:int(v) for k,v in (x.split() for x in (c/'memory.events').read_text().splitlines())}
 sample={'monotonic_ns':time.monotonic_ns(),'host':os.uname().nodename,'uid':os.getuid(),'host_MemAvailable_bytes':int(next(x.split()[1] for x in P('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024,'cgroup':group,'pressure':{k:resources.parsed_pressure((P('/proc/pressure')/k).read_text()) for k in ['memory','io']},'pswpin':vm['pswpin'],'pswpout':vm['pswpout']}
 return resources.enrich(sample,output)

class NativeDTCGuard:
 def __init__(self,channel,binding,output,started_ns):
  self.receiver=TelemetryReceiver(channel,binding,started_ns=started_ns,opt_in=True)
  self.policy=RuntimePolicyB(snapshot(output),output,resource_module=resources,started_ns=started_ns,opt_in=True)
  self.last_full=time.monotonic_ns();self.last_faults=0
 def drain(self):return self.receiver.drain(time.monotonic_ns)
 def sample(self,output,safety_checks,io_impact,own_major_faults):
  current=snapshot(output)
  decision=self.policy.observe(current,own_major_faults,self.last_faults,progress=self.receiver.last_semantic,safety_checks=safety_checks,io_impact=io_impact)
  self.last_faults=own_major_faults;self.last_full=current['monotonic_ns']
  return {'sample':current,'decision':decision}
 def quick_stop(self):return self.policy.quick_stop()
