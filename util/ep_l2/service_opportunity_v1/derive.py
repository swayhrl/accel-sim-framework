#!/usr/bin/env python3
"""Bounded, read-only extraction of accepted finite service evidence.

No simulator launch, trace-body scan, ledger update, or synthetic timing inference.
Final cumulative rows replace earlier kernel-boundary prints; windows stay windows.
"""
import argparse
import collections
import csv
import datetime
import fcntl
import hashlib
import json
from pathlib import Path
import subprocess

AUTHORITY = 'c8aa87bdbe220853eb2d27d8babd448cff02a66e'
ROOT = Path('/workspace/ep_l2_ft20261016_shared')
L5 = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1')
FINITE_BINARY = 'fb67448d08818bc8cbe72961580e8340f0e6f337a4df95e7c8ee9468472953f7'
WORKLOADS = ('convolutionSeparable', 'FWT_7_21')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def write_csv(p, rows):
    if not rows:
        return
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def parse(path):
    """Only the last application/slice and FT/slice rows are cumulative totals."""
    final = collections.defaultdict(dict)
    windows = []
    prefixes = collections.Counter()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for line in stream:
            h.update(line)
            if not line.startswith((b'EPL2', b'L2CHARV1')):
                continue
            parts = line.decode().strip().split('|')
            prefixes[parts[0]] += 1
            fields = dict(p.split('=', 1) for p in parts[1:] if '=' in p)
            if parts[0] == 'EPL2B0V1' and fields.get('scope') == 'application':
                final['B0'][int(fields['slice'])] = fields
            elif parts[0] == 'EPL2FTV1' and parts[1] == 'SUMMARY':
                final['FT'][int(fields['slice'])] = fields
            elif parts[0] == 'EPL2STRUCTV1':
                final[parts[1]][int(fields['slice'])] = fields
            elif parts[0] == 'EPL2M0AV1' and fields.get('scope') == 'application':
                final['M0'][int(fields['slice'])] = fields
            elif parts[0] == 'L2CHARV1' and parts[1] in ('SLICE', 'SLICE_DETAIL'):
                final[parts[1]][int(fields['slice'])] = fields
            elif parts[0] == 'EPL2B0V1' and fields.get('scope') == 'window':
                windows.append(fields)
    assert set(final['B0']) == set(range(64))
    assert set(final['FT']) == set(range(64))
    return h.hexdigest(), final, windows, dict(prefixes)


def total(final, section, key):
    rows = final.get(section, {})
    if len(rows) != 64 or any(key not in r for r in rows.values()):
        return None
    return sum(int(r[key]) for r in rows.values())


def maximum(final, section, key):
    rows = final.get(section, {})
    if len(rows) != 64 or any(key not in r for r in rows.values()):
        return None
    return max(int(r[key]) for r in rows.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    client = json.loads((ROOT / 'CLIENT_CONTRACT.json').read_text())
    binding = client['scientific_acceptance']
    snapshot_path = Path(binding['snapshot_path'])
    snapshot_bytes = snapshot_path.read_bytes()
    assert digest(snapshot_bytes) == binding['sha256']
    relative = str(snapshot_path.relative_to(L5))
    published = subprocess.check_output(['git', 'show', binding['publication_commit'] + ':' + relative], cwd=L5)
    assert published == snapshot_bytes
    snapshot = json.loads(snapshot_bytes)
    with (ROOT / 'REGISTRY.lock').open() as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        registry = json.loads((ROOT / 'RUN_REGISTRY.json').read_text())
    write_json(args.out / 'AUTHORITY.json', {
        'goal': 'EPL2_SERVICE_OPPORTUNITY_AND_MATCHED_EFFECT_V1',
        'coordination_commit': AUTHORITY, 'section': 4,
        'scientific_acceptance': binding, 'observed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'script_sha256': digest(Path(__file__).read_bytes()),
        'registry_updated_at': registry['updated_at'],
        'trace_body_scans': 0, 'only_current_accepted': True,
    })
    (args.out / 'SCIENTIFIC_ACCEPTANCE_SNAPSHOT.json').write_bytes(snapshot_bytes)
    catalog, metrics, window_rows, provenance, raw_fields = [], [], [], [], []
    for row in snapshot['rows']:
        if row['scientific_acceptance'] != 'CURRENT_ACCEPTED':
            continue
        ident = row['identity']
        profile = row.get('profile', row['mode'])
        base = dict(run_key=row['run_key'], workload=row['workload'], condition=row.get('regime', 'H0'),
                    profile=profile, mode=row['mode'], cycles=row['observed_cycles'], instructions=row['instructions'],
                    core=ident['core_source_commit'], framework=ident['framework_source_commit'],
                    binary=ident['binary_sha256'], config=ident['runtime_config_sha256'], trace=ident['trace_content_sha256'],
                    scientific_scope=row.get('scientific_scope', 'FINITE_NATIVE_SYMBOLIC_SECTOR'), acceptance_generation=snapshot['generation'])
        catalog.append(base)
        # Ideals are preserved in the catalog, never repurposed as finite evidence.
        if profile.startswith('I_') or profile == 'NATIVE_OFF_CONTROL':
            continue
        review = L5 / row['independent_review']['path']
        assert digest(review.read_bytes()) == row['independent_review']['sha256']
        directory = Path(registry['runs'][row['run_key']]['result_directory'])
        raw = directory / 'raw.log'
        got, final, windows, prefixes = parse(raw)
        assert got == row['raw_log_sha256']
        record = dict(base, raw_log=str(raw), raw_sha256=got)
        for key in ('samples', 'block_payload', 'block_bank', 'block_lower', 'bank_logical_ops', 'bank_grants',
                    'bank_attempts', 'bank_retry_attempts', 'bank_true_conflict_ops', 'bank_true_conflict_events', 'bank_wait_cycles',
                    'c7d_wad_full_events', 'c7d_wad_hazard_events', 'c7d_wad_hazard_wait_cycles',
                    'c7d_missq_full_block', 'c7d_l2_to_dram_full_block', 'c7d_dram_issue_eligible',
                    'c7d_dram_scheduler_full_block', 'c7d_dram_credit_block', 'c7d_dram_returnq_block',
                    'c7d_bank_wb_readout', 'c7d_bank_resident_hit_read', 'c7d_bank_fill_write'):
            record[key] = total(final, 'B0', key)
        for key in ('pin_block', 'pool_full', 'wbuf_full', 'bank_block', 'issue_block', 'copy_lines',
                    'staging_reads', 'wb_created', 'wb_completed', 'wb_lower_accept', 'rollback', 'wb_live',
                    'reserved', 'read_refs', 'wb_slots'):
            record[key] = total(final, 'FT', key)
        record['WAD_peak'] = maximum(final, 'B0', 'wad_max')
        record['MissQ_peak'] = maximum(final, 'B0', 'missq_max')
        record['WB_record_peak'] = maximum(final, 'FT', 'staged_max')
        record['bank_service_peak'] = max((maximum(final, 'BANK_PEAK', f'bank{i}') or 0) for i in range(4)) if final.get('BANK_PEAK') else None
        for key in ('refusal_attempts', 'pending_retry_calls', 'rollback_releases', 'lower_accept_releases'):
            record['quota_' + key] = total(final, 'WB_QUOTA', key)
        for key in ('m0_frontend_head_observed_cycles', 'm0_frontend_head_any_blocked_cycles',
                    'm0_frontend_head_blocked_cycles_wad_full', 'm0_frontend_head_blocked_cycles_wad_hazard',
                    'm0_frontend_head_blocked_cycles_missq', 'm0_frontend_head_blocked_cycles_responseq'):
            record[key] = total(final, 'M0', key)
        for key in ('lower_drain_eligible_cycles', 'lower_drain_blocked_cycles',
                    'mshr_response_eligible_cycles', 'mshr_response_blocked_cycles'):
            record[key] = total(final, 'SLICE_DETAIL', key)
        # Neither existing bank totals nor queue occupancy reveal a joint cycle witness.
        for key in ('mq2_safe_second_behind_bank_blocked_WB', 'rg1_held_not_ready_another_ready_zero_service',
                    'frontend_other_request_refused_by_pending_token'):
            record[key] = None
        metrics.append(record)
        window_rows.append(dict(run_key=row['run_key'], workload=row['workload'], condition=base['condition'], profile=profile,
                                slice_window_records=len(windows), sampled_slice_cycles=sum(int(w['samples']) for w in windows),
                                max_window_missq_integer_average=max((int(w['missq_avg']) for w in windows), default=None),
                                max_window_lowerq_integer_average=max((int(w['lowerq_avg']) for w in windows), default=None),
                                windows_nonzero_missq_average_and_bank_wait=sum(int(w['missq_avg']) > 0 and int(w['bank_wait_cycles']) > 0 for w in windows),
                                windows_nonzero_WAD_average_and_bank_wait=sum(int(w['wad_avg']) > 0 and int(w['bank_wait_cycles']) > 0 for w in windows),
                                interpretation='Coarse slice-window coexistence only; not same-cycle ordering/readiness, opportunity count or exclusive GPU stall'))
        raw_fields.append(dict(run_key=row['run_key'], record_counts=prefixes,
                               fields_by_section={k: sorted(next(iter(v.values()))) for k, v in final.items() if v}))
        provenance.append(dict(run_key=row['run_key'], identity=ident, raw_log=str(raw), raw_sha256=got,
                               review=str(review), review_sha256=digest(review.read_bytes()),
                               input_spec_sha256=digest((directory / 'input_spec.json').read_bytes()),
                               input_audit_sha256=digest((directory / 'input_audit.json').read_bytes())))
    four = []
    for work in WORKLOADS:
        found = {r['profile']: r for r in catalog if r['workload'] == work and r['condition'] == 'H0' and r['binary'] == FINITE_BINARY}
        need = ('B16_OFF', 'S64', 'U_CAP16', 'U_OFF')
        if not all(p in found for p in need):
            four.append(dict(workload=work, status='INCOMPLETE_ACCEPTED_FOUR_MODE', missing=','.join(p for p in need if p not in found)))
            continue
        b, s, cap, u = (found[p] for p in need)
        for key in ('core', 'framework', 'binary', 'trace', 'instructions', 'condition', 'scientific_scope'):
            assert len({r[key] for r in (b, s, cap, u)}) == 1
        four.append(dict(workload=work, status='CURRENT_ACCEPTED_HISTORICAL_OFF_ONLY', core=b['core'], framework=b['framework'],
                         binary=FINITE_BINARY, trace=b['trace'], C_B=b['cycles'], C_S64=s['cycles'], C_U_CAP16=cap['cycles'], C_U=u['cycles'],
                         S_EP=b['cycles'] / u['cycles'], S_static=s['cycles'] / u['cycles'],
                         U_capacity_marginal=cap['cycles'] / u['cycles'], S64_vs_B=b['cycles'] / s['cycles'],
                         delta_B_minus_U=b['cycles'] - u['cycles'], delta_S64_minus_U=s['cycles'] - u['cycles'],
                         delta_Ucap_minus_U=cap['cycles'] - u['cycles'],
                         B_key=b['run_key'], S64_key=s['run_key'], U_CAP16_key=cap['run_key'], U_key=u['run_key'],
                         reuse_as_new_candidate_OFF='NO_UNLESS_EXACT_SAME_OFF_ON_CANDIDATE_RELEASE_ACCEPTED'))
    cells, comparisons = [], []
    for work in WORKLOADS:
        trace = next(r['trace'] for r in catalog if r['workload'] == work and r['condition'] == 'H0' and r['binary'] == FINITE_BINARY)
        for optimization in ('OFF', 'MQ2', 'RG1'):
            comparisons.append(dict(workload=work, optimization=optimization, condition='H0', C_B=None, C_S64=None, C_U=None,
                                    S_EP=None, S_static=None, interaction_EP_vs_OFF=None, interaction_static_vs_OFF=None,
                                    absolute_speedup_B_vs_OFF=None, absolute_speedup_S64_vs_OFF=None, absolute_speedup_U_vs_OFF=None,
                                    candidate_release=None, binary=None, acceptance_generation=None,
                                    status='NOT_RUN_AWAITING_CANDIDATE_PUBLICATION_AND_INDEPENDENT_QUALIFICATION'))
            for architecture in ('B16', 'S64', 'Unified'):
                cells.append(dict(cell=f'{work}__{architecture}__{optimization}', workload=work, architecture=architecture,
                                  condition='H0', optimization=optimization, cycles=None, instructions=None,
                                  core=None, framework=None, binary=None, config=None, effective_config_sha256=None,
                                  non_mechanism_config_projection_sha256=None, trace=trace, epoch_range='all/full_application',
                                  qualification_receipt=None, source_run_key=None, raw_sha256=None, acceptance_generation=None,
                                  status='NOT_RUN_AWAITING_PRODUCER', missing_is_not_zero=True))
    write_csv(args.out / 'accepted_catalog.csv', catalog)
    write_csv(args.out / 'finite_service_metrics.csv', metrics)
    write_csv(args.out / 'window_availability_summary.csv', window_rows)
    write_csv(args.out / 'four_mode_OFF_context.csv', four)
    write_csv(args.out / 'matched_effect_comparison_TEMPLATE.csv', comparisons)
    write_json(args.out / 'matched_endpoints_TEMPLATE.json', cells)
    write_json(args.out / 'RAW_FIELD_AVAILABILITY.json', raw_fields)
    write_json(args.out / 'SOURCE_INPUT_MANIFEST.json', provenance)
    write_json(args.out / 'DERIVATION_RECEIPT.json', dict(status='PASS_ACCEPTED_RAW_IDENTITY_AND_FINAL_CUMULATIVE_EXTRACTION',
               accepted_rows=len(catalog), finite_raw_logs=len(metrics), window_rows=len(window_rows),
               historical_four_mode_groups=len(four), candidate_endpoints=len(cells),
               candidate_cycles_measured=0, full_apps_started=0, trace_body_scans=0,
               snapshot_generation=snapshot['generation'], exclusive_GPU_stall_inference=False))
    print(json.dumps(dict(accepted_rows=len(catalog), finite_raw_logs=len(metrics), windows=len(window_rows), four_mode=four), indent=2))


if __name__ == '__main__':
    main()
