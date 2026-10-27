"""Owner-instance zero-start CPU rebinding. No action on import.
Only unconsumed, unclaimed, no-INTENT bindings can change host CPU. All science
and canonical spec bytes stay fixed. Existing ATTEMPT lock prevents native race.
"""
import pathlib,os,sys,json,hashlib,fcntl,threading,time,uuid
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_L2_MLP_ZERO_START_CPU_REBIND_V1'
def read(p):return json.loads(P(p).read_bytes())
def digest(b):return hashlib.sha256(b).hexdigest()
def js(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def append(p,v):
 fd=os.open(str(p),os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
 try:os.write(fd,(json.dumps(v,sort_keys=True,separators=(',',':'))+'\n').encode());os.fsync(fd)
 finally:os.close(fd)
def maybe_rebind(root,engine,res,decision,sample,claims,previous=None):
 if decision is None:return None
 root=P(root);c=decision['cohort'];db=root/'control/dispatch_bindings'/(c+'.json')
 if not db.exists():return decision
 legal=res.cpu_candidates(sample,claims,previous);before=db.read_bytes();old=json.loads(before)
 if old['host_cpu']in legal:return decision
 if type(decision.get('host_cpu'))is not int or decision['host_cpu']not in legal:return None
 ledger=root/'control/qualification_ledger';lockpath=ledger/(c+'.ATTEMPT.lock')
 with lockpath.open('a+b')as lock:
  try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:return None
  def validate():
   q=engine.registered()[2];persisted=read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   assert c not in q['consumed']and c not in claims and c not in persisted,'Already spent or claimed'
   assert not(ledger/(c+'.INTENT.json')).exists(),'Intent already exists'
   assert db.read_bytes()==before,'Binding changed concurrently'
   spec=engine.canonical(c);sp=root/'control/specs'/(c+'.json');canonical_sha=digest(sp.read_bytes())
   assert q['admitted_specs'][c]==canonical_sha==old['canonical_spec_sha256']and old['cohort']==c
   assert spec['host_cpu']is None and old['resolved_spec_sha256']==engine.jsonsha(dict(spec,host_cpu=old['host_cpu']))
   assert decision['host_cpu']in res.cpu_candidates(sample,claims,previous)
   return spec,canonical_sha
  try:spec,canonical_sha=validate()
  except (AssertionError,KeyError):return None
  new=dict(old,host_cpu=decision['host_cpu'],resolved_spec_sha256=engine.jsonsha(dict(spec,host_cpu=decision['host_cpu'])))
  newbytes=js(new);oldsha=digest(before);newsha=digest(newbytes)
  folder=root/'control/operational_amendments/zero_start_cpu_rebind_v1';folder.mkdir(parents=True,exist_ok=True);pre=folder/'preimages';pre.mkdir(exist_ok=True);pp=pre/(oldsha+'.json')
  try:
   with pp.open('xb')as f:f.write(before);f.flush();os.fsync(f.fileno())
  except FileExistsError:assert pp.read_bytes()==before
  record=dict(schema='ZERO_START_CPU_REBIND_RECEIPT_V1',transaction=uuid.uuid4().hex,UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),cohort=c,old_cpu=old['host_cpu'],new_cpu=new['host_cpu'],canonical_spec_sha256=canonical_sha,old_binding_sha256=oldsha,new_binding_sha256=newsha,preimage_path=str(pp),source_sha256=digest(P(__file__).read_bytes()),zero_start=True,scientific_spec_unchanged=True)
  journal=folder/'AMENDMENTS.jsonl';append(journal,dict(record,stage='PREPARED'))
  try:validate()
  except (AssertionError,KeyError):append(journal,dict(record,stage='CANCELLED_CONCURRENT_CHANGE'));return None
  tmp=db.with_name('.'+db.name+'.cpu-rebind-'+record['transaction'])
  try:
   with tmp.open('xb')as f:f.write(newbytes);f.flush();os.fsync(f.fileno())
   # Recheck immediately before replace while the native ATTEMPT lock is held.
   try:validate()
   except (AssertionError,KeyError):append(journal,dict(record,stage='CANCELLED_CONCURRENT_CHANGE'));return None
   os.replace(tmp,db);dirfd=os.open(str(db.parent),os.O_RDONLY)
   try:os.fsync(dirfd)
   finally:os.close(dirfd)
  finally:
   if tmp.exists():tmp.unlink()
  append(journal,dict(record,stage='COMMITTED'))
  assert engine.spec_for(c)['host_cpu']==decision['host_cpu']
  return dict(decision,zero_start_cpu_rebind=record)
def install_on_frame(frame,root=R,scheduler_ident=None):
 assert threading.current_thread()is threading.main_thread()
 main=sys.modules['__main__'];res=frame.f_locals['res'];engine=frame.f_locals['engine']
 if hasattr(main,MARKER):
  state=getattr(main,MARKER);assert state['res']is res and res.choose_dispatch is state['wrapper'];return dict(state['proof'],idempotent=True)
 original=res.choose_dispatch;scheduler_ident=threading.get_ident()if scheduler_ident is None else scheduler_ident
 def wrapper(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  assert threading.get_ident()==scheduler_ident,'Only existing scheduler chooser thread may rebind'
  decision=original(pending,sample,claims,history,previous,policy,dispatch_index)
  return maybe_rebind(root,engine,res,decision,sample,claims,previous)
 res.choose_dispatch=wrapper
 proof=dict(status='OWNER_INSTANCE_ZERO_START_CPU_REBIND_INSTALLED',owner_pid=os.getpid(),source_sha256=digest(P(__file__).read_bytes()),pool_object_id=id(frame.f_locals['pool']),claims_object_id=id(frame.f_locals['claims']),previous_choose_name=getattr(original,'__name__',''),canonical_spec_mutations=0,running_binding_mutations=0,model_signals=0)
 setattr(main,MARKER,dict(res=res,original=original,wrapper=wrapper,proof=proof));return proof
def apply_in_owner():
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']==977758783
 thread=sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame is not None and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;pin=next(x['sha256']for x in plan['source_pins']if P(x['path'])==R/'tools/l2_resources.py');assert digest(P(frame.f_locals['res'].__file__).read_bytes())==pin
 return install_on_frame(frame,scheduler_ident=thread.ident)
def restore_in_owner():
 assert threading.current_thread()is threading.main_thread();main=sys.modules['__main__'];state=getattr(main,MARKER);assert state['res'].choose_dispatch is state['wrapper'],'Restore outer wrappers first; do not clobber another amendment'
 state['res'].choose_dispatch=state['original'];delattr(main,MARKER);return dict(status='ORIGINAL_OWNER_CHOOSER_RESTORED',bindings_not_rolled_back=True,models_untouched=True)
