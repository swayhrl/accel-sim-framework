"""Main-only independent NOFLAG RuntimeFrames adapter. Import is inert.

Never strips padding proof or reconstructs full costs from a discounted sample.
The true pre-padding raw callable is authenticated and called afresh instead.
"""
import pathlib,json,hashlib,copy,sys,threading
P=pathlib.Path
ID='BROAD_CPU_OWNER_FRAME_NOFLAG_V2'
MAIN3='DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1'
TINY='DTC_FUTURE_MEMORY_AGING_FACADE_095_V1'
PADDING='DTC_L2_MLP_PADDING_ONLY_OWNER_V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def objsha(v):return hashlib.sha256(js(v)).hexdigest()
def record(cfg):
 keys=['request','overlay_id','source_path','source_sha256','resource_configuration_path','resource_configuration_sha256','raw_resources_source_path','raw_resources_source_sha256','prior_owner_frame_source_path','prior_owner_frame_source_sha256','source_pins','QA_path','QA_sha256','readback_path','readback_sha256','actual_raw_capture_path','actual_raw_capture_sha256']
 return dict({k:copy.deepcopy(cfg[k])for k in keys},configuration_sha256=objsha(cfg),status='ACTIVE_OPERATIONAL_ONLY',new_model_grants=0)
def validate(adapter_cfg,resource_cfg,lib,q):
 c=adapter_cfg
 assert c['schema']==c['overlay_id']==ID and c['request']==q['request']==resource_cfg['request']
 assert c['status']=='ACTIVE_OPERATIONAL_ONLY'and c['source_path']==str(P(__file__))and c['source_sha256']==sha(__file__)
 assert read(c['resource_configuration_path'])==resource_cfg and sha(c['resource_configuration_path'])==c['resource_configuration_sha256']
 assert c['raw_resources_source_path']==str(lib.RES)and c['raw_resources_source_sha256']==resource_cfg['expected_pins'][str(lib.RES)]==sha(lib.RES)
 assert c['prior_owner_frame_source_sha256']=='94dd822a5cacb1b68b7c17ea98945f024cd351d263954eb7b20c8de850900760'and sha(c['prior_owner_frame_source_path'])==c['prior_owner_frame_source_sha256']
 for path,h in c['source_pins'].items():assert sha(path)==h,'NOFLAG_ADAPTER_SOURCE_DRIFT '+path
 assert c['source_pins'][c['source_path']]==c['source_sha256']and c['source_pins'][c['raw_resources_source_path']]==c['raw_resources_source_sha256']
 for key in ['QA','readback']:assert sha(c[key+'_path'])==c[key+'_sha256']
 qa=read(c['QA_path']);rb=read(c['readback_path'])
 assert qa['status']=='PASS'and qa['owner_frame_NOFLAG_fullcost_qualified']is True and qa['actual_returned_base_replay_qualified']is True
 assert rb['verified']is True and rb['QA_sha256']==c['QA_sha256']
 for d in [qa,rb]:assert d['source_sha256']==c['source_sha256']and d['source_pins']==c['source_pins']
 if qa.get('qualification_only')or rb.get('qualification_only'):assert c['qualification_only']is True and q.get('qualification_only')is True
 assert c['qualification_only']==resource_cfg['qualification_only']
 capture=read(c['actual_raw_capture_path']);assert sha(c['actual_raw_capture_path'])==c['actual_raw_capture_sha256']=='d5ede0e104c776f0064bcc9f64d31a4021a05b2638faedce2fb9b067e43e858c'
 assert capture['NOFLAG_marker_absent']is True and capture['full_cost_sum_verified']is True and capture['leaf_source_path']==c['raw_resources_source_path']and capture['leaf_source_sha256']==c['raw_resources_source_sha256']
 lib.validate(resource_cfg,q)
 row=q['additional_operational_overlays'][ID];assert all(row.get(k)==v for k,v in record(c).items())
 return row
def fullcost95(raw,lib,resource_cfg):
 """Same immutable raw resource semantics, with the qualified .95 projection."""
 assert 'additional_padding_admission_proof'not in raw,'TRUE_NOFLAG_LEAF_REQUIRED_NO_STRIPPING'
 assert 'additional_future_memory_admission_proof'not in raw,'TRUE_RAW_RESOURCE_REQUIRED'
 assert raw['source_module_sha256']==resource_cfg['expected_pins'][str(lib.RES)]and raw['policy_sha256']==resource_cfg['expected_pins'][str(lib.RPOLICY)]
 rows=raw['RAM_reservation_entries']+raw['own_ram_forecasts'];assert sum(x['additional_reserved_bytes']for x in rows)==raw['total_projected_additional_RAM_bytes']
 value=lib.project(raw)
 assert value['total_projected_additional_RAM_bytes']==raw['total_projected_additional_RAM_bytes']and value['own_ram_forecasts']==raw['own_ram_forecasts']and value['RAM_reservation_entries']==raw['RAM_reservation_entries']
 assert value['physical_disk_pass']==raw['physical_disk_pass']and value['own_write_ceiling_pass']==raw['own_write_ceiling_pass']
 return value
def make_owner_frame(tiny,resource_cfg,adapter_cfg,lib,prior_state,raw_resources,owner_assert):
 frames=tiny.frames;facade=tiny.facade;aging=tiny.aging;engine=tiny.engine;gate=tiny.coupling['gate']
 unavailable=type(gate).choose.__globals__['FrameUnavailable'];original=facade.resources
 assert original is prior_state['wrapper']and prior_state['enabled']is True and prior_state['facade']is facade
 assert prior_state['cfg']==resource_cfg and prior_state['lib']is lib
 assert original.__code__.co_filename==adapter_cfg['prior_owner_frame_source_path']
 assert raw_resources.__code__.co_filename==adapter_cfg['raw_resources_source_path']and raw_resources.__qualname__=='resources'
 frozen=copy.deepcopy(adapter_cfg);rcfg=copy.deepcopy(resource_cfg)
 state=dict(tiny=tiny,frames=frames,facade=facade,aging=aging,engine=engine,lib=lib,cfg=frozen,resource_cfg=rcfg,prior_state=prior_state,original=original,raw_resources=raw_resources,last_issue=None,enabled=False,owner_assert=owner_assert)
 def resources(spec,fresh_source=False):
  if not fresh_source:return original(spec,False)
  caller=sys._getframe(1);actual=None
  while caller:
   if caller.f_code is type(frames).__call__.__code__ and caller.f_locals.get('self')is frames:actual=caller;break
   caller=caller.f_back
  if actual is None:return original(spec,True)
  pending=actual.f_locals['pending']
  if not any(s['cohort']in rcfg['allowed_cohorts']for s in pending):return original(spec,True)
  try:
   assert adapter_cfg==frozen and resource_cfg==rcfg,'NOFLAG_FRAME_CONFIG_OBJECT_DRIFT'
   provider=aging.frame_provider;guarded=getattr(provider,'__self__',None)is gate and getattr(provider,'__func__',None)is type(gate).frames
   assert frames.res is facade and tiny.frames is frames and tiny.facade is facade and (provider is frames or guarded)and gate.original_provider is frames
   q=engine.registered()[2];validate(frozen,rcfg,lib,q);engine.assert_parent_lease()
   claims=actual.f_locals['claims'];eligible=[s['cohort']for s in pending if lib.eligible_cohort(rcfg,q,s['cohort'],'OWNER_CHOOSE',claims)]
   eligible=[c for c in eligible if not(P(rcfg['root'])/'control/qualification_ledger'/(c+'.INTENT.json')).exists()]
   if not eligible:return original(spec,True)
   # Preserve the unchanged old-generation config/source guard, but do not call
   # its direct PaddingOverlay resource leaf for a new NOFLAG frame.
   tiny.guard()
   raw=raw_resources(spec,True);base=fullcost95(raw,lib,rcfg);candidate=eligible[0]
   slot=lib.capture_slot_evidence(rcfg,q,candidate,None,root=rcfg['root']);liveclaims=read(P(rcfg['root'])/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
   assert liveclaims==json.loads(slot['claims_utf8'])['claims'],'NOFLAG_FRAME_CLAIM_SNAPSHOT_DRIFT'
   cpu=lib.sample_cpu_evidence(None,prospective_cpu_threads=slot['prospective_cpu_threads']);legal=lib.capture_legal_cpu_evidence(rcfg,liveclaims,candidate,None)
   projected=lib.project_for_candidate(base,rcfg,candidate,None,cpu,slot,{'kind':'OWNER_FRAME'},legal);lib.verify_proof(projected[lib.PROOF])
   state.update(last_issue=None,eligible_pending_witnesses=eligible,last_raw_source_sha256=raw['source_module_sha256'],last_full_growth_bytes=raw['total_projected_additional_RAM_bytes'],last_prospective_cpu_threads=slot['prospective_cpu_threads']);return projected
  except unavailable:raise
  except Exception as error:
   state['last_issue']=dict(status='BROAD_NOFLAG_FRAME_SOURCE_OR_RESOURCE_HOLD',error=repr(error),fabricated_frame=False)
   raise unavailable(state['last_issue'])from error
 state['wrapper']=resources;return state
def install_on_frame(frame,resource_cfg,adapter_cfg,lib,owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
 main=main or sys.modules['__main__'];owner_assert();tiny=getattr(main,TINY);tiny.frames.assert_owner()
 assert tiny.engine is frame.f_locals['engine']and tiny.aging is frame.f_locals['res'].DTC_LARGE_JOB_AGING_INSTALLED
 prior_state=getattr(main,MAIN3)['owner_frame_state'];raw_resources=getattr(main,PADDING)['resource']
 with tiny.aging.lock:
  q=tiny.engine.registered()[2];validate(adapter_cfg,resource_cfg,lib,q)
  state=make_owner_frame(tiny,resource_cfg,adapter_cfg,lib,prior_state,raw_resources,owner_assert)
  refs=(tiny.frames,tiny.facade,tiny.aging.frame_provider,tiny.coupling['gate'].original_provider,tiny.coupling['gate'].wrapper,tiny.coupling['cpu']['wrapper'],tiny.coupling['cpu']['original'],tiny.aging.original)
  previous=tiny.aging.state.previous_C;R=copy.deepcopy(tiny.aging.state.protected);tokens=copy.deepcopy(tiny.aging.state.pending_releases)
  try:
   tiny.guard();reference=next(iter(q['consumed']));base=fullcost95(raw_resources({'cohort':reference},True),lib,resource_cfg)
   tiny.aging.state.previous_C=lib.budget(base)-base['total_projected_additional_RAM_bytes'];tiny.facade.resources=state['wrapper'];state['enabled']=True
   assert R==tiny.aging.state.protected and tokens==tiny.aging.state.pending_releases
   assert refs==(tiny.frames,tiny.facade,tiny.aging.frame_provider,tiny.coupling['gate'].original_provider,tiny.coupling['gate'].wrapper,tiny.coupling['cpu']['wrapper'],tiny.coupling['cpu']['original'],tiny.aging.original)
  except BaseException:tiny.facade.resources=state['original'];tiny.aging.state.previous_C=previous;raise
  state.update(previous_C_before=previous,previous_C_after=tiny.aging.state.previous_C,policy_change_release_credit_bytes=0,immutable_refs=refs)
  return state
def restore_owner_frame(state,owner_assert):
 assert threading.current_thread()is threading.main_thread(),'MAIN_THREAD_ONLY'
 owner_assert();tiny=state['tiny'];tiny.frames.assert_owner()
 with tiny.aging.lock:
  assert state['enabled']and tiny.facade.resources is state['wrapper'],'REFUSE_NEWER_FACADE'
  R=copy.deepcopy(tiny.aging.state.protected);tokens=copy.deepcopy(tiny.aging.state.pending_releases)
  q=tiny.engine.registered()[2];reference=next(iter(q['consumed']));base=state['original']({'cohort':reference},True)
  tiny.facade.resources=state['original'];tiny.aging.state.previous_C=state['lib'].budget(base)-base['total_projected_additional_RAM_bytes'];state['enabled']=False
  assert R==tiny.aging.state.protected and tokens==tiny.aging.state.pending_releases
 return dict(status='EXACT_PRIOR_NOFLAG_REJECTING_FACADE_RESTORED',policy_change_release_credit_bytes=0,models_signaled=0)
