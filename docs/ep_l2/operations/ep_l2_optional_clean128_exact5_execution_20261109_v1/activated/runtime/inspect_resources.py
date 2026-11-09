#!/usr/bin/env python3
"""Read-only exact5 resource summary; never changes registry or claims."""
import importlib.util
import json
import pathlib
import sys

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
FAMILIES = {
    'gemm': 'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1',
    'stencil': 'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
}
case = FAMILIES[sys.argv[1]]
spec = json.loads((ROOT / 'cases' / case / 'control/FROZEN_SPEC.json').read_text())
item = spec['resource_module_ref']
p = pathlib.Path(item['path'])
import hashlib
if len(sys.argv) > 2 and sys.argv[2] == 'v2':
    p = p.with_name('resources_exact5_v2.py')
else:
    assert hashlib.sha256(p.read_bytes()).hexdigest() == item['sha256']
loader = importlib.util.spec_from_file_location('exact5_resources', p)
module = importlib.util.module_from_spec(loader)
loader.loader.exec_module(module)
s = module.snapshot()
keys = ('schema', 'current_request', 'current_scope_registered', 'registry_sha256',
        'foreign_metadata_errors', 'cpu_allowed', 'cpu_quota_equivalent',
        'occupied_model_or_claim_cpus', 'EP_CPU_claims', 'actual_loader_aware_models',
        'global_EP_consumed_active_count', 'true164_mount_verified',
        'true164_free_bytes', 'foreign_additional_RAM_bytes',
        'foreign_remaining_write_bytes', 'host_available_bytes',
        'cgroup_available_bytes', 'native_free_bytes',
        'exact5_terminal_legacy_reconciliation')
print(json.dumps({k: s.get(k) for k in keys}, separators=(',', ':')))
