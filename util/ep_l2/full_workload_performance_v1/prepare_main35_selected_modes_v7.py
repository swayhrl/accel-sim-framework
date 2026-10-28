"""Main-only, finite S/WV preparation from reviewed complete input components."""
import copy, re, sys
from ep_perf_common import *

NORMALIZER_REF={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/tools/qualified_input_component_normalize_v1/normalize_ep9dd_complete_component.py', 'sha256': '6cdfee5fe9e8ab53b27ecfe7846c342e32cf4914dc2dc66e322a986934f37080'}
NORMALIZER_CPU_REF={'path': '/root/data/ep_l2_full_workload_performance_20261027_v1/agent_b/component_normalize_v1/runs/6a8d3416-919a-4540-b69b-33ef21ae4315/RESULT.json', 'sha256': 'e44f142bc0b97d935433af2faeda07052afabb29151c696a237ea5fd38321643'}



def prepare(index_path, digests, stage_name):
    index = read(index_path)
    plan = read(ROOT/'control'/(stage_name+'_PLAN.json'))
    need(plan['goal']==GOAL and plan['status']=='MAIN_REVIEWED_FINITE_REFERENCE_S_WV_PLAN','explicit per-input resource plan required')
    resource_rows={r['input_identity_sha256']:r for r in plan['inputs']}
    need(set(digests)==set(resource_rows),'plan population mismatch')
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
        binding_ref=item.get('binding_ref',item.get('InputBinding_candidate_ref'))
        binding = exact(binding_ref)
        need(binding['Source5_consumer_identity'] == base['source_identity'] == handoff['source_identity'], 'Source binding')
        component = exact(binding['ep_component_ref'])
        original_component_schema=component.get('schema')
        if original_component_schema in ['EP9DD_COMPLETE_LARGE_INPUT_COMPONENT_PROOF_V2','EP9DD_COMPLETE_REMAINING_PRIMARY_INPUT_COMPONENT_PROOF_V1']:
            normalizer=module(NORMALIZER_REF,'Main_strict_complete_component_normalizer')
            component=normalizer.normalize_input_component(binding_ref,base['source_identity'])
            need(component['status']=='STRICT_EVIDENCE_JOIN_PASS_COMPONENT_ONLY_MAIN_REVIEW_REQUIRED' and all(component['checks'].values()),'all exact component evidence joins required')
            need(component['body_reuse_reference_join']['kind']=='EXACT_SAME_BODY_PROOF_REFERENCE','domain continuation needs separate Main adjudication, excluded from this seven input stage')
        legacy=component['status']=='EXACT_PRIOR_FRAMEWORK9DD_INPUT_COMPATIBILITY_REBOUND_PENDING_MAIN_REVIEW'
        need(component['status'] in ['ACTUAL_PARSER_FULL_MEMBER_POPULATION_PASS_COMPONENT_ONLY','STRICT_EVIDENCE_JOIN_PASS_COMPONENT_ONLY_MAIN_REVIEW_REQUIRED'] or legacy,'complete actual parser qualification and exact normalized evidence')
        need(component['input_identity_sha256']==digest and component['all_declared_commands' if legacy else 'expectedcommands']==binding['expectedcommands'],'whole command identity')
        ordered=copy.deepcopy(binding['ordered_kernel_identity'])
        scopes={k['member']:k for k in binding['expected_kernel_scopes']}
        need(len(scopes)==len(ordered),'unique complete kernel scopes')
        for k in ordered:
            scope=scopes[k['member']]
            need(scope['command_ordinal']==k['command_ordinal'],'scope ordinal')
            for key,value in [('name',scope['name']),('expected_CTA',scope['CTA']),('expected_instructions',scope['instructions'])]:
                need(key not in k or k[key]==value,'identity/scope header mismatch')
                k[key]=value
            k.setdefault('path',str(P(binding['trace_entry']).parent/k['member']))
        parser_sha=component['source_parser_ref']['sha256'] if legacy else component['source_parser_sha256']
        need(parser_sha=='9545c56336c8fa25cb7af842ce6955bf4e08b41835f9cfea2dcfa9a8a5802c28','actual consumer Source')
        if legacy:
            need(all(component['checks'].values()) and not component['authority_or_semantic_hold_preserved'],'prior exact compatibility not closed')
            for r in component['evidence_refs'].values():
                need(sha(r['path'])==r['sha256'],'prior actual parser bytes changed')
            compared=component['ordered_kernel_identity']
        else:
            compared=[m['declared_member'] for m in component['ordered_members']]
        need([(m['member'],m['sha256'],m['bytes']) for m in compared]==[(m['member'],m['sha256'],m['bytes']) for m in ordered],'all ordered members')
        exact(binding['DTC_complete_body_ref']); exact(binding['Root125_acceptance_ref'])
        need(sum(m['expected_instructions'] for m in ordered) == binding['expected_instructions'] and sum(m['expected_CTA'] for m in ordered) == binding['expected_CTA'], 'full counts')
        cmd = P(binding['trace_entry'])
        need(sha(cmd) == binding['literal_commandlist_sha256'], 'small commandlist changed')
        members = []
        for m in binding['members']:
            p = P(m['path']); st = p.stat()
            need(st.st_size == m['size'] and st.st_mtime_ns == m['mtime_ns'] and str(p.resolve()) == m['resolved_path'], 'current body storage changed')
            members.append({k:m[k] for k in ['member','path','resolved_path','size','mtime_ns','sha256']})
        need({m['member'] for m in members} - {'kernelslist.g'}=={m['member'] for m in ordered},'all kernel members required')
        if 'kernelslist.g' not in {m['member'] for m in members}:
            st=cmd.stat()
            members.append(dict(member='kernelslist.g',path=str(cmd),resolved_path=str(cmd.resolve()),size=st.st_size,mtime_ns=st.st_mtime_ns,sha256=binding['literal_commandlist_sha256']))
        need({m['member'] for m in members} == {m['member'] for m in ordered} | {'kernelslist.g'}, 'all bodies plus commandlist required')
        normalized_ref=put(ROOT/'control/input_components'/digest/'NORMALIZED_COMPLETE_COMPONENT_JOIN_V1.json',component,True)
        out_binding = copy.deepcopy(binding)
        out_binding['Main_normalized_component_join_ref']=normalized_ref
        out_binding['Main_component_normalizer_ref']=NORMALIZER_REF
        out_binding.update(schema='EP_FULL_PERF_REUSED_BODY_CURRENT_STORAGE_INPUT_BINDING_V1',goal=GOAL,qualified_by='Main',status='MAIN_REVIEWED_COMPLETE_INPUT_BINDING',members=members,ordered_kernel_identity=ordered,original_candidate_ref=binding_ref)
        input_path=ROOT/'control/inputs'/digest/'INPUT_BINDING_V5.json'
        put(input_path, out_binding, True)
        short = re.sub('[^A-Za-z0-9]', '', binding['program']).upper()+'_'+digest[:8].upper()
        for mode in resource_rows[digest]['modes']:
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
                     estimated_peak_RAM_bytes=resource_rows[digest]['estimated_peak_RAM_bytes'],estimated_wall_seconds=resource_rows[digest]['estimated_wall_seconds'],ro_qualification_ref=None)
            s['limits']=resource_rows[digest]['limits']
            s['host_input_specific_resource_plan_ref']=ref(ROOT/'control'/(stage_name+'_PLAN.json'))
            hostq=exact(plan['host_qualification_ref'])
            s.update(host_qualification_ref=plan['host_qualification_ref'],validation_module_ref=hostq['qualified_parameter_validation_module_ref'],
                helpers_ref=ref(ROOT/'tools/qualified_geometry_queue_v1/host_scaling/dynamic_observation_scaled.py'))
            s['pinned_files'].update({r['path']:r['sha256'] for r in hostq['modules']})
            s['pinned_files'][NORMALIZER_REF['path']]=NORMALIZER_REF['sha256']
            s['pinned_files'][normalized_ref['path']]=normalized_ref['sha256']
            eligibility = dict(schema='EP_FULL_PERF_INPUT_ELIGIBILITY_V1', goal=GOAL, status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',
                input_identity_sha256=digest, source_identity=s['source_identity'], ordered_kernel_identity=ordered, program=binding['program'],
                modes_qualified=[mode],authority_scope='MAIN42_SELECTED_REPRESENTATIVE',
                actual_EP_parser_ref=binding['ep_component_ref'], input_binding_ref=s['input_binding_ref'],
                scientific_scope='TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST', original_capture_completeness='UNKNOWN', numeric_output='UNKNOWN',
                old_application_acceptance_inherited=False, qualified_by='Main', WV_mode_CPU_ref=handoff_ref,
                T_M_applicability='DISABLED_NOT_EXERCISED', RO_coverage='NO_READONLY_CERTIFICATION')
            eligibility.update(full_input_RO_population='UNKNOWN_UNLESS_SEPARATELY_CERTIFIED',component_evidence_type='PRIOR_EXACT_REBIND_NOT_NEW_BODY_SCAN' if legacy else 'ACTUAL_NEW_FULL_CONSUMER_COMPONENT',
                master_ref=ref(index_path),per_input_resource_plan_ref=ref(ROOT/'control'/(stage_name+'_PLAN.json')))
            eligibility.update(Main_normalized_component_join_ref=normalized_ref,Main_component_normalizer_ref=NORMALIZER_REF,component_normalizer_CPU_ref=NORMALIZER_CPU_REF,original_component_schema_preserved=original_component_schema)
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
    need(len(refs) == sum(len(r['modes']) for r in resource_rows.values()), 'all requested finite input/mode combinations required')
    stage = dict(schema='EP_FULL_PERF_FINITE_STAGE_V1', goal=GOAL, status='MAIN_REVIEWED_EXACT_FINITE_STAGE', stage=stage_name,
        scientific_owner='Main', maximum_new_starts=len(refs), automatic_retry=False, refund=False, source_keep=True,
        authorization_ref=ref(ROOT/'control/USER_AUTHORIZATION.json'), engine_ref=ref(ROOT/'tools/ep_perf_native.py'), common_ref=ref(ROOT/'tools/ep_perf_common.py'),
        specs=refs, resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME')
    path=ROOT/'control'/(stage_name+'.json'); put(path,stage,True)
    return dict(status='S_WV_ZERO_RO_PREPARED_ZERO_STARTS',stage_ref=ref(path),cases=[read(x['path'])['cohort'] for x in refs])


if __name__ == '__main__':
    print(json.dumps(prepare(sys.argv[1], sys.argv[3:], sys.argv[2])))
