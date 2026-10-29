"""Explicit Main-only exact-four engineering grant. Import performs no operation."""
import copy,hashlib,importlib.util,json,os,pathlib,threading,types
P=pathlib.Path
ROOT=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ROLE='ENGINEERING_OBSERVATION_CANARY'
PLAN_SHA='45c557b66316bf4bc4daa083101f95b09f38751d0c8a95c6405e66e1e862bf1f'
CONTRACT_SHA='4d7e1d1990771d8dc8bc1a9afe6ea85b9dae0f8752e951332742664a28dd0aa7'
SCOPE_SHA='2a82ae5fdab944801422e7f9c4a236adc4221f1b90675282b2434f42c3997e6d'
NATIVE_SHA='e8276aadbb243b29166d89e5e937de260e6017061b475b62ac9c6c6f3dc3825a'
RESULTS_SHA='6cc6cc30a71740df951327414d094953effb73a406e7036358ad0b702ebb0403'
OPS_SHA='a53f4933d2f0a7479a15d0e6dd8aa0501c4762d6b2161363b9467472a43fc1dc'
ENTRY_DELIVERY_SHA='2ffae93a47003e49f63234653a165c974c969289d2dc6e612897e399896616ba'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(js(v)).hexdigest()
def compact(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def immutable(p,v):
 p=P(p);data=js(v);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert p.read_bytes()==data,'IMMUTABLE_CONFLICT '+str(p);return
 t=p.with_name('.'+p.name+'.'+os.urandom(8).hex())
 try:
  with t.open('xb')as h:h.write(data);h.flush();os.fsync(h.fileno())
  try:os.link(t,p)
  except FileExistsError:assert p.read_bytes()==data,'CONCURRENT_IMMUTABLE_CONFLICT'
  t.unlink();fd=os.open(p.parent,os.O_DIRECTORY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if t.exists():t.unlink()

class EngineeringCanaryRegistry:
 def __init__(self,root,engine,scheduler_frame,configuration,fault_hook=None):
  self.root=P(root);self.engine=engine;self.frame=scheduler_frame;self.cfg=copy.deepcopy(configuration);self.fault_hook=fault_hook
  self.lock=scheduler_frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED.lock
  self.folder=self.root/'control/bpf_engineering_registration_v1/transactions'
  self.transaction_id=digest(dict(schema='EXACT4_ENGINEERING_TRANSACTION_V1',configuration_sha256=digest(self.cfg)))
 def checkpoint(self,name):
  if self.fault_hook:self.fault_hook(name)
 def assert_owner(self):
  assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
  assert self.frame.f_locals['engine']is self.engine
  assert self.frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED.lock is self.lock
  self.engine.assert_parent_lease();_,_,q,plan=self.engine.registered()
  assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
  assert sha(self.engine.__file__)==NATIVE_SHA
  if self.cfg['qualification_only']:
   assert q.get('qualification_only')is True and self.root.resolve()!=ROOT
  else:
   assert self.root.resolve()==ROOT and not q.get('qualification_only',False)
   assert isinstance(self.frame,types.FrameType)and sha(self.frame.f_code.co_filename)==OPS_SHA
   assert P(self.engine.__file__).resolve()==ROOT/'tools/l2_native.py'
   assert P(self.engine.update_authority.__code__.co_filename).resolve()==ROOT/'tools/l2_native.py'
 def validate(self):
  self.assert_owner();cfg=self.cfg
  assert cfg['schema']=='BPF_EXACT4_REGISTRATION_CONFIGURATION_V1'and cfg['request']==REQ
  assert cfg['registration_source_sha256']==sha(__file__)
  assert sha(cfg['entry_delivery_path'])==cfg['entry_delivery_sha256']==ENTRY_DELIVERY_SHA
  delivered=read(cfg['entry_delivery_path']);assert cfg['qualified_sources']==delivered['qualified_sources']
  assert all(cfg['expected_pins'].get(p)==h for p,h in delivered['expected_pins'].items()),'REQUIRED_OLD_SOURCE_PIN_OMITTED'
  for key,h in [('draft_plan',PLAN_SHA),('exclusion_contract',CONTRACT_SHA),('scope_source',SCOPE_SHA)]:assert sha(cfg[key+'_path'])==cfg[key+'_sha256']==h
  for path,h in cfg['expected_pins'].items():assert sha(path)==h
  assert set(cfg['source_paths'])==set(cfg['qualified_sources'])=={'entry','frontend','producer','extra_strict','consumer'}
  for role,path in cfg['source_paths'].items():assert sha(path)==cfg['qualified_sources'][role]
  for key in ['QA','readback']:assert sha(cfg[key+'_path'])==cfg[key+'_sha256']
  qa=read(cfg['QA_path']);back=read(cfg['readback_path'])
  assert qa['status']=='PASS'and all(qa[k]is True for k in ['native_prefix_qualified','extra_strict_qualified','consumer_archive_qualified'])
  assert back['verified']is True and back['QA_sha256']==cfg['QA_sha256']
  assert qa['qualified_sources']==back['qualified_sources']==cfg['qualified_sources']and qa['expected_pins']==back['expected_pins']==cfg['expected_pins']
  plan=read(cfg['draft_plan_path']);contract=read(cfg['exclusion_contract_path']);rows=plan['rows'];scope=load('exact4_registered_scope',cfg['scope_source_path']).CanaryScope(plan)
  assert len(rows)==4 and {r['cohort']for r in rows}==set(contract['scope_cohorts'])and plan['science_keys']==contract['science_keys']
  assert plan['scientific_role']==ROLE and contract['status']=='EXCLUSION_RULES_ONLY_NOT_ADMISSION_AUTHORITY'
  matrix=read(self.root/'control/MATRIX_CURRENT.json');primary=read(self.root/'control/SCOPE.json');scope.check_primary(matrix,primary)
  _,_,q,_=self.engine.registered();assert q['request']==REQ and q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
  originals=load('exact4_original_acceptance',cfg['original_results_source_path']);assert sha(originals.__file__)==RESULTS_SHA
  specs={}
  for row in rows:
   c=row['cohort'];rule=contract['scope_cohorts'][c]
   for k in ['mode','scientific_role','pair_id','science_projection_sha256','reference_cohort','reference_cycles','reference_result_sha256']:assert row[k]==rule[k]
   assert sha(row['draft_spec_path'])==row['draft_spec_sha256'];s=read(row['draft_spec_path']);assert s['cohort']==c and s['host_cpu']is None and s['request']==REQ
   assert compact({k:s[k]for k in plan['science_keys']})==row['science_projection_sha256']
   lin=s['engineering_observation_canary_lineage']
   for k in ['mode','pair_id','science_projection_sha256','reference_cohort','reference_cycles','reference_result_sha256']:assert lin[k]==row[k]
   assert lin['primary_statistics_excluded']is True and lin['validated_union_authorized']is False and s['scientific_role']==ROLE
   ref=self.root/'analysis'/(row['reference_cohort']+'.RESULT.json');assert sha(ref)==row['reference_result_sha256'];result=read(ref)
   assert originals.accepted(result)and result['cohort']==row['reference_cohort']and result['cycles']==row['reference_cycles']
   assert q['consumed'][row['reference_cohort']]['uuid']==result['uuid']
   refspec=self.engine.canonical(row['reference_cohort']);assert compact({k:refspec[k]for k in plan['science_keys']})==row['science_projection_sha256']
   assert result['proof']['effective_options']==s['expected_options']
   for k in ['input_digest','core_commit','framework_commit','binary_sha256']:assert result['proof'][k]==s[k]
   assert c not in {p['cohort']for p in matrix['points']};specs[c]=s
  return q,plan,scope,specs
 def expected_authorization(self):
  self.assert_owner();_,_,_,p=self.engine.registered()
  return dict(approved_transaction_id=self.transaction_id,request=REQ,role=ROLE,additional_starts=4,refunds=0,primary_statistics_unchanged=True,validated_union_authorized=False,parent_pid=p['parent_pid'],parent_start_ticks=p['parent_start_ticks'])
 def _prepare(self,authorization):
  q,plan,scope,specs=self.validate();assert authorization==self.expected_authorization(),'EXPLICIT_MAIN_AUTHORIZATION_REQUIRED'
  folder=self.folder/self.transaction_id;path=folder/'PREPARED.json'
  if path.exists():
   p=read(path);assert p['configuration']==self.cfg and p['authorization']==authorization and p['transaction_id']==self.transaction_id
   assert p['specs']==specs and p['initial_spec_sha256']=={c:digest(s)for c,s in specs.items()},'PREPARED_SPEC_TAMPER'
   return folder,p
  for c in specs:
   assert c not in q['admitted_specs']and c not in q['consumed']and c not in q.get('sealed',[])
   assert not any(x['cohort']==c for x in q.get('authorized_engineering_observation_canaries',[]))
   assert not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(self.root/'control/dispatch_bindings'/(c+'.json')).exists()
   assert not(self.root/'analysis'/(c+'.RESULT.json')).exists()
   assert not(self.root/'control/specs'/(c+'.json')).exists()and not(self.root/'control'/(c+'_SPEC.json')).exists()
  prepared=dict(schema='BPF_EXACT4_PREPARED_V1',transaction_id=self.transaction_id,configuration=self.cfg,authorization=copy.deepcopy(authorization),initial_spec_sha256={c:digest(s)for c,s in specs.items()},specs=specs,authority_before=dict(budget=q['budget'],remaining=q['remaining'],consumed_uuids={c:x['uuid']for c,x in q['consumed'].items()}),primary_SCOPE_sha256=sha(self.root/'control/SCOPE.json'),primary_MATRIX_sha256=sha(self.root/'control/MATRIX_CURRENT.json'))
  immutable(path,prepared);return folder,prepared
 def prepare(self,authorization):
  with self.lock:
   folder,p=self._prepare(authorization);return dict(state='PREPARED_NO_GRANT',path=str(folder/'PREPARED.json'),sha256=sha(folder/'PREPARED.json'),transaction_id=self.transaction_id,new_grants=0)
 def _reconcile(self,folder,p):
  q,plan,scope,specs=self.validate();assert p['configuration']==self.cfg and p['transaction_id']==self.transaction_id
  assert p['specs']==specs and p['initial_spec_sha256']=={c:digest(s)for c,s in specs.items()},'PREPARED_SPEC_TAMPER'
  cs=set(specs);present=cs&set(q['admitted_specs']);records=[r for r in q.get('authorized_engineering_observation_canaries',[])if r.get('transaction_id')==self.transaction_id];batches=[r for r in q.get('authorized_engineering_observation_transactions',[])if r['transaction_id']==self.transaction_id]
  assert all(q['consumed'].get(c,{}).get('uuid')==u for c,u in p['authority_before']['consumed_uuids'].items()),'OLD_UUID_CHANGED'
  if not present:
   assert not records and not batches and not(P(folder)/'COMMITTED.json').exists(),'AUTHORITY_WITNESS_MISSING_NEVER_REGRANT'
   for c,s in specs.items():
    assert c not in q['consumed']and not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()and not(self.root/'control/dispatch_bindings'/(c+'.json')).exists()
    for path in [self.root/'control/specs'/(c+'.json'),self.root/'control'/(c+'_SPEC.json')]:
     if path.exists():assert sha(path)==p['initial_spec_sha256'][c]
   return dict(state='UNGRANTED_SAFE_TO_CONTINUE',new_grants=0)
  assert present==cs and len(records)==4 and {r['cohort']for r in records}==cs and len(batches)==1,'PARTIAL_AUTHORITY_HOLD'
  assert batches[0]['initial_spec_sha256']==p['initial_spec_sha256']and batches[0]['additional_starts']==4 and batches[0]['refunds']==0
  olduuids=set(p['authority_before']['consumed_uuids'].values())
  for c in cs:
   r=next(r for r in records if r['cohort']==c);assert r['initial_spec_sha256']==p['initial_spec_sha256'][c]
   current=self.engine.canonical(c);assert sha(self.root/'control/specs'/(c+'.json'))==q['admitted_specs'][c]
   scope.validate(c,current,q['admitted_specs'][c],q)
   assert current['engineering_observation_canary_lineage']==specs[c]['engineering_observation_canary_lineage']
   assert q['admitted_inputs'][current['input_digest']]['specs'].count(c)==1
   if c in q['consumed']:assert q['consumed'][c]['uuid']not in olduuids,'OLD_UUID_REUSED'
  committed=dict(schema='BPF_EXACT4_COMMITTED_V1',transaction_id=self.transaction_id,cohorts=sorted(cs),initial_spec_sha256=p['initial_spec_sha256'],additional_starts=4,refunds=0,primary_statistics_excluded=True,validated_union_authorized=False,primary_SCOPE_sha256_at_registration=p['primary_SCOPE_sha256'],primary_MATRIX_sha256_at_registration=p['primary_MATRIX_sha256'])
  immutable(P(folder)/'COMMITTED.json',committed);return dict(state='COMMITTED_RECONCILED',transaction_id=self.transaction_id,new_grants=0,cohorts=sorted(cs),committed_path=str(P(folder)/'COMMITTED.json'))
 def reconcile(self):
  with self.lock:
   self.assert_owner();folder=self.folder/self.transaction_id;return self._reconcile(folder,read(folder/'PREPARED.json'))
 def register(self,authorization):
  with self.lock:
   folder,p=self._prepare(authorization);self.checkpoint('AFTER_PREPARED');prior=self._reconcile(folder,p)
   if prior['state']=='COMMITTED_RECONCILED':return prior
   for i,(c,s)in enumerate(p['specs'].items()):
    immutable(self.root/'control/specs'/(c+'.json'),s);immutable(self.root/'control'/(c+'_SPEC.json'),s);self.checkpoint('AFTER_SPEC_'+str(i+1))
   self.checkpoint('AFTER_SPEC_PUBLICATION')
   def grant(reg):
    before=copy.deepcopy(reg);q=reg['registered_future_requests'][REQ];cs=set(p['specs'])
    assert not(cs&set(q['admitted_specs']))and not(cs&set(q['consumed']))
    assert not any(r.get('transaction_id')==self.transaction_id for r in q.get('authorized_engineering_observation_transactions',[]))
    assert q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
    for c,s in p['specs'].items():
     assert sha(self.root/'control/specs'/(c+'.json'))==p['initial_spec_sha256'][c]==sha(self.root/'control'/(c+'_SPEC.json'))
     assert c not in q['admitted_inputs'][s['input_digest']]['specs']
     q['admitted_specs'][c]=p['initial_spec_sha256'][c];q['admitted_inputs'][s['input_digest']]['specs'].append(c)
     row=next(r for r in read(self.cfg['draft_plan_path'])['rows']if r['cohort']==c)
     q.setdefault('authorized_engineering_observation_canaries',[]).append(dict(transaction_id=self.transaction_id,cohort=c,role=ROLE,mode=row['mode'],science_projection_sha256=row['science_projection_sha256'],initial_spec_sha256=p['initial_spec_sha256'][c],primary_statistics_excluded=True,validated_union_authorized=False))
    q['budget']+=4;q['remaining']+=4
    q.setdefault('authorized_engineering_observation_transactions',[]).append(dict(transaction_id=self.transaction_id,additional_starts=4,refunds=0,initial_spec_sha256=p['initial_spec_sha256']))
    # Exact callback mutation allowlist: peers, consumed, old specs/history and
    # all other q fields remain byte-semantically unchanged by this grant.
    stripped=copy.deepcopy(reg);sq=stripped['registered_future_requests'][REQ];bq=before['registered_future_requests'][REQ]
    for c,s in p['specs'].items():
     del sq['admitted_specs'][c];sq['admitted_inputs'][s['input_digest']]['specs'].remove(c)
    sq['budget']-=4;sq['remaining']-=4
    for key in ['authorized_engineering_observation_canaries','authorized_engineering_observation_transactions']:
     sq[key]=[r for r in sq[key]if r.get('transaction_id')!=self.transaction_id]
     if key not in bq:del sq[key]
    assert stripped==before,'NON_ALLOWLIST_AUTHORITY_MUTATION'
    assert sha(self.root/'control/SCOPE.json')==p['primary_SCOPE_sha256']and sha(self.root/'control/MATRIX_CURRENT.json')==p['primary_MATRIX_sha256']
   self.engine.update_authority(grant);self.checkpoint('AFTER_AUTHORITY')
   result=self._reconcile(folder,p);self.checkpoint('AFTER_COMMITTED');return dict(result,new_grants=4)
