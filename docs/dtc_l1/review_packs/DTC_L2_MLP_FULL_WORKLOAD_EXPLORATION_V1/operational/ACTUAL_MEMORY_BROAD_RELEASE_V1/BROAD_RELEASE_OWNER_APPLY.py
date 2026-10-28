import pathlib,json,hashlib,importlib.util,sys,copy,os,datetime,traceback
_d=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/future_memory_admission_v1')
def _read(p):return json.loads(pathlib.Path(p).read_bytes())
def _sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def _put(p,v):
 with pathlib.Path(p).open('x')as h:json.dump(v,h,indent=2);h.write('\n');h.flush();os.fsync(h.fileno())
def _load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
try:
 _main=sys.modules['__main__'];_r=_d.parents[2];_m=_main.DTC_FUTURE_MEMORY_ADMISSION_095_FLOOR10_V1;_e=_m['engine'];_e.assert_parent_lease();_lib=_m['lib'];_aging=_m['aging'];_proof=_read(_d/'ACTUAL_MEMORY_ROLLOUT_QUALIFICATION.json')
 assert _proof['status']=='PASS_FUTURE_MEMORY_CANARY_ROLLOUT_READONLY_REPLAY'and _proof['backend']=='ACTUAL_READONLY'and _proof['production_release_eligible']is True
 _c=_proof['cohort'];assert _sha(_r/'analysis'/(_c+'.RESULT.json'))==_proof['RESULT_sha256']and _sha(_r/'control/qualification_ledger'/(_c+'.DONE.json'))==_proof['DONE_sha256']
 for _path,_digest in _proof['source_and_route_pins'].items():assert _sha(_path)==_digest
 assert not hasattr(_main,'DTC_FUTURE_MEMORY_PRIMARY_SCOPE_SYNC_V1'),'Restore priority lease before installing scope synchronizer'
 with _aging.lock:
  _old=_read(_d/'ACTIVE_MEMORY.json');assert _old==_m['context']['cfg']and _old['scope_mode']=='FINITE_CANARY'and _old['allowed_cohorts']==[_c];_q=_e.registered()[2];_lib.validate(_old,_q)
  _done=_q['consumed'][_c]['execution_receipt'];assert _done['uuid']==_proof['uuid']and _done['stop_reason']is None and _done['launcher_wait_returncode']==0
  _primary={p['cohort']for p in _read(_r/'control/MATRIX_CURRENT.json')['points']};assert len(_primary)==350 and _read(_r/'control/MATRIX_CURRENT.json')['revision']==0
  _new=copy.deepcopy(_old);_new['scope_mode']='ALL_UNSPENT_FUTURE';_new['allowed_cohorts']=_old['allowed_cohorts']+sorted((_primary&set(_q['admitted_specs']))-set(_q['consumed'])-set(_old['allowed_cohorts']))
  assert len(_new['allowed_cohorts'])>1;_row=copy.deepcopy(_q['additional_operational_overlays'][_lib.ID]);_newrow=copy.deepcopy(_row);_newrow.update(_lib.record(_new));_newrow.update(actual_canary_qualification_sha256=_sha(_d/'ACTUAL_MEMORY_ROLLOUT_QUALIFICATION.json'),broad_scope_approved_by_Main=True)
  _prepared=dict(old_config=_old,new_config=_new,old_record=_row,new_record=_newrow,old_config_file_sha256=_sha(_d/'ACTIVE_MEMORY.json'),new_config_file_sha256=hashlib.sha256(_lib.js(_new)).hexdigest(),qualification_sha256=_sha(_d/'ACTUAL_MEMORY_ROLLOUT_QUALIFICATION.json'),additional_grants=0,supplemental_R2_already_live_keeps_original_generation=True)
  _put(_d/'BROAD_RELEASE_PREPARED.json',_prepared)
  _lease=_main.DTC_FINITE_MEMORY_CANARY_PRIORITY_LEASE_V1;assert _lease['adapter'].cfg['source_sha256']=='3fa893ff93083ac1b4f3dd7536fe6db6467af8fb15b9fca1ba42eba2ef80f1e4';_lm=_load('main_restore_closed_memory_priority_lease',_lease['adapter'].cfg['source_path']);_restored=_lm.restore_in_owner();_put(_d/'BROAD_RELEASE_PRIORITY_RESTORE_ACK.json',_restored)
  _protected=_aging.state.protected;_tokens=copy.deepcopy(_aging.state.pending_releases)
  def _amend(reg):
   q=reg['registered_future_requests'][_e.REQ];assert q['additional_operational_overlays'][_lib.ID]==_row;_before={k:copy.deepcopy(v)for k,v in q.items()if k!='additional_operational_overlays'};q['additional_operational_overlays'][_lib.ID]=copy.deepcopy(_newrow);assert _before=={k:v for k,v in q.items()if k!='additional_operational_overlays'}
  _e.update_authority(_amend)
  _path=_d/'ACTIVE_MEMORY.json';_tmp=_d/'.ACTIVE_MEMORY.BROAD_RELEASE_V1.tmp';assert not _tmp.exists()
  with _tmp.open('xb')as h:h.write(_lib.js(_new));h.flush();os.fsync(h.fileno())
  assert _sha(_path)==_prepared['old_config_file_sha256']and _sha(_tmp)==_prepared['new_config_file_sha256'];os.replace(_tmp,_path);_fd=os.open(_d,os.O_RDONLY);os.fsync(_fd);os.close(_fd)
  _om=_load('main_explicit_memory_broad_scope_update',_new['owner_path']);assert _sha(_new['owner_path'])==_new['owner_sha256'];_ack=_om.update_scope_in_owner(_new,_e.assert_parent_lease)
  assert _aging.state.protected==_protected and _aging.state.pending_releases==_tokens and _m['context']['cfg']==_new;_lib.validate(_new,_e.registered()[2]);assert not hasattr(_main,'DTC_FINITE_MEMORY_CANARY_PRIORITY_LEASE_V1')
  _ref=next(iter(_e.registered()[2]['consumed']));_res=_m['res'].resources(_e.canonical(_ref),True);assert _res['admission_decision']['memory_utilization_fraction']==.95
  _thread=_main.DTC_L2_MLP_ADDON_THREAD;_frame=sys._current_frames()[_thread.ident]
  while _frame and not(_frame.f_code.co_name=='run_scheduler'and pathlib.Path(_frame.f_code.co_filename)==_r/'tools/l2_ops.py'):_frame=_frame.f_back
  assert _frame is not None;_ack.update(status='ACTUAL_CANARY_VERIFIED_BROAD_FUTURE_MEMORY_SCOPE_ACTIVE',UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),owner_pid=os.getpid(),canary_uuid=_proof['uuid'],canary_cycles=_proof['cycles'],allowed_cohorts=_new['allowed_cohorts'],scope_mode=_new['scope_mode'],active_config_sha256=_sha(_path),old_overlay_provenance_retained=True,policy_change_natural_release_credit_bytes=0,protected_R_bytes=_protected,pool_object_id=id(_frame.f_locals['pool']),claims_object_id=id(_frame.f_locals['claims']),additional_grants=0,model_signals=0,model_starts_by_installer=0,native_entry_sha256=_sha('/root/data/ep_l2_dtc_l1_native_v2/bin/native'),qualification_sha256=_prepared['qualification_sha256'],fresh_budget_bytes=_res['admission_decision']['admission_RAM_budget_bytes'],full_growth_bytes=_res['total_projected_additional_RAM_bytes'])
  _put(_d/'BROAD_RELEASE_ACK.json',_ack)
except BaseException:
 _put(_d/'BROAD_RELEASE_ERROR.json',dict(traceback=traceback.format_exc(),automatic_retry=False))
