#!/usr/bin/env python3
"""Record a fresh exact5 resource HOLD without consuming or changing budget."""
import importlib.util
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
module = importlib.util.spec_from_file_location('exact5_common_hold', ROOT / 'runtime/exact5_common.py')
common = importlib.util.module_from_spec(module)
module.loader.exec_module(common)

reg, epoch = common.authority()
claims = common.read(ROOT / 'control/DISPATCH_CLAIMS.json')
common.need(claims == {'claims': {}}, 'unexpected active claims')
samples = {}
families = {
    'gemm': ('EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
             'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1'),
    'stencil': ('EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
                'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1'),
}
for name, (request, case) in families.items():
    row = reg['registered_future_requests'][request]
    common.need(len(row['consumed']) == 0, 'point already consumed')
    spec = common.read(ROOT / 'cases' / case / 'control/FROZEN_SPEC.json')
    adapter = common.module(spec['resource_module_ref'], 'hold_resource_' + name)
    sample = adapter.snapshot()
    common.need(sample['registry_sha256'] == common.sha(common.REG), 'registry changed')
    common.need(not sample['foreign_metadata_errors'] and not sample['actual_loader_aware_models'],
                'resource or model changed')
    own = row['reserved_write_bytes']
    floor = common.exact(spec['resource_policy_ref'])['native_safety_floor_bytes']
    required = sample['foreign_remaining_write_bytes'] + own + floor
    samples[name] = {
        'request': request, 'budget': row['budget'], 'consumed': 0,
        'remaining': row['remaining'], 'foreign_remaining_write_bytes': sample['foreign_remaining_write_bytes'],
        'own_reserved_write_bytes': own, 'native_safety_floor_bytes': floor,
        'native_required_bytes': required, 'native_free_bytes': sample['native_free_bytes'],
        'native_deficit_bytes': max(0, required - sample['native_free_bytes']),
        'true164_free_bytes': sample['true164_free_bytes'],
        'true164_mount_verified': sample['true164_mount_verified'],
        'global_EP_active_count': sample['global_EP_consumed_active_count'],
        'resource_errors': sample['foreign_metadata_errors'],
    }
    common.need(required > sample['native_free_bytes'], 'HOLD condition already cleared')

receipt = {
    'schema': 'EP_L2_EXACT5_RESOURCE_HOLD_RECEIPT_V1', 'captured_utc': common.now(),
    'goal': common.GOAL, 'status': 'BOTH_FAMILIES_HOLD_NO_CLAIMS_NO_CONSUMPTION',
    'epoch': epoch['epoch'], 'registry_sha256': common.sha(common.REG),
    'staged_admission_refs': [common.ref(p) for p in sorted((ROOT / 'control').glob('STAGED_ADMISSION_*.json'))],
    'claims': claims, 'families': samples,
    'no_peer_reservation_reduction': True, 'no_automatic_retry': True,
}
receipt_ref = common.put(ROOT / 'documents/RESOURCE_HOLD_RECEIPT.json', receipt, True)
manifest_path = ROOT / 'control/ACTIVATION_MANIFEST.json'
old = common.read(manifest_path)
common.need(old['status'] == 'AUTHORIZED_BINDING_IN_PROGRESS_NO_BUDGET_REGISTRATION_OR_MODEL_START',
            'manifest unexpected state')
common.put(ROOT / 'control/ACTIVATION_MANIFEST.version1.json', old, True)
old['status'] = 'BOTH_FAMILIES_REGISTERED_PREPARED_RESOURCE_HOLD_NO_CONSUMPTION'
old['updated_utc'] = common.now()
old['resource_hold_receipt'] = receipt_ref
for family in old['families'].values():
    family['budget_registered'] = family['budget_authorized']
    family['consumed'] = 0
for point in old['points']:
    point['state'] = 'REGISTERED_PREPARED_RESOURCE_HOLD_NO_CONSUMPTION'
    common.need(point['uuid'] is None, 'unexpected point UUID')
common.put(manifest_path, old)
print(receipt_ref)
