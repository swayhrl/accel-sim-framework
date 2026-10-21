#!/usr/bin/env python3
"""Finite review of saved FWT tails and SGEMM metadata; no trace/simulator IO."""
import argparse
import collections
import csv
import hashlib
import io
import json
import time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True, type=Path)
    out = ap.parse_args().out
    out.mkdir(parents=True, exist_ok=False)
    started = time.time()
    sources = {}
    charged = 0

    def read(path):
        nonlocal charged
        p = Path(path)
        assert p.stat().st_size < 8 * 1024**2
        b = p.read_bytes()
        charged += len(b)
        assert charged < 20 * 1024**2
        sources[str(p)] = {'bytes_read': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
        return b

    def js(p):
        return json.loads(read(p))

    def rows(p):
        return list(csv.DictReader(io.StringIO(read(p).decode())))

    def write(name, obj):
        (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')

    shared = Path('/workspace/ep_l2_ft20261016_shared')
    m = js(shared / 'RUN_REGISTRY.json')['mechanism_study_20261019_v1']
    dr = Path('/workspace/worktrees/accel-sim-ep-l2-ms20261019-d-analysis-v1/docs/ep_l2/mechanism_study_2026_10_19_v1/lane_d')
    features = js(dr / 'main61_attribution_20261020_r2/S_ONLY_CANDIDATE_FEATURES.json')
    proposal = js(dr / 'input_suitability_20261020_r1/SGEMM_PROPOSAL_TO_E.json')
    audit = js(dr / 'input_suitability_20261020_r1/CANDIDATE_AUDIT.json')
    sgemm_audit = next(x for x in audit['results'] if x['workload'] == 'sgemm')
    assert sgemm_audit['trace_content_sha256'] == proposal['trace_content_sha256']
    assert sources[str(dr / 'input_suitability_20261020_r1/CANDIDATE_AUDIT.json')]['sha256'] == proposal['input_proof_sha256']
    write('D_PRIOR_SELECTION_AND_SGEMM_PROOF.json', {
        'selection_rule': features['selection_rule'],
        'FWT_SGEMM_S_only_features': [x for x in features['features'] if x['workload'] in ['FWT_7_21', 'sgemm']],
        'SGEMM_proposal': proposal, 'SGEMM_saved_input_audit': sgemm_audit})

    ft_selection = next(v for v in m['input_selections'].values()
                        if v['selection']['full_input_identity']['workload'] == 'FWT_7_21')
    fwt_manifest_path = dr / 'full_system_v2/readonly_evidence/FWT_7_21/manifest.json'
    fwt_model = js(fwt_manifest_path)
    write('FWT_SAVED_UNORDERED_MODEL.json', fwt_model)
    snapshots = {}
    evidence = []
    for rid in ['E011_618407f0', 'E012_63be0bb4']:
        attempt = next(x for x in m['attempts'] if x['attempt_id'] == rid)
        receipt = js(attempt['receipt_path'])
        assert sources[attempt['receipt_path']]['sha256'] == attempt['receipt_sha256']
        assert receipt['identity'] == attempt['identity']
        assert receipt['status'] == 'INCOMPLETE' and rid not in m['accepted_results']
        assert receipt['identity']['trace_content_sha256'] == ft_selection['selection']['full_input_identity']['trace_content_sha256']
        assert not receipt['complete_input_verified']
        raw = Path(attempt['result_directory']) / 'raw.log'
        before = raw.stat()
        offset = max(0, before.st_size - 1572864)
        with raw.open('rb') as f:
            f.seek(offset)
            data = f.read(1572864)
        after = raw.stat()
        assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        charged += len(data)
        assert charged < 20 * 1024**2
        sources[str(raw)] = {'file_bytes': before.st_size, 'bytes_read': len(data),
                             'offset': offset, 'tail_sha256': hashlib.sha256(data).hexdigest(),
                             'full_raw_sha256_from_E_NOT_REHASHED': receipt['raw_log_sha256'],
                             'range_only_not_full_raw_hash': True}
        lines = data.decode(errors='strict').splitlines()[1 if offset else 0:]
        wanted = ['EPL2FTV1|SUMMARY', 'EPL2TVDV2|SUMMARY',
                  'EPL2MSV1|OBSERVER', 'EPL2MSV1|LOCAL_DIAGNOSTIC']
        grouped = collections.defaultdict(list)
        for line in lines:
            typ = '|'.join(line.split('|')[:2])
            if typ in wanted:
                d = dict(x.split('=', 1) for x in line.split('|')[2:] if '=' in x)
                grouped[typ].append((line, d))
        aggregate, saved = {}, []
        for typ in wanted:
            values = grouped[typ][-64:]
            if not values:
                assert typ == 'EPL2TVDV2|SUMMARY' and receipt['profile'] == 'S'
                aggregate[typ] = {'status': 'FEATURE_OFF_NOT_A_MISSING_ZERO_MEASUREMENT'}
                continue
            assert [int(x[1]['slice']) for x in values] == list(range(64)), (rid, typ)
            fields = {
                'EPL2FTV1|SUMMARY': ['wb_created', 'wb_completed', 'wb_lower_accept',
                    'wbuf_full', 'pool_full', 'copy_lines', 'copy_bytes', 'staging_reads',
                    'bank_block', 'issue_block', 'pin_block', 'rollback'],
                'EPL2TVDV2|SUMMARY': ['clean_installs', 'dirty_installs', 'read_responses',
                    'dirty_forward_responses', 'served_sectors', 'served_sector_bytes',
                    'promotions', 'directory_queries', 'lookup_wait_cycles',
                    'wb_wait_cycles', 'bank_wait_cycles', 'icnt_wait_cycles'],
                'EPL2MSV1|OBSERVER': ['lower_reads', 'lower_read_bytes', 'lower_writes',
                    'lower_write_bytes', 'lower_wb_bytes', 'unclassified_refusal_observations'],
                'EPL2MSV1|LOCAL_DIAGNOSTIC': ['logical_copy_reads', 'logical_copy_writes',
                    'physical_grants', 'exempt_response', 'exempt_fill', 'exempt_lower_wb',
                    'exempt_frontend', 'exempt_copy_read', 'exempt_copy_write'],
            }[typ]
            aggregate[typ] = {k: sum(int(d[k]) for _, d in values) for k in fields}
            aggregate[typ]['slice_count'] = 64
            if typ == 'EPL2FTV1|SUMMARY':
                assert len({d['observed_cycles'] for _, d in values}) == 1
                aggregate[typ]['common_observed_cycles_IDENTITY_NOT_RANK'] = values[0][1]['observed_cycles']
            saved.extend(x[0] for x in values)
        (out / (rid + '_LAST_OBSERVED_RECORDS.txt')).write_text('\n'.join(saved) + '\n')
        snapshots[receipt['profile']] = {'attempt_id': rid, 'receipt': receipt,
                                        'last_observed_cumulative_snapshot': aggregate,
                                        'not_accepted_terminal_or_performance': True}
        evidence.append({'attempt_id': rid, 'snapshot_rows': len(saved),
                         'FWT_actual_start_finished_unix': attempt['finished_unix']})
    write('FWT_UNACCEPTED_OBSERVED_MECHANISMS.json', snapshots)

    tr = Path('/workspace/worktrees/accel-sim-ep-l2/docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1')
    old_comparison = next(x for x in rows(tr / 'target_baseline_comparison.csv') if x['workload'] == 'sgemm')
    old_runs = [x for x in rows(tr / 'ACCEPTED_FORMAL_RUNS.csv') if x['workload'] == 'sgemm']
    old_evidence = {}
    for run in old_runs:
        assert run['trace_sha256'] == sgemm_audit['commandlist_sha256']
        rd = Path(run['run_directory'])
        slices = rows(rd / 'target_slice.csv')
        summary = rows(rd / 'target_summary.csv')[0]
        assert len(slices) == 64
        sums = {k: sum(int(x[k]) for x in slices) for k in [
            'c7d_bank_wb_readout', 'c7d_bank_resident_write',
            'c7e_dram_successful_write_bytes', 'c7e_dram_successful_read_bytes',
            'c7d_wad_full_events', 'c7d_wad_hazard_events']}
        old_evidence[run['variant']] = {
            'identity_and_historical_acceptance': run, 'summary': summary,
            'slice_counter_sums': sums,
            'dirty_resident_peak_per_slice_range': [min(int(x['c7d_resident_dirty_max']) for x in slices), max(int(x['c7d_resident_dirty_max']) for x in slices)],
            'victim_read_responses': 'NOT_INSTRUMENTED_NOT_ZERO',
            'dirty_forward_responses': 'NOT_INSTRUMENTED_NOT_ZERO',
            'explicit_WBUF_copy_count': 'NOT_EMITTED_BY_OLD_B0',
            'read_store_line_intersection': 'UNKNOWN_NO_SAVED_ADDRESS_AGGREGATE',
            'post_eviction_short_distance_reuse': 'UNKNOWN'}
    write('SGEMM_HISTORICAL_B0_COUNTERS.json', {'old_comparison': old_comparison, 'variants': old_evidence})
    core = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ms20261020-a-r39-own-pending-v1')
    for f in ['ep-l2-tvd-directory.h', 'ep-l2-tvd-cache.inc']:
        read(core / 'src/gpgpu-sim' / f)
    write('REGISTRY_SCOPE_SNAPSHOT.json', {
        'at_unix': started, 'actual_starts': m['actual_starts'], 'maximum_actual_starts': m['maximum_actual_starts'],
        'controller': m['controller'], 'FWT_acceptance': 'INCOMPLETE_NOT_ACCEPTED',
        'SGEMM_registered': any(x['selection']['full_input_identity']['workload'] == 'sgemm' for x in m['input_selections'].values()),
        'FWT_input_registration': ft_selection,
        'producer_reference': m['official_producer_current'],
        'evidence_scope': 'metadata and unaccepted cumulative snapshots, not new E qualification',
        'B_E_registry_writes': 0})
    write('SOURCE_MANIFEST.json', sources)
    write('CPU_REVIEW_RECEIPT.json', {
        'started_unix': started, 'finished_unix': time.time(), 'bytes_read': charged,
        'read_cap_bytes': 20 * 1024**2, 'raw_tail_cap_per_FWT_attempt': 1572864,
        'actual_trace_body_reads': 0, 'SQLite_reads': 0, 'new_builds': 0,
        'new_native_or_full_application_or_GPU_starts': 0, 'new_watchers': 0,
        'shared_storage_scans': 0, 'old_snapshots': evidence,
        'F_cycles_or_speedups_used_for_selection': False})
    print(json.dumps({'status': 'COMPLETE_BOUNDED_SAVED_EVIDENCE_REVIEW', 'bytes_read': charged,
                      'seconds': time.time() - started}))


if __name__ == '__main__':
    main()
