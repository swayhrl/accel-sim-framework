"""Consume only a published fetched Y2 verdict on the exact candidate Core."""
from common import *


def main():
    ref='refs/remotes/origin/hrl/iscas2027-dtc-lane-y2-k1-requal-174-v1'
    commit=git(FW_REPO,'rev-parse',ref)
    base='docs/dtc_l1/review_packs/DTC_LANE_Y2_K1_REQUAL_V1'
    gate=git_json(FW_REPO,commit,base+'/VALIDATION_GATE_V2.json')
    assert gate['target_core']==CANDIDATE_CORE and gate['lane_v_commit']==V_SHA
    assert gate['status']!='PENDING','Y2 published verdict is still pending'
    proven=[]
    for name in ['VALIDATION_GATE_V2.json','SOURCE_BINDING.json','EXTRACTED_BODY_BINDING.json',
                 'EXPECTED_VS_OBSERVED.json','TEST_MATRIX.tsv','K0_EQUIVALENCE.md',
                 'K1_CONSERVATION.md','SOURCE_EVENT_TIMING.md','LATEST_REPORT.md',
                 'BUILD_RECEIPTS.json','TOOLCHAIN_IDENTITY.json']:
        proven.append(copy_blob(FW_REPO,commit,base+'/'+name,PACK/'inputs/Y2'/name))
    results=json.loads((PACK/'inputs/Y2/EXPECTED_VS_OBSERVED.json').read_text())
    assert results['core']==CANDIDATE_CORE
    indexed={r['id']:r for r in results['results']}
    option_checks={}
    for name,value in [('options_default','0'),('options_omitted_oo','0'),('options_off_oo','0'),('options_on_oo','1')]:
        r=indexed[name]
        option_checks[name]=r['exit_code']==0 and r['observed'].get(K_OPTION)==value
    option_checks['omitted_equals_explicit_OFF']=indexed['options_omitted_oo']['observed']==indexed['options_off_oo']['observed']
    option_checks['unknown_rejected']=indexed['options_unknown']['exit_code']==1 and indexed['options_unknown']['observed'].get('unknown_rejected') is True
    assert all(option_checks.values()),'Y2 real option proof did not match exact K option'
    accepted=gate['status']=='PASS_K1_OO_MODEL_SCOPE'
    write(PACK/'Y2_GATE_BINDING.json',dict(utc=now(),published_fetch_back_commit=commit,provenance=proven,
         target_Core=CANDIDATE_CORE,exact_option=K_OPTION,real_option_checks=option_checks,
         published_verdict=gate['status'],accepted_PASS_K1_OO_MODEL_SCOPE=accepted,
         accepted_K0_equivalence=accepted and gate.get('k0_cpu_default_off_equivalent') is True,
         K0_full_Gaussian_equivalence='NOT_RUN_REQUIRES_BOTH_NEW_K0_EXACT_CONTROLS',
         qualification_scope=gate.get('qualification_scope'),fixture_limits=gate.get('fixture_limits'),
         architectural_values=gate.get('architectural_value_correctness'),
         actual_Gaussian_source_events='NOT_MEASURED',new_full_simulator_starts=0,
         no_FAIL_CLOSED_override=True,launch_admitted=False))
    print('Bound exact published Y2 verdict:',gate['status'],'; no execution admission implied.')


if __name__=='__main__':main()
