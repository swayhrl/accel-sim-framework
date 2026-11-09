"""Capture bounded, no-model native route CPU evidence for the R0 review."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('/root/data/dtc_short_collect_native_discovery10_v1_20261109')
TOOLS = ROOT / 'tools'
EVIDENCE = ROOT / 'evidence' / 'r0_native_route_cpu'
REGISTRY = Path('/root/data/ep_l2_dtc_l1_native_v2/control/science_authority/NATIVE_SCIENCE_REGISTRY.json')
REQUEST = ROOT / 'control/requests/C1_EXACT_REQUEST_PREPARED.json'
REQUEST_ID = 'DTC_SHORT_COLLECT_C1_20261109_V1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    before = sha(REGISTRY)
    runs = []
    for script in ('test_route_cpu.py', 'test_guard_cpu.py'):
        result = subprocess.run([sys.executable, '-B', str(TOOLS / script)],
                                cwd=TOOLS, capture_output=True, text=True,
                                timeout=30, check=False)
        log_path = EVIDENCE / (script + '.log')
        log_path.write_text(result.stdout + result.stderr)
        runs.append({'script': str(TOOLS / script), 'exit_code': result.returncode,
                     'log': str(log_path), 'log_sha256': sha(log_path)})
    after = sha(REGISTRY)
    registry = json.loads(REGISTRY.read_bytes())
    result_root = ROOT / 'DTC/run/results'
    ledger = ROOT / 'control/qualification_ledger'
    evidence = {
        'schema': 'DTC_SHORT_COLLECT_R0_NATIVE_ROUTE_CPU_EVIDENCE_V1',
        'utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'status': 'CPU_FIXTURE_TESTS_ONLY_R0_NOT_QUALIFIED',
        'contract_commit': 'dfd6d7aa0383b8fda9ff08672f8c9efc392df26f',
        'candidate_core': '9a0de9b9f97144f481b3e3637e329ebab01acb74',
        'exact_c1_request': str(REQUEST), 'exact_c1_request_sha256': sha(REQUEST),
        'tools': {name: sha(TOOLS / name) for name in
                  ('route_authority.py', 'route_lease.py', 'route_guard.py',
                   'test_route_cpu.py', 'test_guard_cpu.py')},
        'test_runs': runs,
        'registry_sha256_before': before, 'registry_sha256_after': after,
        'registry_unchanged_during_capture': before == after,
        'request_registered_in_global_registry': REQUEST_ID in registry['registered_future_requests'],
        'new_root_intent_count': len(list(ledger.glob('*.INTENT.json'))) if ledger.exists() else 0,
        'new_root_done_count': len(list(ledger.glob('*.DONE.json'))) if ledger.exists() else 0,
        'new_root_result_directory_count': len([p for p in result_root.iterdir() if p.is_dir()]) if result_root.exists() else 0,
        'production_dispatcher_implemented': False,
        'production_launcher_implemented': False,
        'models_started_by_this_capture': 0,
        'r0_release_present': (ROOT / 'control/R0_RELEASE.json').exists(),
    }
    path = EVIDENCE / 'CPU_ROUTE_EVIDENCE.json'
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'evidence': str(path), 'sha256': sha(path),
                      'all_tests_pass': all(r['exit_code'] == 0 for r in runs),
                      'registry_unchanged': before == after,
                      'request_registered': evidence['request_registered_in_global_registry'],
                      'new_root_intents': evidence['new_root_intent_count']}, sort_keys=True))
    if not all(r['exit_code'] == 0 for r in runs) or before != after:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
