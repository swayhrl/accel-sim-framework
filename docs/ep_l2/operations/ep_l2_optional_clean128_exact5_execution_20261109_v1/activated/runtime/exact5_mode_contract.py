"""Source5 exact five-point identity contract. Pure read-only validation."""
import hashlib
import json
import pathlib

P = pathlib.Path
ROOT = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/optional_clean128_exact5_execution_20261109_v1')
REQUEST = P('/root/data/ep_l2_full_workload_performance_20261027_v1/research/next_cost_aware_architecture_20261107_v1/agent_d/FINAL_EXACT_EXPERIMENT_REQUEST.json')
REQUEST_SHA = '646e6b5c718f68de6c1f12fd5c3fc2f0f73b07761757d009d0c773ac790c7247'
SOURCE_Q = ROOT / 'documents/SOURCE_CPU_QUALIFICATION.json'
FAMILIES = {'GEMM': 'EP_L2_OPTIONAL_CLEAN128_GEMM3_20261109_V1',
            'Stencil': 'EP_L2_OPTIONAL_CLEAN128_STENCIL2_20261109_V1'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with P(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def read(path):
    return json.loads(P(path).read_bytes())


def exact(ref):
    need(type(ref) is dict and sha(ref['path']) == ref['sha256'], 'immutable reference drift')
    return read(ref['path'])


def request_point(point_id):
    need(sha(REQUEST) == REQUEST_SHA, 'fixed request drift')
    request = read(REQUEST)
    points = [row for row in request['points'] if row['point_id'] == point_id]
    need(len(points) == 1, 'not one exact authorized proposal point')
    point = points[0]
    need(point['Source5'] == request['Source5'], 'request Source5 inconsistency')
    return point


def validate_static(spec, candidate=False):
    s = read(spec) if isinstance(spec, (str, P)) else spec
    p = request_point(s['proposal_point_id'])
    source = read(SOURCE_Q)
    need(s['source_identity'] == p['Source5'] == source['source_identity'], 'Source5 drift')
    need(source['status'] == 'PRODUCTION_CPU_BUILD_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED'
         and source['application_acceptance_granted'] is False, 'Source5 engineering evidence scope')
    need(s['program'].lower() == p['program'].lower() and
         s['science_request_id'] == FAMILIES[p['program']],
         'wrong family request')
    need(s['cohort'] == 'EP_PERF_CLEAN128_' + p['program'].upper() + '_WV_EXT' +
         str(p['victim_extension']) + '_20261109_V1', 'point/cohort map')
    need(s['victim_extension'] == p['victim_extension'] and
         s['mode'] == p['mode'] == 'WV_ZERO_RO' and s['T'] is s['M'] is False,
         'extension or WV mode')
    need(s['expected_effective_options'] == p['full_effective_option_map'] and
         len(s['expected_effective_options']) == 283 and
         s['exact_config_canonical_sha256'] == p['full_config_canonical_sha256'],
         'exact application 283 option map')
    need(s['input_identity_sha256'] == p['input_identity']['input_identity_sha256'] and
         s['input_binding_ref'] == p['input_identity']['input_binding_ref'],
         'input identity mismatch')
    need(s['expected_instructions'] == p['input_identity']['expected_instructions'] and
         s['expected_CTA'] == p['input_identity']['expected_CTA'] and
         s['expected_kernel_launches'] == p['input_identity']['expected_kernel_launches'],
         'kernel/instruction/CTA population')
    need(s['geometry'] == p['geometry'] and s['application_budget'] ==
         s['approved_launches'] == 1 and s['independent_scientific_release'] is True,
         'geometry or one-start budget')
    need(s['limits'] == {'AS_bytes': p['resources']['hard_AS_bytes'],
                         'RSS_bytes': p['resources']['hard_RSS_bytes'],
                         'result_bytes': p['resources']['hard_native_result_bytes'],
                         'wall_seconds': p['resources']['hard_wall_seconds']},
         'resource contract mismatch')
    need(s['estimated_peak_RAM_bytes'] == p['resources']['estimated_RAM_bytes'] and
         s['source_keep'] is True and s['automatic_retry'] is False and s['refund'] is False,
         'resource estimate or KEEP/retry policy')
    need(s['ro_qualification_ref'] is None and all(s['observer_env'].get(key) == '0'
         for key in ('EPL2_DETACH_DIAG', 'EPL2_TAGPRESSURE_DIAG',
                     'EPL2_TAG_LIFETIME', 'EP_L2_EVENT_TIMELINE')),
         'RO or optional observer changed')
    if not candidate:
        need(s['source_qualification_ref'] == {'path': str(SOURCE_Q), 'sha256': sha(SOURCE_Q)},
             'Source5 qualification not bound')
        eligibility = exact(s['eligibility_ref'])
        need(eligibility['status'] == 'ENGINEERING_COMPLETE_INPUT_IDENTITY_ELIGIBLE_NOT_APP_ACCEPTED'
             and eligibility['source_identity'] == s['source_identity']
             and eligibility['input_identity_sha256'] == s['input_identity_sha256']
             and eligibility['application_acceptance_granted'] is False,
             'new Source5 input engineering eligibility missing')
        need(s['scientific_option_contract'].get('complete_282') is not True,
             'stale 282-option declaration')
    return {'status': 'EXACT5_SOURCE5_POINT_IDENTITY_PASS_NOT_APPLICATION_ACCEPTANCE',
            'point_id': p['point_id'], 'cohort': s['cohort'],
            'family': p['family'], 'extension': p['victim_extension'],
            'launch_permission': False}


def validate_fair_pair(left, right):
    a, b = request_point(left['proposal_point_id']), request_point(right['proposal_point_id'])
    need(a['program'] == b['program'] and a['Source5'] == b['Source5'] and
         a['input_identity']['input_identity_sha256'] == b['input_identity']['input_identity_sha256'],
         'cross-source or cross-input comparison')
    x, y = a['full_effective_option_map'], b['full_effective_option_map']
    flag = '-gpgpu_ep_l2_victim_extension'
    need({k: v for k, v in x.items() if k != flag} ==
         {k: v for k, v in y.items() if k != flag}, 'unmatched 283 option background')
    return {'status': 'SAME_SOURCE_INPUT_AND_BACKGROUND_EXCEPT_EXTENSION_PASS',
            'extensions': [a['victim_extension'], b['victim_extension']],
            'application_acceptance_granted': False}


if __name__ == '__main__':
    for file in sorted(ROOT.glob('cases/*/control/DRAFT_SPEC.json')):
        print(json.dumps(validate_static(file, candidate=True), sort_keys=True))
