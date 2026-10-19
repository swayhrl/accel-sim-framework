#!/usr/bin/env python3
"""Corrupt only in-memory copies of fixed historical full controls; no launches."""
from common import *
from strict_screen import parse_full,compare_calibration,echo
import copy
import re


def main():
    reference=json.loads((PACK/'controls/GEMM_CALIBRATION_REFERENCE.json').read_text())
    text=Path(reference['stdout']).read_text()
    assert sha(reference['stdout'])==reference['stdout_sha256']
    good=parse_full(text,'GEMM');compare_calibration(good,reference)
    cases=[]
    def reject(name,candidate):
        assert candidate!=text,name
        try:parse_full(candidate,'GEMM')
        except (ValueError,KeyError) as exc:cases.append(dict(case=name,status='REJECTED_AS_REQUIRED',reason=str(exc)[:250]))
        else:raise AssertionError('Accepted corrupt full-control output:'+name)
    def change(key,delta=1):
        pattern=r'^(\s*'+re.escape(key)+r'\s*=\s*)(\d+)(\s*)$'
        value,n=re.subn(pattern,lambda m:m[1]+str(int(m[2])+delta)+m[3],text,count=1,flags=re.M)
        assert n==1,key
        return value
    reject('natural_exit_marker_missing',text.replace('GPGPU-Sim: *** exit detected ***','TRUNCATED',1))
    reject('thread_exit_marker_missing',text.replace('GPGPU-Sim: *** simulation thread exiting ***','TRUNCATED',1))
    reject('actual_member_path_changed',text.replace('Processing kernel /workspace/','Processing kernel /wrong/',1))
    reject('missing_memcpy',re.sub(r'^launching memcpy command : .*\n','',text,count=1,flags=re.M))
    reject('duplicate_kernel',text+'\nkernel_name = duplicate\n')
    reject('wrong_active_instructions',change('gpu_sim_insn'))
    reject('wrong_CTA_total',change('gpu_tot_issued_cta'))
    reject('credit_imbalance',change('DTC_L1_lower_credit_released'))
    reject('Ref_population_imbalance',change('DTC_L1_oo_completion_dependency_closed'))
    reject('finite_SM_population_mismatch',change('DTC_SERVICE_V1_samples'))
    reject('finite_scope_decomposition_mismatch',change('DTC_SERVICE_V1_wb_wait'))
    reject('duplicate_common_metric',text+'\nDTC_SERVICE_V1_samples = 0\n')
    reject('K1_export_under_K0',text+'\nDTC_INVALIDATE_V1_SNAPSHOT_BEGIN version=1\n')
    reject('noninteger_GPU_cycles',re.sub(r'^gpu_tot_sim_cycle\s*=\s*\d+', 'gpu_tot_sim_cycle = nan',text,count=1,flags=re.M))
    for name,change_fn in [
        ('calibration_cycles_only_insufficient',lambda d:d['metrics'][-1].__setitem__('DTC_L1_oo_new_misses',d['metrics'][-1]['DTC_L1_oo_new_misses']+1)),
        ('calibration_traffic_changed',lambda d:d['traffic'].__setitem__('DRAM_issued_read_atoms',d['traffic']['DRAM_issued_read_atoms']+1))]:
        bad=copy.deepcopy(good);change_fn(bad)
        try:compare_calibration(bad,reference)
        except ValueError as exc:cases.append(dict(case=name,status='REJECTED_AS_REQUIRED',reason=str(exc)[:250]))
        else:raise AssertionError(name)
    try:echo('-gpgpu_dtc_l1_mode 3 #a\n-gpgpu_dtc_l1_mode 2 #b\n')
    except ValueError:cases.append(dict(case='conflicting_option_echo',status='REJECTED_AS_REQUIRED'))
    else:raise AssertionError('Conflicting echo accepted')
    gaussian=json.loads((PACK/'controls/Gaussian_CALIBRATION_REFERENCE.json').read_text())
    gtext=Path(gaussian['stdout']).read_text()
    assert sha(gaussian['stdout'])==gaussian['stdout_sha256']
    starts=list(re.finditer(r'^kernel_name =',gtext,re.M))
    partial=gtext[:starts[67].start()]
    try:parse_full(partial,'Gaussian')
    except ValueError:cases.append(dict(case='67_of_510_prefix_never_full_control',status='REJECTED_AS_REQUIRED'))
    else:raise AssertionError('Partial Gaussian accepted')
    write(PACK/'STRICT_CPU_NEGATIVES.json',dict(status='PASS_FULL_CONTROL_POSITIVE_AND_CORRUPTION_NEGATIVES',cases=cases,
        positive_controls=['GEMM_full_1_kernel','Gaussian_full_510_kernel_reference_preparation'],
        strict_sha256=sha(PACK/'tools/strict_screen.py'),test_sha256=sha(Path(__file__)),
        prior_raw_modified=False,new_simulations_started=0,AA5_prefix_used_for_calibration=False))
    print(json.dumps(dict(status='PASS_STRICT_CPU_NEGATIVES',cases=len(cases),new_simulations_started=0)))


if __name__=='__main__':main()
