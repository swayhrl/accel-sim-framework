"""Summarize diagnostic-only intervals without mixing Host and CUDA clocks."""
import json
from collections import defaultdict
from pathlib import Path

root = Path('/home/huangrulin/workspace/worktrees/accel-sim-aiarch-q1-shn-gpu-residency-109-v1/docs/ai_workload_research/runs/AI_ARCH_Q1_SHN_GPU_RESIDENCY_NATIVE_V1')
jobs = root / '.private/JOBS'

def union_seconds(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return sum(end - start for start, end in merged)

ledger = {}
for phase, start, end in [('DISCOVERY', 15150, 15200), ('VALIDATION', 15311, 15361)]:
    ledger[phase] = {}
    for policy in ['OFF', 'ON']:
        job = jobs / (phase + '_DIAG_' + policy)
        result = json.loads((job / 'RESULT.json').read_text())
        regions = json.loads((job / 'REGIONS.json').read_text())
        transfers = json.loads((job / 'TRANSFERS.json').read_text())
        events = json.loads((job / 'GPU_EVENT_SPANS.json').read_text())
        tags = defaultdict(list)
        for row in regions:
            if start <= row['step'] <= end:
                tags[row['tag'].split('@')[0]].append((row['begin_host_monotonic'], row['end_host_monotonic']))
        region_summary = {tag: {'calls': len(intervals),
                                'host_interval_sum_seconds': sum(b-a for a,b in intervals),
                                'host_interval_union_seconds': union_seconds(intervals)}
                          for tag, intervals in sorted(tags.items())}
        transfers_by_direction = defaultdict(lambda: {'calls': 0, 'logical_operand_bytes': 0, 'host_call_seconds': 0.0})
        for row in transfers:
            if start <= row['step'] <= end:
                source = row['src'].get('device') if row['src'] else None
                destination = row['dst'].get('device') if row['dst'] else None
                direction = str(source) + '->' + str(destination)
                record = transfers_by_direction[direction]
                record['calls'] += 1
                record['logical_operand_bytes'] += row.get('logical_payload_bytes') or 0
                record['host_call_seconds'] += row['host_call_elapsed_ns'] / 1e9
        target_events = [r for r in events if start <= r['step'] <= end]
        ledger[phase][policy] = {
            'job': job.name, 'complete': result['status'] == 'COMPLETE',
            'closed_window_host_seconds': result['closed_window_wall_seconds'],
            'regions': region_summary,
            'transfer_observer_installed': policy == 'OFF',
            'transfers_observed': dict(transfers_by_direction) if policy == 'OFF' else None,
            'CUDA_event_count': len(target_events),
            'CUDA_event_span_sum_seconds': sum(r['gpu_span_ms'] for r in target_events) / 1000,
            'CUDA_event_scope': 'Launch-gap-inclusive CUDA spans on a device clock; do not subtract from Host intervals or call pure kernel time',
        }
output = {'status': 'DIAGNOSTIC_PARTIAL_ATTRIBUTION',
          'scope': 'Separate diagnostic runs; intervals can overlap and include instrumentation overhead. ON transformed train disables detailed region/transfer observer.',
          'logical_bytes_warning': 'Call operand bytes do not establish PCIe or DRAM traffic.',
          'ledger': ledger}
(root / 'COST_LEDGER.json').write_text(json.dumps(output, indent=2) + '\n')
print(json.dumps({'status': output['status'], 'ledger': ledger}, indent=2))
