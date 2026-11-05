"""Main-only exact11 incident-recovery CPU2 append forward transaction; never installs on import.
No grants, retries, model operations, registry entry routing or old-source edits.
"""
import pathlib,json,hashlib,copy,threading,os,uuid
P=pathlib.Path;ID='INCIDENT_RECOVERY_EXACT11_CPU2_SCOPE_FORWARD_TRANSACTION_V1'
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def digest(v):return hashlib.sha256(raw(v)).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def fsync_dir(p):
 fd=os.open(P(p),os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def exclusive_bytes(path,data):
 path=P(path);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():assert path.read_bytes()==data,'IMMUTABLE_PREIMAGE_OR_ACK_CONFLICT';return
 tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex)
 try:
  with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  try:os.link(tmp,path)
  except FileExistsError:assert path.read_bytes()==data
  fsync_dir(path.parent)
 finally:
  if tmp.exists():tmp.unlink()
def replace_expected_bytes(path,data,oldsha,newsha):
 path=P(path);current=sha(path)
 if current==newsha:return
 assert current==oldsha,'UNKNOWN_ACTIVE_PREIMAGE'
 tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex)
 try:
  with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  assert sha(tmp)==newsha and sha(path)==oldsha,'ACTIVE_CAS_DRIFT'
  os.replace(tmp,path);fsync_dir(path.parent)
 finally:
  if tmp.exists():tmp.unlink()
def birth():return int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])

class ScopeTransaction:
 def __init__(self,sync,canary_scope,contract_path,priority_module,source_pins,owner_identity,directory):
  self.sync=sync;self.memory=sync.memory;self.engine=sync.engine;self.lib=self.memory['lib'];self.root=P(sync.root)
  self.scope=canary_scope;self.contract_path=P(contract_path);self.priority=priority_module
  self.pins=copy.deepcopy(source_pins);self.owner=copy.deepcopy(owner_identity);self.directory=P(directory);self.fault_hook=None
 def owner_assert(self):
  assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_REQUIRED'
  assert os.getpid()==self.owner['pid']and birth()==self.owner['start_ticks'],'WRONG_OWNER_BIRTH'
  self.engine.assert_parent_lease()
  assert self.pins.get(str(P(__file__)))==sha(__file__),'TRANSACTION_SOURCE_NOT_PINNED'
  for path,h in self.pins.items():assert sha(path)==h,'SOURCE_DRIFT '+path
  assert self.pins.get(str(P(self.sync.owner_module.__file__)))==sha(self.sync.owner_module.__file__),'OFFICIAL_OWNER_SOURCE_NOT_PINNED'
 def snapshot(self):
  self.owner_assert();q,_=self.sync.check();assert self.memory is self.sync.memory
  assert self.memory['aging'].lock is self.sync.memory['aging'].lock
  return q
 def canonical(self,c):
  spec=self.engine.canonical(c);path=self.root/'control/specs'/(c+'.json');h=sha(path)
  assert spec==read(path)and spec['host_cpu']is None,'CANONICAL_HOST_CPU_MUST_BE_NONE'
  return spec,h
 def evidence(self,q,tx=None,unspent=True):
  matrix=read(self.root/'control/MATRIX_CURRENT.json');scope=read(self.root/'control/SCOPE.json');self.scope.check_primary(matrix,scope)
  assert len(self.scope.rows)==11
  claims=read(self.root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];out=[]
  for c in sorted(self.scope.rows):
   spec,h=self.canonical(c);checked=self.scope.validate(c,spec,h,q)
   if tx is not None:assert next(x['canonical_sha256']for x in tx['exact_registered_cohorts']if x['cohort']==c)==h,'CANONICAL_CHANGED_SINCE_PREPARE'
   if unspent:
    assert c not in q['consumed']and c not in q.get('sealed',[])and c not in claims,'SPENT_SEALED_OR_CLAIMED'
    assert not any((self.root/'control/qualification_ledger'/(c+s)).exists()for s in['.INTENT.json','.DONE.json']),'INTENT_OR_DONE_EXISTS'
   out.append(checked)
  return out,matrix,scope
 def locked_evidence(self,q,tx):
  """Pure current-locked-q + file checks; NEVER reenter engine authority.

  engine.update_authority already holds REGISTRY_UPDATE EX on another FD.
  canonical()/registered()/authority()/owner_assert() are forbidden here.
  Source/lease were verified outside that lock by apply(), before mutation.
  """
  assert q['request']==tx['request']
  assert q['budget']==len(q['admitted_specs'])and q['remaining']==q['budget']-len(q['consumed'])
  matrix=read(self.root/'control/MATRIX_CURRENT.json');scope=read(self.root/'control/SCOPE.json');self.scope.check_primary(matrix,scope)
  claims=read(self.root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
  assert set(tx['added_cohorts'])==set(self.scope.rows)and len(self.scope.rows)==11
  for c in sorted(self.scope.rows):
   path=self.root/'control/specs'/(c+'.json');alias=self.root/'control'/(c+'_SPEC.json');h=sha(path);spec=read(path)
   assert h==sha(alias)==q['admitted_specs'][c],'LOCKED_CANONICAL_ALIAS_OR_GRANT_DRIFT'
   assert spec['host_cpu']is None,'CANONICAL_HOST_CPU_MUST_BE_NONE'
   assert h==next(x['canonical_sha256']for x in tx['exact_registered_cohorts']if x['cohort']==c),'CANONICAL_CHANGED_SINCE_PREPARE'
   self.scope.validate(c,spec,h,q)
   assert c not in q['consumed']and c not in q.get('sealed',[])and c not in claims,'SPENT_SEALED_OR_CLAIMED'
   assert not any((self.root/'control/qualification_ledger'/(c+s)).exists()for s in['.INTENT.json','.DONE.json']),'INTENT_OR_DONE_EXISTS'
 def prepare(self):
  self.owner_assert()
  with self.memory['aging'].lock:
   with self.sync.lock:
    q=self.snapshot();active=P(self.sync.cfg['memory_active_path']);oldbytes=active.read_bytes();old=read(active)
    assert old==self.memory['context']['cfg'];self.lib.validate(old,q)
    exact,matrix,scope=self.evidence(q);proposal=self.priority.propose_scope_append(old,q,self.scope,read(self.contract_path),matrix,scope,self.canonical,self.lib)
    assert set(proposal['added_cohorts'])==set(self.scope.rows),'EXACT11_MUST_BE_NEW_SCOPE_ADDITIONS'
    new=proposal['new_config'];newbytes=raw(new)
    tx=dict(schema=ID,source_sha256=sha(__file__),source_pins=self.pins,owner_identity=self.owner,request=q['request'],contract_path=str(self.contract_path),contract_sha256=sha(self.contract_path),exact_registered_cohorts=exact,
     old_config_utf8=oldbytes.decode('utf-8'),old_config_sha256=hashlib.sha256(oldbytes).hexdigest(),new_config_utf8=newbytes.decode('utf-8'),new_config_sha256=hashlib.sha256(newbytes).hexdigest(),old_config=old,new_config=new,old_record=proposal['old_full_record'],new_record=proposal['new_full_record'],added_cohorts=proposal['added_cohorts'],grants_added=0,models_started=0)
    folder=self.directory/digest(tx);prepared=folder/'PREPARED.json'
    exclusive_bytes(folder/'OLD_ACTIVE_MEMORY.json',oldbytes);exclusive_bytes(folder/'OLD_FULL_CPU2_RECORD.json',raw(tx['old_record']));exclusive_bytes(folder/'NEW_FULL_CPU2_RECORD.json',raw(tx['new_record']));exclusive_bytes(prepared,raw(tx))
    return prepared
 def checkpoint(self,phase):
  if self.fault_hook:self.fault_hook(phase)
 def apply(self,path):
  """Explicit Main-only operation, not invoked by this candidate's import/CLI."""
  self.owner_assert();path=P(path);tx=read(path);assert path.parent.name==digest(tx)and tx['schema']==ID
  assert tx['source_sha256']==sha(__file__)and tx['source_pins']==self.pins and tx['owner_identity']==self.owner
  assert tx['contract_path']==str(self.contract_path)and tx['contract_sha256']==sha(self.contract_path)
  old,new=tx['old_config'],tx['new_config'];oldbytes=tx['old_config_utf8'].encode();newbytes=tx['new_config_utf8'].encode()
  assert hashlib.sha256(oldbytes).hexdigest()==tx['old_config_sha256']and json.loads(oldbytes)==old
  assert hashlib.sha256(newbytes).hexdigest()==tx['new_config_sha256']and json.loads(newbytes)==new
  assert path.with_name('OLD_ACTIVE_MEMORY.json').read_bytes()==oldbytes
  assert read(path.with_name('OLD_FULL_CPU2_RECORD.json'))==tx['old_record']and read(path.with_name('NEW_FULL_CPU2_RECORD.json'))==tx['new_record']
  expected=copy.deepcopy(tx['old_record']);expected.update(self.lib.record(new));assert tx['new_record']==expected
  assert old['allowed_cohorts']+sorted(set(new['allowed_cohorts'])-set(old['allowed_cohorts']))==new['allowed_cohorts']
  assert set(tx['added_cohorts'])==set(new['allowed_cohorts'])-set(old['allowed_cohorts'])==set(self.scope.rows)
  assert {k:v for k,v in old.items()if k!='allowed_cohorts'}=={k:v for k,v in new.items()if k!='allowed_cohorts'}
  ack=path.with_name('ACK.json')
  if ack.exists():
   result=read(ack);assert result['transaction_sha256']==sha(path)and result['new_config_sha256']==tx['new_config_sha256'];return result
  with self.memory['aging'].lock:
   with self.sync.lock:
    q=self.snapshot();active=P(self.sync.cfg['memory_active_path']);row=q['additional_operational_overlays'][self.lib.ID];ctx=self.memory['context']['cfg'];h=sha(active)
    assert row in[tx['old_record'],tx['new_record']],'UNKNOWN_FULL_RECORD'
    assert h in[tx['old_config_sha256'],tx['new_config_sha256']],'UNKNOWN_ACTIVE_BYTES'
    assert ctx in[old,new],'UNKNOWN_OWNER_CONTEXT'
    phase=(int(row==tx['new_record']),int(h==tx['new_config_sha256']),int(ctx==new))
    assert phase in[(0,0,0),(1,0,0),(1,1,0),(1,1,1)],'OUT_OF_ORDER_COMPONENT_STATE'
    # Verify all official six sources, QA/readback, policy and lineage BEFORE
    # any mutation, using the config matching the actual authority row.
    self.lib.validate(new if phase[0]else old,q)
    self.evidence(q,tx,unspent=phase!=(1,1,1))
    if phase==(1,1,1):self.lib.validate(new,q)
    if row==tx['old_record']:
     def mutate(reg):
      actual=reg['registered_future_requests'][tx['request']];assert actual['additional_operational_overlays'][self.lib.ID]==tx['old_record'],'AUTHORITY_ROW_CAS_DRIFT'
      self.locked_evidence(actual,tx)
      before=copy.deepcopy(actual);actual['additional_operational_overlays'][self.lib.ID]=copy.deepcopy(tx['new_record'])
      expected_q=copy.deepcopy(before);expected_q['additional_operational_overlays'][self.lib.ID]=copy.deepcopy(tx['new_record']);assert actual==expected_q
     self.engine.update_authority(mutate)
    self.checkpoint('AFTER_AUTHORITY')
    replace_expected_bytes(active,newbytes,tx['old_config_sha256'],tx['new_config_sha256']);self.checkpoint('AFTER_ACTIVE_FILE')
    if self.memory['context']['cfg']!=new:self.sync.owner_module.update_scope_in_owner(new,self.owner_assert)
    self.checkpoint('AFTER_OWNER_CONTEXT')
    q,cfg=self.sync.stable_memory();assert cfg==new
    result=dict(schema=ID,status='EXACT11_INCIDENT_CPU2_SCOPE_APPEND_ACK',transaction_sha256=sha(path),source_sha256=sha(__file__),new_config_sha256=tx['new_config_sha256'],added_cohorts=tx['added_cohorts'],owner_identity=self.owner,Main_thread=True,grants_added=0,models_started=0,old_sources_unchanged=True,policy_change_completion_credit_bytes=0)
    exclusive_bytes(ack,raw(result));return result
