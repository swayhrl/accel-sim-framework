#!/usr/bin/env python3
"""Read only, small exact5 live state receipt for EP-L2-8."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

root = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
native = Path('/root/data/ep_l2_dtc_l1_native_v2')
regpath = native / 'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
epochpath = native / 'control/CURRENT_SCIENCE_EPOCH.json'
raw = regpath.read_bytes()
registry = json.loads(raw)['registered_future_requests']
epoch = json.loads(epochpath.read_bytes())
assert epoch['native_registry_sha256'] == hashlib.sha256(raw).hexdigest()
claims = json.loads((root / 'control/DISPATCH_CLAIMS.json').read_bytes())['claims']
request_ids = ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
               'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1')
expected = {
    'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1',
    'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1',
    'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1',
    'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
    'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1',
}
assert set(claims) == expected
points = {}
for case, claim in sorted(claims.items()):
    request = claim['request']
    row = registry[request]['consumed'][case]
    assert claim['state'] == 'RUNNING' and row['uuid'] == claim['uuid']
    specpath = root / 'cases' / case / 'control/FROZEN_SPEC.json'
    assert hashlib.sha256(specpath.read_bytes()).hexdigest() == claim['spec_sha256']
    proc = Path('/proc') / str(claim['model_pid'])
    stat = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
    live = int(stat[19]) == claim['model_start_ticks'] and stat[0] not in ('Z', 'X')
    assert live
    points[case] = {'request': request, 'uuid': claim['uuid'],
                    'cpu': claim['host_cpu'], 'model_pid': claim['model_pid'],
                    'model_start_ticks': claim['model_start_ticks'],
                    'live': live, 'observed_RSS_bytes': claim['observed_RSS_bytes'],
                    'remaining_write_bytes': claim['remaining_write_bytes'],
                    'spec_sha256': claim['spec_sha256'], 'output': claim['output'],
                    'done_exists': (Path(claim['output']) / 'NATIVE_EXIT.json').exists()}
assert len({p['cpu'] for p in points.values()}) == 5
resources = {}
for family in ('gemm', 'stencil'):
    path = root / 'runtime' / ('host_' + family + '_bound_v2') / 'resources_exact5_v5.py'
    spec = importlib.util.spec_from_file_location('exact5_active_resources_' + family, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    s = mod.snapshot()
    assert not s['foreign_metadata_errors']
    resources[family] = {'native_free_bytes': s['native_free_bytes'],
                         'host_MemAvailable_bytes': s['host_MemAvailable_bytes'],
                         'true164_mount_verified': s['true164_mount_verified'],
                         'foreign_metadata_errors': s['foreign_metadata_errors'],
                         'global_EP_consumed_active_count': s['global_EP_consumed_active_count']}
requests = {r: {'budget': registry[r]['budget'], 'remaining': registry[r]['remaining'],
                'consumed_count': len(registry[r]['consumed']),
                'reserved_write_bytes': registry[r]['reserved_write_bytes']}
            for r in request_ids}
for r in request_ids:
    assert requests[r]['remaining'] == 0
    assert requests[r]['reserved_write_bytes'] >= 130*1024**2 + sum(
        p['remaining_write_bytes'] for p in points.values() if p['request'] == r)
print(json.dumps({'schema': 'EP_EXACT5_ACTIVE_BACKGROUND_RECEIPT_V1',
                  'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  'epoch': epoch['epoch'],
                  'registry_sha256': hashlib.sha256(raw).hexdigest(),
                  'execution_root': str(root), 'native_entry': str(native / 'bin/native'),
                  'requests': requests, 'points': points, 'resources': resources,
                  'status': 'FIVE_CONSUMED_FIVE_LIVE_NOT_YET_ACCEPTED',
                  'automatic_retry': False, 'source_keep': True},
                 sort_keys=True, separators=(',', ':')))
