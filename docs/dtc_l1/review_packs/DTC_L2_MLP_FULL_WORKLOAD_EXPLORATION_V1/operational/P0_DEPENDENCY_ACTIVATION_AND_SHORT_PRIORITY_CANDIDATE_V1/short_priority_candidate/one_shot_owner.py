"""Qualified-candidate owner-instance short-P0 priority exception.
No import-time action, source/registry/spec/worker/model mutation or launcher.
Only Main may install on the existing owner after publication/registration.
"""
import pathlib,json,hashlib,importlib.util,threading,sys,os,time,copy,gzip,statistics,fcntl
P=pathlib.Path;R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1');REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1';ID='DTC_L2_MLP_ONE_SHOT_SHORT_P0_PRIORITY_V1';MARKER='DTC_L2_MLP_ONE_SHOT_SHORT_P0_OWNER_V1';G=1024**3
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def js(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def jsha(v):return hashlib.sha256(js(v)).hexdigest()
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
class Hold(Exception):pass
def validate(cfg,engine):
 assert cfg['status']=='ACTIVE_FUTURE_ONLY'and cfg['request']==REQ and cfg['overlay_id']==ID
 assert sha(cfg['source_path'])==cfg['source_sha256']==sha(__file__)
 for role in['policy','QA','readback']:assert sha(cfg[role+'_path'])==cfg[role+'_sha256']
 for path,digest in cfg['dependency_pins'].items():assert sha(path)==digest,'SOURCE_DRIFT '+path
 policy=read(cfg['policy_path']);qa=read(cfg['QA_path']);back=read(cfg['readback_path']);assert policy['request']==REQ and policy['overlay_id']==ID and policy['max_cost_bytes']==12*G and policy['max_history_elapsed_seconds']==1800 and policy['min_history_count']>=2
 assert qa['status']=='PASS'and qa['owner_integration_qualified']is True and qa['native_prefix_qualified']is True and back['verified']is True and back['QA_sha256']==cfg['QA_sha256']
 for v in[qa,back]:assert v['source_sha256']==cfg['source_sha256']and v['policy_sha256']==cfg['policy_sha256']and v['dependency_pins']==cfg['dependency_pins']
 q=engine.registered()[2];record=q['additional_operational_overlays'][ID];assert record['status']=='ACTIVE_PRIORITY_ONLY'
 for key in['request','overlay_id','source_sha256','policy_sha256','QA_sha256','readback_sha256','dependency_pins','allowed_cohorts','token_directory']:assert record[key]==cfg[key]
 return policy,q,record
class ProgressAssessment:
 def __init__(self,root,interval=60):self.root=P(root);self.interval=interval;self.previous=None;self.cached=None;self.last=0
 def __call__(self,frame):
  now=time.monotonic()
  if self.cached is not None and now-self.last<self.interval:return self.cached
  values={}
  for row in frame['own_live']:
   c=row['cohort'];out=self.root/'DTC/run/results'/row['uuid'];p=out/'progress.jsonl.gz';assert p.stat().st_size<=16*1024**2,'Progress file too large for light observer';last=None
   try:
    with gzip.open(p,'rt')as f:
     for line in f:last=json.loads(line)
   except(EOFError,json.JSONDecodeError):pass
   assert last and last['generation']==row['uuid']and last['pid']==row['pid']and last['start_ticks']==row['start_ticks'];s=read(self.root/'control/specs'/(c+'.json'));values[c]=dict(completed=last['completed'],expected=s['expected']['instructions'],cash=.88*row['anon_PSS_bytes']+row['effective_future_bytes'])
  if self.previous is None:self.previous=(now,values);return None
  stamp,before=self.previous;dt=now-stamp
  if dt<self.interval:return None
  modeled=0;unknown=0
  for c,v in values.items():
   old=before.get(c);rate=(v['completed']-old['completed'])/dt if old else 0
   if rate<=0:unknown+=1;continue
   if max(0,v['expected']-v['completed'])/rate<=1800:modeled+=v['cash']
  self.previous=(now,values);self.last=now;self.cached=dict(modeled_30min_release_bytes=modeled,unknown_count=unknown,window_seconds=dt,modeled_not_deadline=True,monotonic=now);return self.cached
class Adapter:
 def __init__(self,frame,cfgpath,cfg,gate,assessment=None):
  self.frame=frame;self.cfgpath=P(cfgpath);self.cfg=cfg;self.gate=gate;self.aging=gate.aging;self.res=frame.f_locals['res'];self.engine=frame.f_locals['engine'];self.root=P(cfg['root']);self.old_choose=gate.original_choose;self.old_cpu=self.res.choose_dispatch;self.assessment=assessment or ProgressAssessment(self.root);self.enabled=True;self.last_hold=None;self.returned={};self.helper=load('one_shot_atomic_helper',cfg['atomic_helper_path']);assert sha(cfg['atomic_helper_path'])==cfg['dependency_pins'][cfg['atomic_helper_path']]
 def active(self):
  cfg=read(self.cfgpath);assert cfg==self.cfg,'Operational config changed; explicitly restore/reinstall';return validate(cfg,self.engine)
 def legal(self,c,q,claims):
  return c in q['admitted_specs']and c not in q['consumed']and c not in claims and c not in read(self.root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']and not(self.root/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
 def history(self,spec,q):
  rows=[]
  for c,row in q['consumed'].items():
   sp=self.root/'control/specs'/(c+'.json');hs=read(sp)
   if any(hs.get(k)!=spec.get(k)for k in['input_digest','input_binding_sha256','cell','core_commit','framework_commit','binary_sha256']):continue
   rp=self.root/'analysis'/(c+'.RESULT.json');dp=self.root/'control/qualification_ledger'/(c+'.DONE.json')
   if not(rp.exists()and dp.exists()):continue
   result=read(rp);done=read(dp)
   if result.get('state')!='PASS_L2MLP_STRICT_ARCHIVE_NATIVE_RESTORE'or result.get('proof',{}).get('performance_accepted')is not True:continue
   assert sha(sp)==q['admitted_specs'][c]and done==row['execution_receipt']and done['stop_reason']is None and done['launcher_wait_returncode']==0
   assert result['proof']['input_digest']==hs['input_digest']and result['proof']['effective_options']==hs['expected_options']
   rows.append(dict(cohort=c,elapsed_seconds=done['elapsed_seconds'],DONE_path=str(dp),DONE_sha256=sha(dp),RESULT_path=str(rp),RESULT_sha256=sha(rp)))
  return rows
 def token_path(self,target):return P(self.cfg['token_directory'])/(jsha(dict(request=REQ,target_cohort=target['cohort']))+'.RESERVED.json')
 def inner(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  if not self.enabled:return self.old_choose(pending,sample,claims,history,previous,policy,dispatch_index)
  try:self.active()
  except(Exception)as e:self.last_hold=dict(stage='SOURCE_OR_ACTIVATION',error=repr(e));return None
  try:
   fn=self.aging.original;path=str(P(fn.__code__.co_filename));digest=sha(path)
   if self.cfg['dependency_pins'].get(path)!=digest:
    def strings(v):
     if isinstance(v,dict):return [x for w in v.values()for x in strings(w)]
     if isinstance(v,list):return [x for w in v for x in strings(w)]
     return [v]if isinstance(v,str)else[]
    q=self.engine.registered()[2];registered={x for rec in q.get('additional_operational_overlays',{}).values()if str(rec.get('status','')).startswith('ACTIVE')for x in strings(rec)}
    if digest not in registered:self.last_hold=dict(stage='UNQUALIFIED_B_CALLABLE_SOURCE',path=path);return None
  except Exception as e:self.last_hold=dict(stage='B_CALLABLE_SOURCE',error=repr(e));return None
  original=self.old_choose(pending,sample,claims,history,previous,policy,dispatch_index)
  if original is not None:return original
  aging=self.aging;decision=aging.state.last_decision;target=decision.get('target')
  if not target or decision['phase']!='ACCUMULATING_PROTECTED_RELEASE'or decision['pressure_reasons']or decision['backfill_cohorts']or decision['current_slack_bytes']>=target['cost_bytes']:return None
  path=self.token_path(target)
  if path.exists():return None
  # Both new resource reads use the already installed bounded E frame guard.
  first=aging.frame_provider(pending,sample,claims,history,previous,policy or{},dispatch_index)
  if first['pressure_reasons']:return None
  protected=aging.state.protected
  try:assessment=self.assessment(first)
  except Exception as e:self.last_hold=dict(stage='PROGRESS_ASSESSMENT',error=repr(e));return None
  if not assessment or assessment['unknown_count']or not 0<=time.monotonic()-assessment['monotonic']<=120 or assessment['modeled_30min_release_bytes']<0 or assessment['window_seconds']<60:return None
  C=first['budget_bytes']-first['effective_total_growth_bytes']
  if C>=target['cost_bytes']or C+assessment['modeled_30min_release_bytes']>=target['cost_bytes']:return None
  try:op,q,record=self.active();candidates=[]
  except Exception as e:self.last_hold=dict(stage='FRESH_ACTIVATION',error=repr(e));return None
  costs={r['cohort']:r['cost_bytes']for r in first['pending']}
  for spec in pending:
   c=spec['cohort']
   if c not in self.cfg['allowed_cohorts']or spec['cell']!='DH'or spec['profile']!='P0'or not self.legal(c,q,claims):continue
   cost=costs.get(c)
   if cost is None or not 0<cost<=min(12*G,C)or cost>spec['limits']['max_process_tree_rss_bytes']:continue
   try:rows=self.history(spec,q)
   except Exception as e:self.last_hold=dict(stage='HISTORY_IDENTITY',error=repr(e));return None
   if len(rows)<op['min_history_count']or max(x['elapsed_seconds']for x in rows)>1800:continue
   candidates.append((statistics.median(x['elapsed_seconds']for x in rows),c,spec,cost,rows))
  if not candidates:return None
  _,c,spec,cost,timings=min(candidates,key=lambda v:(v[0],v[1]));value=aging.original([spec],sample,claims,history,previous,policy,dispatch_index)
  if value is None:return None
  assert value['cohort']==c
  second=aging.frame_provider(pending,sample,claims,history,previous,policy or{},dispatch_index)
  if second['pressure_reasons']or c in second['consumed']or c in second['claim_cohorts']:return None
  costs2={r['cohort']:r['cost_bytes']for r in second['pending']};full=costs2.get(c)
  if full is None or full>12*G or full>second['budget_bytes']-second['effective_total_growth_bytes']or second['budget_bytes']-second['effective_total_growth_bytes']>=target['cost_bytes']:return None
  if aging.state.protected!=protected:self.last_hold=dict(stage='PROTECTED_STATE_CHANGED');return None
  try:
   _,q,_=self.active();assert self.legal(c,q,claims);assert sha(self.root/'control/specs'/(c+'.json'))==q['admitted_specs'][c];assert not path.exists()
   token=dict(schema=ID,stage='RESERVED_BEFORE_CPU_RETURN',target_cohort=target['cohort'],candidate_cohort=c,canonical_spec_sha256=q['admitted_specs'][c],source_sha256=self.cfg['source_sha256'],policy_sha256=self.cfg['policy_sha256'],QA_sha256=self.cfg['QA_sha256'],readback_sha256=self.cfg['readback_sha256'],protected_R_bytes=protected,full_candidate_cost_bytes=full,first_frame=dict(budget_bytes=first['budget_bytes'],growth_bytes=first['effective_total_growth_bytes'],pressure_reasons=first['pressure_reasons'],sha256=jsha(first)),second_frame=dict(budget_bytes=second['budget_bytes'],growth_bytes=second['effective_total_growth_bytes'],pressure_reasons=second['pressure_reasons'],sha256=jsha(second)),timing_evidence=timings,assessment=assessment,original_B_decision_sha256=jsha(value),target_cost_bytes=target['cost_bytes'],scientific_credit_changed=False,UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
   self.helper.atomic_exclusive(path,token);assert read(path)==token
  except Exception as e:self.last_hold=dict(stage='DURABLE_RESERVATION_FAILED',error=repr(e));return None
  return dict(value,one_shot_priority_token=dict(path=str(path),sha256=sha(path),cohort=c,canonical_spec_sha256=token['canonical_spec_sha256']))
 def outer(self,pending,sample,claims,history,previous=None,policy=None,dispatch_index=0):
  if not self.enabled:return self.old_cpu(pending,sample,claims,history,previous,policy,dispatch_index)
  try:self.active()
  except Exception as e:self.last_hold=dict(stage='OUTER_SOURCE_OR_ACTIVATION',error=repr(e));return None
  value=self.old_cpu(pending,sample,claims,history,previous,policy,dispatch_index)
  if value is None or'one_shot_priority_token'not in value:return value
  try:
   self.active();link=value['one_shot_priority_token'];token=read(link['path']);assert token['candidate_cohort']==value['cohort']and sha(link['path'])==link['sha256'];c=value['cohort'];db=self.root/'control/dispatch_bindings'/(c+'.json');created=False
   if not db.exists():
    with(self.root/'control/qualification_ledger'/(c+'.ATTEMPT.lock')).open('a+b')as held:
     fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB);q=self.engine.registered()[2];assert self.legal(c,q,claims)and q['admitted_specs'][c]==token['canonical_spec_sha256'];spec=self.engine.canonical(c);assert value['host_cpu']in self.res.cpu_candidates(sample,claims,previous)
     if not db.exists():self.helper.atomic_exclusive(db,dict(cohort=c,canonical_spec_sha256=token['canonical_spec_sha256'],host_cpu=value['host_cpu'],resolved_spec_sha256=self.engine.jsonsha(dict(spec,host_cpu=value['host_cpu']))));created=True
   binding=read(db);assert binding['canonical_spec_sha256']==token['canonical_spec_sha256']and binding['host_cpu']in self.res.cpu_candidates(sample,claims,previous);assert self.engine.spec_for(c)['host_cpu']==binding['host_cpu']
   p=P(link['path']).with_name(P(link['path']).name.replace('.RESERVED.json','.DISPATCH_RETURNED.json'));receipt=dict(schema=ID,stage='CPU_REBINDER_RETURNED_BEFORE_CLAIM',cohort=value['cohort'],reservation=link,actual_returned_decision_sha256=jsha(value),source_sha256=self.cfg['source_sha256'],dispatch_binding_sha256=sha(db),zero_start_binding_created=created);self.helper.atomic_exclusive(p,receipt);assert read(p)==receipt;self.returned[value['cohort']]=dict(path=str(p),sha256=sha(p));return dict(value,one_shot_priority_dispatch=self.returned[value['cohort']])
  except Exception as e:self.last_hold=dict(stage='DURABLE_DISPATCH_RETURN_FAILED',error=repr(e));return None

def install_on_frame(frame,cfgpath,main=None,assessment=None,fixture=False):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];cfg=read(cfgpath);engine=frame.f_locals['engine'];validate(cfg,engine);assert not hasattr(main,MARKER)
 coupling=getattr(main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')
 with coupling['aging'].lock:
  gate=coupling['gate'];aging=coupling['aging'];res=frame.f_locals['res'];cpu=coupling['cpu'];assert res is coupling['res']and aging is res.DTC_LARGE_JOB_AGING_INSTALLED
  assert res.choose_dispatch is cpu['wrapper']and coupling['cell'].cell_contents is gate.wrapper and cpu['original']is gate.wrapper and aging.wrapper is gate.wrapper
  assert gate.original_choose.__self__ is aging and gate.original_choose.__name__=='choose';assert gate.original_provider is aging.frame_provider
  for fn in[cpu['wrapper'],gate.original_choose,gate.wrapper]:
   path=str(P(fn.__code__.co_filename));assert path in cfg['dependency_pins']and sha(path)==cfg['dependency_pins'][path]
  adapter=Adapter(frame,cfgpath,cfg,gate,assessment=assessment);oldgate=gate.original_choose;oldcpu=res.choose_dispatch;gate.original_choose=adapter.inner;res.choose_dispatch=adapter.outer
  assert coupling['cell'].cell_contents is gate.wrapper and cpu['wrapper']is oldcpu and aging.original is not adapter.inner
  state=dict(adapter=adapter,gate=gate,res=res,cpu=cpu,coupling=coupling,oldgate=oldgate,oldcpu=oldcpu,pool=frame.f_locals['pool'],claims=frame.f_locals['claims']);setattr(main,MARKER,state)
  return dict(status='ONE_SHOT_PRIORITY_INSTANCE_ADAPTER_INSTALLED',owner_pid=os.getpid(),pool_object_id=id(state['pool']),claims_object_id=id(state['claims']),source_sha256=sha(__file__),path='observer -> unchanged CPU -> unchanged frameguard -> old E then explicit priority-only B fallback',R_state_not_replaced=True,worker_native_route_and_runtime_guards_unchanged=True,model_starts=0,model_signals=0)

def apply_in_owner(config_path):
 cfg=read(config_path);plan=read(R/'control/EXECUTION_PLAN.json');assert os.getpid()==plan['parent_pid']==1498278 and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==plan['parent_start_ticks']==977758783
 main=sys.modules['__main__'];thread=main.DTC_L2_MLP_ADDON_THREAD;frame=sys._current_frames()[thread.ident]
 while frame is not None and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None;frame.f_locals['engine'].assert_parent_lease();assert P(cfg['root'])==R and P(cfg['token_directory']).parent==R/'control/operational_amendments/one_shot_short_p0_v1'
 return install_on_frame(frame,config_path)
def restore_in_owner(main=None):
 assert threading.current_thread()is threading.main_thread();main=main or sys.modules['__main__'];state=getattr(main,MARKER);adapter=state['adapter'];adapter.enabled=False
 with state['gate'].aging.lock:
  assert state['gate'].original_choose==adapter.inner,'Newer gate adapter must be restored first';state['gate'].original_choose=state['oldgate']
  unwrapped=state['res'].choose_dispatch==adapter.outer
  if unwrapped:state['res'].choose_dispatch=state['oldcpu'];delattr(main,MARKER)
  return dict(status='ONE_SHOT_PRIORITY_DISABLED',observer_unwrapped=unwrapped,newer_outer_preserved=not unwrapped,durable_tokens_retained=True,models_untouched=True)

def verify_native_link(cohort,dispatch_receipt_path,engine,root=R):
 """Read-only independent link; it grants no start or performance acceptance."""
 root=P(root);receipt=read(dispatch_receipt_path);link=receipt['reservation'];token=read(link['path']);assert sha(link['path'])==link['sha256']and receipt['cohort']==token['candidate_cohort']==cohort and receipt['source_sha256']==token['source_sha256']
 q=engine.registered()[2];row=q['consumed'][cohort];ip=root/'control/qualification_ledger'/(cohort+'.INTENT.json');intent=read(ip);out=P(intent['output']);assert row['uuid']==intent['uuid']and row['intent_sha256']==sha(ip)
 assert token['canonical_spec_sha256']==intent['spec_sha256']==q['admitted_specs'][cohort]==sha(root/'control/specs'/(cohort+'.json'));docs=[intent,read(out/'NATIVE_LAUNCH.json'),read(out/'NATIVE_SIMULATOR_PID_AND_MAPS.json')];assert all(x['l2_mlp_execution_binding']==intent['l2_mlp_execution_binding']for x in docs);assert all(x['additional_shared_json_io_binding']==intent['additional_shared_json_io_binding']for x in docs)
 if 'additional_padding_admission_binding'in intent:assert all(x['additional_padding_admission_binding']==intent['additional_padding_admission_binding']for x in docs)
 return dict(status='PASS_DURABLE_PRIORITY_TOKEN_NATIVE_IDENTITY_LINK',cohort=cohort,uuid=row['uuid'],reservation_sha256=link['sha256'],dispatch_receipt_sha256=sha(dispatch_receipt_path),INTENT_sha256=sha(ip),original_scientific_strict_not_replaced=True,source_sha256=token['source_sha256'],production_admission_changed=False)
