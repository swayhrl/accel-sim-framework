"""Read-only admission audit before the frozen validation formal dispatch."""
import json
from pathlib import Path

base = Path('/home/huangrulin/workspace/worktrees')
root = base / 'accel-sim-aiarch-q1-shn-gpu-residency-109-v1/docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1'
old = base / 'accel-sim-aiarch-q1-completion-109/docs/ai_workload_research/runs/AI_ARCH_Q1_COMPLETION_109_V1/windows/W2/.private/JOBS'
plan = json.loads((root / 'FORMAL_PLAN.json').read_text())
warm = [r for r in plan['rows'] if r['phase'] == 'VALIDATION' and r['mode'] == 'WARMUP']
assert len(warm) == 4
actual = []
for p in warm:
    job = root / '.private/JOBS' / p['id']
    result = json.loads((job / 'RESULT.json').read_text())
    bundle = json.loads((job / 'BUNDLE_ROUNDTRIP.json').read_text())
    steps = [r['step'] for r in result['rows']]
    cameras = [r['camera_ids'][0] for r in result['rows']]
    work = [(r['N_total'], r['N_visible'], r['N_updated']) for r in result['rows']]
    assert result['status'] == 'COMPLETE' and result['reached_next_step'] == 15362
    assert steps == list(range(15311, 15362))
    assert result['frontier']['processed_GPU_step'] == 15361
    assert result['frontier']['CPU_applied_through_step'] == 15360
    assert result['frontier']['pending_CPU_gradient_step'] == 15361
    assert result['frontier']['prepared_camera_step'] == 15362
    assert bundle['status'] == 'HASH_VERIFIED_BUNDLE_DECODED'
    assert bundle['next_step'] == 15301
    assert bundle['frontier']['pending_CPU_gradient_step'] == 15300
    assert bundle['frontier']['prepared_camera_step'] == 15301
    actual.append((cameras, work))
assert all(x[0] == actual[0][0] for x in actual), 'warmup camera mismatch'
assert all([t[0] for t in x[1]] == [t[0] for t in actual[0][1]] for x in actual), 'N mismatch'
work_jitter = []
for p, (_, work) in zip(warm, actual):
    visible_delta = sum(x[1] for x in work) - sum(x[1] for x in actual[0][1])
    update_delta = sum(x[2] for x in work) - sum(x[2] for x in actual[0][1])
    work_jitter.append({'job': p['id'], 'visible_sum_delta_vs_first_OFF': visible_delta,
                        'update_sum_delta_vs_first_OFF': update_delta})
hist = {}
for name in ['DISCOVERY_FORMAL_R3_T16', 'VALIDATION_FORMAL_R3_T16']:
    result = json.loads((old / name / 'RESULT.json').read_text())
    hist[name] = [r['camera_ids'][0] for r in result['rows']]
overlap = {name: sorted(set(actual[0][0]) & set(ids)) for name, ids in hist.items()}
audit = {
    'status': 'PRE_FORMAL_VALIDATION_ADMISSIBLE',
    'warmup_jobs': [p['id'] for p in warm],
    'validation_camera_count_with_closure': len(actual[0][0]),
    'validation_camera_ids': actual[0][0],
    'historical_overlap': overlap,
    'work_jitter': work_jitter,
    'pending15300_restore_frontier': 'present in four immutable C_FINAL restores; step15301 natural continuation reached terminal frontier',
}
(root / 'PRE_FORMAL_VALIDATION_AUDIT.json').write_text(json.dumps(audit, indent=2) + '\n')
print(json.dumps(audit, indent=2))
