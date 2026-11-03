"""Main-only independent operational repair. No simulation or source edits."""
from pathlib import Path
import json,hashlib,copy,sys,os,threading,datetime,traceback,importlib.util
P=Path
R=P('/root/data/dtc_l2_mlp_exploration_20261027_v1')
ID='BROAD_CPU_OWNER_FRAME_NOFLAG_V2'
MARKER='DTC_MAIN_OWNER_FRAME_NOFLAG_AUX_V2'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with P(p).open('xb')as f:f.write(raw(v));f.flush();os.fsync(f.fileno())
def append_aux_locked(reg,request,before,row):
 """Pure passed registry only: no file/engine/lease/library calls under EX."""
 q=reg['registered_future_requests'][request]
 assert ID not in q['additional_operational_overlays']
 assert q['budget']==before['budget']and q['remaining']==before['remaining']
 assert q['remaining']==q['budget']-len(q['consumed'])and q['consumed']==before['consumed']
 assert q['additional_operational_overlays']==before['records']
 prior=copy.deepcopy(q);q['additional_operational_overlays'][ID]=copy.deepcopy(row)
 expected=copy.deepcopy(prior);expected['additional_operational_overlays'][ID]=copy.deepcopy(row);assert q==expected
def apply(config_path):
 cfg=read(config_path)
 assert cfg['schema']=='DTC_MAIN_OWNER_FRAME_NOFLAG_AUX_INSTALL_CONFIG_V2'
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 assert cfg['installer_path']==str(P(__file__))and sha(__file__)==cfg['installer_sha256']
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'AUX_SOURCE_DRIFT '+p
 assert set(cfg['modules'])=={'adapter','library'}
 for name,path in cfg['modules'].items():assert cfg['source_pins'][path]==sha(path)
 resource_cfg=read(cfg['resource_configuration_path']);adapter_cfg=read(cfg['adapter_configuration_path'])
 assert cfg['modules']['adapter']==adapter_cfg['source_path']and cfg['modules']['library']==resource_cfg['source_paths']['library']
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'OBSERVE_PREVIOUS_AUX_ATTEMPT_NEVER_REAPPLY'
 old=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1;assert old['phase']=='ARMED_ACKED'and old['armed']is True
 frame=old['frame'];engine=old['engine'];engine.assert_parent_lease()
 assert old['ACK']['configuration_sha256']==cfg['Main3_configuration_sha256']
 ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']};assert ids==old['ACK']['same_frame_object_ids']
 directory=P(cfg['directory']);directory.mkdir(parents=True,exist_ok=True)
 state=dict(phase='PREFLIGHT',directory=str(directory),frame=frame,engine=engine,old_Main3=old)
 setattr(main,MARKER,state)
 try:
  helper=load('actual_aux_NOFLAG_frame_helper',cfg['modules']['adapter']);lib=load('actual_aux_unchanged_dynamic_resource',cfg['modules']['library'])
  assert helper.ID==ID;state.update(helper=helper,lib=lib)
  tiny=main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1;aging=tiny.aging
  with aging.lock:
   engine.assert_parent_lease();q=engine.registered()[2]
   assert tiny.facade.resources is old['owner_frame_state']['wrapper']and old['owner_frame_state']['enabled']is True
   B=main.DTC_STRACE_BROAD_SHARED_DISPATCH_V1
   refs=(tiny.frames,tiny.facade,aging.frame_provider,tiny.coupling['gate'].original_provider,tiny.coupling['gate'].wrapper,aging.original,frame.f_globals['worker'],frame.f_locals['res'].choose_dispatch,frame.f_locals['consumer'].safe_finish)
   assert B['armed']and aging.original is B['leaf']
   before=dict(budget=q['budget'],remaining=q['remaining'],consumed=copy.deepcopy(q['consumed']),records=copy.deepcopy(q['additional_operational_overlays']),protected=copy.deepcopy(aging.state.protected),tokens=copy.deepcopy(aging.state.pending_releases))
   row=helper.record(adapter_cfg);shadow=copy.deepcopy(q);shadow['additional_operational_overlays'][ID]=row;helper.validate(adapter_cfg,resource_cfg,lib,shadow)
   put(directory/'PREIMAGE.json',dict(budget=q['budget'],remaining=q['remaining'],old_UUIDs={c:x['uuid']for c,x in q['consumed'].items()},old_operational_records=before['records'],protected_bytes=before['protected'],pending_release_count=len(before['tokens']),old_frame_wrapper_source_sha256='94dd822a5cacb1b68b7c17ea98945f024cd351d263954eb7b20c8de850900760'))
   engine.update_authority(lambda reg:append_aux_locked(reg,engine.REQ,before,row))
   state['phase']='AUX_RECORD_REGISTERED_ZERO_GRANT'
   token=helper.install_on_frame(frame,resource_cfg,adapter_cfg,lib,engine.assert_parent_lease,main=main);state['adapter_state']=token
   assert token['enabled']is True and tiny.facade.resources is token['wrapper']
   assert token['policy_change_release_credit_bytes']==0
   assert refs==(tiny.frames,tiny.facade,aging.frame_provider,tiny.coupling['gate'].original_provider,tiny.coupling['gate'].wrapper,aging.original,frame.f_globals['worker'],frame.f_locals['res'].choose_dispatch,frame.f_locals['consumer'].safe_finish)
   assert aging.state.protected==before['protected']and aging.state.pending_releases==before['tokens']
   after=engine.registered()[2];assert after['budget']==before['budget']and after['remaining']==before['remaining']and after['consumed']==before['consumed']
   assert all(after['additional_operational_overlays'][k]==v for k,v in before['records'].items())
   for p,h in cfg['source_pins'].items():assert sha(p)==h,'AUX_FINAL_SOURCE_DRIFT '+p
   ack=dict(schema='DTC_MAIN_OWNER_FRAME_NOFLAG_AUX_ACK_V2',status='INSTALLED_SAME_OWNER_TRUE_RAW_NOFLAG_FRAME_NOT_SIMULATION_ACCEPTANCE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,configuration_sha256=sha(config_path),adapter_configuration_sha256=sha(cfg['adapter_configuration_path']),adapter_source_sha256=sha(cfg['modules']['adapter']),unchanged_resource_configuration_sha256=sha(cfg['resource_configuration_path']),prior_Main3_configuration_sha256=cfg['Main3_configuration_sha256'],same_frame_object_ids=ids,exact_guard_aging_leaf_worker_chooser_consumer_refs_preserved=True,old_all_records_preserved=True,protected_bytes=aging.state.protected,pending_release_count=len(aging.state.pending_releases),policy_change_release_credit_bytes=0,previous_C_before=token['previous_C_before'],previous_C_after=token['previous_C_after'],models_started_by_callback=0,new_grants=0,budget=after['budget'],remaining=after['remaining'])
   put(directory/'ACK.json',ack);state.update(phase='INSTALLED_ACKED',ACK=ack);return ack
 except BaseException as error:
  value=dict(status='AUX_FRAME_INSTALL_HOLD_PRESERVE',phase=state['phase'],error=repr(error),traceback=traceback.format_exc(),automatic_retry=False,automatic_rollback=False,models_started_by_callback=0,new_grants=0)
  state.update(phase='HOLD_PRESERVE',failure=value)
  try:put(directory/'ERROR.json',value)
  except BaseException as e:state['error_evidence_failure']=repr(e)
  return value
