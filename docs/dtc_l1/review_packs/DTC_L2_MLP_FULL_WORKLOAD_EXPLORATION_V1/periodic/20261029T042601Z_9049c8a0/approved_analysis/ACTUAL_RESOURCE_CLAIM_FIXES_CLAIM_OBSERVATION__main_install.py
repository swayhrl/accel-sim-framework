"""Main-only observed-model claim persistence. No import-time mutations."""
from pathlib import Path
import json,hashlib,copy,sys,os,threading,datetime,traceback,importlib.util
P=Path
ID='OWNER_CLAIM_SNAPSHOT_SYNC_V1'
MARKER='DTC_MAIN_OWNER_CLAIM_SNAPSHOT_SYNC_INSTALL_V1'
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def read(p):return json.loads(P(p).read_bytes())
def raw(v):return(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def put(p,v):
 with P(p).open('xb')as f:f.write(raw(v));f.flush();os.fsync(f.fileno())
def append_locked(reg,request,before,row):
 # This callback operates only on its passed object. No nested engine locks.
 q=reg['registered_future_requests'][request]
 assert ID not in q['additional_operational_overlays']
 assert q['budget']==before['budget']and q['remaining']==before['remaining']==q['budget']-len(q['consumed'])
 assert q['consumed']==before['consumed']and q['additional_operational_overlays']==before['records']
 previous=copy.deepcopy(q);q['additional_operational_overlays'][ID]=copy.deepcopy(row)
 expected=copy.deepcopy(previous);expected['additional_operational_overlays'][ID]=copy.deepcopy(row);assert q==expected
def apply(config_path):
 cfg=read(config_path);assert cfg['schema']=='DTC_MAIN_CLAIM_SNAPSHOT_SYNC_INSTALL_CONFIG_V1'
 assert threading.current_thread()is threading.main_thread()and os.getpid()==1498278
 assert int(P('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 assert cfg['installer_path']==str(P(__file__))and sha(__file__)==cfg['installer_sha256']
 for p,h in cfg['source_pins'].items():assert sha(p)==h,'CLAIM_MAIN_SOURCE_DRIFT '+p
 main=sys.modules['__main__'];assert not hasattr(main,MARKER),'OBSERVE_EXISTING_CLAIM_SYNC_INSTALL_NO_BLIND_REAPPLY'
 old=main.DTC_MAIN_BROAD_SHARED_CPU_INSTALL_V1;assert old['phase']=='ARMED_ACKED'and old['armed']is True
 frame=old['frame'];engine=old['engine'];engine.assert_parent_lease()
 res=frame.f_locals['res'];aging=res.DTC_LARGE_JOB_AGING_INSTALLED;directory=P(cfg['directory'])
 state=dict(frame=frame,engine=engine,res=res,aging=aging,phase='PREFLIGHT',directory=str(directory))
 setattr(main,MARKER,state)
 try:
  helper=load('actual_owner_claim_snapshot_sync',cfg['helper_source_path']);assert helper.ID==ID
  with aging.lock:
   engine.assert_parent_lease()
   assert main.DTC_MAIN_PENDING_SYRK_RESOURCE_REFRESH_V1['phase']=='COMMITTED_ACKED'
   bridge=main.DTC_MAIN_COUPLED_ROUTE_BRIDGE_INSTALL_V1['bridge_state']
   previous=res.choose_dispatch;assert previous is bridge['wrapper']
   addon=main.DTC_L2_MLP_ADDON_THREAD
   assert addon.is_alive()and addon.native_id==1723771 and type(addon.ident)is int
   bcfg=read(cfg['helper_configuration_template_path'])
   assert bcfg['scheduler_thread_ident']=='MAIN_MUST_CAPTURE_ACTUAL_ADDON_THREAD_IDENT'
   bcfg['scheduler_thread_ident']=addon.ident
   put(cfg['helper_configuration_path'],bcfg)
   q=engine.registered()[2]
   refs=(frame.f_globals['worker'],aging.original,aging.frame_provider,aging.state,aging.state.advance,res.resources,frame.f_locals['consumer'].safe_finish)
   before=dict(budget=q['budget'],remaining=q['remaining'],consumed=copy.deepcopy(q['consumed']),records=copy.deepcopy(q['additional_operational_overlays']),protected=copy.deepcopy(aging.state.protected),tokens=copy.deepcopy(aging.state.pending_releases),previous_C=aging.state.previous_C,calls=aging.calls)
   row=helper.record(bcfg);shadow=copy.deepcopy(q);shadow['additional_operational_overlays'][ID]=row;helper.validate(bcfg,shadow)
   put(directory/'PREIMAGE.json',dict(budget=q['budget'],remaining=q['remaining'],old_UUIDs={c:v['uuid']for c,v in q['consumed'].items()},old_operational_records=before['records'],scheduler_thread_ident=addon.ident,scheduler_native_id=addon.native_id,claims_sha256=sha(P(bcfg['root'])/'control/POOL_DISPATCH_RESERVATIONS.json')))
   state.update(previous_choose=previous,phase='CONFIGURATION_CAPTURED_NO_REF_CHANGE')
   engine.update_authority(lambda reg:append_locked(reg,engine.REQ,before,row));state['phase']='NEW_CLAIM_SYNC_ROW_REGISTERED_ZERO_GRANT'
   token=helper.install_on_frame(frame,bcfg,engine.assert_parent_lease,main=main);state['sync_state']=token
   assert res.choose_dispatch is token['wrapper']and token['previous']is previous
   assert refs==(frame.f_globals['worker'],aging.original,aging.frame_provider,aging.state,aging.state.advance,res.resources,frame.f_locals['consumer'].safe_finish)
   assert aging.state.protected==before['protected']and aging.state.pending_releases==before['tokens']and aging.state.previous_C==before['previous_C']and aging.calls==before['calls']
   after=engine.registered()[2];expected=copy.deepcopy(q);expected['additional_operational_overlays'][ID]=row;assert after==expected
   for p,h in cfg['source_pins'].items():assert sha(p)==h,'CLAIM_MAIN_FINAL_SOURCE_DRIFT '+p
   ack=dict(schema='DTC_MAIN_CLAIM_SNAPSHOT_SYNC_INSTALL_ACK_V1',status='INSTALLED_SAME_OWNER_OBSERVATION_BOOKKEEPING_NOT_SIMULATION_ACCEPTANCE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,configuration_sha256=sha(config_path),helper_configuration_sha256=sha(cfg['helper_configuration_path']),helper_source_sha256=sha(cfg['helper_source_path']),helper_receipt=token['receipt'],only_changed_reference='res.choose_dispatch',old_worker_consumer_aging_facade_refs_preserved=True,old_records_preserved=True,aging_advance_calls_by_callback=0,models_started_by_callback=0,new_grants=0,budget=after['budget'],remaining=after['remaining'],scheduler_thread_ident=addon.ident,scheduler_native_id=addon.native_id)
   put(directory/'ACK.json',ack);state.update(phase='INSTALLED_ACKED',ACK=ack);return ack
 except BaseException as error:
  admission_held=False
  with aging.lock:
   token=state.get('sync_state')or getattr(main,ID,None)
   if token is not None and res.choose_dispatch is token['wrapper']:
    def hold(*a,**kw):return None
    state['hold']=hold;res.choose_dispatch=hold;admission_held=True
  failure=dict(status='CLAIM_SYNC_INSTALL_HOLD_PRESERVE',phase=state['phase'],error=repr(error),traceback=traceback.format_exc(),admission_held=admission_held,automatic_retry=False,new_grants=0,models_started_by_callback=0)
  state.update(phase='HOLD_PRESERVE',failure=failure)
  try:put(directory/'ERROR.json',failure)
  except BaseException as e:state['error_evidence_failure']=repr(e)
  return failure
