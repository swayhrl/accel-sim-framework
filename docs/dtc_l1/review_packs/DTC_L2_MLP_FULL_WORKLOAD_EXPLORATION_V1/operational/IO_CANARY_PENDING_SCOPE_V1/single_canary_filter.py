"""Single existing-canary candidate filter. Import has no side effect.
It only narrows a pending proposal list before all original chooser gates.
"""
import pathlib,json,hashlib,sys,threading,os
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_L2_MLP_SINGLE_CANARY_PENDING_SCOPE_V1'
def read(p):return json.loads(P(p).read_bytes())
def legal(root,engine,claims,c):
 q=engine.registered()[2];disk=read(P(root)/'control/POOL_DISPATCH_RESERVATIONS.json')['claims'];return c in q['admitted_specs']and c not in q['consumed']and c not in claims and c not in disk and not(P(root)/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
def install_on_frame(frame,cohort,root=R,scheduler_ident=None):
 assert threading.current_thread()is threading.main_thread();main=sys.modules['__main__'];res=frame.f_locals['res'];engine=frame.f_locals['engine'];claims=frame.f_locals['claims'];assert legal(root,engine,claims,cohort),'Canary must be admitted, unconsumed, unclaimed and have no INTENT'
 if hasattr(main,MARKER):
  old=getattr(main,MARKER);assert old['res']is res and old['cohort']==cohort and old['enabled'];return dict(old['proof'],idempotent=True)
 original=res.choose_dispatch;scheduler_ident=threading.get_ident()if scheduler_ident is None else scheduler_ident;state=dict(enabled=True,cohort=cohort,res=res,original=original)
 def wrapper(pending,sample,current_claims,history,previous=None,policy=None,dispatch_index=0):
  assert threading.get_ident()==scheduler_ident,'Only existing scheduler chooser thread'
  if not state['enabled']:return original(pending,sample,current_claims,history,previous,policy,dispatch_index)
  if not legal(root,engine,current_claims,cohort):return None
  narrowed=[row for row in pending if row['cohort']==cohort]
  if not narrowed:return None
  return original(narrowed,sample,current_claims,history,previous,policy,dispatch_index)
 res.choose_dispatch=wrapper;proof=dict(status='SINGLE_EXISTING_CANARY_PENDING_FILTER_INSTALLED',cohort=cohort,source_sha256=hashlib.sha256(P(__file__).read_bytes()).hexdigest(),owner_pid=os.getpid(),pool_object_id=id(frame.f_locals['pool']),claims_object_id=id(claims),only_pending_candidates_narrowed=True,all_original_resource_gates_retained=True,existing_jobs_untouched=True,model_starts=0)
 state.update(wrapper=wrapper,proof=proof);setattr(main,MARKER,state);return proof
def apply_in_owner(cohort):
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']==977758783
 thread=sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame is not None and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;return install_on_frame(frame,cohort,scheduler_ident=thread.ident)
def restore_in_owner():
 assert threading.current_thread()is threading.main_thread();main=sys.modules['__main__'];state=getattr(main,MARKER);state['enabled']=False;unwrapped=state['res'].choose_dispatch is state['wrapper']
 if unwrapped:state['res'].choose_dispatch=state['original'];delattr(main,MARKER)
 return dict(status='CANARY_FILTER_DISABLED',original_chooser_restored=unwrapped,newer_outer_wrapper_preserved=not unwrapped,no_running_jobs_interrupted=True)
