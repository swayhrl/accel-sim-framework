"""Record the user's exact five-start authority; do not register budgets."""
import json
import pathlib

import exact5_common as common

ROOT = common.ROOT
AUTH_SHA = '900e9b6b1a31f1a9f3b8dd13c7e4580df415f27af3acc5727e59d930b7d7efc0'
REQUEST_SHA = '646e6b5c718f68de6c1f12fd5c3fc2f0f73b07761757d009d0c773ac790c7247'


def main():
    manifest = common.read(ROOT / 'control/ACTIVATION_MANIFEST.json')
    request = manifest['request']['path']
    user_text = manifest['user_authorization']['path']
    common.need(common.sha(request) == REQUEST_SHA and common.sha(user_text) == AUTH_SHA,
                'request or user authorization drift')
    common.need(manifest['Source5'] == common.read(request)['Source5'], 'Source5 drift')
    point_map = {point['cohort']: point for point in manifest['points']}
    common.need(set(point_map) == set(common.COHORTS), 'five cohorts changed')
    families = []
    for program, request_id in common.REQUESTS.items():
        members = [point for point in manifest['points'] if point['request_id'] == request_id]
        expected = 3 if program == 'GEMM' else 2
        common.need(len(members) == expected and
                    {point['cohort'] for point in members} ==
                    {cohort for cohort, name in common.COHORTS.items() if name == program},
                    'family point budget mismatch')
        families.append({'program': program, 'request_id': request_id,
                         'approved_launches': expected,
                         'allowed_cohorts': sorted(point['cohort'] for point in members),
                         'point_ids': sorted(point['point_id'] for point in members),
                         'Source5': manifest['Source5'],
                         'independent_release': True})
    record = {'schema': 'EP_L2_EXACT5_USER_AUTHORIZATION_V1',
              'goal': common.GOAL, 'explicit_user_approval': True,
              'approved_total_launches': 5,
              'user_request_ref': common.ref(user_text),
              'exact_request_ref': common.ref(request),
              'fixed_takeover_commit': manifest['fixed_takeover_commit'],
              'Source5': manifest['Source5'], 'families': families,
              'one_start_per_point': True, 'automatic_retry': False,
              'refund': False, 'source_keep': True,
              'budget_registration_performed': False,
              'model_start_performed': False}
    target = ROOT / 'control/USER_AUTHORIZATION.json'
    common.put(target, record, exclusive=True)
    print(json.dumps({'status': 'EXACT5_AUTHORITY_RECORDED_NO_BUDGET_OR_START',
                      'authorization_ref': common.ref(target)}, sort_keys=True))


if __name__ == '__main__':
    main()
