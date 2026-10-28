import pathlib,json,hashlib,importlib.util,sys,os,copy,traceback,datetime
_d=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/cpu_spare_memory_v1')
def _read(p):return json.loads(pathlib.Path(p).read_bytes())
def _sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def _put(p,v):
 with pathlib.Path(p).open('x')as h:json.dump(v,h,indent=2);h.flush();os.fsync(h.fileno())
def _atomic(p,v):
 p=pathlib.Path(p);t=_d/('.'+p.name+'.transition');assert not t.exists()
 with t.open('x')as h:json.dump(v,h,sort_keys=True,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
 os.replace(t,p);fd=os.open(p.parent,os.O_RDONLY);os.fsync(fd);os.close(fd)
_active=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json');_changed=False;_owner=None
try:
 _cfg=_read(_d/'INSTALL.json');_main=sys.modules['__main__'];_m=_main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;_aging=_m['aging'];_e=_m['engine'];_e.assert_parent_lease()
 assert os.getpid()==1498278 and int(pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 assert _sha(_cfg['owner_path'])==_cfg['owner_sha256'] and _sha(_cfg['library_path'])==_cfg['library_sha256']
 _sp=importlib.util.spec_from_file_location('main_actual_cpu_spare_owner',_cfg['owner_path']);_owner=importlib.util.module_from_spec(_sp);_sp.loader.exec_module(_owner)
 with _aging.lock:
  _old=_read(_d/'OLD_ACTIVE_CONFIG.json');assert _read(_active)==_old==_m['context']['cfg']
  _sync=_main.DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1;_tiny=_main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1;_sync.stable_memory();_tiny.guard()
  _thread=_main.DTC_L2_MLP_ADDON_THREAD;_frame=sys._current_frames()[_thread.ident]
  while _frame and not(_frame.f_code.co_name=='run_scheduler'and pathlib.Path(_frame.f_code.co_filename)==_d.parents[2]/'tools/l2_ops.py'):_frame=_frame.f_back
  assert _frame is not None
  _c=_cfg['cpu_exception_scope']['allowed_cohorts'][0];_q=copy.deepcopy(_e.registered()[2]);assert _c not in _q['consumed']and _c not in _frame.f_locals['claims']
  assert not(_d.parents[2]/'control/qualification_ledger'/(_c+'.INTENT.json')).exists()
  assert not(_d.parents[2]/'control/dispatch_bindings'/(_c+'.json')).exists()
  _ids={k:id(_frame.f_locals[k])for k in ['pool','claims','running','post','registry']};_memory_id=id(_m);_oldR=_aging.state.protected;_tokens=copy.deepcopy(_aging.state.pending_releases)
  _put(_d/'TRANSITION_PREPARED.json',dict(old_config=_old,new_config=_cfg,old_MEMORY_row=_q['additional_operational_overlays'][_old['overlay_id']],budget=_q['budget'],same_runtime_objects=_ids,new_grants=0))
  _atomic(_active,_cfg);_changed=True
  _proof=_owner.install_on_frame(_frame,_cfg,_aging,_e.assert_parent_lease,_main)
  assert id(_m)==_memory_id and _m['context']['cfg']==_cfg and _read(_active)==_cfg
  _sync.stable_memory();_tiny.guard();_m['lib'].validate(_cfg,_e.registered()[2])
  assert _ids=={k:id(_frame.f_locals[k])for k in _ids}and _oldR==_aging.state.protected and _tokens==_aging.state.pending_releases
  assert _q['budget']==_e.registered()[2]['budget']and _q['additional_operational_overlays'][_old['overlay_id']]==_e.registered()[2]['additional_operational_overlays'][_old['overlay_id']]
  def _activated(reg):reg['registered_future_requests'][_e.REQ]['additional_operational_overlays'][_cfg['overlay_id']]['production_installation_pending']=False
  _e.update_authority(_activated)
  _proof.update(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),publication_commit='8ed9ae0509f8f1e6ca1f900f67a6ba88ddd77211',cohort=_c,owner_pid=os.getpid(),active_config_sha256=_sha(_active),same_runtime_objects=_ids,old_memory_record_unchanged=True,native46_and_MEM6_unchanged=True,automatic_CPU_scope_expansion=False,next_required='ACTUAL_NATIVE_BIRTH_NATURAL_STRICT_ARCHIVE_AND_CPU_IMPACT')
  _put(_d/'ACK.json',_proof)
except BaseException:
 _error=traceback.format_exc();_rollback=None
 try:
  if _changed:
   with _aging.lock:
    if hasattr(_main,'DTC_CPU_SPARE_EXECUTION_SINGLETON_V1'):_rollback=_owner.restore_in_owner(_e.assert_parent_lease,_main)
    _atomic(_active,_read(_d/'OLD_ACTIVE_CONFIG.json'));_sync.stable_memory();_tiny.guard()
 except BaseException:_rollback=dict(error=traceback.format_exc())
 _put(_d/'ERROR.json',dict(traceback=_error,rollback=_rollback,automatic_retry=False))
