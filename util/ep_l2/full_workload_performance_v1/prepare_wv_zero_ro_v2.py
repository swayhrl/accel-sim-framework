"""Main-only, finite S/WV preparation from reviewed complete input components."""
import copy, re, sys
from ep_perf_common import *


def prepare(index_path, digests, stage_name):
    index = read(index_path)
    handoff_ref = ref(ROOT/'agent_a/wv_zero_ro_20261028_v1/WV_ZERO_RO_CONFIG_AND_CPU_HANDOFF.json')
    handoff = exact(handoff_ref)
    need(handoff['status'] == 'ACTUAL_SOURCE78_CTOR_EMPTY_CLASSIFIER_NEGATIVE_GUARDS_PASS_NO_APP_OR_LAUNCH_GRANT', 'WV CPU qualification absent')
    exact(handoff['actual_CPU_receipt_ref'])
    base = read(ROOT/'cases/EP_PERF_VECTOR4M_S_REF_V1/control/FROZEN_SPEC.json')
    refs = []
    for item in index['rows']:
        digest = item['input_identity_sha256']
        if digest not in digests:
            continue
        binding = exact(item['binding_ref'])
        need(binding['Source5_consumer_identity'] == base['source_identity'] == handoff['source_identity'], 'Source binding')
        component = exact(binding['ep_component_ref'])
        need(component['status'] == 'ACTUAL_PARSER_FULL_MEMBER_POPULATION_PASS_COMPONENT_ONLY', 'complete actual parser qualification')
        need(component['input_identity_sha256'] == digest and component['expectedcommands'] == binding['expectedcommands'], 'whole command identity')
        ordered = binding['ordered_kernel_identity']
        need(component['source_parser_sha256'] == '9545c56336c8fa25cb7af842ce6955bf4e08b41835f9cfea2dcfa9a8a5802c28', 'actual consumer Source')
        need([(m['declared_member']['member'], m['declared_member']['sha256'], m['declared_member']['bytes']) for m in component['ordered_members']] == [(m['member'], m['sha256'], m['bytes']) for m in ordered], 'all ordered members')
        exact(binding['DTC_complete_body_ref']); exact(binding['Root125_acceptance_ref'])
        need(sum(m['expected_instructions'] for m in ordered) == binding['expected_instructions'] and sum(m['expected_CTA'] for m in ordered) == binding['expected_CTA'], 'full counts')
        cmd = P(binding['trace_entry'])
        need(sha(cmd) == binding['literal_commandlist_sha256'], 'small commandlist changed')
        members = []
        for m in binding['members']:
            p = P(m['path']); st = p.stat()
            need(st.st_size == m['size'] and st.st_mtime_ns == m['mtime_ns'] and str(p.resolve()) == m['resolved_path'], 'current body storage changed')
            members.append({k:m[k] for k in ['member','path','resolved_path','size','mtime_ns','sha256']})
        need({m['member'] for m in members} == {m['member'] for m in ordered}, 'all kernel body members required')
        st = cmd.stat(); previous = binding['commandlist_current_stat']
        need(st.st_size == previous['size'] and st.st_mtime_ns == previous['mtime_ns'] and str(cmd.resolve()) == previous['resolved_path'], 'small commandlist storage changed')
        members.append(dict(member='kernelslist.g', path=str(cmd), resolved_path=str(cmd.resolve()), size=st.st_size, mtime_ns=st.st_mtime_ns, sha256=binding['literal_commandlist_sha256']))
        need({m['member'] for m in members} == {m['member'] for m in ordered} | {'kernelslist.g'}, 'all bodies plus commandlist required')
        out_binding = copy.deepcopy(binding)
        out_binding.update(schema='EP_FULL_PERF_REUSED_BODY_CURRENT_STORAGE_INPUT_BINDING_V1', goal=GOAL, qualified_by='Main', status='MAIN_REVIEWED_COMPLETE_INPUT_BINDING', members=members, original_candidate_ref=item['binding_ref'])
        input_path = ROOT/'control/inputs'/digest/'INPUT_BINDING.json'
        put(input_path, out_binding, True)
        short = re.sub('[^A-Za-z0-9]', '', binding['program']).upper()+'_'+digest[:8].upper()
        for mode in ['S','WV_ZERO_RO']:
            case = 'EP_PERF_'+short+'_'+mode+'_REF_V1'
            folder = ROOT/'cases'/case
            s = copy.deepcopy(base)
            s.update(cohort=case, program=binding['program'], input_identity_sha256=digest,
                     input_binding_ref=ref(input_path), trace_entry=str(cmd), mode=mode, T=False, M=False,
                     expected_instructions=binding['expected_instructions'], expected_CTA=binding['expected_CTA'],
                     command_count=len(binding['expectedcommands']),
                     expected_kernel_launches=[dict(uid=i+1, name=k['name'], trace_member=k['member'], command_ordinal=k['command_ordinal']) for i,k in enumerate(ordered)],
                     expected_kernel_scopes=[dict(ordinal=i+1, name=k['name'], member=k['member'], CTA=k['expected_CTA'], instructions=k['expected_instructions'], command_ordinal=k['command_ordinal']) for i,k in enumerate(ordered)],
                     all_unique_kernel_members=[dict(member=k['member'], path=k['path'], sha256=k['sha256'], size=k['bytes']) for k in ordered],
                     estimated_peak_RAM_bytes=768*M, estimated_wall_seconds=1200, ro_qualification_ref=None)
            s['limits'] = dict(RSS_bytes=2*G, AS_bytes=10*G, result_bytes=128*M, wall_seconds=24*3600)
            eligibility = dict(schema='EP_FULL_PERF_INPUT_ELIGIBILITY_V1', goal=GOAL, status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',
                input_identity_sha256=digest, source_identity=s['source_identity'], ordered_kernel_identity=ordered, program=binding['program'],
                modes_qualified=[mode], authority_scope='MAIN42_SELECTED_REPRESENTATIVE' if binding['authority42_selected'] else 'ORDINARY_EXTENSION',
                actual_EP_parser_ref=binding['ep_component_ref'], input_binding_ref=s['input_binding_ref'],
                scientific_scope='TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST', original_capture_completeness='UNKNOWN', numeric_output='UNKNOWN',
                old_application_acceptance_inherited=False, qualified_by='Main', WV_mode_CPU_ref=handoff_ref,
                T_M_applicability='DISABLED_NOT_EXERCISED', RO_coverage='NO_READONLY_CERTIFICATION')
            put(folder/'control/INPUT_ELIGIBILITY.json', eligibility, True)
            s['eligibility_ref'] = ref(folder/'control/INPUT_ELIGIBILITY.json')
            opts = copy.deepcopy(base['expected_effective_options'])
            substitutions = dict(handoff['required_effective_options'])
            if mode == 'S':
                substitutions.update({'-gpgpu_ep_l2_ft_mode':'1','-gpgpu_ep_l2_tvd_clean':'0','-gpgpu_ep_l2_tvd_dirty':'0'})
            opts.update(substitutions); opts['-trace'] = str(cmd)
            omitted = handoff['required_omitted_and_cleared_options']
            for k in omitted:
                opts[k] = 'NULL'
            configs = []
            for i,entry in enumerate(base['ordered_configs']):
                text = P(entry['path']).read_text()
                for k in omitted:
                    text = re.sub(r'(?m)^'+re.escape(k)+r'[ \t]+[^\n]*\n?', '', text)
                for k,v in substitutions.items():
                    pat = r'(?m)^'+re.escape(k)+r'[ \t]+[^\n]*$'
                    if re.search(pat, text):
                        text = re.sub(pat, k+' '+v, text)
                path = folder/'env'/('config-'+str(i)+'.config'); path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('x') as f:
                    f.write(text)
                configs.append(ref(path))
            s['ordered_configs'] = configs; s['expected_effective_options'] = opts
            s['scientific_option_contract'] = dict(mode=mode, complete_282=True, hardware_profile='REF32x8_L100',
                matched_input=digest, observer_profile='FOUR_OPTIONAL_OFF_MS_B0_M0A_ON', T_M='DISABLED_NOT_EXERCISED',
                all_RO_certificate_fields='OMITTED_DEFAULT_NULL', RO_scope='NO_READONLY_CERTIFICATION', CPU_mode_qualification_ref=handoff_ref)
            put(folder/'control/FROZEN_SPEC.json', s, True)
            refs.append(ref(folder/'control/FROZEN_SPEC.json'))
    need(len(refs) == 2*len(digests), 'all requested inputs required')
    stage = dict(schema='EP_FULL_PERF_FINITE_STAGE_V1', goal=GOAL, status='MAIN_REVIEWED_EXACT_FINITE_STAGE', stage=stage_name,
        scientific_owner='Main', maximum_new_starts=len(refs), automatic_retry=False, refund=False, source_keep=True,
        authorization_ref=ref(ROOT/'control/USER_AUTHORIZATION.json'), engine_ref=ref(ROOT/'tools/ep_perf_native.py'), common_ref=ref(ROOT/'tools/ep_perf_common.py'),
        specs=refs, resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME')
    path=ROOT/'control'/(stage_name+'.json'); put(path,stage,True)
    return dict(status='S_WV_ZERO_RO_PREPARED_ZERO_STARTS',stage_ref=ref(path),cases=[read(x['path'])['cohort'] for x in refs])


if __name__ == '__main__':
    print(json.dumps(prepare(sys.argv[1], sys.argv[3:], sys.argv[2])))
