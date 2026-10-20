#!/usr/bin/env python3
"""Bounded, metadata-only W/V screen. Never opens trace bodies or simulator logs."""
import argparse
import csv
import hashlib
import io
import json
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    started = time.time()
    sources = {}
    budget = 16 * 1024 * 1024

    def read(path):
        nonlocal budget
        p = Path(path)
        assert p.suffix in ('.json', '.csv', '.h', '.inc'), p
        assert p.stat().st_size <= budget, 'metadata read budget exceeded'
        b = p.read_bytes()
        budget -= len(b)
        sources[str(p)] = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
        return b

    def js(path):
        return json.loads(read(path))

    def rows(path):
        return list(csv.DictReader(io.StringIO(read(path).decode())))

    def write(name, obj):
        (args.out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

    def table(name, records):
        with (args.out / name).open('w') as f:
            w = csv.DictWriter(f, list(records[0]), lineterminator='\n')
            w.writeheader()
            w.writerows(records)

    args.out.mkdir(parents=True, exist_ok=False)
    registry_path = '/workspace/ep_l2_ft20261016_shared/RUN_REGISTRY.json'
    registry = js(registry_path)
    m = registry['mechanism_study_20261019_v1']
    dr = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1/docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d')
    roster = js(dr / 'full_system_v2/SEVEN_INPUTS.json')
    opportunity = rows(dr / 'OPPORTUNITY_TABLE.csv')
    suitability = js(dr / 'input_suitability_20261020_r1/INPUT_APPLICABILITY.json')
    old = rows('/workspace/ep_l2_mechanism_lane3_v1/derived_r2/pressure_and_banks.csv')
    historical = {r['workload']: r for r in old if r['condition'] == 'H0'
                  and r['mode'] == 'B16_BANKED'
                  and r['binary'].startswith('23094a9d')}
    assert len(historical) == 5
    producer = js(m['official_producer_current']['path'])
    assert sources[m['official_producer_current']['path']]['sha256'] == m['official_producer_current']['sha256']
    core = Path(producer['production_source_path'])
    for f in ['ep-l2-tvd-directory.h', 'ep-l2-tvd-cache.inc']:
        read(core / 'src/gpgpu-sim' / f)

    # Explicitly bind the accepted terminal endpoints; do not use active FWT logs.
    pair_key = 'V2_MAIN_convolutionSeparable_S_F_MAIN61'
    pair = m['accepted_pairs'][pair_key]
    assert pair['status'] == 'CURRENT_ACCEPTED'
    accepted = {}
    endpoint_proof = {}
    details = []
    for side, ep in pair['endpoints'].items():
        rid = ep['attempt_id']
        r = m['accepted_results'][rid]
        s = js(r['path'])
        assert sources[r['path']]['sha256'] == r['sha256'] == ep['sha256']
        assert s['identity'] == ep['identity'] == r['identity']
        assert s['identity']['binary_sha256'] == producer['binary_sha256']
        assert s['identity']['workload'] == 'convolutionSeparable'
        profile = s['profile']
        assert profile in ('S', 'F') and profile not in accepted
        metrics = s['mechanism_metrics']
        victims = metrics['full_mechanism_records']['victim']
        assert len(victims) == (64 if profile == 'F' else 0)
        sums = {k: sum(z[k] for z in victims.values()) for k in
                ['clean_installs', 'dirty_installs', 'read_responses',
                 'dirty_forward_responses', 'served_sector_bytes', 'promotions',
                 'directory_queries', 'retention_slot_cycles', 'clean_retention_slot_cycles',
                 'total_retention_slot_cycles', 'bank_wait_cycles', 'icnt_wait_cycles', 'wb_wait_cycles']}
        accepted[profile] = {'attempt_id': rid, 'identity': s['identity'],
                            'local_service': metrics['local_service'],
                            'trigger': metrics['trigger'], 'victim': sums,
                            'wb_created': s['summary']['wb_created'],
                            'bottleneck': metrics['bottleneck'],
                            'source_map_prose': s['summary']['source_map'],
                            'raw_log_sha256': s['raw_log_sha256']}
        endpoint_proof[profile] = r
        for reason, counts in metrics['bottleneck'].items():
            details.append(dict(profile=profile, reason=reason,
                                **{k: counts[k] for k in ['distinct_requests_first_block',
                                   'resolved_first_waits', 'request_wait_cycle_sum',
                                   'request_wait_max', 'blocked_observations_over_slices']}))
    assert set(accepted) == {'S', 'F'}
    assert accepted['S']['identity']['trace_content_sha256'] == accepted['F']['identity']['trace_content_sha256']
    write('ACCEPTED_CONV_MECHANISMS.json', accepted)
    table('CONV_REQUEST_WAIT_OBSERVATIONS.csv', details)

    profiles = []
    metadata = {}
    for w in roster['workloads']:
        name = w['workload']
        registration = next(v for v in m['input_selections'].values()
                            if v['selection']['full_input_identity']['workload'] == name)
        ident = registration['selection']['full_input_identity']
        assert ident['trace_content_sha256'] == w['full_trace_content_sha256']
        held = name == 'btree'
        # The old Btree oracle is invalid for native applicability. Do not use its
        # plausible-looking read/write overlap to rank a victim candidate.
        model = None if held else js(w['model_manifest_path'])
        if model:
            assert sources[w['model_manifest_path']]['sha256'] == w['model_manifest_sha256']
            counts = model['counts']
            kernels = [{'name': Path(k['path']).name, 'opcodes': k['opcodes']}
                       for k in model['kernels']]
        else:
            counts, kernels = {}, []
        metadata[name] = {'trace_content_sha256': ident['trace_content_sha256'],
                          'model_counts': counts, 'per_kernel_opcode_counts': kernels,
                          'temporal_order_available': False, 'L2_order_available': False,
                          'native_input_hold': held}
        h = historical.get(name, {})
        legacy = next((x for x in opportunity if x['workload'] == name
                       and x['baseline_profile'] == 'B0-Legacy'), {})
        banks = [int(h[f'bank{i}_logical_ops']) for i in range(4)] if h else []
        profiles.append({
            'workload': name, 'input_status': 'HOLD_DO_NOT_RUN' if held else 'FROZEN_REGISTERED_E_RUNTIME_GATE_RETAINED',
            'selection_id': registration['selection']['selection_id'],
            'trace_content_sha256': ident['trace_content_sha256'],
            'kernels': w['kernel_count'], 'declared_body_bytes_NOT_READ': w['total_body_bytes'],
            'historical_S_scope': 'SOURCE2309_H0_ONLY_NOT_MAIN61_PERFORMANCE' if h else 'OLDER_B0_CONTEXT_ONLY',
            'historical_S_run_key': h.get('run_key', 'UNKNOWN'),
            'historical_S_wb_created': h.get('wb_created', 'UNKNOWN'),
            'historical_S_copy_lines': h.get('copy_lines', 'UNKNOWN'),
            'historical_S_copy_bytes': h.get('copy_bytes', 'UNKNOWN'),
            'historical_S_wbuf_full_retries': h.get('wbuf_full', 'UNKNOWN'),
            'historical_S_WAD_full_retries': h.get('c7d_wad_full_events', 'UNKNOWN'),
            'historical_S_WAD_hazard_retries': h.get('c7d_wad_hazard_events', 'UNKNOWN'),
            'historical_S_bank_wait_observations': h.get('bank_wait_cycles', 'UNKNOWN'),
            'historical_S_bank0_logical_share': banks[0] / sum(banks) if banks else 'UNKNOWN',
            'older_B0_WAD_full_retries': legacy.get('W_WAD_control_retry_events', 'NOT_USED'),
            'historical_S_source_core': h.get('core', 'UNKNOWN'),
            'historical_S_source_binary': h.get('binary', 'UNKNOWN'),
            'historical_S_raw_log_sha256_NOT_REHASHED': h.get('raw_sha256', 'UNKNOWN'),
            'model_read_and_stored_lines_UNORDERED': counts.get('SAME_LINE_STORE_lines', 0) if model else 'EXCLUDED_INVALID_INPUT',
            'model_read_refs_on_stored_lines_UNORDERED': counts.get('SAME_LINE_STORE_read_lane_references', 0) if model else 'EXCLUDED_INVALID_INPUT',
            'model_write_only_lines': counts.get('NO_GLOBAL_READ_lines', 0) if model else 'EXCLUDED_INVALID_INPUT',
            'short_distance_post_eviction_reuse': 'UNKNOWN',
            'current_actual_victim_read_responses': accepted['F']['victim']['read_responses'] if name == 'convolutionSeparable' else 'UNKNOWN',
            'current_dirty_forward_responses': accepted['F']['victim']['dirty_forward_responses'] if name == 'convolutionSeparable' else 'UNKNOWN',
        })
    table('CANDIDATE_PROFILES.csv', profiles)
    write('SAVED_TRACE_METADATA.json', metadata)
    write('E_INPUT_APPLICABILITY_CONTEXT.json', suitability)
    write('REGISTRY_IDENTITY_SNAPSHOT.json', {
        'snapshot_unix': started, 'registry_updated_at': registry.get('updated_at'),
        'official_producer_current': m['official_producer_current'],
        'accepted_conv_endpoints': endpoint_proof,
        'pair_id': pair_key, 'pair_status': pair['status'],
        'actual_starts': m['actual_starts'], 'maximum_actual_starts': m['maximum_actual_starts'],
        'controller': m['controller'], 'screen_actual_starts': m['screen_actual_starts'],
        'registered_inputs': [p['selection_id'] for p in profiles],
        'active_attempts_not_read': ['E011_618407f0', 'E012_63be0bb4'],
        'source_map_caution': 'Accepted endpoint prose mentions older C994/producer75707624; use exact machine identity and release d010/main61, not stale prose.',
        'E_ledger_or_inputs_modified_by_B': False})
    s, f = accepted['S'], accepted['F']
    write('CONV_SEPARATED_EFFECTS.json', {
        'victim_installs_F': f['victim']['clean_installs'] + f['victim']['dirty_installs'],
        'actual_victim_read_responses_F': f['victim']['read_responses'],
        'actual_victim_served_bytes_F': f['victim']['served_sector_bytes'],
        'dirty_forward_responses_F': f['victim']['dirty_forward_responses'],
        'victim_response_per_install_RATIO_NOT_HIT_RATE': f['victim']['read_responses'] / (f['victim']['clean_installs'] + f['victim']['dirty_installs']),
        'matched_total_lower_reads_S_minus_F': s['local_service']['lower_reads'] - f['local_service']['lower_reads'],
        'matched_total_lower_read_bytes_S_minus_F': s['local_service']['lower_read_bytes'] - f['local_service']['lower_read_bytes'],
        'matched_lower_wb_bytes_F_minus_S': f['local_service']['lower_wb_bytes'] - s['local_service']['lower_wb_bytes'],
        'victim_only_counterfactual_avoided_lower_reads': 'UNKNOWN: 36 actual responses are not an isolated V-only counterfactual; 66 net lower delta includes W/V/T/M interactions and promotions',
        'exclusive_GPU_stall_cycles_saved_by_W_or_V': 'UNKNOWN',
        'wait_interpretation': 'First-block request wait sums can overlap reasons/slices, identities and traffic change; not exclusive GPU stall or a matched per-UID causal estimate.',
        'ranking_uses_cycles_or_speedup': False})
    write('SOURCE_MANIFEST.json', sources)
    write('CPU_SCREEN_RECEIPT.json', {
        'started_unix': started, 'finished_unix': time.time(),
        'unique_source_bytes': sum(v['bytes'] for v in sources.values()),
        'read_bytes_charged': 16 * 1024 * 1024 - budget,
        'read_budget_bytes': 16 * 1024 * 1024,
        'source_files': len(sources), 'trace_body_reads': 0, 'raw_log_reads': 0,
        'oracle_SQLite_reads': 0, 'shared_storage_directory_scans': 0,
        'simulator_or_GPU_starts': 0, 'builds': 0, 'new_watchers': 0,
        'candidate_count': len(profiles), 'main61_conv_aggregate_slices_F': 64,
        'original_B_Core_preserved': '4770adffb2531e5a213601053ac02fdbbc621e77'})
    print(json.dumps({'status': 'METADATA_SCREEN_COMPLETE', 'candidates': len(profiles),
                      'read_bytes': 16 * 1024 * 1024 - budget, 'seconds': time.time() - started}))


if __name__ == '__main__':
    main()
