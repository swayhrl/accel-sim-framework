import pathlib,json,hashlib,importlib.util,sys,traceback,datetime
_d=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/io_actual_canary_v1')
try:
 def _load(n,p):
  s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
 _e=_load('io_canary_release_native_main',_d.parents[2]/'tools/l2_native.py');_e.assert_parent_lease();_main=sys.modules['__main__'];_p=json.loads((_d/'ACTUAL_IO_ROLLOUT_QUALIFICATION.json').read_bytes())
 assert _p['production_release_eligible']and _p['backend']=='ACTUAL_READONLY'and _p['status']=='PASS_CANARY_ROLLOUT_READONLY_REPLAY'
 _c=_p['cohort'];_r=_d.parents[2];assert hashlib.sha256((_r/'analysis'/(_c+'.RESULT.json')).read_bytes()).hexdigest()==_p['RESULT_sha256']
 _q=_e.registered()[2];_done=_q['consumed'][_c]['execution_receipt'];assert _done['uuid']==_p['uuid']and _done['stop_reason']is None and _done['launcher_wait_returncode']==0
 assert _main.DTC_L2_MLP_SINGLE_CANARY_PENDING_SCOPE_V1['cohort']==_c and _main.DTC_L2_MLP_SINGLE_CANARY_PENDING_SCOPE_V1['enabled']
 assert hasattr(_main,'DTC_L2_MLP_SHARED_JSON_IO_OUTER_V1')and hasattr(_main,'DTC_L2_MLP_FRAME_READ_GUARD_CPU_COUPLING_V1')
 for path,digest in _p['source_and_route_pins'].items():assert hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()==digest
 def _amend(reg):
  q=reg['registered_future_requests'][_e.REQ];before={k:json.dumps(q[k],sort_keys=True)for k in ['budget','remaining','consumed','admitted_specs']};x=q['additional_operational_overlays']['DTC_L2_MLP_SINGLE_CANARY_PENDING_SCOPE_V1'];x.update(status='CANARY_VERIFIED_BROAD_FUTURE_ADMISSION_APPROVED',accepted_canary_uuid=_p['uuid'],actual_IO_qualification_sha256=hashlib.sha256((_d/'ACTUAL_IO_ROLLOUT_QUALIFICATION.json').read_bytes()).hexdigest());assert before=={k:json.dumps(q[k],sort_keys=True)for k in before}
 _e.update_authority(_amend);_m=_load('published_single_io_canary_scope_restore',_d/'single_canary_filter.py');assert hashlib.sha256((_d/'single_canary_filter.py').read_bytes()).hexdigest()=='38f0a1f0f731e9033b780a324c99d5a23749e4008b6c73b004a7ac065fe60862';_ack=_m.restore_in_owner();_ack.update(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_canary_uuid=_p['uuid'],owner_pid=1498278,broad_future_admission_enabled=True,no_budget_grants=True,no_model_signals=True)
 with(_d/'BROAD_RELEASE_ACK.json').open('x')as h:json.dump(_ack,h,indent=2)
except BaseException:
 with(_d/'BROAD_RELEASE_ERROR.json').open('x')as h:json.dump({'traceback':traceback.format_exc()},h)
