"""Install five exact Native routes as an additive prefix under the shared lock."""
import fcntl
import hashlib
import json
import os
import pathlib
import uuid

P = pathlib.Path
ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
NATIVE = P('/root/data/ep_l2_dtc_l1_native_v2')
GLOBAL = NATIVE / 'bin/native'
LOCK = NATIVE / 'control/science_authority/NATIVE_ROUTE_UPDATE.lock'
REQUESTS = {
    'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1': ('gemm', (0, 1, 2)),
    'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1': ('stencil', (0, 2)),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    h = hashlib.sha256()
    with P(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': sha(path)}


def write_once(path, data):
    path = P(path)
    if path.exists():
        need(path.read_bytes() == data, 'immutable route artifact changed ' + str(path))
    else:
        with path.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    return ref(path)


def main():
    auth = json.loads((ROOT / 'control/USER_AUTHORIZATION.json').read_bytes())
    need(auth['explicit_user_approval'] and auth['approved_total_launches'] == 5,
         'exact user authority missing')
    cohorts = []
    entries = {}
    for request, (label, extensions) in REQUESTS.items():
        entry = ROOT / 'runtime' / ('host_' + label + '_bound_v2') / 'native_b1'
        entries[request] = ref(entry)
        for ext in extensions:
            cohort = 'EP_PERF_CLEAN128_' + label.upper() + '_WV_EXT' + str(ext) + '_20261109_V1'
            spec = ROOT / 'cases' / cohort / 'control/FROZEN_SPEC.json'
            s = json.loads(spec.read_bytes())
            need(s['cohort'] == cohort and s['science_request_id'] == request and
                 s['native_entry_ref'] == entries[request], 'formal Spec/entry mismatch')
            cohorts.append(cohort)
    need(len(cohorts) == len(set(cohorts)) == 5, 'route cohort set')
    cases = '\n'.join('  experiment:' + cohort + ')' +
                      '\n   exec ' + entries[request]['path'] + ' "$@"' +
                      '\n   ;;'
                      for request, (label, extensions) in REQUESTS.items()
                      for cohort in cohorts if cohort.startswith('EP_PERF_CLEAN128_' + label.upper() + '_'))
    prefix = ('#!/bin/sh\nset -eu\n# EP-L2 Main exact Source5 optional CLEAN128 five cohorts.\n'
              'if [ "$#" -eq 5 ] && [ "$1" = experiment ] && [ "$4" = --project ] && [ "$5" = EP_L2 ]; then\n'
              ' case "$1:$3" in\n' + cases + '\n esac\nfi\n').encode()
    need(prefix.count(b'experiment:EP_PERF_CLEAN128_') == 5 and
         prefix.count(b'result:EP_PERF_CLEAN128_') == 0, 'exact route prefix')
    guard = ROOT / 'runtime/native_route_guard_exact5.py'
    route_path = ROOT / 'control/NATIVE_ENTRY_ROUTE_EXACT5.json'
    with LOCK.open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        need(not route_path.exists(), 'route already installed; validate existing before retry')
        previous = GLOBAL.read_bytes()
        need(previous.startswith(b'#!/bin/sh\nset -eu\n') and
             b'EP_PERF_CLEAN128_' not in previous, 'shared Native already has this scope')
        before_ref = write_once(ROOT / 'control/NATIVE_GLOBAL_PREIMAGE_EXACT5.bin', previous)
        prefix_ref = write_once(ROOT / 'control/NATIVE_OWNED_PREFIX_EXACT5.bin', prefix)
        pins = [ref(guard)]
        for label in ('gemm', 'stencil'):
            host = ROOT / 'runtime' / ('host_' + label + '_bound_v2')
            for name in ('native_b1', 'ep_perf_frontend.py', 'ep_perf_native_wv_modes_draft.py',
                         'ep_perf_common_v2.py', 'ep_perf_postprocess.py', 'ep_perf_archive.py',
                         'resources_b1.py', 'runtime_monitor_schema_v4_strict.py'):
                pins.append(ref(host / name))
        pins += [ref(ROOT / 'runtime/exact5_consumer.py'),
                 ref(ROOT / 'runtime/exact5_mode_contract.py')]
        need(len({item['path'] for item in pins}) == len(pins), 'duplicate runtime pin')
        route = {
            'schema': 'EP_L2_EXACT5_NATIVE_ROUTE_V1',
            'approved_by': 'EP-L2 Main',
            'scientific_scope_activated': True,
            'request_ids': sorted(REQUESTS),
            'exact_cohorts': sorted(cohorts),
            'entry_refs': entries,
            'Main_user_authorization_ref': ref(ROOT / 'control/USER_AUTHORIZATION.json'),
            'guard_module_ref': ref(guard),
            'global_shared_native_path': str(GLOBAL),
            'global_preimage_ref': before_ref,
            'owned_prefix_ref': prefix_ref,
            'owned_runtime_pins': pins,
            'source_keep': True,
            'other_owner_routes_preserved_as_exact_preimage': True,
        }
        candidate = prefix + previous
        temp = GLOBAL.with_name('.native.exact5.' + str(uuid.uuid4()))
        with temp.open('xb') as stream:
            stream.write(candidate)
            stream.flush()
            os.fsync(stream.fileno())
        temp.chmod(GLOBAL.stat().st_mode & 0o777)
        need(GLOBAL.read_bytes() == previous, 'global Native changed while locked')
        os.replace(temp, GLOBAL)
        need(GLOBAL.read_bytes() == candidate and sha(GLOBAL) == hashlib.sha256(candidate).hexdigest(),
             'Native install readback')
        route_ref = write_once(route_path, (json.dumps(route, sort_keys=True, separators=(',', ':')) + '\n').encode())
        import importlib.util
        spec = importlib.util.spec_from_file_location('exact5_route_guard', guard)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        check = module.validate_current(route_path)
    print(json.dumps({'status': 'FIVE_EXACT_NATIVE_ROUTES_INSTALLED_NO_BUDGET_NO_MODEL',
                      'route_ref': route_ref, 'guard': check}, sort_keys=True))


if __name__ == '__main__':
    main()
