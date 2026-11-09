"""Read-only Gate C first-four route and immutable source manifest draft.

This module has no request/UUID allocator, registry writer, launcher, or archive
writer. Main must freeze W before any output can be promoted to science.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path('/root/data/dtc_finite_service_completion_v1_20261109')
MATRIX = Path('/root/data/dtc_core32_oracle_main_closeout_20261109_v1/docs/dtc_l1/review_packs/CORE32_ORACLE_FINAL_SCIENTIFIC_REVIEW_20261109_V1/evidence/fixed/FIXED32_INPUT_AND_RESULT_INDEX.json')
CONTRACT = Path(__file__).with_name('INPUT_MATRIX10.json')
WITNESSES = {'GESUMMV', 'MVT', 'ATAX', 'BICG'}
MODES = ('OFF', 'ON')
NEW_OPTION = '-gpgpu_dtc_l1_short_collect_first'
CORE_COMMIT = '9a0de9b9f97144f481b3e3637e329ebab01acb74'
FRAMEWORK_COMMIT = '02775fd795cde5aae1480d81cee6eb481d0a08f4'
GOAL_COMMIT = '32cbe43f6975ff6a11cfd1210f88026771656b48'
CONTRACT_SHA256 = '09d1257c532269bab41d2cf845399482812ce02e54e02897ae46e72cedec4a4a'
MATRIX_SHA256 = '0ae69ed6c73d38415b0f10344a0d2f50e960c6a0324d48c8763a7760d87fdab1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def require(ok, code):
    if not ok:
        raise RuntimeError(code)


def route(witness):
    require(witness in WITNESSES, 'W_NOT_ALLOWED_OR_NOT_FROZEN')
    require(sha(CONTRACT) == CONTRACT_SHA256, 'GOAL_CONTRACT_SHA')
    require(sha(MATRIX) == MATRIX_SHA256, 'FIXED_CORE32_INDEX_SHA')
    matrix = read(CONTRACT)
    index = read(MATRIX)
    require(matrix['schema'] == 'DTC_FINITE_SERVICE_DISCOVERY10_PREREGISTRATION_V1', 'MATRIX_SCHEMA')
    require(index['schema'] and len(index['rows']) == 32, 'INDEX_SCOPE')
    programs = {p['program']: p for p in matrix['programs']}
    indexed = {r['program']: r for r in index['rows']}
    require(set(programs) <= set(indexed), 'INDEX_MISSING_PROGRAM')
    cells = []
    for program in (witness, 'vectorAdd'):
        p, source = programs[program], indexed[program]
        require(p['full_input_digest_sha256'] == source['input_digest'], 'INPUT_DIGEST_MISMATCH')
        require((p['declared_kernel_count'], p['declared_total_CTA'], p['declared_active_thread_instructions']) ==
                (source['declared_kernels'], source['declared_CTA'], source['declared_active_thread_instructions']), 'WORKLOAD_SHAPE_MISMATCH')
        binding = source['input_binding']
        require(sha(binding['path']) == binding['sha256'], 'INPUT_BINDING_SHA')
        old = source['cells']['OFF_MATCHED']
        require(sha(old['spec_path']) == old['spec_sha256'], 'HISTORICAL_SPEC_SHA')
        spec = read(old['spec_path'])
        require(spec['input_digest'] == source['input_digest'] and spec['expected'] ==
                {'kernels': p['declared_kernel_count'], 'CTA': p['declared_total_CTA'],
                 'instructions': p['declared_active_thread_instructions']}, 'HISTORICAL_SPEC_SCOPE')
        require(len(spec['expected_options']) == 271 and spec['expected_options']['-gpgpu_dtc_oracle_mode'] == ['0'], 'OLD_ORACLE_OPTIONS_SCOPE')
        historical_spec_path = Path(spec['historical_DH_P0_spec_path'])
        require(sha(historical_spec_path) == spec['historical_DH_P0_spec_sha256'], 'DH_P0_SPEC_SHA')
        historical = read(historical_spec_path)
        require(historical['input_digest'] == source['input_digest'] and
                historical['expected'] == spec['expected'], 'DH_P0_SPEC_SCOPE')
        options = historical['expected_options']
        require(len(options) == 270 and NEW_OPTION not in options and
                dict(options, **{'-gpgpu_dtc_oracle_mode':['0']}) == spec['expected_options'], 'BASE_OPTION_SCOPE')
        require(options['-gpgpu_perfect_mem'] == ['0'] and options['-l2_ideal'] == ['0'], 'IDEAL_OPTIONS_FORBIDDEN')
        for mode in MODES:
            effective = dict(options, **{NEW_OPTION: ['1' if mode == 'ON' else '0']})
            require(len(effective) == 271, 'NEW_EFFECTIVE_OPTION_COUNT')
            cells.append({
                'program': program, 'mode': mode,
                'input_digest': source['input_digest'],
                'input_binding': binding,
                'historical_DH_P0_source_spec_path': str(historical_spec_path),
                'historical_DH_P0_source_spec_sha256': spec['historical_DH_P0_spec_sha256'],
                'oracle_crosscheck_spec_path': old['spec_path'],
                'oracle_crosscheck_spec_sha256': old['spec_sha256'],
                'declared_kernel_count': p['declared_kernel_count'],
                'declared_total_CTA': p['declared_total_CTA'],
                'declared_active_thread_instructions': p['declared_active_thread_instructions'],
                'core_commit': CORE_COMMIT, 'framework_commit': FRAMEWORK_COMMIT,
                'effective_options': effective,
                'effective_options_count': len(effective),
                'route_status': 'STATIC_ONLY_NO_REQUEST_NO_UUID_NO_MODEL',
            })
    require(len(cells) == 4 and [c['mode'] for c in cells] == ['OFF','ON','OFF','ON'], 'FIRST4_ORDER')
    require(cells[0]['effective_options'].keys() == cells[1]['effective_options'].keys(), 'PAIR_OPTION_SET')
    for a,b in ((cells[0],cells[1]), (cells[2],cells[3])):
        require({k:v for k,v in a['effective_options'].items() if k != NEW_OPTION} ==
                {k:v for k,v in b['effective_options'].items() if k != NEW_OPTION}, 'NONCANDIDATE_OPTIONS_DIFFER')
    return {'schema':'DTC_FIRST4_STATIC_ROUTE_V1','status':'DRAFT_NO_SCIENCE_ADMISSION',
            'goal_commit':GOAL_COMMIT,'witness':witness,'source_matrix_sha256':CONTRACT_SHA256,
            'source_index_sha256':MATRIX_SHA256,'cells':cells,
            'unbound':['request','uuid','binary_sha256','libcudart_sha256','framework_build_sha256',
                       'new_config_sha256','runtime_guard','strict','true164_archive','typed_native_restore']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--witness', choices=sorted(WITNESSES))
    parser.add_argument('--check-all', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    require(args.check_all != bool(args.witness), 'SELECT_ONE_CHECK_ALL_OR_WITNESS')
    if args.check_all:
        require(args.output is None, 'CHECK_ALL_CANNOT_WRITE')
        for witness in sorted(WITNESSES):
            data = route(witness)
            print(f"PASS_STATIC {witness} cells={len(data['cells'])} "
                  f"digests={data['cells'][0]['input_digest']},{data['cells'][2]['input_digest']} "
                  f"options={data['cells'][0]['effective_options_count']}")
        return
    data = route(args.witness)
    payload = json.dumps(data, sort_keys=True, indent=2) + '\n'
    if args.output:
        require(args.output.resolve().is_relative_to((ROOT/'evidence'/'gate_c_static').resolve()), 'OUTPUT_OUTSIDE_ISOLATION')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload)
    else:
        print(payload, end='')


if __name__ == '__main__':
    main()
