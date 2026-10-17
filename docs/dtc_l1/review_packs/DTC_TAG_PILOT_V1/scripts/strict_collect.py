"""Extend the frozen collector with declared Tag options and ordered CPU proofs."""
import argparse
import math
from common import *


def strict(run, spec):
    base = old_collector().collect(run)
    if base['status']=='RUNNING':
        return dict(status='RUNNING',attempt_uuid=spec['attempt_uuid'],base=base)
    text=(run/'simulator.stdout').read_text(errors='replace')
    options_actual=echo_options(text)
    checks=json.loads(base['scientific_checks'])
    checks['preregistered_uuid']=base['attempt_uuid']==spec['attempt_uuid']
    checks['source_core_header']='gpgpu-sim_git-commit-6fba0136_modified_0.0.' in text
    checks['all_declared_effective_options']=all(options_actual.get(k)==v for k,v in spec['expected_effective_options'].items())
    # Include parser defaults that would otherwise be hidden from config deltas.
    checks['default_and_config_option_echo']=all(options_actual.get(k)==v for k,v in spec['expected_option_echo'].items())
    expected=json.loads((PACK/'ORDERED_KERNELS.json').read_text())[spec['workload']]
    starts=list(re.finditer(r'^kernel_name\s*=\s*(\S+)\s*$',text,re.M))
    checks['ordered_kernel_names']=[m.group(1) for m in starts]==[r['kernel'] for r in expected]
    checks['kernel_count']=len(starts)==len(expected)
    kernel_checks=[]
    cumulative_ctas=0
    cumulative_instructions=0
    for index,(mark,proof) in enumerate(zip(starts,expected)):
        block=text[mark.start():starts[index+1].start() if index+1<len(starts) else len(text)]
        metrics={k:int(v) for k,v in re.findall(r'^\s*(\w+)\s*=\s*(\d+)\s*$',block,re.M)}
        cumulative_ctas+=proof['complete_ctas']
        cumulative_instructions+=proof['active_instructions']
        n=lambda k:metrics.get(k,-1)
        mode=spec['dtc_mode']
        ck=dict(ordinal=index+1,
                active_instructions=n('gpu_sim_insn')==proof['active_instructions'],
                cumulative_instructions=n('gpu_tot_sim_insn')==cumulative_instructions,
                cumulative_ctas=n('gpu_tot_issued_cta')==cumulative_ctas,
                pib_empty=n('DTC_L1_'+mode+'_pib_occupancy')==0,
                inflight_empty=n('DTC_L1_'+mode+'_inflight_current')==0,
                lower_empty=n('DTC_L1_lower_outstanding')==0,
                credits_balanced=n('DTC_L1_lower_credit_acquired')==n('DTC_L1_lower_credit_released')>=0,
                lower_responses=n('DTC_L1_'+mode+'_lower_created')==n('DTC_L1_'+mode+'_lower_issued')==n('DTC_L1_'+mode+'_lower_responses')>=0,
                dependencies=n('DTC_L1_'+mode+'_completion_dependency_count')==n('DTC_L1_'+mode+'_completion_dependency_closed')>=0)
        observed=sum(n('DTC_L1_m4_'+s+'_admits') for s in ['store','atomic','bypass_load','proxy_fence'])
        ck['ordinary_balanced']=observed==n('DTC_L1_m4_source_completions')==n('DTC_L1_m4_observation_retires')>=0
        if mode=='oo':
            ck['refs_empty']=n('DTC_L1_oo_active_refs')==0
            ck['physical_balance']=(n('DTC_L1_oo_new_misses')-n('DTC_L1_oo_immediate_reclaims')-
                                    n('DTC_L1_oo_final_ref_reclaims')==n('DTC_L1_oo_physical_allocated'))
        else:
            ck['partial_empty']=n('DTC_L1_io_partial_entries_current')==n('DTC_L1_io_partial_lines_held_current')==0
            ck['physical_balance']=(n('DTC_L1_io_physical_allocations')-n('DTC_L1_io_physical_releases')==n('DTC_L1_io_physical_allocated_current'))
        # Retained tag-visible physical allocations are legal after references
        # drain; demanding allocated==0 would reject accepted frozen behavior.
        allocated=n('DTC_L1_oo_physical_allocated' if mode=='oo' else 'DTC_L1_io_physical_allocated_current')
        ck['retained_physical_bound']=0<=allocated<=64*640
        svc={k:v for k,v in metrics.items() if k.startswith('DTC_SERVICE_V1_')}
        ck['eleven_finite_metrics']=len(svc)==11
        ck['all_sm_cycle_samples']=svc.get('DTC_SERVICE_V1_samples',-1)==64*n('gpu_tot_sim_cycle')
        ck['residence_decomposition']=(svc.get('DTC_SERVICE_V1_fully_ready_to_complete_sum',-1)==
            sum(svc.get('DTC_SERVICE_V1_'+s,-10**15) for s in ['ready_to_collect_sum','collection_cycles','wb_wait']))
        ck['pass']=all(v for k,v in ck.items() if k!='ordinal')
        kernel_checks.append(ck)
    checks['every_ordered_kernel_strict']=len(kernel_checks)==len(expected) and all(k['pass'] for k in kernel_checks)
    # Copy-time hashes were checked by the immutable runner; verify current
    # identities once more so a replaced input cannot be silently accepted.
    checks['input_list_identity']=sha(spec['trace_list'])==spec['trace_list_sha256']
    checks['all_member_identities']=all(Path(m['path']).stat().st_size==m['bytes'] and sha(m['path'])==m['sha256'] for m in spec['members'])
    return dict(status='PASS_STRICT_EXPLORATORY_SCOPE' if all(checks.values()) else 'FAIL_PRESERVED',
                attempt_uuid=spec['attempt_uuid'],label=spec['label'],workload=spec['workload'],
                candidate=spec['candidate'],checks=checks,ordered_kernel_checks=kernel_checks,base=base,
                scope=dict(physical_drain='NO_LIVE_REF/PENDING/OWNERSHIP_LEAK; TAG_VISIBLE_RETAINED_DATA_ALLOWED',
                           individual_sector_count='UNAVAILABLE; frozen full-line completion mask + inflight/credit identities and negative CPU tests retained',
                           ordinary_internal_mshr_occupancy='UNAVAILABLE_AS_DISTINCT_DTC_COUNTER; natural termination and source-side completion balances checked',
                           numeric_load_values='UNAVAILABLE_IN_SASS_TIMING_MODEL',
                           hardware_area='UNAVAILABLE'))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--run')
    ap.add_argument('--spec')
    ap.add_argument('--output')
    args=ap.parse_args()
    result=strict(Path(args.run),json.loads(Path(args.spec).read_text()))
    write(Path(args.output),result)
    print(result['status'],result['attempt_uuid'])


if __name__=='__main__':
    main()
