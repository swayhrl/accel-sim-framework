"""Read-only Short-Collect R0 admission snapshot. Never registers a request."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path('/root/data/dtc_short_collect_native_discovery10_v1_20261109')
sys.path.insert(0, str(ROOT / 'tools'))

import mechanism_outbox
import route_authority
import route_guard

GIB = 1024 ** 3
request_path = ROOT / 'control/requests/C1_EXACT_REQUEST_PREPARED.json'
spec_path = ROOT / 'control/specs/E2-DTCSHORT-C1-GESUMMV-OFF-V1.json'
registry_path = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
epoch_path = Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
lock_path = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/REGISTRY_UPDATE.lock')

result = {
    'schema': 'DTC_SHORT_COLLECT_R0_FRESH_READONLY_ADMISSION_V1',
    'utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'contract_commit': route_authority.CONTRACT,
    'candidate_core': route_authority.CORE,
    'new_science_requests': 0,
    'new_model_starts': 0,
    'new_budget_consumption': 0,
}
try:
    request = route_authority.validate_request(request_path, ROOT)
    result['prepared_request'] = {'status': 'VALID_PREPARED_UNREGISTERED', 'sha256': route_authority.sha(request_path),
                                   'request_id': request['request_id'], 'reserved_write_bytes': request['reserved_write_bytes']}
    spec = route_authority.read(spec_path)
    result['runtime'] = route_guard.verify_runtime(spec)
    result['input'] = route_guard.verify_input(spec)
    store = route_authority.RegistryStore(registry_path, epoch_path, lock_path, fixture_only=False)
    registry, epoch = store.snapshot()
    result['authority'] = {'registry_sha256': route_authority.sha(registry_path),
                           'epoch_sha256': route_authority.sha(epoch_path), 'epoch': epoch['epoch'],
                           'registered_requests': len(registry['registered_future_requests']),
                           'new_budget_remaining': registry['new_scientific_budget_remaining'],
                           'prepared_request_present': request['request_id'] in registry['registered_future_requests']}
    peers = route_guard.peer_reservation(registry, request['request_id'])
    local = route_guard.local_sample(ROOT)
    own = 2 * spec['limits']['max_result_directory_bytes'] + GIB
    required = 5 * GIB + own + sum(row['reserved_write_bytes'] for row in peers)
    result['native_capacity'] = {'free_bytes': local['native_free_bytes'],
                                 'free_inodes': local['native_free_inodes'],
                                 'floor_bytes': 5 * GIB, 'own_write_bytes': own,
                                 'peer_reserved_bytes': sum(row['reserved_write_bytes'] for row in peers),
                                 'peer_count': len(peers), 'required_bytes_strict_gt': required,
                                 'gap_to_strict_pass_bytes': max(0, required + 1 - local['native_free_bytes']),
                                 'pass': local['native_free_bytes'] > required and local['native_free_inodes'] >= 100000,
                                 'largest_peers': sorted(peers, key=lambda row: row['reserved_write_bytes'], reverse=True)[:12]}
    result['memory'] = {'MemAvailable_bytes': local['host_MemAvailable_bytes'],
                        'cgroup_current_bytes': local['cgroup_current_bytes'],
                        'cgroup_max_bytes': local['cgroup_max_bytes']}
    try:
        result['true164_archive_capacity'] = route_guard.archive_capacity(mechanism_outbox.NAS, own)
    except Exception as exc:
        result['true164_archive_capacity'] = {'status': 'HOLD', 'reason': type(exc).__name__ + ': ' + str(exc)}
    try:
        result['pinned_outbox_gate'] = {'status': 'PASS', 'receipt': mechanism_outbox.gate(2 * 1024 * 1024)}
    except Exception as exc:
        result['pinned_outbox_gate'] = {'status': 'HOLD', 'reason': type(exc).__name__ + ': ' + str(exc)}
    result['decision'] = 'R0_HOLD_NO_SCIENCE' if not result['native_capacity']['pass'] or result['pinned_outbox_gate']['status'] != 'PASS' else 'RESOURCE_ONLY_PASS_OTHER_R0_GATES_PENDING'
except Exception as exc:
    result['decision'] = 'R0_HOLD_NO_SCIENCE'
    result['error'] = type(exc).__name__ + ': ' + str(exc)
print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
