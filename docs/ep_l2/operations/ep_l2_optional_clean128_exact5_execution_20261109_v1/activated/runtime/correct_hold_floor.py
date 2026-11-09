#!/usr/bin/env python3
"""Version the HOLD receipt using the resource adapter's effective Native floor."""
import importlib.util
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
module = importlib.util.spec_from_file_location('exact5_common_correct', ROOT / 'runtime/exact5_common.py')
common = importlib.util.module_from_spec(module)
module.loader.exec_module(common)
path = ROOT / 'documents/RESOURCE_HOLD_RECEIPT.json'
old = common.read(path)
common.need(old['status'] == 'BOTH_FAMILIES_HOLD_NO_CLAIMS_NO_CONSUMPTION', 'wrong receipt')
old_ref = common.put(ROOT / 'documents/RESOURCE_HOLD_RECEIPT.version1.json', old, True)
reg, epoch = common.authority()
common.need(common.read(ROOT / 'control/DISPATCH_CLAIMS.json') == {'claims': {}}, 'active claims')
for name, case in [('gemm', 'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1'),
                   ('stencil', 'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1')]:
    spec = common.read(ROOT / 'cases' / case / 'control/FROZEN_SPEC.json')
    sample = common.module(spec['resource_module_ref'], 'correct_resource_' + name).snapshot()
    request = spec['science_request_id']
    row = reg['registered_future_requests'][request]
    common.need(not row['consumed'] and not sample['actual_loader_aware_models'], 'state changed')
    floor = max(common.exact(spec['resource_policy_ref'])['native_safety_floor_bytes'],
                sample['confirmed_foreign_native_floor_bytes'])
    required = sample['foreign_remaining_write_bytes'] + row['reserved_write_bytes'] + floor
    item = old['families'][name]
    item.update(foreign_remaining_write_bytes=sample['foreign_remaining_write_bytes'],
                native_safety_floor_bytes=floor, native_required_bytes=required,
                native_free_bytes=sample['native_free_bytes'],
                native_deficit_bytes=max(0, required - sample['native_free_bytes']),
                true164_free_bytes=sample['true164_free_bytes'])
    common.need(required > sample['native_free_bytes'], 'HOLD cleared')
old['captured_utc'] = common.now()
old['supersedes'] = old_ref
old['floor_semantics'] = 'max(frozen_family_policy, confirmed_foreign_native_floor)'
new_ref = common.put(path, old)
manifest_path = ROOT / 'control/ACTIVATION_MANIFEST.json'
manifest = common.read(manifest_path)
common.need(manifest['resource_hold_receipt']['sha256'] == common.sha(old_ref['path']),
            'manifest receipt mismatch')
manifest['resource_hold_receipt'] = new_ref
manifest['updated_utc'] = common.now()
common.put(manifest_path, manifest)
print(new_ref)
