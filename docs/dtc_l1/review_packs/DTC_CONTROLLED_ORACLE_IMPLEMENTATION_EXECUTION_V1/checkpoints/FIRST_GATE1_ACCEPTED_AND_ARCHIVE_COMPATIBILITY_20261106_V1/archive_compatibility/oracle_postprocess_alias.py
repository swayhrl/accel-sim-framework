"""Private postprocess-only legacy approval-key projection; no files rewritten."""
from pathlib import Path
import hashlib,json,os,sys,threading,types
P=Path;BASE=P('/root/data/dtc_controlled_oracle_20261106_v1');PRIMITIVE=P('/root/data/dtc_main_v100_sweep_20261025_v1/tools/sweep_outbox.py');PRIMITIVE_SHA='b2bac008c8de73d3f6e7344129f094cd073d19d1572005374dc067fb2077e229'
MARKER='_DTC_ORACLE_CLOSED_POSTPROCESS_APPROVAL_ALIAS_V1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def make_exact_read_alias(original_read,approval_path,approval_sha,primitive_path,primitive_sha,outbox_path,outbox_sha):
 approval_path=P(approval_path);primitive_path=P(primitive_path);outbox_path=P(outbox_path)
 assert sha(approval_path)==approval_sha,'ACTUAL_APPROVAL_FROZEN_SHA_REQUIRED'
 assert sha(primitive_path)==primitive_sha,'ACTUAL_LEGACY_PRIMITIVE_SHA_REQUIRED'
 assert sha(outbox_path)==outbox_sha,'ACTUAL_REGISTERED_OUTBOX_SHA_REQUIRED'
 def projected(path):
  value=original_read(path)
  if P(path)!=approval_path:return value
  assert sha(approval_path)==approval_sha and sha(primitive_path)==primitive_sha and sha(outbox_path)==outbox_sha
  assert isinstance(value,dict)
  assert 'outbox_sha256'not in value or value['outbox_sha256']==primitive_sha,'DO_NOT_OVERWRITE_CONFLICTING_REAL_FIELD'
  return dict(value,outbox_sha256=primitive_sha)
 return projected
def wrap_outbox(module,root):
 root=P(root);assert P(module.__file__)==root/'tools/oracle_outbox.py'
 if getattr(module,MARKER,False):return module
 original=module.adapted
 def adapted(cohort):
  base=original(cohort)
  engine,q,plan,intent,done,out=module.closed(cohort)
  assert done['uuid']==q['consumed'][cohort]['uuid']and done['new_attempt_consumed']==1
  assert sha(module.__file__)==q['outbox_sha256']
  assert module.PRIMITIVE==PRIMITIVE and module.PRIMITIVE_SHA==PRIMITIVE_SHA and sha(PRIMITIVE)==PRIMITIVE_SHA
  approval=root/'control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json';expected=q['spec_request_sha256']
  assert sha(approval)==expected
  base.read=make_exact_read_alias(base.read,approval,expected,PRIMITIVE,PRIMITIVE_SHA,module.__file__,q['outbox_sha256'])
  return base
 module.adapted=adapted;setattr(module,MARKER,True);return module
def wrap_consumer(module,root):
 root=P(root);assert P(module.__file__)==root/'tools/oracle_results.py'
 if getattr(module,MARKER,False):return module
 original=module.load
 def loaded(name,filename):
  value=original(name,filename)
  if filename=='oracle_outbox.py':return wrap_outbox(value,root)
  return value
 module.load=loaded;setattr(module,MARKER,True);return module
def wrap_ops(module):
 if getattr(module,MARKER,False):return module
 original=module.load
 def loaded(name,path):
  value=original(name,path)
  if P(path).name=='oracle_results.py':return wrap_consumer(value,P(path).resolve().parents[1])
  return value
 module.load=loaded;setattr(module,MARKER,True);return module
def install(parent_module_name='dtc_oracle_initial_scientific_main_addon_forward_v2'):
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 parent=sys.modules[parent_module_name]
 assert sha(parent.__file__)=='f4b3338510b4c89ca16977c2f1fc13fcde262f8d8b3b21681946b177f2016778'
 state=getattr(sys.modules['__main__'],'DTC_CONTROLLED_ORACLE_SHARED_POOL_V1')
 current=[]
 with state['lock']:
  for ctx in state['contexts'].values():
   wrap_consumer(ctx['consumer'],ctx['root']);current.append(ctx['request'])
  if not getattr(parent,MARKER,False):
   original=parent.load
   def loaded(name,path):
    value=original(name,path)
    if P(path).name=='oracle_ops.py':return wrap_ops(value)
    return value
   parent.load=loaded;setattr(parent,MARKER,True)
 return dict(status='POSTPROCESS_ONLY_PRIVATE_APPROVAL_ALIAS_INSTALLED',source_sha256=sha(__file__),current_requests=current,future_remaining24_consumer_hooked=True,model_restarts=0,new_dispatchers=0,registry_or_approval_or_plan_or_source_file_writes=0,alias_only_path='EACH_OWN_STAGE/control/SINGLE_SCIENTIFIC_APPROVAL_REQUEST.json',legacy_alias_value=PRIMITIVE_SHA)
