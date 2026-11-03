import pathlib,json,hashlib,importlib.util,traceback,datetime,os
try:
 _p=pathlib.Path('/root/data/dtc_stage_iia_first16_20261104_v1/control/operational_amendments/disk_preclaim_v1/owner_disk_preclaim.py')
 assert hashlib.sha256(_p.read_bytes()).hexdigest()=='a4c5aaf17ad92adb2ae8141fb864b73377ce8db2ded64056e7b4b75fd9f99d38'
 _s=importlib.util.spec_from_file_location("main_bpf_engineering_owner_callback_v2",_p)
 _m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _m.apply('/root/data/dtc_stage_iia_first16_20261104_v1/control/operational_amendments/disk_preclaim_v1/actual_single_callback_v1')
except BaseException:
 try:
  _error=traceback.format_exc();_ep=pathlib.Path('/root/data/dtc_stage_iia_first16_20261104_v1/control/operational_amendments/disk_preclaim_v1/actual_single_callback_v1')/"CALLBACK_ERROR.json"
  with _ep.open("x")as _f:
   json.dump(dict(schema="MAIN_BPF_PENDING_CALLBACK_ERROR_V2",UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),traceback=_error,automatic_requeue=False,original_owner_exception_contained=True),_f,indent=2)
   _f.write("\n");_f.flush();os.fsync(_f.fileno())
 except BaseException:pass
