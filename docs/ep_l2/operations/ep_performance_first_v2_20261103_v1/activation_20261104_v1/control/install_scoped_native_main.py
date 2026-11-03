"""Main-only exact two-family native installation. No registry/model operations."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shlex
import subprocess

V = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v2_20261103_v1')
A = V / 'activation_20261104_v1'
GLOBAL = Path('/root/data/ep_l2_dtc_l1_native_v2/bin/native')
PRIOR_SHA = '46c69a74154e0690afd82324a348da236baf90189d9a7e474b4b14eb01ab4f0e'
GROUPS = {
    'system': (A / 'agent_c_binding/qualified_runtime', Path('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_system850_v2_20261104_v1/system'), 12),
    'highclock': (A / 'agent_b_binding/qualified_runtime', Path('/root/data/ep_l2_full_workload_performance_20261027_v1/execution_cc_cam_highclock_20261104_v1/highclock'), 6),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    return dict(path=str(path), sha256=digest(path.read_bytes()))


def immutable_write(path, data, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, 'existing immutable bytes differ: ' + str(path)
    else:
        with path.open('xb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(path, mode)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def render(cohorts, frontend, prior):
    assert all(x.startswith('EP_PERF_') and x.replace('_', '').isalnum() for x in cohorts)
    prelude = prior.splitlines(keepends=True)[0].decode() + '''set -eu
# Main exact approved PFV2 family only. Preserved global suffix is unreachable.
if [ "$#" -ge 3 ] && [ "$1" = experiment ]; then
 case "$3" in
  ''' + '|'.join(cohorts) + ''')
   if [ "$#" -ne 5 ] || [ "$4" != --project ] || [ "$5" != EP_L2 ]; then
    printf '%s\n' '{"status":"HOLD","reason":"EXACT5_EP_PROJECT_REQUIRED","scientific_starts":0}' >&2; exit 2
   fi
   case "$2" in prepare|inspect|run-native|accept) ;;
    *) printf '%s\n' '{"status":"HOLD","reason":"UNSUPPORTED_OPERATION","scientific_starts":0}' >&2; exit 2;;
   esac
   export EP_FULL_PERF_NATIVE_ENTRY=1
   exec /usr/bin/python3 -B ''' + shlex.quote(str(frontend)) + ''' "$@"
   ;;
 esac
fi
printf '%s\n' '{"status":"HOLD","reason":"OUTSIDE_EXACT_APPROVED_PFV2_SCOPE","scientific_starts":0}' >&2
exit 2
# Original global-native preimage, preserved byte-for-byte and unreachable.
'''
    return prelude, prelude.encode() + prior


def install(group):
    runtime, root, count = GROUPS[group]
    scope = json.loads((runtime / 'FAMILY_SCOPE.json').read_text())
    cohorts = sorted(x.get('cohort', x.get('id')) for x in scope['points'])
    assert len(cohorts) == len(set(cohorts)) == count
    auth = json.loads((root / 'control/USER_AUTHORIZATION.json').read_text())
    assert auth['goal'] == scope['request_id'] and auth['budget'] == count
    assert auth['review_commit'] == '14b2eead02e70cdf39fa2a6cd5e53a48f1590559'
    prior = GLOBAL.read_bytes()
    assert digest(prior) == PRIOR_SHA
    assert (A / 'control/SHARED_NATIVE_PREIMAGE.bin').read_bytes() == prior
    prelude, payload = render(cohorts, runtime / 'ep_perf_frontend.py', prior)
    entry = root.parent / 'bin/native'
    saved_prior = root.parent / ('control/SHARED_NATIVE_PREIMAGE_' + PRIOR_SHA + '.bin')
    immutable_write(saved_prior, prior)
    immutable_write(entry, payload, 0o755)
    assert entry.read_bytes().endswith(prior) and GLOBAL.read_bytes() == prior
    syntax = subprocess.run(['/bin/sh', '-n', str(entry)], capture_output=True, text=True)
    assert syntax.returncode == 0, syntax.stderr
    controls = []
    cases = [
        ['experiment', 'run-native', 'EP_PERF_UNKNOWN', '--project', 'EP_L2'],
        ['experiment', 'prepare', 'EP_PERF_VECTOR4M_F_REF_V1', '--project', 'EP_L2'],
        ['experiment', 'run-native', 'E2-DTCL2MLP_UNKNOWN', '--project', 'DTC_L1'],
        ['experiment', 'bad-operation', cohorts[0], '--project', 'EP_L2'],
        ['experiment', 'prepare', cohorts[0], '--project', 'DTC_L1'],
        ['experiment', 'prepare', cohorts[0]],
    ]
    for args in cases:
        p = subprocess.run([str(entry)] + args, capture_output=True, text=True)
        assert p.returncode == 2, (args, p.stdout, p.stderr)
        controls.append(dict(args=args, exit=p.returncode, output=p.stdout + p.stderr, scientific_starts=0))
    route = dict(goal=scope['request_id'], status='MAIN_INSTALLED_ADDITIVE_NATIVE_EP_PERF_ROUTE',
                 entry_ref=ref(entry), prior_entry_ref=ref(saved_prior), own_prelude=prelude,
                 global_native_ref=ref(GLOBAL), frontend_ref=ref(runtime / 'ep_perf_frontend.py'),
                 global_native_unchanged=True, scientific_starts=0)
    immutable_write(root / 'control/NATIVE_ENTRY_ROUTE.json', json_bytes(route))
    receipt = dict(schema='EP_MAIN_PFV2_INSTALLED_SCOPED_NATIVE_PREPARATION_V1',
                   status='INSTALLED_EXACT_FAILCLOSED_ENTRY_NO_REGISTRATION_OR_START', group=group,
                   entry_ref=ref(entry), route_ref=ref(root / 'control/NATIVE_ENTRY_ROUTE.json'),
                   cohorts=cohorts, negative_controls=controls, shell_syntax='PASS',
                   global_native_ref=ref(GLOBAL), global_prior_suffix='EXACT_BYTES_UNREACHABLE',
                   new_scientific_starts=0)
    p = A / ('control/SCOPED_NATIVE_INSTALL_' + group.upper() + '.json')
    immutable_write(p, json_bytes(receipt))
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=list(GROUPS))
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    assert args.apply, 'Explicit Main installation only; this does not authorize models'
    print(json.dumps(install(args.group)))
