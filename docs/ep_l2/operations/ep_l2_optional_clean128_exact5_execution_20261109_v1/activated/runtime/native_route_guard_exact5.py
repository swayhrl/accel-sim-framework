"""Read-only guard for the five exact Source5 Native routes."""
import hashlib
import json
import pathlib

P = pathlib.Path
REQUESTS = {
    'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1': (
        'EP_PERF_CLEAN128_GEMM_WV_EXT0_20261109_V1',
        'EP_PERF_CLEAN128_GEMM_WV_EXT1_20261109_V1',
        'EP_PERF_CLEAN128_GEMM_WV_EXT2_20261109_V1'),
    'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1': (
        'EP_PERF_CLEAN128_STENCIL_WV_EXT0_20261109_V1',
        'EP_PERF_CLEAN128_STENCIL_WV_EXT2_20261109_V1'),
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with P(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def pinned(ref):
    need(type(ref) is dict and type(ref.get('path')) is str and
         type(ref.get('sha256')) is str and sha(ref['path']) == ref['sha256'],
         'route reference changed')
    return P(ref['path']).read_bytes()


def validate_current(routepath):
    route = json.loads(P(routepath).read_bytes())
    need(route['schema'] == 'EP_L2_EXACT5_NATIVE_ROUTE_V1' and
         route['approved_by'] == 'EP-L2 Main' and
         route['scientific_scope_activated'] is True,
         'inactive or unrelated route')
    need(route['request_ids'] == sorted(REQUESTS) and
         route['exact_cohorts'] == sorted(c for cases in REQUESTS.values() for c in cases),
         'route has wrong request or cohort set')
    need(set(route['entry_refs']) == set(REQUESTS), 'entry request set changed')
    for request, ref in route['entry_refs'].items():
        entry = pinned(ref)
        need(b'EP_FULL_PERF_NATIVE_ENTRY=1' in entry and
             b'/usr/bin/python3 -B ' in entry,
             'entry no longer enforces the sole Native path: ' + request)
    auth = json.loads(pinned(route['Main_user_authorization_ref']))
    need(auth['goal'] == 'EP_L2_OPTIONAL_CLEAN128_EXACT5_EXECUTION_V1' and
         auth['explicit_user_approval'] is True and
         auth['approved_total_launches'] == 5,
         'authorization reference')
    guard = route['guard_module_ref']
    need(guard['path'] == str(P(__file__).resolve()) and
         guard['sha256'] == sha(__file__), 'guard self pin changed')
    before = pinned(route['global_preimage_ref'])
    prefix = pinned(route['owned_prefix_ref'])
    need(prefix.startswith(b'#!/bin/sh\nset -eu\n') and
         prefix.count(b'experiment:EP_PERF_CLEAN128_') == 5 and
         prefix.count(b'result:EP_PERF_CLEAN128_') == 0,
         'owned route prefix changed')
    global_path = route['global_shared_native_path']
    need(global_path == '/root/data/ep_l2_dtc_l1_native_v2/bin/native',
         'not the installed shared Native entry')
    need(P(global_path).read_bytes() == prefix + before,
         'shared Native differs from exact additive insertion')
    pins = route['owned_runtime_pins']
    paths = [ref['path'] for ref in pins]
    need(len(paths) == len(set(paths)) and
         guard['path'] in paths and
         {r['path'] for r in route['entry_refs'].values()}.issubset(paths),
         'owned runtime pin population')
    for ref in pins:
        pinned(ref)
    return {
        'status': 'EXACT5_ADDITIVE_NATIVE_ROUTE_PASS',
        'request_ids': route['request_ids'],
        'exact_cohorts': route['exact_cohorts'],
        'global_sha256': sha(global_path),
        'preimage_sha256': route['global_preimage_ref']['sha256'],
        'owned_prefix_sha256': route['owned_prefix_ref']['sha256'],
        'consumes_science_budget': False,
    }
