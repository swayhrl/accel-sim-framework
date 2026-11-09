"""Idempotently register two fresh scoped budgets; never consumes or starts."""
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

P = pathlib.Path
ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
NATIVE = P('/root/data/ep_l2_dtc_l1_native_v2')
FAMILIES = {
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


def main():
    auth_ref = ref(ROOT / 'control/USER_AUTHORIZATION.json')
    auth = json.loads(P(auth_ref['path']).read_bytes())
    need(auth['approved_total_launches'] == 5 and auth['explicit_user_approval'] is True,
         'five exact launches not authorized')
    route_path = ROOT / 'control/NATIVE_ENTRY_ROUTE_EXACT5.json'
    route_ref = ref(route_path)
    guard_path = ROOT / 'runtime/native_route_guard_exact5.py'
    guard = importlib.util.spec_from_file_location('exact5_route_guard_for_registration', guard_path)
    module = importlib.util.module_from_spec(guard)
    guard.loader.exec_module(module)
    module.validate_current(route_path)
    pre = subprocess.check_output([sys.executable, '-B', str(ROOT / 'control/preactivation_check.py')],
                                  text=True)
    observed = json.loads(pre)
    need(observed['status'] == 'READ_ONLY_PREACTIVATION_CHECK_PASS' and
         observed['observed_model_lines'] == [], 'pre-registration current model status')
    results = []
    for request, (label, extensions) in FAMILIES.items():
        host = ROOT / 'runtime' / ('host_' + label + '_bound_v2')
        common_path = host / 'ep_perf_common_v2.py'
        spec = importlib.util.spec_from_file_location('exact5_common_' + label, common_path)
        common = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(common)
        need(common.GOAL == request and common.ROOT == ROOT, 'Host family common mismatch')
        cohorts = ['EP_PERF_CLEAN128_' + label.upper() + '_WV_EXT' + str(ext) + '_20261109_V1'
                   for ext in extensions]
        admitted = {}
        for cohort in cohorts:
            path = ROOT / 'cases' / cohort / 'control/FROZEN_SPEC.json'
            s = json.loads(path.read_bytes())
            need(s['cohort'] == cohort and s['science_request_id'] == request and
                 s['native_entry_ref'] == ref(host / 'native_b1') and
                 s['Main_scientific_launch_authorization'] == auth_ref and
                 s['source_identity'] == auth['Source5'], 'formal point binding changed')
            admitted[cohort] = sha(path)
        engine_ref = ref(host / 'ep_perf_native_wv_modes_draft.py')
        common_ref = ref(common_path)
        def register(registry):
            rows = registry['registered_future_requests']
            if request in rows:
                q = rows[request]
                need(q['admitted_specs'] == admitted and q['budget'] == len(cohorts) and
                     q['authorization_ref'] == auth_ref and
                     q['native_entry_ref'] == ref(host / 'native_b1'),
                     'existing scope has different identity')
                return {'status': 'EXISTING_IDENTICAL_SCOPE_REUSED', 'request': request}
            need(all(c not in (q.get('admitted_specs') if isinstance(q.get('admitted_specs'), dict) else {})
                     and c not in (q.get('consumed') if isinstance(q.get('consumed'), dict) else {})
                     for q in rows.values() for c in cohorts), 'cohort already registered elsewhere')
            q = {
                'request': request, 'request_id': request, 'resource_group_id': request,
                'owner': 'EP-L2 Main', 'project': 'EP_L2', 'state': 'REGISTERED_FRESH_SCOPE_NO_START',
                'budget': len(cohorts), 'remaining': len(cohorts), 'consumed': {},
                'admitted_specs': admitted, 'allowed_cohorts': sorted(cohorts),
                'authorization_ref': auth_ref, 'native_qualification_ref': route_ref,
                'native_entry_ref': ref(host / 'native_b1'),
                'runtime_versions': {engine_ref['sha256']: {'engine_ref': engine_ref,
                                                           'common_ref': common_ref}},
                'source_identity': auth['Source5'], 'source_keep': True,
                'independent_release': True, 'automatic_retry': False, 'refund': False,
                'global_model_concurrency_authorized': 10,
                'global_model_concurrency_qualified': 10,
                'reserved_write_bytes': (len(cohorts) * 64 + 64 + 2) * 1024 * 1024,
                'registered_utc': common.now(),
            }
            rows[request] = q
            return {'status': 'FRESH_SCOPE_REGISTERED_NO_START', 'request': request,
                    'budget': len(cohorts), 'admitted_specs': admitted}
        current, unused = common.authority()
        if request in current['registered_future_requests']:
            result = register(current)
        else:
            result = common.transaction('REGISTER_FRESH_EXACT5_SCOPED_BUDGET_NO_START', register)
        results.append(result)
    print(json.dumps({'status': 'TWO_EXACT5_SCOPES_REGISTERED_NO_MODEL_CONSUMED',
                      'families': results}, sort_keys=True))


if __name__ == '__main__':
    main()
