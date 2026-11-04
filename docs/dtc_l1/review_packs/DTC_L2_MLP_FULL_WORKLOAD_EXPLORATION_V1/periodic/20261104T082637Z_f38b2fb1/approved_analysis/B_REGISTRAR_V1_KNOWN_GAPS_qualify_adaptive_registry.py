"""Isolated authority/selection fixtures; real sealed A70 candidate bytes.
No production selection, registration, source edits, controller or model.
"""
import pathlib,json,hashlib,copy,sys,threading,types,tempfile,fcntl,importlib.util,ast
sys.dont_write_bytecode=True
P=pathlib.Path;A=P('/root/share/mnt164/huangrulin/host174_storage_recovery/dtc_l2_mlp_full_workload_exploration_v1');R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');D=A/'agents/B/adaptive_batch_registry_v1';C=A/'agents/A/adaptive_ch_ad1_candidates_v1';S=types.SimpleNamespace
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('private_B_adaptive_registry',D/'adaptive_batch_registry.py');adapter=load('private_A70_exact_adapter',D/'a_candidate_adapter.py')
catalog,source=adapter.normalize(C,R)
(D/'A70_NORMALIZED_CATALOG_REFERENCE.json').write_bytes(m.raw(catalog));(D/'A70_SOURCE_MANIFEST_REFERENCE.json').write_bytes(m.raw(source))
class Engine:
 def __init__(self,root,q):self.root=root;self.q=q;self.inside=False;self.calls=0;self.ex_proved=False;self.fail=False;self.peers={'old72':{'budget':288,'keep':'OLD'},'PQPS':{'budget':18,'keep':'OLD'}}
 def assert_parent_lease(self):assert not self.inside
 def registered(self):assert not self.inside;return None,None,copy.deepcopy(self.q),{}
 def canonical(self,c):
  assert not self.inside;s=m.read(self.root/'control/specs'/(c+'.json'));assert m.sha(self.root/'control/specs'/(c+'.json'))==m.sha(self.root/'control'/(c+'_SPEC.json'))==self.q['admitted_specs'][c];return s
 def update_authority(self,fn):
  self.calls+=1
  with(self.root/'CPU_EX.lock').open('a+b')as one:
   fcntl.flock(one,fcntl.LOCK_EX)
   with(self.root/'CPU_EX.lock').open('a+b')as two:
    try:fcntl.flock(two,fcntl.LOCK_EX|fcntl.LOCK_NB);raise AssertionError('INDEPENDENT_FD_EX_NOT_HELD')
    except BlockingIOError:self.ex_proved=True
   reg={'registered_future_requests':{m.REQ:copy.deepcopy(self.q),**copy.deepcopy(self.peers)},'old_source_history':['KEEP'],'qualification_history':['KEEP']};old=copy.deepcopy(reg);self.inside=True
   try:fn(reg)
   finally:self.inside=False
   assert all(reg['registered_future_requests'][k]==v for k,v in self.peers.items())and reg['old_source_history']==old['old_source_history']and reg['qualification_history']==old['qualification_history']
   if self.fail:self.fail=False;raise RuntimeError('CPU_AFTER_CALLBACK_BEFORE_AUTHORITY_PUBLICATION')
   self.q=reg['registered_future_requests'][m.REQ]
def fixture(profiles=('F128',),early=False):
 root=P(tempfile.mkdtemp(prefix='CPU_BATCH_REGISTRY_',dir=D));(root/'control/specs').mkdir(parents=True);(root/'control/qualification_ledger').mkdir();(root/'control/dispatch_bindings').mkdir();(root/'control/MATRIX_CURRENT.json').write_bytes((R/'control/MATRIX_CURRENT.json').read_bytes())
 cp=root/'CATALOG.json';cp.write_bytes(m.raw(catalog));sp=root/'SOURCES.json';sp.write_bytes(m.raw(source));scope=m.read(C/'contracts/SCOPE_INITIAL.json');digests=catalog['frozen_input_digests'];old='KEEP_OLD_NEGATIVE_ID'
 q=dict(request=m.REQ,qualification_only=True,budget=1,remaining=0,admitted_specs={old:'KEEP_SHA'},consumed={old:{'uuid':'KEEP_UUID','performance_accepted':False}},admitted_inputs={d:{'specs':[old]if d==digests[0]else[]}for d in digests},authorized_incident_recovery_trials=[{'KEEP':'IR11'}],additional_operational_overlays={'KEEP':'OLD'},old_primary_membership='EXACT350_UNCHANGED')
 completion=[];terminal=root/'CPU_TERMINAL_ROWS';terminal.mkdir()
 for point in scope['points']:
  path=terminal/(point['cohort']+'.json');v=dict(cohort=point['cohort'],uuid='CPU_TERMINAL_IDENTITY_STANDIN',cycles=123,state='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE',proof={'performance_accepted':True});path.write_bytes(m.raw(v));completion.append(dict(cohort=point['cohort'],state='ACCEPTED',cycles=123,IR_R2_engineering_substitution=False,terminal_evidence_path=str(path),terminal_evidence_sha256=m.sha(path)))
 completion_path=root/'COMPLETION_CPU_STANDIN.json';completion_path.write_bytes(m.raw(dict(schema='INITIAL35_SINGLE_FACTOR_TERMINAL_STATUS_EVIDENCE_V1',request=m.REQ,frozen_scope_sha256=m.FROZEN_SCOPE_SHA,all_initial350_statuses_terminal=True,pending_count=0,running_count=0,unknown_count=0,cell_evidence=completion,CPU_ONLY_NOT_REAL_COMPLETION=True)))
 selected=[r for r in catalog['rows']if r['profile']in profiles];vectors=sorted([dict(profile=p,cell='CH',parameters=next(r['parameters']for r in selected if r['profile']==p))for p in profiles],key=lambda v:(v['profile'],v['cell']))
 auth=R/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';ap=root/'APPROVAL_CPU_STANDIN.json';ev=A/'agents/E/results_refresh_20261028_v4/EVIDENCE.json'
 approval=dict(schema='ADAPTIVE_BATCH_STAGE_SELECTION_APPROVAL_V1',request=m.REQ,approved_for_registration=True,candidate_catalog_sha256=m.sha(cp),source_manifest_sha256=m.sha(sp),registrar_source_sha256=m.sha(D/'adaptive_batch_registry.py'),same_goal_authorization_path=str(auth),same_goal_authorization_sha256=m.sha(auth),selected_cohorts=[r['cohort']for r in selected],selected_vectors=vectors,new_grants=len(selected),refunds=0,automatic_retry=False,changes_initial350_membership=False,initial_single_factor_completion={'path':str(completion_path),'sha256':m.sha(completion_path)},selection_kind='MATCHED_CH_FOLLOWUP',execution_order_mode='ORIGINAL_CANDIDATE_GATE_SATISFIED',matched_DH_evidence={'path':str(ev),'sha256':m.sha(ev)},matching_purpose='MODERATE_UNIFORM_RESOURCE_CONTROL',explicit_uniform_control_justification='CPU_ONLY source-bound uniform moderate/high comparison, not an actual selection',formal_winner_selected=False,formal_adoption_authorized=False,IR_R2_engineering_union_authorized=False,CPU_ONLY_NOT_MAIN_APPROVAL=True)
 if early:
  approval['execution_order_mode']='EXPLICIT_ROOT_SUPERSESSION_FOR_NECESSARY_CH';approval['matching_purpose']='EFFECTIVE_DIRECTION_MATCH';approval.pop('initial_single_factor_completion')
  rp=root/'SUPERSESSION_CPU_STANDIN.json';rp.write_bytes(m.raw(dict(schema='DTC_MAIN_AD1_MATCHED_CH_EXECUTION_ORDER_REVIEW_V1',request=m.REQ,status='APPROVED_EXECUTION_ORDER_REVISION_ONLY',owner_pid=1498278,owner_start_ticks=977758783,candidate_catalog_sha256=m.sha(cp),selected_cohorts=approval['selected_cohorts'],earlier_necessary_CH_matching_approved=True,original_candidate_bytes_unchanged=True,parameter_families_inputs_physics_unchanged=True,formal_adoption_authorized=False,matched_DH_evidence_sha256=m.sha(ev),original_candidate_batch_gates=catalog['candidate_batch_activation_gates'],CPU_ONLY_NOT_MAIN_REVIEW=True)))
  approval['superseding_execution_order_review']={'path':str(rp),'sha256':m.sha(rp)}
 ap.write_bytes(m.raw(approval))
 qa=root/'SOURCE_QA_CPU_STANDIN.json';rb=root/'READBACK_CPU_STANDIN.json';qa.write_bytes(m.raw(dict(status='PASS_ADAPTIVE_BATCH_ISOLATED_TRANSACTION_CPU',source_sha256=m.sha(D/'adaptive_batch_registry.py'),pure_EX_callback_qualified=True,actual_candidate_schema_qualified=False,qualification_only=True)));rb.write_bytes(m.raw(dict(verified=True,source_sha256=m.sha(D/'adaptive_batch_registry.py'),QA_sha256=m.sha(qa),qualification_only=True)))
 dep=root/'source_dependency.txt';dep.write_text('CPU_CLEAN_SOURCE')
 cfg=dict(schema='ADAPTIVE_BATCH_REGISTRY_CONFIGURATION_V1',qualification_only=True,source_sha256=m.sha(D/'adaptive_batch_registry.py'),catalog_path=str(cp),catalog_sha256=m.sha(cp),approval_path=str(ap),approval_sha256=m.sha(ap),source_manifest_path=str(sp),source_manifest_sha256=m.sha(sp),QA_path=str(qa),QA_sha256=m.sha(qa),readback_path=str(rb),readback_sha256=m.sha(rb),dependency_pins={str(dep):m.sha(dep),str(D/'a_candidate_adapter.py'):m.sha(D/'a_candidate_adapter.py')},source_worktree_checks=[],same_goal_authorization_path=str(auth),same_goal_authorization_sha256=m.sha(auth),initial350_matrix_sha256=m.sha(root/'control/MATRIX_CURRENT.json'))
 e=Engine(root,q);frame=S(f_locals={'engine':e,'res':S(DTC_LARGE_JOB_AGING_INSTALLED=S(lock=threading.RLock()))});reg=m.AdaptiveBatchRegistry(root,e,frame,cfg);return root,e,reg,dep
checks=[]
def test(name,fn):fn();checks.append(dict(case=name,status='PASS'))
def reject(fn):
 try:fn()
 except(AssertionError,RuntimeError):return
 raise AssertionError('EXPECTED_REJECTION')
def positive():
 root,e,reg,dep=fixture(('F128','F256'));before=copy.deepcopy(e.q);files_before=set(root.rglob('*'));p=reg.prepare();assert set(root.rglob('*'))==files_before,'PREPARE_MUST_BE_READONLY'
 forged=copy.deepcopy(p);forged['batch_id']='FORGED';reject(lambda:reg.commit(forged));assert e.calls==0
 forged=copy.deepcopy(p);forged['frozen_scope_utf8']='{}';reject(lambda:reg.commit(forged));assert e.calls==0
 value=reg.commit(p);assert value['new_grants']==70 and e.calls==1 and e.ex_proved and e.q['budget']==71 and e.q['remaining']==70
 again=reg.commit(p);assert again['new_grants']==0 and e.calls==1
 assert e.q['consumed']==before['consumed']and e.q['authorized_incident_recovery_trials']==before['authorized_incident_recovery_trials']and m.sha(root/'control/MATRIX_CURRENT.json')==reg.cfg['initial350_matrix_sha256']
 c=p['rows'][0]['spec']['cohort'];spec=e.canonical(c);spec['estimated_peak_model_RAM_bytes']+=1024;spec['limits']['max_process_tree_rss_bytes']+=2048;spec['limits']['max_process_tree_vms_bytes']+=4096
 for path in[root/'control/specs'/(c+'.json'),root/'control'/(c+'_SPEC.json')]:path.write_bytes(m.raw(spec))
 e.q['admitted_specs'][c]=m.objsha(spec);assert reg.reconcile(p)['state']=='COMMITTED_RECONCILED'and e.calls==1
test('actual_A70_bytes_readonly_prepare_EX_grant70_idempotent_no_old_budget_or_IR_UUID_change_postgrant_resource_refresh',positive)
def partial(stage):
 root,e,reg,dep=fixture();p=reg.prepare();hit=[False]
 def fail(s):
  if s==stage and not hit[0]:hit[0]=True;raise RuntimeError('CPU_PARTIAL '+stage)
 reg.fault_hook=fail;reject(lambda:reg.commit(p));reg.fault_hook=None
 value=reg.commit(p);assert value['state']=='COMMITTED_RECONCILED'and e.q['budget']==36 and len(e.q.get('authorized_parameter_batches',[]))==1
test('partial_first_spec_sameproposal_forward_reconcile_exact_grant_once',lambda:partial('AFTER_FIRST_SPEC'))
test('crash_after_authority_before_COMMITTED_reconcile_no_second_grant',lambda:partial('AFTER_AUTHORITY'))
def callbackfail():
 root,e,reg,dep=fixture();p=reg.prepare();e.fail=True;reject(lambda:reg.commit(p));assert e.q['budget']==1 and e.calls==1
 reg.commit(p);assert e.q['budget']==36 and e.calls==2 and len(e.q['authorized_parameter_batches'])==1
test('callback_after_ex_before_registry_publication_sameproposal_reconcile_no_refund',callbackfail)
def dirty():
 root,e,reg,dep=fixture();dep.write_text('SOURCE_DRIFT');reject(reg.prepare);assert e.calls==0
 # Exercise actual worktree-clean check with private subprocess standin; no Git
 # command or global subprocess monkeypatch. The implementation would run only
 # exact readonly git rev-parse/status before EX in a future real Main prepare.
 root,e,reg,dep=fixture();reg.cfg['source_worktree_checks']=[{'path':'CPU_ONLY_WORKTREE','commit':'CPU_HEAD'}];old=m.subprocess
 m.subprocess=S(run=lambda argv,**kw:S(stdout='CPU_HEAD\n'if'rev-parse'in argv else' M dirty-source.cpp\n'))
 try:reject(reg.prepare)
 finally:m.subprocess=old
 assert e.calls==0
test('source_pin_or_dirty_worktree_refused_before_grant',dirty)
def badselection():
 root,e,reg,dep=fixture();app=m.read(reg.cfg['approval_path']);app['selected_cohorts'].pop();app['new_grants']-=1;P(reg.cfg['approval_path']).write_bytes(m.raw(app));reg.cfg['approval_sha256']=m.sha(reg.cfg['approval_path']);reject(reg.prepare);assert e.calls==0
 root,e,reg,dep=fixture();app=m.read(reg.cfg['approval_path']);cp=P(app['initial_single_factor_completion']['path']);v=m.read(cp);v['cell_evidence'][0]['IR_R2_engineering_substitution']=True;cp.write_bytes(m.raw(v));app['initial_single_factor_completion']['sha256']=m.sha(cp);P(reg.cfg['approval_path']).write_bytes(m.raw(app));reg.cfg['approval_sha256']=m.sha(reg.cfg['approval_path']);reject(reg.prepare);assert e.calls==0
test('partial_population_or_IR_R2_substitution_sourcebound_approval_refused',badselection)
def forbiddenrole():
 row=catalog['rows'][0];s=m.read(row['spec_path']);base=m.read(row['base_spec_path']);s['scientific_role']='PRIMARY';reject(lambda:m.validate_new_science(s,base,row))
 s=m.read(row['spec_path']);s['expected_options']['-gpgpu_clock_domains']=['BAD_CLOCK'];reject(lambda:m.validate_new_science(s,base,row))
test('newrole_cannot_masquerade_primary_or_change_GPU_science',forbiddenrole)
def early():
 root,e,reg,dep=fixture(('F256',),early=True);p=reg.prepare();assert p['source_bound_selection']['selection_kind']=='MATCHED_CH_FOLLOWUP'and 'initial_single_factor_completion'not in p['source_bound_selection']
 assert all(i['spec']['adaptive_registration_binding']['original_candidate_spec_sha256']==i['row']['spec_sha256']and i['spec']['adaptive_trial_lineage']['full35_single_factor_gate_complete']is False for i in p['rows'])
 reg.commit(p);assert e.q['budget']==36 and e.q['authorized_parameter_batches'][0]['selection_kind']=='MATCHED_CH_FOLLOWUP'
 root,e,reg,dep=fixture(('F256',),early=True);app=m.read(reg.cfg['approval_path']);app.pop('superseding_execution_order_review');P(reg.cfg['approval_path']).write_bytes(m.raw(app));reg.cfg['approval_sha256']=m.sha(reg.cfg['approval_path'])
 try:reg.prepare();raise AssertionError('MISSING_SUPERSESSION_MUST_HOLD')
 except KeyError:pass
 assert e.calls==0
test('early_F256_CH_sourcebound_same31_DH_effect_and_explicit_supersession_required_old_candidate_gate_unchanged',early)
result=dict(schema='B_ADAPTIVE_BATCH_REGISTRY_FOCUSED_CPU_V1',status='PASS_ADAPTIVE_BATCH_ISOLATED_TRANSACTION_CPU',source_sha256=m.sha(D/'adaptive_batch_registry.py'),adapter_sha256=m.sha(D/'a_candidate_adapter.py'),driver_sha256=m.sha(__file__),A_manifest_sha256=adapter.A_MANIFEST_SHA,pure_EX_callback_qualified=True,actual_candidate_schema_qualified=True,actual_stage_selection_or_completion_qualified=False,production_release_eligible=False,count=len(checks),checks=checks,production_actions=0,models_started=0,qualification_only=True,limitations=['Uses actual sealed A70 specs/configs/parent snapshots and exact adapter; fakeauthority, completion350 and Mainselection documents are explicit CPU-only standins.','No actual grant/stage selection/native role generation/worker/scope/consumer qualification or installation. Actual full35 completion remains pending.','No Git operation was run; dirty-worktree branch used private subprocess standin. No global patch, controller, model, signal or budget change.'])
(D/'CPU_QUALIFICATION.json').write_bytes(m.raw(result));print(json.dumps(dict(status=result['status'],count=len(checks),source_sha256=result['source_sha256'],adapter_sha256=result['adapter_sha256'],QA_sha256=m.sha(D/'CPU_QUALIFICATION.json')),indent=2))
