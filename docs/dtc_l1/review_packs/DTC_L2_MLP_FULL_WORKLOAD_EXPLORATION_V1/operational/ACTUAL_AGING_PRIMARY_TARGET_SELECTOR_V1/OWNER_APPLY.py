import pathlib,json,hashlib,sys,os,copy,datetime,traceback,importlib.util
_d=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/aging_primary_target_selector_v1');_r=_d.parents[2];_changed=False;_module=None
def _read(p):return json.loads(pathlib.Path(p).read_bytes())
def _sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def _put(p,v):
 with pathlib.Path(p).open('x')as h:json.dump(v,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
try:
 _main=sys.modules['__main__'];_m=_main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;_e=_m['engine'];_a=_m['aging'];_e.assert_parent_lease()
 assert os.getpid()==1498278 and int(pathlib.Path('/proc/self/stat').read_text().rsplit(')',1)[1].split()[19])==977758783
 assert _sha(_d/'primary_target_selector.py')=='af09621e85945e489d6022f1b22b6c8702374af8ad81d5e14945977fed039b57'
 _s=importlib.util.spec_from_file_location('actual_aging_primary_selector_v1',_d/'primary_target_selector.py');_module=importlib.util.module_from_spec(_s);_s.loader.exec_module(_module)
 with _a.lock:
  _sync=_main.DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1;_tiny=_main.DTC_FUTURE_MEMORY_AGING_FACADE_095_V1;_sync.stable_memory();_tiny.guard()
  _cfg=_m['context']['cfg'];_m['lib'].validate(_cfg,_e.registered()[2]);assert hasattr(_main,'DTC_CPU_SPARE_EXECUTION_PRIMARY_FUTURE_V2')
  _active=_r/'control/operational_amendments/future_memory_admission_v1/ACTIVE_MEMORY.json';_active_sha=_sha(_active)
  assert _active_sha=='4dc935376bc0cfadb4d6049c28f063a72b4f83e5b4a571a7f4aa61e4f3515441'
  _thread=_main.DTC_L2_MLP_ADDON_THREAD;_f=sys._current_frames()[_thread.ident]
  while _f and not(_f.f_code.co_name=='run_scheduler'and pathlib.Path(_f.f_code.co_filename)==_r/'tools/l2_ops.py'):_f=_f.f_back
  assert _f is not None
  _ids={k:id(_f.f_locals[k])for k in ['pool','claims','running','post','registry']}
  _refs=(_a.state,_a.lock,_a.original,_a.wrapper,_a.frame_provider,_m['res'].choose_dispatch,_m['res'].resources,_f.f_globals['worker'],_m,_sync,_tiny)
  _before=copy.deepcopy(_a.state.__dict__);_q=_e.registered()[2];_budget=_q['budget'];_seen=len(_a.state.seen_completions)
  _put(_d/'PREIMAGE.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),same_runtime_objects=_ids,aging_id=id(_a),state_id=id(_a.state),lock_id=id(_a.lock),protected_bytes=_a.state.protected,previous_C=_a.state.previous_C,seen_completions=[list(x)for x in sorted(_a.state.seen_completions)],pending_release_count=len(_a.state.pending_releases),budget=_budget,active_memory_sha256=_active_sha))
  _proof=_module.apply_in_owner();_changed=True
  assert _refs==(_a.state,_a.lock,_a.original,_a.wrapper,_a.frame_provider,_m['res'].choose_dispatch,_m['res'].resources,_f.f_globals['worker'],_m,_sync,_tiny)
  assert _ids=={k:id(_f.f_locals[k])for k in _ids}and {k:v for k,v in _a.state.__dict__.items()if k!='advance'}==_before
  assert copy.deepcopy(_a.state.__dict__)['advance']is _a.state.advance
  _sync.stable_memory();_tiny.guard();_m['lib'].validate(_cfg,_e.registered()[2])
  assert _sha(_active)==_active_sha and _e.registered()[2]['budget']==_budget and len(_a.state.seen_completions)==_seen
  for _p,_h in _cfg['expected_pins'].items():assert _sha(_p)==_h
  def _activated(reg):
   q=reg['registered_future_requests'][_e.REQ];before=copy.deepcopy(q);q['additional_operational_overlays']['AGING_PRIMARY_TARGET_SELECTOR_V1']['production_installation_pending']=False
   expected=copy.deepcopy(before);expected['additional_operational_overlays']['AGING_PRIMARY_TARGET_SELECTOR_V1']['production_installation_pending']=False;assert q==expected
  _e.update_authority(_activated)
  _proof.update(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),owner_start_ticks=977758783,publication_commit='0a8c7a2e00204e8b89b0411bdf887e64fd3c0bbe',same_runtime_objects=_ids,lock_id=id(_a.lock),same_CPU2_Tiny_SYNC_FrameGuard_provider_refs=True,all_existing_credit_history_unchanged=True,no_retroactive_credit=True,active_memory_sha256=_active_sha,all_old_source_pins_unchanged=True,model_signals=0,next_required='OBSERVE_ACTUAL_CHOOSER_DECISION_AND_TRUE_NATURAL_RELEASE')
  _put(_d/'ACK.json',_proof)
except BaseException:
 _error=traceback.format_exc();_rollback=None
 try:
  if _changed:
   with _a.lock:_rollback=_module.restore_in_owner(_e.assert_parent_lease,_main)
 except BaseException:_rollback=dict(traceback=traceback.format_exc())
 _put(_d/'ERROR.json',dict(traceback=_error,rollback=_rollback,automatic_retry=False))
