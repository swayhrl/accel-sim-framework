"""Main-only exact two-point Source92 default P1 application NI preparation.

No registry/model operations; successful CPU gates precede frozen specs.
"""
import copy,json,sys
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0,str(J/'tools'))
from ep_perf_common import *

def main():
    sqref=ref(J/'control/SOURCE_QUALIFICATION_SOURCE92_P1P2_V1.json');sq=exact(sqref)
    er=ref(J/'tools/ep_perf_native_source92_v1.py');engine=module(er,'main_source92_new_engine_control')
    vr=ref(J/'tools/qualified_source92_p1p2_v1/source92_p1p2_terminal.py');validator=module(vr,'main_source92_new_math_control')
    producer=exact(sq['evidence_refs']['producer']); loader_ref=read(J/'control/SOURCE92_VECTOR_RO_CPU_RESULT_REF.json');loader=exact(loader_ref)
    need(loader['source_identity']==sq['source_identity'] and all(x['PASS'] for x in loader['checks']),'new exact Vector loader qualification')
    source_root=Path(producer['binary_path']).parents[1]
    reg,unused=authority();q=reg['registered_future_requests'][GOAL]
    drafts=[];checks=[]
    for mode in ['S','F']:
        oldcase='EP_PERF_VECTOR4M_'+mode+'_REF_V1';case='EP_PERF_VECTOR4M_'+mode+'_SOURCE92_P1_NI_V1'
        need(q['consumed'][oldcase]['state']=='CLOSED_ACCEPTED' and case not in q['admitted_specs'],'accepted old reference and new case')
        oldpath=J/'cases'/oldcase/'control/FROZEN_SPEC.json';s=copy.deepcopy(read(oldpath))
        s.update(cohort=case,profile='SOURCE92_P1_APPLICATION_NI',source_identity=sq['source_identity'],source_qualification_ref=sqref,
                 binary_path=producer['binary_path'],static_library_path=producer['static_library_path'],source_worktrees=dict(core=str(source_root/'core'),framework=str(source_root/'framework')),
                 host_engine_ref=er,validation_module_ref=vr,source92_P1_application_NI_ref=None,old_application_acceptance_inherited=False)
        folder=J/'cases'/case
        b=copy.deepcopy(exact(s['input_binding_ref']));b.update(Source5_consumer_identity=sq['source_identity'],exact_same_Framework_decoder_rebind_from_Source78_ref=s['input_binding_ref'],
            rebind_basis='Framework9dd/vendorf90 unchanged; actual consumer body component and all ordered hashes/counts reused, no new capture completeness claim',qualified_by='EP-MAIN')
        br=put(folder/'control/INPUT_BINDING_SOURCE92.json',b,True);s['input_binding_ref']=dict(path=br['path'],sha256=br['sha256'])
        eligible=copy.deepcopy(exact(s['eligibility_ref']));eligible.update(source_identity=sq['source_identity'],input_binding_ref=s['input_binding_ref'],qualified_by='EP-MAIN',
            old_source_eligibility_ref=s['eligibility_ref'],new_source_CPU_qualification_ref=sqref,application_acceptance_granted=False,old_application_acceptance_inherited=False)
        egr=put(folder/'control/INPUT_ELIGIBILITY.json',eligible,True);s['eligibility_ref']=dict(path=egr['path'],sha256=egr['sha256'])
        if mode=='F':
            oldro=s['ro_qualification_ref'];ro=copy.deepcopy(exact(oldro))
            need(loader['manifest_ref']==ro['manifest_ref'] and loader['ranges_ref']==ro['ranges_ref'] and loader['input_identity_sha256']==s['input_identity_sha256'],'actual new source loaded exact unchanged RO bytes and input')
            ro.update(source_identity=sq['source_identity'],qualified_by='EP-MAIN',actual_loader_proof_ref=loader_ref,source78_readonly_whole_commandlist_facts_ref=oldro,
                rebind_scope='same exact commands, 128B lines and readonly ranges; new Source92 actual positive/badSHA/badcommandpopulation checks; no body rescan or old app inheritance')
            rr=put(folder/'control/RO_QUALIFICATION.json',ro,True);s['ro_qualification_ref']=dict(path=rr['path'],sha256=rr['sha256'])
        configs=[]
        for i,r in enumerate(s['ordered_configs']):
            p=folder/'env'/('config-'+str(i)+'.config');p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as f:f.write(Path(r['path']).read_bytes())
            need(sha(p)==r['sha256'],'unchanged default config byte copy');configs.append(ref(p))
        s['ordered_configs']=configs
        s['scientific_option_contract']=dict(mode=mode,complete_282=True,old_source_engineering_NI_reference_spec_ref=ref(oldpath),old_source_engineering_NI_reference_point_ref=q['consumed'][oldcase]['accepted_point_ref'],
            old_new_comparison_purpose='DEFAULT_P1_APPLICATION_NONINTERFERENCE_ONLY_NOT_CROSS_ELF_PERFORMANCE_PAIRING',new_Source92_S_F_same_ELF=True,observer_and_hardware_option_delta={},
            performance_expansion_requires_actual_S_and_F_application_NI=True,source_release_ref=sq['evidence_refs']['source_release'])
        validator.qualify_history_spec(s);validator.qualify_sourceq(s,sqref['path'],sqref['sha256']);engine.qualify_new_source(s,sq)
        checks.append(dict(check='POSITIVE_EXACT_DEFAULT_P1_'+mode,PASS=True))
        drafts.append(s)
    def reject(label,s,src=sq):
        try:engine.qualify_new_source(s,src)
        except (ValueError,RuntimeError,KeyError,FileNotFoundError) as e:checks.append(dict(check=label,PASS=True,rejected_reason=str(e)));return
        raise RuntimeError('negative accepted: '+label)
    bad=copy.deepcopy(drafts[0]);bad['expected_effective_options']['-dram_latency']='101';reject('UNQUALIFIED_DRAM_CHANGE',bad)
    bad=copy.deepcopy(drafts[0]);bad['source_identity']['core_source_commit']='78f4b59e865b136eede74df74c44c210f5b4ca04';reject('OLD_SOURCE_SUBSTITUTION',bad)
    bad=copy.deepcopy(drafts[0]);bad['profile']='SOURCE92_P2_PERFORMANCE';bad['expected_effective_options']['-gpgpu_ep_l2_bank_ops']='2';reject('P2_BEFORE_APPLICATION_NI',bad)
    bad=copy.deepcopy(drafts[0]);bad['cohort']='EP_PERF_UNAUTHORIZED_P1_INITIAL_V1';reject('EXPANDED_INITIAL_NI_POPULATION',bad)
    bad=copy.deepcopy(drafts[1]);bad['observer_env']['EP_L2_EVENT_TIMELINE']='1';reject('ET_NOT_GLOBALLY_CLOCK_QUALIFIED',bad)
    bad=copy.deepcopy(drafts[1]);bad['geometry']['ways']=4;reject('UNQUALIFIED_SMALLER_GEOMETRY',bad)
    # Legacy spec_for must retain its exact source78/runtime/ref contract.
    old_engine=module(ref(J/'tools/ep_perf_native.py'),'main_legacy_engine_regression')
    for mode in ['S','F']:
        oldcase='EP_PERF_VECTOR4M_'+mode+'_REF_V1';need(old_engine.spec_for(oldcase)==read(J/'cases'/oldcase/'control/FROZEN_SPEC.json'),'old runtime Source78 spec unchanged')
        checks.append(dict(check='FROZEN_SOURCE78_'+mode+'_ENGINE_STILL_EXACT',PASS=True))
    receipt=put(J/'control/SOURCE92_NATIVE_BRIDGE_CPU_CONTROLS_V1.json',dict(status='MAIN_PURE_SOURCE92_BRIDGE_AND_UNCHANGED_SOURCE78_CONTROLS_PASS_NO_APPLICATION',utc=now(),engine_ref=er,adapter_ref=vr,
        SourceQ_ref=sqref,checks=checks,full_model_starts=0,registry_writes=0,source_keep=True),True)
    oldhq=read(J/'control/HOST_QUALIFICATION_GEOMETRY_QUEUE_V1.json');paths={r['path'] for r in oldhq['modules']}
    paths.add(er['path'])
    paths.update(str(p) for p in (J/'tools/qualified_source92_p1p2_v1').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    hq=dict(schema='EP_FULL_PERF_HOST_QUALIFICATION_V1',goal=GOAL,status='HOST_CPU_ENGINEERING_QUALIFIED_NOT_APPLICATION_ACCEPTED',qualified_by='EP-MAIN',utc=now(),
        modules=[ref(p) for p in sorted(paths)],exact_source_identity=sq['source_identity'],qualified_parameter_validation_module_ref=vr,
        Main_review='New immutable native engine version for Source92 only. All original consume/admission/syscall/terminal/archive code unchanged; strict SourceQ and P1 NI-first gate. Both P1 NI modes use complete same282 as accepted old default, new same ELF; SourceCPU never implies app permission.',
        original_host_qualification_ref=ref(J/'control/HOST_QUALIFICATION_GEOMETRY_QUEUE_V1.json'),new_SourceQ_ref=sqref,CPU_bridge_controls_ref=receipt,
        host_math_delivery_ref=ref(J/'agent_b/source92_p1p2_math_v1/DELIVERY_MANIFEST.json'),actual_vector_new_loader_ref=loader_ref,
        application_acceptance_inherited=False,scientific_acceptance_granted=False,initial_new_application_qualification='PENDING_FINITE_FRESH_REGISTERED_P1_S_F_NI')
    hqr=put(J/'control/HOST_QUALIFICATION_SOURCE92_P1P2_V1.json',hq,True)
    refs=[]
    for s in drafts:
        s['host_qualification_ref']=dict(path=hqr['path'],sha256=hqr['sha256'])
        s['pinned_files'].update({r['path']:r['sha256'] for r in hq['modules']})
        for key in ['eligibility_ref','source_qualification_ref','input_binding_ref','ro_qualification_ref']:
            r=s.get(key)
            if r:s['pinned_files'][r['path']]=r['sha256']
        for p,d in s['pinned_files'].items():need(sha(p)==d,'final host/spec pin changed')
        validator.qualify_history_spec(s);engine.qualify_new_source(s,sq)
        refs.append(put(J/'cases'/s['cohort']/'control/FROZEN_SPEC.json',s,True))
    stage='STAGE_SOURCE92_P1_VECTOR4M_APPLICATION_NI'
    st=dict(schema='EP_FULL_PERF_FINITE_STAGE_V1',goal=GOAL,status='MAIN_REVIEWED_EXACT_FINITE_STAGE',stage=stage,scientific_owner='Main',maximum_new_starts=2,automatic_retry=False,refund=False,source_keep=True,
        authorization_ref=ref(J/'control/USER_AUTHORIZATION.json'),engine_ref=er,common_ref=ref(J/'tools/ep_perf_common.py'),specs=refs,resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME',
        SourceQ_ref=sqref,host_qualification_ref=hqr,P2_starts_authorized_by_this_stage=0,design='New Source92 P1 default same282 S/F; first independently archived application endpoints then finite actual protocol NI receipt required before P2 expansion')
    sr=put(J/'control'/(stage+'.json'),st,True)
    print(json.dumps(dict(stage_ref=sr,HostQ_ref=hqr,pure_CPU_checks=len(checks),application_starts=0)))

if __name__=='__main__':main()
