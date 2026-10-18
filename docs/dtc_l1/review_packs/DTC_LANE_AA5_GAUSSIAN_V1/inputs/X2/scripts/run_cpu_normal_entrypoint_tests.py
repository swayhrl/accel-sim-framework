"""CPU normal-print qualification only. Never invokes accel-sim or a workload."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from parse_normal_export import BEGIN, END, ROW, SENTINEL, parse_normal_export


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def boundaries(text):
    result = []
    current = None
    for line in text.splitlines():
        if line.startswith('X2_CPU_NORMAL_BOUNDARY_BEGIN '):
            assert current is None
            current = []
        elif line.startswith('X2_CPU_NORMAL_BOUNDARY_END '):
            assert current is not None
            result.append('\n'.join(current) + '\n')
            current = None
        elif current is not None:
            current.append(line)
    assert current is None and len(result) == 3
    return result


def public_output(body):
    # Drop only the new, explicitly framed K1 export, preserving every old line.
    lines, inside = [], False
    for line in body.splitlines():
        if line.startswith(BEGIN):
            assert not inside
            inside = True
        elif line.startswith(END):
            assert inside
            inside = False
        elif not inside:
            lines.append(line)
    assert not inside
    return '\n'.join(lines) + '\n'


def negative_tests(body, multi_text):
    lines = body.splitlines()
    row_indices = [i for i, line in enumerate(lines) if line.startswith(ROW)]
    assert len(row_indices) == 64
    def text(parts):
        return '\n'.join(parts) + '\n'
    corrupt = {
        'missing_sm': text([line for i, line in enumerate(lines) if i != row_indices[4]]),
        'duplicate_sm': text(lines[:row_indices[4]] + [lines[row_indices[4]]] + lines[row_indices[4]:]),
        'truncated_snapshot': text([line for line in lines if not line.startswith(END)]),
        'truncated_row': body.replace(lines[row_indices[4]], lines[row_indices[4]][:-9]),
        'missing_field': body.replace('sm=4 requests=0 ', 'sm=4 '),
        'duplicate_field': body.replace('sm=4 requests=0 ', 'sm=4 requests=0 requests=0 '),
        'bad_no_event_sentinel': body.replace('sm=4 requests=0 ', 'sm=4 requests=0 ').replace(
            lines[row_indices[4]], lines[row_indices[4]].replace('first_request_cycle=' + str(SENTINEL), 'first_request_cycle=0')),
        'out_of_range_sm': body.replace('sm=4 requests=0 ', 'sm=64 requests=0 '),
        'source_counter_mismatch': body.replace('sm=0 requests=4 ', 'sm=0 requests=5 '),
        'wrong_end_cycle': body.replace(END + ' version=1 sms=64 cycle=22', END + ' version=1 sms=64 cycle=23'),
        'unframed_private_summary': text([lines[row_indices[0]]]),
        'missing_export': 'gpu_sim_cycle = 22\n',
        'truncated_last_frame_no_fallback': multi_text.rsplit(END, 1)[0],
        'missing_final_newline': body.rstrip('\n'),
    }
    checks = []
    for name, candidate in corrupt.items():
        assert candidate != body, name
        try:
            parse_normal_export(candidate, k1=True)
        except ValueError as error:
            checks.append({'case': name, 'status': 'REJECTED_AS_REQUIRED', 'reason': str(error)})
        else:
            raise AssertionError('corrupt normal export accepted: ' + name)
    try:
        parse_normal_export(body, k1=False)
    except ValueError as error:
        checks.append({'case': 'K0_unexpected_export', 'status': 'REJECTED_AS_REQUIRED', 'reason': str(error)})
    else:
        raise AssertionError('K0 unexpected summary was accepted')
    return checks


def main():
    ap = argparse.ArgumentParser()
    for key in ('new_probe', 'base_probe', 'new_library', 'base_library', 'config', 'raw'):
        ap.add_argument('--' + key.replace('_', '-'), required=True, type=Path)
    args = ap.parse_args()
    args.raw.mkdir(parents=True, exist_ok=False)
    inputs = {key: {'path': str(getattr(args, key).resolve()), 'sha256': sha(getattr(args, key))}
              for key in ('new_probe', 'base_probe', 'new_library', 'base_library', 'config')}
    cases = [('omitted', 'events', '1'), ('0', 'events', '1'), ('1', 'no_event', '1'),
             ('1', 'events', '1'), ('1', 'events', '8')]
    receipts, outputs = [], {}
    for build in ('new', 'base'):
        probe, library = getattr(args, build + '_probe'), getattr(args, build + '_library')
        for flag, scenario, topology in cases:
            label = '_'.join((build, flag, scenario, topology))
            work = args.raw / label
            work.mkdir()
            env = dict(os.environ)
            env.pop('LD_PRELOAD', None)
            env['LD_LIBRARY_PATH'] = str(library.parent.resolve())
            env['CUDA_VISIBLE_DEVICES'] = ''
            argv = [str(probe.resolve()), str(args.config.resolve()), flag, scenario, topology]
            with (work / 'stdout').open('w') as out, (work / 'stderr').open('w') as err:
                proc = subprocess.run(argv, cwd=work, env=env, stdout=out, stderr=err, timeout=60)
            assert proc.returncode == 0, (label, proc.returncode, (work / 'stderr').read_text()[-2000:])
            data = (work / 'stdout').read_text()
            assert re.findall(r'^X2_CPU_LOADED_LIBRARY path=(.*)$', data, re.M) == [str(library.resolve())]
            assert re.findall(r'^X2_CPU_LOADED_ELF path=(.*)$', data, re.M) == [str(probe.resolve())]
            mappings = [line for line in data.splitlines() if line.startswith('X2_CPU_LIBRARY_MAP ')]
            assert mappings and all(str(library.resolve()) in line for line in mappings)
            assert 'X2_CPU_COMPONENT_RESULT boundaries=3 sms=64 kernels=0 gpu_cycle_calls=0 simulation_threads_started=0 print_state_unchanged=1' in data
            assert not re.search(r'^DTC_INVALIDATE_V1 sm=', data, re.M) # fixed debuglimit0
            body = boundaries(data)
            outputs[(build, flag, scenario, topology)] = body
            if build == 'new':
                parsed = parse_normal_export(data, k1=flag == '1')
                if flag == '1':
                    assert parsed['snapshots'] == 3 and parsed['cycle'] == 22
                    individual = [parse_normal_export(part, k1=True) for part in body]
                    assert [part['cycle'] for part in individual] == [0, 13, 22]
                    for part, cycle in zip(body, (0, 13, 22)):
                        assert 'gpu_sim_cycle = ' + str(cycle) + '\n' in part
                    for row in individual[0]['rows']:
                        assert row['requests'] == row['ordinary_commits'] == 0
                        assert row['first_request_cycle'] == row['first_ordinary_commit_cycle'] == SENTINEL
                    if scenario == 'events':
                        mid, final = individual[1]['rows'][0], parsed['rows'][0]
                        assert mid['requests'] == 3 and mid['ordinary_commits'] == 0
                        assert mid['pending_first_request'] == 1 and mid['pending_last_request'] == 3
                        assert mid['first_ordinary_commit_cycle'] == SENTINEL
                        assert final['requests'] == 4 and final['idle'] == 3 and final['membar'] == 1
                        assert final['ordinary_commits'] == 2
                        assert final['changed'] == 2 and final['retained_at_event'] == final['reclaimed_at_event'] == 1
                        assert final['first_request_cycle'] == 10 and final['last_request_cycle'] == 22
                        assert final['first_ordinary_commit_cycle'] == 21 and final['last_ordinary_commit_cycle'] == 22
                        assert final['requests'] != mid['requests'] + final['requests'] # no cumulative-snapshot sum
                        assert parsed['rows'][63]['config'] == parsed['rows'][63]['requests'] == 1
                        assert all(row['requests'] == 0 for row in parsed['rows'][1:63])
                    else:
                        assert all(row['requests'] == row['ordinary_commits'] == 0 for row in parsed['rows'])
                else:
                    assert not parsed['available'] and 'rows' not in parsed # unavailable is not measured zero
            else:
                try:
                    parse_normal_export(data, k1=flag == '1')
                except ValueError as error:
                    assert flag == '1' and str(error) == 'K1 normal export missing'
                else:
                    assert flag != '1'
            receipts.append({'case': label, 'argv': argv, 'returncode': proc.returncode,
                             'stdout_sha256': sha(work / 'stdout'), 'stderr_sha256': sha(work / 'stderr'),
                             'loaded_library': str(library.resolve()), 'loaded_library_sha256': sha(library),
                             'probe_sha256': sha(probe), 'actual_process_library_maps': mappings,
                             'normal_boundary_count': 3, 'full_or_canary_simulator': False})
    comparisons = []
    for flag, scenario, topology in cases:
        a, b = outputs[('new', flag, scenario, topology)], outputs[('base', flag, scenario, topology)]
        for boundary, (left, right) in enumerate(zip(a, b)):
            assert public_output(left) == right, ('public-output-changed', flag, scenario, topology, boundary)
            comparisons.append({'flag': flag, 'scenario': scenario, 'cores_per_cluster': topology,
                                'boundary': boundary, 'status': 'OLD_PUBLIC_OUTPUT_BYTE_IDENTICAL',
                                'sha256': hashlib.sha256(right.encode()).hexdigest()})
    assert outputs[('new', 'omitted', 'events', '1')] == outputs[('new', '0', 'events', '1')]
    corruption = negative_tests(outputs[('new', '1', 'events', '1')][-1],
                                ''.join(outputs[('new', '1', 'events', '1')]))
    for key, item in inputs.items():
        assert sha(Path(item['path'])) == item['sha256'], 'identity changed during CPU tests: ' + key
    result = {'status': 'PASS_CPU_REAL_NORMAL_ENTRYPOINT_EXPORT_SCOPE_ONLY',
              'entrypoint': 'actual compiled gpgpu_sim::gpu_print_stat(0)',
              'private_observer_print_called_by_test': False,
              'inputs_before_after_identical': inputs, 'processes': receipts,
              'public_output_comparisons': comparisons, 'negative_parser_checks': corruption,
              'K0_omitted_equals_zero': True, 'snapshots_per_K1_process': 3,
              'unique_sms_per_snapshot': 64, 'last_complete_snapshot_not_sum': True,
              'debug_event_limit': 0, 'runtime_stat': '500000',
              'baseline_K1_normal_export_absent_confirmed': True,
              'full_simulators_started': 0, 'canary_simulators_started': 0,
              'GPU_cycle_calls': 0, 'simulation_threads_started': 0,
              'scope_limit': 'CPU prepared metadata and passive timestamps; no workload, payload/ISA validation or performance result; accepts existing Y2 bounded scope unchanged'}
    (args.raw / 'CPU_NORMAL_ENTRYPOINT_TESTS.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'processes': len(receipts),
                      'unchanged_public_boundaries': len(comparisons),
                      'negative_parser_checks': len(corruption)}, indent=2))


if __name__ == '__main__':
    main()
