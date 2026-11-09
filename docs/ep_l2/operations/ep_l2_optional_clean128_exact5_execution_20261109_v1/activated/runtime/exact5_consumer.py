"""Pure Source5 optional CLEAN128 terminal adapter; never starts or accepts science.

Retains the frozen numeric math body. The only change to the old raw scanner is
the actual option count (282 to 283). X1 is checked from original raw bytes.
"""
import gzip
import hashlib
import importlib.util
import inspect
import json
import pathlib
import re

P = pathlib.Path
L = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1')
FROZEN = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/performance_first_v5_20261105_v1/track_d_workloads/three_mm/runtime/deps/host_scaling/frozen_math/lowcost_terminal_v2.py')
SHELL = L / 'agent_d/a_segment_record_shell.py'
ABI = L / 'agent_d/A_FINAL_SOURCE_RECORD_ABI_CONTRACT.json'
FROZEN_SHA = 'cba193d8ec810219f58bbe55870814b70604082f4f6683a236a418e80b9da35c'
SHELL_SHA = '69de70f607f6337a21ac99a1ab43131b205baeeec8691b02fbbf9c45c0987c6c'
SOURCE5 = {
    'core_source_commit': '3d3887bb2e8d5073d13b0792ff9116834e89fe2f',
    'framework_source_commit': '9dd1ee57a83d83b56b7874bc7c716185ab52c8f7',
    'vendor_pybind11_commit': 'f90c430c3a1ce8f08c09942a5a1c3a797bb2295b',
    'binary_sha256': '9db48c06ca64e441b5824071f52e0aa0be50374045fbdcef6cdf5d4469182f86',
    'archive_sha256': '7199f3dd5bdba2167186ca6858cd15603997f560660b54e8a1457761f115f48b',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with P(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def isolated(path, name, expected):
    need(sha(path) == expected, 'pinned source drift: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def final_cost_frame(raw):
    """Keep exact final clock's original V2/V3/X1 lines; reject conflicts."""
    lines = {}
    current = None
    opener = gzip.open if str(raw).endswith('.gz') else P(raw).open
    with opener(raw, 'rt', errors='strict') if opener is gzip.open else opener('rt', errors='strict') as stream:
        for line in stream:
            m = re.fullmatch(r'gpu_tot_sim_cycle\s*=\s*(\d+)\s*', line)
            if m:
                cycle = int(m[1])
                need(current is None or cycle >= current, 'native cycle regressed')
                if cycle != current:
                    lines = {}
                current = cycle
            if line.startswith(('EPL2TVDV2|SUMMARY|', 'EPL2TVDV3|METADATA_COST|',
                                'EPL2TVDX1|SEGMENT|', 'EPL2TVDX1|CONTROL|')):
                need(current is not None, 'cost record without native clock')
                parts = line.rstrip('\n').split('|')
                sid = next((part[6:] for part in parts if part.startswith('slice=')), None)
                need(sid is not None, 'cost slice missing')
                key = (parts[0], parts[1], sid)
                prior = lines.get(key)
                need(prior is None or prior == line, 'conflicting final cost record')
                lines[key] = line
    need(current is not None, 'native final clock missing')
    return list(lines.values()), current


def adapted_scan(frozen):
    """Compile the pinned scanner with its single declared 283 count delta."""
    source = inspect.getsource(frozen.scan)
    needle = 'len(options)==282'
    need(source.count(needle) == 1, 'unexpected frozen scanner shape')
    source = source.replace(needle, 'len(options)==283')
    scope = dict(frozen.__dict__)
    exec(compile(source, 'SOURCE5_283_OPTION_SCANNER', 'exec'), scope)
    return scope['scan']


def validate_case(raw, spec, qualification, sourceq_path, sourceq_sha):
    frozen = isolated(FROZEN, 'isolated_exact5_frozen_lowcost', FROZEN_SHA)
    shell = isolated(SHELL, 'isolated_exact5_A_segment', SHELL_SHA)
    abi = json.loads(ABI.read_bytes())
    s = frozen.doc(spec)
    q = frozen.doc(qualification)
    need(s['source_identity'] == SOURCE5 == abi['Source5'], 'exact A Source5 mismatch')
    need(s['mode'] == 'WV_ZERO_RO' and s['T'] is False and s['M'] is False, 'exact WV no RO mode')
    mode = int(s['expected_effective_options']['-gpgpu_ep_l2_victim_extension'])
    need(mode in (0, 1, 2) and mode == s['victim_extension'], 'extension Spec/options mismatch')
    need(len(s['expected_effective_options']) == 283, 'actual 283 option map required')
    need(q['source_identity'] == SOURCE5, 'new Source Native qualification missing')
    need(sourceq_path is not None and sourceq_sha is not None,
         'Source qualification reference incomplete')
    need(sha(sourceq_path) == sourceq_sha,
         'Source qualification reference drift')
    sourceq = frozen.doc(sourceq_path)
    need(sourceq['source_identity'] == SOURCE5,
         'Source qualification has another producer')
    need(sha(s['binary_path']) == SOURCE5['binary_sha256'], 'ELF drift')
    need(sha(s['static_library_path']) == SOURCE5['archive_sha256'], 'static library drift')
    need(all(s['observer_env'].get(k) == '0' for k in
             ('EPL2_DETACH_DIAG', 'EPL2_TAGPRESSURE_DIAG', 'EPL2_TAG_LIFETIME', 'EP_L2_EVENT_TIMELINE')),
         'observer contract changed')
    lines, cost_clock = final_cost_frame(raw)
    x1 = shell.validate_final_frame(lines, mode, abi)
    by_slice = {row['slice']: row for row in x1['rows']}

    parse, receipt = frozen.numeric_math()
    need(receipt['numeric_body_sha256'] == abi['old_math_body_sha256'], 'numeric body drift')
    def source_specific_full_records(records, history, victim, ro):
        need(victim and not ro, 'unexpected frozen parser feature vector')
        expected = {(prefix, kind, sid, -1)
                    for sid in range(64)
                    for prefix, kind in (('EPL2TVDV2', 'SUMMARY'), ('EPL2TVDV3', 'METADATA_COST'))}
        need(set(records) == expected, 'frozen Base record population changed')
        for sid in range(64):
            row = by_slice[sid]
            need(records['EPL2TVDV2', 'SUMMARY', sid, -1] == row['base_raw_summary'], 'Base summary differs from X1 join')
            need(records['EPL2TVDV3', 'METADATA_COST', sid, -1] == row['base_raw_cost'], 'Base cost differs from X1 join')
        return {sid: by_slice[sid]['base_raw_summary'] for sid in range(64)}, {}
    parse.__globals__['validate_full_records'] = source_specific_full_records

    logical_hash, logical_bytes = frozen.logical_hash(raw)
    application = adapted_scan(frozen)(raw, s)
    need(application['optional_records'] == 0, 'disabled optional observer emitted data')
    hist = frozen.history_for(s)
    model = parse(frozen.RawPath(raw), hist, {})
    need(model['cycles'] == application['cycles'] == cost_clock, 'native, cost, and math cycles differ')
    need(model['instructions'] == application['instructions'], 'native and math instructions differ')
    model['data_correctness_qualification'] = False
    model['legacy_numeric_parser_protocol_checks_passed'] = True
    model['source_map']['mechanism'] = {
        'actual_source_identity': SOURCE5,
        'base_and_extension_join': 'SOURCE_SPECIFIC_A_COST_POPULATION_PASS',
        'application_numeric_output': 'UNKNOWN',
    }
    return {
        'status': 'EP_FULL_PERF_VALIDATED_PENDING_MAIN_NOT_APPLICATION_ACCEPTED',
        'source_identity': SOURCE5,
        'cohort': s['cohort'],
        'input_identity_sha256': s['input_identity_sha256'],
        'cycles': model['cycles'], 'instructions': model['instructions'],
        'CTA': application['CTA'], 'kernel_count': application['kernel_count'],
        'hardware_drained': True,
        'raw_logical_sha256': logical_hash, 'raw_uncompressed_bytes': logical_bytes,
        'raw_stored_sha256': sha(raw), 'raw_stored_bytes': P(raw).stat().st_size,
        'model': model, 'application': application, 'segment_cost': x1,
        'math_binding': receipt, 'scientific_acceptance_granted': False,
        'numeric_output': 'UNKNOWN',
        'outer_join_required': [
            'official consumed natural DONE and PID/argv/env/maps/strace',
            'current Source5, immutable Spec, NativeQ and Host pins',
            'lossless raw receipt and resource hard limits',
            'true164 full SHA archive and two distinct Native target restores',
        ],
    }
