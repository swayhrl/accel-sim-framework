"""Main-only, one-reference current-scope chooser repair. Import is inert."""
from pathlib import Path
import json,hashlib,copy,sys,os,threading,datetime,traceback,importlib.util
P=Path
ID='DTC_BROAD_COUPLED_ROUTE_BRIDGE_V1'
MARKER='DTC_MAIN_COUPLED_ROUTE_BRIDGE_INSTALL_V1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with P(p).open('xb')as f:f.write(raw(v));f.flush();os.fsync(f.fileno())
def append_locked(reg,request,before,row):
 """Pure locked registry update, never calls the engine or another lock."""
 q=reg['registered_future_requests'][request]
 assert ID not in q['additional_operational_overlays']
 assert q['budget']==before['budget']and q['remaining']==before['remaining']==q['budget']-len(q['consumed'])
 assert q['consumed']==before['consumed']and q['additional_operational_overlays']==before['records']
 previous=copy.deepcopy(q);q['additional_operational_overlays'][ID]=copy.deepcopy(row)
 expected=copy.deepcopy(previous);expected['additional_operational_overlays'][ID]=copy.deepcopy(row);assert q==expected
def apply(config_path):
 cfg=read(config_path);assert cfg['schema']=='DTC_MAIN_COUPLED_ROUTE_BRIDGE_INSTALL_CONFIG_V1'
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 assert cfg['installer_path']==str(P(__file__))and sha(__file__)==cfg['installer_sha256']
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'ROUTE_MAIN_SOURCE_DRIFT '+p
 assert cfg['source_pins'][cfg['helper_source_path']]==cfg['helper_source_sha256']==sha(cfg['helper_source_path'])
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'OBSERVE_EXISTING_ROUTE_INSTALL_NEVER_REAPPLY'
 old=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1;assert old['phase']=='ARMED_ACKED'and old['armed']is True
 aux=main.DTC_MAIN_OWNER_FRAME_NOFLAG_AUX_V2;assert aux['phase']=='INSTALLED_ACKED'
 frame=old['frame'];engine=old['engine'];engine.assert_parent_lease()
 ids={k:id(frame.f_locals[k])for k in ['pool','claims','running','post','registry']};assert ids==old['ACK']['same_frame_object_ids']
 directory=P(cfg['directory']);directory.mkdir(parents=True,exist_ok=True)
 state=dict(frame=frame,engine=engine,phase='PREFLIGHT',directory=str(directory))
 setattr(main,MARKER,state)
 try:
  helper=load('actual_current_scope_coupled_route_bridge',cfg['helper_source_path']);assert helper.ID==ID
  state['helper']=helper;bcfg=read(cfg['bridge_configuration_path'])
  tiny=main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1;aging=tiny.aging;res=frame.f_locals['res'];consumer=frame.f_locals['consumer'];B=main.DTC_STRACE_BROAD_SHARED_DISPATCH_V1;coupling=tiny.coupling
  with aging.lock:
   engine.assert_parent_lease();q=engine.registered()[2]
   assert res.choose_dispatch is B['chooser']and B['armed']is True and aging.original is B['leaf']
   assert tiny.facade.resources is aux['adapter_state']['wrapper']and aux['adapter_state']['enabled']is True
   refs=(frame.f_globals['worker'],aging.original,aging.frame_provider,coupling['gate'].original_provider,coupling['gate'].wrapper,coupling['gate'].original_choose,coupling['cpu']['wrapper'],coupling['cpu']['original'],tiny.frames,tiny.facade,tiny.facade.resources,res.resources,consumer.safe_finish)
   before=dict(budget=q['budget'],remaining=q['remaining'],consumed=copy.deepcopy(q['consumed']),records=copy.deepcopy(q['additional_operational_overlays']),protected=copy.deepcopy(aging.state.protected),tokens=copy.deepcopy(aging.state.pending_releases),previous_C=aging.state.previous_C,calls=aging.calls)
   row=helper.record(bcfg);shadow=copy.deepcopy(q);shadow['additional_operational_overlays'][ID]=row;helper.validate(bcfg,shadow)
   put(directory/'PREIMAGE.json',dict(budget=q['budget'],remaining=q['remaining'],old_UUIDs={c:v['uuid']for c,v in q['consumed'].items()},old_operational_records=before['records'],protected_bytes=before['protected'],pending_release_count=len(before['tokens']),previous_C=before['previous_C'],aging_calls=before['calls']))
   engine.update_authority(lambda reg:append_locked(reg,engine.REQ,before,row));state['phase']='NEW_ROUTE_ROW_REGISTERED_ZERO_GRANT'
   token=helper.install_on_frame(frame,bcfg,engine.assert_parent_lease,main=main);state['bridge_state']=token
   assert res.choose_dispatch is token['wrapper']and token['previous']is B['chooser']
   assert refs==(frame.f_globals['worker'],aging.original,aging.frame_provider,coupling['gate'].original_provider,coupling['gate'].wrapper,coupling['gate'].original_choose,coupling['cpu']['wrapper'],coupling['cpu']['original'],tiny.frames,tiny.facade,tiny.facade.resources,res.resources,consumer.safe_finish)
   assert aging.state.protected==before['protected']and aging.state.pending_releases==before['tokens']and aging.state.previous_C==before['previous_C']and aging.calls==before['calls']
   after=engine.registered()[2];assert after['budget']==before['budget']and after['remaining']==before['remaining']and after['consumed']==before['consumed']
   assert all(after['additional_operational_overlays'][k]==v for k,v in before['records'].items())
   for p,h in cfg['source_pins'].items():assert sha(p)==h,'ROUTE_MAIN_FINAL_SOURCE_DRIFT '+p
   ack=dict(schema='DTC_MAIN_COUPLED_ROUTE_BRIDGE_INSTALL_ACK_V1',status='INSTALLED_SAME_OWNER_SAME_COUPLED_GATES_NOT_SIMULATION_ACCEPTANCE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,configuration_sha256=sha(config_path),bridge_configuration_sha256=sha(cfg['bridge_configuration_path']),helper_source_sha256=sha(cfg['helper_source_path']),same_frame_object_ids=ids,helper_receipt=token['receipt'],only_changed_reference='res.choose_dispatch',old_worker_consumer_cpu_FrameGuard_aging_facade_refs_preserved=True,old_records_preserved=True,protected_bytes=aging.state.protected,pending_release_count=len(aging.state.pending_releases),aging_advance_calls_by_callback=0,models_started_by_callback=0,new_grants=0,budget=after['budget'],remaining=after['remaining'])
   put(directory/'ACK.json',ack);state.update(phase='INSTALLED_ACKED',ACK=ack);return ack
 except BaseException as error:
  failure=dict(status='COUPLED_ROUTE_INSTALL_HOLD_PRESERVE',phase=state['phase'],error=repr(error),traceback=traceback.format_exc(),automatic_retry=False,automatic_rollback=False,new_grants=0,models_started_by_callback=0)
  state.update(phase='HOLD_PRESERVE',failure=failure)
  try:put(directory/'ERROR.json',failure)
  except BaseException as e:state['error_evidence_failure']=repr(e)
  return failure
