#!/usr/bin/env python3
"""Reconcile the exact5 owner's published future write carrier under its locks."""
import importlib.util
import json
import pathlib
import sys

root = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
family = sys.argv[1]
assert family in ('gemm', 'stencil')
host = root / 'runtime' / ('host_' + family + '_bound_v2')
spec = importlib.util.spec_from_file_location('exact5_carrier_common', host / 'ep_perf_common_v2.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
with c.locked(c.GLOBAL_MAIN_ADMISSION_LOCK):
    claims = c.read(root / 'control/DISPATCH_CLAIMS.json')['claims']
    assert all(row['request'] in (
        'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
        'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1') for row in claims.values())
    before = c.authority()[0]['registered_future_requests'][c.GOAL]['reserved_write_bytes']
    after = c.publish_own_write_carrier(claims)
    print(json.dumps({'request': c.GOAL, 'before_bytes': before,
                      'after_bytes': after, 'claims': sorted(
                          case for case, row in claims.items()
                          if row['request'] == c.GOAL)}))
