"""R0 rolling full-application pairs; independent R0 qualification is mandatory."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import csv
import json
from pathlib import Path
import re

from registry import Registry, write_json
from run import run, digest

REPO = Path(__file__).resolve().parents[3]


def ft_metrics(directory):
    final = {}
    with (directory / 'raw.log').open(errors='replace') as stream:
        for line in stream:
            if not line.startswith('EPL2FTV1|SUMMARY|'):
                continue
            row = {k: int(v) for k, v in (part.split('=', 1) for part in line.strip().split('|')[2:])}
            final[row['slice']] = row
    if set(final) != set(range(64)):
        raise ValueError('exact 64 final FT slices required')
    rows = list(final.values())
    names = ('accepted', 'wb_created', 'wb_completed', 'wb_lower_accept', 'wbuf_full',
             'pool_full', 'pin_block', 'bank_block', 'issue_block', 'copy_lines',
             'copy_bytes', 'staging_reads', 'staging_lifetime', 'borrow_resident',
             'borrow_bypass', 'rollback', 'version_checks', 'observed_cycles',
             'wb_occupancy_sum', 'descriptor_responses')
    result = {key: sum(r[key] for r in rows) for key in names}
    result['staged_max_across_slice_peaks'] = max(r['staged_max'] for r in rows)
    result['staging_mean_per_slice_cycle'] = result['wb_occupancy_sum'] / result['observed_cycles']
    result['capacity_above_C16_observed'] = result['staged_max_across_slice_peaks'] > 16
    return result


def b0_metrics(directory):
    # Producer parser is frozen separately from runtime, and writes only a new
    # derived directory. The campaign adapter performs extraction without reruns.
    final = {}
    native = {}
    with (directory / 'raw.log').open(errors='replace') as stream:
        for line in stream:
            if line.startswith('EPL2B0V1|scope=application|'):
                parts = dict(p.split('=', 1) for p in line.strip().split('|')[1:])
                final[int(parts['slice'])] = parts
            if match := re.fullmatch(r'(gpu_tot_dram_reads|gpu_tot_dram_writes)\s*=\s*(\d+)\s*', line):
                native[match[1]] = int(match[2])
    if set(final) != set(range(64)):
        raise ValueError('exact 64 final application B0 records required')
    rows = list(final.values())
    summed = {name: sum(int(row[name]) for row in rows) for name in
        ('c7d_wad_full_events', 'c7d_wad_hazard_events', 'bank_wait_cycles',
         'bank_logical_ops', 'bank_true_conflict_ops', 'c7d_l2_to_dram_full_block',
         'c7d_dram_scheduler_full_block', 'c7e_dram_successful_read_bytes',
         'c7e_dram_successful_write_bytes')}
    summed['lowerq_avg_mean_across_slices'] = sum(int(r['lowerq_avg']) for r in rows) / 64
    summed['lowerq_max_across_slice_peaks'] = max(int(r['lowerq_max']) for r in rows)
    return {'b0_app_records': final, 'native_dram_counts_if_emitted': native,
            'aggregate': summed, 'scope': 'sum of source-defined per-slice events/bytes; occupancy explicitly mean/max'}


def csv_write(path, rows):
    if not rows:
        raise ValueError('a frozen pair must contain actual observations')
    with path.open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def publish_pair(workload, results, specs, stage_root):
    actual = []
    for result in results:
        if result['status'] == 'DUPLICATE_NOT_LAUNCHED':
            existing = result['existing']
            if existing['status'] != 'COMPLETE_VALID':
                raise ValueError('existing task is not a completed valid result; never relaunch')
            result = json.loads((Path(existing['result_directory']) / 'run_status.json').read_text())
        actual.append(result)
    rows = []
    for mode, result, spec in zip(('B16_BANKED', 'U_WB16'), actual, specs):
        identity = spec['identity']
        row = {'workload': workload, 'mode': mode, 'status': result['status'],
               'run_key': result['run_key'], 'core_source_commit': identity['core_source_commit'],
               'framework_source_commit': identity['framework_source_commit'],
               'binary_sha256': identity['binary_sha256'],
               'runtime_config_sha256': identity['runtime_config_sha256'],
               'trace_content_sha256': identity['trace_content_sha256'],
               'feature_vector': json.dumps(identity['feature_vector'], sort_keys=True),
               'ideal_vector': json.dumps(identity['ideal_vector'], sort_keys=True),
               'epoch_range': json.dumps(identity['epoch_range'], sort_keys=True),
               'cycles': result.get('summary', {}).get('cycles'),
               'instructions': result.get('summary', {}).get('instructions'),
               'raw_log_sha256': result.get('raw_log_sha256')}
        rows.append(row)
    path = stage_root / ('pair_' + workload)
    path.mkdir(exist_ok=False)
    write_json(path / 'PAIR_RECEIPT.json', {'workload': workload,
        'status': 'COMPLETE_VALID' if all(r['status'] == 'COMPLETE_VALID' for r in actual) else 'INCOMPLETE_OR_FAILED',
        'results': actual, 'specs': specs, 'population': 'one paired full workload; no suite average',
        'data_scope': 'SYMBOLIC_SECTOR_VERSION_REFERENCE_AND_REQUEST_LIFECYCLE; numerical SASS output unavailable'})
    csv_write(path / 'RESULTS.csv', rows)
    if all(r['status'] == 'COMPLETE_VALID' for r in actual):
        if rows[0]['instructions'] != rows[1]['instructions']:
            raise ValueError('paired application instruction count changed')
        for field in ('core_source_commit', 'framework_source_commit', 'binary_sha256',
                      'trace_content_sha256', 'epoch_range', 'ideal_vector'):
            if rows[0][field] != rows[1][field]:
                raise ValueError('mixed-source/input pair: ' + field)
        metrics = []
        for row in rows:
            directory = Path('/workspace/results/ep_l2_ft20261016') / row['run_key']
            b0 = b0_metrics(directory)
            metrics.append({'workload': workload, 'mode': row['mode'], 'run_key': row['run_key'],
                            **ft_metrics(directory), **b0['aggregate']})
            write_json(path / (row['mode'] + '_B0_NATIVE.json'), b0)
        csv_write(path / 'RESOURCE_MOVEMENT.csv', metrics)
        write_json(path / 'COMPARISON.json', {'workload': workload,
            'speedup_B16_over_U_WB16': rows[0]['cycles'] / rows[1]['cycles'],
            'cycle_reduction_percent': (1 - rows[1]['cycles'] / rows[0]['cycles']) * 100,
            'instructions_equal': True, 'same_binary': True,
            'capacity_above_C16_observed': metrics[1]['capacity_above_C16_observed'],
            'interpretation_limit': 'role transfers alone do not establish capacity benefit; compare copy service and strong static redivision before attribution'})
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.campaign.read_text())
    registry = Registry()
    results = []
    for pair in config['pairs']:
        specs = [json.loads(Path(path).read_text()) for path in pair['specs']]
        print('START_PAIR', pair['workload'], flush=True)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(run, spec, registry) for spec in specs]
            actual = [future.result() for future in futures]
        out = publish_pair(pair['workload'], actual, specs, Path(config['result_root']))
        results.append({'workload': pair['workload'], 'directory': str(out),
                        'statuses': [r['status'] for r in actual]})
        write_json(Path(config['result_root']) / 'CAMPAIGN_PROGRESS.json', results)
        print('FINISHED_PAIR', pair['workload'], json.dumps(results[-1]), flush=True)
    print('CAMPAIGN_FINISHED', flush=True)


if __name__ == '__main__':
    main()
