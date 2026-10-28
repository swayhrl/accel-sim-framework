import pathlib,json,hashlib,importlib.util,traceback,datetime,os
try:
 _p=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/pending_resource_forecast_refresh_v1/actual_install_v2/OWNER_APPLY.py')
 assert hashlib.sha256(_p.read_bytes()).hexdigest()=='70f7f1426acd98469cb5fba60a21ad1a8094523719a160a25d3a246e3455e13f'
 _s=importlib.util.spec_from_file_location("main_bpf_engineering_owner_callback_v2",_p)
 _m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _m.apply('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/pending_resource_forecast_refresh_v1/actual_install_v2')
except BaseException:
 try:
  _error=traceback.format_exc();_ep=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/pending_resource_forecast_refresh_v1/actual_install_v2')/"CALLBACK_ERROR.json"
  with _ep.open("x")as _f:
   json.dump(dict(schema="MAIN_BPF_PENDING_CALLBACK_ERROR_V2",UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),traceback=_error,automatic_requeue=False,original_owner_exception_contained=True),_f,indent=2)
   _f.write("\n");_f.flush();os.fsync(_f.fileno())
 except BaseException:pass
