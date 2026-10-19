"""Pure production BASE/budget gate tests, explicit synthetic CPU receipts."""
from common import *
import run_screen as runner
from unittest.mock import patch
import time

def main():
 dest=RAW/'cpu-qualification'/('paired-gates-'+str(time.time_ns()));dest.mkdir(parents=True)
 specs=[dict(point=point,workload='GEMM' if 'GEMM' in point else 'Gaussian',arm=point.split('_')[0],attempt_uuid=f'{i+1:08x}-2222-4222-8222-222222222222') for i,point in enumerate(runner.ORDER)]
 rows=[]
 def reject(name,fn):
  try:fn()
  except ValueError as e:rows.append(dict(case=name,status='EXPECTED_REJECT',reason=str(e)));return
  raise AssertionError('NEGATIVE_ACCEPTED:'+name)
 def receipt(index,accepted=True,valid_uuid=True):
  s=specs[index];write(dest/'attempts'/(s['point']+'_'+s['attempt_uuid'])/'STRICT.json',dict(CPU_SYNTHETIC_NOT_PERFORMANCE=True,attempt_uuid=s['attempt_uuid'] if valid_uuid else 'WRONG_UUID',performance_accepted=accepted,calibration=dict(status='PASS_FULL_INPUT_CYCLES_AND_ALL_FROZEN_COMMON_METRICS')))
 with patch.object(runner,'RAW',dest):
  runner.require_BASE_gate(specs[0],specs);rows.append(dict(case='first_BASE_has_no_imported_control_requirement',status='PASS'))
  reject('second_BASE_requires_first_new_BASE',lambda:runner.require_BASE_gate(specs[1],specs))
  receipt(0,accepted=False);reject('failed_first_BASE_cannot_open_second',lambda:runner.require_BASE_gate(specs[1],specs))
  receipt(0);runner.require_BASE_gate(specs[1],specs);rows.append(dict(case='second_BASE_after_first_new_calibrated_BASE',status='PASS'))
  reject('ON_requires_second_BASE_too',lambda:runner.require_BASE_gate(specs[2],specs))
  receipt(1,valid_uuid=False);reject('BASE_receipt_UUID_must_match_new_reservation',lambda:runner.require_BASE_gate(specs[2],specs))
  receipt(1)
  for s in specs[2:]:runner.require_BASE_gate(s,specs)
  rows.append(dict(case='four_ON_gates_after_both_new_BASEs',status='PASS'))
  starts=[dict(attempt_uuid=s['attempt_uuid']) for s in specs]
  assert len(runner.validate_records(starts,specs))==6
  rows.append(dict(case='six_start_prefix_allowed',status='PASS'))
  reject('seventh_start_forbidden',lambda:runner.validate_records(starts+[starts[0]],specs))
  reject('five_reservation_list_cannot_be_used',lambda:runner.validate_records([],specs[:-1]))
 write(PACK/'PAIRED_BASE_GATE_CPU_TESTS.json',dict(status='PASS_NEW_SIX_POINT_BASE_AND_BUDGET_GATES',cases=rows,raw=str(dest),all_receipts_synthetic=True,performance_accepted=False,simulator_starts=0,real_performance_UUIDs=0,runner_sha256=sha(PACK/'tools/run_screen.py')))
 print('PASS_PAIRED_BASE_BUDGET_GATES',len(rows))
if __name__=='__main__':main()
