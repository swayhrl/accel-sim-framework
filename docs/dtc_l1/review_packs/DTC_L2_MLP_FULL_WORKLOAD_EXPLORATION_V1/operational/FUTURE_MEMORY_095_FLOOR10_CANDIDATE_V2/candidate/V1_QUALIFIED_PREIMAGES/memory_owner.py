"""Existing owner private instances only; Main-controlled install, no auto action."""
import pathlib,threading,importlib.util,copy,os,sys,json
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');MARKER='DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1'
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def install_on_frame(frame,cfg,aging,owner_assert):
 assert threading.current_thread()is threading.main_thread();owner_assert();lib=load('future_memory_owner_library',cfg['library_path']);engine=frame.f_locals['engine'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer'];lib.validate(cfg,engine.registered()[2]);main=sys.modules['__main__'];assert not hasattr(main,MARKER);oldres=res.resources;oldchoose=aging.original;oldload=consumer.load;context={'cfg':cfg};local=threading.local()
 def resource(spec,fresh_source=False):
  base=oldres(spec,fresh_source);active=context['cfg']
  if not fresh_source or not(getattr(local,'memory',False)or active['scope_mode']=='ALL_UNSPENT_FUTURE'):return base
  lib.validate(active,engine.registered()[2]);return lib.project(base)
 def choose(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  active=context['cfg'];baseline=oldchoose(pending,sample,claims,history,previous,policy,dispatch_index)
  if baseline is not None and baseline['cohort']not in active['allowed_cohorts']:return baseline
  pool=[s for s in pending if s['cohort']in active['allowed_cohorts']]
  if not pool:return baseline
  lib.validate(active,engine.registered()[2]);local.memory=True
  try:value=oldchoose(pool,sample,claims,history,previous,lib.effective_policy(policy),dispatch_index)
  finally:local.memory=False
  return value if value is not None else baseline
 def consumer_load(name,file):
  module=oldload(name,file)
  if P(file).name=='l2_strict.py':
   historical=module.terminal
   def terminal(c):
    ip=R/'control/qualification_ledger'/(c+'.INTENT.json');intent=lib.read(ip)
    if'additional_future_memory_admission_binding'not in intent:return historical(c)
    # Full unchanged physics/performance strict, without invoking legacy outer
    # B5 .88 replay for a new explicitly bound memory-policy generation.
    raw=load('future_memory_original_performance_strict',R/'tools/l2_strict.py');base=raw.terminal(c);extra=load('future_memory_joint_extra_strict',context['cfg']['extra_strict_path']);return extra.terminal(c,base)
   module.terminal=terminal
  return module
 with aging.lock:
  assert aging.original is oldchoose and res.resources is oldres;newres=resource;oldC=aging.state.previous_C;protected=aging.state.protected;state_tokens=copy.deepcopy(aging.state.pending_releases);res.resources=newres;aging.original=choose;consumer.load=consumer_load
  try:
   reference=next(iter(engine.registered()[2]['consumed']));v=res.resources(engine.canonical(reference),True);newC=v['admission_decision']['admission_RAM_budget_bytes']-v['total_projected_additional_RAM_bytes'];aging.state.previous_C=newC;assert aging.state.protected==protected and aging.state.pending_releases==state_tokens
  except BaseException:res.resources=oldres;aging.original=oldchoose;consumer.load=oldload;aging.state.previous_C=oldC;raise
 saved=dict(res=res,consumer=consumer,aging=aging,engine=engine,lib=lib,context=context,old_resources=oldres,old_choose=oldchoose,old_load=oldload,new_resources=newres,new_choose=choose,new_load=consumer_load,cfg=cfg);setattr(main,MARKER,saved)
 return dict(status='FUTURE_MEMORY_PRIVATE_OWNER_INSTALLED',owner_pid=os.getpid(),source_sha256=lib.sha(__file__),previous_C_before=oldC,previous_C_after=newC,policy_increase_completion_credit_bytes=0,protected_R_bytes_unchanged=protected,old_generic_chooser_filename=oldchoose.__code__.co_filename,old_P0_dependency_preference_preserved=True,healthy_models_untouched=True)
def apply_in_owner(config_path):
 plan=json.loads((R/'control/EXECUTION_PLAN.json').read_bytes());assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks'];thread=sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;engine=frame.f_locals['engine'];res=frame.f_locals['res'];return install_on_frame(frame,json.loads(P(config_path).read_bytes()),res.DTC_LARGE_JOB_AGING_INSTALLED,engine.assert_parent_lease)
def restore_dispatch_in_owner(owner_assert):
 assert threading.current_thread()is threading.main_thread();owner_assert();saved=getattr(sys.modules['__main__'],MARKER);aging=saved['aging'];res=saved['res']
 with aging.lock:
  assert res.resources is saved['new_resources']and aging.original is saved['new_choose'];res.resources=saved['old_resources'];aging.original=saved['old_choose'];saved['dispatch_restored']=True
 # Keep new-generation strict installed until its real receipts are finalized.
 return dict(status='RESTORED_EXACT_PRIOR_RESOURCE_AND_GENERIC_B',new_generation_strict_retained=True,healthy_models_untouched=True)
def update_scope_in_owner(new_cfg,owner_assert):
 assert threading.current_thread()is threading.main_thread();owner_assert();s=getattr(sys.modules['__main__'],MARKER);lib=s['lib'];engine=s['engine'];aging=s['aging'];lib.validate(new_cfg,engine.registered()[2]);old=s['context']['cfg'];assert all(old[r+'_sha256']==new_cfg[r+'_sha256']for r in lib.ROLES),'scope update cannot change source';assert set(old['allowed_cohorts'])<=set(new_cfg['allowed_cohorts']),'scope must be explicit monotonic expansion'
 with aging.lock:
  assert aging.original is s['new_choose']and s['res'].resources is s['new_resources'];priorC=aging.state.previous_C;protected=aging.state.protected;tokens=copy.deepcopy(aging.state.pending_releases);s['context']['cfg']=new_cfg
  try:
   reference=next(iter(engine.registered()[2]['consumed']));v=s['res'].resources(engine.canonical(reference),True);aging.state.previous_C=v['admission_decision']['admission_RAM_budget_bytes']-v['total_projected_additional_RAM_bytes'];assert aging.state.protected==protected and aging.state.pending_releases==tokens
  except BaseException:s['context']['cfg']=old;aging.state.previous_C=priorC;raise
 return dict(status='EXPLICIT_FUTURE_MEMORY_SCOPE_UPDATED',previous_C_before=priorC,previous_C_after=aging.state.previous_C,policy_increase_completion_credit_bytes=0,protected_R_unchanged=protected,scope_mode=new_cfg['scope_mode'])
