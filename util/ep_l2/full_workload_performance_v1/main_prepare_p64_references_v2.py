"""Main-only next bounded P64 study: real matched MS0 references, no starts."""
import copy,json,sys
from pathlib import Path
J=Path('/root/data/ep_l2_full_workload_performance_20261027_v1')
sys.path.insert(0,str(J/'tools'))
from ep_perf_common import *

def main():
    hqr=ref(J/'control/HOST_QUALIFICATION_P_S64_MS0_V1.json');hq=exact(hqr)
    planref=ref(J/'control/SEARCH_PLAN_P_S64_MS0_V1.json');plan=exact(planref)
    previous=exact(ref(J/'control/P_MS0_VECTOR4M_APPLICATION_NI_RECEIPT.json'))
    need(previous['status'].endswith('PASS') or 'PASS'in previous['status'],'existing finite MS0 qualification')
    reg,unused=authority();q=reg['registered_future_requests'][GOAL];refs=[];rows=[]
    for sample in read(J/'control/SEARCH_PLAN_U_D_N_V1.json')['exploration_inputs'][1:]:
        for mode in ['S','F']:
            oldcase=sample['reference_cohorts'][mode];oldpath=J/'cases'/oldcase/'control/FROZEN_SPEC.json';base=read(oldpath)
            need(q['consumed'][oldcase]['state']=='CLOSED_ACCEPTED','exact original reference accepted')
            case='EP_PERF_'+sample['case_short']+'_'+mode+'_REF_G32_W8_P1168_MS0_V1'
            need(case not in q['admitted_specs'],'new matched observer reference only')
            folder=J/'cases'/case;s=copy.deepcopy(base)
            s.update(cohort=case,profile='REF_G_P1168_MSOFF',observer_profile_id='MS0_B0M0A1_FOUR_OFF',host_qualification_ref=hqr,validation_module_ref=hq['qualified_parameter_validation_module_ref'])
            s['expected_effective_options']['-gpgpu_ep_l2_ms_observer']='0'
            configs=[]
            for i,r in enumerate(base['ordered_configs']):
                text=Path(r['path']).read_text()
                if i==len(base['ordered_configs'])-1:text+='\n# Matched MS0 profile for separately qualified strong static S64 study.\n-gpgpu_ep_l2_ms_observer 0\n'
                p=folder/'env'/('config-'+str(i)+'.config');p.parent.mkdir(parents=True,exist_ok=True)
                if p.exists():need(p.read_text()==text,'unspent reference config differs')
                else:
                    with p.open('x')as f:f.write(text)
                configs.append(ref(p))
            s['ordered_configs']=configs
            s['scientific_option_contract']=dict(mode=mode,complete_282=True,NI_reference_spec_ref=ref(oldpath),exact_delta_from_same_mode_MS1={'-gpgpu_ep_l2_ms_observer':'0'},hardware_geometry=s['geometry'],
                observer_profile_id='MS0_B0M0A1_FOUR_OFF',physical_budget='S16 fixed1024/128/16 or F unified1168; static64 OFF in this reference stage',
                search_plan_ref=planref,source_unchanged=True,cross_observer_performance_pairing_forbidden=True)
            s['pinned_files'].update({r['path']:r['sha256']for r in hq['modules']})
            adapter=module(s['validation_module_ref'],'main_p_ms0_reference_qualify');adapter.qualify_history_spec(s)
            refs.append(put(folder/'control/FROZEN_SPEC.json',s,True));rows.append(dict(cohort=case,mode=mode,program=s['program'],input_identity_sha256=s['input_identity_sha256'],all282_delta={'-gpgpu_ep_l2_ms_observer':['1','0']}))
    stage='STAGE_P_MS0_CONV_BLACK_REFERENCE4'
    v=dict(schema='EP_FULL_PERF_FINITE_STAGE_V1',goal=GOAL,status='MAIN_REVIEWED_EXACT_FINITE_STAGE',stage=stage,scientific_owner='Main',maximum_new_starts=4,automatic_retry=False,refund=False,source_keep=True,
        authorization_ref=ref(J/'control/USER_AUTHORIZATION.json'),engine_ref=ref(J/'tools/ep_perf_native.py'),common_ref=ref(J/'tools/ep_perf_common.py'),specs=refs,resource_admission='REQUIRED_FRESH_BEFORE_EVERY_CONSUME',
        predeclared_P_plan_ref=planref,P_static64_new_starts_in_this_stage=0,next='After actual reference/NI closure, two new static64 S points; each reuses its exact real matched F MS0 identity by explicit alias, never MS1')
    sr=put(J/'control'/(stage+'.json'),v,True)
    put(J/'control'/(stage+'_PREPARATION_RECEIPT.json'),dict(status='ALL4_STRICT_P_MATH_AND_282_PROFILE_PASS_ZERO_STARTS',utc=now(),rows=rows,stage_ref=sr),True)
    print(json.dumps(dict(stage_ref=sr,model_starts=0)))

if __name__=='__main__':main()
