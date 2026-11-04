"""Focused pure-policy CPU cases; all authority rows are private stand-ins."""
import copy, importlib.util, json, hashlib
from pathlib import Path
from types import SimpleNamespace
O=Path(__file__).parent
sp=importlib.util.spec_from_file_location('inactive_bpf_policy',O/'future_policy.py')
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
ex,plan=m.pinned_contracts()
matrix=m.read(m.ROOT/'control/MATRIX_CURRENT.json');scope=m.read(m.ROOT/'control/SCOPE.json')
row=plan['rows'][0];s=m.read(row['draft_spec']['path'])
assert m.sha(row['draft_spec']['path'])==row['draft_spec']['sha256']
checks=[]
def ok(name,fn):
 fn();checks.append({'name':name,'status':'PASS'})
def rejects(fn):
 try:fn()
 except (m.PolicyHold,KeyError):return
 raise AssertionError('expected HOLD')
def authority(spec):
 return {'request':spec['request'],'admitted_specs':{spec['cohort']:m.objsha(spec)},'consumed':{},'sealed':[],
         'authorized_incident_recovery_trials':[],'qualification_only':True}
auth={'cohort':s['cohort'],'role':m.ROLE_IR,'incident_id':plan['incident_id'],'recovery_plan_sha256':m.IR_PLAN_SHA,
      'primary_statistics_excluded':True,'validated_union_authorized':False}
for k in ('original_cohort','original_uuid','science_projection_sha256','original_negative_RESULT_sha256','original_DONE_sha256'):auth[k]=row[k]
q=authority(s);q['authorized_incident_recovery_trials']=[auth]
mem={'allowed_cohorts':[s['cohort']]}
bindings={s['input_digest']:{'input_binding_sha256':s['input_binding_sha256'],'expected':s['expected']}}
def classify(spec=s,qq=q,mm=matrix,me=mem,bb=bindings,stage='ADMISSION'):
 return m.classify_registered(spec['cohort'],spec,m.objsha(spec),qq,mm,scope,me,ex,plan,bb,stage=stage)
ok('actual_frozen_IR_draft_scientific_projection_matches',lambda: m.require(m.science_sha(s)==row['science_projection_sha256'],'science'))
policy=classify()
ok('exact_IR_plan_and_private_registered_row_excluded_no_union',lambda:m.require(policy['primary_statistics_excluded']and not policy['validated_union_authorized']and not policy['production_permission'],'exclusion'))
qq=copy.deepcopy(q);qq['authorized_incident_recovery_trials']=[]
ok('unregistered_IR_rejected',lambda:rejects(lambda:classify(qq=qq)))
qq=copy.deepcopy(q);qq['consumed'][s['cohort']]={'uuid':'cpu-private'}
ok('spent_IR_not_resubmitted',lambda:rejects(lambda:classify(qq=qq)))
qq=copy.deepcopy(q);qq['authorized_incident_recovery_trials'][0]['validated_union_authorized']=True
ok('IR_union_flag_rejected',lambda:rejects(lambda:classify(qq=qq)))
ok('missing_memory_append_rejected',lambda:rejects(lambda:classify(me={'allowed_cohorts':[]})))
ss=copy.deepcopy(s);ss['host_cpu']=1;qq=authority(ss);qq['authorized_incident_recovery_trials']=[auth]
ok('canonical_CPU_binding_rejected',lambda:rejects(lambda:classify(spec=ss,qq=qq)))
ss=copy.deepcopy(s);ss['expected']['CTA']+=1;qq=authority(ss);qq['authorized_incident_recovery_trials']=[auth]
ok('changed_frozen_capture_counts_rejected',lambda:rejects(lambda:classify(spec=ss,qq=qq)))
ss=copy.deepcopy(s);ss['input_binding_sha256']='0'*64;qq=authority(ss);qq['authorized_incident_recovery_trials']=[auth]
ok('changed_trace_binding_rejected',lambda:rejects(lambda:classify(spec=ss,qq=qq)))
ss=copy.deepcopy(s);ss['core_commit']='0'*40;qq=authority(ss);qq['authorized_incident_recovery_trials']=[auth]
ok('changed_Core_rejected',lambda:rejects(lambda:classify(spec=ss,qq=qq)))
p=matrix['points'][0];primary=m.read(m.ROOT/'control/specs'/(p['cohort']+'.json'))
pb={primary['input_digest']:{'input_binding_sha256':primary['input_binding_sha256'],'expected':primary['expected']}}
pq=authority(primary);pm={'allowed_cohorts':[primary['cohort']]}
def pc(spec=primary,qq=pq,mm=matrix):
 return m.classify_registered(spec['cohort'],spec,m.objsha(spec),qq,mm,scope,pm,ex,plan,pb)
ok('actual_primary_MATRIX_spec_classifies_only_as_candidate',lambda:m.require(pc()['scientific_role']=='PRIMARY_PERFORMANCE'and not pc()['production_permission'],'primary'))
ok('primary_not_in_current_MATRIX_rejected',lambda:rejects(lambda:pc(mm={'points':[]})))
ec=next(iter(ex['scope_cohorts']));es=m.read(m.ROOT/'control/specs'/(ec+'.json'))
eq=authority(es);em={'allowed_cohorts':[ec]};eb={es['input_digest']:{'input_binding_sha256':es['input_binding_sha256'],'expected':es['expected']}}
ok('exact_engineering4_retain_V2_reference_cycles_rule',lambda:m.require(m.classify_registered(ec,es,m.objsha(es),eq,matrix,scope,em,ex,plan,eb)['route']=='EXACT_DELEGATE_V2_ENGINEERING','old4'))
ss=copy.deepcopy(primary);ss['cohort']='CPU_ONLY_FUTURE_COMBO';ss['profile']='CPU_COMBO_E384_M8'
qp=authority(ss);mp={'points':[dict(p,cohort=ss['cohort'],profile=ss['profile'])]};me={'allowed_cohorts':[ss['cohort']]}
ok('future_registered_matrix_primary_not_limited_to_current_15',lambda:m.require(m.classify_registered(ss['cohort'],ss,m.objsha(ss),qp,mp,scope,me,ex,plan,pb)['route']=='V3_FUTURE_BPF_CANDIDATE','future'))
proof=dict(cohort=s['cohort'],uuid='PRIVATE_CPU_UUID',performance_accepted=True,cycles=1234567,
 additional_cpu_spare_memory_admission_strict={'status':'PASS_CPU_SPARE_MEMORY_IO_AND_ORIGINAL_PERFORMANCE'},
 additional_shared_json_io_strict={'status':'CPU_SEMANTIC_STANDIN'},effective_options=s['expected_options'],
 CTA=s['expected']['CTA'],instructions=s['expected']['instructions'],kernel_count=s['expected']['kernels'])
for k in ('input_digest','core_commit','framework_commit','binary_sha256','cell','profile'):proof[k]=s[k]
done={'cohort':s['cohort'],'uuid':proof['uuid'],'stop_reason':None,'launcher_wait_returncode':0}
activation={'status':'PASS_BPF_REQUIRED_ACTIVE','fallback_accepted':False,'baseline_Seccomp':0,'baseline_filters':0,'model_Seccomp':2,'model_filters':1}
archive={'status':'PASS_NEW_OBSERVATION_ARCHIVED_AND_NATIVE_RESTORED','cohort':s['cohort'],'uuid':proof['uuid'],'original_full_archive_verifier_required':True}
def sem(pp=proof,dd=done,aa=activation,ar=archive):return m.check_terminal_semantics(policy,s,pp,dd,dd,dd,aa,ar)
ok('IR_positive_cycles_no_comparison_to_failed_or_P0_cycles',lambda:m.require(sem()['cycles']==1234567 and sem()['reference_cycles_equality_checked']is False,'cycles'))
pp=copy.deepcopy(proof);pp['cycles']=2345678
ok('alternate_positive_cycles_allowed_without_bestof_selection',lambda:m.require(sem(pp=pp)['cycles']==2345678,'cycles2'))
pp=copy.deepcopy(proof);pp['effective_options']['CPU_ONLY_EXTRA']='x'
ok('actual_full_options_mismatch_rejected',lambda:rejects(lambda:sem(pp=pp)))
pp=copy.deepcopy(proof);pp['kernel_count']-=1
ok('partial_capture_rejected',lambda:rejects(lambda:sem(pp=pp)))
aa=copy.deepcopy(activation);aa['model_Seccomp']=0;aa['model_filters']=0
ok('silent_BPF_fallback_rejected',lambda:rejects(lambda:sem(aa=aa)))
dd=copy.deepcopy(done);dd['stop_reason']='INVALID_SAMPLE'
ok('non_natural_recovery_rejected',lambda:rejects(lambda:sem(dd=dd)))
ar=copy.deepcopy(archive);ar['original_full_archive_verifier_required']=False
ok('new_proof_without_original_full_archive_rejected',lambda:rejects(lambda:sem(ar=ar)))
ok('CPU_QA_or_fake_PASS_not_accepted_as_canary_release',lambda:m.require(m.canary4_release_eligibility(None,SimpleNamespace())['status']=='NOT_ELIGIBLE_NOT_INSTALLED','activation'))
ok('candidate_has_no_production_permission_or_installer',lambda:m.require(not m.deployment_status()['production_permission']and not hasattr(m,'install_on_frame'),'inactive'))
result={'schema':'DTC_FUTURE_BPF_V3_PURE_POLICY_CPU_QUALIFICATION','status':'PASS','checks':checks,'count':len(checks),
 'source_sha256':m.sha(O/'future_policy.py'),'driver_sha256':m.sha(__file__),
 'actual_production_canary_release_qualified':False,'authority_fixtures':'Private stand-ins; actual MATRIX/SCOPE and frozen IR draft bytes are read-only inputs.',
 'terminal_proofs':'Synthetic semantic inputs only; no physics/native/strict/archive execution. Does not prove runtime production qualification.',
 'models_started':0,'new_grants':0,'production_changes':0,'tests_rerun':0}
with(O/'CPU_POLICY_QUALIFICATION.json').open('x')as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':'PASS','checks':len(checks),'source_sha256':result['source_sha256']}))
