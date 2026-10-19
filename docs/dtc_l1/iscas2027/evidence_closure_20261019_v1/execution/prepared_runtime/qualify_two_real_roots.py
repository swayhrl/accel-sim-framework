"""Exact registered two-root CPU lifecycle; no simulator entry or global PASS."""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
RAW = Path('/workspace/dtc-evidence-closure-20261019-v1/coordinator')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def absent_instance(row):
    try:
        fields = Path('/proc', str(row['pid']), 'stat').read_text().rsplit(')', 1)[1].split()
        return int(fields[19]) != row['start_ticks'] or fields[0] == 'Z'
    except FileNotFoundError:
        return True

def main():
    registration = json.loads((HERE.parent / 'CPU_REAL_LIFECYCLE_REGISTRATION.json').read_text())
    if registration['status'] != 'REGISTERED_FOR_TWO_CPU_ROOTS_ONLY':
        raise ValueError('EXACT_CPU_RELEASE_REQUIRED')
    for rel, digest in registration['prepared_source_sha256'].items():
        if sha(HERE / rel) != digest:
            raise ValueError('SOURCE_CHANGED:' + rel)
    for path, digest in registration['runtime_sha256'].items():
        if sha(path) != digest:
            raise ValueError('RUNTIME_CHANGED:' + path)
    sys.path.insert(0, str(HERE))
    from multi_root_cpu import run_two_registered_cpu_roots
    report = run_two_registered_cpu_roots(registration['requests'], registration['manager_output'])
    checks = {'two_roots': report['status'] == 'PASS_CPU_TWO_ROOT_LIFECYCLE_ONLY'}
    evidence = []
    for request in registration['requests']:
        destination = Path(request['destination'])
        events = [json.loads(line) for line in (destination / 'MAP_EVENTS.jsonl').read_text().splitlines()]
        images = {row.get('exe') for row in events}
        proofs = [row for row in events if row.get('proof') == 'PTRACE_GETEVENTMSG_FROM_CONFIRMED_PARENT']
        root = json.loads((destination / 'CHILD.json').read_text())
        identities = [{'pid': root['pid'], 'start_ticks': root['start_ticks']}]
        identities += [{'pid': row['new_owned_pid'], 'start_ticks': row['child_start_ticks']} for row in proofs]
        rows = {'root': root, 'proof_count': len(proofs), 'proof_events': sorted({row['event'] for row in proofs}),
                'images': sorted(x for x in images if x),
                'helper_dash_and_cat_observed': {'/usr/bin/dash', '/usr/bin/cat'} <= images,
                'fork_or_vfork_and_clone_observed': bool({1, 2} & {r['event'] for r in proofs}) and any(r['event'] == 3 for r in proofs),
                'all_event_proven_instances_absent': all(absent_instance(r) for r in identities),
                'event_proven_instances': identities,
                'stdout_marker_exact': (destination / 'stdout').read_bytes() == b'AG4_CPU_ONLY_OK\n',
                'cache_observed_and_unmapped': any(r.get('cache_present') for r in events) and any('/etc/ld.so.cache' in r.get('removed_files', []) for r in events),
                'map_events_sha256': sha(destination / 'MAP_EVENTS.jsonl')}
        evidence.append(rows)
        for key in ['helper_dash_and_cat_observed', 'fork_or_vfork_and_clone_observed',
                    'all_event_proven_instances_absent', 'stdout_marker_exact', 'cache_observed_and_unmapped']:
            checks[str(len(evidence)) + ':' + key] = rows[key]
    result = {'status': 'PASS_TWO_REAL_CPU_ROOTS_HELPER_LIFECYCLE_ONLY' if all(checks.values()) else 'CPU_LIFECYCLE_INCOMPLETE',
              'checks': checks, 'evidence': evidence, 'simulation_starts': 0,
              'whole_dispatcher_qualified': False, 'global_observer_external_roles_qualified': False,
              'performance_or_application_values_qualified': False,
              'remaining': ['production shared cross-root/global observer and unknown-role negatives',
                            'three exact external role integration', 'full family/ledger/source/resource admission']}
    output = Path(registration['manager_output']) / 'LIFECYCLE_SCOPE_RESULT.json'
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'output': str(output), 'checks': checks}), flush=True)
    return 0 if all(checks.values()) else 1

if __name__ == '__main__':
    sys.exit(main())
