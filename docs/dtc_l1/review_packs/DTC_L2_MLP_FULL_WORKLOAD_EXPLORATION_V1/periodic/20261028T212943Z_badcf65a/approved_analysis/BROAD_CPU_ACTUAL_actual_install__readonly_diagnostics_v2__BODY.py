import pathlib,json,hashlib,importlib.util,traceback,datetime,os
try:
 _p=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_diagnostics_v2/diagnose.py')
 assert hashlib.sha256(_p.read_bytes()).hexdigest()=='15cb4ca63b1cc9712ccd107845c16cae62d96864c58d45de0af1b4265e842920'
 _s=importlib.util.spec_from_file_location("main_bpf_engineering_owner_callback_v2",_p)
 _m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _m.apply('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_diagnostics_v2')
except BaseException:
 try:
  _error=traceback.format_exc();_ep=pathlib.Path('/root/data/dtc_l2_mlp_exploration_20261027_v1/control/operational_amendments/broad_shared_cpu_v1/actual_install_v2/readonly_diagnostics_v2')/"CALLBACK_ERROR.json"
  with _ep.open("x")as _f:
   json.dump(dict(schema="MAIN_BPF_PENDING_CALLBACK_ERROR_V2",UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),traceback=_error,automatic_requeue=False,original_owner_exception_contained=True),_f,indent=2)
   _f.write("\n");_f.flush();os.fsync(_f.fileno())
 except BaseException:pass
