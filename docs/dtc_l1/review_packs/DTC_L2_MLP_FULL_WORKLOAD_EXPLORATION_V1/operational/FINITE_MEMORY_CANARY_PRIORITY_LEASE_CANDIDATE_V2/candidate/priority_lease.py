"""Finite engineering-canary priority lease. No import-time installation.

Main only. The old E chooser always runs first. This exception borrows only
virtual priority, never physical capacity, scientific credit, or a new grant.
"""
import pathlib,json,hashlib,importlib.util,threading,sys,os,time,uuid,copy,traceback
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='FINITE_MEMORY_ENGINEERING_CANARY_PRIORITY_LEASE_V1'
MARKER='DTC_FINITE_MEMORY_CANARY_PRIORITY_LEASE_V1'
MEMORY='DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1'
FIELDS=['request','overlay_id','source_sha256','QA_sha256','readback_sha256','dependency_pins','memory_active_sha256','allowed_cohorts','token_directory']
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def jsha(v):return hashlib.sha256(js(v)).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def record(cfg):return dict({k:copy.deepcopy(cfg[k])for k in FIELDS},status='ACTIVE_PRIORITY_ONLY')
def validate(cfg,engine,memory):
 assert cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==REQ and cfg['overlay_id']==ID
 assert sha(cfg['source_path'])==cfg['source_sha256']==sha(__file__)
 assert len(cfg['allowed_cohorts'])==1 and cfg['priority_only']is True
 for p,h in cfg['dependency_pins'].items():assert sha(p)==h,'SOURCE_DRIFT '+p
 for r in ['QA','readback']:assert sha(cfg[r+'_path'])==cfg[r+'_sha256']
 qa=read(cfg['QA_path']);back=read(cfg['readback_path'])
 assert qa['status']=='PASS'and qa['owner_integration_qualified']and qa['complete_memory_generic_B_exercised']and back['verified']is True
 assert back['QA_sha256']==cfg['QA_sha256']
 for v in [qa,back]:assert v['source_sha256']==cfg['source_sha256']and v['dependency_pins']==cfg['dependency_pins']
 q=engine.registered()[2];assert q['additional_operational_overlays'][ID]==record(cfg)
 active=read(cfg['memory_active_path']);assert active==memory['context']['cfg']
 memory['lib'].validate(active,q)
 assert memory['aging'].original is memory['new_choose']and memory['res'].resources is memory['new_resources']
 if active['scope_mode']=='FINITE_CANARY':
  assert sha(cfg['memory_active_path'])==cfg['memory_active_sha256']and active['allowed_cohorts']==cfg['allowed_cohorts']
  return q,True
 assert active['scope_mode']=='ALL_UNSPENT_FUTURE'and set(cfg['allowed_cohorts'])<=set(active['allowed_cohorts'])
 return q,False
class Adapter:
 def __init__(self,frame,cfgpath,cfg,gate,memory,padding):
  self.frame=frame;self.cfgpath=P(cfgpath);self.cfg=cfg;self.gate=gate;self.aging=gate.aging
  self.res=frame.f_locals['res'];self.engine=frame.f_locals['engine'];self.root=P(cfg['root'])
  self.old_choose=gate.original_choose;self.old_cpu=self.res.choose_dispatch;self.memory=memory;self.padding=padding
  self.enabled=True;self.last_hold=None;self.scheduler_ident=None;self.returned={}
  # Exact class belonging to the unchanged guard. Never swallow or recreate a
  # lookalike: its own catch must roll back aging state/calls on failed frames.
  self.FrameUnavailable=type(gate).choose.__globals__['FrameUnavailable']
  self.helper=load('finite_canary_atomic_helper',cfg['atomic_helper_path'])
  assert sha(cfg['atomic_helper_path'])==cfg['dependency_pins'][cfg['atomic_helper_path']]
 def active(self):
  assert read(self.cfgpath)==self.cfg,'Explicit restore/reinstall required for config change'
  return validate(self.cfg,self.engine,self.memory)
 def legal(self,c,q,claims):
  ledger=self.root/'control/qualification_ledger'
  return c in q['admitted_specs']and c not in q['consumed']and c not in q.get('sealed',[])and c not in claims and c not in read(self.root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']and not any((ledger/(c+s)).exists()for s in ['.INTENT.json','.DONE.json'])and c not in self.frame.f_locals.get('running',{}).values()
 def call_old_e(self,*args):
  try:return self.old_choose(*args)
  except self.FrameUnavailable:raise
  except Exception as e:
   # This is an engineering exception, not a claimed transient JSON read. The
   # original guard owns the rollback; never mutate private state here.
   raise self.FrameUnavailable(dict(status='UPSTREAM_E_CHOOSER_ENGINEERING_EXCEPTION',error_type=type(e).__name__,error=str(e)[:500],resource_snapshot_fabricated=False,priority_exception_applied=False))from e
 def call_old_cpu(self,*args):
  try:return self.old_cpu(*args)
  except Exception as e:
   self.last_hold=dict(stage='UPSTREAM_CPU_CHOOSER_ENGINEERING_EXCEPTION',error_type=type(e).__name__,error=str(e)[:500]);return None
 def fresh(self,pending,sample,claims,history,previous,policy,index,spec,decision=None):
  q,finite=self.active();assert finite;c=spec['cohort'];assert self.legal(c,q,claims)
  frame=self.aging.frame_provider(pending,sample,claims,history,previous,policy or{},index)
  assert not frame['pressure_reasons']and c not in frame['consumed']and c not in frame['claim_cohorts']
  matches=[x for x in frame['pending']if x['cohort']==c];assert len(matches)==1
  cost=max(matches[0]['cost_bytes'],spec['estimated_peak_model_RAM_bytes'],decision['forecast']['predicted_peak_RAM_bytes']if decision else 0)
  assert 0<cost<=spec['limits']['max_process_tree_rss_bytes']
  reference=next(iter(q['consumed']));base=self.padding.resources(self.engine.canonical(reference),True)
  projected=self.memory['lib'].project(base);proof=projected['additional_future_memory_admission_proof']
  self.memory['lib'].verify_memory_proof(proof)
  assert not projected['admission_decision']['pressure_reasons']
  assert projected['total_projected_additional_RAM_bytes']+cost<=projected['admission_decision']['admission_RAM_budget_bytes']
  extra=2*spec['limits']['max_result_directory_bytes']
  assert projected['physical_disk_pass']and projected['own_write_ceiling_pass']
  assert projected['native_free_bytes']>projected['required_free_bytes']+extra
  assert projected['own_remaining_write_and_restore_bytes']+extra<=q['reserved_write_bytes']
  assert self.res.cpu_candidates(sample,claims,previous)
  return dict(frame_sha256=jsha(frame),memory_proof=proof,full_candidate_cost_bytes=cost,prospective_growth_bytes=projected['total_projected_additional_RAM_bytes']+cost)
 def inner(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  args=(pending,sample,claims,history,previous,policy,dispatch_index)
  if not self.enabled:return self.call_old_e(*args)
  try:q,finite=self.active()
  except Exception as e:self.last_hold=dict(stage='ACTIVATION',error=repr(e));return None
  original=self.call_old_e(*args)
  if original is not None:return original
  if not finite:return None
  try:
   q,finite=self.active();assert finite;c=self.cfg['allowed_cohorts'][0];pool=[s for s in pending if s['cohort']==c]
   if len(pool)!=1 or not self.legal(c,q,claims):return None
   spec=pool[0];canonical=self.engine.canonical(c)
   assert spec==canonical and sha(self.root/'control/specs'/(c+'.json'))==q['admitted_specs'][c]
   state=copy.deepcopy({k:getattr(self.aging.state,k)for k in ['protected','pending_releases']})
   first=self.fresh(pending,sample,claims,history,previous,policy,dispatch_index,spec)
   # Current generic callable includes memory348 + a650 + complete B5/f3.
   value=self.aging.original([spec],sample,claims,history,previous,policy,dispatch_index)
   if value is None:return None
   assert value['cohort']==c
   second=self.fresh(pending,sample,claims,history,previous,policy,dispatch_index,spec,value)
   assert state=={k:getattr(self.aging.state,k)for k in state},'Virtual R/credit changed during engineering fallback'
   q,finite=self.active();assert finite and self.legal(c,q,claims)
   attempt=uuid.uuid4().hex;path=P(self.cfg['token_directory'])/(attempt+'.RESERVED.json')
   token=dict(schema=ID,stage='RESERVED_BEFORE_CPU_RETURN',attempt=attempt,cohort=c,canonical_spec_sha256=q['admitted_specs'][c],source_sha256=self.cfg['source_sha256'],QA_sha256=self.cfg['QA_sha256'],readback_sha256=self.cfg['readback_sha256'],memory_active_sha256=self.cfg['memory_active_sha256'],priority_only=True,borrowed_virtual_R_bytes=state['protected'],R_mutated=False,natural_release_credit_bytes=0,first=first,second=second,original_generic_B_decision_sha256=jsha(value),UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
   token=json.loads(js(token));self.helper.atomic_exclusive(path,token);assert read(path)==token
   return dict(value,finite_memory_canary_priority_reservation=dict(path=str(path),sha256=sha(path),cohort=c,attempt=attempt))
  except self.FrameUnavailable:raise
  except Exception as e:self.last_hold=dict(stage='PRIORITY_FALLBACK_FAILCLOSED',error=repr(e),traceback=traceback.format_exc(limit=4));return None
 def outer(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  args=(pending,sample,claims,history,previous,policy,dispatch_index)
  if not self.enabled:return self.call_old_cpu(*args)
  try:
   assert self.scheduler_ident is None or threading.get_ident()==self.scheduler_ident
   _,finite=self.active()
  except Exception as e:self.last_hold=dict(stage='OUTER_ACTIVATION',error=repr(e));return None
  value=self.call_old_cpu(*args)
  if value is None or 'finite_memory_canary_priority_reservation'not in value:return value
  try:
   q,finite=self.active();assert finite;c=value['cohort'];link=value['finite_memory_canary_priority_reservation'];token=read(link['path'])
   assert c==link['cohort']==token['cohort']==self.cfg['allowed_cohorts'][0]and sha(link['path'])==link['sha256']
   assert token['source_sha256']==self.cfg['source_sha256']and token['canonical_spec_sha256']==q['admitted_specs'][c]
   assert self.legal(c,q,claims)and value['host_cpu']in self.res.cpu_candidates(sample,claims,previous)
   path=P(link['path']).with_name(link['attempt']+'.CPU_RETURNED.json')
   receipt=dict(schema=ID,stage='CPU_RETURNED_DURABLE_BEFORE_CLAIM_INTENT',reservation=link,cohort=c,host_cpu=value['host_cpu'],canonical_spec_sha256=token['canonical_spec_sha256'],returned_decision_sha256=jsha(value),source_sha256=self.cfg['source_sha256'],priority_only=True,no_grant_or_R_change=True)
   self.helper.atomic_exclusive(path,receipt);assert read(path)==receipt
   self.returned[c]=dict(path=str(path),sha256=sha(path))
   return dict(value,finite_memory_canary_priority_dispatch=self.returned[c])
  except Exception as e:self.last_hold=dict(stage='CPU_RETURN_RECEIPT_FAILCLOSED',error=repr(e));return None
def install_on_frame(frame,cfgpath,main=None,scheduler_ident=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];cfg=read(cfgpath)
 assert not hasattr(main,MARKER);memory=getattr(main,MEMORY);engine=frame.f_locals['engine'];validate(cfg,engine,memory)
 coupling=getattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1');gate=coupling['gate'];aging=coupling['aging'];res=frame.f_locals['res'];cpu=coupling['cpu']
 with aging.lock:
  assert res is coupling['res']and memory['aging']is aging and memory['res']is res
  assert res.choose_dispatch is cpu['wrapper']and coupling['cell'].cell_contents is gate.wrapper and cpu['original']is gate.wrapper and aging.wrapper is gate.wrapper
  assert gate.original_choose.__self__ is aging and gate.original_choose.__name__=='choose'and gate.original_provider is aging.frame_provider
  for fn in [cpu['wrapper'],gate.original_choose,gate.wrapper,memory['new_choose']]:assert cfg['dependency_pins'].get(str(P(fn.__code__.co_filename)))==sha(fn.__code__.co_filename)
  padding=getattr(main,'DTC_L2_MLP_PADDING_ONLY_OWNER_V1')['overlay']
  assert cfg['dependency_pins'].get(str(P(padding.resources.__code__.co_filename)))==sha(padding.resources.__code__.co_filename)
  adapter=Adapter(frame,cfgpath,cfg,gate,memory,padding);adapter.scheduler_ident=scheduler_ident
  gate.original_choose=adapter.inner;res.choose_dispatch=adapter.outer
  setattr(main,MARKER,dict(adapter=adapter,gate=gate,res=res,oldgate=adapter.old_choose,oldcpu=adapter.old_cpu,pool=frame.f_locals['pool'],claims=frame.f_locals['claims']))
 return dict(status='FINITE_CANARY_PRIORITY_LEASE_INSTALLED',source_sha256=sha(__file__),allowed_cohorts=cfg['allowed_cohorts'],pool_object_id=id(frame.f_locals['pool']),claims_object_id=id(frame.f_locals['claims']),priority_only=True,R_mutations=0,model_starts=0,signals=0)
def apply_in_owner(cfgpath):
 plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']
 main=sys.modules['__main__'];thread=main.DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame;frame.f_locals['engine'].assert_parent_lease();cfg=read(cfgpath)
 assert P(cfg['root'])==R and P(cfg['token_directory']).parent==P(cfgpath).parent
 return install_on_frame(frame,cfgpath,scheduler_ident=thread.ident)
def restore_in_owner(main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];s=getattr(main,MARKER);a=s['adapter']
 with a.aging.lock:
  assert s['gate'].original_choose==a.inner and s['res'].choose_dispatch==a.outer,'Restore newer wrappers first'
  a.enabled=False;s['gate'].original_choose=s['oldgate'];s['res'].choose_dispatch=s['oldcpu'];delattr(main,MARKER)
 return dict(status='EXACT_PRIOR_E_CPU_RESTORED',immutable_attempt_receipts_retained=True,models_untouched=True)
