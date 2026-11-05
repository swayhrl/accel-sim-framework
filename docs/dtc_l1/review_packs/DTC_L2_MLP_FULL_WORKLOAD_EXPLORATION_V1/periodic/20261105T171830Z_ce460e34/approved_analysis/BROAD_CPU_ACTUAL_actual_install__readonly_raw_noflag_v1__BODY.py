import pathlib,json,hashlib,importlib.util,traceback,datetime,os
try:
 _p=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_raw_noflag_v1/diagnose.py')
 assert hashlib.sha256(_p.read_bytes()).hexdigest()=='97e09c596651cc28765b82abb32d5123e2c1c63582c585955d2b473d8ffed0ce'
 _s=importlib.util.spec_from_file_location("main_bpf_engineering_owner_callback_v2",_p)
 _m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _m.apply('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_raw_noflag_v1')
except BaseException:
 try:
  _error=traceback.format_exc();_ep=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_raw_noflag_v1')/"CALLBACK_ERROR.json"
  with _ep.open("x")as _f:
   json.dump(dict(schema="MAIN_BPF_PENDING_CALLBACK_ERROR_V2",UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),traceback=_error,automatic_requeue=False,original_owner_exception_contained=True),_f,indent=2)
   _f.write("\n");_f.flush();os.fsync(_f.fileno())
 except BaseException:pass
