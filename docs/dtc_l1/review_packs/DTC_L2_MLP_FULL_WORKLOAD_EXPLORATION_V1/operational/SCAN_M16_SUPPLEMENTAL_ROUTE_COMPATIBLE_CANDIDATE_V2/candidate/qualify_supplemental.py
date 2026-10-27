"""Isolated native CPU: no actual registration/prepare/model/old-result writes.
Actual canonical/spec_for/prepare, refresh and dispatch-binding source bodies.
Authority, source lease/input/resource/Git checks are scoped CPU fixtures.
"""
import copy,hashlib,importlib.util,json,os,pathlib,tempfile,threading,types
from unittest.mock import patch
import supplemental_trial as m
P=pathlib.Path;HERE=P(__file__).resolve().parent
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
def read(p):return json.loads(P(p).read_bytes())
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);o=importlib.util.module_from_spec(sp);sp.loader.exec_module(o);return o
def put(p,v):P(p).parent.mkdir(parents=True,exist_ok=True);P(p).write_bytes(m.encoded(v))
real_scope=read(R/'control/SCOPE.json');real_matrix=read(R/'control/MATRIX_CURRENT.json')
oldspec=read(R/'control/specs'/(m.OLD+'.json'))
actual_native_sha=m.sha(R/'tools/l2_native.py');actual_consumer=load('supp_CPU_actual_consumer',R/'tools/l2_results.py')
registered_ids=set(load('supp_CPU_readonly_domain',R/'tools/l2_native.py').registered()[2]['admitted_specs'])&{p['cohort']for p in real_matrix['points']}
checks=[]
def ck(name,condition):assert condition,name;checks.append(name)
class Fixture:
 def __init__(self,fault=None):
  self.tmp=tempfile.TemporaryDirectory(prefix='CPU_SUPPLEMENTAL_ONLY_',dir=R/'analysis');self.r=P(self.tmp.name)
  put(self.r/'control/SCOPE.json',real_scope);matrix=copy.deepcopy(real_matrix);matrix['base_scope_sha256']=m.sha(self.r/'control/SCOPE.json');put(self.r/'control/MATRIX_CURRENT.json',matrix)
  self.matrix_before=(self.r/'control/MATRIX_CURRENT.json').read_bytes();self.scope_before=(self.r/'control/SCOPE.json').read_bytes()
  old=copy.deepcopy(oldspec);put(self.r/'control/specs'/(m.OLD+'.json'),old);put(self.r/'control'/(m.OLD+'_SPEC.json'),old)
  put(self.r/'control/BUILD_PROFILE.json',dict(core_commit=old['core_commit'],framework_commit=old['framework_commit']))
  put(self.r/'control/EXECUTION_PLAN.json',read(R/'control/EXECUTION_PLAN.json'))
  (self.r/'tools').mkdir();(self.r/'tools/l2_resources.py').symlink_to(R/'tools/l2_resources.py')
  put(self.r/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',{'input_digests':sorted({p['input_digest']for p in real_scope['points']})})
  self.original_budget=len(registered_ids)
  q=dict(request='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1',state='RUNNING',budget=self.original_budget,remaining=self.original_budget-1,
   admitted_specs={p['cohort']:'CPU_OTHER_SPEC_SHA'for p in matrix['points']if p['cohort']in registered_ids},
   admitted_inputs={d:{'specs':[p['cohort']for p in matrix['points']if p['input_digest']==d and p['cohort']in registered_ids]}for d in{p['input_digest']for p in matrix['points']}},
   consumed={m.OLD:{'uuid':m.OLD_UUID}},strict_sha256=m.sha(R/'tools/l2_strict.py'))
  q['admitted_specs'][m.OLD]=m.digest(old);self.authority=self.r/'CPU_AUTHORITY.json';put(self.authority,{'registered_future_requests':{q['request']:q}});self.grants=0
  self.e=load('supp_CPU_actual_native',R/'tools/l2_native.py');self.e.R=self.r
  self.owner_plan=dict(parent_pid=os.getpid(),parent_start_ticks=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19]))
  self.e.registered=lambda:(self.reg(),dict(epoch=2,state='NATIVE_SCIENCE_ACTIVE',holder=os.uname().nodename),self.q(),self.owner_plan)
  self.e.update_authority=self.update
  lineage=dict(schema='DTC_L2_MLP_SUPPLEMENTAL_TRIAL_LINEAGE_V1',role=m.ROLE,original_failed_cohort=m.OLD,original_uuid=m.OLD_UUID,
   primary_statistics_excluded=True,validated_union_authorized=False,new_grants=1,refunds=0,reuse_old_UUID=False,
   negative_certificate_sha256='CPU_ONLY_SYNTHETIC_VERIFIER_PROOF_NOT_ACTUAL_CERTIFICATION')
  new=copy.deepcopy(old);new.update(cohort=m.NEW,scientific_role=m.ROLE,supplemental_trial_lineage=lineage)
  point=next(p for p in matrix['points']if p['cohort']==m.OLD)
  self.plan=dict(schema='DTC_L2_MLP_SUPPLEMENTAL_TRIAL_PLAN_V1',old_cohort=m.OLD,new_cohort=m.NEW,old_uuid=m.OLD_UUID,old_spec=old,new_spec=new,
   old_spec_sha256=m.digest(old),new_spec_sha256=m.digest(new),scientific_identity_sha256=m.digest(m.scientific(old)),
   new_point=dict(point,cohort=m.NEW,scientific_role=m.ROLE),source_and_evidence_pins=[dict(path=str(R/'tools/l2_native.py'),sha256=actual_native_sha)],CPU_FIXTURE_ONLY=True)
  self.authorization=dict(approved_plan_sha256=m.digest(self.plan),cohort=m.NEW,additional_starts=1,primary_statistics_unchanged=True,CPU_FIXTURE_ONLY=True)
  def verifier(plan):return dict(cohort=m.OLD,uuid=m.OLD_UUID,performance_accepted=False,accepted_cycles=None,certificate_sha256=lineage['negative_certificate_sha256'],CPU_FIXTURE_ONLY=True)
  self.verifier=verifier;self.store=m.SupplementalRegistry(self.r,self.e,threading.RLock(),lambda:None,fault,verifier)
 def reg(self):return read(self.authority)
 def q(self):return self.reg()['registered_future_requests'][self.e.REQ]
 def update(self,fn):
  before=self.q()['budget'];v=self.reg();fn(v);put(self.authority,v);self.grants+=self.q()['budget']-before
 def run(self):return self.store.register(self.plan,self.authorization)
 def close(self):self.tmp.cleanup()
 def old_unchanged(self):return self.q()['consumed'][m.OLD]=={'uuid':m.OLD_UUID}and(self.r/'control/MATRIX_CURRENT.json').read_bytes()==self.matrix_before and(self.r/'control/SCOPE.json').read_bytes()==self.scope_before
 def spent(self,uuid='CPU_ONLY_FRESH_UUID'):
  def fn(reg):
   q=reg['registered_future_requests'][self.e.REQ];q['consumed'][m.NEW]={'uuid':uuid};q['remaining']-=1
  self.update(fn)
 def natural_fixture(self):
  self.spent();q=self.q();spec=self.e.canonical(m.NEW);uid=q['consumed'][m.NEW]['uuid'];out=self.r/'DTC/run/results'/uid;out.mkdir(parents=True)
  side=out/'SHARED_JSON_IO_EXTRA_STRICT.json';put(side,dict(status='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT',CPU_FIXTURE_ONLY=True))
  intent=dict(cohort=m.NEW,uuid=uid,output=str(out),additional_shared_json_io_binding={'CPU_FIXTURE_ONLY':True})
  ip=self.r/'control/qualification_ledger'/(m.NEW+'.INTENT.json');put(ip,intent)
  done=dict(uuid=uid,stop_reason=None,launcher_wait_returncode=0,native_simulator_observed=True,raw_sha256='CPU_ONLY_RAW');put(ip.with_name(m.NEW+'.DONE.json'),done);put(out/'NATIVE_EXIT.json',done)
  def add(reg):reg['registered_future_requests'][self.e.REQ]['consumed'][m.NEW].update(execution_receipt=done,intent_sha256=m.sha(ip))
  self.update(add)
  proof=dict(performance_accepted=True,cycles=12345,cohort=m.NEW,input_digest=spec['input_digest'],cell='DH',profile='M16',
   effective_options=spec['expected_options'],raw_gzip_sha256='CPU_ONLY_RAW',CTA=spec['expected']['CTA'],instructions=spec['expected']['instructions'],kernel_count=spec['expected']['kernels'],
   additional_shared_json_io_strict=dict(status='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT',sidecar_path=str(side),sidecar_sha256=m.sha(side)),
   **{k:spec[k]for k in ('core_commit','framework_commit','binary_sha256')})
  value=dict(state=actual_consumer.PASS,cycles=12345,cohort=m.NEW,uuid=uid,proof=proof,archive={'CPU_ONLY_NATIVE_RESTORE':True})
  put(out/'L2_STRICT.json',proof);put(self.r/'DTC/control'/('SCIENCE_QUALIFICATION_'+m.NEW+'.json'),dict(uuid=uid,strict_sha256=m.sha(out/'L2_STRICT.json')))
  put(self.r/'analysis'/(m.NEW+'.RESULT.json'),value);return value

f=Fixture();m.validate_plan(f.plan)
ck('same_complete_input_Core_FW_binary_all270_options_and_configs_preserved',m.scientific(f.plan['old_spec'])==m.scientific(f.plan['new_spec'])and len(f.plan['new_spec']['expected_options'])==270)
f.run();ck('one_new_grant_no_refund_primary350_and_old_spent_unchanged',f.grants==1 and f.q()['budget']==f.original_budget+1 and f.old_unchanged())
f.run();ck('idempotent_registration_never_regrants_or_reuses_old_UUID',f.grants==1)
view=f.store.dispatch_view(f.store.primary());ck('dispatch_only351_view_has_role_but_disk_matrix350',len(view['points'])==len(real_matrix['points'])+1 and len(read(f.r/'control/MATRIX_CURRENT.json')['points'])==len(real_matrix['points'])and view['points'][-1]['scientific_role']==m.ROLE)
seen=[]
class Journal:
 def guard_decision(self,v):return dict(v,existing_journal_preserved=True)
def previous(summary,scope,history):seen.append(scope);return dict(proposals=[],existing_typed_gate_preserved=True,scientific_stage_complete=False,adoption_ready=False)
wrapped=m.make_primary_adaptive(previous,f.store,Journal());result=wrapped({},view,{})
ck('existing_typed_adaptive_receives_exact_primary350_not_supplemental_scope',seen[-1]==f.store.primary()and result['existing_typed_gate_preserved'])
rawsum=actual_consumer.summarize(f.store.primary(),{m.OLD:{'state':'ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY','uuid':m.OLD_UUID,'cycles':None}})
ck('original_M16_slot_unaccepted_cyclesNone_before_supplemental_closure',not rawsum['table'][oldspec['input_digest']]['M16']['DH']['accepted'])
value=f.natural_fixture();table=m.supplemental_result(f.store,actual_consumer.accepted,lambda c:value['archive'])
ck('fresh_natural_metadata_strict_archive_IO_closure_goes_supplemental_only_no_GM',table['rows'][0]['accepted']and table['rows'][0]['cycles']==12345 and table['GM']is None and table['automatic_union']is False)
sum_after=actual_consumer.summarize(f.store.primary(),{m.NEW:value,m.OLD:{'state':'ENGINEERING_TERMINAL_NEGATIVE_ARCHIVED_NO_RETRY','cycles':None}})
ck('accepted_newtrial_cannot_replace_failed_original_M16_slot',not sum_after['table'][oldspec['input_digest']]['M16']['DH']['accepted']and sum_after['table'][oldspec['input_digest']]['M16']['DH']['cycles']is None)
try:m.supplemental_result(f.store,actual_consumer.accepted)
except AssertionError:ck('supplemental_accepted_requires_real_archive_verifier_callback',True)
else:raise AssertionError('archive verifier omitted')
strict_path=P(table['rows'][0]['strict_path']);strict_path.unlink()
try:m.supplemental_result(f.store,actual_consumer.accepted,lambda c:value['archive'])
except FileNotFoundError:ck('missing_full_strict_qualification_chain_cannot_supply_cycles',True)
else:raise AssertionError('strict proof missing accepted')
f.close()

f=Fixture();f.owner_plan['parent_pid']=-1
try:f.run()
except AssertionError:pass
else:raise AssertionError('extra owner accepted')
ck('different_parent_owner_rejected_before_any_registration',f.grants==0 and not f.store.folder.exists())
f.close()
for stage in ('AFTER_PREPARED','AFTER_SPEC_PUBLICATION','AFTER_AUTHORITY','AFTER_COMMITTED'):
 fired=[]
 def fault(name):
  if name==stage and not fired:fired.append(name);raise RuntimeError('CPU crash '+name)
 f=Fixture(fault)
 try:f.run()
 except RuntimeError:pass
 f.store.fault_hook=None;before=f.grants;recovered=f.store.recover_pending()
 if stage in ('AFTER_PREPARED','AFTER_SPEC_PUBLICATION'):
  assert f.grants==0 and recovered[0]['state']=='UNGRANTED_SAFE_TO_CONTINUE';f.run()
 else:assert recovered[0]['state']=='COMMITTED_RECONCILED';f.run()
 ck('crash_resume_'+stage+'_exactly_one_total_grant_and_no_primary_write',f.grants==1 and f.old_unchanged())
 f.close()
f=Fixture(lambda name:(_ for _ in()).throw(RuntimeError('CPU authority gap'))if name=='AFTER_AUTHORITY'else None)
try:f.run()
except RuntimeError:pass
f.spent();f.store.fault_hook=None;f.store.recover_pending();f.run()
ck('authority_gap_already_spent_generation_preserved_without_regrant',f.grants==1 and f.q()['consumed'][m.NEW]['uuid']=='CPU_ONLY_FRESH_UUID')
f.close()
f=Fixture();f.authorization['additional_starts']=2
try:f.run()
except AssertionError:pass
else:raise AssertionError('bad authorization')
ck('wrong_authorization_cannot_publish_spec_or_grant',f.grants==0 and not(f.r/'control/specs'/(m.NEW+'.json')).exists())
f.close()
f=Fixture();f.store.lineage_verifier=lambda plan:(_ for _ in()).throw(RuntimeError('HOLD real lineage'))
try:f.run()
except RuntimeError:pass
else:raise AssertionError('lineage HOLD ignored')
ck('actual_lineage_HOLD_blocks_before_PREPARED_spec_and_authority',f.grants==0 and not f.store.folder.exists())
f.close()
f=Fixture();f.plan['new_spec']['expected_options']['-gpgpu_clock_domains']=['CHANGED']
try:f.run()
except AssertionError:pass
else:raise AssertionError('science changed')
ck('clock_or_other_scientific_change_rejected',f.grants==0)
f.close()

f=Fixture();f.run();before=f.reg()
q=before['registered_future_requests'][f.e.REQ];q['admitted_specs'].pop(m.NEW);q['authorized_supplemental_trials']=[];q['admitted_inputs'][oldspec['input_digest']]['specs'].remove(m.NEW);q['budget']-=1;q['remaining']-=1
put(f.authority,before)
try:f.run()
except AssertionError:pass
else:raise AssertionError('committed grant silently regenerated after authority loss')
ck('lost_authority_after_COMMITTED_HOLD_never_budget_reset_or_regrant',f.grants==1)
f.close()
f=Fixture();f.run();f.spent(m.OLD_UUID)
try:f.store.recover_pending()
except AssertionError:pass
else:raise AssertionError('old UUID reused')
ck('malicious_old_UUID_substitution_rejected',f.grants==1)
f.close()
# Actual frozen refresh_pending_resource_spec -> canonical -> spec_for/prepare.
f=Fixture();f.run();regmod=load('supp_CPU_actual_registry',R/'tools/l2_registry.py');regmod.R=f.r
resource=load('supp_CPU_actual_resources',R/'tools/l2_resources.py')
regmod.load=lambda name,file:f.e if file=='l2_native.py'else resource
regmod.refresh_pending_resource_spec(m.NEW,{'records':[dict(workload=oldspec['workload'],rss=2*1024**3,success=True,elapsed=100,core_commit=oldspec['core_commit'])]})
updated=f.e.canonical(m.NEW)
ck('actual_refresh_resource_amend_preserves_registered_scientific_identity',m.digest(m.scientific(updated))==f.plan['scientific_identity_sha256'])
f.store.recover_pending();cpu=min(os.sched_getaffinity(0));binding=dict(cohort=m.NEW,canonical_spec_sha256=m.sha(f.r/'control/specs'/(m.NEW+'.json')),host_cpu=cpu,resolved_spec_sha256=f.e.jsonsha(dict(updated,host_cpu=cpu)))
put(f.r/'control/dispatch_bindings'/(m.NEW+'.json'),binding);put(f.r/'control/POOL_DISPATCH_RESERVATIONS.json',{'claims':{m.NEW:{'host_cpu':cpu}}})
for item in updated['runtime_files']:
 target=f.r/item['target'];target.parent.mkdir(parents=True,exist_ok=True);target.symlink_to(item['actual_realpath'])
f.e.assert_parent_lease=lambda:None;f.e.check_input=lambda spec:{'CPU_FIXTURE_ONLY':True};f.e.resources=lambda *args:{'physical_RAM_pass':True,'physical_disk_pass':True};f.e.base=lambda:types.SimpleNamespace(identity=lambda:{'CPU_FIXTURE_ONLY':True})
def git(argv,**kwargs):
 if argv[-2:]==['status','--porcelain']:return ''
 assert argv[-2:]==['rev-parse','HEAD']
 return(updated['core_commit']if argv[2]==updated['source_worktrees']['core']else updated['framework_commit'])+'\n'
with patch.object(f.e.subprocess,'check_output',side_effect=git):prepared=f.e.prepare(m.NEW)
ck('actual_native_prepare_accepts_V2_cohort_with_same_science_and_no_start',prepared['cohort']==m.NEW and prepared['scientific_starts']==0)
strict=load('supp_CPU_actual_strict',R/'tools/l2_strict.py');strict.R=f.r;out=f.r/'CPU_BINDING_OUT';out.mkdir()
(out/'DOWNSTREAM_FROZEN_SPEC.json').write_bytes((f.r/'control/specs'/(m.NEW+'.json')).read_bytes());put(out/'DISPATCH_BINDING.json',binding)
strict.dispatch_binding(m.NEW,f.e.spec_for(m.NEW),out,{'dispatch_binding_sha256':m.sha(f.r/'control/dispatch_bindings'/(m.NEW+'.json'))})
ck('actual_strict_dispatch_binding_supports_exact_new_identity',True)
f.close()
f=Fixture();f.run();view=f.store.dispatch_view(f.store.primary());view['points'][0]['program']='ILLEGAL_CHANGE'
result=m.make_primary_adaptive(previous,f.store,Journal())({},view,{})
ck('bad_dispatch_scope_fails_closed_preserving_existing_journal_no_proposals',not result['proposals']and result['requires_engineering_review']and result['existing_journal_preserved'])
readwrapper=m.make_ops_read(lambda path:f.store.primary(),f.store)
with patch.object(f.store,'dispatch_view',side_effect=OSError('CPU sidecar IO')):plain=readwrapper(f.r/'control/MATRIX_CURRENT.json')
ck('supplemental_view_IO_failure_returns_real_primary_not_fake_empty_scope',plain==f.store.primary()and readwrapper.last_issue is not None)
f.close()
output=dict(status='PASS',count=len(checks),checks=checks,source_sha256=m.sha(HERE/'supplemental_trial.py'),
 actual_native_source_sha256=actual_native_sha,actual_registry_source_sha256=m.sha(R/'tools/l2_registry.py'),actual_strict_source_sha256=m.sha(R/'tools/l2_strict.py'),
 qualification_scope='owned native temp FS+mock authority/lease/input/resource/Git; synthetic closed metadata, not an actual model or performance acceptance',
 real_negative_lineage_is_mocked_in_CPU_fixture=True,production_registry_grants=0,production_prepare_calls=0,model_starts=0,signals=0,production_mutations=0)
(HERE/'CPU_QUALIFICATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
