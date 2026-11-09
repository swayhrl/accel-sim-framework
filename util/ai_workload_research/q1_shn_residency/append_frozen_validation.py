"""Append only the prefrozen validation formal/diagnostic block to the live owner."""
import json
import os
from pathlib import Path

root = Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-shn-gpu-residency-109-v1/docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1')
plan = json.loads((root / 'FORMAL_PLAN.json').read_text())['rows']
dispatch = root / '.private/DISPATCH.jsonl'
current = [json.loads(x) for x in dispatch.read_text().splitlines()]
receipt = json.loads((root / 'RESOURCE_RECEIPT.json').read_text())
assert len(plan) == 32 and len(current) == 22 and current[2:] == plan[:20]
assert [x['id'] for x in current[:2]] == ['CFINAL_NUMERIC_OFF_15301_15305', 'CFINAL_NUMERIC_ON_15301_15305']
assert receipt['status'] == 'DISPATCH_IDLE' and len(receipt['jobs']) == 22
assert receipt['lock_acquired'] and not receipt['lock_released']
assert receipt['reservation_created'] and receipt.get('reason') is None
assert all(j.get('returncode') == 0 and j.get('result', {}).get('status') == 'COMPLETE' for j in receipt['jobs'])
assert [p['mode'] for p in plan[20:]] == ['FORMAL'] * 10 + ['DIAGNOSTIC'] * 2
assert all(p['phase'] == 'VALIDATION' for p in plan[20:])
new = current + plan[20:] + [{'action': 'STOP', 'status': 'COMPLETE'}]
temporary = dispatch.with_name('DISPATCH.next.jsonl')
assert not temporary.exists()
with temporary.open('x') as f:
    for row in new:
        f.write(json.dumps(row, separators=(',', ':')) + '\n')
    f.flush()
    os.fsync(f.fileno())
os.replace(temporary, dispatch)
print(json.dumps({'status': 'FROZEN_VALIDATION_DISPATCH_APPENDED',
                  'line_count': len(new), 'first_new': new[22]['id'],
                  'last_job': new[-2]['id'], 'last_action': new[-1]}))
