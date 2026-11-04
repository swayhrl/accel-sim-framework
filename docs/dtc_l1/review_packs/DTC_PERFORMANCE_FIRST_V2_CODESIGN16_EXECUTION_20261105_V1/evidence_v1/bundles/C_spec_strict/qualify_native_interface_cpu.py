from pathlib import Path
import json,hashlib,types,copy,ast,datetime
O=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/agents/C_spec_strict_v1');T=O/'runtime';P=Path;sha=lambda p:hashlib.sha256(P(p).read_bytes()).hexdigest();rd=lambda p:json.loads(P(p).read_bytes())
p=T/'perf16_results.py';s=p.read_text().replace('FIXED8_INPUTS_TIMES_2_PHYSICAL_OOPIB192_COMBINATIONS_NOT_CORE32','EXPLORATORY_FIXED8_TWO_UNIFORM_COMBINATIONS_16_NOT_CORE32');p.write_text(s)
root=O/'cpu_runtime_fixture';(root/'control/specs').mkdir(parents=True,exist_ok=True);(root/'tools').mkdir(exist_ok=True)
for p in T.glob('*.py'):(root/'tools'/p.name).write_bytes(p.read_bytes())
checks=[]
def ck(n,v):assert v,n;checks.append({'check':n,'PASS':True})
def reject(n,f):
 try:f()
 except(AssertionError,KeyError,ValueError,TypeError):ck(n,True);return
 raise AssertionError(n)
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def load(p):
 m=types.ModuleType('CPU_NATIVE_FUNCTIONS_ONLY');m.__file__=str(p);exec(compile(Path(p).read_bytes(),str(p),'exec'),m.__dict__);return m
src=T/'perf16_native.py';e=load(src);e.R=root
matrix=rd(O/'cpu_sandbox/control/MATRIX.fixed.json');admitted={}
for row in matrix['points']:
 s=rd(O/'cpu_sandbox/control/specs'/(row['cohort']+'.json'))
 for c in s['configs']:c['path']=str(O/'cpu_sandbox'/P(c['path']).relative_to('/root/data/dtc_perf_first_v2_codesign16_20261105_v1'))
 s['input_binding_path']=str(O/'cpu_sandbox/control/input_bindings'/(s['input_digest']+'.json'));p=root/'control/specs'/(s['cohort']+'.json');write(p,s);(root/'control'/(s['cohort']+'_SPEC.json')).write_bytes(p.read_bytes());admitted[s['cohort']]=sha(p)
write(root/'control/MATRIX.fixed.json',matrix);write(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',{'input_digests':[r['input_digest']for r in matrix['points']]});write(root/'control/BUILD_PROFILE.json',{'core_commit':'9eedb3131937748f0492fa83aad37d3691118d70','framework_commit':'02775fd795cde5aae1480d81cee6eb481d0a08f4'})
release=Path('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_perf_first_v2_codesign16_execution_20261105_v1/control/V1_DIRECTION_RELEASE.fixed.json');plan={'source_pins':[{'path':str(p),'sha256':sha(p)}for p in T.glob('*.py')],'direction_release':{'path':str(release),'sha256':sha(release)}};write(root/'control/EXECUTION_PLAN.json',plan)
q={'state':'ARMED','request':e.REQ,'engine_sha256':sha(src),'execution_plan_sha256':sha(root/'control/EXECUTION_PLAN.json'),'spec_request_sha256':sha(root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json'),'model_automatic_retries':0,'budget':16,'remaining':16,'admitted_specs':admitted,'consumed':{},'runtime_release_evidence':{'direction_release_path':str(release),'direction_release_sha256':sha(release),'authority_commit':'320b1365902a72502fa61ba114cb4a4a28b934bb','exact_candidate_count':16}}
reg={'registered_future_requests':{e.REQ:q,'FOREIGN_OPTIONAL_REMAINING':{'budget':1,'consumed':{}}},'old_source_history':['CPU_SENTINEL'],'qualification_history':['CPU_SENTINEL']};before=copy.deepcopy(reg);e.authority=lambda:(reg,{'epoch':2});ck('actual_registered_source_with_inmemory_exact16_context',e.registered()[2]is q)
for row in matrix['points']:
 s=e.canonical(row['cohort']);ck('actual_canonical_'+row['cohort'],s['request']==e.REQ and s['profile']==row['profile']and s['expected_options']['-gpgpu_dtc_l1_oo_pib_entries']==['192'])
for key,value in [('budget',17),('remaining',15),('model_automatic_retries',1),('engine_sha256','0'*64)]:
 keep=q[key];q[key]=value;reject('registered_reject_'+key,lambda:e.registered());q[key]=keep
q['runtime_release_evidence']['exact_candidate_count']=28;reject('rejectwrong_release28',lambda:e.registered());q['runtime_release_evidence']['exact_candidate_count']=16
q['runtime_release_evidence']['authority_commit']='0'*40;reject('rejectwrong_releaseAuthority',lambda:e.registered());q['runtime_release_evidence']['authority_commit']='320b1365902a72502fa61ba114cb4a4a28b934bb'
reject('rejectforeign_V1_cohort',lambda:e.canonical('E2-DTCPF28-d984ea5475a581ad-DH-PHYS1024-V1'))
ck('allreadonly_engine_tests_preserve_mock_peers_history',reg==before)
# Atomic consume protection uses the same resource typed-HOLD helper as prepare.
# The helper itself is independently qualified by A; these fixtures test the
# actual native wrapper never invokes a model/INTENT mutator while unconsumed held.
spec=rd(root/'control/specs'/(matrix['points'][0]['cohort']+'.json'));cohort=spec['cohort'];calls=[];e.spec_for=lambda c:spec
e.admission_hold=lambda own,s:own.get('admission_holds',{}).get(s['profile'])or own.get('admission_holds',{}).get(s['cohort'])
e.guard_model_mutation(reg,cohort,lambda cur:calls.append('mutated'));ck('atomic_guard_allows_eligible_unheld_once',calls==['mutated'])
q['admission_holds']={spec['profile']:{'typed_fixture':True}};reject('atomic_profileHOLD_noINTENTmutator',lambda:e.guard_model_mutation(reg,cohort,lambda cur:calls.append('bad')));ck('profileHOLD_no_mutator_effect',calls==['mutated'])
q['admission_holds']={cohort:{'typed_fixture':True}};reject('atomic_cohortHOLD_noINTENTmutator',lambda:e.guard_model_mutation(reg,cohort,lambda cur:calls.append('bad')))
q['consumed'][cohort]={'uuid':'CPU_ONLY_NOT_NATIVE'};e.guard_model_mutation(reg,cohort,lambda cur:calls.append('healthy_consumed_completion'));ck('already_consumed_completion_not_blocked_by_admissionHOLD',calls[-1]=='healthy_consumed_completion');q['consumed'].clear();q.pop('admission_holds')
# Only loaders and definitions are exercised. Never prepare/run_native/engine,
# update_authority, frontend.main, terminal or archive on actual science state.
for name in ['native','frontend','strict','results','outbox']:
 p=T/('perf16_'+name+'.py');text=p.read_text();ck(name+'_newnamespace_no_oldreq_or_root', 'DTC_PERF_FIRST_NON_TAG_REMAINING28_20261104_V1'not in text and '/root/data/dtc_perf_first_remaining28_20261104_v1'not in text and 'perf28_'not in text);ck(name+'_private_compile_loader_no_pyc','spec_from_file_location'not in text)
ck('no_first4gate_or_singlefactor_validator',all('terminal_gate_receipt'not in (T/('perf16_'+n+'.py')).read_text()for n in ['native','strict']))
oldpolicy=Path('/root/data/dtc_perf_first_remaining28_20261104_v1/tools/perf28_guard_policy.py').read_text();newpolicy=(T/'perf16_guard_policy.py').read_text();ck('guard_semantics_original_unchanged',newpolicy.replace('Physical x OO-PIB16 new-request resource policy','Stage II-A new-request resource policy')==oldpolicy)
ck('guard_policy_exact_SHA_binding',sha(T/'perf16_guard_policy.py')in(T/'perf16_guard.py').read_text());ck('strict_acceptance_schema_roles_explicit',"schema='DTC_PERFV2_CODESIGN16_STRICT_V1'"in(T/'perf16_strict.py').read_text()and"status='PERFV2_CODESIGN16_NATIVE_TRACE_PERFORMANCE_QUALIFIED'"in(T/'perf16_strict.py').read_text())
ck('outbox_true164_SOURCE_KEEP_copy_restore_kept',all(t in(T/'perf16_outbox.py').read_text()for t in ['SOURCE','admission_disk_pass','check_native','verify_archive','fuse.sshfs','admin-wcx@10.208.130.164:/home/shared']) )
ck('negative_nullcycles_no_retry_explicit',"cycles=None if failed"in(T/'perf16_results.py').read_text()and'FAIL_PERFV2_CODESIGN16_DH_ARCHIVED_NO_RETRY'in(T/'perf16_results.py').read_text())
ck('unusedscopes_not_authorized_by_label',"validated_union_authorized=False"in(T/'perf16_results.py').read_text()and'EXPLORATORY_FIXED8_TWO_UNIFORM_COMBINATIONS_16_NOT_CORE32'in(T/'perf16_results.py').read_text())
write(O/'CPU_NATIVE_INTERFACE_QUALIFICATION.json',{'schema':'DTC_PERFV2_CODESIGN16_NATIVE_INTERFACE_CPU_V1','status':'PASS_INMEMORY_MOCK_AUTHORITY_ONLY','count':len(checks),'checks':checks,'real_authority_writes':0,'real_prepare_engine_terminal_archive_calls':0,'real_scientific_models':0,'notes':'Production source canonical/registered functions executed using isolated fake registry/control/spec files; not a real native grant or runtime acceptance.'})
print('CPU_NATIVE_INTERFACE_PASS',len(checks))

