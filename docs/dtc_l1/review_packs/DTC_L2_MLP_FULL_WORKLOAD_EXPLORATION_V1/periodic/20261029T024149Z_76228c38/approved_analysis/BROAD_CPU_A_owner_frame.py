"""Inert Main-only dynamic-shared RuntimeFrames facade adapter.

Only the existing facade.resources reference changes. Global CPU2 memory
configuration, Tiny, RuntimeFrames, FrameGuard, aging and CPU wrappers remain.
"""
import pathlib,hashlib,copy,sys,threading,json
P=pathlib.Path
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def make_owner_frame(tiny,cfg,lib,owner_assert):
 frames=tiny.frames;facade=tiny.facade;aging=tiny.aging;engine=tiny.engine
 original=facade.resources;leaf=tiny.wrapper
 unavailable=type(tiny.coupling['gate']).choose.__globals__['FrameUnavailable']
 frozen=copy.deepcopy(cfg);state=dict(tiny=tiny,frames=frames,facade=facade,aging=aging,engine=engine,lib=lib,cfg=frozen,original=original,leaf=leaf,last_issue=None,enabled=False,owner_assert=owner_assert)
 def resources(spec,fresh_source=False):
  if not fresh_source:return original(spec,False)
  caller=sys._getframe(1);actual=None
  while caller:
   if caller.f_code is type(frames).__call__.__code__ and caller.f_locals.get('self')is frames:actual=caller;break
   caller=caller.f_back
  if actual is None:return original(spec,True)
  try:
   assert cfg==frozen,'BROAD_FRAME_CONFIG_OBJECT_DRIFT'
   assert frozen['expected_pins'][str(P(__file__))]==sha(__file__),'BROAD_FRAME_SOURCE_NOT_PINNED_OR_DRIFT'
   assert frames.res is facade and tiny.frames is frames and tiny.facade is facade and tiny.wrapper is leaf
   gate=tiny.coupling['gate'];provider=aging.frame_provider
   provider_is_guard=(getattr(provider,'__self__',None)is gate and getattr(provider,'__func__',None)is type(gate).frames)
   assert tiny.aging is aging and (provider is frames or provider_is_guard)and gate.original_provider is frames
   q=engine.registered()[2];lib.validate(frozen,q);engine.assert_parent_lease()
   pending=actual.f_locals['pending'];claims=actual.f_locals['claims']
   eligible=[s['cohort']for s in pending if lib.eligible_cohort(frozen,q,s['cohort'],'OWNER_CHOOSE',claims)]
   eligible=[c for c in eligible if not(P(frozen['root'])/'control/qualification_ledger'/(c+'.INTENT.json')).exists()]
   if not eligible:return original(spec,True)
   # The old Tiny leaf performs its own unchanged guard and true 95 projection.
   base=leaf(spec,True);candidate=eligible[0]
   slot=lib.capture_slot_evidence(frozen,q,candidate,None,root=frozen['root'])
   liveclaims=lib.read(P(frozen['root'])/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   assert liveclaims==json.loads(slot['claims_utf8'])['claims'],'BROAD_FRAME_CLAIM_CHANGED_BETWEEN_SNAPSHOTS'
   cpu=lib.sample_cpu_evidence(None,prospective_cpu_threads=slot['prospective_cpu_threads']);legal=lib.capture_legal_cpu_evidence(frozen,liveclaims,candidate,None)
   projected=lib.project_for_candidate(base,frozen,candidate,None,cpu,slot,{'kind':'OWNER_FRAME'},legal)
   lib.verify_proof(projected[lib.PROOF]);state.update(last_issue=None,eligible_pending_witnesses=eligible);return projected
  except unavailable:raise
  except Exception as error:
   state['last_issue']=dict(status='BROAD_SHARED_FRAME_SOURCE_OR_RESOURCE_HOLD',error=repr(error),fabricated_frame=False)
   raise unavailable(state['last_issue'])from error
 state['wrapper']=resources;return state
def install_owner_frame(tiny,cfg,lib,owner_assert):
 assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
 owner_assert();tiny.frames.assert_owner()
 with tiny.aging.lock:
  q=tiny.engine.registered()[2];lib.validate(cfg,q)
  state=make_owner_frame(tiny,cfg,lib,owner_assert);aging=tiny.aging
  refs=(tiny.frames,tiny.facade,aging.frame_provider,tiny.coupling['gate'].original_provider,tiny.coupling['gate'].wrapper,tiny.coupling['cpu']['wrapper'],tiny.coupling['cpu']['original'])
  previous=aging.state.previous_C;protected=copy.deepcopy(aging.state.protected);tokens=copy.deepcopy(aging.state.pending_releases)
  try:
   # Rebase only the existing capacity reference. No release/tokens are minted.
   ref=next(iter(q['consumed']));base=state['leaf']({'cohort':ref},True)
   aging.state.previous_C=lib.budget(base)-base['total_projected_additional_RAM_bytes']
   tiny.facade.resources=state['wrapper'];state['enabled']=True
   assert protected==aging.state.protected and tokens==aging.state.pending_releases
   assert refs==(tiny.frames,tiny.facade,aging.frame_provider,tiny.coupling['gate'].original_provider,tiny.coupling['gate'].wrapper,tiny.coupling['cpu']['wrapper'],tiny.coupling['cpu']['original'])
  except BaseException:
   tiny.facade.resources=state['original'];aging.state.previous_C=previous;raise
  state.update(previous_C_before=previous,previous_C_after=aging.state.previous_C,policy_change_release_credit_bytes=0,immutable_refs=refs)
  return state
def restore_owner_frame(state,owner_assert):
 assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
 owner_assert();tiny=state['tiny'];tiny.frames.assert_owner()
 with tiny.aging.lock:
  assert state['enabled']and tiny.facade.resources is state['wrapper'],'REFUSE_NEWER_FACADE_REFERENCE'
  protected=copy.deepcopy(tiny.aging.state.protected);tokens=copy.deepcopy(tiny.aging.state.pending_releases)
  q=tiny.engine.registered()[2];ref=next(iter(q['consumed']));base=state['original']({'cohort':ref},True)
  tiny.facade.resources=state['original'];tiny.aging.state.previous_C=state['lib'].budget(base)-base['total_projected_additional_RAM_bytes'];state['enabled']=False
  assert protected==tiny.aging.state.protected and tokens==tiny.aging.state.pending_releases
 return dict(status='EXACT_PRIOR_FACADE_RESOURCE_REFERENCE_RESTORED',policy_change_release_credit_bytes=0,models_signaled=0)
def install_on_frame(frame,cfg,lib,owner_assert,main=None):
 main=main or sys.modules['__main__'];tiny=getattr(main,'DTC_FUTURE_MEMORY_AGING_FACADE_095_V1')
 assert tiny.engine is frame.f_locals['engine']and tiny.aging is frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED
 memory=getattr(main,'DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1')
 assert tiny.memory is memory and memory['aging']is tiny.aging and tiny.frames.res is tiny.facade
 return install_owner_frame(tiny,cfg,lib,owner_assert)
