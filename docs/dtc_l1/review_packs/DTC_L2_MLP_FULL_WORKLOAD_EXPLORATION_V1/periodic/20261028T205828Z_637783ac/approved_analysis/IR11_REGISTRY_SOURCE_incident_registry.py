"""Explicit independent IR11 registration; no runtime/scope installation."""
import copy,hashlib,importlib.util,json,os,pathlib,threading,types
P=pathlib.Path;ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';ROLE='INCIDENT_RECOVERY_PERFORMANCE_TRIAL'
PLAN_SHA='72ce5472b5d3fc76d4f8d27c3aa3f4f7ad3d224a5ada3eaba88b3f1a2e6feff5';MANIFEST_SHA='5914080d60acf51cf0ffa47046acb767657dc64b292e300eeed4146bf12d7cd2';IDENTITY_SHA='35d28c842c0b53ace6eb08e46094f058b1e87770f195dcf9f592aac611ffeb37';ACCEPTED_SHA='2407305a59e9af52b07065a36816fdcecc559a6fa65d56b9d6c4e54f2c32f477'
NATIVE_SHA='e8276aadbb243b29166d89e5e937de260e6017061b475b62ac9c6c6f3dc3825a';OPS_SHA='a53f4933d2f0a7479a15d0e6dd8aa0501c4762d6b2161363b9467472a43fc1dc'
MATRIX_SHA='0ca2df7320392eb55eae1eecd23d2f5df0316df1cfc6e757d8dee9e27f0dcdf8';SCOPE_SHA='5f079aed36eca8dd62906bdfaa68006d3b3f27964c506a03361f2fab0908d1d2'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(js(v)).hexdigest()
def scientific(v,keys):return hashlib.sha256(json.dumps({k:v[k]for k in keys},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def immutable(path,value):
 p=P(path);data=js(value);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data,'IMMUTABLE_CONFLICT';return
 t=p.with_name('.'+p.name+'.'+os.urandom(8).hex())
 try:
  with t.open('xb')as h:h.write(data);h.flush();os.fsync(h.fileno())
  try:os.link(t,p)
  except FileExistsError:assert p.read_bytes()==data
  t.unlink();fd=os.open(p.parent,os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if t.exists():t.unlink()
def pure_identity(spec,row,keys,original,expected_lineage):
 assert spec['cohort']==row['new_cohort']and spec['host_cpu']is None and spec['scientific_role']==ROLE and spec['request']==REQ
 assert scientific(spec,keys)==scientific(original,keys)==row['science_projection_sha256']
 assert spec['expected_options']==original['expected_options']and spec['native_simulator_argv']==original['native_simulator_argv']
 assert spec['incident_recovery_trial_lineage']==expected_lineage
 lin=spec['incident_recovery_trial_lineage'];assert lin['original_cohort']==row['original_cohort']and lin['original_uuid']==row['original_uuid']and lin['original_negative_RESULT_sha256']==row['original_negative_RESULT_sha256']and lin['original_DONE_sha256']==row['original_DONE_sha256']and lin['original_raw_sha256']==row['original_raw_sha256']
 assert lin['new_grants']==1 and lin['refunds']==0 and lin['automatic_retry']is False and lin['primary_statistics_excluded']is True and lin['validated_union_authorized']is False

class IncidentRecoveryRegistry:
 def __init__(self,root,engine,frame,configuration,fault_hook=None):
  self.root=P(root);self.engine=engine;self.frame=frame;self.cfg=copy.deepcopy(configuration);self.lock=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED.lock;self.fault_hook=fault_hook
  self.transaction_id=digest(dict(schema='IR11_TRANSACTION_V1',configuration=self.cfg));self.folder=self.root/'control/incident_recovery_registry_v1'/self.transaction_id
 def checkpoint(self,name):
  if self.fault_hook:self.fault_hook(name)
 def owner(self):
  assert threading.current_thread()is threading.main_thread()and self.frame.f_locals['engine']is self.engine and self.frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED.lock is self.lock
  self.engine.assert_parent_lease();_,_,q,p=self.engine.registered();assert p['parent_pid']==os.getpid()and p['parent_start_ticks']==int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])and sha(self.engine.__file__)==NATIVE_SHA
  if self.cfg['qualification_only']:assert q.get('qualification_only')is True and self.root.resolve()!=ROOT
  else:assert self.root.resolve()==ROOT and not q.get('qualification_only',False)and isinstance(self.frame,types.FrameType)and sha(self.frame.f_code.co_filename)==OPS_SHA and P(self.engine.update_authority.__code__.co_filename).resolve()==ROOT/'tools/l2_native.py'
  return q,p
 def fresh(self):
  q,p=self.owner();cfg=self.cfg;assert cfg['schema']=='IR11_REGISTRATION_CONFIGURATION_V1'and cfg['source_sha256']==sha(__file__)
  for k,h in [('plan',PLAN_SHA),('manifest',MANIFEST_SHA),('identity_proof',IDENTITY_SHA),('accepted_snapshot',ACCEPTED_SHA)]:assert sha(cfg[k+'_path'])==cfg[k+'_sha256']==h
  for key in ['QA','readback']:assert sha(cfg[key+'_path'])==cfg[key+'_sha256']
  qa=read(cfg['QA_path']);rb=read(cfg['readback_path']);assert qa['status']=='PASS_IR11_ISOLATED_REGISTRY_CPU_QUALIFICATION'and qa['source_sha256']==cfg['source_sha256']and qa['real_independent_FD_EX_callback_pure']is True
  assert rb['verified']is True and rb['source_sha256']==cfg['source_sha256']and rb['QA_sha256']==cfg['QA_sha256']
  manifest=read(cfg['manifest_path'])
  for member in manifest['members']:assert sha(member['path'])==member['sha256']
  plan=read(cfg['plan_path']);rows=plan['rows'];assert len(rows)==len({r['new_cohort']for r in rows})==11 and plan['actual_new_grants']==plan['actual_model_starts']==0
  assert sha(self.root/'control/MATRIX_CURRENT.json')==MATRIX_SHA and sha(self.root/'control/SCOPE.json')==SCOPE_SHA and len(read(self.root/'control/MATRIX_CURRENT.json')['points'])==350
  assert q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
  known=read(cfg['accepted_snapshot_path'])['known_results_checks'];assert len(known)==324
  for r in known:assert sha(r['expected']['path'])==r['expected']['sha256']
  prepared_rows=[]
  for row in rows:
   old=row['original_cohort'];new=row['new_cohort'];assert new==old[:-3]+'-IR1-V1'
   original=self.engine.canonical(old);op=self.root/'control/specs'/(old+'.json');rp=self.root/'analysis'/(old+'.RESULT.json');dp=self.root/'control/qualification_ledger'/(old+'.DONE.json');spec=read(row['draft_spec']['path']);negative=read(rp);done=read(dp)
   assert sha(op)==q['admitted_specs'][old]==spec['incident_recovery_trial_lineage']['original_canonical_spec_sha256']and sha(rp)==row['original_negative_RESULT_sha256']and sha(dp)==row['original_DONE_sha256']
   assert done==q['consumed'][old]['execution_receipt']and done['uuid']==row['original_uuid']and done['source_disposition']=='SOURCE_KEEP'and done['raw_sha256']==row['original_raw_sha256']
   assert negative['proof']['performance_accepted']is False and negative['cycles']is None and negative['state']=='FAIL_L2MLP_ARCHIVED_NO_RETRY'
   pure_identity(spec,row,plan['science_projection_keys'],original,spec['incident_recovery_trial_lineage'])
   prepared_rows.append(dict(mapping=row,spec=spec,initial_spec_sha256=digest(spec),original_spec=original,old_receipt=copy.deepcopy(q['consumed'][old])))
  return q,p,plan,prepared_rows
 def expected_authorization(self):
  q,p=self.owner();return dict(transaction_id=self.transaction_id,role=ROLE,additional_starts=11,refunds=0,primary_statistics_excluded=True,validated_union_authorized=False,parent_pid=p['parent_pid'],parent_start_ticks=p['parent_start_ticks'])
 def _prepare(self,authorization):
  q,p,plan,rows=self.fresh();assert authorization==self.expected_authorization();path=self.folder/'PREPARED.json'
  if path.exists():
   v=read(path);assert v['configuration']==self.cfg and v['rows']==rows and v['authorization']==authorization;return v
  for r in rows:
   c=r['spec']['cohort'];assert c not in q['admitted_specs']and c not in q['consumed']and not any(x['cohort']==c for x in q.get('authorized_incident_recovery_trials',[]))
   for path in [self.root/'control/specs'/(c+'.json'),self.root/'control'/(c+'_SPEC.json'),self.root/'control/qualification_ledger'/(c+'.INTENT.json'),self.root/'control/dispatch_bindings'/(c+'.json')]:assert not path.exists()
  v=dict(schema='IR11_PREPARED_V1',transaction_id=self.transaction_id,configuration=self.cfg,authorization=authorization,rows=rows,science_keys=plan['science_projection_keys'],incident_id=plan['incident_id']);immutable(self.folder/'PREPARED.json',v);return v
 def prepare(self,authorization):
  with self.lock:p=self._prepare(authorization);return dict(state='PREPARED_NO_GRANT',transaction_id=self.transaction_id,path=str(self.folder/'PREPARED.json'),new_grants=0)
 def _reconcile(self,p):
  q,ep,plan,rows=self.fresh();assert p['rows']==rows and p['configuration']==self.cfg
  cs={r['spec']['cohort']for r in rows};present=cs&set(q['admitted_specs']);records=[r for r in q.get('authorized_incident_recovery_trials',[])if r.get('transaction_id')==self.transaction_id];batch=[r for r in q.get('authorized_incident_recovery_transactions',[])if r['transaction_id']==self.transaction_id]
  if not present:
   assert not records and not batch and not(self.folder/'COMMITTED.json').exists()
   for r in rows:
    c=r['spec']['cohort'];assert c not in q['consumed']and not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(self.root/'control/dispatch_bindings'/(c+'.json')).exists()
    for path in [self.root/'control/specs'/(c+'.json'),self.root/'control'/(c+'_SPEC.json')]:
     if path.exists():assert sha(path)==r['initial_spec_sha256']
   return dict(state='UNGRANTED_SAFE_TO_CONTINUE',new_grants=0)
  assert present==cs and len(records)==11 and len(batch)==1 and batch[0]['additional_starts']==11
  for r in rows:
   c=r['spec']['cohort'];s=self.engine.canonical(c);pure_identity(s,r['mapping'],p['science_keys'],r['original_spec'],r['spec']['incident_recovery_trial_lineage']);assert sha(self.root/'control/specs'/(c+'.json'))==q['admitted_specs'][c]
   record=next(x for x in records if x['cohort']==c);assert record['initial_spec_sha256']==r['initial_spec_sha256']and record['role']==ROLE and record['primary_statistics_excluded']is True and record['validated_union_authorized']is False
   assert q['admitted_inputs'][s['input_digest']]['specs'].count(c)==1
   if c in q['consumed']:assert q['consumed'][c]['uuid']not in {x['mapping']['original_uuid']for x in rows}
  committed=dict(schema='IR11_COMMITTED_V1',transaction_id=self.transaction_id,cohorts=sorted(cs),additional_starts=11,refunds=0,role=ROLE,primary_statistics_excluded=True,validated_union_authorized=False,initial_spec_sha256={r['spec']['cohort']:r['initial_spec_sha256']for r in rows},runtime_view_installed_by_this_transaction=False)
  immutable(self.folder/'COMMITTED.json',committed);return dict(state='COMMITTED_RECONCILED',new_grants=0,path=str(self.folder/'COMMITTED.json'),cohorts=sorted(cs))
 def reconcile(self):
  with self.lock:self.owner();return self._reconcile(read(self.folder/'PREPARED.json'))
 def register(self,authorization):
  with self.lock:
   p=self._prepare(authorization);self.checkpoint('AFTER_PREPARED');prior=self._reconcile(p)
   if prior['state']=='COMMITTED_RECONCILED':return prior
   for r in p['rows']:
    c=r['spec']['cohort'];immutable(self.root/'control/specs'/(c+'.json'),r['spec']);immutable(self.root/'control'/(c+'_SPEC.json'),r['spec'])
   self.checkpoint('AFTER_SPEC_PUBLICATION');self.fresh() # authoritative/read-lock work occurs BEFORE update_authority
   def grant(reg):
    # LOCKED CALLBACK: no engine/canonical/registered/authority calls. Only
    # the supplied q, immutable file hashes and pure identity functions.
    before=copy.deepcopy(reg);q=reg['registered_future_requests'][REQ];cs={r['spec']['cohort']for r in p['rows']};assert not(cs&set(q['admitted_specs']))and not(cs&set(q['consumed']))
    assert not any(r.get('transaction_id')==self.transaction_id for r in q.get('authorized_incident_recovery_transactions',[]))
    assert sha(self.root/'control/MATRIX_CURRENT.json')==MATRIX_SHA and sha(self.root/'control/SCOPE.json')==SCOPE_SHA
    for r in p['rows']:
     s=r['spec'];c=s['cohort'];old=r['mapping']['original_cohort'];assert q['consumed'][old]==r['old_receipt']and q['admitted_specs'][old]==digest(r['original_spec'])
     assert sha(self.root/'analysis'/(old+'.RESULT.json'))==r['mapping']['original_negative_RESULT_sha256']and sha(self.root/'control/qualification_ledger'/(old+'.DONE.json'))==r['mapping']['original_DONE_sha256']
     assert sha(self.root/'control/specs'/(c+'.json'))==sha(self.root/'control'/(c+'_SPEC.json'))==r['initial_spec_sha256'];pure_identity(s,r['mapping'],p['science_keys'],r['original_spec'],r['spec']['incident_recovery_trial_lineage'])
     assert c not in q['admitted_inputs'][s['input_digest']]['specs'];q['admitted_specs'][c]=r['initial_spec_sha256'];q['admitted_inputs'][s['input_digest']]['specs'].append(c)
     q.setdefault('authorized_incident_recovery_trials',[]).append(dict(transaction_id=self.transaction_id,cohort=c,original_cohort=old,original_uuid=r['mapping']['original_uuid'],incident_id=p['incident_id'],role=ROLE,recovery_plan_sha256=PLAN_SHA,initial_spec_sha256=r['initial_spec_sha256'],science_projection_sha256=r['mapping']['science_projection_sha256'],original_negative_RESULT_sha256=r['mapping']['original_negative_RESULT_sha256'],original_DONE_sha256=r['mapping']['original_DONE_sha256'],original_raw_sha256=r['mapping']['original_raw_sha256'],primary_statistics_excluded=True,validated_union_authorized=False,new_grants=1,refunds=0))
    q['budget']+=11;q['remaining']+=11;q.setdefault('authorized_incident_recovery_transactions',[]).append(dict(transaction_id=self.transaction_id,additional_starts=11,refunds=0))
    stripped=copy.deepcopy(reg);sq=stripped['registered_future_requests'][REQ];bq=before['registered_future_requests'][REQ]
    for r in p['rows']:
     c=r['spec']['cohort'];del sq['admitted_specs'][c];sq['admitted_inputs'][r['spec']['input_digest']]['specs'].remove(c)
    sq['budget']-=11;sq['remaining']-=11
    for key in ['authorized_incident_recovery_trials','authorized_incident_recovery_transactions']:
     sq[key]=[r for r in sq[key]if r.get('transaction_id')!=self.transaction_id]
     if key not in bq:del sq[key]
    assert stripped==before,'NONALLOWLIST_MUTATION'
   self.engine.update_authority(grant);self.checkpoint('AFTER_AUTHORITY');result=self._reconcile(p);self.checkpoint('AFTER_COMMITTED');return dict(result,new_grants=11)
