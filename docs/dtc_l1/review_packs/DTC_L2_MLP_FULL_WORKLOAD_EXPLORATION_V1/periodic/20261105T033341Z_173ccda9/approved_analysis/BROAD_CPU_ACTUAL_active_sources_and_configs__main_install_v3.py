"""Main-only broad shared CPU installation. Import is inert; no model calls.

New operational IDs are appended to a pure locked registry transaction. All
library/engine/source checks happen outside that transaction. Prior engineering
dispatch/consumer generations remain as delegating underlays.
"""
import pathlib,json,hashlib,copy,os,sys,threading,datetime,traceback,importlib.util
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
MARKER='DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1'
MAIN1_SHA='0baca56f31c65c893021f19214c77802d539c637115fa5594219005f03f632de'
RESOURCE_ID='CPU_SHARED_DYNAMIC_FUTURE_MEMORY_095_V1'
OBSERVER_ID='DTC_STRACE_BROAD_SHARED_CPU_V1'

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 p=P(p);b=raw(v)
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def event(state,phase,**extra):
 state['phase']=phase
 with(P(state['directory'])/'EVENTS.jsonl').open('ab')as f:
  f.write(json.dumps(dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,**extra),sort_keys=True).encode()+b'\n');f.flush();os.fsync(f.fileno())
def science_sha(spec,keys):
 return hashlib.sha256(json.dumps({k:spec[k]for k in keys},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def check_unused(root,q,scope,claims=None):
 """Pure passed-q/local-file checks, including inside the short authority EX."""
 root=P(root);claims=claims or{}
 disk_claims=read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 keys=scope['scientific_projection_keys'];out={}
 for row in scope['rows']:
  c=row['cohort'];p=root/'control/specs'/(c+'.json')
  assert c in q['admitted_specs']and c not in q['consumed']and c not in q.get('sealed',[])and c not in claims and c not in disk_claims,'NEW_SCOPE_IDENTITY_ALREADY_USED_OR_CLAIMED '+c
  assert not any((root/'control/qualification_ledger'/(c+x)).exists()for x in ['.INTENT.json','.DONE.json'])
  assert sha(p)==sha(root/'control'/(c+'_SPEC.json'))==q['admitted_specs'][c]
  s=read(p);assert s['cohort']==c and s['host_cpu']is None
  assert science_sha(s,keys)==row['science_projection_sha256']
  assert {k:s[k]for k in keys}==row['science_projection']
  if row['role']=='INCIDENT_RECOVERY_PERFORMANCE_TRIAL':
   assert s['scientific_role']==row['role']
   assert next(x for x in q['authorized_incident_recovery_trials']if x['cohort']==c)==row['incident_authorization_record']
   lineage=s['incident_recovery_trial_lineage'];auth=row['incident_authorization_record']
   for key in ['incident_id','original_cohort','original_uuid','original_negative_RESULT_sha256','original_DONE_sha256','science_projection_sha256','primary_statistics_excluded','validated_union_authorized']:
    assert lineage[key]==auth[key],'INCIDENT_LINEAGE_DRIFT '+key
   assert lineage['reuse_old_UUID']is False and lineage['automatic_retry']is False and lineage['refunds']==0 and lineage['new_grants']==1
  else:assert row['role']=='PRIMARY'and s.get('scientific_role')is None
  out[c]=q['admitted_specs'][c]
 return out
def append_records_locked(reg,request,records,root,scope,canonical_shas,before):
 """No engine, library validation, lease or recursive authority access here."""
 q=reg['registered_future_requests'][request]
 assert set(records)=={RESOURCE_ID,OBSERVER_ID}
 assert q['budget']==before['budget']and q['remaining']==q['budget']-len(q['consumed'])
 assert q['consumed']==before['consumed'],'CONCURRENT_CONSUMPTION_BEFORE_ARM'
 assert q['additional_operational_overlays']==before['operational_records'],'OPERATIONAL_RECORD_CAS_CONFLICT'
 assert not set(records)&set(q['additional_operational_overlays']),'NEW_IDS_ALREADY_REGISTERED'
 assert check_unused(root,q,scope)==canonical_shas
 previous=copy.deepcopy(q);q['additional_operational_overlays'].update(copy.deepcopy(records))
 expected=copy.deepcopy(previous);expected['additional_operational_overlays'].update(copy.deepcopy(records));assert q==expected
def held(state,c,reason):
 try:
  q=state['engine'].registered()[2];spent=c in q['consumed']or(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
  if spent:return dict(state='SPENT_BROAD_SCOPE_PRESERVE',cohort=c,model_retries=0,reason=reason)
  return dict(state='ZERO_START_DEFERRED',cohort=c,model_retries=0,model_starts=0,reason=reason)
 except BaseException as e:return dict(state='BROAD_SCOPE_PRESERVE',cohort=c,model_retries=0,reason=reason,identity_error=repr(e))
def contain(state):
 """Retain all installed mandatory generations; fence only selected new IDs."""
 frame=state['frame'];res=frame.f_locals['res'];previous=frame.f_globals['worker'];previous_choose=res.choose_dispatch;scope=set(state['scope'])
 def worker(c):return held(state,c,'BROAD_INSTALL_CONTAINMENT')if c in scope else previous(c)
 def choose(pending,*a,**kw):
  # Preserve the existing aging target and R accounting on a contained failure.
  # Admission is blocked after the ordinary full-pending state transition.
  decision=previous_choose(pending,*a,**kw)
  return None if decision is not None and decision['cohort']in scope else decision
 frame.f_globals['worker']=worker;res.choose_dispatch=choose
 state.update(containment_worker=worker,containment_choose=choose,armed=False)
 return dict(scope=sorted(scope),all_current_mandatory_routes_retained=True,automatic_rollback=False,automatic_retry=False,models_signaled=0)
def apply(config_path):
 cfg=read(config_path);assert cfg['schema']=='DTC_MAIN_BROAD_SHARED_CPU_INSTALL_CONFIG_V1'and cfg['root']==str(R)
 assert cfg['installer_path']==str(P(__file__))and sha(__file__)==cfg['installer_sha256']
 assert sha(cfg['Main1_source_path'])==cfg['Main1_source_sha256']==MAIN1_SHA
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'SOURCE_DRIFT '+p
 discover=load('broad_Main_original_owner_discovery',cfg['Main1_source_path'])
 main,frame,engine=discover.actual_owner(cfg);assert not hasattr(main,MARKER),'OBSERVE_EXISTING_INSTALL_NEVER_REAPPLY'
 old=main.DTC_MAIN_CPU_SHARED_STAGE2_HANDOFF_V1;assert old['frame']is frame and old['engine']is engine and old['phase']=='ARMED_ACKED'
 memory=main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;aging=memory['aging'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer'];adaptive=frame.f_locals['adaptive']
 assert old['memory']is memory and old['aging']is aging and res.DTC_LARGE_JOB_AGING_INSTALLED is aging
 ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']};assert ids==cfg['expected_frame_object_ids']
 directory=P(cfg['directory']);directory.mkdir(parents=True,exist_ok=True)
 scope=read(cfg['scope_contract_path']);scope_ids={r['cohort']for r in scope['rows']};assert len(scope_ids)==26
 state=dict(frame=frame,engine=engine,directory=str(directory),scope=scope_ids,phase='PREFLIGHT',armed=False,ever_exposed=False,old_Main2=old)
 setattr(main,MARKER,state)
 try:
  rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
  assert set(cfg['modules'])=={'library','producer','consumer','owner_frame','IR_view'}
  assert cfg['modules']['library']==rcfg['source_paths']['library']
  assert cfg['modules']['producer']==ocfg['source_paths']['producer']==rcfg['source_paths']['owner']
  assert cfg['modules']['consumer']==ocfg['source_paths']['consumer']==rcfg['source_paths']['consumer']
  for name,path in cfg['modules'].items():assert path in cfg['source_pins']and sha(path)==cfg['source_pins'][path],'PRELOAD_UNQUALIFIED_MODULE '+name
  assert cfg['source_pins'][str(P(__file__))]==cfg['installer_sha256']and cfg['source_pins'][cfg['Main1_source_path']]==MAIN1_SHA
  for contract in [rcfg,ocfg]:
   for role,path in contract['source_paths'].items():assert cfg['source_pins'][path]==contract['qualified_sources'][role]==sha(path)
  modules={k:load('broad_Main_'+k,p)for k,p in cfg['modules'].items()};state['modules']=modules
  lib=modules['library'];producer=modules['producer'];bridge=modules['consumer'];framehelper=modules['owner_frame'];irhelper=modules['IR_view']
  assert lib.ID==RESOURCE_ID and producer.ID==OBSERVER_ID
  assert set(rcfg['allowed_cohorts'])==scope_ids and rcfg['max_shared_running']is None
  assert rcfg['scope_contract_path']==cfg['scope_contract_path']and sha(cfg['scope_contract_path'])==rcfg['scope_contract_sha256']
  assert ocfg['resource_configuration_path']==cfg['resource_configuration_path']and ocfg['resource_configuration_sha256']==sha(cfg['resource_configuration_path'])
  assert ocfg['future_primary_policy']=='MATRIX_REGISTERED_UNSPENT_BPF_REQUIRED'and ocfg['future_ir_policy']=='EXACT_REGISTERED_IR11_BPF_REQUIRED'
  assert rcfg['qualification_only']is ocfg['qualification_only']is False
  with aging.lock:
   engine.assert_parent_lease();q=engine.registered()[2];canonical=check_unused(R,q,scope,frame.f_locals['claims'])
   lib.validate_broad_approval(rcfg,q)
   before=dict(budget=q['budget'],remaining=q['remaining'],consumed=copy.deepcopy(q['consumed']),operational_records=copy.deepcopy(q['additional_operational_overlays']),matrix_sha256=sha(R/'control/MATRIX_CURRENT.json'),scope_sha256=sha(R/'control/SCOPE.json'),memory_active_sha256=sha(cfg['old_memory_active_path']),context=copy.deepcopy(memory['context']['cfg']))
   assert before['matrix_sha256']==cfg['matrix_sha256']and before['scope_sha256']==cfg['scope_sha256']and before['memory_active_sha256']==cfg['old_memory_active_sha256']
   originals=dict(worker=frame.f_globals['worker'],choose=res.choose_dispatch,safe_finish=consumer.safe_finish,callbacks=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed),reader=frame.f_globals['read'],recommend=adaptive.recommend)
   state.update(before=before,originals=originals)
   records={lib.ID:dict(lib.record(rcfg),status='ACTIVE'),producer.ID:dict(producer.record(ocfg),status='ACTIVE')}
   shadow=copy.deepcopy(q);shadow['additional_operational_overlays'].update(copy.deepcopy(records));lib.validate(rcfg,shadow);producer.validate(ocfg,shadow)
   put(directory/'PREIMAGE.json',dict(budget=before['budget'],remaining=before['remaining'],old_UUIDs={c:r['uuid']for c,r in before['consumed'].items()},old_operational_records=before['operational_records'],canonical_shas=canonical,same_frame_object_ids=ids,matrix_sha256=before['matrix_sha256'],scope_sha256=before['scope_sha256'],CPU2_memory_active_sha256=before['memory_active_sha256']))
   def worker(c):return held(state,c,'BROAD_MAIN_PREARM')if c in scope_ids else originals['worker'](c)
   def choose(pending,*args,**kw):
    decision=originals['choose'](pending,*args,**kw)
    return None if not state['armed']and decision is not None and decision['cohort']in scope_ids else decision
   state.update(fence=worker,prearm_choose=choose,ever_exposed=True);frame.f_globals['worker']=worker;res.choose_dispatch=choose
   event(state,'NEW_SCOPE_PREARM_OLD_GENERATIONS_RETAINED')
   engine.update_authority(lambda reg:append_records_locked(reg,engine.REQ,records,R,scope,canonical,before))
   event(state,'NEW_OPERATIONAL_IDS_APPENDED_ZERO_GRANT')
   actual=engine.registered()[2];lib.validate(rcfg,actual);producer.validate(ocfg,actual)
   state['consumer_receipt']=bridge.install_on_frame(frame,cfg['observation_configuration_path'],engine.assert_parent_lease,main=main)
   event(state,'BROAD_TYPED_CONSUMER_INSTALLED_OVER_STAGE2')
   # Exact method and call contract are bound by the qualified helper's config.
   token=framehelper.install_on_frame(frame,rcfg,lib,engine.assert_parent_lease,main=main)
   state['owner_frame_state']=token
   assert token['enabled']is True and token['facade'].resources is token['wrapper']
   state['owner_frame_receipt']=dict(status='INSTALLED_DYNAMIC_OWNER_FRAME',helper_source_sha256=sha(cfg['modules']['owner_frame']),enabled=token['enabled'],previous_C_before=token['previous_C_before'],previous_C_after=token['previous_C_after'],policy_change_release_credit_bytes=token['policy_change_release_credit_bytes'])
   event(state,'DYNAMIC_OWNER_FRAME_SAME_GUARD_INSTALLED')
   state['dispatcher_receipt']=producer.install_owner_dispatch(frame,cfg['observation_configuration_path'],bridge.consumer_check,main=main,armed=False)
   event(state,'BROAD_DISPATCH_CLOSED_SAME_AGING_STATE')
   def current_sources():
    matrix=read(R/'control/MATRIX_CURRENT.json');frozen=read(R/'control/SCOPE.json');current=engine.registered()[2]
    def canonical_now(c):return engine.canonical(c),current['admitted_specs'][c]
    return matrix,frozen,current,canonical_now
   hooks=irhelper.make_optional_hooks(originals['reader'],originals['recommend'],current_sources,R/'control/MATRIX_CURRENT.json',cfg['IR_source_path'],cfg['IR_plan_path'],cfg['legacy_nonprimary_cohorts'])
   staged_view=hooks['reader'](R/'control/MATRIX_CURRENT.json');ir_status=dict(status=hooks['reader'].last_status,error=hooks['reader'].last_issue,runtime_view_points=len(staged_view['points']))
   state['IR_hooks']=hooks
   assert ir_status['runtime_view_points']in [355,366]
   assert bridge.consumer_check(frame,ocfg)is True and ids=={k:id(frame.f_locals[k])for k in ids}
   assert originals['callbacks']==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
   assert before['matrix_sha256']==sha(R/'control/MATRIX_CURRENT.json')and before['scope_sha256']==sha(R/'control/SCOPE.json')
   assert before['memory_active_sha256']==sha(cfg['old_memory_active_path'])and memory['context']['cfg']==before['context']
   for p,h in cfg['source_pins'].items():assert sha(p)==h,'FINAL_SOURCE_DRIFT '+p
   current=engine.registered()[2];assert check_unused(R,current,scope,frame.f_locals['claims'])==canonical
   assert current['budget']==before['budget']and current['remaining']==before['remaining']and current['consumed']==before['consumed']
   for key,value in before['operational_records'].items():assert current['additional_operational_overlays'][key]==value
   # Runtime-only view is exposed last; science files and original negatives stay.
   frame.f_globals['read']=hooks['reader'];adaptive.recommend=hooks['recommend'];event(state,'OPTIONAL_IR_RUNTIME_VIEW_EXPOSED_LAST',IR=ir_status)
   state['armed']=True;state['arm_receipt']=producer.arm_owner_dispatch(main=main)
   event(state,'BROAD_SHARED_CPU_ARMED_SAME_OWNER')
   ack=dict(schema='DTC_MAIN_BROAD_SHARED_CPU_INSTALL_ACK_V1',status='ARMED_SAME_OWNER_NOT_SIMULATION_ACCEPTANCE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=cfg['owner'],scope=sorted(scope_ids),scope_counts=scope['counts'],configuration_sha256=sha(config_path),resource_configuration_sha256=sha(cfg['resource_configuration_path']),observation_configuration_sha256=sha(cfg['observation_configuration_path']),same_frame_object_ids=ids,consumer=state['consumer_receipt'],owner_frame=state['owner_frame_receipt'],dispatcher=state['dispatcher_receipt'],IR_runtime=ir_status,arming=state['arm_receipt'],old_source_generations_and_records_preserved=True,global_CPU2_ACTIVE_context_unchanged=True,matrix_scope_unchanged=True,incident_statistical_union_authorized=False,max_shared_running=None,new_grants=0,models_started_by_callback=0,budget=current['budget'],remaining=current['remaining'])
   put(directory/'ACK.json',ack);state.update(phase='ARMED_ACKED',ACK=ack);return ack
 except BaseException as error:
  failure=dict(status='BROAD_INSTALL_HOLD_PRESERVE',error=repr(error),traceback=traceback.format_exc(),ever_exposed=state['ever_exposed'],automatic_rollback=False,automatic_retry=False,new_grants=0,models_started_by_callback=0)
  if state['ever_exposed']:
   try:failure['containment']=contain(state)
   except BaseException as e:failure['containment_error']=repr(e)
  state.update(phase='BROAD_INSTALL_HOLD_PRESERVE',failure=failure)
  try:put(directory/'ERROR.json',failure)
  except BaseException as e:state['evidence_write_error']=repr(e)
  return failure
