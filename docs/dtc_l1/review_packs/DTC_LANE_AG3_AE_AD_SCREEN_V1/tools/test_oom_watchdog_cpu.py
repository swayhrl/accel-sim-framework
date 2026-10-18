"""Fault-injected cgroup reader and real owned CPU pidfd STOP; not host OOM."""
from common import *
from unittest.mock import patch
from guarded_process import run_guarded
import oom_watchdog

def main():
 root=RAW/'cpu-qualification/oom-watchdog-final';root.mkdir(parents=True,exist_ok=False)
 manifests=json.loads((PACK/'PRODUCTION_WRAPPER_CPU.json').read_text())['manifests'];target=str(BUILD/'ag3-cpu-production-wrapper')
 env=dict(PATH='/usr/bin:/bin',LANG='C',LC_ALL='C',CUDA_VISIBLE_DEVICES='',LD_LIBRARY_PATH=str(BUILD/'combined-final'))
 real=oom_watchdog.start;results=[]
 for name in ['new_oom_kill','reader_failure']:
  eventfile=root/(name+'.events');state={}
  def factory(pid,destination,event_path=None,baseline=None):
   state.update(baseline)
   eventfile.write_text('\n'.join(k+' '+str(v) for k,v in baseline.items())+'\n')
   return real(pid,destination,event_path=eventfile,baseline=baseline)
  fired=[False]
  def inject(pid,full):
   if not fired[0]:
    if name=='new_oom_kill':
     changed=dict(state);changed['oom_kill']+=1;eventfile.write_text('\n'.join(k+' '+str(v) for k,v in changed.items())+'\n')
    else:eventfile.unlink()
    fired[0]=True
  with patch.object(oom_watchdog,'start',factory):
   result=run_guarded([target,'hang'],env,manifests,root/name,'CPU_FIXTURE',10,observer=inject)
  assert result['status']=='STOP_GUARDED_PROCESS' and result['owned_children_live']==0
  assert result['forced_reason'].startswith('NEW_CGROUP_OOM_OR_OOM_KILL' if name=='new_oom_kill' else 'OOM_WATCHDOG_FAILURE'),result
  results.append(dict(case=name,injected_private_reader_not_actual_cgroup=True,result=result))
 write(PACK/'OOM_WATCHDOG_CPU_TESTS.json',dict(status='PASS_CPU_OWNED_PIDFD_STOP_AND_READER_FAILURE',cases=results,watchdog_sha256=sha(PACK/'tools/oom_watchdog.py'),real_simulator_starts=0,real_cgroup_writes=0,foreign_signals=0))
 print('PASS 2 CPU-only OOM reader/pidfd lifecycle controls')
if __name__=='__main__':main()
