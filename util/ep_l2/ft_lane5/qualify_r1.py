"""Independent replay of a frozen R1 producer candidate; never rebuild it."""
import argparse
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess

from registry import Registry, write_json
from run import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', required=True, type=Path)
    args = parser.parse_args()
    root = args.stage
    contract = json.loads((root / 'R1_DIAGNOSTIC_CONTRACT_V1.json').read_text())
    producer = json.loads((root / 'INTEGRATION_TEST_RESULTS.json').read_text())
    assert contract['status'] == 'PRODUCER_INTEGRATION_READY_FOR_INDEPENDENT_VALIDATION'
    assert digest(contract['binary']) == contract['binary_sha256']
    out = root / 'independent'
    out.mkdir(exist_ok=False)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    registry = Registry()
    lease = registry.build_lease('lane5', cpu=1, memory=4 * 1024**3)
    report = {'status': 'INCOMPLETE', 'kind': 'INDEPENDENT_PRODUCTION_DRIVEN_R1_INCREMENTAL',
              'lease_id': lease, 'contract_sha256': digest(root / 'R1_DIAGNOSTIC_CONTRACT_V1.json'),
              'tests': [], 'all_off_incremental_equivalence': [], 'illegal_modes': [],
              'application_equivalence': 'PENDING_SEPARATE_R1_BASELINES_NO_R0_RELAUNCH'}
    env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
    try:
        for group, field in [('tests', 'tests'), ('mode_legality', 'illegal_modes')]:
            for row in producer[group]:
                source = Path(row['command'][0])
                expected_binary = row.get('binary_sha256', contract['binary_sha256'])
                assert digest(source) == expected_binary
                target = out / source.name
                if target.exists():
                    assert digest(target) == expected_binary
                else:
                    shutil.copyfile(source, target)
                    target.chmod(0o555)
                command = [str(target)]
                assets = []
                for index, value in enumerate(row['command'][1:]):
                    path = Path(value)
                    if path.is_file():
                        # Trace guard reads only kernelslist.g; retain its original
                        # location, avoiding a false assertion of kernel execution.
                        if value.endswith('kernelslist.g'):
                            assert digest(path) == row['trace_list_sha256']
                            command.append(value)
                        else:
                            copy = out / (row['test'] + '-arg-' + str(index) + path.suffix)
                            shutil.copyfile(path, copy)
                            command.append(str(copy))
                        assets.append({'source': str(path), 'sha256': digest(path)})
                    else:
                        command.append(value)
                original_hashes = row.get('config_sha256')
                if original_hashes is not None:
                    assert all(digest(p) == h for p, h in original_hashes.items())
                if 'ordered_config_sha256' in row:
                    assert [a['sha256'] for a in assets[:-1]] == row['ordered_config_sha256']
                log = out / (row['test'] + '.log')
                with log.open('x') as stream:
                    execution = subprocess.run(command, cwd=out, env=env, stdout=stream,
                        stderr=subprocess.STDOUT, timeout=180)
                text = log.read_text()
                item = {'test': row['test'], 'command': command, 'assets': assets,
                        'binary_sha256': expected_binary, 'exit_code': execution.returncode,
                        'log': str(log), 'log_sha256': digest(log)}
                report[field].append(item)
                if field == 'tests':
                    assert execution.returncode == 0 and 'PASS' in text, row['test']
                    # Independent execution is additionally checked against frozen
                    # producer stdout, rather than accepting its PASS label alone.
                    item['producer_log_exact'] = digest(log) == row['log_sha256']
                    assert item['producer_log_exact'], row['test']
                else:
                    assert execution.returncode == -6 and row['guard_message'] in text, row['test']
                    item['scope'] = 'PRE_WORKLOAD_CLI_REJECTION_NO_KERNEL_EXECUTION'
                print(row['test'], 'PASS', flush=True)
        for row in producer['all_ideal_off_equivalence']:
            old = Path(row['r0_log'])
            assert digest(old) == row['r0_log_sha256']
            new = out / (row['test'] + '.log')
            exact = old.read_bytes() == new.read_bytes()
            report['all_off_incremental_equivalence'].append({'test': row['test'],
                'r0_log_sha256': digest(old), 'r1_log_sha256': digest(new), 'byte_equal': exact})
            assert exact
        assert digest(contract['binary']) == contract['binary_sha256']
        report['status'] = 'PASS'
    finally:
        registry.release_build(lease, 'lane5')
        write_json(root / 'INDEPENDENT_R1_TESTS.json', report)
    print(report['status'], flush=True)


if __name__ == '__main__':
    main()
