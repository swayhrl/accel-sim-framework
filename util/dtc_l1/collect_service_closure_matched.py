#!/usr/bin/env python3
"""Join only the preregistered complete IO128/OO128 mechanism pairs."""
import argparse
import csv
import json
from pathlib import Path
import re
import shlex
from collect_service_closure_attempts import collect, sha

PLAN_SHA = '281b2d22ace3bbf105711473516f075fc11c495a1d6c214d9f4a3e42414892e1'


def effective_options(spec, run=None):
    result = {}
    for i, config in enumerate(spec['configs']):
        path = run/f'config-{i}.config' if run else Path(config['path'])
        assert sha(path) == config['sha256']
        # DRAM timing strings span quoted lines in the original config.
        key = None
        for token in shlex.split(path.read_text(), comments=True):
            if re.match(r'^-[A-Za-z_]', token):
                key = token
                result[key] = []
            else:
                assert key is not None
                result[key].append(token)
    return result


def contract_checks(io, oo, ci, co):
    diffs = {k for k in ci.keys() | co.keys() if ci.get(k) != co.get(k)}
    # The IO-only depth is inactive on the OO path. Preserve and expose that
    # literal difference; do not call this total metadata/area equivalence.
    checks = {'only_declared_config_differences': diffs <= {
        '-gpgpu_dtc_l1_mode', '-gpgpu_dtc_l1_io_pib_entries'}}
    for field in ['workload', 'core', 'build_framework', 'runtime_sha256',
                  'trace_list_sha256', 'expected_instructions', 'members']:
        checks['same_'+field] = io[field] == oo[field]
    checks['same_trace_list_path'] = io['trace_list'] == oo['trace_list']
    checks['finite_spec'] = io['finite_service'] is True and oo['finite_service'] is True
    checks['declared_modes'] = io['dtc_mode'] == 'io' and oo['dtc_mode'] == 'oo'
    checks['io_active_depth128'] = ci.get('-gpgpu_dtc_l1_io_pib_entries') == ['128']
    checks['oo_active_depth128'] = co.get('-gpgpu_dtc_l1_oo_pib_entries') == ['128']
    for arm, config, mode in [('io', ci, '2'), ('oo', co, '3')]:
        checks[arm+'_mode'] = config.get('-gpgpu_dtc_l1_mode') == [mode]
        checks[arm+'_finite_enabled'] = config.get('-gpgpu_dtc_l1_finite_service') == ['1']
        checks[arm+'_pool640'] = config.get('-gpgpu_dtc_l1_physical_lines') == ['640']
        checks[arm+'_logical128'] = (config.get('-gpgpu_dtc_l1_logical_sets') == ['32'] and
                                   config.get('-gpgpu_dtc_l1_logical_ways') == ['4'])
    return checks


def table(path, rows):
    with path.open('x') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True)
    ap.add_argument('--root', required=True)
    ap.add_argument('--output-dir', required=True)
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    assert sha(Path(a.plan)) == PLAN_SHA
    plan = list(csv.DictReader(Path(a.plan).open(), delimiter='\t'))
    specs = {}
    for row in plan:
        assert sha(Path(row['spec_path'])) == row['spec_sha256']
        specs[row['label']] = json.loads(Path(row['spec_path']).read_text())
    controls = [r for r in plan if r['arm'] == 'IO128']
    assert {r['workload'] for r in controls} == {'BICG', 'Btree', '2DConvolution', 'Hotspot1'}
    starts = {}
    for p in root.glob('*/RUN_START.json'):
        s = json.loads(p.read_text())
        label = s['spec']['label']
        if label in specs:
            assert label not in starts, 'Duplicate current registered label'
            assert s['spec'] == specs[label]
            starts[label] = p.parent
    hold = root/'ROW_ADMISSION_HOLDS.json'
    held = set(json.loads(hold.read_text())['held_labels']) if hold.exists() else set()
    gates, metrics, audits = [], [], []
    for control in controls:
        peer = next(r for r in plan if r['arm'] == 'OO' and r['workload'] == control['workload'])
        assert control['phase'] == 'CONTROL' and peer['phase'] == 'PILOT'
        io, oo = specs[control['label']], specs[peer['label']]
        runs = [starts.get(control['label']), starts.get(peer['label'])]
        configs = [effective_options(s, r) for s, r in zip([io, oo], runs)]
        checks = contract_checks(io, oo, *configs)
        rows = [collect(r) if r else None for r in runs]
        status = 'PENDING_COMPLETE_PAIR'
        if control['label'] in held or peer['label'] in held:
            status = 'ADMISSION_HOLD'
        elif not all(checks.values()):
            status = 'PAIR_CONTRACT_HOLD'
        elif all(r and r['status'] != 'RUNNING' for r in rows):
            checks['both_strict_pass'] = all(r['status'] == 'PASS_CHECKED_SCOPE' for r in rows)
            checks['same_complete_instructions'] = rows[0]['instructions'] == rows[1]['instructions']
            if checks['both_strict_pass']:
                service = [json.loads(r['service_metrics']) for r in rows]
                for field in ['retired', 'collected_sectors']:
                    key = 'DTC_SERVICE_V1_'+field
                    checks['same_'+field] = service[0][key] == service[1][key] > 0
                for index, (run, mode, depth_option) in enumerate(zip(runs, ['2', '3'],
                        ['-gpgpu_dtc_l1_io_pib_entries', '-gpgpu_dtc_l1_oo_pib_entries'])):
                    text = (run/'simulator.stdout').read_text()
                    def echo(option):
                        values = re.findall(r'^'+re.escape(option)+r'\s+(\d+)\s', text, re.M)
                        return int(values[-1]) if values else None
                    checks[f'arm{index}_active_depth_echo128'] = echo(depth_option) == 128
                    checks[f'arm{index}_mode_echo'] = echo('-gpgpu_dtc_l1_mode') == int(mode)
                    checks[f'arm{index}_pool_echo640'] = echo('-gpgpu_dtc_l1_physical_lines') == 640
                if all(checks.values()):
                    status = 'PASS_MATCHED128_SCOPE'
                    for arm, row, s in zip(['IO128', 'OO128'], rows, service):
                        v = lambda name: s['DTC_SERVICE_V1_'+name]
                        metrics.append(dict(workload=control['workload'], arm=arm,
                            attempt_uuid=row['attempt_uuid'], core=row['core'],
                            binary_sha256=row['binary_sha256'], instructions=row['instructions'],
                            cycles=row['cycles'], active_pib_entries=128, physical_lines=640,
                            retired=v('retired'), all_sm_core_cycle_samples=v('samples'),
                            mean_ready_to_complete=v('fully_ready_to_complete_sum')/v('retired'),
                            mean_ready_to_collect=v('ready_to_collect_sum')/v('retired'),
                            mean_collection=v('collection_cycles')/v('retired'),
                            mean_post_collection_wb_wait=v('wb_wait')/v('retired'),
                            mean_map_loss_to_free=v('map_loss_to_free_sum')/v('map_loss_to_free_count') if v('map_loss_to_free_count') else 'NA_NO_EVENTS',
                            mean_pib_entries_per_sm=v('pib_integral')/v('samples'),
                            mean_physical_lines_per_sm=v('physical_integral')/v('samples'),
                            raw_service_metrics=json.dumps(s, sort_keys=True),
                            scope='COMPLETE_MATCHED_ACTIVE_DEPTH_NOT_EQUAL_AREA_OR_NATIVE_DTC'))
            if status != 'PASS_MATCHED128_SCOPE':
                status = 'PAIR_VALIDATION_HOLD'
        gates.append(dict(workload=control['workload'], status=status,
            io_label=control['label'], oo_label=peer['label'],
            io_spec_sha256=control['spec_sha256'], oo_spec_sha256=peer['spec_sha256'],
            io_attempt_uuid=rows[0]['attempt_uuid'] if rows[0] else '',
            oo_attempt_uuid=rows[1]['attempt_uuid'] if rows[1] else '',
            io_status=rows[0]['status'] if rows[0] else 'NOT_STARTED',
            oo_status=rows[1]['status'] if rows[1] else 'NOT_STARTED'))
        diffs = {k: [configs[0].get(k), configs[1].get(k)] for k in configs[0].keys() | configs[1].keys()
                 if configs[0].get(k) != configs[1].get(k)}
        audits.append(dict(workload=control['workload'], status=status, checks=checks,
                           literal_effective_config_differences=diffs))
    table(out/'MATCHED128_GATES.tsv', gates)
    if metrics:
        table(out/'MATCHED128_METRICS.tsv', metrics)
    (out/'MATCHED128_AUDIT.json').write_text(json.dumps(dict(plan_sha256=PLAN_SHA,
        collector_sha256=sha(Path(__file__)), strict_collector_sha256=sha(Path(__file__).with_name('collect_service_closure_attempts.py')),
        audits=audits, averages='NONE', scope='FOUR_FIXED_PILOTS_ONLY'), indent=2, sort_keys=True)+'\n')
    assert not any(r['status'] in {'PAIR_CONTRACT_HOLD', 'PAIR_VALIDATION_HOLD'} for r in gates)
    print(json.dumps({r['workload']: r['status'] for r in gates}))


if __name__ == '__main__':
    main()
