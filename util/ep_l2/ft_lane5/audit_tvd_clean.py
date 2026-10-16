"""Independently replay only Lane2's frozen clean production checkpoint."""
import argparse
import os
from pathlib import Path
import resource
import shutil
import subprocess
from registry import Registry, write_json
from run import digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    out = args.out
    out.mkdir(exist_ok=False)
    binary = Path('/workspace/results/ep_l2_ft20261016/lane2/review_r2_clean_production/clean-8ae60ff1.out')
    assert digest(binary) == '4320583bedff41aa7122f2ad64c919882f84538f82e175a7eba4ff8d7a125bfa'
    core = Path('/workspace/worktrees/gpgpu-sim-ep-l2-ft20261016-lane1-v1')
    source = '8ae60ff11ad847f28013df2873a5b7a8df7085b4'
    stimulus = subprocess.check_output(['git', 'show', source + ':tests/ep_l2/test_tvd_production.cc'], cwd=core)
    (out / 'test_tvd_production.cc').write_bytes(stimulus)
    assert digest(out / 'test_tvd_production.cc') == '9b9cf52f025e94335c8e7195b5dec8dad155bcb76784e90380cbb20cb64bf7db'
    configs = []
    for name, expected in [('configs/tested-cfgs/SM7_QV100/gpgpusim.config', '8ccad878b6abfec8254ecd6c7e0efee2714908dc3a04f611ff8787000e277bd3'),
                           ('tests/ep_l2/ft_wbuf.config', 'b8748fe67aafc617eacb11e04f296990f1c88e5b51bdd24295466ab85c9e9372')]:
        path = out / Path(name).name
        path.write_bytes(subprocess.check_output(['git', 'show', source + ':' + name], cwd=core))
        assert digest(path) == expected
        configs.append(str(path))
    target = out / 'clean-8ae60ff1.out'
    shutil.copyfile(binary, target)
    target.chmod(0o555)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    reg = Registry()
    lease = reg.build_lease('lane5', cpu=1, memory=4 * 1024**3)
    try:
        command = [str(target), *configs]
        with (out / 'raw.log').open('x') as log:
            result = subprocess.run(command, cwd=out, stdout=log, stderr=subprocess.STDOUT,
                env=dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1'), timeout=180)
        text = (out / 'raw.log').read_text()
        groups = [line for line in text.splitlines() if line.startswith('PASS production_')]
        assert result.returncode == 0 and len(groups) == 4
        expected = 'MATCHED_LOWER|off_packets=2|on_packets=1|off_bytes=64|on_bytes=32'
        assert text.splitlines().count(expected) == 1
        assert digest(out / 'raw.log') == '51da7c018524ec6efc44e1d48a5e8d67652634e96aa757068ee7023b472042fc'
        assert digest(binary) == digest(target)
        write_json(out / 'INDEPENDENT_CLEAN_CHECKS.json', {'status': 'PASS_CLEAN_CHECKPOINT_ONLY',
            'core_source_commit': source, 'r0_parent': '126394be46b15f55b9756d43eb9ca9a9baae1c84',
            'binary_sha256': digest(target), 'stimulus_sha256': digest(out / 'test_tvd_production.cc'),
            'command': command, 'exit_code': result.returncode, 'groups': groups,
            'actual_lower': {'off_packets': 2, 'on_packets': 1, 'off_bytes': 64, 'on_bytes': 32},
            'raw_log_sha256': digest(out / 'raw.log'), 'raw_matches_producer_exactly': True,
            'scope': 'actual memory_sub_partition small-geometry clean fixture; symbolic sector versions and real packet counts',
            'served_bytes_are_DRAM_savings': False, 'dirty_qualified': False,
            'integrated_R2_runtime_qualified': False, 'formal_applications': 0,
            'lease_id': lease, 'runner_source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()})
    finally:
        reg.release_build(lease, 'lane5')
    print('PASS_CLEAN_CHECKPOINT_ONLY', flush=True)


if __name__ == '__main__':
    main()
