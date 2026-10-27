"""One explicitly supplemental SAME-CONFIG performance identity. No auto action.
Main-only registration; private dispatch read view; primary statistics untouched.
"""
import copy,hashlib,importlib.util,json,os,pathlib,threading,time,uuid
P=pathlib.Path
ROLE='SUPPLEMENTAL_NEW_PERFORMANCE_TRIAL'
OLD='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V1'
NEW='E2-DTCL2MLP-6df3a84b612086e8-DH-M16-V2'
OLD_UUID='19105d9d-7522-498e-bf1d-73fbf7aba766'
def encoded(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(encoded(v)).hexdigest()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def syncdir(p):
 fd=os.open(str(p),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def immutable(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);data=encoded(v)
 if p.exists():assert p.read_bytes()==data,'Immutable identity collision';return
 tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex+'.prepared')
 try:
  with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  try:os.link(tmp,p)
  except FileExistsError:assert p.read_bytes()==data,'Concurrent immutable collision'
  syncdir(p.parent)
 finally:tmp.unlink(missing_ok=True)

def scientific(spec):
 """Only identity labels and the EXISTING qualified dynamic RSS/AS vary."""
 v=copy.deepcopy(spec)
 for k in ('cohort','scientific_role','supplemental_trial_lineage','estimated_peak_model_RAM_bytes'):v.pop(k,None)
 for k in ('max_process_tree_rss_bytes','max_process_tree_vms_bytes'):v.get('limits',{}).pop(k,None)
 return v

def verify_lineage(plan):
 """Fresh exact pinned negative verifier; never constructs a fake closure."""
 lineage=plan['new_spec']['supplemental_trial_lineage'];path=P(lineage['negative_verifier_path'])
 assert sha(path)==lineage['negative_verifier_sha256']
 sp=importlib.util.spec_from_file_location('supplemental_negative_'+uuid.uuid4().hex,path)
 module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
 proof=module.verify_bundle(P(lineage['negative_certificate_path']).parent,lineage['negative_verifier_sha256'])
 assert proof['status']=='VERIFIED_TYPED_ENGINEERING_NEGATIVE_UNACCEPTED'
 assert proof['certificate_sha256']==lineage['negative_certificate_sha256']
 if lineage.get('negative_verification_policy')is not None:
  assert proof['verification_policy']==lineage['negative_verification_policy']
  assert proof['original_v1_verifier_pass_claimed']is False
 return proof

def validate_plan(plan):
 assert plan['schema']=='DTC_L2_MLP_SUPPLEMENTAL_TRIAL_PLAN_V1'
 assert plan['old_cohort']==OLD and plan['new_cohort']==NEW and plan['old_uuid']==OLD_UUID
 old=plan['old_spec'];new=plan['new_spec'];lineage=new['supplemental_trial_lineage']
 assert old['cohort']==OLD and new['cohort']==NEW and new['host_cpu']is None
 assert new['scientific_role']==ROLE and scientific(old)==scientific(new)
 assert new['profile']==new['downstream_profile']=='M16'and new['cell']=='DH'
 assert new['input_digest'].startswith('6df3a84b612086e8')
 assert lineage['role']==ROLE and lineage['original_failed_cohort']==OLD and lineage['original_uuid']==OLD_UUID
 assert lineage['primary_statistics_excluded']is True and lineage['validated_union_authorized']is False
 assert lineage['new_grants']==1 and lineage['refunds']==0 and lineage['reuse_old_UUID']is False
 assert digest(old)==plan['old_spec_sha256']and digest(new)==plan['new_spec_sha256']
 assert plan['scientific_identity_sha256']==digest(scientific(old))
 assert plan['new_point']['cohort']==NEW and plan['new_point']['scientific_role']==ROLE
 assert plan['new_point']['profile']=='M16'and plan['new_point']['input_digest']==new['input_digest']
 assert plan['new_point']['cell']=='DH'
 return True

class SupplementalRegistry:
 def __init__(self,root,engine,owner_lock,owner_assert,fault_hook=None,lineage_verifier=None):
  self.root=P(root);self.engine=engine;self.lock=owner_lock;self.owner_assert=owner_assert
  self.fault_hook=fault_hook;self.lineage_verifier=lineage_verifier;self.folder=self.root/'control/supplemental_trial_registry_v1';self.last_issue=None
 def checkpoint(self,name):
  if self.fault_hook:self.fault_hook(name)
 def assert_owner(self):
  assert threading.current_thread()is threading.main_thread();self.owner_assert()
  plan=self.engine.registered()[3]
  assert os.getpid()==plan['parent_pid'],'Only existing parent owner may register'
  start=int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])
  assert start==plan['parent_start_ticks'],'Existing owner generation changed'
 def primary(self):
  scope=read(self.root/'control/SCOPE.json');matrix=read(self.root/'control/MATRIX_CURRENT.json')
  assert matrix['base_scope_sha256']==sha(self.root/'control/SCOPE.json')
  points={p['cohort']:p for p in matrix['points']};assert len(points)==len(matrix['points'])
  assert all(points.get(p['cohort'])==p for p in scope['points'])
  assert not any(p.get('scientific_role')==ROLE or p['cohort']==NEW for p in matrix['points'])
  return matrix
 def check(self,plan):
  validate_plan(plan)
  for pin in plan['source_and_evidence_pins']:assert sha(pin['path'])==pin['sha256'],pin['path']
  _,_,q,_=self.engine.registered();matrix=self.primary()
  assert q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
  assert q['admitted_specs'][OLD]==plan['old_spec_sha256']
  assert self.engine.canonical(OLD)==plan['old_spec']
  assert q['consumed'][OLD]['uuid']==OLD_UUID,'Original failed generation changed'
  assert not q['consumed'][OLD].get('execution_receipt'),'Do not reinterpret original missing closure'
  return q,matrix
 def prepare(self,plan,authorization):
  q,matrix=self.check(plan);tx=digest(plan);folder=self.folder/tx
  assert callable(self.lineage_verifier),'Fresh real lineage verifier is mandatory before any grant'
  lineage_proof=self.lineage_verifier(plan)
  assert lineage_proof['cohort']==OLD and lineage_proof['uuid']==OLD_UUID
  assert lineage_proof['performance_accepted']is False and lineage_proof['accepted_cycles']is None
  assert lineage_proof['certificate_sha256']==plan['new_spec']['supplemental_trial_lineage']['negative_certificate_sha256']
  expected=dict(approved_plan_sha256=tx,cohort=NEW,additional_starts=1,primary_statistics_unchanged=True)
  assert all(authorization.get(k)==v for k,v in expected.items()),'Main authorization binding missing'
  p=folder/'PREPARED.json'
  if p.exists():
   value=read(p);assert value['plan']==plan and value['authorization']==authorization;return folder,value
  assert NEW not in q['admitted_specs'],'New identity already exists without prepared transaction'
  assert not(self.root/'control/qualification_ledger'/(NEW+'.INTENT.json')).exists()
  value=dict(schema='SUPPLEMENTAL_TRIAL_PREPARED_V1',txid=tx,plan=copy.deepcopy(plan),authorization=copy.deepcopy(authorization),lineage_verification=copy.deepcopy(lineage_proof),
   authority_before=dict(budget=q['budget'],remaining=q['remaining'],consumed_uuids={c:v['uuid']for c,v in q['consumed'].items()}),
   primary_matrix_sha256=sha(self.root/'control/MATRIX_CURRENT.json'),primary_scope_sha256=sha(self.root/'control/SCOPE.json'))
  immutable(p,value);return folder,value
 def reconcile(self,folder,prepared):
  plan=prepared['plan'];q,matrix=self.check(plan);tx=prepared['txid']
  records=[r for r in q.get('authorized_supplemental_trials',[])if r['txid']==tx]
  if NEW not in q['admitted_specs']:
   assert not records,'Authority record without admitted spec'
   assert not(P(folder)/'COMMITTED.json').exists(),'Committed grant absent from authority: never reset or regrant'
   assert not(self.root/'control/qualification_ledger'/(NEW+'.INTENT.json')).exists(),'Consumed witness without authority'
   assert not(self.root/'control/dispatch_bindings'/(NEW+'.json')).exists(),'Prior admitted identity binding without authority'
   return dict(state='UNGRANTED_SAFE_TO_CONTINUE',new_grants=0)
  assert len(records)==1 and records[0]['new_cohort']==NEW and records[0]['initial_spec_sha256']==plan['new_spec_sha256']
  spec=self.engine.canonical(NEW)
  assert digest(scientific(spec))==plan['scientific_identity_sha256']
  assert spec['supplemental_trial_lineage']==plan['new_spec']['supplemental_trial_lineage']and spec['scientific_role']==ROLE
  assert sha(self.root/'control/SCOPE.json')==prepared['primary_scope_sha256']
  prior=prepared['authority_before']['consumed_uuids']
  assert all(q['consumed'].get(c,{}).get('uuid')==u for c,u in prior.items())
  if NEW in q['consumed']:assert q['consumed'][NEW]['uuid']!=OLD_UUID,'Old UUID illegally reused'
  committed=dict(schema='SUPPLEMENTAL_TRIAL_COMMITTED_V1',txid=tx,new_cohort=NEW,role=ROLE,
   plan_sha256=digest(plan),initial_spec_sha256=plan['new_spec_sha256'],scientific_identity_sha256=plan['scientific_identity_sha256'],
   point=plan['new_point'],new_grants=1,refunds=0,primary_scope_unchanged=True,primary_matrix_not_written=True,
   final_statistics_destination='SUPPLEMENTAL_ONLY_NO_AUTOMATIC_UNION')
  immutable(P(folder)/'COMMITTED.json',committed)
  return dict(state='COMMITTED_RECONCILED',new_grants=0,already_consumed=NEW in q['consumed'],cohort=NEW)
 def register(self,plan,authorization):
  self.assert_owner()
  with self.lock:
   folder,prepared=self.prepare(plan,authorization);self.checkpoint('AFTER_PREPARED')
   status=self.reconcile(folder,prepared)
   if status['state']=='COMMITTED_RECONCILED':return status
   before_primary=sha(self.root/'control/MATRIX_CURRENT.json')
   immutable(self.root/'control/specs'/(NEW+'.json'),plan['new_spec'])
   immutable(self.root/'control'/(NEW+'_SPEC.json'),plan['new_spec']);self.checkpoint('AFTER_SPEC_PUBLICATION')
   def grant(reg):
    q=reg['registered_future_requests'][self.engine.REQ]
    assert NEW not in q['admitted_specs']and NEW not in q['consumed']
    assert not any(r['txid']==prepared['txid']for r in q.get('authorized_supplemental_trials',[]))
    assert q['admitted_specs'][OLD]==plan['old_spec_sha256']and q['consumed'][OLD]['uuid']==OLD_UUID
    q['admitted_specs'][NEW]=sha(self.root/'control/specs'/(NEW+'.json'))
    q['admitted_inputs'][plan['new_spec']['input_digest']]['specs'].append(NEW)
    q['budget']+=1;q['remaining']+=1
    q.setdefault('authorized_supplemental_trials',[]).append(dict(txid=prepared['txid'],new_cohort=NEW,
     initial_spec_sha256=plan['new_spec_sha256'],plan_sha256=digest(plan),role=ROLE,additional_starts=1,refunds=0))
   self.engine.update_authority(grant);self.checkpoint('AFTER_AUTHORITY')
   assert sha(self.root/'control/MATRIX_CURRENT.json')==before_primary,'Registration must not change primary matrix'
   result=self.reconcile(folder,prepared);self.checkpoint('AFTER_COMMITTED');return dict(result,new_grants=1)
 def recover_pending(self):
  self.assert_owner()
  with self.lock:
   results=[]
   for p in sorted(self.folder.glob('*/PREPARED.json')):
    results.append(dict(txid=p.parent.name,**self.reconcile(p.parent,read(p))))
   return results # ungranted stays ungranted; only register(plan,authorization) may add1
 def dispatch_view(self,primary):
  expected=self.primary();assert primary==expected,'Dispatch source is not exact primary matrix'
  view=copy.deepcopy(primary);added=[]
  for p in sorted(self.folder.glob('*/COMMITTED.json')):
   commit=read(p);prepared=read(p.with_name('PREPARED.json'));plan=prepared['plan'];q,_=self.check(plan)
   assert digest(plan)==commit['plan_sha256']and commit['new_cohort']==NEW
   spec=self.engine.canonical(NEW);assert digest(scientific(spec))==plan['scientific_identity_sha256']
   assert all(point['cohort']!=NEW for point in view['points'])
   view['points'].append(copy.deepcopy(commit['point']));added.append(NEW)
  view['supplemental_dispatch_view']=dict(schema='SUPPLEMENTAL_DISPATCH_ONLY_VIEW_V1',
   primary_matrix_sha256=digest(primary),supplemental_cohorts=added,primary_statistics_unchanged=True)
  return view

def make_ops_read(previous_read,registry):
 """Return callable only; Main may install on its EXISTING ops module instance."""
 target=registry.root/'control/MATRIX_CURRENT.json'
 def wrapper(path):
  value=previous_read(path)
  if P(path)!=target:return value
  try:
   result=registry.dispatch_view(value);wrapper.last_issue=None;return result
  except Exception as error:
   wrapper.last_issue=repr(error);return value # real primary continues; no unverified supplemental admission
 wrapper.previous_read=previous_read;wrapper.last_issue=None;return wrapper

def make_primary_adaptive(previous_recommend,registry,existing_journal):
 """Preserve current typed-terminal+full35+same journal recommendation chain."""
 def wrapper(summary,scope,history=None):
  try:
   primary=registry.primary();extras=[p for p in scope['points']if p.get('scientific_role')==ROLE]
   stripped=copy.deepcopy(scope);stripped['points']=[p for p in scope['points']if p.get('scientific_role')!=ROLE]
   stripped.pop('supplemental_dispatch_view',None)
   assert stripped==primary and all(p['cohort']==NEW for p in extras)
   return previous_recommend(summary,primary,history or{})
  except Exception as error:
   hold=dict(schema='SUPPLEMENTAL_VIEW_ADAPTIVE_HOLD_V1',proposals=[],scientific_stage_complete=False,
    adoption_ready=False,requires_engineering_review=True,state='SUPPLEMENTAL_VIEW_ENGINEERING_HOLD',error=repr(error),healthy_models_continue=True)
   try:
    guarded=existing_journal.guard_decision(hold);assert isinstance(guarded,dict);return dict(guarded,proposals=[],scientific_stage_complete=False,adoption_ready=False,requires_engineering_review=True)
   except Exception as guard_error:return dict(hold,registry_journal_status=dict(safe_for_scientific_completion=False,error=repr(guard_error)))
 wrapper.previous_recommend=previous_recommend;wrapper.existing_journal=existing_journal;return wrapper

def supplemental_result(registry,consumer_accepted,verify_archive=None):
 """Independent one-row table only; never changes primary summary or slot."""
 rows=[]
 for p in sorted(registry.folder.glob('*/COMMITTED.json')):
  prepared=read(p.with_name('PREPARED.json'));plan=prepared['plan'];q,_=registry.check(plan);spec=registry.engine.canonical(NEW)
  row=dict(cohort=NEW,role=ROLE,profile='M16',input_digest=spec['input_digest'],accepted=False,cycles=None,
   primary_statistics_excluded=True,validated_union_authorized=False,lineage=spec['supplemental_trial_lineage'])
  spent=q['consumed'].get(NEW);rp=registry.root/'analysis'/(NEW+'.RESULT.json')
  if not spent:row['state']='SUPPLEMENTAL_UNSTARTED'
  elif not rp.exists():row.update(state='SUPPLEMENTAL_SPENT_AWAITING_STRICT_NO_RETRY',uuid=spent['uuid'])
  else:
   value=read(rp);assert spent['uuid']==value['uuid']!=OLD_UUID
   row.update(state=value['state'],uuid=value['uuid'],RESULT_path=str(rp),RESULT_sha256=sha(rp))
   if consumer_accepted(value):
    assert callable(verify_archive),'Real archive/native-restore verifier mandatory for supplemental acceptance'
    assert verify_archive(NEW)==value['archive']
    proof=value['proof'];assert proof['cohort']==NEW and proof['input_digest']==spec['input_digest']and proof['cell']=='DH'
    assert proof['effective_options']==spec['expected_options']and proof['profile']=='M16'
    for key in ('core_commit','framework_commit','binary_sha256'):assert proof[key]==spec[key]
    assert dict(CTA=proof['CTA'],instructions=proof['instructions'],kernels=proof['kernel_count'])==spec['expected']
    ip=registry.root/'control/qualification_ledger'/(NEW+'.INTENT.json');intent=read(ip);out=P(intent['output']);done=read(ip.with_name(NEW+'.DONE.json'))
    assert done==spent['execution_receipt']==read(out/'NATIVE_EXIT.json')
    assert done['stop_reason']is None and done['launcher_wait_returncode']==0 and done['native_simulator_observed']is True
    assert spent['intent_sha256']==sha(ip)
    strict_path=out/'L2_STRICT.json';assert read(strict_path)==proof
    assert proof['raw_gzip_sha256']==done['raw_sha256']
    qualification=read(registry.root/'DTC/control'/('SCIENCE_QUALIFICATION_'+NEW+'.json'))
    assert qualification['uuid']==spent['uuid']and qualification['strict_sha256']==sha(strict_path)
    assert intent['uuid']==spent['uuid']and 'additional_shared_json_io_binding'in intent
    extra=proof['additional_shared_json_io_strict'];assert extra['status']=='PASS_SHARED_JSON_IO_AND_ORIGINAL_STRICT'
    assert sha(extra['sidecar_path'])==extra['sidecar_sha256']
    row.update(accepted=True,cycles=value['cycles'],state='SUPPLEMENTAL_PERFORMANCE_ACCEPTED_SEPARATE_TABLE',
     strict_path=str(strict_path),strict_sha256=sha(strict_path),
     natural_DONE_path=str(ip.with_name(NEW+'.DONE.json')),natural_DONE_sha256=sha(ip.with_name(NEW+'.DONE.json')))
  rows.append(row)
 return dict(schema='DTC_L2_MLP_SUPPLEMENTAL_PERFORMANCE_TABLE_V1',rows=rows,primary_results_modified=False,
  original_M16_full35_inference_HOLD_preserved=True,automatic_union=False,GM=None)
