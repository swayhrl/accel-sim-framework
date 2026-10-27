"""Main-only finite exact-stage registration, never starts a model."""
import sys
from ep_perf_common import *


def extend(stage_path):
    stage = read(stage_path)
    need(stage['goal'] == GOAL and stage['status'] == 'MAIN_REVIEWED_EXACT_FINITE_STAGE', 'stage not reviewed')
    need(stage['maximum_new_starts'] == len(stage['specs']) > 0, 'finite stage count')
    auth = exact(stage['authorization_ref'])
    need(auth['goal'] == GOAL and auth['user_request_ref'] == ref(ROOT/'control/USER_REQUEST.txt'), 'fresh Goal authorization')
    need(stage['scientific_owner'] == 'Main' and stage['automatic_retry'] is False, 'sole dispatcher/no retry')
    specs = {}
    for item in stage['specs']:
        value = exact(item)
        case = value['cohort']
        need(case not in specs and case.startswith('EP_PERF_'), 'duplicate/bad cohort')
        need(value['goal'] == GOAL and value['application_budget'] == 1, 'fresh one-start spec')
        need(P(item['path']) == ROOT/'cases'/case/'control/FROZEN_SPEC.json', 'noncanonical spec')
        specs[case] = item['sha256']
    stage_ref = ref(stage_path)
    def register(registry):
        requests = registry['registered_future_requests']
        if GOAL not in requests:
            requests[GOAL] = dict(request=GOAL, project='EP_L2', owner='EP-MAIN', state='ARMED',
                budget=0, remaining=0, consumed={}, admitted_specs={}, stages=[], source_keep=True,
                automatic_retry=False, refund=False, authorization_ref=stage['authorization_ref'],
                runtime_versions={},
                reserved_write_bytes=0, resource_group_id=GOAL)
        q = requests[GOAL]
        runtime = dict(engine_ref=stage['engine_ref'], common_ref=stage['common_ref'])
        key = stage['engine_ref']['sha256']
        if key in q['runtime_versions']:
            need(q['runtime_versions'][key] == runtime, 'existing runtime version immutable')
        else:
            need(sha(stage['engine_ref']['path']) == key and sha(stage['common_ref']['path']) == stage['common_ref']['sha256'], 'new runtime pins')
            q['runtime_versions'][key] = runtime
        need(q['authorization_ref'] == stage['authorization_ref'], 'authorization changed')
        need(stage_ref not in q['stages'], 'stage already registered; no automatic repeat')
        need(not set(specs) & set(q['admitted_specs']), 'existing cohort preserved')
        q['admitted_specs'].update(specs)
        q['budget'] += len(specs)
        q['remaining'] += len(specs)
        q['stages'].append(stage_ref)
        q['state'] = 'ARMED' if not q['consumed'] else 'RUNNING'
    transaction('REGISTER_NEW_EXACT_FINITE_STAGE_NO_OLD_BUDGET', register)
    return dict(status='NEW_SCOPED_STAGE_REGISTERED_ZERO_STARTS', stage_ref=stage_ref,
                new_budget=len(specs), cohorts=list(specs))


if __name__ == '__main__':
    need(len(sys.argv) == 2, 'exact stage JSON required')
    print(json.dumps(extend(sys.argv[1])))
