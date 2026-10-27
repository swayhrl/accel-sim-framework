"""Main-only finite parameter specs; never starts a simulator or grants a budget."""
import copy, sys
from ep_perf_common import *


def prepare(plan_path, hostq_path):
    plan = read(plan_path); hostq = read(hostq_path)
    need(plan['goal'] == GOAL and plan['status'] == 'MAIN_REVIEWED_PREDECLARED_FINITE_EXPLORATION', 'reviewed plan required')
    need(hostq['status'] == 'HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED', 'qualified new host adapters')
    for item in hostq['modules']:
        need(sha(item['path']) == item['sha256'], 'host adapter bytes changed')
    catalog = exact(plan['catalog_ref']); compose = module(plan['composer_ref'], 'finite_parameter_composer')
    ctor = exact(plan['production_constructor_ref'])
    need(ctor['Source_unchanged'] and ctor['no_scientific_start'] and all(t['PASS'] for t in ctor['tests']), 'actual production constructor evidence')
    registry, unused = authority(); q = registry['registered_future_requests'][GOAL]
    refs = []; contracts = {}
    for profile in plan['profiles']:
        composed = compose.compose(catalog, profile['component_candidate_ids'])
        delta = composed['exact_common_effective_delta']
        need(delta == profile['expected_common_delta'], 'exact reviewed intervention changed')
        contracts[profile['profile']] = dict(common_delta=delta, resource_proxies=composed['resource_proxies'],
            physical_payload_budget='1168 line-owned128B slots/slice; metadata area UNKNOWN; static role reachability differs',
            implicit_observer_delta_included=False)
        for sample in plan['exploration_inputs']:
            for mode in ['S','F']:
                base_case = sample['reference_cohorts'][mode]
                row = q['consumed'][base_case]
                need(row['state'] == 'CLOSED_ACCEPTED', 'reference must have completed archive closure')
                base = read(ROOT/'cases'/base_case/'control/FROZEN_SPEC.json')
                point = exact(row['accepted_point_ref'])
                need(point['input_identity_sha256'] == sample['input_identity_sha256'] and point['mode'] == mode, 'reference input/mode')
                need(base['profile'] == 'REF32x8_L100' and base['mode'] == mode, 'reference configuration')
                case = 'EP_PERF_'+sample['case_short']+'_'+mode+'_'+profile['profile']+'_V1'
                folder = ROOT/'cases'/case; s = copy.deepcopy(base)
                s.update(cohort=case, profile=profile['profile'], host_qualification_ref=ref(hostq_path),
                    validation_module_ref=hostq['qualified_parameter_validation_module_ref'])
                opts = copy.deepcopy(base['expected_effective_options']); opts.update(delta)
                need(all(opts[k] == base['expected_effective_options'][k] for k in ['-gpgpu_ep_l2_ms_observer','-gpgpu_ep_l2_b0_stats','-gpgpu_ep_l2_m0a_stats','-gpgpu_l2_char_enable']), 'observation profile must match')
                need(s['observer_env'] == base['observer_env'], 'optional observer environment match')
                parts = opts['-gpgpu_cache:dl2'].split(',')[0].split(':')
                s['geometry'] = dict(slices=64, sets=int(parts[1]), ways=int(parts[3]), line_bytes=int(parts[2]))
                s['expected_effective_options'] = opts
                need(s['geometry']['sets'] in [32,64] and s['geometry']['ways'] in [8,16], 'unqualified geometry')
                configs = []
                for i,entry in enumerate(base['ordered_configs']):
                    text = P(entry['path']).read_text()
                    if i == len(base['ordered_configs'])-1:
                        text += '\n# Exact common hardware intervention; applied to matched S and F.\n'
                        text += ''.join(k+' '+v+'\n' for k,v in sorted(delta.items()))
                    path = folder/'env'/('config-'+str(i)+'.config'); path.parent.mkdir(parents=True,exist_ok=True)
                    with path.open('x') as f:
                        f.write(text)
                    configs.append(ref(path))
                s['ordered_configs'] = configs
                s['scientific_option_contract'] = dict(mode=mode, hardware_profile=profile['profile'], complete_282=True,
                    reference_spec_ref=ref(ROOT/'cases'/base_case/'control/FROZEN_SPEC.json'), reference_accepted_point_ref=row['accepted_point_ref'],
                    exact_common_hardware_delta=delta, mode_policy_unchanged=True, observer_profile_unchanged=True,
                    search_plan_ref=ref(plan_path), actual_constructor_ref=plan['production_constructor_ref'],
                    resource_proxies=composed['resource_proxies'], changes_are_modeled_hardware_not_area_claim=True)
                # New files only: reference eligibility/RO and all frozen prior artifacts stay immutable.
                s['pinned_files'].update({item['path']:item['sha256'] for item in hostq['modules']})
                put(folder/'control/FROZEN_SPEC.json', s, True)
                refs.append(ref(folder/'control/FROZEN_SPEC.json'))
    need(len(refs) == plan['maximum_new_starts'], 'finite point count')
    stage = dict(schema='EP_FULL_PERF_FINITE_STAGE_V1', goal=GOAL, status='MAIN_REVIEWED_EXACT_FINITE_STAGE', stage=plan['stage'],
        scientific_owner='Main', maximum_new_starts=len(refs), automatic_retry=False, refund=False, source_keep=True,
        authorization_ref=ref(ROOT/'control/USER_AUTHORIZATION.json'), engine_ref=ref(ROOT/'tools/ep_perf_native.py'),
        common_ref=ref(ROOT/'tools/ep_perf_common.py'), specs=refs, resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME',
        predeclared_search_plan_ref=ref(plan_path), host_qualification_ref=ref(hostq_path), exact_profile_contracts=contracts)
    path = ROOT/'control'/(plan['stage']+'.json'); put(path,stage,True)
    return dict(status='PARAMETER_SPECS_PREPARED_ZERO_STARTS', stage_ref=ref(path), cases=[read(r['path'])['cohort'] for r in refs])


if __name__ == '__main__':
    print(json.dumps(prepare(sys.argv[1], sys.argv[2])))
