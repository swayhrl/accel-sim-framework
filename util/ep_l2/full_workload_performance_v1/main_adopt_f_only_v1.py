"""Main-only adoption of exact, independently reviewed positive-RO F-only drafts.

No registry write or simulator start. All files created exclusively.
"""
import copy, json, shutil, sys
from pathlib import Path
J = Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0, str(J/'tools'))
from ep_perf_common import *

FORMAL = {'-gpgpu_ep_l2_ft_mode':'2', '-gpgpu_ep_l2_ro_line_mshr_bypass':'1',
          '-gpgpu_ep_l2_ro_tag_detach':'1', '-gpgpu_ep_l2_tvd_clean':'1',
          '-gpgpu_ep_l2_tvd_dirty':'1', '-gpgpu_ep_l2_ro_scope':'TRACE_MODEL_CLOSED_WORLD'}
FORMAL_KEYS=set(FORMAL)|{'-gpgpu_ep_l2_ro_'+k for k in ['manifest','ranges','manifest_sha256','ranges_sha256']}

def prepare(manifest_path, stage_name):
    mr=ref(manifest_path); m=exact(mr)
    reg,unused=authority(); q=reg['registered_future_requests'][GOAL]
    refs=[]; reviews=[]
    for row in m['rows']:
        s=copy.deepcopy(exact(row['draft_ref'])); case=s['cohort']
        need(case==row['case'] and s['mode']=='F' and s['T'] and s['M'],'full F only')
        need(case not in q['admitted_specs'] and not (J/'cases'/case).exists(),'new cohort only')
        paired=row['paired_S']; base=exact(paired['spec_ref'])
        need(q['admitted_specs'][base['cohort']]==paired['spec_ref']['sha256'],'actual registered S')
        need(base['mode']=='S' and s['source_identity']==base['source_identity'] and s['input_identity_sha256']==base['input_identity_sha256'],'same input Source')
        for key in ['limits','estimated_peak_RAM_bytes','observer_env','geometry','trace_entry','input_binding_ref','expected_instructions','expected_CTA','expected_kernel_scopes','binary_path','static_library_path']:
            need(s[key]==base[key], 'F changes unrelated S field '+key)
        opts=s['expected_effective_options']; bo=base['expected_effective_options']
        need(len(opts)==len(bo)==282 and set(opts)==set(bo),'all 282 keys')
        delta={k:[bo[k],opts[k]] for k in opts if bo[k]!=opts[k]}
        need(set(delta)<=FORMAL_KEYS and all(opts[k]==v for k,v in FORMAL.items()),'only exact mode/certificate delta')
        cert=copy.deepcopy(exact(s['ro_qualification_ref'])); elig=copy.deepcopy(exact(s['eligibility_ref']))
        need(cert['status']=='DRAFT_EXACT_WHOLE_COMMANDLIST_RO_MAIN_REVIEW_REQUIRED','unsigned RO draft expected')
        need(cert['source_identity']==s['source_identity'] and cert['input_identity_sha256']==s['input_identity_sha256'],'RO source/input')
        need(cert['epoch']=='whole_commandlist' and cert['line_bytes']==128 and cert['scope']=='TRACE_MODEL_CLOSED_WORLD','RO safety scope')
        loader=exact(cert['actual_loader_proof_ref']); derivation=exact(cert['whole_epoch_derivation_ref']); scope=exact(cert['exact_scope_binding_ref'])
        need(loader['status']=='ACTUAL_SOURCE78_POSITIVE_AND2_NEGATIVE_CPU_PASS_NOT_APPLICATION_ACCEPTED','real loader controls')
        need(loader['source_identity']==s['source_identity'] and loader['input_identity_sha256']==s['input_identity_sha256'] and loader['certified_lines']>0,'positive actual loader identity')
        for kind in ['manifest','ranges']:
            r=cert[kind+'_ref']; exact(r) if kind=='manifest' else need(sha(r['path'])==r['sha256'],'ranges SHA')
            need(loader[kind+'_ref']==r and opts['-gpgpu_ep_l2_ro_'+kind]==r['path'] and opts['-gpgpu_ep_l2_ro_'+kind+'_sha256']==r['sha256'],'certificate config exact')
        ib=exact(s['input_binding_ref'])
        need(scope['input_identity_sha256']==s['input_identity_sha256'] and scope['commands']==ib['expectedcommands'],'whole ordered command scope')
        need(scope['source_identity']==s['source_identity'],'scope Source')
        need([(r['member'],r['sha256'],r['bytes']) for r in scope['members']]==[(r['member'],r['sha256'],r['bytes']) for r in ib['ordered_kernel_identity']],'scope full ordered members')
        for r in ib['members']:
            p=Path(r['path']); st=p.stat()
            need(st.st_size==r['size'] and st.st_mtime_ns==r['mtime_ns'] and str(p.resolve())==r['resolved_path'],'current real164 member stat')
        need(len(derivation['body_passes'])==len(scope['members']) and all(r['pass_count']==1 and not r['new_body_SHA'] and r['fd_stat_before']==r['fd_stat_after'] for r in derivation['body_passes']),'one complete stable derivation')
        # Main signs new official files; private evidence stays untouched.
        folder=J/'cases'/case
        cert.update(status='EXACT_WHOLE_COMMANDLIST_RO_SOURCE_LOADER_QUALIFIED',qualified_by='Main')
        cr=put(folder/'control/RO_QUALIFICATION.json',cert,True)
        elig.update(status='MAIN_REVIEWED_EP_COMPLETE_INPUT_ELIGIBLE',qualified_by='Main',modes_qualified=['F'],
                    T_M_applicability='ENABLED_EXACT_POSITIVE_RO_CERTIFICATE',full_input_RO_population='POSITIVE_EXACT_WHOLE_EPOCH',
                    new_F_exact_certificate_ref=cr,draft_review_ref=mr)
        need(elig['ordered_kernel_identity']==ib['ordered_kernel_identity'],'eligibility full member identity')
        er=put(folder/'control/INPUT_ELIGIBILITY.json',elig,True)
        oldrefs=[s['ro_qualification_ref'],s['eligibility_ref']]
        s.update(ro_qualification_ref=cr,eligibility_ref=er)
        for r in oldrefs:s['pinned_files'].pop(r['path'],None)
        for r in [cr,er]:s['pinned_files'][r['path']]=r['sha256']
        configs=[]
        for i,r in enumerate(s['ordered_configs']):
            p=folder/'env'/('config-'+str(i)+'.config');p.parent.mkdir(parents=True,exist_ok=True)
            with p.open('xb') as out:out.write(Path(r['path']).read_bytes())
            need(sha(p)==r['sha256'],'config byte copy');configs.append(ref(p))
        s['ordered_configs']=configs
        s['scientific_option_contract'].update(draft_only_no_source_or_S_model_rerun=False,Main_draft_review_ref=mr,
            S_acceptance_required_before_performance_pairing=True,new_S_starts=0)
        for path,digest in s['pinned_files'].items():need(sha(path)==digest,'final pin '+path)
        adapter=module(s['validation_module_ref'],'adopt_F_only_math')
        adapter.qualify_history_spec(s)
        sr=put(folder/'control/FROZEN_SPEC.json',s,True);refs.append(sr)
        reviews.append(dict(cohort=case,paired_S=base['cohort'],actual_282_delta=delta,positive_RO_lines=loader['certified_lines'],
            RO_qualification_ref=cr,eligibility_ref=er,spec_ref=sr,current_S_state=q['consumed'].get(base['cohort'],{}).get('state','REGISTERED_UNSPENT'),
            no_new_S_start=True,validation='MAIN_IDENTITY_COMMAND_SCOPE_STAT_LOADER_ALL282_AND_STRICT_MATH_PASS'))
    need(len(refs)==m['maximum_new_starts_if_Main_authorizes'],'exact bounded population')
    stage=dict(schema='EP_FULL_PERF_FINITE_STAGE_V1',goal=GOAL,status='MAIN_REVIEWED_EXACT_FINITE_STAGE',stage=stage_name,scientific_owner='Main',maximum_new_starts=len(refs),automatic_retry=False,refund=False,source_keep=True,authorization_ref=ref(J/'control/USER_AUTHORIZATION.json'),engine_ref=ref(J/'tools/ep_perf_native.py'),common_ref=ref(J/'tools/ep_perf_common.py'),specs=refs,resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME',Main_signed_private_draft_manifest_ref=mr,duplicated_S_models=0)
    stage_ref=put(J/'control'/(stage_name+'.json'),stage,True)
    receipt=put(J/'control'/(stage_name+'_MAIN_ADOPTION_RECEIPT.json'),dict(utc=now(),status='MAIN_ALL_ROWS_REVIEWED_STRICT_MATH_PASS_ZERO_STARTS',helper_ref=ref(__file__),stage_ref=stage_ref,rows=reviews,science_starts=0),True)
    return dict(stage_ref=stage_ref,receipt_ref=receipt)

if __name__=='__main__': print(json.dumps(prepare(sys.argv[1],sys.argv[2])))
