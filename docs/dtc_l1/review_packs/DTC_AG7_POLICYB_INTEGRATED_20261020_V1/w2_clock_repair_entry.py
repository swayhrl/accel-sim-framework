"""One finite strict-R2 protocol rerun after the receive-clock race repair."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time
import unittest

P = Path(__file__).resolve().parent
E = Path('/workspace/dtc-ag7-policyb-integrated-174-v1/evidence')
G = E / 'w0_frozen_authority'
Q = E / 'w2_clock_repair_once'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def main():
    assert sys.argv == [str(P / 'w2_clock_repair_entry.py')]
    Q.mkdir(exist_ok=False)
    reg = json.loads((P / 'W2_CLOCK_REPAIR_REGISTRATION.json').read_text())
    role = reg['role']
    assert os.getcwd() == role['cwd'] and sha(sys.executable) == role['executable_sha256']
    for path, digest in role['source_sha256'].items():
        assert sha(path) == digest, path
    sys.path[:0] = [str(P / 'prepared_ag7'), str(P), str(G / 'vendor'), str(G)]
    from cpu_admission_v2 import CPUAdmission
    from w1_cpu_entry import images, identity
    import test_integration
    before, loaded = identity(), images()
    gate = CPUAdmission(reg, [role])
    samples, checks = [], {}
    for index in range(2):
        if index:
            time.sleep(10.1)
        sample = gate.sample()
        samples.append(sample)
        write(Q / ('FIRST.json' if index == 0 else 'SECOND.json'), sample)
        current = gate.checks(sample)
        current.update(self_instance=identity() == before, loaded_images=images() == loaded,
            output_device=os.stat(E).st_dev == sample['output_filesystem_device'],
            projected_writes=sample['disk_free'] - 2 * 1024**2 > 5 * 1024**3)
        checks.update({str(index) + ':' + key: value for key, value in current.items()})
        if not all(current.values()):
            write(Q / 'RESULT.json', dict(status='RESOURCE_HOLD', checks=checks, simulator_starts=0))
            return 0
    first, second = samples
    checks.update(gap_ge10s=second['monotonic_ns'] - first['monotonic_ns'] >= 10**10,
        host_oom_same=first['host_oom_kill'] == second['host_oom_kill'],
        cg_oom_same=all(first['cgroup_events'][k] == second['cgroup_events'][k] for k in ['oom', 'oom_kill']))
    assert all(checks.values()), checks
    transcript = io.StringIO()
    started = time.monotonic_ns()
    result = unittest.TextTestRunner(stream=transcript, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromModule(test_integration))
    stable = images() == loaded and identity() == before
    passed = result.wasSuccessful() and result.testsRun == 9 and stable
    write(Q / 'RESULT.json', dict(status='PASS_CLOCK_REPAIR_NINE_PROTOCOL_METHODS' if passed else 'TEST_FAILURE',
        checks=checks, tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        transcript=transcript.getvalue(), elapsed_ns=time.monotonic_ns() - started,
        mapped_images_stable=stable, source_sha256=role['source_sha256'],
        strict_host_io_exception=False, simulator_starts=0, fixtures=0,
        provenance='DECLARED_SYNTHETIC_TIMELINES_REAL_SELF_SOCKET_CREDENTIALS',
        reason='Consumer monotonic clock sampled after receive; producer timestamp remains progress evidence')))
    print(transcript.getvalue())
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
