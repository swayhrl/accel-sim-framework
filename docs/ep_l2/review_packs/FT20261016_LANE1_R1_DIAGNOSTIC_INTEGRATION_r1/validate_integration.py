"""Lane 1 R1 integration checks; independent acceptance remains owned by Lane 5."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys

ROOT = Path('/workspace/results/ep_l2_ft20261016/lane1/r1')
CORE = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-r1')
FRAME = Path('/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane1-r1')
BUILD = Path('/workspace/build/ep-l2-ft20261016-lane1-r1')
sys.path.insert(0, '/workspace/worktrees/accel-sim-ep-l2-ft20261016-lane5-v1/util/ep_l2/ft_lane5')
from registry import Registry


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def records(path):
    return [line for line in Path(path).read_text().splitlines()
            if line.startswith(('EPL2FTV1|', 'EPL2B0V1|'))]


def main():
    build_manifest = json.loads((ROOT / 'BUILD_MANIFEST.json').read_text())
    assert build_manifest['status'] == 'PASS'
    for tree, name in [(CORE, 'core'), (FRAME, 'framework')]:
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=tree,
            text=True).strip() == build_manifest[name + '_source_commit']
        assert not subprocess.check_output(['git', 'status', '--porcelain',
            '--untracked-files=no'], cwd=tree)
    assert digest(BUILD / 'accel-sim.out') == build_manifest['binary_sha256']
    resume = '--resume' in sys.argv[1:]
    dest = ROOT / 'integration-tests-r1'
    dest.mkdir(exist_ok=resume)
    bins = ROOT / 'binaries'
    bins.mkdir(exist_ok=resume)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    reg = Registry()
    lease = reg.build_lease('lane1', cpu=1, memory=4 * 1024**3)
    result = {'kind': 'PRODUCER_INTEGRATION_NOT_INDEPENDENT_QUALIFICATION',
              'build_manifest': build_manifest, 'lease_id': lease, 'tests': [],
              'all_ideal_off_equivalence': [], 'mode_legality': []}
    if resume:
        result = json.loads((ROOT / 'INTEGRATION_TEST_RESULTS_FAILED_R1.json').read_text())
        assert len(result['tests']) == 10 and not result['mode_legality']
        assert all(row['exit_code'] == 0 and digest(row['log']) == row['log_sha256']
                   for row in result['tests'])
        result['all_ideal_off_equivalence'] = []
        result['resume_lease_id'] = lease
        result['preserved_harness_diagnostic'] = 'INTEGRATION_TEST_RESULTS_FAILED_R1.json'
    try:
        names = ['accel-sim.out', 'ep_l2_ft_directed', 'ep_l2_ft_partition',
                 'ep_l2_ideal_wb', 'ep_l2_ideal_meta',
                 'ep_l2_ideal_meta_integrated', 'ep_l2_ideal_read_hit']
        for name in names:
            src = BUILD / (name if name == 'accel-sim.out' else 'gpgpu-sim/' + name)
            if not resume:
                shutil.copyfile(src, bins / name)
                (bins / name).chmod(0o555)
            assert digest(src) == digest(bins / name)
        base = str(CORE / 'configs/tested-cfgs/SM7_QV100/gpgpusim.config')
        cfg = lambda name: str(CORE / 'tests/ep_l2' / name)
        read_b16 = dest / 'ideal_read_hit_b16.config'
        read_config = Path(cfg('ideal_read_hit.config')).read_text() + \
                      '\n-gpgpu_ep_l2_ft_mode 1\n-gpgpu_ep_l2_wbuf_entries 16\n'
        if resume:
            assert read_b16.read_text() == read_config
        else:
            read_b16.write_text(read_config)
        cases = [('ft_directed', 'ep_l2_ft_directed', [base, cfg('ft_wbuf.config')]),
                 *[(f'ft_partition_{mode}_{c}', 'ep_l2_ft_partition',
                    [base, cfg('ft_wbuf.config'), str(mode), str(c)])
                   for mode in (1, 2) for c in (8, 16)],
                 ('ideal_wb', 'ep_l2_ideal_wb', [base, cfg('ft_wbuf.config')]),
                 ('ideal_meta', 'ep_l2_ideal_meta', []),
                 ('ideal_meta_integrated', 'ep_l2_ideal_meta_integrated',
                    [base, cfg('ideal_meta_integrated.config')]),
                 ('ideal_read_hit', 'ep_l2_ideal_read_hit', [base, cfg('ideal_read_hit.config')]),
                 ('ideal_read_hit_b16', 'ep_l2_ideal_read_hit', [base, str(read_b16)])]
        env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
        for name, binary, args in cases:
            if resume:
                row = next(r for r in result['tests'] if r['test'] == name)
                assert digest(bins / binary) == row['binary_sha256']
                assert all(digest(p) == h for p, h in row['config_sha256'].items())
                continue
            log = dest / (name + '.log')
            command = [str(bins / binary), *args]
            with log.open('w') as stream:
                run = subprocess.run(command, cwd=dest, env=env, stdout=stream,
                                     stderr=subprocess.STDOUT, timeout=180)
            row = {'test': name, 'command': command, 'exit_code': run.returncode,
                   'binary_sha256': digest(bins / binary), 'log': str(log),
                   'log_sha256': digest(log), 'config_sha256':
                   {p: digest(p) for p in args if Path(p).is_file()}}
            result['tests'].append(row)
            print(name, run.returncode, flush=True)
            assert run.returncode == 0, name

        old_root = ROOT.parent
        matches = [('ft_directed', old_root / 'immutable-directed-r1.log'),
                   *[(f'ft_partition_{m}_{c}', old_root / f'immutable-partition-{m}-{c}-r1.log')
                     for m in (1, 2) for c in (8, 16)]]
        for name, old_log in matches:
            new_log = dest / (name + '.log')
            old, new = records(old_log), records(new_log)
            row = {'test': name, 'r0_log': str(old_log), 'r0_log_sha256': digest(old_log),
                   'r1_log': str(new_log), 'r1_log_sha256': digest(new_log),
                   'native_ft_b0_record_count': len(old), 'native_records_equal': old == new,
                   'comparison': 'FULL_STDOUT_STDERR_BYTE_EQUALITY',
                   'exact': old_log.read_bytes() == new_log.read_bytes()}
            result['all_ideal_off_equivalence'].append(row)
            assert row['exact'], (name, 'R1 ideal-OFF production fixture output changed')

        illegal = {
            'wb_without_finite': '-gpgpu_ep_l2_ft_mode 0\n-gpgpu_ep_l2_wbuf_entries 0\n-gpgpu_ep_l2_ideal_wb 1\n',
            'wb_on_unified': '-gpgpu_ep_l2_ft_mode 2\n-gpgpu_ep_l2_ideal_wb 1\n',
            'read_plus_meta': '-gpgpu_ep_l2_ideal_read_hit 1\n-gpgpu_ep_l2_ideal_meta 1\n',
            'read_plus_wb': '-gpgpu_ep_l2_ideal_read_hit 1\n-gpgpu_ep_l2_ideal_wb 1\n',
            'read_on_unified': '-gpgpu_ep_l2_ft_mode 2\n-gpgpu_ep_l2_ideal_read_hit 1\n',
            'meta_without_descriptors': '-gpgpu_ep_l2_descriptor_pool_size 0\n-gpgpu_ep_l2_descriptor_per_line_cap 0\n-gpgpu_ep_l2_ideal_meta 1\n'}
        trace = '/workspace/worktrees/accel-sim-decoupled-l2/hw_run/decoupled-l2-pretraces/cudasdk/9.1/vectorAdd/__size_4000000/traces/kernelslist.g'
        for name, text in illegal.items():
            overlay = dest / (name + '.config')
            overlay.write_text(text)
            configs = [base, str(FRAME / 'gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config'),
                       str(FRAME / 'tests/ep_l2/b0_banked_d512_850.config'),
                       str(FRAME / 'tests/ep_l2/m0a_off.config'),
                       str(FRAME / 'tests/ep_l2/ft20261016/b16_banked.config'),
                       str(FRAME / 'tests/ep_l2/ft20261016/r1/off.config'), str(overlay)]
            command = [str(bins / 'accel-sim.out')]
            for config in configs:
                command += ['-config', config]
            command += ['-trace', trace]
            log = dest / (name + '.log')
            with log.open('w') as stream:
                run = subprocess.run(command, cwd=dest, env=env, stdout=stream,
                                     stderr=subprocess.STDOUT, timeout=30)
            guard = ('EP-L2 ideal mode requires target metadata/banked model'
                     if name in ('read_plus_meta', 'meta_without_descriptors')
                     else 'I_WB requires static finite-WBUF source')
            row = {'test': name, 'command': command, 'exit_code': run.returncode,
                   'guard_message': guard, 'log': str(log), 'log_sha256': digest(log),
                   'ordered_config_sha256': [digest(p) for p in configs],
                   'trace_list_sha256': digest(trace),
                   'trace_scope': 'CLI_GUARD_PRE_WORKLOAD_INITIALIZATION_NO_KERNEL_EXECUTION'}
            result['mode_legality'].append(row)
            assert run.returncode == -6 and guard in log.read_text(), name
            print(name, 'EXPECTED_REJECTION', flush=True)
        result['status'] = 'PASS'
    finally:
        reg.release_build(lease, 'lane1')
        (ROOT / 'INTEGRATION_TEST_RESULTS.json').write_text(json.dumps(result, indent=2) + '\n')
        print(result.get('status', 'FAILED'), flush=True)


if __name__ == '__main__':
    main()
