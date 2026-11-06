"""Build a pending-call body which cannot propagate an ordinary Python error."""
def build_body(source_path,source_sha256,directory):
    return '''import pathlib,json,hashlib,importlib.util,traceback,datetime,os
try:
 _p=pathlib.Path(SOURCE_LITERAL)
 assert hashlib.sha256(_p.read_bytes()).hexdigest()==SHA_LITERAL
 _s=importlib.util.spec_from_file_location("main_bpf_engineering_owner_callback_v2",_p)
 _m=importlib.util.module_from_spec(_s);_s.loader.exec_module(_m)
 _m.apply(DIRECTORY_LITERAL)
except BaseException:
 try:
  _error=traceback.format_exc();_ep=pathlib.Path(DIRECTORY_LITERAL)/"CALLBACK_ERROR.json"
  with _ep.open("x")as _f:
   json.dump(dict(schema="MAIN_BPF_PENDING_CALLBACK_ERROR_V2",UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),traceback=_error,automatic_requeue=False,original_owner_exception_contained=True),_f,indent=2)
   _f.write("\\n");_f.flush();os.fsync(_f.fileno())
 except BaseException:pass
'''.replace('SOURCE_LITERAL',repr(str(source_path))).replace('SHA_LITERAL',repr(source_sha256)).replace('DIRECTORY_LITERAL',repr(str(directory)))
