"""Parent-side fault injection and forced-stop lifecycle of CPU targets only."""
from common import *
from unittest.mock import patch
import guarded_process as guard
from mapping_roles import Sequence

def main():
 manifests=json.loads((PACK/'PRODUCTION_WRAPPER_CPU.json').read_text())['manifests'];target=str(BUILD/'ag3-cpu-production-wrapper')
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',LD_LIBRARY_PATH=str(BUILD/'combined-final'))
 dest=RAW/'cpu-qualification/guard-faults-final';dest.mkdir(parents=True,exist_ok=False);results=[]
 def run(label,observer=None):
  r=guard.run_guarded([target],env,manifests,dest/label,'CPU_FIXTURE',10,observer=observer)
  assert r['status']=='STOP_GUARDED_PROCESS' and r['owned_children_live']==0,label
  results.append(dict(case=label,result=r));return r
 with patch.object(guard.os,'fork',side_effect=OSError('CPU_INJECTED_FORK_FAILURE')):
  r=run('fork_failure');assert r['actual_fork_children']==0 and r['simulator_starts']==0
 with patch.object(Sequence,'observe',side_effect=OSError('CPU_INJECTED_MAP_READ_FAILURE')):
  r=run('maps_read_failure');assert 'CPU_INJECTED_MAP_READ_FAILURE' in r['forced_reason']
 def observer_error(pid,full):raise OSError('CPU_INJECTED_OBSERVER_FAILURE')
 r=run('observer_exception',observer_error);assert 'CPU_INJECTED_OBSERVER_FAILURE' in r['forced_reason']
 r=run('forced_resource_stop',lambda pid,full:'CPU_TEST_FORCED_RESOURCE_STOP');assert r['forced_reason']=='CPU_TEST_FORCED_RESOURCE_STOP'
 original=Sequence.observe
 def remove_confirmed(self,text,exe):
  result=original(self,text,exe)
  if self.cache_disappearances>=1 and '/etc/ld.so.cache' not in result['files']:
   key=next(k for k,v in self.registry.items() if v['role']=='ELF_SHARED_OBJECT')
   # Inject an impossible validator result after the first closed startup,
   # then the next capture: the runner must not silently drop this file.
   if getattr(self,'cpu_seen_closed',False):result['files'].pop(key,None)
   self.cpu_seen_closed=True
  return result
 with patch.object(Sequence,'observe',remove_confirmed):
  r=run('confirmed_ELF_disappearance');assert 'REGISTERED_ELF_DISAPPEARED_AFTER_STARTUP' in r['forced_reason']
 write(PACK/'GUARD_EXCEPTION_CPU_TESTS.json',dict(status='PASS_FIVE_PARENT_FAULT_AND_FORCE_STOP_CASES',cases=results,guard_sha256=sha(PACK/'tools/guarded_process.py'),real_simulator_starts=0,disappearance_case='controlled parent validator fault, not an actual library unmap claim'))
 print(json.dumps(dict(status='PASS_GUARD_FAULTS_CPU',cases=len(results),real_simulator_starts=0)))
if __name__=='__main__':main()
