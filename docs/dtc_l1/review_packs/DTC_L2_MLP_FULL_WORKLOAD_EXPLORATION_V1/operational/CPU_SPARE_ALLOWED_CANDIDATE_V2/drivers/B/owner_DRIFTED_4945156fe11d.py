"""Version2 direct generation replacement. Import never installs or dispatches."""
import copy,datetime,hashlib,importlib.util,json,os,pathlib,sys,threading
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
MEMORY='DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1'
UPGRADE='DTC_CPU_SPARE_EXECUTION_PRIMARY_FUTURE_V2'
PREVIOUS_UPGRADE='DTC_CPU_SPARE_EXECUTION_SINGLETON_V1'
PADDING='DTC_L2_MLP_PADDING_ONLY_OWNER_V1'
SYNC='DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1'
TINY='DTC_FUTURE_MEMORY_AGING_FACADE_095_V1'
OLD_ID='FUTURE_ONLY_MEMORY_ADMISSION_095_FLOOR10_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def target(cfg):
 assert cfg['cpu_exception_scope']['mode']=='ALL_ALLOWED_ADMITTED_UNSPENT'
 assert cfg['scope_mode']=='ALL_UNSPENT_FUTURE'
 assert len(cfg['allowed_cohorts'])==len(set(cfg['allowed_cohorts']))
 return set(cfg['allowed_cohorts'])
def historical_extra(intent,out):
 """Select immutable INTENT generation, never ACTIVE_MEMORY's current strict."""
 bindings=[(k,f)for k,f in [('additional_future_memory_admission_binding','FUTURE_MEMORY_ADMISSION_SNAPSHOT.json'),
  ('additional_cpu_spare_memory_admission_binding','CPU_SPARE_MEMORY_ADMISSION_SNAPSHOT.json')]if k in intent]
 assert len(bindings)==1,'Ambiguous memory-generation binding'
 k,f=bindings[0];b=intent[k];path=P(out)/f;assert sha(path)==b['snapshot_sha256'];snap=read(path)
 assert snap['schema']==b['schema'];cfg=snap['config']
 assert (k=='additional_future_memory_admission_binding')==(b['schema']==OLD_ID),'Unknown memory binding/schema pairing'
 extra=load('intent_bound_exact_generation_extra',cfg['extra_strict_path']);assert sha(extra.__file__)==cfg['extra_strict_sha256']
 return extra

def build_functions(frame,cfg,aging,saved,lib,main,worker_anchor):
 """Closures capture NEW lib, not just saved['lib'] metadata replacement."""
 engine=frame.f_locals['engine'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer']
 oldres=saved['old_resources'];oldchoose=saved['old_choose'];oldload=saved['old_load'];context={'cfg':copy.deepcopy(cfg)}
 currentworker=worker_anchor;rawworker=getattr(main,PADDING)['worker'];assert callable(rawworker)
 state=dict(context=context,lib=lib,last_issue=None,worker_previous=currentworker,worker_no_padding=rawworker)
 def active():
  value=context['cfg'];lib.validate(value,engine.registered()[2]);target(value);return value
 def resource(spec,fresh_source=False):
  base=oldres(spec,fresh_source)
  if not fresh_source:return base
  active();return lib.project(base) # normal .95; no global CPU pressure mask
 def choose(pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  try:
   value=active();q=engine.registered()[2]
   normal=[s for s in pending if s['cohort']not in q['consumed']]
   baseline=oldchoose(normal,sample,claims,history,previous,policy,dispatch_index)
   # A normal foreign decision retains its exact legacy route. An eligible
   # decision is rechecked NOFLAG; old padding PASS is not a new-source PASS.
   if baseline is not None and not lib.eligible_cohort(value,q,baseline['cohort'],'OWNER_CHOOSE',claims):return baseline
   # Existing pre-exec gate stays <=4, with candidate full RAM/claims retained.
   if sum(not r.get('observed_model',False)for r in claims.values())>=4:return None
   cpus=res.cpu_candidates(sample,claims,previous)
   if not cpus:return None
   pool=[s for s in normal if lib.eligible_cohort(value,q,s['cohort'],'OWNER_CHOOSE',claims)]
   active_counts={}
   for row in claims.values():active_counts[row.get('workload')]=active_counts.get(row.get('workload'),0)+1
   forecasts={s['cohort']:res.forecast(s,history,policy)for s in pool};long_turn=dispatch_index%3==0
   pool.sort(key=lambda s:(active_counts.get(s.get('workload'),0),-forecasts[s['cohort']]['historical_elapsed_seconds']if long_turn else forecasts[s['cohort']]['historical_elapsed_seconds'],forecasts[s['cohort']]['predicted_peak_RAM_bytes'],s['cohort']))
   if baseline is not None:pool.sort(key=lambda s:s['cohort']!=baseline['cohort'])
   # Existing same-input/design P0 preference, confined to this E-filtered pool.
   ordered=[];seen=set()
   for s in pool:
    p0=[p for p in pool if p['profile']=='P0'and p['input_digest']==s['input_digest']and p['cell']==s['cell']]
    for p in (p0+[s]):
     if p['cohort']not in seen:ordered.append(p);seen.add(p['cohort'])
   holds=[]
   for pending_spec in ordered:
    c=pending_spec['cohort'];q=engine.registered()[2]
    if not lib.eligible_cohort(value,q,c,'OWNER_CHOOSE',claims):continue
    if(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists():continue
    spec=engine.canonical(c);assert spec==pending_spec
    assert sha(R/'control/specs'/(c+'.json'))==q['admitted_specs'][c]
    forecast=forecasts[c]
    if forecast['predicted_peak_RAM_bytes']>spec['estimated_peak_model_RAM_bytes']:
     holds.append(dict(status='CANONICAL_FULL_FORECAST_REFRESH_REQUIRED',cohort=c,canonical=spec['estimated_peak_model_RAM_bytes'],current_full_forecast=forecast['predicted_peak_RAM_bytes']));continue
    base=oldres(spec,True);normal95=lib.project(base);d=normal95['admission_decision']
    if any(r!='cpu_pressure_full'for r in d['pressure_reasons'])or d['additional_reserved_RAM_bytes']>d['admission_RAM_budget_bytes']or not(normal95['physical_disk_pass']and normal95['own_write_ceiling_pass']):
     holds.append(dict(status='FULL_NOFLAG_RESOURCE_HOLD',cohort=c));continue
    # A fresh, per-selected-cohort double sample; no cross-cohort reuse.
    evidence=lib.sample_cpu_evidence(selected_cpu=None);assessment=lib.verify_cpu_evidence(evidence)
    eligible=set(assessment['eligible_cpu_ids']);available=[cpu for cpu in cpus if cpu in eligible]
    if not available:return None
    selected=available[0]
    db=R/'control/dispatch_bindings'/(c+'.json')
    if db.exists():
     bound=read(db)['host_cpu']
     if bound in available:selected=bound
     elif bound in cpus:
      # Frozen outer rebind only changes an old CPU absent from its legal set.
      # Do not claim our prospective spare CPU will replace a still-legal DB.
      holds.append(dict(status='EXISTING_DB_CPU_NOT_FRESH_SPARE',cohort=c,bound_cpu=bound));continue
    projected=lib.project_for_candidate(base,value,c,selected_cpu=selected,evidence=evidence,context={'kind':'OWNER_CHOOSE'})
    proof=projected['additional_cpu_spare_memory_admission_proof'];lib.verify_memory_proof(proof)
    assert projected['physical_RAM_pass']and projected['physical_disk_pass']and projected['own_write_ceiling_pass']and projected['admission_decision']['pass_admission']
    assert projected['total_projected_additional_RAM_bytes']==base['total_projected_additional_RAM_bytes']
    state['last_issue']=None
    return dict(cohort=c,host_cpu=selected,forecast=forecast,admission=projected['admission_decision'],cpu_spare_owner_proof=proof,
     old_B5_PASS_claimed=False,new_execution_no_padding=True,operational_generation='CPU_SPARE_PER_COHORT_V2',
     cpu_spare_priority=dict(only_supplied_pending_pool=True,P0_same_input_design=True,active_input_balance=True,long_turn=long_turn,earlier_resource_holds=holds))
   state['last_issue']=dict(status='NO_ELIGIBLE_FULL_RESOURCE_FIT',holds=holds);return None
  except Exception as error:
   state['last_issue']=dict(status='CPU_SPARE_OWNER_HOLD',error=repr(error),healthy_models_continue=True);return None
 def worker(c):
  try:
   value=active();q=engine.registered()[2]
   if c not in target(value):return currentworker(c)
   if c in q['consumed']or(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists():
    return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,model_retries=0,error='CPU_FUTURE_ALREADY_BOUND_NO_RESUBMIT')
   assert lib.eligible_cohort(value,q,c,'NATIVE',frame.f_locals['claims'])
   return rawworker(c) # exact l2_ops.worker; its global put retains shared IO
  except Exception as error:return dict(state='ZERO_START_ENGINEERING',cohort=c,model_starts=0,error='CPU_SOURCE_OR_SCOPE_HOLD '+repr(error))
 def consumer_load(name,file):
  module=oldload(name,file)
  if P(file).name=='l2_strict.py':
   historical=module.terminal
   def terminal(c):
    intent=read(R/'control/qualification_ledger'/(c+'.INTENT.json'))
    if not any(k in intent for k in('additional_future_memory_admission_binding','additional_cpu_spare_memory_admission_binding')):return historical(c)
    original=load('unchanged_full_original_performance_strict',R/'tools/l2_strict.py')
    base=original.terminal(c);extra=historical_extra(intent,intent['output']);extra.R=R;return extra.terminal(c,base)
   module.terminal=terminal
  return module
 state.update(new_resources=resource,new_choose=choose,new_load=consumer_load,new_worker=worker)
 return state

def frame_helper(tiny,memory,lib):
 """New private callable; frozen Tiny/RuntimeFrames/FrameGuard objects remain."""
 original=tiny.wrapper;frames=tiny.frames;engine=tiny.engine;state=dict(original=original,last_issue=None)
 def resources(spec,fresh_source=False):
  base=original(spec,fresh_source)
  if not fresh_source:return base
  # Actual RuntimeFrames invocation and pending locals, not ambient global cfg.
  call=sys._getframe(1);actual=None
  while call:
   if call.f_code is type(frames).__call__.__code__ and call.f_locals.get('self')is frames:actual=call;break
   call=call.f_back
  if actual is None:return base
  pending=actual.f_locals['pending'];q=engine.registered()[2];cfg=memory['context']['cfg']
  eligible=[s['cohort']for s in pending if lib.eligible_cohort(cfg,q,s['cohort'],'OWNER_FRAME',actual.f_locals['claims'])]
  eligible=[c for c in eligible if not(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()]
  if not eligible:return base
  try:
   lib.validate(cfg,q);target(cfg)
   value=lib.project_for_candidate(base,cfg,eligible[0],selected_cpu=None,context={'kind':'OWNER_FRAME'})
   lib.verify_memory_proof(value['additional_cpu_spare_memory_admission_proof'])
   state['last_issue']=None;state['eligible_pending_witnesses']=eligible;return value
  except Exception as error:
   state['last_issue']=dict(status='CPU_SPARE_FRAME_NOT_ELIGIBLE',error=repr(error),raw_pressure_preserved=True)
   return base # true old95 snapshot remains; outer E still HOLDs old full PSI
 state['wrapper']=resources;return state

def install_on_frame(frame,cfg,aging,owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__']
 assert not hasattr(main,UPGRADE);s=getattr(main,MEMORY);target(cfg)
 engine=frame.f_locals['engine'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer']
 assert s['engine']is engine and s['res']is res and s['consumer']is consumer and s['aging']is aging
 lib=load('cpu_spare_new_library',cfg['library_path']);assert sha(lib.__file__)==cfg['library_sha256'];lib.validate(cfg,engine.registered()[2])
 q=engine.registered()[2]
 assert not any(c not in q['consumed']for c in frame.f_locals['claims']),'Drain pre-exec claims before generation replacement'
 assert not any((R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()for c in target(cfg)if c not in q['consumed']),'Unresolved INTENT birth in progress'
 sync=getattr(main,SYNC);tiny=getattr(main,TINY)
 assert sync.memory is s and tiny.memory is s and tiny.frames.res is tiny.facade
 previous=getattr(main,PREVIOUS_UPGRADE);assert previous['memory']is s
 assert cfg['previous_cpu_v1_config']==s['context']['cfg']
 assert lib.objsha(cfg['previous_cpu_v1_config'])==cfg['previous_cpu_v1_config_sha256']
 worker_anchor=previous['old_refs']['worker']
 with aging.lock:
  assert res.resources is s['new_resources']and aging.original is s['new_choose']
  assert consumer.load is s['new_load']or consumer.load is s.get('retained_cpu_generation_consumer')
  pre=dict(s);old_refs=dict(resource=res.resources,choose=aging.original,load=consumer.load,worker=frame.f_globals['worker'],sync_owner=sync.owner_module,tiny_lib=tiny.lib,tiny_resource=tiny.facade.resources)
  refs=(tiny.frames,tiny.frames.res,aging.frame_provider,tiny.coupling['gate'].original_provider,
   tiny.coupling['gate'].wrapper,tiny.coupling['cpu']['wrapper'],res.choose_dispatch,sync.memory,tiny.memory)
  oldC=aging.state.previous_C;protected=aging.state.protected;tokens=copy.deepcopy(aging.state.pending_releases)
  try:
   # Direct leaf replacement, not another wrapper and not a blind call to348.
   res.resources=pre['old_resources'];aging.original=pre['old_choose']
   functions=build_functions(frame,cfg,aging,pre,lib,main,worker_anchor)
   replacement=dict(pre,lib=lib,context=functions['context'],cfg=cfg,new_resources=functions['new_resources'],
    new_choose=functions['new_choose'],new_load=functions['new_load'],cpu_generation=functions)
   replacement['generation_history']=list(pre.get('generation_history',[]))+[dict(schema='PRESERVED_PREVIOUS_MEMORY_GENERATION',saved=pre,owner_path=pre['context']['cfg']['owner_path'],owner_sha256=pre['context']['cfg']['owner_sha256'])]
   s.clear();s.update(replacement) # SAME dictionary object retained by all consumers
   res.resources=s['new_resources'];aging.original=s['new_choose'];consumer.load=s['new_load'];frame.f_globals['worker']=functions['new_worker']
   sync.owner_module=load('cpu_spare_qualified_scope_owner',__file__);tiny.lib=lib
   helper=frame_helper(tiny,s,lib);tiny.facade.resources=helper['wrapper']
   reference=next(iter(engine.registered()[2]['consumed']));v=res.resources(engine.canonical(reference),True)
   aging.state.previous_C=v['admission_decision']['admission_RAM_budget_bytes']-v['total_projected_additional_RAM_bytes']
   assert protected==aging.state.protected and tokens==aging.state.pending_releases
   assert refs==(tiny.frames,tiny.frames.res,aging.frame_provider,tiny.coupling['gate'].original_provider,
    tiny.coupling['gate'].wrapper,tiny.coupling['cpu']['wrapper'],res.choose_dispatch,sync.memory,tiny.memory)
   saved=dict(memory=s,preimage=pre,old_refs=old_refs,frame=frame,sync=sync,tiny=tiny,helper=helper,functions=functions,oldC=oldC,owner_assert=owner_assert,lib=lib,previous_upgrade=previous)
   setattr(main,UPGRADE,saved)
  except BaseException:
   res.resources=old_refs['resource'];aging.original=old_refs['choose'];consumer.load=old_refs['load'];frame.f_globals['worker']=old_refs['worker'];sync.owner_module=old_refs['sync_owner'];tiny.lib=old_refs['tiny_lib'];tiny.facade.resources=old_refs['tiny_resource'];s.clear();s.update(pre);aging.state.previous_C=oldC
   raise
 return dict(status='CPU_SPARE_PRIMARY_FUTURE_V2_PRIVATE_GENERATION_REPLACED',same_memory_dictionary=id(s),protected_R_unchanged=True,
  policy_change_completion_credit_bytes=0,model_starts=0,new_grants=0,old_runtime_generation_provenance_retained=True)

def update_scope_in_owner(new_cfg,owner_assert):
 assert threading.current_thread()is threading.main_thread();owner_assert();s=getattr(sys.modules['__main__'],MEMORY)
 lib=s['lib'];old=s['context']['cfg'];lib.validate(new_cfg,s['engine'].registered()[2])
 assert all(old[r+'_sha256']==new_cfg[r+'_sha256']for r in lib.ROLES),'Scope append cannot change generation source'
 assert old['cpu_exception_scope']==new_cfg['cpu_exception_scope'],'CPU scope expansion requires separate Main authorization'
 assert set(old['allowed_cohorts'])<=set(new_cfg['allowed_cohorts'])
 static_old=copy.deepcopy(old);static_new=copy.deepcopy(new_cfg)
 static_old.pop('allowed_cohorts');static_new.pop('allowed_cohorts')
 assert static_old==static_new,'Scope append cannot change approval, lineage, policy, source or validation contract'
 with s['aging'].lock:
  assert s['res'].resources is s['new_resources']and s['aging'].original is s['new_choose']
  oldC=s['aging'].state.previous_C;protected=s['aging'].state.protected;tokens=copy.deepcopy(s['aging'].state.pending_releases)
  try:
   s['context']['cfg']=new_cfg;s['cfg']=new_cfg
   reference=next(iter(s['engine'].registered()[2]['consumed']));v=s['res'].resources(s['engine'].canonical(reference),True)
   s['aging'].state.previous_C=v['admission_decision']['admission_RAM_budget_bytes']-v['total_projected_additional_RAM_bytes']
   assert protected==s['aging'].state.protected and tokens==s['aging'].state.pending_releases
  except BaseException:s['context']['cfg']=old;s['cfg']=old;s['aging'].state.previous_C=oldC;raise
 return dict(status='CPU_MEMORY_SCOPE_UPDATED_NO_CPU_SCOPE_CHANGE',policy_increase_completion_credit_bytes=0,new_grants=0)

def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];v=getattr(main,UPGRADE)
 s=v['memory'];aging=s['aging'];old=v['old_refs'];tiny=v['tiny'];frame=v['frame']
 with aging.lock:
  assert tiny.facade.resources is v['helper']['wrapper'],'Restore newer CPU facade layers first'
  assert s['res'].resources is s['new_resources']and aging.original is s['new_choose']and frame.f_globals['worker']is v['functions']['new_worker']
  # Restore CPU helper before any future Tiny facade removal.
  tiny.facade.resources=old['tiny_resource'];tiny.lib=old['tiny_lib'];v['sync'].owner_module=old['sync_owner']
  s['res'].resources=old['resource'];aging.original=old['choose'];frame.f_globals['worker']=old['worker']
  # New/old generation consumer stays installed to finish already-born receipts.
  consumer=s['consumer'];dispatch_consumer=consumer.load;s.clear();s.update(v['preimage']);s['retained_cpu_generation_consumer']=dispatch_consumer;consumer.load=dispatch_consumer
  reference=next(iter(s['engine'].registered()[2]['consumed']));base=s['res'].resources(s['engine'].canonical(reference),True)
  aging.state.previous_C=base['admission_decision']['admission_RAM_budget_bytes']-base['total_projected_additional_RAM_bytes']
  delattr(main,UPGRADE)
 return dict(status='EXACT_PRIOR_MEMORY_DISPATCH_AND_FACADE_RESTORED',new_generation_consumer_retained=True,new_grants=0,model_starts=0)

def apply_in_owner(config_path):
 assert threading.current_thread()is threading.main_thread()
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
 thread=sys.modules['__main__'].DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;engine=frame.f_locals['engine'];aging=frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED
 return install_on_frame(frame,read(config_path),aging,engine.assert_parent_lease)
