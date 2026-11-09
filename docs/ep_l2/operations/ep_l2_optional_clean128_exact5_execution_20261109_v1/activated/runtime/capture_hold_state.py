#!/usr/bin/env python3
"""Read current exact5 authority and resource values without changing state."""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
COMMON = ROOT / 'runtime/exact5_common.py'
module = importlib.util.spec_from_file_location('exact5_common_read', COMMON)
common = importlib.util.module_from_spec(module)
module.loader.exec_module(common)
reg, epoch = common.authority()
requests = {}
for family, request in common.REQUESTS.items():
    row = reg['registered_future_requests'][request]
    requests[family] = {'request': request, 'budget': row['budget'],
                        'consumed': len(row['consumed']), 'remaining': row['remaining'],
                        'reserved_write_bytes': row['reserved_write_bytes']}
resources = {}
for family, case in [('gemm', 'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1'),
                     ('stencil', 'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1')]:
    spec = common.read(ROOT / 'cases' / case / 'control/FROZEN_SPEC.json')
    adapter = common.module(spec['resource_module_ref'], 'exact5_resource_' + family)
    sample = adapter.snapshot()
    writes = defaultdict(int)
    for entry in sample.get('foreign_write_entries', []):
        writes[(entry.get('request', 'UNKNOWN'), entry.get('kind', 'UNSPECIFIED'))] += entry['bytes']
    resources[family] = {key: sample.get(key) for key in (
        'registry_sha256', 'native_free_bytes', 'foreign_remaining_write_bytes',
        'confirmed_foreign_native_floor_bytes',
        'true164_free_bytes', 'foreign_metadata_errors', 'actual_loader_aware_models',
        'global_EP_consumed_active_count', 'true164_mount_verified')}
    resources[family]['foreign_write_breakdown'] = [
        {'request': request, 'kind': kind, 'bytes': value}
        for (request, kind), value in sorted(writes.items())]
print(json.dumps({'utc': common.now(), 'epoch': epoch['epoch'],
                  'registry_sha256': common.sha(common.REG), 'requests': requests,
                  'resources': resources,
                  'claims': common.read(ROOT / 'control/DISPATCH_CLAIMS.json'),
                  'staged_receipts': sorted(p.name for p in (ROOT / 'control').glob('STAGED_ADMISSION_*.json'))},
                 ensure_ascii=False, separators=(',', ':')))
