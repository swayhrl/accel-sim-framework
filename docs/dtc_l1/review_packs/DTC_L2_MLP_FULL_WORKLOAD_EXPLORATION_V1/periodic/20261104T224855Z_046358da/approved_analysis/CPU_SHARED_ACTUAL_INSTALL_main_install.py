"""Explicit same-owner exact1 installation; importing never installs or starts.

Caller must contain BaseException around loading this source and apply().
This source deliberately has no CLI and no native/controller invocation.
"""
import pathlib,json,hashlib,copy,os,sys,threading,importlib.util,datetime,traceback
P=pathlib.Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
MARKER='DTC_MAIN_CPU_SHARED_EXACT1_INSTALL_V1'
C='E2-DTCL2MLP-731af5428c4b8155-DH-P0-OBSCTRL-V1'
def read(p):return json.loads(P(p).read_bytes())
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 p=P(p);b=raw(v)
 if p.exists():assert p.read_bytes()==b,'IMMUTABLE_INSTALL_ARTIFACT_CONFLICT';return
 with p.open('xb')as f:f.write(b);f.flush();os.fsync(f.fileno())
def event(state,phase,**extra):
 state['phase']=phase
 value=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),phase=phase,**extra)
 with(P(state['directory'])/'EVENTS.jsonl').open('ab')as f:f.write((json.dumps(value,sort_keys=True)+'\n').encode());f.flush();os.fsync(f.fileno())
def actual_owner(cfg):
 assert threading.current_thread()is threading.main_thread(),'ACTUAL_MAIN_THREAD_REQUIRED'
 assert cfg['owner']==dict(pid=1498278,start_ticks=977758783)
 assert os.getpid()==cfg['owner']['pid']and int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==cfg['owner']['start_ticks']
 main=sys.modules['__main__'];thread=main.DTC_L2_MLP_ADDON_THREAD
 assert thread.native_id==1723771
 frame=sys._current_frames()[thread.ident]
 while frame and not(frame.f_code.co_name=='run_scheduler'and P(frame.f_code.co_filename)==R/'tools/l2_ops.py'):frame=frame.f_back
 assert frame is not None,'ACTUAL_SCHEDULER_FRAME_REQUIRED'
 engine=frame.f_locals['engine'];engine.assert_parent_lease();return main,frame,engine
def unused_identity(root,q,claims):
 root=P(root);assert C in q['admitted_specs']and C not in q['consumed']and C not in q.get('sealed',[])and C not in claims
 assert C not in read(root/'control/POOL_DISPATCH_RESERVATIONS.json')['claims']
 assert not any((root/'control/qualification_ledger'/(C+s)).exists()for s in ['.INTENT.json','.DONE.json'])
 path=root/'control/specs'/(C+'.json');alias=root/'control'/(C+'_SPEC.json');assert sha(path)==sha(alias)==q['admitted_specs'][C]
 spec=read(path);assert spec['cohort']==C and spec['host_cpu']is None and spec['scientific_role']=='ENGINEERING_OBSERVATION_CANARY';return spec
def append_records_locked(reg,request,records,root,expected_canonical_sha256):
 """Pure current locked q/files. NO engine, lease, library or authority call."""
 q=reg['registered_future_requests'][request]
 assert q['remaining']==q['budget']-len(q['consumed'])and q['budget']==len(q['admitted_specs'])
 unused_identity(root,q,{})
 assert q['admitted_specs'][C]==expected_canonical_sha256,'PREPARED_CURRENT_CANONICAL_DRIFT'
 before=copy.deepcopy(q)
 for key,value in records.items():
  if key in q['additional_operational_overlays']:assert q['additional_operational_overlays'][key]==value,'EXISTING_OPERATIONAL_RECORD_CONFLICT'
 q['additional_operational_overlays'].update(copy.deepcopy(records))
 expected=copy.deepcopy(before);expected['additional_operational_overlays'].update(copy.deepcopy(records));assert q==expected
def selected_hold(state,c,reason):
 try:
  q=state['engine'].registered()[2]
  spent=c in q['consumed']or(R/'control/qualification_ledger'/(c+'.INTENT.json')).exists()
  if spent:return dict(state='SPENT_ENGINEERING_PRESERVE',cohort=c,model_retries=0,reason=reason)
  assert c in q['admitted_specs'],'UNKNOWN_SELECTED_IDENTITY'
  return dict(state='ZERO_START_DEFERRED',cohort=c,model_starts=0,model_retries=0,reason=reason)
 except BaseException as error:return dict(state='ENGINEERING_PRESERVE',cohort=c,model_retries=0,reason=reason,identity_error=repr(error))
def contain_selected(state):
 """Retain mandatory typed routes; prevent cached selected work from old entry."""
 frame=state['frame'];res=frame.f_locals['res'];old_worker=frame.f_globals['worker'];old_choose=res.choose_dispatch
 def worker(c):
  if c==C:return selected_hold(state,c,'CPU_SHARED_INSTALL_CONTAINMENT_HOLD')
  return old_worker(c)
 def choose(pending,*args,**kwargs):return old_choose([s for s in pending if s['cohort']!=C],*args,**kwargs)
 frame.f_globals['worker']=worker;res.choose_dispatch=choose
 state['containment_worker']=worker;state['containment_choose']=choose
 return dict(exact_cohort=C,mandatory_consumer_retained=True,healthy_models_signaled=0,old_other_work_delegates=True)
def apply(config_path):
 config_path=P(config_path);cfg=read(config_path)
 assert cfg['schema']=='MAIN_CPU_SHARED_EXACT1_INSTALL_CONFIG_V1'and cfg['root']==str(R)
 assert sha(__file__)==cfg['installer_sha256']and cfg['installer_path']==str(P(__file__))
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'SOURCE_DRIFT '+p
 main,frame,engine=actual_owner(cfg);assert not hasattr(main,MARKER),'OBSERVE_OR_RECONCILE_EXISTING_INSTALL_STATE_DO_NOT_REPEAT'
 directory=P(cfg['directory']);directory.mkdir(parents=True,exist_ok=True)
 memory=main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;aging=memory['aging'];res=frame.f_locals['res'];consumer=frame.f_locals['consumer']
 assert aging is res.DTC_LARGE_JOB_AGING_INSTALLED
 ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']};assert all(ids[k]==v for k,v in cfg['expected_frame_object_ids'].items())
 state=dict(directory=str(directory),frame=frame,engine=engine,memory=memory,aging=aging,phase='PREFLIGHT',ever_exposed=False,config_path=str(config_path),config_sha256=sha(config_path),model_starts_by_callback=0,new_grants=0)
 setattr(main,MARKER,state)
 try:
  modules={k:load('main_shared_'+k,p)for k,p in cfg['modules'].items()};state['modules']=modules
  lib=modules['library'];producer=modules['producer'];bridge=modules['consumer']
  rcfg=read(cfg['resource_configuration_path']);ocfg=read(cfg['observation_configuration_path'])
  assert rcfg['allowed_cohorts']==[C]and rcfg['max_shared_running']==1 and set(ocfg['modes'])=={C}and ocfg['modes'][C]=='DEFAULT_CONTROL'
  assert rcfg['qualification_only']is False and ocfg['qualification_only']is False
  assert ocfg['resource_configuration_sha256']==sha(cfg['resource_configuration_path'])
  with aging.lock:
   engine.assert_parent_lease();q=engine.registered()[2];spec=unused_identity(R,q,frame.f_locals['claims'])
   producer.verify_engineering_spec(ocfg,C,'DEFAULT_CONTROL',spec)
   before=dict(budget=q['budget'],remaining=q['remaining'],old_UUIDs={c:r['uuid']for c,r in q['consumed'].items()},matrix_sha256=sha(R/'control/MATRIX_CURRENT.json'),scope_sha256=sha(R/'control/SCOPE.json'),memory_active_sha256=sha(cfg['old_memory_active_path']),context=copy.deepcopy(memory['context']['cfg']))
   assert before['matrix_sha256']==cfg['matrix_sha256']and before['scope_sha256']==cfg['scope_sha256']and before['memory_active_sha256']==cfg['old_memory_active_sha256']
   originals=dict(worker=frame.f_globals['worker'],choose=res.choose_dispatch,safe_finish=consumer.safe_finish,callbacks=(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed))
   state.update(before=before,originals=originals)
   put(directory/'PREIMAGE.json',{k:v for k,v in before.items()if k!='context'})
   # ExactC is already in the old runtime view. Fence BEFORE changing its
   # consumer; aging does not cover an old cached choose->claim->submit gap.
   def fence(c):
    if c==C:return selected_hold(state,c,'CPU_SHARED_INSTALL_PREARM')
    return originals['worker'](c)
   # Old V2 engineering readiness checks require its safe_finish to be the
   # outermost route. While Shared is outer, defer new old-engineer admissions
   # rather than creating spurious zero-start postprocessing evidence.
   contract=read(cfg['exclusion_contract_path']);assert sha(cfg['exclusion_contract_path'])==cfg['exclusion_contract_sha256']
   old_engineers=set(contract['scope_cohorts'])-{C};assert len(old_engineers)==3
   def readiness_choose(pending,*args,**kwargs):return originals['choose']([s for s in pending if s['cohort']not in old_engineers|{C}],*args,**kwargs)
   state['ever_exposed']=True;state['fence']=fence;state['readiness_choose']=readiness_choose;state['temporarily_deferred_old_engineers']=sorted(old_engineers)
   frame.f_globals['worker']=fence;res.choose_dispatch=readiness_choose
   event(state,'PREARM_FENCE_INSTALLED',temporarily_deferred_old_engineers=sorted(old_engineers))
   q=engine.registered()[2];unused_identity(R,q,frame.f_locals['claims'])
   records={lib.ID:dict(lib.record(rcfg),status='ACTIVE'),producer.ID:dict(producer.record(ocfg),status='ACTIVE')}
   shadow=copy.deepcopy(q);shadow['additional_operational_overlays'].update(copy.deepcopy(records))
   lib.validate(rcfg,shadow);producer.validate(ocfg,shadow)
   # No validation helper or engine reader is invoked under the EX lock.
   expected_current_canonical=q['admitted_specs'][C]
   engine.update_authority(lambda reg:append_records_locked(reg,engine.REQ,records,R,expected_current_canonical))
   state['records']=records;event(state,'ZERO_GRANT_OPERATIONAL_RECORDS_REGISTERED')
   actual=engine.registered()[2];lib.validate(rcfg,actual);producer.validate(ocfg,actual)
   er=bridge.install_on_frame(frame,cfg['observation_configuration_path'],cfg['exclusion_contract_path'],cfg['exclusion_contract_sha256'],engine.assert_parent_lease,main=main)
   state['consumer_receipt']=er;event(state,'MANDATORY_SHARED_CONSUMER_INSTALLED')
   br=producer.install_owner_dispatch(frame,cfg['observation_configuration_path'],bridge.consumer_check,main=main,armed=False)
   state['dispatcher_receipt']=br;event(state,'FINITE_SHARED_DISPATCHER_INSTALLED_UNARMED')
   assert bridge.consumer_check(frame,ocfg)is True
   assert originals['callbacks']==(consumer.load,consumer.finish_evidence,consumer.put,consumer.archive_closed)
   assert ids=={k:id(frame.f_locals[k])for k in ids}
   assert sha(R/'control/MATRIX_CURRENT.json')==before['matrix_sha256']and sha(R/'control/SCOPE.json')==before['scope_sha256']
   assert sha(cfg['old_memory_active_path'])==before['memory_active_sha256']and memory['context']['cfg']==before['context']
   for p,h in cfg['source_pins'].items():assert sha(p)==h,'FINAL_SOURCE_DRIFT '+p
   q=engine.registered()[2];unused_identity(R,q,frame.f_locals['claims'])
   assert q['budget']==before['budget']and all(q['consumed'][c]['uuid']==u for c,u in before['old_UUIDs'].items())
   ar=producer.arm_owner_dispatch(main=main);state['arm_receipt']=ar;event(state,'ARMED_EXISTING_SINGLE_CONTROLLER')
   q=engine.registered()[2]
   ack=dict(schema='MAIN_CPU_SHARED_EXACT1_INSTALL_ACK_V1',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='ARMED_EXISTING_SINGLE_OWNER_NOT_CANARY_ACCEPTANCE',owner=cfg['owner'],configuration_path=str(config_path),configuration_sha256=sha(config_path),resource_configuration_sha256=sha(cfg['resource_configuration_path']),observation_configuration_sha256=sha(cfg['observation_configuration_path']),cohort=C,consumer=er,dispatcher=br,arming=ar,old_scope_matrix_CPU2_context_unchanged=True,temporarily_deferred_old_engineers=sorted(old_engineers),readiness_mask_requires_explicit_Main_restore_after_shared_routes_restore=True,budget=q['budget'],remaining=q['remaining'],new_grants=0,model_starts_by_callback=0,callback_never_calls_worker=True,cohort_consumed_at_ACK=C in q['consumed'],cohort_UUID_at_ACK=q['consumed'].get(C,{}).get('uuid'),source_pins=cfg['source_pins'])
   put(directory/'ACK.json',ack);state['ACK']=ack;state['phase']='ARMED_ACKED';return ack
 except BaseException as error:
  failure=dict(status='INSTALL_ENGINEERING_HOLD_PRESERVE',error=repr(error),traceback=traceback.format_exc(),ever_exposed=state['ever_exposed'],model_starts_by_callback=0,new_grants=0)
  if state['ever_exposed']:
   try:failure['containment']=contain_selected(state)
   except BaseException as containment_error:failure['containment_error']=repr(containment_error)
  state.update(phase='INSTALL_ENGINEERING_HOLD_PRESERVE',failure=failure)
  try:put(directory/'ERROR.json',failure)
  except BaseException as evidence_error:state['failure_evidence_error']=repr(evidence_error)
  return failure
