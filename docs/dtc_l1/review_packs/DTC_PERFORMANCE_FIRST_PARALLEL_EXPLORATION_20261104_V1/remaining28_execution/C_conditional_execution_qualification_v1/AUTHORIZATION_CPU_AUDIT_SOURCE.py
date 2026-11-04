from pathlib import Path
import json,hashlib
R=Path('/root/data/dtc_perf_first_remaining28_20261104_v1');A=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_parallel_exploration_20261104_v1');O=A/'C_remaining28_execution_qualification_v1';c=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rd(p):return json.loads(Path(p).read_bytes())
def ck(n,v):assert v,n;c.append(dict(name=n,PASS=True))
q=rd(R/'control/REGISTRY_REQUEST_CANDIDATE.json');p=rd(R/'control/EXECUTION_PLAN.json');s=rd(R/'control/SCIENCE_AUTHORIZATION.json');req=rd(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json');build=rd(R/'control/BUILD_PROFILE.json');policy=rd(R/'control/RESOURCE_POLICY.json');matrix=rd(R/'control/MATRIX.json')
ck('auth_explicit_exact28_oneeach',s['explicit_user_approval']is True and set(s['budgets'])==set(q['admitted_specs'])and len(s['budgets'])==28 and all(v==1 for v in s['budgets'].values()));ck('approval_request_SHA',q['spec_request_sha256']==s['approval_request_sha256']==sha(R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'))
for key,file in [('engine_sha256','native'),('controller_sha256','ops'),('strict_sha256','strict'),('outbox_sha256','outbox')]:ck('candidate_actual_'+key,q[key]==sha(R/'tools'/('perf28_'+file+'.py')))
ck('profile_and_resource_policy_SHA',p['build_profile_sha256']==sha(R/'control/BUILD_PROFILE.json')and build['resource_policy_sha256']==sha(R/'control/RESOURCE_POLICY.json'))
ck('5GiB_88percent_and_no_other_grants',policy['native_safety_floor_bytes']==5*1024**3 and policy['memory_utilization_fraction']==.88 and q['all_other_candidate_grants']==0)
cap=sum(2*x['limits']['max_result_directory_bytes']for x in matrix['points']);ck('heterogeneous_lifetime_write_ceiling',cap==q['maximum_source_plus_restore_lifetime_bytes']==4294967296 and cap+policy['metadata_reserve_bytes']==q['reserved_write_bytes']==4563402752)
ck('user_gate_auth_preserved',sha(R/'control/GATE_AMENDMENT_USER_AUTHORIZATION.fixed.md')=='119217415136f6bae824ed25ecb5d0776fcd67eeff9dcae7fde6b5a0ce73f894')
ck('remaining28_requires_separate_registration_not_extension',q['new_registration_only']is True and q['old_request_budget_reused']is False and p['no_extensions']is True and p['expected_new_starts']==28)
for k in ['core','framework']:
 ck('fixed_clean_'+k,__import__('subprocess').check_output(['git','-C',build['source_worktrees'][k],'rev-parse','HEAD'],text=True).strip()==build[k+'_commit']and not __import__('subprocess').check_output(['git','-C',build['source_worktrees'][k],'status','--porcelain'],text=True).strip())
(O/'AUTHORIZATION_AND_CEILING_CHECKS.json').write_text(json.dumps(dict(status='PASS_CPU_CONDITIONAL',count=len(c),checks=c),indent=2)+'\n');print('FINAL_EXTRA',len(c))
