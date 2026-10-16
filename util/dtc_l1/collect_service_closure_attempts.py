#!/usr/bin/env python3
"""Collect immutable terminal receipts, retaining failed and live attempts."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def collect(run):
    start = json.loads((run / 'RUN_START.json').read_text())
    spec = start['spec']
    row = dict(label=spec['label'], attempt_uuid=start['attempt_uuid'], run_dir=str(run),
               classification=spec['classification'], core=spec['core'],
               binary_sha256=spec['runtime_sha256'], identity=start['identity'],
               status='RUNNING', terminal_sha256='', stdout_sha256='', stderr_sha256='',
               cycles='', instructions='', scientific_checks='NOT_TERMINAL',
               service_metrics='UNAVAILABLE', max_rss_kb='', elapsed_wall='')
    terminal = run / 'RUN_TERMINAL.json'
    if not terminal.exists():
        return row
    end = json.loads(terminal.read_text())
    text = (run / 'simulator.stdout').read_text(errors='replace')
    stderr = (run / 'simulator.stderr').read_text(errors='replace')
    metrics = dict(re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$', text, re.M))
    row.update(terminal_sha256=sha(terminal), stdout_sha256=end['stdout_sha256'],
               stderr_sha256=end['stderr_sha256'], cycles=metrics.get('gpu_tot_sim_cycle', ''),
               instructions=metrics.get('gpu_tot_sim_insn', ''))
    checks = dict(natural_exit=end['exit_status'] == 0,
                  stdout_hash=sha(run / 'simulator.stdout') == end['stdout_sha256'],
                  stderr_hash=sha(run / 'simulator.stderr') == end['stderr_sha256'],
                  full_instructions=row['instructions'] == str(spec['expected_instructions']),
                  no_crash=not any(s in stderr for s in ['Assertion', '=== CRASH:', 'Segmentation fault']))
    checks['spec_identity'] = hashlib.sha256(json.dumps(spec,sort_keys=True).encode()).hexdigest() == start['identity']
    checks['runner_identity'] = sha(run/'immutable_runner.py') == start['runner_sha256']
    checks['runtime_identity'] = sha(run.parent/'binaries'/spec['runtime_sha256']/'accel-sim.out') == spec['runtime_sha256']
    checks['config_snapshots'] = all(sha(run/f'config-{i}.config') == c['sha256'] for i,c in enumerate(spec['configs']))
    checks['resource_identity'] = sha(run/'resource.time') == end['resource_sha256']
    checks['single_epoch'] = (text.count('GPGPU-Sim uArch: performance model initialization complete.') == 1 and
                              text.count('GPGPU-Sim: *** exit detected ***') == 1)
    checks['complete_kernels'] = len(re.findall(r'^kernel_name\s*=',text,re.M)) == len(spec['members'])
    checks['no_limits_or_deadlock'] = not any(s in text for s in ['break due to reaching the maximum', 'DEADLOCK detected'])
    finite = spec.get('finite_service', any('FINITE_SERVICE_ON' in c['path'] for c in spec['configs']))
    if finite and checks['natural_exit']:
        service = {k: int(v) for k, v in metrics.items() if k.startswith('DTC_SERVICE_V1_')}
        row['service_metrics'] = json.dumps(service, sort_keys=True)
        prefix = 'DTC_SERVICE_V1_'
        checks['service_complete'] = len(service) == 11
        if checks['service_complete']:
            checks['residence_decomposition'] = (service[prefix+'fully_ready_to_complete_sum'] ==
                sum(service[prefix+s] for s in ['ready_to_collect_sum','collection_cycles','wb_wait']))
            checks['service_activity'] = service[prefix+'retired'] > 0 and service[prefix+'samples'] > 0
        mode = spec.get('dtc_mode', 'io' if '_IO_' in spec['label'] else 'oo').lower()
        def n(name):
            return int(metrics.get('DTC_L1_'+name, '-1'))
        checks['lower_balance'] = (n(mode+'_lower_created') == n(mode+'_lower_issued') == n(mode+'_lower_responses') > 0)
        checks['pib_drained'] = n(mode+'_pib_occupancy') == 0
        checks['lower_drained'] = n('lower_outstanding') == 0
        checks['inflight_drained'] = n(mode+'_inflight_current') == 0
        checks['credit_balance'] = n('lower_credit_acquired') == n('lower_credit_released') == n(mode+'_lower_created')
        checks['dependency_balance'] = n(mode+'_completion_dependency_count') == n(mode+'_completion_dependency_closed') > 0
        observed = sum(n('m4_'+s+'_admits') for s in ['store','atomic','bypass_load','proxy_fence'])
        checks['ordinary_completion_balance'] = observed == n('m4_source_completions') == n('m4_observation_retires')
        if checks.get('service_complete'):
            def option(name):
                values=re.findall(r'^-'+name+r'\s+(\d+)\s',text,re.M)
                return int(values[-1]) if values else -1
            cores=option('gpgpu_n_clusters')*option('gpgpu_n_cores_per_cluster')
            checks['samples_cover_all_cores'] = service[prefix+'samples'] == cores*int(row['cycles']) and cores>0
            checks['service_retire_balance'] = service[prefix+'retired']+observed == n(mode+'_retire_count')
        if mode == 'oo':
            checks['refs_drained'] = n('oo_active_refs') == 0
            checks['physical_balance'] = n('oo_new_misses')-n('oo_immediate_reclaims')-n('oo_final_ref_reclaims') == n('oo_physical_allocated')
        else:
            checks['physical_balance'] = n('io_physical_allocations')-n('io_physical_releases') == n('io_physical_allocated_current')
            checks['partial_drained'] = n('io_partial_entries_current') == n('io_partial_lines_held_current') == 0
            checks['response_identity'] = n('io_inflight_identity_mismatch') == 0
        checks['flag_echo'] = bool(re.search(r'^-gpgpu_dtc_l1_finite_service\s+1\s', text, re.M))
        checks['mode_echo'] = ('DTC_L1_mode = PAPER_' + mode.upper()) in text
    if checks['natural_exit'] and 'expected_dl1' in spec:
        checks['dl1_echo'] = bool(re.search(r'^-gpgpu_cache:dl1\s+' + re.escape(spec['expected_dl1']) + r'\s', text, re.M))
        checks['mshr_effective'] = metrics.get('DTC_L1_baseline_mshr_entries') == str(spec['expected_mshr'])
        checks['pib_echo'] = bool(re.search(r'^-gpgpu_dtc_l1_pib_entries\s+' + str(spec['expected_pib']) + r'\s', text, re.M))
        checks['pib_drained'] = metrics.get('DTC_L1_pib_occupancy') == '0'
    row['scientific_checks'] = json.dumps(checks, sort_keys=True)
    row['status'] = 'PASS_CHECKED_SCOPE' if all(checks.values()) else 'FAIL_PRESERVED'
    resource = (run / 'resource.time').read_text(errors='replace')
    for key, pattern in [('max_rss_kb', r'Maximum resident set size \(kbytes\):\s*(\d+)'),
                         ('elapsed_wall', r'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(\S+)')]:
        match = re.search(pattern, resource)
        if match:
            row[key] = match.group(1)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', action='append', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    data = [collect(p.parent) for root in args.root for p in sorted(Path(root).glob('*/RUN_START.json'))]
    assert data
    with Path(args.output).open('x') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(data)
    print(json.dumps({s: sum(r['status'] == s for r in data) for s in sorted({r['status'] for r in data})}))


if __name__ == '__main__':
    main()
