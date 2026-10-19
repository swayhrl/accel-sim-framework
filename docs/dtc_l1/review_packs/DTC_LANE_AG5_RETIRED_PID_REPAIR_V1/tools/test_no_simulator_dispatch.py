"""Launch-policy negatives must reject before os.fork; no real target execution."""
from common import *
from mapping_roles import Reject
import guarded_process as guard
from unittest.mock import patch

def main():
 rows=[]
 cases=[('SIMULATION','/unexecuted/accel-sim.out','CPU_ONLY_NO_SIMULATION_DISPATCH'),('CPU_FIXTURE','/unexecuted/accel-sim.out','CPU_TARGET_NOT_FIXED_FIXTURE'),('CPU_FIXTURE',str(BUILD/'ag5-cpu-arbitrary'),'CPU_TARGET_NOT_FIXED_FIXTURE')]
 for purpose,target,reason in cases:
  with patch.object(guard.os,'fork',side_effect=AssertionError('FORBIDDEN_FORK')) as fork:
   try:guard.run_guarded([target],{}, {target:{}},RAW/'never-created',purpose,1,capability=lambda *a:None)
   except Reject as e:
    assert str(e)==reason and fork.call_count==0
    rows.append(dict(purpose=purpose,target=target,status='EXPECTED_REJECT',reason=str(e),fork_calls=0))
   else:raise AssertionError('NEGATIVE_ACCEPTED')
 assert not (RAW/'never-created').exists()
 write(PACK/'NO_SIMULATOR_DISPATCH_TESTS.json',dict(status='PASS',cases=rows,simulator_starts=0,scope='Shipped launch policy and call sites; not an adversarial executable-content sandbox'))
 print('PASS_NO_SIMULATOR_DISPATCH',len(rows))
if __name__=='__main__':main()
