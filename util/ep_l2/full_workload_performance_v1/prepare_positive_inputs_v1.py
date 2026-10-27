"""Main-only preparation for newly parser-qualified positive-RO inputs. Zero starts."""
import copy, json, pathlib, re, sys
from ep_perf_common import *

OLD=P('/root/data/ep_l2_multiworkload_event_timeline_20261027_v1')


def prepare(handoff_path, requested_ids, stage_name):
    handoff=read(handoff_path)
    corpus=read(ROOT/'agent_a/all_coverage/SM70_125_COMPLETE_INPUT_AND_RO_SCOPE_MAP.json')
    base=read(ROOT/'cases/EP_PERF_VECTOR4M_S_REF_V1/control/FROZEN_SPEC.json')
    f_template=read(OLD/'cases/EP_MULTI_VECTOR_F_ET0_20261027_V1/control/FROZEN_SPEC.json')
    refs=[]
    for new in handoff['rows']:
        digest=new['input_identity_sha256']
        if digest not in requested_ids:
            continue
        matches=[r for r in corpus['rows'] if r['full_command_identity_sha256']==digest]
        need(matches,'new positive input absent from fixed ordinary population')
        selected=[r for r in matches if r['main42_selected']]
        row=selected[0] if selected else matches[0]
        need(not row['hold_or_missing'],'input still has unresolved capture/semantics '+repr(row['hold_or_missing']))
        original_component_ref=new['exact_whole_input_component_ref']
        component=exact(original_component_ref)
        component_ref=original_component_ref
        if component['status']!='ACTUAL_PARSER_FULL_MEMBER_POPULATION_PASS_COMPONENT_ONLY':
            normalized_index=exact(dict(path=str(ROOT/'agent_c/parser_expansion/completed_proofs_20261027T151825Z/INDEX.json'),
                                        sha256='81150c8d52dc768b96be5ee6e9f04b771d6d78fb6a93e95be25c4158dbba56af'))
            item=normalized_index['rows'][digest]
            component_ref=dict(path=item['path'],sha256=item['sha256'])
            component=exact(component_ref)
        need(component['status']=='ACTUAL_PARSER_FULL_MEMBER_POPULATION_PASS_COMPONENT_ONLY','actual complete parser component missing')
        need(component['input_identity_sha256']==digest and component['expectedcommands']==row['ordered_commands'],'component/whole command identity')
        need(component['source_parser_sha256']=='9545c56336c8fa25cb7af842ce6955bf4e08b41835f9cfea2dcfa9a8a5802c28','different parser source')
        need(component['reference_DTC_body_SHA_proof']['expected_instructions']==row['expected_instructions'] and component['reference_DTC_body_SHA_proof']['expected_CTA']==row['expected_CTA'],'complete reference counts')
        derivation=exact(new['derivation_ref'])
        scope=exact(new['input_scope_ref'])
        loader=exact(new['loader_ref'])
        need(new['source_identity']==base['source_identity'] and new['certified_RO_lines']>0,'positive same-source certificate')
        for key in ['manifest_ref','ranges_ref']:
            need(sha(new[key]['path'])==new[key]['sha256'],'new certificate bytes changed')
        need(loader['source_identity']==base['source_identity'],'loader Source mismatch')
        # Require a true positive production loader execution; statuses are kept in the receipt.
        tests=loader.get('tests',[])
        need(tests and any(t.get('returncode')==0 for t in tests) and all(t.get('PASS',t.get('pass',False)) for t in tests),'production loader positive/negative controls incomplete')
        ordered=row['ordered_kernel_identity']
        declared=[m['declared_member'] for m in component['ordered_members']]
        need([(m['member'],m['sha256'],m['bytes'])for m in declared]==[(m['member'],m['sha256'],m['bytes'])for m in ordered],'all ordered kernel bodies/ordinal closure')
        before_by_path={m['path']:m for m in derivation['body_passes']}
        members=[]
        cmd=P(row['canonical_genuine164_trace_entry'])
        for name,size,dig in [('kernelslist.g',cmd.stat().st_size,row['literal_commandlist_sha256'])]+[(m['member'],m['bytes'],m['sha256'])for m in ordered]:
            path=cmd.parent/name
            st=path.stat()
            need(st.st_size==size,'member byte count mismatch')
            if name!='kernelslist.g':
                proof=before_by_path[str(path)]
                need(proof['fd_stat_before']==proof['fd_stat_after'] and st.st_size==proof['fd_stat_after']['size'] and st.st_mtime_ns==proof['fd_stat_after']['mtime_ns'],'same descriptor storage changed after RO pass')
                need(proof['existing_attested_body_SHA256']==dig,'RO body proof SHA differs')
            members.append(dict(member=name,path=str(path),resolved_path=str(path.resolve()),size=size,mtime_ns=st.st_mtime_ns,sha256=dig))
        need(sha(cmd)==row['literal_commandlist_sha256'],'small commandlist changed')
        binding=dict(schema='EP_FULL_PERF_REUSED_BODY_CURRENT_STORAGE_INPUT_BINDING_V1',goal=GOAL,
                     input_identity_sha256=digest,literal_commandlist_sha256=row['literal_commandlist_sha256'],
                     expectedcommands=row['ordered_commands'],ordered_kernel_identity=ordered,members=members,
                     program=row['program'],trace_entry=str(cmd),reference_DTC_body_proof=component['reference_DTC_body_SHA_proof'],
                     actual_EP_component_ref=component_ref,original_RO_component_ref=original_component_ref,RO_current_fd_stat_ref=new['derivation_ref'],
                     Root125_acceptance_ref=new['Root125_acceptance_ref'],body_freshly_rehashed=False,
                     original_capture_completeness='UNKNOWN',numeric_output='UNKNOWN')
        input_root=ROOT/'control/inputs'/digest
        put(input_root/'INPUT_BINDING.json',binding,True)
        short='VECTOR6M' if row['program']=='vectorAdd' else re.sub('[^A-Za-z0-9]','',row['program']).upper()+'_'+digest[:8].upper()
        for mode in ['S','F']:
            case='EP_PERF_'+short+'_'+mode+'_REF_V1'
            folder=ROOT/'cases'/case
            s=copy.deepcopy(base)
            s.update(cohort=case,program=row['program'],input_identity_sha256=digest,input_binding_ref=ref(input_root/'INPUT_BINDING.json'),trace_entry=str(cmd),mode=mode,T=mode=='F',M=mode=='F',
                     expected_instructions=row['expected_instructions'],expected_CTA=row['expected_CTA'],
                     expected_kernel_launches=[dict(uid=i+1,name=k['name'],trace_member=k['member'],command_ordinal=k['command_ordinal'])for i,k in enumerate(declared)],
                     expected_kernel_scopes=[dict(ordinal=i+1,member=k['member'],name=k['name'],CTA=k['expected_CTA'],instructions=k['expected_instructions'],command_ordinal=k['command_ordinal'])for i,k in enumerate(declared)],
                     command_count=len(row['ordered_commands']),all_unique_kernel_members=[dict(member=k['member'],path=k['path'],sha256=k['sha256'],size=k['bytes'])for k in declared],
                     estimated_peak_RAM_bytes=768*M,estimated_wall_seconds=900 if row['program']=='vectorAdd' else 240)
            s['limits']=dict(RSS_bytes=2*G,AS_bytes=10*G,result_bytes=128*M,wall_seconds=24*3600)
            eligibility=dict(schema='EP_FULL_PERF_INPUT_ELIGIBILITY_V1',goal=GOAL,status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',
                 input_identity_sha256=digest,source_identity=s['source_identity'],ordered_kernel_identity=ordered,program=row['program'],
                 modes_qualified=[mode],authority_scope='MAIN42_SELECTED_REPRESENTATIVE' if row['main42_selected']else'ORDINARY_EXTENSION',
                 authority_ref=scope['authority42_ref'],actual_EP_parser_ref=component_ref,
                 input_binding_ref=s['input_binding_ref'],scientific_scope='TRACE_DEFINED_COMPLETE_DECLARED_COMMANDLIST',original_capture_completeness='UNKNOWN',
                 numeric_output='UNKNOWN',old_application_acceptance_inherited=False,qualified_by='Main')
            put(folder/'control/INPUT_ELIGIBILITY.json',eligibility,True)
            s['eligibility_ref']=ref(folder/'control/INPUT_ELIGIBILITY.json')
            substitutions={}
            if mode=='F':
                cert=dict(schema='EP_FULL_PERF_POSITIVE_RO_QUALIFICATION_V1',status='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED',goal=GOAL,
                    input_identity_sha256=digest,source_identity=s['source_identity'],manifest_ref=new['manifest_ref'],ranges_ref=new['ranges_ref'],
                    actual_loader_proof_ref=new['loader_ref'],exact_scope_binding_ref=new['input_scope_ref'],whole_epoch_derivation_ref=new['derivation_ref'],
                    scope='TRACE_MODEL_CLOSED_WORLD',epoch='whole_commandlist',line_bytes=128,address_domain='CANONICAL_GPU_GLOBAL_VA_NO_TRANSLATION_ALIAS',
                    qualified_by='Main',application_acceptance_granted=False)
                put(folder/'control/RO_QUALIFICATION.json',cert,True)
                s['ro_qualification_ref']=ref(folder/'control/RO_QUALIFICATION.json')
                for kind in ['manifest','ranges']:
                    substitutions['-gpgpu_ep_l2_ro_'+kind]=new[kind+'_ref']['path']
                    substitutions['-gpgpu_ep_l2_ro_'+kind+'_sha256']=new[kind+'_ref']['sha256']
            else:
                s['ro_qualification_ref']=None
            config_template=f_template if mode=='F' else base
            options=copy.deepcopy(config_template['expected_effective_options'])
            options['-trace']=str(cmd)
            options.update(substitutions)
            configs=[]
            for i,entry in enumerate(config_template['ordered_configs']):
                text=P(entry['path']).read_text()
                if i==3:
                    for key,value in substitutions.items():
                        pattern=r'(?m)^'+re.escape(key)+r'[ \t]+[^\n]*$'
                        need(len(re.findall(pattern,text))==1,'exact RO option not unique')
                        text=re.sub(pattern,key+' '+value,text)
                out=folder/'env'/('config-'+str(i)+'.config')
                out.parent.mkdir(parents=True,exist_ok=True)
                out.write_text(text)
                configs.append(ref(out))
            s['ordered_configs']=configs
            s['expected_effective_options']=options
            s['scientific_option_contract']=dict(mode=mode,complete_282=True,hardware_profile='REF32x8_L100',
                matched_input=digest,observer_profile='FOUR_OPTIONAL_OFF_MS_B0_M0A_ON',
                physical_budget='1168 modeled128B slots/slice; Tag2MiB GPU; metadata/area explicitly separate')
            put(folder/'control/FROZEN_SPEC.json',s,True)
            refs.append(ref(folder/'control/FROZEN_SPEC.json'))
    need(len(refs)==2*len(requested_ids),'not all requested positive inputs prepared')
    stage=dict(schema='EP_FULL_PERF_FINITE_STAGE_V1',goal=GOAL,status='MAIN_REVIEWED_EXACT_FINITE_STAGE',stage=stage_name,
         scientific_owner='Main',maximum_new_starts=len(refs),automatic_retry=False,refund=False,source_keep=True,
         authorization_ref=ref(ROOT/'control/USER_AUTHORIZATION.json'),engine_ref=ref(ROOT/'tools/ep_perf_native.py'),
         common_ref=ref(ROOT/'tools/ep_perf_common.py'),specs=refs,resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME')
    path=ROOT/'control'/(stage_name+'.json')
    put(path,stage,True)
    return dict(status='NEW_POSITIVE_INPUTS_PREPARED_ZERO_STARTS',stage_ref=ref(path),cases=[read(x['path'])['cohort']for x in refs])


if __name__=='__main__':
    need(len(sys.argv)>=4,'handoff stage_name input_digest...')
    print(json.dumps(prepare(sys.argv[1],sys.argv[3:],sys.argv[2])))
