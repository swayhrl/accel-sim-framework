"""CPU-only PID evidence boundary tests; no Torch, NVML, CUDA or GPU lock."""
from ownership import classify_snapshot

def test():
 known={100:{'start_ticks':123,'pgid':100}}
 live={100:{'start_ticks':123,'pgid':100,'state':'S'}}
 empty={};exited={100:{'start_ticks':123,'pgid':100,'state':'Z'}}
 def check(rows,a,b,terminal,reason):
  x=classify_snapshot(rows,known,a,b,terminal);assert x['stop_reason']==reason
  return x
 check([(100,20)],live,live,False,None)
 assert check([(100,20)],live,empty,True,None)['classification'][0]['classification'].startswith('OWN_EXIT')
 check([(100,20)],empty,empty,True,None)
 check([(100,20)],live,exited,True,None)
 check([(100,20)],empty,empty,False,'GPU_EXCLUSIVITY_UNRESOLVED')
 reused={100:{'start_ticks':124,'pgid':100,'state':'S'}}
 check([(100,20)],live,reused,True,'GPU_EXCLUSIVITY_UNRESOLVED')
 check([(999,20)],{}, {},True,'EXTERNAL_GPU_TASK_STOP')
 check([(100,20),(999,1)],live,live,False,'EXTERNAL_GPU_TASK_STOP')
 # Same PGID does not grant ownership to an unregistered third-party PID.
 check([(999,1)],{}, {999:{'start_ticks':1,'pgid':100,'state':'S'}},True,'EXTERNAL_GPU_TASK_STOP')
 check([],empty,empty,True,None)
 print('PASS_10_PID_EVIDENCE_CASES_NO_GPU')

if __name__=='__main__':test()
