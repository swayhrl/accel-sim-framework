"""Freeze the declared five-workload R0 cohort only after all pairs validate."""
import csv
import json
import math
from pathlib import Path

from campaign_r0 import csv_write
from package_r0 import checksum, freeze_checksums
from registry import write_json

REPO = Path(__file__).resolve().parents[3]
WORKLOADS = ('sad', 'vectorAdd_4M', 'cfd_097k', 'convolutionSeparable', 'FWT_7_21')


def collect(root):
    if (REPO / 'docs/ep_l2/codex_handoff/fast_track_2026_10_16_v1/lane5/SCIENTIFIC_HOLD.json').is_file():
        raise ValueError('R0 scientific qualification suspended; no primary cohort average')
    rows, manifests = [], []
    for workload in WORKLOADS:
        pack = root / ('FT20261016_LANE5_R0_' + workload.upper() + '_PAIR_r1')
        if not pack.is_dir():
            raise ValueError('declared cohort incomplete: ' + workload)
        for line in (pack / 'SHA256SUMS').read_text().splitlines():
            expected, name = line.split('  ', 1)
            if checksum(pack / name) != expected:
                raise ValueError('frozen pair checksum mismatch: ' + str(pack / name))
        results = list(csv.DictReader((pack / 'RESULTS.csv').open()))
        if [r['mode'] for r in results] != ['B16_BANKED', 'U_WB16']:
            raise ValueError('expected one B16/U_WB16 pair')
        if any(r['status'] != 'COMPLETE_VALID' or r['workload'] != workload for r in results):
            raise ValueError('invalid/incomplete workload pair')
        b, u = results
        for key in ('core_source_commit', 'framework_source_commit', 'binary_sha256',
                    'trace_content_sha256', 'epoch_range', 'ideal_vector', 'instructions'):
            if b[key] != u[key]:
                raise ValueError('unmatched pair dimension: ' + key)
        for result, unified in [(b, False), (u, True)]:
            features = json.loads(result['feature_vector'])
            if (features['unified_wb'] is not unified or features['wbuf_entries'] != 16 or
                features['payload_capacity_per_slice'] != 1168 or
                any(features[k] for k in ('ro', 'tvd', 'adaptive_policy')) or
                any(json.loads(result['ideal_vector']).values())):
                raise ValueError('non-primary vector entered R0 cohort')
        resource = list(csv.DictReader((pack / 'RESOURCE_MOVEMENT.csv').open()))
        item = {'workload': workload, 'B16_cycles': int(b['cycles']),
                'U_WB16_cycles': int(u['cycles']),
                'speedup_B16_over_U_WB16': int(b['cycles']) / int(u['cycles']),
                'cycle_reduction_percent': (1 - int(u['cycles']) / int(b['cycles'])) * 100,
                'B16_run_key': b['run_key'], 'U_WB16_run_key': u['run_key']}
        for metric in ('staged_max_across_slice_peaks', 'staging_mean_per_slice_cycle',
                       'wbuf_full', 'pool_full', 'copy_lines', 'bank_wait_cycles',
                       'c7d_wad_full_events', 'c7d_l2_to_dram_full_block',
                       'c7e_dram_successful_read_bytes', 'c7e_dram_successful_write_bytes'):
            item['B16_' + metric] = resource[0][metric]
            item['U_WB16_' + metric] = resource[1][metric]
        rows.append(item)
        manifests.append({'workload': workload, 'pack': str(pack.relative_to(REPO)),
                          'checksums_sha256': checksum(pack / 'SHA256SUMS'),
                          'runs': results})
    identities = {(r['core_source_commit'], r['framework_source_commit'], r['binary_sha256'])
                  for m in manifests for r in m['runs']}
    if len(identities) != 1:
        raise ValueError('mixed producing releases in cohort')
    return rows, manifests


def main():
    root = REPO / 'docs/ep_l2/review_packs'
    rows, manifests = collect(root)
    out = root / 'FT20261016_LANE5_R0_PRIMARY_COHORT_r1'
    out.mkdir(exist_ok=False)
    csv_write(out / 'PAIRED_RESULTS.csv', rows)
    all_runs = [r for m in manifests for r in m['runs']]
    csv_write(out / 'BASELINE_RESULTS.csv', [r for r in all_runs if r['mode'] == 'B16_BANKED'])
    csv_write(out / 'MECHANISM_RESULTS.csv', [r for r in all_runs if r['mode'] == 'U_WB16'])
    summary = {'status': 'COMPLETE_VALID', 'cohort': list(WORKLOADS), 'pairs': 5, 'runs': 10,
        'geometric_mean_speedup_B16_over_U_WB16': math.exp(sum(math.log(r['speedup_B16_over_U_WB16']) for r in rows) / 5),
        'improved_workloads': sum(r['U_WB16_cycles'] < r['B16_cycles'] for r in rows),
        'ties': sum(r['U_WB16_cycles'] == r['B16_cycles'] for r in rows),
        'regressed_workloads': sum(r['U_WB16_cycles'] > r['B16_cycles'] for r in rows),
        'scope': 'five declared development workloads, full application, R0 primary 1168-slot/128B common latch, TVD/RO/ideals OFF',
        'attribution': 'role transfers or bank/copy reductions alone do not prove dynamic capacity benefit; stronger static redivision/copy control required'}
    write_json(out / 'SUMMARY.json', summary)
    write_json(out / 'SOURCE_MANIFEST.json', {'pairs': manifests})
    (out / 'README.md').write_text('# R0 declared five-workload primary cohort\n\n' +
        'All five paired full applications are COMPLETE_VALID. Geometric mean\n' +
        'is computed only over this explicitly complete development cohort.\n' +
        'Ties and regressions are retained. PAIRED_RESULTS.csv is ready for Lane6.\n\n' +
        'Exact source/config/binary/full-trace identities and raw indexes remain\n' +
        'in the five immutable pair packs referenced by SOURCE_MANIFEST.\n' +
        'Hardware requester/resource closure is checked for every run. Numerical\n' +
        'SASS application output is unavailable; qualification is symbolic sector\n' +
        'versions plus request/resource lifecycles. No TVD/RO/ideal claim.\n')
    freeze_checksums(out)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
