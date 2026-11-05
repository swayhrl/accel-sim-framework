"""Finite current-scope route bridge. Import never installs or dispatches.

Only res.choose_dispatch is replaced by Main. For a wholly approved pending
pool the same CPU wrapper/FrameGuard/priority-inner/E chooser is called once.
Unknown or mixed future scope retains the exact old SYNC/journal route.
"""
import pathlib,json,hashlib,copy,sys,threading,importlib.util
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
REQ='DTC_L2_MLP_FULL_WORKLOAD_EXPLORATION_20261027_V1'
ID='DTC_BROAD_COUPLED_ROUTE_BRIDGE_V1'
BROAD='DTC_STRACE_BROAD_SHARED_DISPATCH_V1'
COUPLING='DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1'
TINY='DTC_FUTURE_MEMORY_AGING_FACADE_095_V1'
MEMORY='DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1'
CPU_SHA='b0db8a54400bd456aa404aa9b033badefc59231f8dd04534bc34bcf56937bcf8'
GUARD_SHA='c38a9cff23f18b8ecbd61e545cfbb775b19fe2ad732fb4ed80eee7e2851c93c2'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def objsha(v):return hashlib.sha256((json.dumps(v,sort_keys=True,indent=2)+'\n').encode()).hexdigest()
def load(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def record(cfg):
 return dict(status='ACTIVE_CURRENT_SCOPE_ROUTE_ONLY',overlay_id=ID,request=REQ,configuration_sha256=objsha(cfg),source_sha256=cfg['source_sha256'],QA_sha256=cfg['QA_sha256'],readback_sha256=cfg['readback_sha256'],scope_contract_sha256=cfg['scope_contract_sha256'],resource_configuration_sha256=cfg['resource_configuration_sha256'],observation_configuration_sha256=cfg['observation_configuration_sha256'],dependency_pins=cfg['dependency_pins'],new_grants=0)
def validate(cfg,q):
 assert cfg['schema']==cfg['overlay_id']==ID and cfg['request']==q['request']==REQ
 assert sha(__file__)==cfg['source_sha256']
 qualification=cfg.get('qualification_only')is True
 assert qualification and q.get('qualification_only')is True and P(cfg['root'])!=R if qualification else not q.get('qualification_only',False)and P(cfg['root'])==R
 for p,h in cfg['dependency_pins'].items():assert sha(p)==h,'BRIDGE_DEPENDENCY_DRIFT '+p
 for k in ['QA','readback']:assert sha(cfg[k+'_path'])==cfg[k+'_sha256']
 qa=read(cfg['QA_path']);rb=read(cfg['readback_path'])
 assert qa['status']=='PASS'and qa['source_sha256']==rb['source_sha256']==cfg['source_sha256']and rb['verified']is True and rb['QA_sha256']==cfg['QA_sha256']
 if qa.get('qualification_only')or rb.get('qualification_only'):assert qualification
 assert sha(cfg['scope_contract_path'])==cfg['scope_contract_sha256']
 scope=read(cfg['scope_contract_path']);rows={x['cohort']:x for x in scope['rows']};assert len(rows)==len(scope['rows'])==26
 assert scope['request']==REQ and scope['new_model_grants']==0 and scope['engineering_excluded']is True and scope['supplemental_R2_excluded']is True
 assert sha(cfg['resource_configuration_path'])==cfg['resource_configuration_sha256']and sha(cfg['observation_configuration_path'])==cfg['observation_configuration_sha256']
 rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
 assert rcfg['scope_contract_path']==cfg['scope_contract_path']and rcfg['scope_contract_sha256']==cfg['scope_contract_sha256']and set(rcfg['allowed_cohorts'])==set(rows)
 assert ocfg['resource_configuration_path']==cfg['resource_configuration_path']and ocfg['resource_configuration_sha256']==cfg['resource_configuration_sha256']
 assert all(c in q['admitted_specs']for c in rows)
 row=q['additional_operational_overlays'][ID];assert all(row.get(k)==v for k,v in record(cfg).items()),'BRIDGE_REGISTRATION_MISMATCH'
 return rows,rcfg,ocfg
def check_pending(pending,rows,cfg,q):
 """Passed fresh q plus current local spec bytes; no authority recursion."""
 keys=read(cfg['scope_contract_path'])['scientific_projection_keys'];matrix=read(P(cfg['root'])/'control/MATRIX_CURRENT.json');primary={p['cohort']:p for p in matrix['points']};ir={r['cohort']:r for r in q.get('authorized_incident_recovery_trials',[])}
 assert len({s['cohort']for s in pending})==len(pending)
 for spec in pending:
  c=spec['cohort'];row=rows[c];p=P(cfg['root'])/'control/specs'/(c+'.json');alias=P(cfg['root'])/'control'/(c+'_SPEC.json')
  assert c not in q['consumed']and c not in q.get('sealed',[]),'SPENT_OR_SEALED_CURRENT_POOL'
  assert sha(p)==sha(alias)==q['admitted_specs'][c]and read(p)==spec and spec['host_cpu']is None
  assert {k:spec[k]for k in keys}==row['science_projection'],'GPU_SCIENCE_PROJECTION_CHANGED'
  if row['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
   assert c not in primary and spec['scientific_role']==row['role']and ir[c]==row['incident_authorization_record']
   assert ir[c]['primary_statistics_excluded']is True and ir[c]['validated_union_authorized']is False
   lineage=spec['incident_recovery_trial_lineage'];auth=ir[c]
   for key in ['incident_id','original_cohort','original_uuid','original_negative_RESULT_sha256','original_DONE_sha256','science_projection_sha256','primary_statistics_excluded','validated_union_authorized']:assert lineage[key]==auth[key],'IR_LINEAGE_DRIFT '+key
   assert lineage['reuse_old_UUID']is False and lineage['automatic_retry']is False and lineage['refunds']==0 and lineage['new_grants']==1
  else:
   assert row['role']=='PRIMARY'and c in primary and spec.get('scientific_role')is None
   for k in ['input_digest','program','suite','cell','profile']:assert primary[c][k]==spec[k]
 return True
def install_on_frame(frame,cfg,owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];assert not hasattr(main,ID)
 engine=frame.f_locals['engine'];res=frame.f_locals['res'];q=engine.registered()[2];validate(cfg,q)
 coupling=getattr(main,COUPLING);broad=getattr(main,BROAD);tiny=getattr(main,TINY);memory=getattr(main,MEMORY);aging=res.DTC_LARGE_JOB_AGING_INSTALLED
 cpu=coupling['cpu'];gate=coupling['gate'];coupled=cpu['wrapper'];previous=res.choose_dispatch
 assert coupling['res']is res and coupling['aging']is aging and tiny.aging is aging and memory['aging']is aging and broad['aging']is aging
 assert coupling['cell'].cell_contents==gate.wrapper and cpu['original']==gate.wrapper and gate.aging is aging and gate.original_provider is tiny.frames
 assert sha(coupled.__code__.co_filename)==CPU_SHA and sha(type(gate).choose.__code__.co_filename)==GUARD_SHA
 assert broad['armed']is True and aging.original is broad['leaf']and frame.f_globals['worker']is broad['wrapper']
 refs=(frame.f_globals['worker'],aging.original,aging.frame_provider,tiny.frames,tiny.facade,tiny.facade.resources,coupling['cell'].cell_contents,gate.original_choose,cpu['wrapper'],memory['new_choose'],res.resources)
 state=dict(frame=frame,res=res,aging=aging,cpu=cpu,gate=gate,broad=broad,tiny=tiny,memory=memory,previous=previous,coupled=coupled,cfg=copy.deepcopy(cfg),refs=refs,last_issue=None,last_route=None,coupled_calls=0,legacy_calls=0)
 def choose(pending,sample,claims,history,previous_sample=None,policy=None,dispatch_index=0):
  # No pending filtering or fresh frame is fabricated here.
  try:
   current=engine.registered()[2];rows,rcfg,ocfg=validate(cfg,current)
   wholly=bool(pending)and all(s['cohort']in rows for s in pending)
   if not wholly:
    state['legacy_calls']+=1;state['last_route']='EXACT_OLD_SYNC_FOR_EMPTY_UNKNOWN_OR_MIXED'
    return previous(pending,sample,claims,history,previous_sample,policy,dispatch_index)
   with aging.lock:
    assert state['refs']==(frame.f_globals['worker'],aging.original,aging.frame_provider,tiny.frames,tiny.facade,tiny.facade.resources,coupling['cell'].cell_contents,gate.original_choose,cpu['wrapper'],memory['new_choose'],res.resources),'BRIDGE_RUNTIME_REFERENCE_DRIFT'
    assert broad['armed']is True and aging.original is broad['leaf']
    check_pending(pending,rows,cfg,current)
    producer=load('bridge_current_broad_producer',ocfg['source_paths']['producer']);assert sha(producer.__file__)==ocfg['qualified_sources']['producer'];producer.validate(ocfg,current)
    assert broad['consumer_check'](frame,ocfg)is True
    before=aging.calls;value=coupled(pending,sample,claims,history,previous_sample,policy,dispatch_index)
    assert aging.calls in [before,before+1],'AGING_ADVANCED_MORE_THAN_ONCE'
    if value is not None:assert aging.calls==before+1 and value['cohort']in {s['cohort']for s in pending}
    state.update(last_issue=None,last_route='SAME_CPU_FRAMEGUARD_PRIORITY_INNER_E_BROAD_LEAF',coupled_calls=state['coupled_calls']+1)
    return value
  except Exception as error:
   state['last_issue']=dict(status='BROAD_COUPLED_ROUTE_HOLD',error=repr(error),models_interrupted=False);return None
 with aging.lock:
  assert res.choose_dispatch is previous
  state['wrapper']=choose;res.choose_dispatch=choose;setattr(main,ID,state)
 receipt=dict(status='CURRENT_SCOPE_COUPLED_ROUTE_BRIDGE_INSTALLED',same_aging_state=id(aging.state),same_cpu_wrapper=True,same_FrameGuard=True,only_changed_reference='res.choose_dispatch',new_grants=0,models_started=0)
 state['receipt']=receipt;return state
def restore_in_owner(owner_assert,main=None):
 assert threading.current_thread()is threading.main_thread();owner_assert();main=main or sys.modules['__main__'];state=getattr(main,ID)
 with state['aging'].lock:
  assert state['res'].choose_dispatch is state['wrapper'];state['res'].choose_dispatch=state['previous'];delattr(main,ID)
 return dict(status='EXACT_PREVIOUS_OUTER_CHOOSER_RESTORED',native_routes_and_models_unchanged=True,new_grants=0,models_started=0)
