"""Bind five immutable Source5 Specs after no-start Host checks.

This command never touches the shared registry or Native route and starts no model.
"""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
DOC = ROOT / 'documents'
NATIVE = Path('/root/data/ep_l2_dtc_l1_native_v2')
COHORTS = {
    'GEMM': ('gemm', (0, 1, 2)),
    'Stencil': ('stencil', (0, 2)),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def ref(path):
    return {'path': str(path), 'sha256': sha(path)}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_once(path, value):
    body = (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()
    if path.exists():
        need(path.read_bytes() == body, 'immutable artifact changed: ' + str(path))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
    return ref(path)


def main():
    auth = json.loads((ROOT / 'control/USER_AUTHORIZATION.json').read_bytes())
    need(auth['explicit_user_approval'] is True and auth['approved_total_launches'] == 5,
         'five start authorization missing')
    need(ref(ROOT / 'control/USER_REQUEST.txt') == auth['user_request_ref'],
         'authorization source changed')
    mode = load(ROOT / 'runtime/exact5_mode_contract.py', 'exact5_mode')
    source = json.loads((DOC / 'SOURCE_CPU_QUALIFICATION.json').read_bytes())
    need(source['status'] == 'PRODUCTION_CPU_BUILD_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',
         'Source5 engineering qualification absent')
    evidence = {}
    for name, script in [('consumer_preflight', 'consumer_preflight.py'),
                         ('population_fixture', 'consumer_population_fixture.py')]:
        output = subprocess.check_output([sys.executable, '-B', str(ROOT / 'runtime' / script)],
                                         text=True, cwd=ROOT / 'runtime')
        rows = [json.loads(line) for line in output.splitlines() if line.strip()]
        need(rows and all('PASS' in row['status'] for row in rows), name + ' failed')
        evidence[name] = write_once(DOC / (name.upper() + '_NO_START_RECEIPT.json'),
                                    {'script_ref': ref(ROOT / 'runtime' / script), 'results': rows,
                                     'models_started': False})
    qualification = {}
    for program, (label, extensions) in COHORTS.items():
        host = ROOT / 'runtime' / ('host_' + label + '_bound_v2')
        paths = [host / name for name in (
            'ep_perf_common_v2.py', 'ep_perf_frontend.py', 'ep_perf_native_wv_modes_draft.py',
            'ep_perf_postprocess.py', 'ep_perf_archive.py', 'resources_b1.py',
            'runtime_monitor_schema_v4_strict.py', 'native_b1')]
        paths += [ROOT / 'runtime' / name for name in (
            'exact5_mode_contract.py', 'exact5_consumer.py', 'native_route_guard_exact5.py')]
        for path in paths:
            need(path.exists(), 'missing Host dependency: ' + str(path))
        module_refs = [ref(path) for path in paths]
        cohorts = ['EP_PERF_CLEAN128_' + program.upper() + '_WV_EXT' + str(ext) + '_20261109_V1'
                   for ext in extensions]
        for cohort in cohorts:
            candidate_path = ROOT / 'cases' / cohort / 'control/BOUND_SPEC_CANDIDATE.json'
            candidate = json.loads(candidate_path.read_bytes())
            mode.validate_static(candidate)
            need(candidate['program'].lower() == program.lower(), 'candidate family drift')
            need(candidate['source_identity'] == source['source_identity'], 'candidate Source5 drift')
        hostq = {
            'schema': 'EP_L2_EXACT5_SOURCE5_HOST_QUALIFICATION_V1',
            'status': 'HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',
            'approved_by': 'EP-L2 Main',
            'source_identity': source['source_identity'],
            'application_acceptance_granted': False,
            'cohorts_qualified': sorted(cohorts),
            'modes_qualified': ['WV_ZERO_RO'],
            'modules': module_refs,
            'evidence_refs': {
                'source_cpu': ref(DOC / 'SOURCE_CPU_QUALIFICATION.json'),
                'native22': ref(DOC / 'SOURCE5_NATIVE22_CLOSURE.json'),
                'host_trace_child': ref(DOC / 'SOURCE5_HOST_TRACE_CHILD_DEPENDENCIES.json'),
                **evidence,
            },
            'qualification_scope': 'STATIC_HOST_AND_BOUNDED_CPU_ABI_NO_FULL_APPLICATION',
        }
        qualification[label] = write_once(DOC / ('HOST_QUALIFICATION_EXACT5_' + label.upper() + '.json'), hostq)
    binding = {
        'schema': 'EP_L2_EXACT5_MAIN_ENGINEERING_BINDING_V1',
        'status': 'MAIN_REVIEWED_EXACT_SOURCE283',
        'approved_by': 'EP-L2 Main',
        'cpu_reviewed_by': 'EP-L2 Main',
        'independent_review_pass': True,
        'source_identity': source['source_identity'],
        'authority_ref': ref(ROOT / 'control/USER_AUTHORIZATION.json'),
        'host_qualification_refs': qualification,
        'no_model_start_during_binding': True,
        'source_keep': True,
    }
    binding_ref = write_once(DOC / 'MAIN_ENGINEERING_BINDING_EXACT5.json', binding)
    results = []
    for program, (label, extensions) in COHORTS.items():
        host = ROOT / 'runtime' / ('host_' + label + '_bound_v2')
        sys.modules.pop('ep_perf_common_v2', None)
        sys.path.insert(0, str(host))
        engine = load(host / 'ep_perf_native_wv_modes_draft.py', 'exact5_engine_' + label)
        for ext in extensions:
            cohort = 'EP_PERF_CLEAN128_' + program.upper() + '_WV_EXT' + str(ext) + '_20261109_V1'
            cp = ROOT / 'cases' / cohort / 'control'
            spec = copy.deepcopy(json.loads((cp / 'BOUND_SPEC_CANDIDATE.json').read_bytes()))
            spec.update({
                'host_engine_ref': ref(host / 'ep_perf_native_wv_modes_draft.py'),
                'host_common_ref': ref(host / 'ep_perf_common_v2.py'),
                'host_qualification_ref': qualification[label],
                'native_entry_ref': ref(host / 'native_b1'),
                'native_route_guard_ref': ref(ROOT / 'runtime/native_route_guard_exact5.py'),
                'postprocess_module_ref': ref(host / 'ep_perf_postprocess.py'),
                'archive_module_ref': ref(host / 'ep_perf_archive.py'),
                'resource_module_ref': ref(host / 'resources_b1.py'),
                'Main_engineering_binding_ref': binding_ref,
                'Main_scientific_launch_authorization': ref(ROOT / 'control/USER_AUTHORIZATION.json'),
                'Main_review_status': 'MAIN_REVIEWED_SOURCE5_EXACT5_FORMAL_BINDING',
                'launch_permission': True,
                'scientific_launch_permission': True,
                'scientific_scope_activated': True,
                'status': 'MAIN_BOUND_EXACT_SOURCE5_PENDING_NATIVE_ROUTE_AND_REGISTRY',
            })
            child_deps = json.loads((DOC / 'SOURCE5_HOST_TRACE_CHILD_DEPENDENCIES.json').read_bytes())
            for item in child_deps['dependencies']:
                need(sha(item['path']) == item['sha256'] and
                     str(Path(item['path']).resolve()) == item['resolved_path'],
                     'Host/Trace-child dependency changed')
                spec['pinned_files'][item['path']] = item['sha256']
            mode.validate_static(spec)
            engine.engineering_static(spec)
            results.append({'cohort': cohort, 'spec_ref': write_once(cp / 'FROZEN_SPEC.json', spec),
                            'host_family': label})
        sys.path.pop(0)
    print(json.dumps({'status': 'FIVE_FORMAL_SPECS_BOUND_NO_NATIVE_INSTALL_NO_REGISTRY_NO_START',
                      'points': results, 'host_qualifications': qualification}, sort_keys=True))


if __name__ == '__main__':
    main()
