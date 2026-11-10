#!/usr/bin/env python3
"""Read only narrow resource snapshot for exact five point execution."""
import importlib.util
import json
import pathlib
import sys

root = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
family = sys.argv[1]
assert family in ('gemm', 'stencil')
name = sys.argv[2] if len(sys.argv) > 2 else 'resources_b1.py'
assert name in ('resources_b1.py', 'resources_exact5_v2.py', 'resources_exact5_v3.py', 'resources_exact5_v4.py', 'resources_exact5_v5.py')
path = root / 'runtime' / ('host_' + family + '_bound_v2') / name
spec = importlib.util.spec_from_file_location('exact5_status_resources', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
s = module.snapshot()
keys = ('utc', 'current_request', 'current_scope_registered', 'foreign_metadata_errors',
        'global_EP_consumed_active_entries', 'occupied_model_or_claim_cpus',
        'native_free_bytes', 'host_MemAvailable_bytes', 'true164_mount_verified',
        'registry_sha256', 'actual_loader_aware_models')
print(json.dumps({k: s.get(k) for k in keys}, separators=(',', ':')))
