"""Append-only primary memory-scope synchronizer; no import-time action.
Main publishes/installs this operational wrapper. It never calls registry.extend
on its own, creates a grant, changes a proposal, or launches a model.
"""
import pathlib,json,hashlib,copy,threading,sys,os,uuid,importlib.util,traceback,time,ctypes
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ID='DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1'
MARKER=ID
MEMORY='DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1'
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
FIELDS=['request','overlay_id','source_sha256','QA_sha256','readback_sha256','dependency_pins','preserved_nonprimary_cohorts']
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(raw(v)).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def exclusive(p,v):
 p=P(p);p.parent.mkdir(parents=True,exist_ok=True);data=raw(v)
 if p.exists():assert p.read_bytes()==data,'IMMUTABLE_RECEIPT_CONFLICT';return
 tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex)
 try:
  with tmp.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
  try:os.link(tmp,p)
  except FileExistsError:assert p.read_bytes()==data
  fd=os.open(p.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if tmp.exists():tmp.unlink()
def replace_expected(p,v,old_sha,new_sha):
 p=P(p)
 if sha(p)==new_sha:return
 assert sha(p)==old_sha,'UNEXPECTED_ACTIVE_SCOPE_PREIMAGE'
 tmp=p.with_name('.'+p.name+'.'+uuid.uuid4().hex)
 try:
  with tmp.open('xb')as f:f.write(raw(v));f.flush();os.fsync(f.fileno())
  assert sha(tmp)==new_sha and sha(p)==old_sha
  os.replace(tmp,p);fd=os.open(p.parent,os.O_RDONLY)
  try:os.fsync(fd)
  finally:os.close(fd)
 finally:
  if tmp.exists():tmp.unlink()
def record(cfg):return dict({k:copy.deepcopy(cfg[k])for k in FIELDS},status='ACTIVE_OPERATIONAL_APPEND_ONLY')
class RetainedMainQueue:
 """Retained in the sole owner. Queueing never invokes Main APIs in addon.
 Uses its own typed Py_AddPendingCall pointer; no shared ctypes argtypes change.
 """
 def __init__(self,drain):
  assert threading.current_thread()is threading.main_thread()
  self.drain=drain;self.lock=threading.Lock();self.pending=False;self.last_result=None;self.last_error=None;self.last_request=None
  callback_type=ctypes.CFUNCTYPE(ctypes.c_int,ctypes.c_void_p)
  self._api=ctypes.PYFUNCTYPE(ctypes.c_int,ctypes.c_void_p,ctypes.c_void_p)(ctypes.cast(ctypes.pythonapi.Py_AddPendingCall,ctypes.c_void_p).value)
  def callback(_):
   try:
    assert threading.current_thread()is threading.main_thread()
    self.last_result=self.drain();self.last_error=None
   except BaseException as e:self.last_error=repr(e)
   finally:
    with self.lock:self.pending=False
   return 0
  self._callback=callback_type(callback)
 def __call__(self,request_path):
  with self.lock:
   self.last_request=request_path
   if self.pending:return dict(status='ALREADY_QUEUED')
   self.pending=True
  result=self._api(ctypes.cast(self._callback,ctypes.c_void_p),None)
  if result:
   with self.lock:self.pending=False
   raise RuntimeError('MAIN_PENDING_CALL_QUEUE_FULL_REQUEST_RETAINED')
  return dict(status='MAIN_PENDING_CALL_QUEUED')
class ScopeSync:
 def __init__(self,frame,cfgpath,journal,memory,enqueue_main):
  self.frame=frame;self.cfgpath=P(cfgpath);self.cfg=read(cfgpath);self.root=P(self.cfg['root']);self.engine=frame.f_locals['engine'];self.res=frame.f_locals['res'];self.registry=frame.f_locals['registry'];self.journal=journal;self.memory=memory;self.aging=memory['aging'];self.enqueue_main=enqueue_main
  # Actual l2_ops calls registry.extend, which may have captured a bound
  # journal method and later an E qualification plain function. Preserve both.
  self.prior_extend=self.registry.extend;self.journal_extend=journal.extend;self.prior_choose=self.res.choose_dispatch;self.lock=threading.RLock();self.directory=P(self.cfg['directory']);self.enabled=True;self.last_issue=None;self.in_main=False;self.fault_hook=None;self.last_recovery_tick=0;self.main_queue=None
  self.owner_module=load('scope_sync_frozen_memory_owner',memory['context']['cfg']['owner_path'])
 def check(self):
  cfg=self.cfg;assert read(self.cfgpath)==cfg and cfg['status']=='ACTIVE_OPERATIONAL_APPEND_ONLY'and cfg['request']==REQ and cfg['overlay_id']==ID
  assert sha(cfg['source_path'])==cfg['source_sha256']==sha(__file__)
  for p,h in cfg['dependency_pins'].items():assert sha(p)==h,'SYNC_DEPENDENCY_DRIFT '+p
  for role in ['QA','readback']:assert sha(cfg[role+'_path'])==cfg[role+'_sha256']
  qa=read(cfg['QA_path']);back=read(cfg['readback_path']);assert qa['status']=='PASS'and qa['actual_journal_and_memory_interfaces_qualified']and back['verified']and back['QA_sha256']==cfg['QA_sha256']
  for v in [qa,back]:assert v['source_sha256']==cfg['source_sha256']and v['dependency_pins']==cfg['dependency_pins']
  assert self.memory['aging'].original is self.memory['new_choose']and self.res.resources is self.memory['new_resources']
  _,_,q,plan=self.journal.check();assert all(q['additional_operational_overlays'][ID].get(k)==v for k,v in record(cfg).items())
  return q,plan
 def stable_memory(self):
  q,_=self.check();active=read(self.cfg['memory_active_path']);assert active==self.memory['context']['cfg'];self.memory['lib'].validate(active,q);return q,active
 def committed(self):
  """Read-only validation. Never invokes reconcile(), extend() or grants."""
  q,plan=self.check();matrix=self.journal.matrix();points={p['cohort']:p for p in matrix['points']};scope=read(self.root/'control/SCOPE.json');initial={p['cohort']for p in scope['points']};history=read(self.root/'control/SEARCH_HISTORY.json');result={}
  helpers=type(self.journal).prepare.__globals__;sci=helpers['scientific_spec'];jhash=helpers['digest']
  for cp in sorted(self.journal.journals.glob('*/COMMITTED.json')):
   pp=cp.with_name('PREPARED.json');v=read(pp);cm=read(cp);pid=v['proposal']['proposal_id']
   assert pp.parent.name==pid and cm['schema']=='L2_MLP_EXTENSION_COMMITTED_V1'and cm['proposal_id']==pid and cm['prepared_sha256']==sha(pp)
   assert v['schema']=='L2_MLP_EXTENSION_PREPARED_V1'and v['wrapper_manifest']==self.journal.manifest and v['source_pins']==plan['source_pins']and v['execution_plan_sha256']==sha(self.root/'control/EXECUTION_PLAN.json')
   assert v['base_scope_sha256']==sha(self.root/'control/SCOPE.json')==matrix['base_scope_sha256']
   assert cm['registered_points']==len(v['planned'])and cm['authority_mutations_during_recovery']==0
   assert pid in history['proposal_ids']and history['profiles'][v['proposal']['profile']]['parameters']==v['parameters']
   extensions=[x for x in q.get('authorized_extensions',[])if x['proposal_id']==pid]
   if v['planned']:assert len(extensions)==1 and extensions[0]['new_starts']==len(v['planned'])and extensions[0]['profile']==v['proposal']['profile']and extensions[0]['parameters']==v['parameters']
   for item in v['planned']:
    p=item['point'];c=p['cohort'];assert c not in initial and c not in self.cfg['preserved_nonprimary_cohorts']
    assert points[c]==p and c in q['admitted_specs']and c in q['admitted_inputs'][p['input_digest']]['specs']
    spec=self.engine.canonical(c);assert sha(self.root/'control/specs'/(c+'.json'))==q['admitted_specs'][c]and jhash(sci(spec))==item['scientific_spec_sha256']
    assert all(sha(x['path'])==x['sha256']for x in item['configs'])and len(spec['expected_options'])==item['expected_options_count']
    evidence=dict(cohort=c,scientific_spec_sha256=item['scientific_spec_sha256'],prepared_path=str(pp),prepared_sha256=sha(pp),committed_path=str(cp),committed_sha256=sha(cp),proposal_id=pid)
    assert c not in result,'DUPLICATE_PRIMARY_COMMITTED_IDENTITY';result[c]=evidence
  return q,result
 def enqueue_scan(self):
  """Addon-safe: queue immutable intent only; no Main-only memory API."""
  if not self.enabled:return None
  try:
   with self.lock:
    q,evidence=self.committed();allowed=set(self.memory['context']['cfg']['allowed_cohorts']);needed=[evidence[c]for c in sorted(evidence)if c not in allowed and c not in q['consumed']and not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()]
    if not needed:return None
    request=dict(schema=ID,kind='REQUEST_MAIN_SCOPE_SYNC',source_sha256=self.cfg['source_sha256'],request=REQ,committed_primary_additions=needed)
    path=self.directory/'requests'/(digest(request)+'.REQUEST.json');exclusive(path,request)
   # Never call/wait for Main while holding sync/journal/aging/authority locks.
   self.enqueue_main(str(path));return str(path)
  except Exception as e:self.last_issue=dict(stage='QUEUE_SYNC',error=repr(e));return None
 def extend(self,proposal):
  if not self.enabled:return self.prior_extend(proposal)
  result=[]
  try:result=self.prior_extend(proposal)
  except Exception as e:self.last_issue=dict(stage='ORIGINAL_EXTEND_ENGINEERING_PRESERVED',error=repr(e),traceback=traceback.format_exc(limit=5))
  finally:self.enqueue_scan()
  return result
 def choose(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  if not self.enabled:return self.prior_choose(pending,sample,claims,history,previous,policy,dispatch_index)
  try:
   self.recovery_tick()
   q,cfg=self.stable_memory()
   if cfg['scope_mode']=='FINITE_CANARY':pool=pending
   else:
    assert cfg['scope_mode']=='ALL_UNSPENT_FUTURE'
    initial={p['cohort']for p in read(self.root/'control/SCOPE.json')['points']};allowed=set(cfg['allowed_cohorts'])|initial|set(self.cfg['preserved_nonprimary_cohorts'])
    unacked=set(c for p in(self.directory/'transactions').glob('*/PREPARED.json')if not p.with_name('ACK.json').exists()for c in read(p)['added_cohorts'])
    pool=[s for s in pending if s['cohort']in allowed and s['cohort']not in unacked]
   return self.prior_choose(pool,sample,claims,history,previous,policy,dispatch_index)
  except Exception as e:self.last_issue=dict(stage='ADMISSION_SYNC_BOUNDARY_HOLD',error=repr(e));return None
 def recovery_tick(self,force=False):
  """Bounded addon-side retry; no Main-only API, no waiting, no new grant."""
  now=time.monotonic()
  if not force and now-self.last_recovery_tick<10:return None
  self.last_recovery_tick=now
  try:
   self.check()
   pending=next((p for p in(self.directory/'transactions').glob('*/PREPARED.json')if not p.with_name('ACK.json').exists()),None)
   if pending is not None:self.enqueue_main(str(pending));return str(pending)
   return self.enqueue_scan()
  except Exception as e:self.last_issue=dict(stage='RECOVERY_TICK_QUEUED_LATER',error=repr(e));return None
 def checkpoint(self,phase):
  if self.fault_hook:self.fault_hook(phase)
 def apply_transaction(self,path,owner_assert):
  tx=read(path);lib=self.memory['lib'];assert path.parent.name==digest(tx)and tx['schema']==ID and tx['source_sha256']==self.cfg['source_sha256']
  old=tx['old_config'];new=tx['new_config'];assert new['scope_mode']=='ALL_UNSPENT_FUTURE'and old['scope_mode']=='ALL_UNSPENT_FUTURE'
  assert set(old['allowed_cohorts'])<=set(new['allowed_cohorts'])and new['allowed_cohorts']==old['allowed_cohorts']+sorted(set(new['allowed_cohorts'])-set(old['allowed_cohorts']))
  assert {k:v for k,v in old.items()if k!='allowed_cohorts'}=={k:v for k,v in new.items()if k!='allowed_cohorts'}
  assert tx['added_cohorts']==sorted(set(new['allowed_cohorts'])-set(old['allowed_cohorts']))
  _,evidence=self.committed();assert tx['committed_evidence']==[evidence[c]for c in tx['added_cohorts']]
  oldrecord=tx['old_record'];newrecord=tx['new_record'];assert oldrecord['status']=='ACTIVE'and all(oldrecord.get(k)==v for k,v in lib.record(old).items())
  expected=copy.deepcopy(oldrecord);expected.update(lib.record(new));assert newrecord==expected,'MEMORY_PROVENANCE_CHANGED'
  ack=path.with_name('ACK.json')
  if ack.exists():
   a=read(ack);assert a['transaction_sha256']==sha(path)and a['new_config_sha256']==tx['new_config_sha256'];return a
  # Exact original callback transaction preserves concurrent receipts/peers.
  q,_=self.check();row=q['additional_operational_overlays'][lib.ID]
  assert row in [oldrecord,newrecord],'UNKNOWN_MEMORY_RECORD_PREIMAGE'
  if row==oldrecord:
   def mutate(reg):
    q=reg['registered_future_requests'][REQ];assert q['additional_operational_overlays'][lib.ID]in[oldrecord,newrecord]
    assert set(new['allowed_cohorts'])<=set(q['admitted_specs'])
    before={k:copy.deepcopy(v)for k,v in q.items()if k!='additional_operational_overlays'}
    q['additional_operational_overlays'][lib.ID]=copy.deepcopy(newrecord)
    assert before=={k:v for k,v in q.items()if k!='additional_operational_overlays'}
   self.engine.update_authority(mutate)
  self.checkpoint('AFTER_AUTHORITY')
  replace_expected(self.cfg['memory_active_path'],new,tx['old_config_sha256'],tx['new_config_sha256'])
  self.checkpoint('AFTER_ACTIVE_FILE')
  current=self.memory['context']['cfg'];assert current in [old,new],'UNKNOWN_OWNER_CONTEXT_PREIMAGE'
  if current!=new:self.owner_module.update_scope_in_owner(new,owner_assert)
  self.checkpoint('AFTER_OWNER_CONTEXT')
  q,cfg=self.stable_memory();assert cfg==new
  result=dict(schema=ID,kind='MAIN_SCOPE_SYNC_ACK',source_sha256=self.cfg['source_sha256'],transaction_sha256=sha(path),request_paths=tx['request_paths'],new_config_sha256=tx['new_config_sha256'],added_cohorts=tx['added_cohorts'],owner_pid=os.getpid(),Main_thread=True,grants_added=0,model_starts=0,policy_change_release_credit_bytes=0,scientific_rules_unchanged=True)
  exclusive(ack,result);return result
 def drain_in_main(self,owner_assert):
  assert threading.current_thread()is threading.main_thread();owner_assert()
  if not self.enabled:return dict(status='RESTORED_SYNC_NOOP',model_starts=0,grants_added=0)
  if self.in_main:return dict(status='REENTRANT_ALREADY_DRAINING',model_starts=0)
  self.in_main=True
  try:
   with self.aging.lock:
    with self.lock:
     self.check()
     # Complete an interrupted forward transaction before making a new one.
     for p in sorted((self.directory/'transactions').glob('*/PREPARED.json')):
      if not p.with_name('ACK.json').exists():self.apply_transaction(p,owner_assert)
     q,active=self.stable_memory()
     if active['scope_mode']=='FINITE_CANARY':return dict(status='DEFERRED_UNTIL_CANARY_APPROVED_BROAD_SCOPE',grants_added=0,model_starts=0)
     assert active['scope_mode']=='ALL_UNSPENT_FUTURE'
     q,evidence=self.committed();claims=self.frame.f_locals['claims']
     added=sorted(c for c in evidence if c not in active['allowed_cohorts']and c not in q['consumed']and c not in claims and not any((self.root/'control/qualification_ledger'/(c+s)).exists()for s in ['.INTENT.json','.DONE.json']))
     if not added:return dict(status='NO_NEW_PRIMARY_UNSPENT_IDENTITIES',grants_added=0,model_starts=0)
     new=copy.deepcopy(active);new['allowed_cohorts']+=added
     request_paths=sorted(str(p)for p in (self.directory/'requests').glob('*.REQUEST.json'))
     oldrecord=copy.deepcopy(q['additional_operational_overlays'][self.memory['lib'].ID]);newrecord=copy.deepcopy(oldrecord);newrecord.update(self.memory['lib'].record(new))
     tx=dict(schema=ID,source_sha256=self.cfg['source_sha256'],old_config=active,old_config_sha256=sha(self.cfg['memory_active_path']),new_config=new,new_config_sha256=hashlib.sha256(raw(new)).hexdigest(),old_record=oldrecord,new_record=newrecord,added_cohorts=added,committed_evidence=[evidence[c]for c in added],request_paths=request_paths)
     folder=self.directory/'transactions'/digest(tx);path=folder/'PREPARED.json';exclusive(path,tx);self.checkpoint('AFTER_PREPARED')
     return dict(status='APPENDED_EXACT_COMMITTED_PRIMARY_IDENTITIES',ACK=self.apply_transaction(path,owner_assert))
  except Exception as e:self.last_issue=dict(stage='MAIN_SYNC_FORWARD_RECOVERY_REQUIRED',error=repr(e));return dict(status='ENGINEERING_PENDING_SAFE_TO_RECOVER',error=repr(e),grants_added=0,model_starts=0)
  finally:self.in_main=False
def install_on_frame(frame,cfgpath,enqueue_main=None,main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];assert not hasattr(main,MARKER)
 journal=getattr(main,'DTC_L2_MLP_REGISTRY_JOURNAL_V1')['guard'];memory=getattr(main,MEMORY)
 frame.f_locals['engine'].assert_parent_lease();plan=frame.f_locals['engine'].registered()[3]
 assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
 sync=ScopeSync(frame,cfgpath,journal,memory,enqueue_main);sync.stable_memory()
 # Main supplies a qualified queue-only callable; bare addon Main API calls
 # are never made by this module. Source origin is publication-pinned.
 if enqueue_main is None:
  sync.main_queue=RetainedMainQueue(lambda:sync.drain_in_main(sync.engine.assert_parent_lease));sync.enqueue_main=sync.main_queue
 else:assert sync.cfg['dependency_pins'].get(str(P(enqueue_main.__code__.co_filename)))==sha(enqueue_main.__code__.co_filename)
 with memory['aging'].lock:
  assert sync.registry is journal.registry and sync.registry.extend==sync.prior_extend and journal.extend==sync.journal_extend and sync.res.choose_dispatch is sync.prior_choose
  sync.registry.extend=sync.extend;sync.res.choose_dispatch=sync.choose;setattr(main,MARKER,sync)
 return dict(status='OPERATIONAL_SCOPE_SYNC_INSTALLED',owner_pid=os.getpid(),source_sha256=sha(__file__),pool_object_id=id(frame.f_locals['pool']),claims_object_id=id(frame.f_locals['claims']),model_starts=0,grants_added=0)
def apply_in_owner(cfgpath):
 assert threading.current_thread()is threading.main_thread();cfg=read(cfgpath);assert P(cfg['root'])==R
 main=sys.modules['__main__'];thread=main.DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame
 return install_on_frame(frame,cfgpath)
def drain_in_owner(owner_assert):return getattr(sys.modules['__main__'],MARKER).drain_in_main(owner_assert)
def restore_in_owner(main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];s=getattr(main,MARKER)
 with s.aging.lock:
  assert s.registry.extend==s.extend and s.journal.extend==s.journal_extend and s.res.choose_dispatch==s.choose,'Restore newer wrappers first'
  assert not any(not p.with_name('ACK.json').exists()for p in(s.directory/'transactions').glob('*/PREPARED.json')),'Finish forward recovery before restore'
  q,active=s.stable_memory();_,evidence=s.committed()
  assert active['scope_mode']!='ALL_UNSPENT_FUTURE'or not any(c not in active['allowed_cohorts']and c not in q['consumed']for c in evidence),'Synchronize pending primary grants before restore'
  s.enabled=False;s.registry.extend=s.prior_extend;s.res.choose_dispatch=s.prior_choose;delattr(main,MARKER)
 return dict(status='PRIOR_CHOOSER_JOURNAL_RESTORED',scope_not_shrunk=True,receipts_retained=True,grants_changed=0,models_untouched=True)
