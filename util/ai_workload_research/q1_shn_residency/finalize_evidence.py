"""Write concise source, capacity, and cleanup receipts from immutable job outputs."""
import hashlib
import json
import subprocess
from pathlib import Path

work = Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-shn-gpu-residency-109-v1')
root = work / 'docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1'
tool = work / 'util/ai_workload_research/q1_shn_residency'
jobs = root / '.private/JOBS'
plan = json.loads((root / 'FORMAL_PLAN.json').read_text())['rows']
receipts = [json.loads((root / '.private/RESOURCE_RECEIPT_WINDOW1.json').read_text()),
            json.loads((root / 'RESOURCE_RECEIPT.json').read_text())]
assert receipts[0]['status'] == 'QUALIFICATION_WINDOW_COMPLETE'
assert receipts[1]['status'] == 'COMPLETE' and len(receipts[1]['jobs']) == 34
for r in receipts:
    assert r['lock_attempt_count'] == 1 and r['lock_released'] and r['lock_closed']
    assert r['own_GPU_contexts_cleared'] and r['reservation_cleanup']['released']
    assert r['NVML_shutdown']
assert all(j['returncode'] == 0 and j['result']['status'] == 'COMPLETE' for j in receipts[1]['jobs'])

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

source = {
    'goal': 'AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1',
    'branch': 'hrl/aiarch-q1-shn-gpu-residency-109-v1',
    'pre_result_freeze_commit': '8e8c15472b5ab211d1108d97672c43757cfbc891',
    'original_Q1_authority': '5787826ca21f7af958e6e1c1f828d62fd58a1ec4',
    'original_trainer_SHA256': '17e70b6466f7e33a24d1610aa7deb69316cd177dc2c212cd8b717b9884f4808a',
    'original_CPUAdam_cpp_SHA256': 'f3f32bc04f61749baf57d1bd877b24379597e50cf4a94d04fdde80a11c19ce9f',
    'tool_SHA256': {p.name: sha(p) for p in sorted(tool.glob('*.py'))},
    'plan_SHA256': sha(root / 'FORMAL_PLAN.json'),
    'contract_SHA256': sha(root / 'PREFROZEN_CONTRACT.md'),
    'actual_dispatch_SHA256': sha(root / '.private/DISPATCH.jsonl'),
    'actual_job_count': len(receipts[1]['jobs']),
    'candidate': 'opt-in shn_resident; OFF uses original Q1 transform',
}
(root / 'SOURCE_FREEZE.json').write_text(json.dumps(source, indent=2) + '\n')

formal = []
for p in plan:
    if p['mode'] == 'FORMAL':
        result = json.loads((jobs / p['id'] / 'RESULT.json').read_text())
        formal.append((p, result))
peaks = {}
for policy in ['OFF', 'ON']:
    selected = [r for p, r in formal if p['shn_resident'] == (policy == 'ON')]
    peaks[policy] = {'formal_job_count': len(selected),
                     'max_torch_allocated_peak_bytes': max(r['torch_allocated_peak'] for r in selected),
                     'max_torch_reserved_peak_bytes': max(r['torch_reserved_peak'] for r in selected)}
live = {'status': 'OBSERVED_WITH_SAMPLING_LIMITS',
        'unique_storage_rule': 'Do not add shared views, torch peaks, own NVML, or old checkpoint bytes together.',
        'static_shN_parameter_plus_two_moments_GiB': 3.379784,
        'static_plus_dense_gradient_GiB': 4.506378,
        'formal_worker_torch_peaks': peaks,
        'window_1_own_NVML_peak_bytes': receipts[0]['peak_own_NVML_bytes'],
        'window_2_own_NVML_peak_bytes': receipts[1]['peak_own_NVML_bytes'],
        'window_2_sampled_RSS_peak_bytes': receipts[1]['peak_sampled_RSS_bytes'],
        'window_2_session_charged_peak_bytes': receipts[1]['peak_charged_bytes'],
        'sampling_gap': 'Terminal worker reap interval has no RSS sample; charged peak retained. Desktop per-process activity unavailable.'}
(root / 'LIVE_STORAGE_PEAK.json').write_text(json.dumps(live, indent=2) + '\n')

receipt = {'status': 'COMPLETE_WITH_DISCLOSED_DEVIATION',
           'window_statuses': [r['status'] for r in receipts],
           'worker_launches': [r['worker_launches'] for r in receipts],
           'GPU_lock_seconds_by_window': [r['GPU_lock_held_seconds'] for r in receipts],
           'GPU_lock_seconds_cumulative': sum(r['GPU_lock_held_seconds'] for r in receipts),
           'GPU_lock_seconds_limit': 5400,
           'locks_released': all(r['lock_released'] for r in receipts),
           'reservations_released': all(r['reservation_cleanup']['released'] for r in receipts),
           'own_GPU_contexts_cleared': all(r['own_GPU_contexts_cleared'] for r in receipts),
           'final_worker_exit_count': sum(j['returncode'] == 0 for j in receipts[1]['jobs']),
           'desktop_activity_attribution_gap': receipts[1]['desktop_activity_attribution_gap'],
           'deviation': 'First GPU window private TORCH_HOME was empty; original runner auto-downloaded 244408911 bytes (about 233 MiB) of AlexNet weights despite the no-model-download restriction. Download completed before window 2 and was not used as a performance sample.'}
(root / 'RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'receipt': receipt, 'live': live, 'source_SHA256_count': len(source['tool_SHA256'])}, indent=2))
