"""Main-only tiny fix for the existing E RuntimeFrames private B5 facade.
No import action, worker/resource-policy change, model launch or registry grant.
"""
import pathlib,json,hashlib,copy,threading,sys,os
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ID='FUTURE_MEMORY_AGING_FACADE_095_V1'
MARKER='DTC_'+ID
MEMORY='DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1'
FIELDS=['request','overlay_id','source_sha256','QA_sha256','readback_sha256','dependency_pins']
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def record(cfg):return dict({k:copy.deepcopy(cfg[k])for k in FIELDS},status='ACTIVE_OPERATIONAL_ONLY')
class FacadeMemory:
 def __init__(self,main,cfgpath):
  self.main=main;self.cfgpath=P(cfgpath);self.cfg=read(cfgpath);self.installed=getattr(main,'DTC_L2_MLP_INSTALLED_AGING_V1');self.frames=self.installed['frames'];self.aging=self.installed['chooser'];self.memory=getattr(main,MEMORY);self.coupling=getattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1');self.facade=self.frames.res;self.original=self.facade.resources;self.engine=self.frames.engine;self.lib=self.memory['lib'];self.wrapper=self.resources
  self.FrameUnavailable=type(self.coupling['gate']).choose.__globals__['FrameUnavailable'];self.enabled=True
 def guard(self):
  c=self.cfg;assert read(self.cfgpath)==c and c['status']=='ACTIVE_OPERATIONAL_ONLY'and c['overlay_id']==ID
  assert sha(c['source_path'])==c['source_sha256']==sha(__file__)
  for p,h in c['dependency_pins'].items():assert sha(p)==h,'FACADE_SOURCE_DRIFT '+p
  for role in ['QA','readback']:assert sha(c[role+'_path'])==c[role+'_sha256']
  qa=read(c['QA_path']);back=read(c['readback_path']);assert qa['status']=='PASS'and qa['real_RuntimeFrames_FrameGuard_qualified']and back['verified']and back['QA_sha256']==c['QA_sha256']
  for v in [qa,back]:assert v['source_sha256']==c['source_sha256']and v['dependency_pins']==c['dependency_pins']
  q=self.engine.registered()[2];assert q['request']==c['request']and all(q['additional_operational_overlays'][ID].get(k)==v for k,v in record(c).items())
  active=read(c['memory_active_path']);assert active==self.memory['context']['cfg'];self.lib.validate(active,q)
  assert self.frames.res is self.facade and self.facade is not self.memory['res']
  assert self.coupling['aging']is self.aging and self.coupling['gate'].original_provider is self.frames and self.memory['aging']is self.aging
  return active
 def resources(self,spec,fresh_source=False):
  if not fresh_source:return self.original(spec,False)
  try:active=self.guard()
  except self.FrameUnavailable:raise
  except Exception as e:raise self.FrameUnavailable(dict(status='AGING_FACADE_SOURCE_OR_MEMORY_CONFIG_INVALID',error_type=type(e).__name__,error=str(e)[:500],resource_snapshot_fabricated=False))from e
  try:base=self.original(spec,True)
  except (json.JSONDecodeError,UnicodeDecodeError,OSError,self.FrameUnavailable):raise
  except Exception as e:raise self.FrameUnavailable(dict(status='AGING_FACADE_UPSTREAM_ENGINEERING_EXCEPTION',error_type=type(e).__name__,error=str(e)[:500],resource_snapshot_fabricated=False))from e
  if active['scope_mode']=='FINITE_CANARY':return base
  try:
   assert active['scope_mode']=='ALL_UNSPENT_FUTURE'
   if 'additional_future_memory_admission_proof'in base:
    # Avoid recursively projecting a legitimate already95 snapshot. Equality
    # proves all original growth/discount/candidate/disk/pressure fields survive.
    again=self.lib.project(base['additional_future_memory_admission_proof']['base_resource_snapshot'])
    assert self.lib.objsha(again)==self.lib.objsha(base),'UNRECOGNIZED_ALREADY_PROJECTED_FRAME'
    return base
   return self.lib.project(base)
  except self.FrameUnavailable:raise
  except Exception as e:raise self.FrameUnavailable(dict(status='AGING_FACADE_PROJECTION_INVALID',error_type=type(e).__name__,error=str(e)[:500],resource_snapshot_fabricated=False))from e
 def identities(self):
  c=self.coupling;return(self.installed['frames'],self.frames.res,self.aging.frame_provider,c['gate'].original_provider,c['gate'].wrapper,c['cpu']['wrapper'],c['cpu']['original'],c['cell'].cell_contents,self.memory['res'].resources,self.memory['res'].choose_dispatch,self.aging.original)
def install_in_owner(cfgpath,main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];assert not hasattr(main,MARKER)
 obj=FacadeMemory(main,cfgpath);obj.frames.assert_owner()
 with obj.aging.lock:
  obj.guard();assert obj.aging.frame_provider is obj.frames
  refs=obj.identities();previous=obj.aging.state.previous_C;protected=obj.aging.state.protected;tokens=copy.deepcopy(obj.aging.state.pending_releases)
  try:
   obj.facade.resources=obj.wrapper;reference=next(iter(obj.engine.registered()[2]['consumed']));base=obj.wrapper({'cohort':reference},True)
   obj.aging.state.previous_C=base['admission_decision']['admission_RAM_budget_bytes']-base['total_projected_additional_RAM_bytes']
   assert obj.aging.state.protected==protected and obj.aging.state.pending_releases==tokens and obj.identities()==refs
  except BaseException:obj.facade.resources=obj.original;obj.aging.state.previous_C=previous;raise
  setattr(main,MARKER,obj)
 return dict(status='AGING_FACADE_95_INSTALLED',owner_pid=os.getpid(),source_sha256=sha(__file__),previous_C_before=previous,previous_C_after=obj.aging.state.previous_C,protected_R_unchanged=protected,policy_change_release_credit_bytes=0,only_changed_reference='existing_RuntimeFrames.res.resources',models_started=0,signals=0)
def restore_in_owner(main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];obj=getattr(main,MARKER);obj.frames.assert_owner()
 with obj.aging.lock:
  assert obj.facade.resources is obj.wrapper,'Refuse newer facade owner'
  refs=obj.identities();protected=obj.aging.state.protected;tokens=copy.deepcopy(obj.aging.state.pending_releases)
  reference=next(iter(obj.engine.registered()[2]['consumed']));base=obj.original({'cohort':reference},True)
  obj.facade.resources=obj.original;obj.aging.state.previous_C=base['admission_decision']['admission_RAM_budget_bytes']-base['total_projected_additional_RAM_bytes'];obj.enabled=False
  assert obj.identities()==refs and obj.aging.state.protected==protected and obj.aging.state.pending_releases==tokens;delattr(main,MARKER)
 return dict(status='EXACT_PRIOR_RUNTIME_FACADE_RESTORED',protected_R_unchanged=True,policy_change_release_credit_bytes=0,healthy_models_untouched=True)
