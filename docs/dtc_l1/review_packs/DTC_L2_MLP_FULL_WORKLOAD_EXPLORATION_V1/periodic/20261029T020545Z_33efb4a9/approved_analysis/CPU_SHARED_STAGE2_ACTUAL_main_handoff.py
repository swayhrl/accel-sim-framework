"""Main-only Stage2 handoff candidate. Import is inert; no CLI or model calls.

Source validation is outside authority EX. replace_records_locked is deliberately
limited to the passed registry plus local canonical/alias/claim file reads.
The caller must contain BaseException while loading this module as well.
"""
import pathlib,json,hashlib,copy,os,sys,threading,importlib.util,datetime,traceback
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
MARKER='DTC_MAIN_CPU_SHARED_STAGE2_HANDOFF_V1'
OLD_MARKER='DTC_MAIN_CPU_SHARED_EXACT1_INSTALL_V1'
MAIN1_SHA='0baca56f31c65c893021f19214c77802d539c637115fa5594219005f03f632de'
RESOURCE_ID='CPU_SHARED_TIMESLICE_FUTURE_MEMORY_095_V1'
OBSERVATION_ID='DTC_STRACE_SHARED_CPU_OBSERVATION_V1'
FIRST='E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1'
FOUR=(FIRST,'E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSBPF-V1','E2-DTCL2MLP-16f4c42373e4961e-DH-P0-OBSCTRL-V1','E2-DTCL2MLP-16f4c42373e4961e-DH-P0-OBSBPF-V1')

def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def digest(v):return hashlib.sha256(raw(v)).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put_bytes(p,data):
 p=P(p)
 if p.exists():assert p.read_bytes()==data,'IMMUTABLE_HANDOFF_ARTIFACT_CONFLICT';return
 with p.open('xb')as f:f.write(data);f.flush();os.fsync(f.fileno())
 fd=os.open(p.parent,os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def put(p,v):put_bytes(p,raw(v))
def event(state,phase,**extra):
 state['phase']=phase
 value=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,**extra)
 with(P(state['directory'])/'EVENTS.jsonl').open('ab')as f:f.write(raw(value).replace(b'\n',b'')+b'\n');f.flush();os.fsync(f.fileno())
def fresh_scope(q):
 assert all(c in q['admitted_specs']for c in FOUR),'ORIGINAL_FOUR_NOT_ALL_ADMITTED'
 assert FIRST in q['consumed'],'FIRST_ACTUAL_CANARY_NOT_CONSUMED'
 return tuple(c for c in FOUR if c not in q['consumed']and c not in q.get('sealed',[]))
def unused_identity(root,q,c,claims):
 """Pure passed-q/files validation; safe inside the short authority callback."""
 root=P(root);assert c in FOUR and c in q['admitted_specs']and c not in q['consumed']and c not in q.get('sealed',[])and c not in claims
 assert c not in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 assert not any((root/'control/qualification_ledger'/(c+s)).exists()for s in ['.INTENT.json','.DONE.json'])
 path=root/'control/specs'/(c+'.json');alias=root/'control'/(c+'_SPEC.json');assert sha(path)==sha(alias)==q['admitted_specs'][c]
 spec=read(path);assert spec['cohort']==c and spec['host_cpu']is None and spec['scientific_role']=='ENGINEERING_OBSERVATION_CANARY';return spec
def replace_records_locked(reg,request,old_records,new_records,root,scope,canonical_shas,budget,old_uuids):
 """NO engine, registered(), lease, source/lib validator or authority access."""
 q=reg['registered_future_requests'][request]
 assert set(old_records)==set(new_records)=={RESOURCE_ID,OBSERVATION_ID}
 assert q['budget']==budget and q['remaining']==q['budget']-len(q['consumed'])
 assert all(q['consumed'].get(c,{}).get('uuid')==u for c,u in old_uuids.items()),'PREVIOUS_UUID_CHANGED'
 assert all(q['additional_operational_overlays'][k]==v for k,v in old_records.items()),'OPERATIONAL_RECORD_CAS_CONFLICT'
 assert tuple(fresh_scope(q))==tuple(scope),'UNUSED_SCOPE_CHANGED_WHILE_FENCED'
 for c in scope:
  unused_identity(root,q,c,{})
  assert q['admitted_specs'][c]==canonical_shas[c],'CURRENT_CANONICAL_CAS_CONFLICT'
 before=copy.deepcopy(q);q['additional_operational_overlays'].update(copy.deepcopy(new_records))
 expected=copy.deepcopy(before);expected['additional_operational_overlays'].update(copy.deepcopy(new_records));assert q==expected
 assert q['budget']==before['budget']and q['remaining']==before['remaining']and q['consumed']==before['consumed']
def selected_hold(state,c,reason):
 try:
  q=state['engine'].registered()[2]
  if c in q['consumed']or(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists():
   return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,model_retries=0,uuid=q['consumed'].get(c,{}).get('uuid'),reason=reason)
  assert c in q['admitted_specs'],'UNKNOWN_SELECTED_IDENTITY'
  return dict(state='ZERO_START_DEFERRED',cohort=c,model_starts=0,model_retries=0,reason=reason)
 except BaseException as error:return dict(state='ENGINEERING_PRESERVE',cohort=c,model_retries=0,reason=reason,identity_error=repr(error))
def contain_selected(state):
 """Do not dismantle whichever mandatory old/new routes already exist."""
 frame=state['frame'];res=state['res'];current_worker=frame.f_globals['worker'];current_choose=res.choose_dispatch
 def worker(c):
  if c in FOUR:return selected_hold(state,c,'SHARED_STAGE2_HANDOFF_CONTAINMENT_HOLD')
  return current_worker(c)
 def choose(pending,*args,**kwargs):return current_choose([s for s in pending if s['cohort']not in FOUR],*args,**kwargs)
 frame.f_globals['worker']=worker;res.choose_dispatch=choose
 state.update(containment_worker=worker,containment_choose=choose)
 return dict(scope=list(FOUR),old_and_new_mandatory_routes_retained=True,existing_models_signaled=0,automatic_rollback=False,automatic_retry=False)
def merged_records(old_records,base_records,preimage):
 result={}
 for key,base in base_records.items():
  row=copy.deepcopy(old_records[key]);history=copy.deepcopy(row.get('operational_generation_history',[]))
  history.append(dict(previous_record_path=preimage['path'],previous_record_file_sha256=preimage['sha256'],previous_record_key=key,previous_record_sha256=digest(old_records[key])))
  row.update(copy.deepcopy(base));row['operational_generation_history']=history;result[key]=row
 return result
def apply(config_path):
 config_path=P(config_path);cfg=read(config_path)
 assert cfg['schema']=='MAIN_CPU_SHARED_STAGE2_HANDOFF_CONFIG_V1'and cfg['root']==str(R)
 assert cfg['installer_path']==str(P(__file__))and sha(__file__)==cfg['installer_sha256']
 assert sha(cfg['Main1_source_path'])==cfg['Main1_source_sha256']==MAIN1_SHA
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'SOURCE_DRIFT '+p
 main1_source=load('main_stage2_exact_Main1_owner_discovery',cfg['Main1_source_path'])
 main,frame,engine=main1_source.actual_owner(cfg);assert not hasattr(main,MARKER),'EXISTING_HANDOFF_STATE_REQUIRES_MAIN_RECONCILIATION_NOT_REAPPLY'
 old=getattr(main,OLD_MARKER);assert old['frame']is frame and old['engine']is engine and old['phase']=='ARMED_ACKED'
 memory=main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;aging=memory['aging'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer']
 assert old['memory']is memory and old['aging']is aging and aging is res.DTC_LARGE_JOB_AGING_INSTALLED
 ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']};assert ids==cfg['expected_frame_object_ids']
 directory=P(cfg['directory']);directory.mkdir(parents=True,exist_ok=True)
 state=dict(directory=str(directory),frame=frame,engine=engine,res=res,memory=memory,aging=aging,old_Main1=old,phase='PREFLIGHT',ever_exposed=False,config_path=str(config_path),config_sha256=sha(config_path),new_grants=0,model_starts_by_callback=0)
 setattr(main,MARKER,state)
 try:
  rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
  assert set(cfg['modules'])=={'library','producer','consumer'}
  assert cfg['modules']==dict(library=rcfg['source_paths']['library'],producer=ocfg['source_paths']['producer'],consumer=ocfg['source_paths']['consumer'])
  for contract in [rcfg,ocfg]:
   for role,path in contract['source_paths'].items():assert cfg['source_pins'][path]==contract['qualified_sources'][role]==sha(path),'INSTALL_CONFIG_SOURCE_SET_JOIN'
  assert cfg['source_pins'][cfg['Main1_source_path']]==MAIN1_SHA and cfg['source_pins'][str(P(__file__))]==cfg['installer_sha256']
  modules={k:load('main_stage2_'+k,p)for k,p in cfg['modules'].items()};state['modules']=modules
  lib=modules['library'];producer=modules['producer'];bridge=modules['consumer']
  assert set(rcfg['allowed_cohorts'])==set(FOUR)and len(rcfg['allowed_cohorts'])==4 and rcfg['max_shared_running']==1 and rcfg['qualification_stage']=='AFTER_NATURAL_SHARED_CANARY'
  assert ocfg['modes']=={c:'BPF_REQUIRED'if'-OBSBPF-'in c else'DEFAULT_CONTROL'for c in FOUR}and ocfg['future_primary_policy']=='NONE'
  assert rcfg['qualification_only']is ocfg['qualification_only']is False
  assert ocfg['resource_configuration_sha256']==sha(cfg['resource_configuration_path'])
  with aging.lock:
   engine.assert_parent_lease();q=engine.registered()[2];scope=fresh_scope(q)
   # Legitimately already-born old generations are preserved, never resubmitted.
   for c in scope:producer.verify_engineering_spec(ocfg,c,ocfg['modes'][c],unused_identity(R,q,c,frame.f_locals['claims']))
   assert originals_callbacks(old,consumer),'ORIGINAL_SHARED_CONSUMER_CALLBACKS_CHANGED'
   old_dispatch=getattr(main,producer.OWNER_MARKER)
   assert frame.f_globals['worker']is old_dispatch['wrapper']and res.choose_dispatch is old_dispatch['chooser']
   assert old_dispatch['previous_choose']is old['readiness_choose'],'MAIN1_ALL_FOUR_READINESS_MASK_NOT_RETAINED'
   before=dict(budget=q['budget'],remaining=q['remaining'],old_UUIDs={c:r['uuid']for c,r in q['consumed'].items()},matrix_sha256=sha(R/'control/MATRIX_CURRENT.json'),scope_sha256=sha(R/'control/SCOPE.json'),memory_active_sha256=sha(cfg['old_memory_active_path']),context=copy.deepcopy(memory['context']['cfg']),old_records={k:copy.deepcopy(q['additional_operational_overlays'][k])for k in [RESOURCE_ID,OBSERVATION_ID]})
   assert before['matrix_sha256']==cfg['matrix_sha256']and before['scope_sha256']==cfg['scope_sha256']and before['memory_active_sha256']==cfg['old_memory_active_sha256']
   state.update(before=before,scope=scope)
   old_observation=read(old['config_path'])['observation_configuration_path'];old_resource=read(old['config_path'])['resource_configuration_path']
   for old_config in [read(old_observation),read(old_resource)]:
    for role,path in old_config['source_paths'].items():assert sha(path)==old_config['qualified_sources'][role],'OLD_GENERATION_SOURCE_PATH_CHANGED'
   old_config_files={}
   for name,path in [('old_observation',old_observation),('old_resource',old_resource),('old_Main1_config',old['config_path'])]:
    body=P(path).read_bytes();target=directory/(name+'.'+hashlib.sha256(body).hexdigest()+'.json');put_bytes(target,body);old_config_files[name]=dict(original_path=path,preimage_path=str(target),sha256=sha(target))
   put(directory/'OLD_OPERATIONAL_RECORDS.json',before['old_records']);record_preimage=dict(path=str(directory/'OLD_OPERATIONAL_RECORDS.json'),sha256=sha(directory/'OLD_OPERATIONAL_RECORDS.json'))
   put(directory/'PREIMAGE.json',dict(before={k:v for k,v in before.items()if k!='context'},old_config_files=old_config_files,current_scope=list(scope),frame_object_ids=ids,old_Main1_marker=OLD_MARKER))
   if not scope:
    value=dict(status='STAGE2_NOT_NEEDED_ALL_ORIGINAL_IDENTITIES_ALREADY_CONSUMED_OR_SEALED',old_routes_unchanged=True,new_grants=0,models_started=0)
    put(directory/'NO_UNUSED_SCOPE.json',value);state.update(phase='NO_UNUSED_SCOPE',result=value);return value
   base_records={lib.ID:dict(lib.record(rcfg),status='ACTIVE'),producer.ID:dict(producer.record(ocfg),status='ACTIVE')}
   assert set(base_records)=={RESOURCE_ID,OBSERVATION_ID}
   records=merged_records(before['old_records'],base_records,record_preimage);shadow=copy.deepcopy(q);shadow['additional_operational_overlays'].update(copy.deepcopy(records))
   lib.validate(rcfg,shadow);producer.validate(ocfg,shadow)
   state['records']=records;state['ever_exposed']=True
   # Main1's existing all-four readiness mask remains until the new fence.
   state['B1_restore']=old['modules']['producer'].restore_owner_dispatch(main=main)
   assert res.choose_dispatch is old['readiness_choose']and frame.f_globals['worker']is old['fence']
   state['E1_restore']=old['modules']['consumer'].restore_in_owner(engine.assert_parent_lease,main=main)
   assert consumer.safe_finish is old['originals']['safe_finish']and originals_callbacks(old,consumer)
   assert res.choose_dispatch is old['readiness_choose'],'OLD_THREE_READINESS_WINDOW'
   def fence(c):
    if c in FOUR:return selected_hold(state,c,'SHARED_STAGE2_PREARM')
    return old['originals']['worker'](c)
   def masked_choose(pending,*args,**kwargs):return old['originals']['choose']([s for s in pending if s['cohort']not in FOUR],*args,**kwargs)
   state.update(fence=fence,masked_choose=masked_choose);frame.f_globals['worker']=fence;res.choose_dispatch=masked_choose
   event(state,'STAGE1_RESTORED_STAGE2_ALL_FOUR_PREARM_RETAINED',scope=list(scope),old_restored=True)
   q=engine.registered()[2];assert fresh_scope(q)==scope,'UNEXPECTED_NEW_BIRTH_IN_HANDOFF_WINDOW'
   canonical_shas={c:q['admitted_specs'][c]for c in scope}
   for c in scope:unused_identity(R,q,c,frame.f_locals['claims'])
   # Everything inside this callback is passed-q and bounded file validation.
   engine.update_authority(lambda reg:replace_records_locked(reg,engine.REQ,before['old_records'],records,R,scope,canonical_shas,before['budget'],before['old_UUIDs']))
   event(state,'SAME_ID_OPERATIONAL_RECORDS_CAS_REPLACED_ZERO_GRANT')
   actual=engine.registered()[2];lib.validate(rcfg,actual);producer.validate(ocfg,actual)
   state['consumer_receipt']=bridge.install_on_frame(frame,cfg['observation_configuration_path'],cfg['exclusion_contract_path'],cfg['exclusion_contract_sha256'],engine.assert_parent_lease,main=main)
   event(state,'STAGE2_TYPED_CONSUMER_INSTALLED')
   state['dispatcher_receipt']=producer.install_owner_dispatch(frame,cfg['observation_configuration_path'],bridge.consumer_check,main=main,armed=False)
   event(state,'STAGE2_DISPATCH_INSTALLED_UNARMED')
   assert bridge.consumer_check(frame,ocfg)is True and ids=={k:id(frame.f_locals[k])for k in ids}and originals_callbacks(old,consumer)
   assert sha(R/'control/MATRIX_CURRENT.json')==before['matrix_sha256']and sha(R/'control/SCOPE.json')==before['scope_sha256']
   assert sha(cfg['old_memory_active_path'])==before['memory_active_sha256']and memory['context']['cfg']==before['context']
   for p,h in cfg['source_pins'].items():assert sha(p)==h,'FINAL_SOURCE_DRIFT '+p
   q=engine.registered()[2];assert fresh_scope(q)==scope and q['budget']==before['budget']and all(q['consumed'][c]['uuid']==u for c,u in before['old_UUIDs'].items())
   for c in scope:producer.verify_engineering_spec(ocfg,c,ocfg['modes'][c],unused_identity(R,q,c,frame.f_locals['claims']))
   state['arm_receipt']=producer.arm_owner_dispatch(main=main);event(state,'STAGE2_ARMED_SAME_OWNER')
   q=engine.registered()[2];ack=dict(schema='MAIN_CPU_SHARED_STAGE2_HANDOFF_ACK_V1',status='ARMED_SAME_OWNER_NOT_SIMULATION_ACCEPTANCE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner=cfg['owner'],configuration_path=str(config_path),configuration_sha256=sha(config_path),scope=list(scope),already_consumed_preserved={c:q['consumed'][c]['uuid']for c in FOUR if c in q['consumed']},resource_configuration_sha256=sha(cfg['resource_configuration_path']),observation_configuration_sha256=sha(cfg['observation_configuration_path']),old_record_preimage=record_preimage,old_config_files=old_config_files,consumer=state['consumer_receipt'],dispatcher=state['dispatcher_receipt'],arming=state['arm_receipt'],same_frame_object_ids=ids,old_matrix_scope_CPU2_context_unchanged=True,max_shared_running=1,new_grants=0,model_starts_by_callback=0,callback_never_calls_worker=True,budget=q['budget'],remaining=q['remaining'],source_pins=cfg['source_pins'])
   put(directory/'ACK.json',ack);state.update(phase='ARMED_ACKED',ACK=ack);return ack
 except BaseException as error:
  failure=dict(status='STAGE2_HANDOFF_HOLD_PRESERVE',error=repr(error),traceback=traceback.format_exc(),ever_exposed=state['ever_exposed'],model_starts_by_callback=0,new_grants=0,automatic_rollback=False,automatic_retry=False)
  if state['ever_exposed']:
   try:failure['containment']=contain_selected(state)
   except BaseException as inner:failure['containment_error']=repr(inner)
  state.update(phase='STAGE2_HANDOFF_HOLD_PRESERVE',failure=failure)
  try:put(directory/'ERROR.json',failure)
  except BaseException as evidence_error:state['failure_evidence_error']=repr(evidence_error)
  return failure
def originals_callbacks(old,consumer):
 return old['originals']['callbacks']==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
