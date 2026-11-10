"""Bounded read-only Short-Collect R0 capacity reconciliation.

This is a diagnostic, not a production admission or science release.  It
keeps the shared registry and every owner claim untouched.
"""
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

GIB = 1024 ** 3
ROOT = Path('/root/data/dtc_short_collect_native_discovery10_v1_20261109')
EP = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REG = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
EPOCH = Path('/root/data/ep_l2_dtc_l1_native_v2/control/CURRENT_SCIENCE_EPOCH.json')
PIN = '3c637b65488123b7db22d936c9e700f9a5ca7f46bf6918c6748b02c582402d02'
LEDGER_PIN = 'e9622ccc20306ca1b9b35c91ae4e7c215cd951b96e5fa21e8e55fded3e5d97bb'
EP_REQUESTS = {
    'gemm': 'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
    'stencil': 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    return json.loads(Path(path).read_bytes())


def snapshot(family):
    path = EP / 'runtime' / ('host_' + family + '_bound_v2') / 'resources_exact5_v2.py'
    need(sha(path) == PIN, 'EP_READONLY_ADAPTER_DRIFT:' + family)
    spec = importlib.util.spec_from_file_location('r0_ep_' + family, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.snapshot()


def totals(rows):
    result = {}
    for row in rows:
        name = row['request']
        amount = row['bytes']
        need(type(amount) is int and amount >= 0, 'FOREIGN_WRITE_AMOUNT_BAD')
        result[name] = result.get(name, 0) + amount
    return result


def run(ledger_path):
    need(sha(ledger_path) == LEDGER_PIN, 'OWNER_LEDGER_DRIFT')
    ledger = read(ledger_path)
    reg_before = sha(REG)
    epoch_before = sha(EPOCH)
    registry = read(REG)
    epoch = read(EPOCH)
    need(epoch['epoch'] == 2 and epoch['native_registry_sha256'] == reg_before,
         'REGISTRY_EPOCH_MISMATCH')
    snaps = {name: snapshot(name) for name in EP_REQUESTS}
    need(sha(REG) == reg_before and sha(EPOCH) == epoch_before,
         'REGISTRY_CHANGED_DURING_READ')
    for family, item in snaps.items():
        peer = EP_REQUESTS['stencil' if family == 'gemm' else 'gemm']
        need(item['registry_sha256'] == reg_before, 'EP_REGISTRY_SNAPSHOT_DRIFT')
        need(item['current_request'] == EP_REQUESTS[family], 'EP_CURRENT_REQUEST_DRIFT')
        need(item['foreign_metadata_errors'] == ['unmapped active foreign RAM owner ' + peer],
             'UNRESOLVED_FOREIGN_METADATA:' + repr(item['foreign_metadata_errors']))
        need(not item['actual_loader_aware_models'] and not item['EP_CPU_claims']
             and item['global_EP_consumed_active_count'] == 0,
             'ACTIVE_EP_MODEL_OR_CLAIM')
        need(item['true164_mount_verified'], 'TRUE164_MOUNT_HOLD')
    writes = {family: totals(item['foreign_write_entries']) for family, item in snaps.items()}
    rows = registry['registered_future_requests']
    dtc = {}
    for item in ledger['rows']:
        name = item['request']
        row = rows[name]
        need(row['reserved_write_bytes'] == item['registry_after_reserved_write_bytes'],
             'DTC_REGISTRY_CARRIER_DRIFT:' + name)
        need(row['budget'] == item['budget'] and row['remaining'] == item['remaining_budget']
             and len(row['consumed']) == item['consumed_count'],
             'DTC_BUDGET_OR_CONSUMED_DRIFT:' + name)
        effective = item['still_guaranteed_admission_bytes']
        need(writes['gemm'].get(name) == writes['stencil'].get(name) == effective,
             'DTC_EFFECTIVE_OWNER_BOUND_DRIFT:' + name)
        dtc[name] = effective
    need(sum(dtc.values()) == ledger['totals']['after_guaranteed_bytes'] == 8380228658,
         'DTC_OWNER_TOTAL_DRIFT')
    ep_peer = {}
    for family, name in EP_REQUESTS.items():
        opposite = 'stencil' if family == 'gemm' else 'gemm'
        amount = writes[opposite].get(name)
        need(type(amount) is int and amount == rows[name]['reserved_write_bytes'],
             'EP_PEER_CARRIER_DRIFT:' + name)
        ep_peer[name] = amount
    allowed = set(dtc) | set(ep_peer)
    other = {name: max(writes['gemm'].get(name, 0), writes['stencil'].get(name, 0))
             for name in set(writes['gemm']) | set(writes['stencil']) if name not in allowed}
    need(not any(other.values()), 'OTHER_NONZERO_FOREIGN_OWNER_UNMAPPED')
    spec = read(ROOT / 'control/specs/E2-DTCSHORT-C1-GESUMMV-OFF-V1.json')
    own = 2 * spec['limits']['max_result_directory_bytes'] + GIB
    free = os.statvfs(ROOT).f_bavail * os.statvfs(ROOT).f_frsize
    required = 5 * GIB + own + sum(dtc.values()) + sum(ep_peer.values())
    host_mem = int(next(line.split()[1] for line in Path('/proc/meminfo').read_text().splitlines()
                        if line.startswith('MemAvailable:'))) * 1024
    # Reserve a further 16 GiB for the EP peer RAM diagnostic that its own
    # adapter leaves unmapped. This does not clear the metadata error.
    ram_required = 64 * GIB + spec['limits']['max_process_tree_rss_bytes'] + max(
        item['foreign_additional_RAM_bytes'] for item in snaps.values()) + 16 * GIB
    return {
        'schema': 'DTC_SHORT_COLLECT_R0_READONLY_CROSS_OWNER_RESOURCE_DIAGNOSTIC_V1',
        'utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'status': 'DIAGNOSTIC_CAPACITY_PASS_R0_STILL_HOLD' if free > required and host_mem > ram_required
                  else 'RESOURCE_HOLD',
        'registry_sha256': reg_before, 'epoch_sha256': epoch_before,
        'owner_ledger_sha256': LEDGER_PIN, 'ep_adapter_sha256': PIN,
        'dtc_effective_guarantee_bytes': sum(dtc.values()),
        'ep_both_peer_carriers_bytes': sum(ep_peer.values()),
        'ep_peer_details': ep_peer,
        'own_first_cell_native_window_bytes': own, 'native_floor_bytes': 5 * GIB,
        'required_free_bytes_strict_gt': required, 'native_free_bytes': free,
        'headroom_bytes': free - required,
        'host_MemAvailable_bytes': host_mem, 'ram_required_bytes_strict_gt': ram_required,
        'remaining_R0_blockers': ['production resource guard not qualified',
                                   'pinned historical outbox gate still HOLD',
                                   'EP peer RAM diagnostic remains unmapped',
                                   'production dispatcher, launcher, true164 positive path and independent review pending'],
        'new_science_requests': 0, 'new_model_starts': 0, 'new_budget_consumption': 0,
    }


if __name__ == '__main__':
    try:
        print(json.dumps(run(sys.argv[1]), indent=2, sort_keys=True))
    except Exception as exc:
        print(json.dumps({'status': 'RESOURCE_HOLD', 'reason': type(exc).__name__ + ': ' + str(exc),
                          'new_science_requests': 0, 'new_model_starts': 0,
                          'new_budget_consumption': 0}, indent=2))
        sys.exit(2)
