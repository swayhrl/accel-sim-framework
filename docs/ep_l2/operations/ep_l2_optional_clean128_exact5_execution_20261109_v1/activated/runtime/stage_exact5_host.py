"""Stage Source5 family Host adapters from the frozen UMT1 seed; no activation."""
import pathlib
import shutil

ROOT = pathlib.Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
SEED = ROOT / 'runtime_seed_UMT1_READONLY_COPY'
FAMILIES = {
    'gemm': ('GEMM', 'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1', (0, 1, 2)),
    'stencil': ('stencil', 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1', (0, 2)),
}


def replace_block(source, start, end, replacement):
    a, b = source.index('\ndef ' + start + '('), source.index('\ndef ' + end + '(')
    if not a < b:
        raise ValueError('seed function order drift')
    return source[:a] + '\n' + replacement.strip() + '\n' + source[b:]


def main():
    for label, (program, request, modes) in FAMILIES.items():
        dest = ROOT / 'runtime' / ('host_' + label + '_bound_v2')
        if dest.exists():
            raise FileExistsError(dest)
        shutil.copytree(SEED, dest)
        common = dest / 'ep_perf_common_v2.py'
        body = common.read_text()
        old_root = "/root/data/ep_l2_full_workload_performance_20261027_v1/research/unified_memory_taxonomy_20261106_v1/execution_authorized4_20261106_v1/engineering_host/conv/execution"
        old_req = 'EP_L2_UMT1_CONV3072_SOURCE812_PRESSURE_MATCHED_F_850_L100_V1'
        if body.count(old_root) != 1 or body.count(old_req) != 1:
            raise ValueError('common seed shape changed')
        body = body.replace(old_root, str(ROOT)).replace(old_req, request)
        common.write_text(body)
        resources = dest / 'resources_b1.py'
        body = resources.read_text()
        if body.count(old_req) != 1:
            raise ValueError('resource seed shape changed')
        old_exec = '/root/data/ep_l2_full_workload_performance_20261027_v1/research/unified_memory_taxonomy_20261106_v1/execution_authorized4_20261106_v1/engineering_host/conv/execution'
        if body.count(old_exec) != 1:
            raise ValueError('resource execution root seed shape changed')
        resources.write_text(body.replace(old_req, request).replace(old_exec, str(ROOT)))
        archive = dest / 'ep_perf_archive.py'
        body = archive.read_text()
        old_archive = '/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_umt1_pressure_20261106_v1/conv'
        if body.count(old_archive) != 1:
            raise ValueError('archive seed shape changed')
        archive.write_text(body.replace(old_archive,
            '/root/share/mnt164/huangrulin/host174_storage_recovery/ep_l2_optional_clean128_exact5_20261109_v1/' + label))
        engine = dest / 'ep_perf_native_wv_modes_draft.py'
        body = engine.read_text()
        head = '''"""Exact Source5 optional CLEAN128 family Host; no import-time actors."""
import gzip, hashlib, json, os, pathlib, resource, selectors, shutil, signal
import subprocess, sys, time, uuid
from ep_perf_common_v2 import *

SCOPED_MODES = {COHORT: 'WV_ZERO_RO' for COHORT in __EXACT5_COHORT_TUPLE__}
ALLOWED_COHORTS = frozenset(SCOPED_MODES)
LEDGER = NATIVE / 'control/qualification_ledger'

def authorized_scope_mode(s):
    need(s.get('cohort') in ALLOWED_COHORTS and s.get('mode') == 'WV_ZERO_RO',
         'outside exact Source5 family')
    need(s.get('T') is False and s.get('M') is False,
         'WV_ZERO_RO T/M mismatch')
    return s['mode']

def formal_mode_contract(s):
    return module(s['mode_contract_ref'], 'exact5_mode_contract').validate_static(s)

def validate_spec_contract(s, require_bound_cpu=False, check_current_domain=True):
    base = ROOT / 'documents'
    schema = module(ref(P(__file__).with_name('runtime_monitor_schema_v4_strict.py')),
                    'exact5_host43_schema')
    return schema.validate_spec_contract(
        s, ref(base / 'RUNTIME_FULL43_CONTRACT.json'),
        ref(base / 'SOURCE5_NATIVE22_CLOSURE.json'),
        require_bound_cpu=require_bound_cpu,
        check_current_domain=check_current_domain,
        check_current_dependencies=True,
        extra_dependencies_ref=ref(base / 'SOURCE5_HOST_TRACE_CHILD_DEPENDENCIES.json'))
'''
        cohorts = ['EP_PERF_CLEAN128_' + program.upper() + '_WV_EXT' + str(mode) + '_20261109_V1'
                   for mode in modes]
        if head.count('__EXACT5_COHORT_TUPLE__') != 1:
            raise ValueError('Host cohort placeholder drift')
        head = head.replace('__EXACT5_COHORT_TUPLE__', repr(tuple(cohorts)))
        a = body.index('def engineering_static(')
        body = head + '\n' + body[a:]
        spec_functions = '''def spec_path(case):
    need(case in ALLOWED_COHORTS, 'not an authorized Source5 cohort')
    return ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'

def spec_for(case):
    path = spec_path(case)
    need(path.exists(), 'immutable Spec not materialized')
    s = read(path)
    engineering_static(s)
    registry, unused = authority()
    need(GOAL in registry['registered_future_requests'], 'family not registered')
    q = registry['registered_future_requests'][GOAL]
    need(q['admitted_specs'].get(case) == sha(path), 'Spec not registered or changed')
    need(q['budget'] == len(q['admitted_specs']) and
         q['remaining'] == q['budget'] - len(q['consumed']), 'scoped budget arithmetic')
    need(s['schema'] == 'EP_FULL_PERF_EXACT_SPEC_V1' and s['goal'] == FRONTEND_GOAL and
         s['science_request_id'] == GOAL and s['cohort'] == case, 'formal Spec identity')
    auth = exact(q['authorization_ref'])
    need(auth['explicit_user_approval'] is True and auth['approved_total_launches'] == 5 and
         auth['user_request_ref'] == ref(ROOT / 'control/USER_REQUEST.txt'), 'user authority')
    family = next((row for row in auth['families'] if row['request_id'] == GOAL), None)
    need(family is not None and case in family['allowed_cohorts'] and
         family['approved_launches'] == q['budget'], 'family authority scope')
    eligibility = exact(s['eligibility_ref'])
    need(eligibility['status'] == 'ENGINEERING_COMPLETE_INPUT_IDENTITY_ELIGIBLE_NOT_APP_ACCEPTED' and
         eligibility['source_identity'] == s['source_identity'] and
         eligibility['input_identity_sha256'] == s['input_identity_sha256'], 'Source5 input eligibility')
    source = exact(s['source_qualification_ref'])
    need(source['source_identity'] == s['source_identity'] and
         source['status'] == 'PRODUCTION_CPU_BUILD_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',
         'Source5 engineering qualification')
    need(s['host_engine_ref'] == ref(__file__) and
         s['host_common_ref'] == ref(P(__file__).with_name('ep_perf_common_v2.py')),
         'Host engine/common pin')
    need(q['runtime_versions'].get(s['host_engine_ref']['sha256']) ==
         dict(engine_ref=s['host_engine_ref'], common_ref=s['host_common_ref']),
         'registered Host runtime version')
    return s

def enforce_stage_gates(s, q, registry):
    need(s['independent_scientific_release'] is True, 'point release not independent')
    need(s['limits']['wall_seconds'] == WALL_SECONDS and
         s['final_comparison_requirement'] == 'SAME_SOURCE_BOTH_ENDPOINTS_CLOSED_ACCEPTED',
         'family wall/comparison contract')
    return dict(status='EXACT5_INDEPENDENT_POINT_RELEASE',
                launch_completion_predecessor=None)
'''
        spec_functions = spec_functions.replace('WALL_SECONDS', '86400' if label == 'gemm' else '172800')
        body = replace_block(body, 'spec_path', 'fresh_input', spec_functions)
        route_name = 'NATIVE_ENTRY_ROUTE_EXACT5.json'
        old_route_path = "ROOT/'control/NATIVE_ENTRY_ROUTE_V3.json'"
        if body.count(old_route_path) != 2:
            raise ValueError('route path seed shape changed')
        body = body.replace(old_route_path, "ROOT/'control/" + route_name + "'")
        old_route = "need(route['goal']==GOAL and route['entry_ref']==registry['registered_future_requests'][GOAL]['native_entry_ref']==s['native_entry_ref'],'scoped Main route/entry binding')"
        new_route = "need(GOAL in route['request_ids'] and route['entry_refs'][GOAL]==registry['registered_future_requests'][GOAL]['native_entry_ref']==s['native_entry_ref'],'scoped Main route/entry binding')"
        if body.count(old_route) != 1:
            raise ValueError('route seed shape changed')
        body = body.replace(old_route, new_route)
        old_cohorts = "need(route['exact_cohorts']==sorted(SCOPED_MODES),'exact two F cohort route')"
        if body.count(old_cohorts) != 1:
            raise ValueError('route cohort seed shape changed')
        body = body.replace(old_cohorts,
                            "need(set(SCOPED_MODES).issubset(route['exact_cohorts']),'exact family cohort route')")
        old_policy = "requested_host_cpu=binding['host_cpu'],stage_ready=True)"
        if body.count(old_policy) != 1:
            raise ValueError('resource admission policy seed drift')
        body = body.replace(old_policy,
                            "requested_host_cpu=binding['host_cpu'],stage_ready=True,max_global_EP_models=10)")
        engine.write_text(body)
        resources = dest / 'resources_b1.py'
        body = resources.read_text()
        old_inject = "m.SCOPES[REQUEST]=Path(EXEC_ROOT)"
        if body.count(old_inject) != 1:
            raise ValueError('resource scope injection seed drift')
        # This Main releases one family at a time. The other family remains a
        # foreign registry row until its own turn, preventing duplicate claims.
        frontend = '''"""One exact family Native entry; all starts consume before model fork."""
import json, os, sys
from ep_perf_common_v2 import *

def main(args):
    need(os.environ.get('EP_FULL_PERF_NATIVE_ENTRY') == '1', 'sole Native entry required')
    need(len(args) == 5 and args[0] == 'experiment' and args[3:] == ['--project', 'EP_L2'],
         'exact Native command')
    need(args[1] in ('prepare', 'inspect', 'run-native', 'accept'), 'unknown operation')
    case = args[2]
    need(case in __EXACT5_COHORT_TUPLE__, 'outside family cohorts')
    registry, unused = authority()
    need(GOAL in registry['registered_future_requests'], 'family unregistered')
    q = registry['registered_future_requests'][GOAL]
    path = ROOT / 'cases' / case / 'control/FROZEN_SPEC.json'
    need(path.exists() and q['admitted_specs'].get(case) == sha(path), 'immutable Spec not registered')
    s = read(path)
    item = s['host_engine_ref']
    need(P(item['path']).is_relative_to(P(__file__).resolve().parent) and
         sha(item['path']) == item['sha256'], 'Host engine location/content')
    if args[1] == 'accept':
        return module(s['postprocess_module_ref'], 'exact5_postprocess').postprocess(case)
    return module(item, 'exact5_case_engine').main(args)

if __name__ == '__main__':
    try:
        print(json.dumps(main(sys.argv[1:])))
    except Exception as exc:
        print(json.dumps(dict(status='HOLD', reason=str(exc), automatic_retry=False)), file=sys.stderr)
        sys.exit(2)
'''.replace('__EXACT5_COHORT_TUPLE__', repr(tuple(cohorts)))
        (dest / 'ep_perf_frontend.py').write_text(frontend)
        (dest / 'native_b1').write_text('#!/bin/sh\nset -eu\nexport EP_FULL_PERF_NATIVE_ENTRY=1\nexec /usr/bin/python3 -B ' + str(dest / 'ep_perf_frontend.py') + ' "$@"\n')
    print('STAGED_TWO_SOURCE5_HOST_FAMILIES_NO_ACTIVATION')


if __name__ == '__main__':
    main()
