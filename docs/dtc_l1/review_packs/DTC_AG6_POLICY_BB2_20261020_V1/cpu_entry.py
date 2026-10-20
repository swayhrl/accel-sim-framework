"""One finite BB2 CPU entry: frozen read-only admission, then pure tests/replay.

No simulator, subprocess, signal, lock acquisition or production runtime import.
Archived admission modules are staged under the independent evidence root.
"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import time
import unittest

PACK = Path(__file__).resolve().parent
EVIDENCE = Path('/workspace/dtc-ag6-bb2-policy-174-v1/evidence')
RECEIPTS = EVIDENCE / 'cpu_attempt2'
GATE = EVIDENCE / 'frozen_admission'
REGISTRATION = PACK / 'CPU_ENTRY_REGISTRATION.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(name, value):
    with (RECEIPTS / name).open('x') as out:
        out.write(json.dumps(value, indent=2) + '\n')


def main():
    started = time.monotonic()
    RECEIPTS.mkdir(exist_ok=False)
    reg = json.loads(REGISTRATION.read_text())
    assert reg['role']['argvs'] == [[sys.executable, '-I', '-B', str(PACK / 'cpu_entry.py')]]
    assert reg['role']['cwd'] == os.getcwd()
    assert sha(sys.executable) == reg['role']['executable_sha256']
    for path, digest in reg['role']['source_sha256'].items():
        assert sha(path) == digest, path
    write('CPU_ENTRY_START.json', dict(utc=datetime.now(timezone.utc).isoformat(),
          monotonic_ns=time.monotonic_ns(), pid=os.getpid(), argv=sys.argv,
          registration_sha256=sha(REGISTRATION), source_sha256=reg['role']['source_sha256'],
          scope='ONE_BB2_OFFLINE_TEST_ROLE_NO_MODEL', max_expected_output_bytes=2*1024**2))
    # Copies of the exact archived CPU-admission/read-only authority source.
    # No guard, dispatcher or Core module is imported, and no BA path is written.
    sys.path[:0] = [str(GATE / 'vendor'), str(GATE)]
    from cpu_admission_v2 import CPUAdmission
    gate = CPUAdmission(reg, [reg['role']])
    status = dict(status='NOT_EXECUTED_RESOURCE_HOLD', test_runs=0,
                  simulator_starts=0, fixture_starts=0, retry=False)
    first = gate.sample()
    write('CPU_FIRST.json', first)
    checks = gate.checks(first)
    checks['actual_output_device'] = os.stat(EVIDENCE).st_dev == first['output_filesystem_device']
    checks['expected_output_margin'] = first['disk_free'] - 5*1024**3 >= 2*1024**2
    if not all(checks.values()):
        status.update(checks=checks, hold_stage='FIRST', actual_test_starts=0)
        write('CPU_ADMISSION.json', status)
        print(json.dumps(status)); return 0
    time.sleep(10.1)
    second = gate.sample()
    write('CPU_SECOND.json', second)
    checks.update({'second_'+k: v for k, v in gate.checks(second).items()})
    checks.update(gap_ge10s=second['monotonic_ns']-first['monotonic_ns'] >= 10*10**9,
        same_output_device=first['output_filesystem_device']==second['output_filesystem_device'],
        no_new_host_oom=first['host_oom_kill']==second['host_oom_kill'],
        no_new_cgroup_oom=all(first['cgroup_events'][k]==second['cgroup_events'][k] for k in ['oom','oom_kill']),
        second_actual_output_device=os.stat(EVIDENCE).st_dev==second['output_filesystem_device'],
        second_expected_output_margin=second['disk_free']-5*1024**3 >= 2*1024**2)
    if not all(checks.values()):
        status.update(checks=checks, hold_stage='PAIR', actual_test_starts=0)
        write('CPU_ADMISSION.json', status)
        print(json.dumps(status)); return 0
    # The fresh source/role binding is checked again before pure test imports.
    for path, digest in reg['role']['source_sha256'].items():
        assert sha(path) == digest, path
    write('CPU_ADMISSION.json', dict(status='PASS_CPU_ADMISSION_ONLY', checks=checks,
          gate_scope='STRICT_CURRENT_PAIRED_HOST_CGROUP_R2_AND_EXACT_ROLE', starts=0))
    sys.path.insert(0, str(PACK))
    import test_policy_b_offline
    output = io.StringIO()
    test_started = time.monotonic_ns()
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_policy_b_offline)
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    write('CPU_TEST_RESULT.json', dict(status='PASS_PURE_CPU_POLICY_ONLY' if result.wasSuccessful() else 'FAIL_CPU_POLICY',
          tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors),
          skipped=len(result.skipped), elapsed_ns=time.monotonic_ns()-test_started,
          transcript=output.getvalue(), scenario_provenance='DECLARED_SYNTHETIC',
          actual_test_starts=1, simulator_starts=0, fixture_starts=0,
          entry_total_seconds=time.monotonic()-started, source_sha256=reg['role']['source_sha256']))
    print(output.getvalue())
    if not result.wasSuccessful():
        return 1
    import replay_closed
    replay_closed.main()
    assert time.monotonic()-started < 90, 'FINITE_ENTRY_BOUND_EXCEEDED'
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        write('CPU_ENTRY_EXCEPTION.json', dict(error=repr(exc), test_result_exists=(RECEIPTS/'CPU_TEST_RESULT.json').exists(),
              simulator_starts=0, action='FAIL_CLOSED_NO_AUTORETRY'))
        raise
