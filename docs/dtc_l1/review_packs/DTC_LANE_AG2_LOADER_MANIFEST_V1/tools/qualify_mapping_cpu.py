"""Run a finite list of CPU parser cases through fixed system Python only."""
import json
from pathlib import Path
import subprocess
from test_mapping_roles_cpu import CASES
from early_system_loader_cpu import RAW, write_new
from mapping_roles import sha

def main():
    script = Path(__file__).resolve().with_name('test_mapping_roles_cpu.py')
    results = []
    for name, (expected_rc, expected_reason) in CASES.items():
        argv = ['/usr/bin/python3', '-B', str(script), name]
        p = subprocess.run(argv, capture_output=True, text=True, timeout=15,
                           env={'PATH':'/usr/bin:/bin', 'LANG':'C', 'LC_ALL':'C', 'PYTHONDONTWRITEBYTECODE':'1'})
        try:
            data = json.loads(p.stdout)
        except ValueError:
            data = {}
        reason = data.get('reason', data.get('outcome', 'MISSING_RESULT'))
        passed = p.returncode == expected_rc and reason.split(':')[0] == expected_reason and not p.stderr
        results.append(dict(case=name, argv=argv, expected_exitcode=expected_rc,
                     expected_reason=expected_reason, actual_exitcode=p.returncode,
                     actual_reason=reason, stdout=p.stdout, stderr=p.stderr,
                     status='PASS_EXPECTED_RESULT' if passed else 'FAIL'))
    write_new(RAW / 'MAPPING_ROLE_TEST_RESULTS_V2.json', dict(
        status='PASS_ALL_CPU_CASES' if all(r['status']=='PASS_EXPECTED_RESULT' for r in results) else 'STOP',
        cases=results, script_sha256=sha(script), simulator_starts=0))
    print(json.dumps(dict(total=len(results), passed=sum(r['status']=='PASS_EXPECTED_RESULT' for r in results),
                          failures=[r for r in results if r['status']!='PASS_EXPECTED_RESULT'])))
    return 0 if all(r['status']=='PASS_EXPECTED_RESULT' for r in results) else 1

if __name__ == '__main__':
    raise SystemExit(main())
