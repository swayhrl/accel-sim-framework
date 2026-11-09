#!/usr/bin/env python3
"""Read-only, bounded exact5 Native commitment sample; never reads raw bodies."""
import datetime
import hashlib
import importlib.util
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
NATIVE = Path('/root/data/ep_l2_dtc_l1_native_v2')
REG = NATIVE/'control/science_authority/NATIVE_SCIENCE_REGISTRY.json'
EPOCH = NATIVE/'control/CURRENT_SCIENCE_EPOCH.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    raw = REG.read_bytes()
    reg = json.loads(raw)
    epoch = json.loads(EPOCH.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == epoch['native_registry_sha256']
    claims_file = ROOT/'control/DISPATCH_CLAIMS.json'
    claims = json.loads(claims_file.read_bytes())['claims']
    result = {
        'schema': 'EP_L2_NATIVE_WRITE_LEDGER_RECONCILIATION_V1',
        'sample_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source': {'registry': str(REG), 'registry_sha256': sha(REG),
                   'epoch': str(EPOCH), 'epoch_sha256': sha(EPOCH), 'epoch_number': epoch['epoch'],
                   'claims': str(claims_file), 'claims_sha256': sha(claims_file)},
        'claims': claims, 'requests': [], 'admission': {}, 'actual_point_admission': {},
        'notes': ['UNKNOWN is not zero; conservative published guarantees remain in force',
                  'Execution receipt alone does not close archival or restore obligations'],
    }
    for family in ('gemm', 'stencil'):
        host = ROOT/'runtime'/('host_'+family+'_bound_v2')
        module = load(host/'resources_exact5_v2.py', 'exact5_'+family)
        snap = module.snapshot()
        assert snap['registry_sha256'] == result['source']['registry_sha256']
        case = next(ROOT.glob('cases/EP_PERF_CLEAN128_'+family.upper()+'_WV_EXT0_*/control/FROZEN_SPEC.json'))
        spec = json.loads(case.read_bytes())
        policy = json.loads(Path(spec['resource_policy_ref']['path']).read_bytes())
        policy.update(requested_request_id=spec['science_request_id'], requested_cohort=spec['cohort'],
                      requested_host_cpu=128, stage_ready=True, max_global_EP_models=10)
        own = reg['registered_future_requests'][spec['science_request_id']]['reserved_write_bytes']
        decision = module.admit(snap, 0, own, policy)
        hold_files = sorted((ROOT/'control').glob('STAGED_ADMISSION_'+family.upper()+'_*.json'),
                            key=lambda path:path.stat().st_mtime_ns)
        hold = json.loads(hold_files[-1].read_bytes()) if hold_files else None
        if hold and hold.get('admission_decision'):
            d = hold['admission_decision']
            result['actual_point_admission'][family] = {
                'receipt_path':str(hold_files[-1]),'receipt_sha256':sha(hold_files[-1]),
                'utc':hold['utc'],'cohort':hold['cohort'],'status':hold['status'],
                'observed_native_free_bytes':hold['observed_native_free_bytes'],
                'required_free_bytes':d['required_free_bytes'],
                'native_deficit_bytes':max(0,d['required_free_bytes']-hold['observed_native_free_bytes']),
                'hold_reasons':d['hold_reasons'],'global_restore_dedup':d['global_restore_dedup'],
                'own_remaining_write_bytes':d['own_remaining_write_bytes'],
                'foreign_remaining_write_bytes':d['foreign_remaining_write_bytes'],
                'required_additional_RAM_bytes':d['required_additional_RAM_bytes'],
                'admission_RAM_budget_bytes':d['admission_RAM_budget_bytes'],
                'claims_rolled_back':hold['status']=='RESOURCE_HOLD_NO_NEW_CLAIM',
                'no_model_started':hold['no_model_started']}
        result['admission'][family] = {
            'snapshot_utc': snap.get('observed_utc'),
            'snapshot_sha256': hashlib.sha256(json.dumps(snap,sort_keys=True,default=str).encode()).hexdigest(),
            'native_free_bytes': snap['native_free_bytes'],
            'true164_free_bytes': snap.get('true164_free_bytes'),
            'true164_mount_verified': snap['true164_mount_verified'],
            'foreign_metadata_errors': snap.get('foreign_metadata_errors'),
            'foreign_write_entries': snap['foreign_write_entries'],
            'foreign_claims_pins': snap.get('foreign_claims_pins'),
            'actual_loader_aware_models': snap['actual_loader_aware_models'],
            'EP_CPU_claims': snap['EP_CPU_claims'],
            'global_EP_consumed_active_count': snap['global_EP_consumed_active_count'],
            'current_own_restore_window_bytes': snap['current_own_restore_window_bytes'],
            'own_published_carrier_bytes': own,
            'diagnostic_whole_family_without_claim_decision': {k: decision[k] for k in ('pass_admission','hold_reasons',
                'foreign_remaining_write_bytes','own_remaining_write_bytes','required_free_bytes',
                'global_restore_dedup','host_floor_bytes','cgroup_floor_bytes')},
            'effective_native_floor_bytes': max(policy['native_safety_floor_bytes'],
                                                 snap.get('confirmed_foreign_native_floor_bytes',0)),
        }
    entries = defaultdict(list)
    for family in ('gemm', 'stencil'):
        for item in result['admission'][family]['foreign_write_entries']:
            bucket = entries[item['request']]
            if item not in bucket:
                bucket.append(item)
    for name,row in reg['registered_future_requests'].items():
        if name not in entries and not name.startswith('EP_L2_OPTIONAL_CLEAN128_'):
            continue
        consumed = row.get('consumed',{})
        if not isinstance(consumed,dict):
            consumed = {}
        receipts = [c.get('execution_receipt',{}) for c in consumed.values()]
        owner_pid = row.get('owner_pid')
        owner_start = row.get('owner_start_ticks')
        proc = Path('/proc')/str(owner_pid)/'stat' if owner_pid else None
        if proc and proc.exists():
            parts=proc.read_text().rsplit(')',1)[1].split()
            owner_live=int(parts[19])==owner_start and parts[0] not in ('Z','X')
        else:
            owner_live=False if owner_pid else 'UNKNOWN'
        paths = sorted({c.get('execution_receipt',{}).get('output') for c in consumed.values()
                        if c.get('execution_receipt',{}).get('output')})
        result['requests'].append({
            'owner': 'EP-L2 Main' if name.startswith('EP_') else 'DTC-L1',
            'request': name, 'state': row.get('state'), 'budget': row.get('budget'),
            'remaining_budget': row.get('remaining'), 'consumed_count': len(consumed),
            'published_carrier_bytes': row.get('reserved_write_bytes'),
            'carrier_source': {'path': str(REG), 'sha256': result['source']['registry_sha256']},
            'foreign_write_entries': entries.get(name,[]),
            'execution_receipt_count': sum(bool(r) for r in receipts),
            'archive_receipt_in_registry_count': sum(bool(c.get('archive_receipt_ref')) for c in consumed.values()),
            'recorded_peak_result_logical_bytes_sum': sum(r.get('peak_result_logical_bytes',0) for r in receipts),
            'adapter_observed_existing_result_bytes': sum(x.get('already_written_bytes',0) for x in entries.get(name,[])),
            'actual_native_already_written_bytes': 0 if name.startswith('EP_L2_OPTIONAL_CLEAN128_') and not consumed and not claims else 'UNKNOWN',
            'actual_future_native_growth_bytes': 'UNKNOWN',
            'supported_future_native_upper_bound_bytes': row.get('reserved_write_bytes') if name.startswith('EP_L2_OPTIONAL_CLEAN128_') else sum(x['bytes'] for x in entries.get(name,[])),
            'conservative_admission_bytes': (row.get('reserved_write_bytes')
                if name.startswith('EP_L2_OPTIONAL_CLEAN128_') else
                sum(x['bytes'] for x in entries.get(name,[]))),
            'true164_archive_root': row.get('archive_target_root','UNKNOWN'),
            'true164_future_bytes': 'UNKNOWN',
            'owner_pid': row.get('owner_pid'), 'owner_start_ticks': row.get('owner_start_ticks'),
            'owner_pid_generation_live': owner_live,
            'controller_ref': {'path':row.get('controller_path'),'sha256':row.get('controller_sha256')},
            'runtime_release_evidence_keys': list(row.get('runtime_release_evidence',{})),
            'output_root_examples': paths[:2],
            'closure_basis': 'UNKNOWN' if row.get('state') not in ('CLOSED','CLOSED_COMPLETED') and row.get('reserved_write_bytes',0) else 'REGISTRY_CLOSED_OR_ZERO_CARRIER',
        })
    result['source']['registry_unchanged_after'] = sha(REG) == result['source']['registry_sha256']
    result['source']['claims_unchanged_after'] = sha(claims_file) == result['source']['claims_sha256']
    result['global_restore_window'] = dict(bytes=128*1024**2,
        lock='/root/data/ep_l2_full_workload_performance_20261027_v1/execution_performance_first_20261103_v1/control/ARCHIVE_SHARED_WINDOW.lock',
        holder='whichever exact5 family has the current archive/restore transaction',
        release='after each of two serial native target verifications and scratch cleanup; carrier released only after own archive close')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
